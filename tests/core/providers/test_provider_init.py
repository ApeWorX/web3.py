import pytest

from web3 import (
    AsyncBaseProvider,
    AsyncEthereumTesterProvider,
    AsyncHTTPProvider,
    AsyncIPCProvider,
    AsyncWeb3,
    BaseProvider,
    EthereumTesterProvider,
    HTTPProvider,
    IPCProvider,
    Web3,
    WebSocketProvider,
)
from web3.exceptions import (
    Web3ValidationError,
)


class ExtendsAsyncBaseProvider(AsyncBaseProvider):
    pass


class ExtendsBaseProvider(BaseProvider):
    pass


@pytest.mark.parametrize(
    "provider_class",
    (
        AsyncBaseProvider,
        ExtendsAsyncBaseProvider,
        AsyncHTTPProvider,
        AsyncIPCProvider,
        WebSocketProvider,
        AsyncEthereumTesterProvider,
    ),
)
def test_init_web3_with_async_provider(provider_class):
    with pytest.raises(Web3ValidationError):
        Web3(provider_class())


@pytest.mark.parametrize(
    "provider_class",
    (
        BaseProvider,
        ExtendsBaseProvider,
        HTTPProvider,
        IPCProvider,
        EthereumTesterProvider,
    ),
)
def test_init_async_web3_with_sync_provider(provider_class):
    with pytest.raises(Web3ValidationError):
        AsyncWeb3(provider_class())


def test_async_web3_exposes_async_ipc_provider():
    assert AsyncWeb3.AsyncIPCProvider is AsyncIPCProvider
