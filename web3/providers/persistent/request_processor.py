import asyncio
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    TypeVar,
)

from web3._utils.batching import (
    BATCH_REQUEST_ID,
)
from web3._utils.caching import (
    RequestInformation,
    generate_cache_key,
)
from web3.exceptions import (
    SubscriptionProcessingFinished,
    TaskNotRunning,
    Web3ValueError,
)
from web3.providers.persistent.subscription_manager import (
    SubscriptionContainer,
)
from web3.types import (
    RPCEndpoint,
    RPCId,
    RPCResponse,
)
from web3.utils import (
    SimpleCache,
)

if TYPE_CHECKING:
    from web3.providers.persistent import (
        PersistentConnectionProvider,
    )

T = TypeVar("T")


class TaskReliantQueue(asyncio.Queue[T]):
    """
    A queue that relies on a task to be running to process items in the queue.
    """

    async def get(self) -> T:
        item = await super().get()
        if isinstance(item, Exception):
            # if the item is an exception, raise it so the task can handle this case
            # more gracefully
            raise item
        return item


class RequestProcessor:
    _subscription_queue_synced_with_ws_stream: bool = False

    # set by the subscription manager when it is initialized
    _subscription_container: SubscriptionContainer | None = None

    def __init__(
        self,
        provider: "PersistentConnectionProvider",
        subscription_response_queue_size: int = 500,
        request_information_cache_size: int = 500,
    ) -> None:
        self._provider = provider
        self._request_information_cache: SimpleCache = SimpleCache(
            request_information_cache_size
        )
        self._request_response_cache: SimpleCache = SimpleCache(500)
        self._subscription_response_queue: TaskReliantQueue[
            RPCResponse | TaskNotRunning
        ] = TaskReliantQueue(maxsize=subscription_response_queue_size)
        self._handler_subscription_queue: TaskReliantQueue[
            RPCResponse | TaskNotRunning | SubscriptionProcessingFinished
        ] = TaskReliantQueue(maxsize=subscription_response_queue_size)

    @property
    def active_subscriptions(self) -> dict[str, Any]:
        return {
            value.subscription_id: {"params": value.params}
            for key, value in self._request_information_cache.items()
            if value.method == "eth_subscribe"
        }

    # request information cache

    def cache_request_information(
        self,
        request_id: RPCId | None,
        method: RPCEndpoint,
        params: Any,
        response_formatters: tuple[
            dict[str, Callable[..., Any]] | Callable[..., Any],
            Callable[..., Any],
            Callable[..., Any],
        ],
    ) -> str | None:
        cached_requests_key = generate_cache_key((method, params))
        if cached_requests_key in self._provider._request_cache._data:
            cached_response = self._provider._request_cache._data[cached_requests_key]
            cached_response_id = cached_response.get("id")
            cache_key = generate_cache_key(cached_response_id)
            if cache_key in self._request_information_cache:
                self._provider.logger.debug(
                    "This is a cached request, not caching request info because it is "
                    "not unique:\n    method=%s,\n    params=%s",
                    method,
                    params,
                )
                return None

        if request_id is None:
            if not self._provider._is_batching:
                raise Web3ValueError(
                    "Request id must be provided when not batching requests."
                )

        cache_key = generate_cache_key(request_id)
        request_info = RequestInformation(
            method,
            params,
            response_formatters,
        )
        self._provider.logger.debug(
            "Caching request info:\n    request_id=%s,\n"
            "    cache_key=%s,\n    request_info=%s",
            request_id,
            cache_key,
            request_info.__dict__,
        )
        self._request_information_cache.cache(
            cache_key,
            request_info,
        )
        if self._request_information_cache.is_full():
            self._provider.logger.warning(
                "Request information cache is full. This may result in unexpected "
                "behavior. Consider increasing the ``request_information_cache_size`` "
                "on the provider."
            )
        return cache_key

    def pop_cached_request_information(
        self, cache_key: str
    ) -> RequestInformation | None:
        request_info = self._request_information_cache.pop(cache_key)
        if request_info is not None:
            self._provider.logger.debug(
                "Request info popped from cache:\n"
                "    cache_key=%s,\n    request_info=%s",
                cache_key,
                request_info.__dict__,
            )
        return request_info

    def get_request_information_for_response(
        self,
        response: RPCResponse,
    ) -> RequestInformation:
        if "method" in response and response["method"] == "eth_subscription":
            if "params" not in response:
                raise Web3ValueError("Subscription response must have params field")
            if "subscription" not in response["params"]:
                raise Web3ValueError(
                    "Subscription response params must have subscription field"
                )

            # retrieve the request info from the cache using the subscription id
            cache_key = generate_cache_key(response["params"]["subscription"])
            request_info = (
                # don't pop the request info from the cache, since we need to keep it
                # to process future subscription responses
                # i.e. subscription request information remains in the cache
                self._request_information_cache.get_cache_entry(cache_key)
            )
        else:
            # retrieve the request info from the cache using the response id
            cache_key = generate_cache_key(response["id"])
            if response in self._provider._request_cache._data.values():
                request_info = (
                    # don't pop the request info from the cache, since we need to keep
                    # it to process future responses
                    # i.e. request information remains in the cache
                    self._request_information_cache.get_cache_entry(cache_key)
                )
            else:
                request_info = (
                    # pop the request info from the cache since we don't need to keep it
                    # this keeps the cache size bounded
                    self.pop_cached_request_information(cache_key)
                )

            if (
                request_info is not None
                and request_info.method == "eth_unsubscribe"
                and response.get("result") is True
            ):
                # if successful unsubscribe request, remove the subscription request
                # information from the cache since it is no longer needed
                subscription_id = request_info.params[0]
                subscribe_cache_key = generate_cache_key(subscription_id)
                self.pop_cached_request_information(subscribe_cache_key)

        return request_info

    def append_middleware_response_processor(
        self,
        response: RPCResponse,
        middleware_response_processor: Callable[..., Any],
    ) -> None:
        response_id = response.get("id", None)

        if response_id is not None:
            cache_key = generate_cache_key(response_id)
            cached_request_info_for_id: RequestInformation = (
                self._request_information_cache.get_cache_entry(cache_key)
            )
            if cached_request_info_for_id is not None:
                cached_request_info_for_id.middleware_response_processors.append(
                    middleware_response_processor
                )
            else:
                self._provider.logger.debug(
                    "No cached request info for response id `%s`. Cannot "
                    "append middleware response processor for response: %s",
                    response_id,
                    response,
                )
        else:
            self._provider.logger.debug(
                "No response `id` in response. Cannot append middleware response "
                "processor for response: %s",
                response,
            )

    # raw response cache

    def _is_batch_response(self, raw_response: list[RPCResponse] | RPCResponse) -> bool:
        return isinstance(raw_response, list) or (
            isinstance(raw_response, dict)
            and raw_response.get("id") is None
            and self._provider._is_batching
        )

    async def cache_raw_response(
        self, raw_response: Any, subscription: bool = False
    ) -> None:
        if subscription:
            if self._subscription_response_queue.full():
                self._provider.logger.debug(
                    "Subscription queue is full. Waiting for provider to consume "
                    "messages before caching."
                )
                self._provider._listen_event.clear()
                await self._provider._listen_event.wait()

            self._provider.logger.debug(
                "Caching subscription response:\n    response=%s", raw_response
            )
            subscription_id = raw_response.get("params", {}).get("subscription")
            sub_container = self._subscription_container
            if sub_container and sub_container.get_handler_subscription_by_id(
                subscription_id
            ):
                # if the subscription has a handler, put it in the handler queue
                await self._handler_subscription_queue.put(raw_response)
            else:
                # otherwise, put it in the subscription response queue so a response
                # can be yielded by the message stream
                await self._subscription_response_queue.put(raw_response)
        elif self._is_batch_response(raw_response):
            # Since only one batch should be in the cache at all times, we use a
            # constant cache key for the batch response.
            cache_key = generate_cache_key(BATCH_REQUEST_ID)
            self._provider.logger.debug(
                "Caching batch response:\n    cache_key=%s,\n    response=%s",
                cache_key,
                raw_response,
            )
            self._request_response_cache.cache(cache_key, raw_response)
        else:
            response_id = raw_response.get("id")
            cache_key = generate_cache_key(response_id)
            self._provider.logger.debug(
                "Caching response:\n    response_id=%s,\n"
                "    cache_key=%s,\n    response=%s",
                response_id,
                cache_key,
                raw_response,
            )
            self._request_response_cache.cache(cache_key, raw_response)

    async def pop_raw_response(
        self, cache_key: str = None, subscription: bool = False
    ) -> Any:
        if subscription:
            qsize = self._subscription_response_queue.qsize()
            raw_response = await self._subscription_response_queue.get()

            if not self._provider._listen_event.is_set():
                self._provider._listen_event.set()

            if qsize == 0:
                if not self._subscription_queue_synced_with_ws_stream:
                    self._subscription_queue_synced_with_ws_stream = True
                    self._provider.logger.info(
                        "Subscription response queue synced with websocket message "
                        "stream."
                    )
            else:
                if self._subscription_queue_synced_with_ws_stream:
                    self._subscription_queue_synced_with_ws_stream = False
                self._provider.logger.info(
                    "Subscription response queue has %s subscriptions. "
                    "Processing as FIFO.",
                    qsize,
                )

            self._provider.logger.debug(
                "Subscription response popped from queue to be processed:\n"
                "    raw_response=%s",
                raw_response,
            )
        else:
            if not cache_key:
                raise Web3ValueError(
                    "Must provide cache key when popping a non-subscription response."
                )

            raw_response = self._request_response_cache.pop(cache_key)
            if raw_response is not None:
                self._provider.logger.debug(
                    "Cached response popped from cache to be processed:\n"
                    "    cache_key=%s,\n    raw_response=%s",
                    cache_key,
                    raw_response,
                )

        return raw_response

    # cache methods

    def _reset_handler_subscription_queue(self) -> None:
        self._handler_subscription_queue = TaskReliantQueue(
            maxsize=self._handler_subscription_queue.maxsize
        )

    def clear_caches(self) -> None:
        """Clear the request processor caches."""
        self._request_information_cache.clear()
        self._request_response_cache.clear()
        self._subscription_response_queue = TaskReliantQueue(
            maxsize=self._subscription_response_queue.maxsize
        )
        self._reset_handler_subscription_queue()
