import pytest
from unittest.mock import (
    AsyncMock,
    patch,
)

from aiohttp import (
    ClientSession,
)

from web3 import (
    AsyncWeb3,
    __version__ as web3py_version,
)
from web3.eth import (
    AsyncEth,
)
from web3.exceptions import (
    ProviderConnectionError,
    Web3RPCError,
)
from web3.geth import (
    AsyncGeth,
    AsyncGethAdmin,
    AsyncGethTxPool,
)
from web3.middleware import (
    AttributeDictMiddleware,
    BufferedGasEstimateMiddleware,
    ENSNameToAddressMiddleware,
    GasPriceStrategyMiddleware,
    ValidationMiddleware,
)
from web3.net import (
    AsyncNet,
)
from web3.providers.rpc import (
    AsyncHTTPProvider,
)

URI = "http://mynode.local:8545"


class AsyncMockedHTTPErrorResponse:
    """A non-2xx `aiohttp` response, mimicking a provider HTTP error."""

    def __init__(self, body: bytes, status: int = 400):
        self.status = status
        self.ok = 200 <= status < 400
        self._body = body

    def __await__(self):
        yield
        return self

    async def read(self):
        return self._body

    def raise_for_status(self) -> None:
        raise Exception("called raise_for_status()")  # noqa: E704


@pytest.mark.asyncio
async def test_async_no_args() -> None:
    provider = AsyncHTTPProvider()
    w3 = AsyncWeb3(provider)
    assert w3.manager.provider == provider
    assert w3.manager.provider.is_async
    assert not await w3.is_connected()
    with pytest.raises(ProviderConnectionError):
        await w3.is_connected(show_traceback=True)
    for cached_items in provider._request_session_manager.session_cache.items():
        cache_key, session = cached_items
        await session.close()


def test_init_kwargs():
    provider = AsyncHTTPProvider(endpoint_uri=URI, request_kwargs={"timeout": 60})
    w3 = AsyncWeb3(provider)
    assert w3.manager.provider == provider


def test_web3_with_async_http_provider_has_default_middleware_and_modules() -> None:
    async_w3 = AsyncWeb3(AsyncHTTPProvider(endpoint_uri=URI))

    # assert default modules

    assert isinstance(async_w3.eth, AsyncEth)
    assert isinstance(async_w3.net, AsyncNet)
    assert isinstance(async_w3.geth, AsyncGeth)
    assert isinstance(async_w3.geth.admin, AsyncGethAdmin)
    assert isinstance(async_w3.geth.txpool, AsyncGethTxPool)

    # assert default middleware

    # the following length check should fail and will need to be added to once more
    # async middleware are added to the defaults
    assert len(async_w3.middleware_onion.middleware) == 5

    assert (
        async_w3.middleware_onion.get("gas_price_strategy")
        == GasPriceStrategyMiddleware
    )
    assert (
        async_w3.middleware_onion.get("ens_name_to_address")
        == ENSNameToAddressMiddleware
    )
    assert async_w3.middleware_onion.get("attrdict") == AttributeDictMiddleware
    assert async_w3.middleware_onion.get("validation") == ValidationMiddleware
    assert (
        async_w3.middleware_onion.get("gas_estimate") == BufferedGasEstimateMiddleware
    )


@pytest.mark.asyncio
async def test_async_user_provided_session() -> None:
    session = ClientSession()
    provider = AsyncHTTPProvider(endpoint_uri=URI)
    cached_session = await provider.cache_async_session(session)
    assert len(provider._request_session_manager.session_cache) == 1
    assert cached_session == session
    await session.close()


@pytest.mark.parametrize("provider", (AsyncHTTPProvider(), AsyncHTTPProvider))
def test_get_request_headers(provider):
    headers = provider.get_request_headers()
    assert len(headers) == 2
    assert headers["Content-Type"] == "application/json"
    assert (
        headers["User-Agent"] == f"web3.py/{web3py_version}/"
        f"{AsyncHTTPProvider.__module__}.{AsyncHTTPProvider.__qualname__}"
    )


@patch(
    "web3._utils.http_session_manager.HTTPSessionManager.async_make_post_request",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_async_http_empty_batch_response(mock_async_post):
    mock_async_post.return_value = (
        b'{"jsonrpc":"2.0","id":null,"error":{"code":-32600,"message":"empty batch"}}'
    )
    async_w3 = AsyncWeb3(AsyncHTTPProvider())
    async with async_w3.batch_requests() as batch:
        with pytest.raises(Web3RPCError, match="empty batch"):
            await batch.async_execute()

    assert not async_w3.provider._is_batching


@patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_async_http_provider_surfaces_rpc_error_on_http_error_response(
    mock_post,
):
    # Regression test for https://github.com/ethereum/web3.py/issues/3915 :
    # a provider that answers a JSON-RPC error with a non-2xx HTTP status
    # should surface the JSON-RPC error, not a bare HTTP error.
    mock_post.return_value = AsyncMockedHTTPErrorResponse(
        b'{"jsonrpc":"2.0","id":0,'
        b'"error":{"code":-32602,"message":"Log response size exceeded."}}'
    )
    async_w3 = AsyncWeb3(AsyncHTTPProvider(endpoint_uri=URI))
    with pytest.raises(Web3RPCError, match="Log response size exceeded"):
        await async_w3.eth.get_logs({"fromBlock": 0, "toBlock": 1000000})

    # -- teardown -- #
    for _, session in async_w3.provider._request_session_manager.session_cache.items():
        await session.close()
