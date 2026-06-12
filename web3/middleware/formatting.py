from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Union,
    cast,
)

from eth_utils.toolz import (
    assoc,
    curry,
    merge,
)

from web3.exceptions import (
    BadResponseFormat,
    Web3ValueError,
)
from web3.middleware.base import (
    Web3MiddlewareBuilder,
)
from web3.types import (
    EthSubscriptionParams,
    Formatters,
    FormattersDict,
    RPCEndpoint,
    RPCResponse,
)

if TYPE_CHECKING:
    from web3 import (  # noqa: F401
        AsyncWeb3,
        Web3,
    )
    from web3.middleware.base import (  # noqa: F401
        Web3Middleware,
    )
    from web3.providers import (  # noqa: F401
        PersistentConnectionProvider,
    )

FORMATTER_DEFAULTS: FormattersDict = {
    "request_formatters": {},
    "result_formatters": {},
    "error_formatters": {},
}


@curry
def _apply_response_formatters(
    method: RPCEndpoint,
    result_formatters: Formatters,
    error_formatters: Formatters,
    response: RPCResponse,
) -> RPCResponse:
    if not isinstance(response, dict):
        raise BadResponseFormat(
            "Malformed response: expected a valid JSON-RPC response object, got: "
            "`{}`".format(response)
        )

    result_formatter = result_formatters.get(method)
    if result_formatter is not None:
        result = response.get("result")
        if result is not None:
            return assoc(response, "result", result_formatter(result))

        params = response.get("params")
        if params is not None and params.get("result") is not None:
            # eth_subscription responses
            subscription_params = cast(EthSubscriptionParams, params)
            return assoc(
                response,
                "params",
                assoc(
                    params,
                    "result",
                    result_formatter(subscription_params["result"]),
                ),
            )

    error_formatter = error_formatters.get(method)
    if error_formatter is not None and "error" in response:
        return assoc(response, "error", error_formatter(response["error"]))

    return response


SYNC_FORMATTERS_BUILDER = Callable[["Web3", RPCEndpoint], FormattersDict]
ASYNC_FORMATTERS_BUILDER = Callable[
    ["AsyncWeb3[Any]", RPCEndpoint], Coroutine[Any, Any, FormattersDict]
]


class FormattingMiddlewareBuilder(Web3MiddlewareBuilder):
    request_formatters: Formatters = None
    result_formatters: Formatters = None
    error_formatters: Formatters = None
    sync_formatters_builder: SYNC_FORMATTERS_BUILDER = None
    async_formatters_builder: ASYNC_FORMATTERS_BUILDER = None

    @staticmethod
    @curry
    def build(
        w3: Union["Web3", "AsyncWeb3[Any]"],
        # formatters option:
        request_formatters: Formatters | None = None,
        result_formatters: Formatters | None = None,
        error_formatters: Formatters | None = None,
        # formatters builder option:
        sync_formatters_builder: SYNC_FORMATTERS_BUILDER | None = None,
        async_formatters_builder: ASYNC_FORMATTERS_BUILDER | None = None,
    ) -> "FormattingMiddlewareBuilder":
        # if not both sync and async formatters are specified, raise error
        if (
            sync_formatters_builder is None and async_formatters_builder is not None
        ) or (sync_formatters_builder is not None and async_formatters_builder is None):
            raise Web3ValueError(
                "Must specify both sync_formatters_builder and async_formatters_builder"
            )

        if sync_formatters_builder is not None and async_formatters_builder is not None:
            if (
                request_formatters is not None
                or result_formatters is not None
                or error_formatters is not None
            ):
                raise Web3ValueError(
                    "Cannot specify formatters_builder and formatters at the same time"
                )

        middleware = FormattingMiddlewareBuilder(w3)
        middleware.request_formatters = request_formatters or {}
        middleware.result_formatters = result_formatters or {}
        middleware.error_formatters = error_formatters or {}
        middleware.sync_formatters_builder = sync_formatters_builder
        middleware.async_formatters_builder = async_formatters_builder
        return middleware

    def request_processor(self, method: "RPCEndpoint", params: Any) -> Any:
        if self.sync_formatters_builder is not None:
            formatters = merge(
                FORMATTER_DEFAULTS,
                self.sync_formatters_builder(cast("Web3", self._w3), method),
            )
            self.request_formatters = formatters.pop("request_formatters")

        if method in self.request_formatters:
            formatter = self.request_formatters[method]
            params = formatter(params)

        return method, params

    def response_processor(self, method: RPCEndpoint, response: "RPCResponse") -> Any:
        if self.sync_formatters_builder is not None:
            formatters = merge(
                FORMATTER_DEFAULTS,
                self.sync_formatters_builder(cast("Web3", self._w3), method),
            )
            self.result_formatters = formatters["result_formatters"]
            self.error_formatters = formatters["error_formatters"]

        return _apply_response_formatters(
            method,
            self.result_formatters,
            self.error_formatters,
            response,
        )

    # -- async -- #

    async def async_request_processor(self, method: "RPCEndpoint", params: Any) -> Any:
        if self.async_formatters_builder is not None:
            formatters = merge(
                FORMATTER_DEFAULTS,
                await self.async_formatters_builder(
                    cast("AsyncWeb3[Any]", self._w3), method
                ),
            )
            self.request_formatters = formatters.pop("request_formatters")

        if method in self.request_formatters:
            formatter = self.request_formatters[method]
            params = formatter(params)

        return method, params

    async def async_response_processor(
        self, method: RPCEndpoint, response: "RPCResponse"
    ) -> Any:
        if self.async_formatters_builder is not None:
            formatters = merge(
                FORMATTER_DEFAULTS,
                await self.async_formatters_builder(
                    cast("AsyncWeb3[Any]", self._w3), method
                ),
            )
            self.result_formatters = formatters["result_formatters"]
            self.error_formatters = formatters["error_formatters"]

        if self._w3.provider.has_persistent_connection:
            # asynchronous response processing
            provider = cast("PersistentConnectionProvider", self._w3.provider)
            provider._request_processor.append_middleware_response_processor(
                response,
                _apply_response_formatters(
                    method,
                    self.result_formatters,
                    self.error_formatters,
                ),
            )
            return response
        else:
            return _apply_response_formatters(
                method,
                self.result_formatters,
                self.error_formatters,
                response,
            )
