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
    Web3ValidationError,
)
from web3.providers import (
    HTTPProvider,
    IPCProvider,
    JSONBaseProvider,
)
from web3.providers.async_base import (
    AsyncJSONBaseProvider,
)
from web3.providers.rpc import (
    AsyncHTTPProvider,
)
from web3.types import (
    RPCEndpoint,
    RPCResponse,
)

HTTP_SCHEMES = {"http", "https"}
WS_SCHEMES = {"ws", "wss"}


def load_provider_from_environment() -> JSONBaseProvider | None:
    """
    Load a synchronous provider from the WEB3_PROVIDER_URI environment variable.

    Returns
    -------
    JSONBaseProvider | None
        JSONBaseProvider or None if the environment variable is not set.

    Raises
    ------
    Web3ValidationError
        If the URI contains a WebSocket scheme (ws/wss),
        which requires AsyncAutoProvider.

    """
    uri_string = URI(os.environ.get("WEB3_PROVIDER_URI", ""))
    if not uri_string:
        return None

    return load_provider_from_uri(uri_string)


def load_provider_from_uri(
    uri_string: URI, headers: dict[str, tuple[str, str]] | None = None
) -> JSONBaseProvider:
    """
    Create a synchronous provider based on a URI string.

    Parameters
    ----------
    uri_string : URI
        URI string for connecting to the node.
    headers : dict[str, tuple[str, str]] | None, optional
        Optional HTTP headers for HTTPProvider.

    Returns
    -------
    JSONBaseProvider
        An instance of JSONBaseProvider (IPCProvider or HTTPProvider).

    Raises
    ------
    Web3ValidationError
        If the URI contains a WebSocket scheme (ws/wss).
    NotImplementedError
        If the URI scheme is not supported.

    """
    uri = urlparse(uri_string)

    if uri.scheme == "file":
        return IPCProvider(uri.path)
    elif uri.scheme in HTTP_SCHEMES:
        return HTTPProvider(uri_string, headers)
    elif uri.scheme in WS_SCHEMES:
        raise Web3ValidationError(
            f"WebSocket URI '{uri_string}' requires an async provider. "
            "Use AsyncAutoProvider with AsyncWeb3 instead of AutoProvider with Web3. "
            "Example: async with AsyncWeb3(AsyncAutoProvider()) as w3: ..."
        )
    else:
        raise NotImplementedError(
            "Web3 does not know how to connect to scheme "
            f"{uri.scheme!r} in {uri_string!r}"
        )


def load_async_provider_from_environment() -> AsyncJSONBaseProvider | None:
    """
    Load an asynchronous provider from environment variables.

    Checks WEB3_PROVIDER_URI and WEB3_WS_PROVIDER_URI.

    Returns
    -------
    AsyncJSONBaseProvider | None
        AsyncJSONBaseProvider or None if no environment variables are set.

    """
    # First check the main environment variable
    uri_string = URI(os.environ.get("WEB3_PROVIDER_URI", ""))
    if uri_string:
        return load_async_provider_from_uri(uri_string)

    # Then check the WebSocket-specific variable
    ws_uri_string = URI(os.environ.get("WEB3_WS_PROVIDER_URI", ""))
    if ws_uri_string:
        return load_async_provider_from_uri(ws_uri_string)

    return None


def load_async_provider_from_uri(
    uri_string: URI, headers: dict[str, tuple[str, str]] | None = None
) -> AsyncJSONBaseProvider:
    """
    Create an asynchronous provider based on a URI string.

    Parameters
    ----------
    uri_string : URI
        URI string for connecting to the node.
    headers : dict[str, tuple[str, str]] | None, optional
        Optional HTTP headers for AsyncHTTPProvider.

    Returns
    -------
    AsyncJSONBaseProvider
        An instance of AsyncJSONBaseProvider.

    Raises
    ------
    NotImplementedError
        If the URI scheme is not supported.

    Note
    ----
    WebSocket providers (ws/wss) require using AsyncWeb3
    with a context manager for proper connection management:
    ``async with AsyncWeb3(WebSocketProvider(uri)) as w3: ...``

    """
    # Import here to avoid circular imports
    from web3.providers.persistent import (
        WebSocketProvider,
    )

    uri = urlparse(uri_string)

    if uri.scheme == "file":
        # For IPC use AsyncIPCProvider
        from web3.providers.persistent import (
            AsyncIPCProvider,
        )

        return AsyncIPCProvider(uri.path)
    elif uri.scheme in HTTP_SCHEMES:
        return AsyncHTTPProvider(uri_string)
    elif uri.scheme in WS_SCHEMES:
        return WebSocketProvider(uri_string)
    else:
        raise NotImplementedError(
            "Web3 does not know how to connect to scheme "
            f"{uri.scheme!r} in {uri_string!r}"
        )


def _is_async_provider(provider: Any) -> bool:
    """
    Check if a provider is asynchronous.

    Parameters
    ----------
    provider : Any
        The provider object to check.

    Returns
    -------
    bool
        True if the provider is asynchronous.

    """
    return getattr(provider, "is_async", False)


