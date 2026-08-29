import pytest
import concurrent.futures
import threading
from unittest.mock import (
    Mock,
    patch,
)

from requests import (
    Session,
)
from requests.adapters import (
    HTTPAdapter,
)

from web3 import (
    Web3,
    __version__ as web3py_version,
)
from web3.eth import (
    Eth,
)
from web3.exceptions import (
    ProviderConnectionError,
    Web3RPCError,
)
from web3.geth import (
    Geth,
    GethAdmin,
    GethTxPool,
)
from web3.middleware import (
    AttributeDictMiddleware,
    BufferedGasEstimateMiddleware,
    ENSNameToAddressMiddleware,
    GasPriceStrategyMiddleware,
    ValidationMiddleware,
)
from web3.net import (
    Net,
)
from web3.providers import (
    HTTPProvider,
)

URI = "http://mynode.local:8545"


def test_no_args():
    provider = HTTPProvider()
    w3 = Web3(provider)
    assert w3.manager.provider == provider
    assert not w3.manager.provider.is_async
    assert not w3.is_connected()
    with pytest.raises(ProviderConnectionError):
        w3.is_connected(show_traceback=True)


def test_init_kwargs():
    provider = HTTPProvider(endpoint_uri=URI, request_kwargs={"timeout": 60})
    w3 = Web3(provider)
    assert w3.manager.provider == provider


def test_web3_with_http_provider_has_default_middleware_and_modules() -> None:
    adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
    session = Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    provider = HTTPProvider(endpoint_uri=URI, session=session)
    w3 = Web3(provider)

    # assert default modules
    assert isinstance(w3.eth, Eth)
    assert isinstance(w3.net, Net)
    assert isinstance(w3.geth, Geth)
    assert isinstance(w3.geth.admin, GethAdmin)
    assert isinstance(w3.geth.txpool, GethTxPool)

    # assert default middleware

    # the following length check should fail and will need to be added to once more
    # middleware are added to the defaults
    assert len(w3.middleware_onion.middleware) == 5

    assert w3.middleware_onion.get("gas_price_strategy") == GasPriceStrategyMiddleware
    assert w3.middleware_onion.get("ens_name_to_address") == ENSNameToAddressMiddleware
    assert w3.middleware_onion.get("attrdict") == AttributeDictMiddleware
    assert w3.middleware_onion.get("validation") == ValidationMiddleware
    assert w3.middleware_onion.get("gas_estimate") == BufferedGasEstimateMiddleware


def test_user_provided_session():
    adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
    session = Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    provider = HTTPProvider(endpoint_uri=URI, session=session)
    session = provider._request_session_manager.cache_and_return_session(URI)
    w3 = Web3(provider)
    assert w3.manager.provider == provider

    adapter = session.get_adapter(URI)
    assert isinstance(adapter, HTTPAdapter)
    assert adapter._pool_connections == 20
    assert adapter._pool_maxsize == 20


@pytest.mark.parametrize("provider", (HTTPProvider(), HTTPProvider))
def test_get_request_headers(provider):
    headers = provider.get_request_headers()
    assert len(headers) == 2
    assert headers["Content-Type"] == "application/json"
    assert (
        headers["User-Agent"] == f"web3.py/{web3py_version}/"
        f"{HTTPProvider.__module__}.{HTTPProvider.__qualname__}"
    )


@patch(
    "web3._utils.http_session_manager.HTTPSessionManager.make_post_request",
    new_callable=Mock,
)
def test_http_empty_batch_response(mock_post):
    mock_post.return_value = (
        b'{"jsonrpc":"2.0","id":null,"error":{"code":-32600,"message":"empty batch"}}'
    )
    w3 = Web3(HTTPProvider())
    with w3.batch_requests() as batch:
        assert w3.provider._is_batching
        with pytest.raises(Web3RPCError, match="empty batch"):
            batch.execute()

    # assert that even though there was an error, we have reset the batching state
    assert not w3.provider._is_batching


def test_user_provided_session_shared_across_threads():
    """
    Test that when a user provides an explicit session to HTTPProvider,
    that same session is used by ALL threads, not just the creating thread.

    This is a regression test for:
    https://github.com/ApeWorX/web3.py/issues/3789
    """
    shared_session = Session()
    provider = HTTPProvider(endpoint_uri=URI, session=shared_session)

    sessions_from_threads = []
    errors = []

    def get_session_from_thread():
        try:
            # This simulates what happens internally when a request is made
            # from a different thread - it calls cache_and_return_session
            session = provider._request_session_manager.cache_and_return_session(URI)
            sessions_from_threads.append(session)
        except Exception as e:
            errors.append(e)

    # Get session from main thread
    main_thread_session = provider._request_session_manager.cache_and_return_session(
        URI
    )

    # Get session from multiple different threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(get_session_from_thread) for _ in range(10)]
        concurrent.futures.wait(futures)

    assert not errors, f"Errors occurred: {errors}"
    assert len(sessions_from_threads) == 10

    # The main assertion: ALL sessions should be the SAME shared session
    assert main_thread_session is shared_session
    for session in sessions_from_threads:
        assert session is shared_session, (
            "Session from different thread should be the same as the "
            "explicitly provided session"
        )


def test_no_explicit_session_creates_per_thread_sessions():
    """
    Test that when no explicit session is provided, each thread gets its own
    session (the original thread-isolated behavior).
    """
    provider = HTTPProvider(endpoint_uri=URI)

    sessions_from_threads = []

    def get_session_from_thread():
        session = provider._request_session_manager.cache_and_return_session(URI)
        sessions_from_threads.append((threading.get_ident(), session))

    # Get session from main thread
    main_thread_id = threading.get_ident()
    main_thread_session = provider._request_session_manager.cache_and_return_session(
        URI
    )

    # Get sessions from different threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(get_session_from_thread) for _ in range(3)]
        concurrent.futures.wait(futures)

    # Group sessions by thread ID
    sessions_by_thread = {}
    for thread_id, session in sessions_from_threads:
        if thread_id not in sessions_by_thread:
            sessions_by_thread[thread_id] = []
        sessions_by_thread[thread_id].append(session)

    # Verify thread isolation: same thread always gets the same session
    for _, sessions in sessions_by_thread.items():
        assert all(s is sessions[0] for s in sessions), (
            "Same thread should always get the same session"
        )

    # Verify different threads get different sessions (not the main thread's)
    for thread_id, sessions in sessions_by_thread.items():
        if thread_id != main_thread_id:
            assert sessions[0] is not main_thread_session, (
                "Different threads should have different sessions"
            )
