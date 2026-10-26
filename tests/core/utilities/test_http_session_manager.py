import pytest
import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
import json
import threading
import time

from aiohttp import (
    ClientSession,
    ClientTimeout,
)
from eth_typing import (
    URI,
)
from requests import (
    Session,
    adapters,
)
from requests.adapters import (
    DEFAULT_POOLSIZE,
    HTTPAdapter,
)

from web3._utils.caching import (
    generate_cache_key,
)
from web3._utils.http_session_manager import (
    HTTPSessionManager,
)
from web3.exceptions import (
    TimeExhausted,
)
from web3.utils.caching import (
    SimpleCache,
)


class MockedResponse:
    def __init__(self, text="", status_code=200):
        assert isinstance(text, str)
        assert isinstance(status_code, int)
        self.status_code = status_code
        self.ok = 200 <= status_code < 400
        self.text = text
        self.reason = None
        self.content = "content"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def iter_content(self):
        return [b"iter content"]

    @staticmethod
    def json():
        return json.dumps({"data": "content"})

    def raise_for_status(self):
        pass


TEST_URI = URI("http://mynode.local:8545")
UNIQUE_URIS = [
    "https://www.test1.com",
    "https://www.test2.com",
    "https://www.test3.com",
    "https://www.test4.com",
    "https://www.test5.com",
]


def check_adapters_mounted(session: Session):
    assert isinstance(session, Session)
    assert len(session.adapters) == 2


def _simulate_call(http_session_manager, uri):
    _session = http_session_manager.cache_and_return_session(uri, request_timeout=0.01)

    # simulate a call taking 0.01s to return a response
    time.sleep(0.01)
    return _session


@pytest.fixture
def http_session_manager():
    return HTTPSessionManager()


def test_session_manager_json_make_get_request(mocker, http_session_manager):
    mocker.patch("requests.Session.get", return_value=MockedResponse())

    # Submit a first request to create a session with default parameters
    assert len(http_session_manager.session_cache) == 0
    response = http_session_manager.json_make_get_request(TEST_URI)
    assert response == json.dumps({"data": "content"})
    assert len(http_session_manager.session_cache) == 1
    cache_key = generate_cache_key(f"{threading.get_ident()}:{TEST_URI}")
    session = http_session_manager.session_cache.get_cache_entry(cache_key)
    session.get.assert_called_once_with(TEST_URI, timeout=30)

    # Ensure the adapter was created with default values
    check_adapters_mounted(session)
    adapter = session.get_adapter(TEST_URI)
    assert isinstance(adapter, HTTPAdapter)
    assert adapter._pool_connections == DEFAULT_POOLSIZE
    assert adapter._pool_maxsize == DEFAULT_POOLSIZE


def test_session_manager_json_make_post_request(mocker, http_session_manager):
    mocker.patch("requests.Session.post", return_value=MockedResponse())

    # Submit a first request to create a session with default parameters
    assert len(http_session_manager.session_cache) == 0
    response = http_session_manager.json_make_post_request(
        TEST_URI, json={"data": "request"}
    )
    assert response == json.dumps({"data": "content"})
    assert len(http_session_manager.session_cache) == 1
    cache_key = generate_cache_key(f"{threading.get_ident()}:{TEST_URI}")
    session = http_session_manager.session_cache.get_cache_entry(cache_key)
    session.post.assert_called_once_with(TEST_URI, json={"data": "request"}, timeout=30)

    # Ensure the adapter was created with default values
    check_adapters_mounted(session)
    adapter = session.get_adapter(TEST_URI)
    assert isinstance(adapter, HTTPAdapter)
    assert adapter._pool_connections == DEFAULT_POOLSIZE
    assert adapter._pool_maxsize == DEFAULT_POOLSIZE


def test_session_manager_make_post_request_no_args(mocker, http_session_manager):
    mocker.patch("requests.Session.post", return_value=MockedResponse())

    # Submit a first request to create a session with default parameters
    assert len(http_session_manager.session_cache) == 0
    response = http_session_manager.make_post_request(TEST_URI, data=b"request")
    assert response == "content"
    assert len(http_session_manager.session_cache) == 1
    cache_key = generate_cache_key(f"{threading.get_ident()}:{TEST_URI}")
    session = http_session_manager.session_cache.get_cache_entry(cache_key)
    session.post.assert_called_once_with(
        TEST_URI, data=b"request", timeout=30, stream=False
    )

    # Ensure the adapter was created with default values
    check_adapters_mounted(session)
    adapter = session.get_adapter(TEST_URI)
    assert isinstance(adapter, HTTPAdapter)
    assert adapter._pool_connections == DEFAULT_POOLSIZE
    assert adapter._pool_maxsize == DEFAULT_POOLSIZE