class AutoProvider(JSONBaseProvider):
    """
    Provider that automatically detects available synchronous providers.

    AutoProvider iterates through a list of potential providers and uses
    the first one that successfully connects to a node.

    Attributes
    ----------
    default_providers : tuple
        Tuple of default provider functions/classes.

    Example
    -------
        >>> from web3 import Web3
        >>> w3 = Web3(AutoProvider())
        >>> # or simply
        >>> w3 = Web3()  # AutoProvider is used by default

    Note
    ----
    For WebSocket connections, use AsyncAutoProvider with AsyncWeb3.

    """

    default_providers = (
        load_provider_from_environment,
        IPCProvider,
        HTTPProvider,
    )
    _active_provider: JSONBaseProvider | None = None

    def __init__(
        self,
        potential_providers: None
        | (Sequence[Callable[..., JSONBaseProvider] | type[JSONBaseProvider]]) = None,
    ) -> None:
        """
        Initialize AutoProvider.

        Parameters
        ----------
        potential_providers : Sequence | None, optional
            Ordered sequence of provider classes or functions to attempt connection
            with. If not specified, default_providers is used.

        Note
        ----
        AutoProvider initializes each potential provider (without arguments)
        in an attempt to find an active node.

        """
        super().__init__()
        if potential_providers:
            self._potential_providers = potential_providers
        else:
            self._potential_providers = self.default_providers

    def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        """
        Execute an RPC request through the active provider.

        Parameters
        ----------
        method : RPCEndpoint
            RPC method to call.
        params : Any
            Parameters for the RPC method.

        Returns
        -------
        RPCResponse
            Response from the provider.

        Raises
        ------
        CannotHandleRequest
            If no active provider could be found.

        """
        try:
            return self._proxy_request(method, params)
        except OSError:
            return self._proxy_request(method, params, use_cache=False)

    def make_batch_request(
        self, requests: list[tuple[RPCEndpoint, Any]]
    ) -> list[RPCResponse] | RPCResponse:
        """
        Execute a batch RPC request through the active provider.

        Parameters
        ----------
        requests : list[tuple[RPCEndpoint, Any]]
            List of (method, params) tuples.

        Returns
        -------
        list[RPCResponse] | RPCResponse
            List of responses or a single error response.

        Raises
        ------
        CannotHandleRequest
            If no active provider could be found.

        """
        try:
            return self._proxy_batch_request(requests)
        except OSError:
            return self._proxy_batch_request(requests, use_cache=False)

    def is_connected(self, show_traceback: bool = False) -> bool:
        """
        Check if the provider is connected to a node.

        Parameters
        ----------
        show_traceback : bool, optional
            If True, show traceback on error.

        Returns
        -------
        bool
            True if the connection is active.

        """
        provider = self._get_active_provider(use_cache=True)
        return provider is not None and provider.is_connected(show_traceback)

    def _proxy_request(
        self, method: RPCEndpoint, params: Any, use_cache: bool = True
    ) -> RPCResponse:
        """
        Proxy the request to the active provider.

        Parameters
        ----------
        method : RPCEndpoint
            RPC method.
        params : Any
            Method parameters.
        use_cache : bool, optional
            Whether to use the cached provider.

        Returns
        -------
        RPCResponse
            Response from the provider.

        Raises
        ------
        CannotHandleRequest
            If no provider is found.

        """
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
        """
        Proxy the batch request to the active provider.

        Parameters
        ----------
        requests : list[tuple[RPCEndpoint, Any]]
            List of requests.
        use_cache : bool, optional
            Whether to use the cached provider.

        Returns
        -------
        list[RPCResponse] | RPCResponse
            Responses from the provider.

        Raises
        ------
        CannotHandleRequest
            If no provider is found.

        """
        provider = self._get_active_provider(use_cache)
        if provider is None:
            raise CannotHandleRequest(
                "Could not discover provider while making batch request: "
                f"requests:{requests}\n"
            )

        return provider.make_batch_request(requests)

    def _get_active_provider(self, use_cache: bool) -> JSONBaseProvider | None:
        """
        Find and return the active provider.

        Parameters
        ----------
        use_cache : bool
            Whether to use the cached provider.

        Returns
        -------
        JSONBaseProvider | None
            Active provider or None.

        Raises
        ------
        Web3ValidationError
            If an async provider is discovered.

        """
        if use_cache and self._active_provider is not None:
            return self._active_provider

        for Provider in self._potential_providers:
            provider = Provider()
            if provider is None:
                continue

            # Verify that the provider is not asynchronous
            if _is_async_provider(provider):
                raise Web3ValidationError(
                    f"AutoProvider discovered an async provider ({type(provider).__name__}), "  # noqa: E501
                    "but AutoProvider only supports sync providers. "
                    "Use AsyncAutoProvider with AsyncWeb3 for async providers."
                )

            if provider.is_connected():
                self._active_provider = provider
                return provider

        return None


