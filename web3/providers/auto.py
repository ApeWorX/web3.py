from collections.abc import Callable, Sequence
import os
from typing import (
    Any,
)
from urllib.parse import (
    urlparse,
)

from eth_typing import (
    URI,
)

from web3.exceptions import (
    CannotHandleRequest,
    ProviderConnectionError,
)
from web3.providers import (
    AsyncHTTPProvider,
    AsyncIPCProvider,
    HTTPProvider,
    IPCProvider,
    JSONBaseProvider,
    WebSocketProvider,
)
from web3.providers.async_base import (
    AsyncJSONBaseProvider,
)
from web3.types import (
    RPCEndpoint,
    RPCResponse,
)

HTTP_SCHEMES = {"http", "https"}
WS_SCHEMES = {"ws", "wss"}


def load_provider_from_environment() -> JSONBaseProvider | None:
    uri_string = URI(os.environ.get("WEB3_PROVIDER_URI", ""))
    if not uri_string:
        return None

    return load_provider_from_uri(uri_string)


def load_provider_from_uri(
    uri_string: URI, headers: dict[str, tuple[str, str]] | None = None
) -> JSONBaseProvider:
    uri = urlparse(uri_string)
    if uri.scheme == "file":
        return IPCProvider(uri.path)
    elif uri.scheme in HTTP_SCHEMES:
        return HTTPProvider(uri_string, headers)
    else:
        raise NotImplementedError(
            "Web3 does not know how to connect to scheme "
            f"{uri.scheme!r} in {uri_string!r}"
        )


def async_load_provider_from_environment() -> AsyncJSONBaseProvider | None:
    uri_string = URI(os.environ.get("WEB3_PROVIDER_URI", ""))
    if not uri_string:
        return None

    return async_load_provider_from_uri(uri_string)


def async_load_provider_from_uri(
    uri_string: URI, headers: dict[str, tuple[str, str]] | None = None
) -> AsyncJSONBaseProvider:
    uri = urlparse(uri_string)
    if uri.scheme == "file":
        return AsyncIPCProvider(uri.path)
    elif uri.scheme in HTTP_SCHEMES:
        request_kwargs = {"headers": headers} if headers else None
        return AsyncHTTPProvider(uri_string, request_kwargs=request_kwargs)
    elif uri.scheme in WS_SCHEMES:
        return WebSocketProvider(uri_string)
    else:
        raise NotImplementedError(
            "Web3 does not know how to connect to scheme "
            f"{uri.scheme!r} in {uri_string!r}"
        )


def _async_ipc_provider_single_attempt() -> AsyncIPCProvider:
    # Only try the default IPC path once, so a missing local node doesn't stall
    # discovery with connection retries and backoff.
    return AsyncIPCProvider(max_connection_retries=1)


class AutoProvider(JSONBaseProvider):
    default_providers = (
        load_provider_from_environment,
        IPCProvider,
        HTTPProvider,
    )
    _active_provider = None

    def __init__(
        self,
        potential_providers: None
        | (Sequence[Callable[..., JSONBaseProvider] | type[JSONBaseProvider]]) = None,
    ) -> None:
        """
        :param iterable potential_providers: ordered series of provider classes
            to attempt with

        AutoProvider will initialize each potential provider (without arguments),
        in an attempt to find an active node. The list will default to
        :attribute:`default_providers`.
        """
        super().__init__()
        if potential_providers:
            self._potential_providers = potential_providers
        else:
            self._potential_providers = self.default_providers

    def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        try:
            return self._proxy_request(method, params)
        except OSError:
            return self._proxy_request(method, params, use_cache=False)

    def make_batch_request(
        self, requests: list[tuple[RPCEndpoint, Any]]
    ) -> list[RPCResponse] | RPCResponse:
        try:
            return self._proxy_batch_request(requests)
        except OSError:
            return self._proxy_batch_request(requests, use_cache=False)

    def is_connected(self, show_traceback: bool = False) -> bool:
        provider = self._get_active_provider(use_cache=True)
        return provider is not None and provider.is_connected(show_traceback)

    def _proxy_request(
        self, method: RPCEndpoint, params: Any, use_cache: bool = True
    ) -> RPCResponse:
        provider = self._get_active_provider(use_cache)
        if provider is None:
            raise CannotHandleRequest(
                "Could not discover provider while making request: "
                f"method:{method}\nparams:{params}\n"
            )

        return provider.make_request(method, params)

    def _proxy_batch_request(
        self, requests: list[tuple[RPCEndpoint, Any]], use_cache: bool = True
    ) -> list[RPCResponse] | RPCResponse:
        provider = self._get_active_provider(use_cache)
        if provider is None:
            raise CannotHandleRequest(
                "Could not discover provider while making batch request: "
                f"requests:{requests}\n"
            )

        return provider.make_batch_request(requests)

    def _get_active_provider(self, use_cache: bool) -> JSONBaseProvider | None:
        if use_cache and self._active_provider is not None:
            return self._active_provider

        for Provider in self._potential_providers:
            provider = Provider()
            if provider is not None and provider.is_connected():
                self._active_provider = provider
                return provider

        return None


