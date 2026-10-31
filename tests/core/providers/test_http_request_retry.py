import pytest
from unittest.mock import (
    patch,
)

import aiohttp
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
    HTTPError,
    Timeout,
    TooManyRedirects,
)

from web3 import (
    AsyncHTTPProvider,
    AsyncWeb3,
    Web3,
    WebSocketProvider,
)
from web3.providers import (
    HTTPProvider,
    IPCProvider,
)
from web3.providers.rpc.utils import (
    ExceptionRetryConfiguration,
    check_if_retry_on_failure,
)
from web3.types import (
    RPCEndpoint,
)

TEST_RETRY_COUNT = 3


@pytest.fixture
def w3():
    errors = (ConnectionError, HTTPError, Timeout, TooManyRedirects)
    config = ExceptionRetryConfiguration(errors=errors, retries=TEST_RETRY_COUNT)
    return Web3(HTTPProvider(exception_retry_configuration=config))


def test_default_request_retry_configuration_for_http_provider():
    w3 = Web3(HTTPProvider())
    assert w3.provider.exception_retry_configuration == ExceptionRetryConfiguration(
        errors=(
            RequestsConnectionError,
            HTTPError,
            Timeout,
        )
    )


@pytest.mark.parametrize(
    "error",
    (
        # requests raises its own ConnectionError, not the builtin one
        RequestsConnectionError,
        HTTPError,
        Timeout,
    ),
)
def test_default_request_retry_configuration_retries_requests_errors(error):
    w3 = Web3(HTTPProvider())
    retries = w3.provider.exception_retry_configuration.retries

    with patch(
        "web3.providers.rpc.rpc.HTTPSessionManager.make_post_request"
    ) as make_post_request_mock:
        make_post_request_mock.side_effect = error

        with patch("web3.providers.rpc.rpc.time.sleep"):
            with pytest.raises(error):
                w3.provider.make_request(
                    RPCEndpoint("eth_getBalance"), [f"0x{'00' * 20}"]
                )
        assert make_post_request_mock.call_count == retries


def test_check_without_retry_config():
    w3 = Web3(HTTPProvider(exception_retry_configuration=None))

    with patch(
        "web3.providers.rpc.rpc.HTTPSessionManager.make_post_request"
    ) as make_post_request_mock:
        make_post_request_mock.side_effect = Timeout

        with pytest.raises(Timeout):
            w3.eth.block_number
        assert make_post_request_mock.call_count == 1


def test_check_if_retry_on_failure_false():
    assert not check_if_retry_on_failure("eth_sendTransaction")


def test_check_if_retry_on_failure_true():
    method = "eth_getBalance"
    assert check_if_retry_on_failure(method)


@patch(
    "web3.providers.rpc.rpc.HTTPSessionManager.make_post_request",
    side_effect=ConnectionError,
)
def test_check_send_transaction_called_once(make_post_request_mock, w3):
    with pytest.raises(ConnectionError):
        w3.provider.make_request(
            RPCEndpoint("eth_sendTransaction"), [{"to": f"0x{'00' * 20}", "value": 1}]
        )
    assert make_post_request_mock.call_count == 1


@patch(
    "web3.providers.rpc.rpc.HTTPSessionManager.make_post_request",
    side_effect=ConnectionError,
)
def test_valid_method_retried(make_post_request_mock, w3):
    with pytest.raises(ConnectionError):
        w3.provider.make_request(RPCEndpoint("eth_getBalance"), [f"0x{'00' * 20}"])
    assert make_post_request_mock.call_count == TEST_RETRY_COUNT


def test_exception_retry_config_is_strictly_on_http_provider():
    w3 = Web3(HTTPProvider())
    assert hasattr(w3.provider, "exception_retry_configuration")

    w3 = Web3(IPCProvider())
    assert not hasattr(w3.provider, "exception_retry_configuration")

    w3 = AsyncWeb3(WebSocketProvider("ws://localhost:8546"))
    assert not hasattr(w3.provider, "exception_retry_configuration")


