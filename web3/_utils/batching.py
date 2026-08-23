from collections.abc import Callable, Coroutine
from types import (
    TracebackType,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Union,
    cast,
)
import warnings

from web3._utils.compat import (
    Self,
)
from web3.exceptions import (
    Web3ValueError,
)
from web3.types import (
    TFunc,
    TReturn,
)

if TYPE_CHECKING:
    from web3 import (  # noqa: F401
        AsyncWeb3,
        Web3,
    )
    from web3.contract.async_contract import (
        AsyncContractFunction,
    )
    from web3.contract.contract import (
        ContractFunction,
    )
    from web3.method import (  # noqa: F401
        Method,
    )
    from web3.providers import (  # noqa: F401
        PersistentConnectionProvider,
    )
    from web3.providers.async_base import (  # noqa: F401
        AsyncJSONBaseProvider,
    )
    from web3.providers.base import (  # noqa: F401
        JSONBaseProvider,
    )
    from web3.types import (  # noqa: F401
        RPCEndpoint,
        RPCResponse,
    )


BATCH_REQUEST_ID = "batch_request"  # for use as the cache key for batch requests

BatchRequestInformation = tuple[tuple["RPCEndpoint", Any], tuple[Any, ...]]
RPC_METHODS_UNSUPPORTED_DURING_BATCH = {
    "eth_subscribe",
    "eth_unsubscribe",
    "eth_sendRawTransaction",
    "eth_sendTransaction",
    "eth_signTransaction",
    "eth_sign",
    "eth_signTypedData",
}


class RequestBatcher(Generic[TFunc]):
    def __init__(self, web3: Union["AsyncWeb3[Any]", "Web3"]) -> None:
        self.web3 = web3
        self._requests_info: list[BatchRequestInformation] = []
        self._async_requests_info: list[
            Coroutine[Any, Any, BatchRequestInformation]
        ] = []
        self._initialize_batching()

    @property
    def _provider(self) -> Union["JSONBaseProvider", "AsyncJSONBaseProvider"]:
        return (
            cast("AsyncJSONBaseProvider", self.web3.provider)
            if self.web3.provider.is_async
            else cast("JSONBaseProvider", self.web3.provider)
        )

    def _validate_is_batching(self) -> None:
        if not self._provider._is_batching:
            raise Web3ValueError(
                "Batch has already been executed or cancelled. Create a new batch to "
                "issue batched requests."
            )

    def _initialize_batching(self) -> None:
        self._provider._batching_context.set(self)
        self.clear()

    def _end_batching(self) -> None:
        self.clear()
        self._provider._batching_context.set(None)

    def add(self, batch_payload: TReturn) -> None:
        self._validate_is_batching()

        if hasattr(batch_payload, "call"):
            batch_payload = batch_payload.call()

        # When batching, we don't make a request. Instead, we will get the request
        # information and store it in the `_requests_info` list. So we have to cast the
        # apparent "request" into the BatchRequestInformation type.
        if self._provider.is_async:
            self._async_requests_info.append(
                cast(Coroutine[Any, Any, BatchRequestInformation], batch_payload)
            )
        else:
            self._requests_info.append(cast(BatchRequestInformation, batch_payload))

    def add_mapping(
        self,
        batch_payload: dict[
            Union[
                "Method[Callable[..., Any]]",
                Callable[..., Any],
                "ContractFunction",
                "AsyncContractFunction",
            ],
            list[Any],
        ],
    ) -> None:
        self._validate_is_batching()
        for method, params in batch_payload.items():
            for param in params:
                self.add(method(param))

    def execute(self) -> list["RPCResponse"]:
        self._validate_is_batching()
        responses = self.web3.manager._make_batch_request(self._requests_info)
        self._end_batching()
        return responses

    def clear(self) -> None:
        self._requests_info = []
        self._async_requests_info = []

    def cancel(self) -> None:
        self._end_batching()

    # -- context manager -- #

    def __enter__(self) -> Self:
        self._initialize_batching()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        self._end_batching()

    # -- async -- #

    async def async_execute(self) -> list["RPCResponse"]:
        self._validate_is_batching()
        if self._provider.has_persistent_connection:
            responses = await self.web3.manager._async_make_socket_batch_request(
                self._async_requests_info
            )
        else:
            responses = await self.web3.manager._async_make_batch_request(
                self._async_requests_info
            )
        self._end_batching()
        return responses

    # -- async context manager -- #

    async def __aenter__(self) -> Self:
        self._initialize_batching()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        self._end_batching()


def sort_batch_response_by_response_ids(
    responses: list["RPCResponse"],
) -> list["RPCResponse"]:
    if all(response.get("id") is not None for response in responses):
        # If all responses have an `id`, sort them by `id`, since the JSON-RPC 2.0 spec
        # doesn't guarantee order.
        return sorted(responses, key=lambda response: response["id"])
    else:
        # If any response is missing an `id`, which should only happen on particular
        # errors, return them in the order they were received and hope that the
        # provider is returning them in order. Issue a warning.
        warnings.warn(
            "Received batch response with missing `id` for one or more responses. "
            "Relying on provider to return these responses in order.",
            RuntimeWarning,
            stacklevel=2,
        )
        return responses