class AsyncAutoProvider(AsyncJSONBaseProvider):
    """
    Asynchronous provider that automatically detects available async providers.

    AsyncAutoProvider iterates through a list of potential providers and uses
    the first one that successfully connects to a node.

    Attributes
    ----------
    default_providers : tuple
        Tuple of default provider functions/classes.

    Example
    -------
        >>> from web3 import AsyncWeb3
        >>> from web3.providers.auto import AsyncAutoProvider
        >>>
        >>> async def main():
        ...     w3 = AsyncWeb3(AsyncAutoProvider())
        ...     if await w3.is_connected():
        ...         print(await w3.eth.block_number)

    Note
    ----
    For WebSocket providers that require explicit connect/disconnect,
    it is recommended to use a context manager or explicitly manage
    the connection.

    """

    default_providers = (
        load_async_provider_from_environment,
        AsyncHTTPProvider,
    )
    _active_provider: AsyncJSONBaseProvider | None = None

    def __init__(
        self,
        potential_providers: None
        | (
            Sequence[Callable[..., AsyncJSONBaseProvider] | type[AsyncJSONBaseProvider]]
        ) = None,
    ) -> None:
        """
        Initialize AsyncAutoProvider.

        Parameters
        ----------
        potential_providers : Sequence | None, optional
            Ordered sequence of provider classes or functions to attempt connection
            with. If not specified, default_providers is used.

        """
        super().__init__()
        if potential_providers:
            self._potential_providers = potential_providers
        else:
            self._potential_providers = self.default_providers

    async def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        """
        Execute an asynchronous RPC request through the active provider.

        Parameters
        ----------
        method : RPCEndpoint
            RPC method to call.
        params : Any
            Parameters for the RPC method.

        Returns
        -------
        RPCResponse
            Response from the provider.

        Raises
        ------
        CannotHandleRequest
            If no active provider could be found.

        """
        try:
            return await self._proxy_request(method, params)
        except OSError:
            return await self._proxy_request(method, params, use_cache=False)

    async def make_batch_request(
        self, requests: list[tuple[RPCEndpoint, Any]]
    ) -> list[RPCResponse] | RPCResponse:
        """
        Execute an asynchronous batch RPC request through the active provider.

        Parameters
        ----------
        requests : list[tuple[RPCEndpoint, Any]]
            List of (method, params) tuples.

        Returns
        -------
        list[RPCResponse] | RPCResponse
            List of responses or a single error response.

        Raises
        ------
        CannotHandleRequest
            If no active provider could be found.

        """
        try:
            return await self._proxy_batch_request(requests)
        except OSError:
            return await self._proxy_batch_request(requests, use_cache=False)

    async def is_connected(self, show_traceback: bool = False) -> bool:
        """
        Check if the provider is connected to a node.

        Parameters
        ----------
        show_traceback : bool, optional
            If True, show traceback on error.

        Returns
        -------
        bool
            True if the connection is active.

        """
        provider = await self._get_active_provider(use_cache=True)
        if provider is None:
            return False
        return await provider.is_connected(show_traceback)

    async def _proxy_request(
        self, method: RPCEndpoint, params: Any, use_cache: bool = True
    ) -> RPCResponse:
        """
        Proxy the request to the active provider.

        Parameters
        ----------
        method : RPCEndpoint
            RPC method.
        params : Any
            Method parameters.
        use_cache : bool, optional
            Whether to use the cached provider.

        Returns
        -------
        RPCResponse
            Response from the provider.

        Raises
        ------
        CannotHandleRequest
            If no provider is found.

        """
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
        """
        Proxy the batch request to the active provider.

        Parameters
        ----------
        requests : list[tuple[RPCEndpoint, Any]]
            List of requests.
        use_cache : bool, optional
            Whether to use the cached provider.

        Returns
        -------
        list[RPCResponse] | RPCResponse
            Responses from the provider.

        Raises
        ------
        CannotHandleRequest
            If no provider is found.

        """
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
        """
        Find and return the active asynchronous provider.

        Parameters
        ----------
        use_cache : bool
            Whether to use the cached provider.

        Returns
        -------
        AsyncJSONBaseProvider | None
            Active provider or None.

        Raises
        ------
        Web3ValidationError
            If a sync provider is discovered.

        """
        if use_cache and self._active_provider is not None:
            return self._active_provider

        for Provider in self._potential_providers:
            provider = Provider()
            if provider is None:
                continue

            # Verify that the provider is asynchronous
            if not _is_async_provider(provider):
                raise Web3ValidationError(
                    f"AsyncAutoProvider discovered a sync provider "
                    f"({type(provider).__name__}), but AsyncAutoProvider only "
                    "supports async providers. Use AutoProvider with Web3 for "
                    "sync providers."
                )

            if await provider.is_connected():
                self._active_provider = provider
                return provider

        return None