@patch(
    "web3.providers.rpc.rpc.HTTPSessionManager.make_post_request",
    side_effect=ConnectionError,
)
def test_exception_retry_middleware_with_allow_list_kwarg(make_post_request_mock):
    config = ExceptionRetryConfiguration(
        errors=(ConnectionError, HTTPError, Timeout, TooManyRedirects),
        retries=TEST_RETRY_COUNT,
        method_allowlist=["test_userProvidedMethod"],
    )
    w3 = Web3(HTTPProvider(exception_retry_configuration=config))

    with pytest.raises(ConnectionError):
        w3.provider.make_request(RPCEndpoint("test_userProvidedMethod"), [])
        assert make_post_request_mock.call_count == TEST_RETRY_COUNT

    make_post_request_mock.reset_mock()
    with pytest.raises(ConnectionError):
        w3.provider.make_request(RPCEndpoint("eth_getBalance"), [])
        assert make_post_request_mock.call_count == 1


# -- async -- #


@pytest.fixture
def async_w3():
    errors = (aiohttp.ClientError, TimeoutError)
    config = ExceptionRetryConfiguration(errors=errors, retries=TEST_RETRY_COUNT)
    return AsyncWeb3(AsyncHTTPProvider(exception_retry_configuration=config))


@pytest.mark.asyncio
async def test_async_default_request_retry_configuration_for_http_provider():
    async_w3 = AsyncWeb3(AsyncHTTPProvider())
    assert (
        async_w3.provider.exception_retry_configuration
        == ExceptionRetryConfiguration(errors=(aiohttp.ClientError, TimeoutError))
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    (
        TimeoutError,
        aiohttp.ClientError,  # general base class for all aiohttp errors
        # ClientError subclasses
        aiohttp.ClientConnectionError,
        aiohttp.ServerTimeoutError,
        aiohttp.ClientOSError,
    ),
)
async def test_async_check_retry_middleware(async_w3, error):
    with patch(
        "web3.providers.rpc.async_rpc.HTTPSessionManager.async_make_post_request"
    ) as async_make_post_request_mock:
        async_make_post_request_mock.side_effect = error

        with pytest.raises(error):
            await async_w3.provider.make_request(RPCEndpoint("eth_getBalance"), [])
        assert async_make_post_request_mock.call_count == TEST_RETRY_COUNT


@pytest.mark.asyncio
async def test_async_check_without_retry_config():
    w3 = AsyncWeb3(AsyncHTTPProvider(exception_retry_configuration=None))

    with patch(
        "web3.providers.rpc.async_rpc.HTTPSessionManager.async_make_post_request"
    ) as async_make_post_request_mock:
        async_make_post_request_mock.side_effect = TimeoutError

        with pytest.raises(TimeoutError):
            await w3.eth.block_number
        assert async_make_post_request_mock.call_count == 1


@pytest.mark.asyncio
async def test_async_exception_retry_middleware_with_allow_list_kwarg():
    config = ExceptionRetryConfiguration(
        errors=(aiohttp.ClientError, TimeoutError),
        retries=TEST_RETRY_COUNT,
        method_allowlist=["test_userProvidedMethod"],
    )
    async_w3 = AsyncWeb3(AsyncHTTPProvider(exception_retry_configuration=config))

    with patch(
        "web3.providers.rpc.async_rpc.HTTPSessionManager.async_make_post_request"
    ) as async_make_post_request_mock:
        async_make_post_request_mock.side_effect = TimeoutError

        with pytest.raises(TimeoutError):
            await async_w3.provider.make_request(
                RPCEndpoint("test_userProvidedMethod"), []
            )
        assert async_make_post_request_mock.call_count == TEST_RETRY_COUNT

        async_make_post_request_mock.reset_mock()
        with pytest.raises(TimeoutError):
            await async_w3.provider.make_request(RPCEndpoint("eth_getBalance"), [])
        assert async_make_post_request_mock.call_count == 1