def test_session_manager_make_post_request_streaming(mocker, http_session_manager):
    mocker.patch("requests.Session.post", return_value=MockedResponse())

    # Submit a first request to create a session
    assert len(http_session_manager.session_cache) == 0
    response = http_session_manager.make_post_request(
        TEST_URI, data=b"request", stream=True
    )
    assert response == b"iter content"
    assert len(http_session_manager.session_cache) == 1
    cache_key = generate_cache_key(f"{threading.get_ident()}:{TEST_URI}")
    session = http_session_manager.session_cache.get_cache_entry(cache_key)
    session.post.assert_called_once_with(
        TEST_URI, data=b"request", timeout=30, stream=True
    )

    # Ensure the adapter was created with passed in values
    check_adapters_mounted(session)
    adapter = session.get_adapter(TEST_URI)
    assert isinstance(adapter, HTTPAdapter)
    assert adapter._pool_connections == DEFAULT_POOLSIZE
    assert adapter._pool_maxsize == DEFAULT_POOLSIZE


def test_session_manager_make_post_request_times_out_while_streaming(
    mocker, http_session_manager
):
    mocker.patch("requests.Session.post", return_value=MockedResponse())
    mocker.patch("web3._utils.http_session_manager.time.time", side_effect=[0, 1])

    # Submit a first request to create a session
    assert len(http_session_manager.session_cache) == 0
    with pytest.raises(TimeExhausted):
        http_session_manager.make_post_request(
            TEST_URI, data=b"request", stream=True, timeout=0.000001
        )
    assert len(http_session_manager.session_cache) == 1
    cache_key = generate_cache_key(f"{threading.get_ident()}:{TEST_URI}")
    session = http_session_manager.session_cache.get_cache_entry(cache_key)
    session.post.assert_called_once_with(
        TEST_URI, data=b"request", timeout=0.000001, stream=True
    )

    # Ensure the adapter was created with default values
    check_adapters_mounted(session)
    adapter = session.get_adapter(TEST_URI)
    assert isinstance(adapter, HTTPAdapter)
    assert adapter._pool_connections == DEFAULT_POOLSIZE
    assert adapter._pool_maxsize == DEFAULT_POOLSIZE


def test_session_manager_precached_session(mocker, http_session_manager):
    mocker.patch("requests.Session.post", return_value=MockedResponse())

    # Update the cache with a handcrafted session
    adapter = adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    session = Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    http_session_manager.cache_and_return_session(TEST_URI, session)

    # Submit a second request with different arguments
    assert len(http_session_manager.session_cache) == 1
    response = http_session_manager.make_post_request(
        TEST_URI, data=b"request", timeout=60
    )
    assert response == "content"
    assert len(http_session_manager.session_cache) == 1

    # Ensure the timeout was passed to the request
    session = http_session_manager.cache_and_return_session(TEST_URI)
    session.post.assert_called_once_with(
        TEST_URI, data=b"request", timeout=60, stream=False
    )

    # Ensure the adapter parameters match those we specified
    check_adapters_mounted(session)
    adapter = session.get_adapter(TEST_URI)
    assert isinstance(adapter, HTTPAdapter)
    assert adapter._pool_connections == 100
    assert adapter._pool_maxsize == 100


def test_simple_cache_cache_session():
    cache = SimpleCache(2)
    _, evicted_items = cache.cache("1", "Hello1")
    assert cache.get_cache_entry("1") == "Hello1"
    assert evicted_items is None

    _, evicted_items = cache.cache("2", "Hello2")
    assert cache.get_cache_entry("2") == "Hello2"
    assert evicted_items is None

    # Changing what is stored at a given cache key should not cause the
    # anything to be evicted
    _, evicted_items = cache.cache("1", "HelloChanged")
    assert cache.get_cache_entry("1") == "HelloChanged"
    assert evicted_items is None

    _, evicted_items = cache.cache("3", "Hello3")
    assert "2" in cache
    assert "3" in cache

    assert "1" not in cache
    assert "1" in evicted_items

    # Cache size is `3`. We should have "2" and "3" in the cache and "1" should have
    # been evicted.
    assert cache.get_cache_entry("1") is None


def test_session_manager_cache_does_not_close_session_before_a_call_when_multithreading(
    http_session_manager,
):
    # set cache size to 1 + set future session close thread time to 0.01s
    http_session_manager.session_cache = SimpleCache(1)

    with ThreadPoolExecutor(max_workers=len(UNIQUE_URIS)) as exc:
        all_sessions = [
            exc.submit(_simulate_call, http_session_manager, uri) for uri in UNIQUE_URIS
        ]

    # assert last session remains in cache, all others evicted
    cache_data = http_session_manager.session_cache._data
    assert len(cache_data) == 1
    _key, cached_session = cache_data.popitem()
    assert cached_session == all_sessions[-1].result()  # result of the `Future`

    # -- teardown -- #

    # close the cached session before exiting test
    cached_session.close()


