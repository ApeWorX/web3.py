import pytest
import os
import sys

from web3.exceptions import (
    Web3ValidationError,
)
from web3.providers import (
    AsyncAutoProvider,
    AsyncHTTPProvider,
    HTTPProvider,
    IPCProvider,
    WebSocketProvider,
)
from web3.providers.auto import (
    load_async_provider_from_environment,
    load_async_provider_from_uri,
    load_provider_from_environment,
    load_provider_from_uri,
)
from web3.providers.ipc import (
    get_dev_ipc_path,
)

# Ugly hack to import infura now that API KEY is required
os.environ["WEB3_INFURA_PROJECT_ID"] = "test"


@pytest.fixture(autouse=True)
def delete_environment_variables(monkeypatch):
    monkeypatch.delenv("WEB3_INFURA_PROJECT_ID", raising=False)
    monkeypatch.delenv("WEB3_INFURA_API_SECRET", raising=False)
    monkeypatch.delenv("WEB3_INFURA_SCHEME", raising=False)


@pytest.mark.parametrize(
    "uri, expected_type, expected_attrs",
    (
        ("", type(None), {}),
        ("http://1.2.3.4:5678", HTTPProvider, {"endpoint_uri": "http://1.2.3.4:5678"}),
        (
            "https://node.ontheweb.com",
            HTTPProvider,
            {"endpoint_uri": "https://node.ontheweb.com"},
        ),
        pytest.param(
            "file:///root/path/to/file.ipc",
            IPCProvider,
            {"ipc_path": "/root/path/to/file.ipc"},
            marks=pytest.mark.skipif(
                sys.platform == "win32",
                reason="Unix domain sockets are not supported on Windows",
            ),
        ),
    ),
)
def test_load_provider_from_env(monkeypatch, uri, expected_type, expected_attrs):
    monkeypatch.setenv("WEB3_PROVIDER_URI", uri)
    provider = load_provider_from_environment()
    assert isinstance(provider, expected_type)
    for attr, val in expected_attrs.items():
        assert getattr(provider, attr) == val


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix domain sockets are not supported on Windows"
)
def test_get_dev_ipc_path(monkeypatch, tmp_path):
    # test default path
    monkeypatch.delenv("TMPDIR", raising=False)
    path = get_dev_ipc_path()
    assert path == "/tmp/geth.ipc"

    uri = str(tmp_path) + "/geth.ipc"

    # test setting the "TMPDIR" environment variable
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    path = get_dev_ipc_path()
    assert path == uri
    monkeypatch.delenv("TMPDIR")  # reset

    # test with WEB3_PROVIDER_URI set
    monkeypatch.setenv("WEB3_PROVIDER_URI", uri)
    path = get_dev_ipc_path()
    assert path == uri


@pytest.mark.parametrize(
    "ws_uri",
    (
        "ws://localhost:8546",
        "wss://mainnet.infura.io/ws/v3/YOUR_KEY",
    ),
)
def test_load_provider_from_uri_raises_for_websocket(ws_uri):
    """
    Test that load_provider_from_uri raises Web3ValidationError for ws/wss URIs.

    WebSocket requires async provider, so sync load_provider_from_uri should fail.
    """
    with pytest.raises(Web3ValidationError) as exc_info:
        load_provider_from_uri(ws_uri)

    assert "WebSocket URI" in str(exc_info.value)
    assert "AsyncAutoProvider" in str(exc_info.value)


def test_load_provider_from_env_raises_for_websocket(monkeypatch):
    """
    Test that load_provider_from_environment raises for WebSocket URIs.
    """
    monkeypatch.setenv("WEB3_PROVIDER_URI", "ws://localhost:8546")
    with pytest.raises(Web3ValidationError):
        load_provider_from_environment()


@pytest.mark.parametrize(
    "uri, expected_type",
    (
        ("http://1.2.3.4:5678", AsyncHTTPProvider),
        ("https://node.ontheweb.com", AsyncHTTPProvider),
        ("ws://localhost:8546", WebSocketProvider),
        ("wss://mainnet.infura.io/ws/v3/KEY", WebSocketProvider),
    ),
)
def test_load_async_provider_from_uri(uri, expected_type):
    """
    Test that load_async_provider_from_uri correctly identifies provider types.
    """
    provider = load_async_provider_from_uri(uri)
    assert isinstance(provider, expected_type)


@pytest.mark.parametrize(
    "uri, expected_type, env_var",
    (
        ("http://1.2.3.4:5678", AsyncHTTPProvider, "WEB3_PROVIDER_URI"),
        ("ws://localhost:8546", WebSocketProvider, "WEB3_PROVIDER_URI"),
        ("wss://localhost:8546", WebSocketProvider, "WEB3_WS_PROVIDER_URI"),
    ),
)
def test_load_async_provider_from_env(monkeypatch, uri, expected_type, env_var):
    """
    Test that load_async_provider_from_environment correctly loads async providers.
    """
    monkeypatch.setenv(env_var, uri)
    provider = load_async_provider_from_environment()
    assert isinstance(provider, expected_type)


def test_load_async_provider_from_env_returns_none(monkeypatch):
    """
    Test that load_async_provider_from_environment returns None when no env vars set.
    """
    monkeypatch.delenv("WEB3_PROVIDER_URI", raising=False)
    monkeypatch.delenv("WEB3_WS_PROVIDER_URI", raising=False)
    provider = load_async_provider_from_environment()
    assert provider is None


def test_async_auto_provider_default_providers():
    """
    Test that AsyncAutoProvider has correct default providers.
    """
    provider = AsyncAutoProvider()
    assert provider._potential_providers is not None
    assert len(provider._potential_providers) > 0


def test_async_auto_provider_custom_providers():
    """
    Test that AsyncAutoProvider accepts custom providers.
    """
    custom_providers = (AsyncHTTPProvider,)
    provider = AsyncAutoProvider(potential_providers=custom_providers)
    assert provider._potential_providers == custom_providers


def test_async_auto_provider_is_async():
    """
    Test that AsyncAutoProvider is marked as async.
    """
    provider = AsyncAutoProvider()
    assert provider.is_async is True
