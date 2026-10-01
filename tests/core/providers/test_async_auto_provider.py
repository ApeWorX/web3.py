import pytest
import sys

from aiohttp import (
    web,
)

from web3 import (
    AsyncWeb3,
)
from web3.exceptions import (
    CannotHandleRequest,
    ProviderConnectionError,
)
from web3.providers import (
    AsyncHTTPProvider,
    AsyncIPCProvider,
    WebSocketProvider,
)
from web3.providers.async_base import (
    AsyncJSONBaseProvider,
)
from web3.providers.auto import (
    AsyncAutoProvider,
    async_load_provider_from_environment,
)


@pytest.fixture(autouse=True)
def delete_provider_uri(monkeypatch):
    monkeypatch.delenv("WEB3_PROVIDER_URI", raising=False)


class FakeAsyncProvider(AsyncJSONBaseProvider):
    connected = True

    def __init__(self) -> None:
        super().__init__()
        self.disconnect_calls = 0

    async def make_request(self, method, params):
        return {"jsonrpc": "2.0", "id": 0, "result": f"{method}:{type(self).__name__}"}

    async def make_batch_request(self, requests):
        return [await self.make_request(method, params) for method, params in requests]

    async def is_connected(self, show_traceback: bool = False) -> bool:
        return self.connected

    async def disconnect(self) -> None:
        self.disconnect_calls += 1


class DisconnectedAsyncProvider(FakeAsyncProvider):
    connected = False


class RaisingAsyncProvider(FakeAsyncProvider):
    async def is_connected(self, show_traceback: bool = False) -> bool:
        raise ProviderConnectionError("cannot reach node")


class FakePersistentProvider(FakeAsyncProvider):
    has_persistent_connection = True

    def __init__(self) -> None:
        super().__init__()
        self.connect_calls = 0

    async def connect(self) -> None:
        self.connect_calls += 1


def _recording(provider_class, created):
    def factory():
        provider = provider_class()
        created.append(provider)
        return provider

    return factory


def test_async_web3_defaults_to_async_auto_provider():
    w3 = AsyncWeb3()
    assert type(w3.provider) is AsyncAutoProvider


@pytest.mark.asyncio
async def test_async_auto_provider_uses_first_connected_provider():
    created = []
    auto = AsyncAutoProvider(
        potential_providers=(
            lambda: None,
            _recording(DisconnectedAsyncProvider, created),
            _recording(FakeAsyncProvider, created),
        )
    )

    assert await auto.is_connected()
    response = await auto.make_request("eth_chainId", [])
    assert response["result"] == "eth_chainId:FakeAsyncProvider"

    disconnected, connected = created
    # the provider that could not connect is cleaned up, the active one is not
    assert disconnected.disconnect_calls == 1
    assert connected.disconnect_calls == 0


@pytest.mark.asyncio
async def test_async_auto_provider_skips_providers_that_raise():
    created = []
    auto = AsyncAutoProvider(
        potential_providers=(
            _recording(RaisingAsyncProvider, created),
            FakeAsyncProvider,
        )
    )

    assert await auto.is_connected()
    assert created[0].disconnect_calls == 1


@pytest.mark.asyncio
async def test_async_auto_provider_connects_persistent_providers():
    created = []
    auto = AsyncAutoProvider(
        potential_providers=(_recording(FakePersistentProvider, created),)
    )

    assert await auto.is_connected()
    assert created[0].connect_calls == 1

    await auto.disconnect()
    assert created[0].disconnect_calls == 1
    assert auto._active_provider is None


@pytest.mark.asyncio
async def test_async_auto_provider_batch_request():
    auto = AsyncAutoProvider(potential_providers=(FakeAsyncProvider,))

    responses = await auto.make_batch_request(
        [("eth_chainId", []), ("eth_blockNumber", [])]
    )
    assert [r["result"] for r in responses] == [
        "eth_chainId:FakeAsyncProvider",
        "eth_blockNumber:FakeAsyncProvider",
    ]


@pytest.mark.asyncio
async def test_async_auto_provider_no_provider_found():
    auto = AsyncAutoProvider(potential_providers=(DisconnectedAsyncProvider,))

    assert not await auto.is_connected()
    with pytest.raises(CannotHandleRequest):
        await auto.make_request("eth_chainId", [])
    with pytest.raises(CannotHandleRequest):
        await auto.make_batch_request([("eth_chainId", [])])


@pytest.mark.parametrize(
    "uri, expected_type, expected_attrs",
    (
        ("", type(None), {}),
        (
            "http://1.2.3.4:5678",
            AsyncHTTPProvider,
            {"endpoint_uri": "http://1.2.3.4:5678"},
        ),
        (
            "https://node.ontheweb.com",
            AsyncHTTPProvider,
            {"endpoint_uri": "https://node.ontheweb.com"},
        ),
        (
            "ws://1.2.3.4:5679",
            WebSocketProvider,
            {"endpoint_uri": "ws://1.2.3.4:5679"},
        ),
        (
            "wss://node.ontheweb.com",
            WebSocketProvider,
            {"endpoint_uri": "wss://node.ontheweb.com"},
        ),
        pytest.param(
            "file:///root/path/to/file.ipc",
            AsyncIPCProvider,
            {"ipc_path": "/root/path/to/file.ipc"},
            marks=pytest.mark.skipif(
                sys.platform == "win32",
                reason="Unix domain sockets are not supported on Windows",
            ),
        ),
    ),
)
def test_async_load_provider_from_env(monkeypatch, uri, expected_type, expected_attrs):
    monkeypatch.setenv("WEB3_PROVIDER_URI", uri)
    provider = async_load_provider_from_environment()
    assert isinstance(provider, expected_type)
    for attr, val in expected_attrs.items():
        assert getattr(provider, attr) == val


@pytest.mark.asyncio
async def test_async_web3_auto_provider_connects_to_http_node_from_environment(
    monkeypatch,
):
    async def handle(request):
        body = await request.json()
        return web.json_response(
            {"jsonrpc": "2.0", "id": body["id"], "result": "0x539"}
        )

    app = web.Application()
    app.router.add_post("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    try:
        monkeypatch.setenv("WEB3_PROVIDER_URI", f"http://127.0.0.1:{port}")
        w3 = AsyncWeb3()

        assert await w3.is_connected()
        assert await w3.eth.chain_id == 1337
        assert isinstance(w3.provider._active_provider, AsyncHTTPProvider)

        await w3.provider.disconnect()
        assert w3.provider._active_provider is None
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
async def test_async_auto_provider_unreachable_ipc_fails_fast(tmp_path):
    missing_ipc = str(tmp_path / "missing.ipc")
    auto = AsyncAutoProvider(
        potential_providers=(
            lambda: AsyncIPCProvider(missing_ipc, max_connection_retries=1),
        )
    )

    assert not await auto.is_connected()