def test_session_manager_unique_cache_keys_created_per_thread_with_same_uri(
    http_session_manager,
):
    # somewhat inspired by issue #2680

    with ThreadPoolExecutor(max_workers=2) as exc:
        test_sessions = [
            exc.submit(_simulate_call, http_session_manager, TEST_URI) for _ in range(2)
        ]

    # assert unique keys are generated per thread for the same uri
    assert len(http_session_manager.session_cache._data) == 2

    # -- teardown -- #

    # appropriately close the test sessions
    [session.result().close() for session in test_sessions]


# -- async -- #


class AsyncMockedResponse:
    status_code = 200

    def __await__(self):
        yield
        return self

    @staticmethod
    async def read():
        return "content"

    @staticmethod
    async def json():
        return json.dumps({"data": "content"})

    @staticmethod
    def raise_for_status() -> None:
        pass


@pytest.mark.asyncio
async def test_session_manager_async_json_make_get_request(
    mocker, http_session_manager
):
    mocker.patch("aiohttp.ClientSession.get", return_value=AsyncMockedResponse())

    # Submit a first request to create a session with default parameters
    assert len(http_session_manager.session_cache) == 0
    response = await http_session_manager.async_json_make_get_request(TEST_URI)
    assert response == json.dumps({"data": "content"})
    assert len(http_session_manager.session_cache) == 1
    cache_key = generate_cache_key(f"{id(asyncio.get_event_loop())}:{TEST_URI}")
    session = http_session_manager.session_cache.get_cache_entry(cache_key)
    assert isinstance(session, ClientSession)
    session.get.assert_called_once_with(
        TEST_URI,
        timeout=ClientTimeout(
            total=30, connect=None, sock_read=None, sock_connect=None
        ),
    )
    await session.close()


@pytest.mark.asyncio
async def test_session_manager_async_json_make_post_request(
    mocker, http_session_manager
):
    mocker.patch("aiohttp.ClientSession.post", return_value=AsyncMockedResponse())

    # Submit a first request to create a session with default parameters
    assert len(http_session_manager.session_cache) == 0
    response = await http_session_manager.async_json_make_post_request(
        TEST_URI, json={"data": "request"}
    )
    assert response == json.dumps({"data": "content"})
    assert len(http_session_manager.session_cache) == 1
    cache_key = generate_cache_key(f"{id(asyncio.get_event_loop())}:{TEST_URI}")
    session = http_session_manager.session_cache.get_cache_entry(cache_key)
    assert isinstance(session, ClientSession)
    session.post.assert_called_once_with(
        TEST_URI,
        json={"data": "request"},
        timeout=ClientTimeout(
            total=30, connect=None, sock_read=None, sock_connect=None
        ),
    )
    await session.close()


@pytest.mark.asyncio
async def test_session_manager_async_make_post_request(mocker, http_session_manager):
    mocker.patch("aiohttp.ClientSession.post", return_value=AsyncMockedResponse())

    # Submit a first request to create a session with default parameters
    assert len(http_session_manager.session_cache) == 0
    response = await http_session_manager.async_make_post_request(
        TEST_URI, data=b"request"
    )
    assert response == "content"
    assert len(http_session_manager.session_cache) == 1
    cache_key = generate_cache_key(f"{id(asyncio.get_event_loop())}:{TEST_URI}")
    session = http_session_manager.session_cache.get_cache_entry(cache_key)
    assert isinstance(session, ClientSession)
    session.post.assert_called_once_with(
        TEST_URI,
        data=b"request",
        timeout=ClientTimeout(
            total=30, connect=None, sock_read=None, sock_connect=None
        ),
    )
    await session.close()


@pytest.mark.asyncio
async def test_session_manager_async_precached_session(http_session_manager):
    # Add a session
    session = ClientSession()
    await http_session_manager.async_cache_and_return_session(TEST_URI, session)
    assert len(http_session_manager.session_cache) == 1

    # Make sure the session isn't duplicated
    await http_session_manager.async_cache_and_return_session(TEST_URI, session)
    assert len(http_session_manager.session_cache) == 1

    # Make sure a request with a different URI adds another cached session
    await http_session_manager.async_cache_and_return_session(
        URI(f"{TEST_URI}/test"), session
    )
    assert len(http_session_manager.session_cache) == 2

    # -- teardown -- #

    # appropriately close the cached sessions
    [
        await session.close()
        for session in http_session_manager.session_cache._data.values()
    ]