class AsyncAutoProvider(AsyncJSONBaseProvider):
    default_providers = (
        async_load_provider_from_environment,
        _async_ipc_provider_single_attempt,
        AsyncHTTPProvider,
    )
    _active_provider = None

    def __init__(
        self,
        potential_providers: None
        | (Sequence[Callable[..., AsyncJSONBaseProvider | None] | type[Any]]) = None,
    ) -> None:
        """
        :param iterable potential_providers: ordered series of async provider
            classes (or callables returning a provider) to attempt with

        AsyncAutoProvider will initialize each potential provider (without
        arguments), in an attempt to find an active node. Persistent connection
        providers are connected before being checked, and any provider that
        isn't connected is disconnected again so no sockets or sessions leak.
        The list will default to :attribute:`default_providers`.
        """
        super().__init__()
        if potential_providers:
            self._potential_providers = potential_providers
        else:
            self._potential_providers = self.default_providers

    async def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        try:
            return await self._proxy_request(method, params)
        except OSError:
            return await self._proxy_request(method, params, use_cache=False)

    async def make_batch_request(
        self, requests: list[tuple[RPCEndpoint, Any]]
    ) -> list[RPCResponse] | RPCResponse:
        try:
            return await self._proxy_batch_request(requests)
        except OSError:
            return await self._proxy_batch_request(requests, use_cache=False)

    async def is_connected(self, show_traceback: bool = False) -> bool:
        provider = await self._get_active_provider(use_cache=True)
        return provider is not None and await provider.is_connected(show_traceback)

    async def disconnect(self) -> None:
        if self._active_provider is not None:
            await self._active_provider.disconnect()
            self._active_provider = None

    async def _proxy_request(
        self, method: RPCEndpoint, params: Any, use_cache: bool = True
    ) -> RPCResponse:
        provider = await self._get_active_provider(use_cache)
        if provider is None:
            raise CannotHandleRequest(
                "Could not discover provider while making request: "
                f"method:{method}\nparams:{params}\n"
            )

        return await provider.make_request(method, params)

    async def _proxy_batch_request(
        self, requests: list[tuple[RPCEndpoint, Any]], use_cache: bool = True
    ) -> list[RPCResponse] | RPCResponse:
        provider = await self._get_active_provider(use_cache)
        if provider is None:
            raise CannotHandleRequest(
                "Could not discover provider while making batch request: "
                f"requests:{requests}\n"
            )

        return await provider.make_batch_request(requests)

    async def _get_active_provider(
        self, use_cache: bool
    ) -> AsyncJSONBaseProvider | None:
        if use_cache and self._active_provider is not None:
            return self._active_provider

        if self._active_provider is not None:
            await self._safe_disconnect(self._active_provider)
            self._active_provider = None

        for Provider in self._potential_providers:
            provider = Provider()
            if provider is None:
                continue

            if await self._try_connect(provider):
                self._active_provider = provider
                return provider

            await self._safe_disconnect(provider)

        return None

    @staticmethod
    async def _try_connect(provider: AsyncJSONBaseProvider) -> bool:
        try:
            if provider.has_persistent_connection:
                await provider.connect()
            return await provider.is_connected()
        except (OSError, ProviderConnectionError):
            return False

    @staticmethod
    async def _safe_disconnect(provider: AsyncJSONBaseProvider) -> None:
        try:
            await provider.disconnect()
        except (OSError, ProviderConnectionError, NotImplementedError):
            pass