@pytest.mark.asyncio
async def test_async_session_manager_cache_does_not_close_session_before_call(
    http_session_manager,
):
    # set cache size to 1 + set future session close thread time to 0.01s
    http_session_manager.session_cache = SimpleCache(1)
    _timeout_for_testing = 0.01

    async def cache_uri_and_return_session(uri):
        _session = await http_session_manager.async_cache_and_return_session(
            uri, request_timeout=ClientTimeout(_timeout_for_testing)
        )
        # simulate a call taking 0.01s to return a response
        await asyncio.sleep(_timeout_for_testing)

        assert not _session.closed
        return _session

    all_sessions = [await cache_uri_and_return_session(uri) for uri in UNIQUE_URIS]
    assert len(all_sessions) == len(UNIQUE_URIS)
    assert all(isinstance(s, ClientSession) for s in all_sessions)

    # last session remains in cache, all others evicted
    cache_data = http_session_manager.session_cache._data
    assert len(cache_data) == 1
    _key, cached_session = cache_data.popitem()
    assert cached_session == all_sessions[-1]

    # assert all evicted sessions were closed
    await asyncio.sleep(_timeout_for_testing + 0.1)
    assert all(session.closed for session in all_sessions[:-1])

    # -- teardown -- #

    # appropriately close the cached session
    await cached_session.close()


@pytest.mark.asyncio
async def test_session_manager_async_unique_cache_keys_created_per_thread_with_same_uri(
    http_session_manager,
):
    # inspired by issue #2680
    # Note: unique event loops for each thread are important here

    # capture the test sessions to appropriately close them in teardown
    test_sessions = []

    def target_function(endpoint_uri):
        event_loop = asyncio.new_event_loop()
        unique_session = event_loop.run_until_complete(
            http_session_manager.async_cache_and_return_session(
                endpoint_uri, request_timeout=ClientTimeout(0.1)
            )
        )
        event_loop.close()
        test_sessions.append(unique_session)

    threads = []

    for _ in range(2):
        thread = threading.Thread(
            target=target_function,
            args=(TEST_URI,),
            daemon=True,
        )
        thread.start()
        time.sleep(0.01)
        threads.append(thread)

    [thread.join() for thread in threads]

    # assert unique keys are generated per thread, w/ unique event loops,
    # for the same uri
    assert len(http_session_manager.session_cache._data) == 2

    # -- teardown -- #

    # appropriately close the test sessions
    [await session.close() for session in test_sessions]


@pytest.mark.asyncio
async def test_session_manager_async_use_new_session_if_loop_closed_for_cached_session(
    http_session_manager,
):
    # create new loop, cache a session within the loop, close the loop
    loop1 = asyncio.new_event_loop()

    session1 = ClientSession(raise_for_status=True)
    session1._loop = loop1

    await http_session_manager.async_cache_and_return_session(
        TEST_URI, session=session1
    )

    # assert session1 was cached
    cache_key = generate_cache_key(f"{id(asyncio.get_event_loop())}:{TEST_URI}")

    assert len(http_session_manager.session_cache) == 1
    cached_session = http_session_manager.session_cache.get_cache_entry(cache_key)
    assert cached_session == session1

    # close loop that was used with session1
    loop1.close()

    # assert we create a new session when trying to retrieve the session at the
    # cache key for TEST_URI
    session2 = await http_session_manager.async_cache_and_return_session(TEST_URI)
    assert not session2._loop.is_closed()
    assert session2 != session1

    # assert we appropriately closed session1, evicted it from the cache, and cached
    # the new session2 at the cache key
    assert session1.closed
    assert len(http_session_manager.session_cache) == 1
    cached_session = http_session_manager.session_cache.get_cache_entry(cache_key)
    assert cached_session == session2

    # -- teardown -- #

    # appropriately close the new session
    await session2.close()


@pytest.mark.asyncio
async def test_session_manager_async_use_new_session_if_session_closed_for_cached_session(  # noqa: E501
    http_session_manager,
):
    # create a session, close it, and cache it at the cache key for TEST_URI
    session1 = ClientSession(raise_for_status=True)
    await session1.close()
    await http_session_manager.async_cache_and_return_session(
        TEST_URI, session=session1
    )

    # assert session1 was cached
    cache_key = generate_cache_key(f"{id(asyncio.get_event_loop())}:{TEST_URI}")

    assert len(http_session_manager.session_cache) == 1
    cached_session = http_session_manager.session_cache.get_cache_entry(cache_key)
    assert cached_session == session1

    # assert we create a new session when trying to retrieve closed session from cache
    session2 = await http_session_manager.async_cache_and_return_session(TEST_URI)
    assert not session2.closed
    assert session2 != session1

    # assert we evicted session1 from the cache, and cached the new session2
    # at the cache key
    assert len(http_session_manager.session_cache) == 1
    cached_session = http_session_manager.session_cache.get_cache_entry(cache_key)
    assert cached_session == session2

    # -- teardown -- #

    # appropriately close the new session
    await session2.close()
