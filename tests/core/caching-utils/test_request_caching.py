import pytest
import itertools
import threading
import time
import uuid

import pytest_asyncio

from web3 import (
    AsyncHTTPProvider,
    AsyncIPCProvider,
    AsyncWeb3,
    HTTPProvider,
    IPCProvider,
    PersistentConnectionProvider,
    Web3,
    WebSocketProvider,
)
from web3._utils.caching import (
    CACHEABLE_REQUESTS,
    generate_cache_key,
)
from web3._utils.caching.caching_utils import (
    ASYNC_INTERNAL_VALIDATION_MAP,
    BLOCK_IN_RESULT,
    BLOCKHASH_IN_PARAMS,
    BLOCKNUM_IN_PARAMS,
    CHAIN_VALIDATION_THRESHOLD_DEFAULTS,
    DEFAULT_VALIDATION_THRESHOLD,
    INTERNAL_VALIDATION_MAP,
    async_handle_send_caching,
)
from web3.exceptions import (
    Web3RPCError,
)
from web3.types import (
    RPCEndpoint,
)
from web3.utils import (
    RequestCacheValidationThreshold,
    SimpleCache,
)

SYNC_PROVIDERS = [
    HTTPProvider,
    IPCProvider,
]
ASYNC_PROVIDERS = [
    AsyncHTTPProvider,
    AsyncIPCProvider,
    WebSocketProvider,
]


def simple_cache_return_value_a():
    _cache = SimpleCache()
    _cache.cache(
        generate_cache_key(f"{threading.get_ident()}:{('fake_endpoint', [1])}"),
        {"jsonrpc": "2.0", "id": 0, "result": "value-a"},
    )
    return _cache


@pytest.fixture(params=SYNC_PROVIDERS)
def sync_provider(request):
    return request.param


@pytest.fixture
def w3(sync_provider, request_mocker):
    _w3 = Web3(provider=sync_provider(cache_allowed_requests=True))
    _w3.provider.cacheable_requests += (RPCEndpoint("fake_endpoint"),)
    with request_mocker(
        _w3,
        mock_results={
            "fake_endpoint": lambda *_: uuid.uuid4(),
            "not_on_allowlist": lambda *_: uuid.uuid4(),
            "eth_chainId": "0x1",  # mainnet
        },
    ):
        yield _w3

    # clear request cache after each test
    _w3.provider._request_cache.clear()


def test_request_caching_pulls_from_cache(w3):
    w3.provider._request_cache = simple_cache_return_value_a()
    assert w3.manager.request_blocking("fake_endpoint", [1]) == "value-a"


def test_request_caching_populates_cache(w3):
    result = w3.manager.request_blocking("fake_endpoint", [])
    assert w3.manager.request_blocking("fake_endpoint", []) == result
    assert w3.manager.request_blocking("fake_endpoint", [1]) != result
    assert len(w3.provider._request_cache.items()) == 2


def test_request_caching_does_not_cache_none_responses(sync_provider, request_mocker):
    w3 = Web3(sync_provider(cache_allowed_requests=True))
    w3.provider.cacheable_requests += (RPCEndpoint("fake_endpoint"),)

    counter = itertools.count()

    def result_cb(_method, _params):
        next(counter)
        return None

    with request_mocker(w3, mock_results={"fake_endpoint": result_cb}):
        w3.manager.request_blocking("fake_endpoint", [])
        w3.manager.request_blocking("fake_endpoint", [])

    assert next(counter) == 2


def test_request_caching_does_not_cache_error_responses(sync_provider, request_mocker):
    w3 = Web3(sync_provider(cache_allowed_requests=True))
    w3.provider.cacheable_requests += (RPCEndpoint("fake_endpoint"),)

    with request_mocker(
        w3, mock_errors={"fake_endpoint": lambda *_: {"message": f"msg-{uuid.uuid4()}"}}
    ):
        with pytest.raises(Web3RPCError) as err_a:
            w3.manager.request_blocking("fake_endpoint", [])
        with pytest.raises(Web3RPCError) as err_b:
            w3.manager.request_blocking("fake_endpoint", [])

        assert str(err_a) != str(err_b)
        assert err_a.value.args != err_b.value.args


def test_request_caching_does_not_cache_endpoints_not_in_allowlist(w3):
    result_a = w3.manager.request_blocking("not_on_allowlist", [])
    result_b = w3.manager.request_blocking("not_on_allowlist", [])
    assert result_a != result_b


def test_caching_requests_does_not_share_state_between_providers(
    sync_provider, request_mocker
):
    w3_a, w3_b, w3_c, w3_a_shared_cache = (
        Web3(provider=sync_provider(cache_allowed_requests=True)),
        Web3(provider=sync_provider(cache_allowed_requests=True)),
        Web3(provider=sync_provider(cache_allowed_requests=True)),
        Web3(provider=sync_provider(cache_allowed_requests=True)),
    )

    # strap w3_a_shared_cache with w3_a's cache
    w3_a_shared_cache.provider._request_cache = w3_a.provider._request_cache

    mock_results_a = {RPCEndpoint("eth_chainId"): hex(11111)}
    mock_results_a_shared_cache = {RPCEndpoint("eth_chainId"): hex(00000)}
    mock_results_b = {RPCEndpoint("eth_chainId"): hex(22222)}
    mock_results_c = {RPCEndpoint("eth_chainId"): hex(33333)}

    with request_mocker(w3_a, mock_results=mock_results_a):
        with request_mocker(w3_b, mock_results=mock_results_b):
            with request_mocker(w3_c, mock_results=mock_results_c):
                result_a = w3_a.manager.request_blocking("eth_chainId", [])
                result_b = w3_b.manager.request_blocking("eth_chainId", [])
                result_c = w3_c.manager.request_blocking("eth_chainId", [])

        with request_mocker(
            w3_a_shared_cache, mock_results=mock_results_a_shared_cache
        ):
            # test a shared cache returns 11111, not 00000
            result_a_shared_cache = w3_a_shared_cache.manager.request_blocking(
                "eth_chainId", []
            )

    assert result_a == hex(11111)
    assert result_b == hex(22222)
    assert result_c == hex(33333)
    assert result_a_shared_cache == hex(11111)


@pytest.mark.parametrize("provider", [*SYNC_PROVIDERS, *ASYNC_PROVIDERS])
def test_all_providers_do_not_cache_by_default_and_can_set_caching_properties(provider):
    _provider_default_init = provider()
    assert _provider_default_init.cache_allowed_requests is False
    assert _provider_default_init.cacheable_requests == CACHEABLE_REQUESTS

    # can set properties
    _provider_default_init.cache_allowed_requests = True
    _provider_default_init.cacheable_requests = {RPCEndpoint("fake_endpoint")}
    assert _provider_default_init.cache_allowed_requests is True
    assert _provider_default_init.cacheable_requests == {RPCEndpoint("fake_endpoint")}

    # can set properties on init
    _provider_set_on_init = provider(
        cache_allowed_requests=True,
        cacheable_requests={RPCEndpoint("fake_endpoint")},
    )
    assert _provider_set_on_init.cache_allowed_requests is True
    assert _provider_set_on_init.cacheable_requests == {RPCEndpoint("fake_endpoint")}


@pytest.mark.parametrize(
    "threshold",
    (RequestCacheValidationThreshold.FINALIZED, RequestCacheValidationThreshold.SAFE),
)
@pytest.mark.parametrize("endpoint", sorted(BLOCKNUM_IN_PARAMS | BLOCK_IN_RESULT))
@pytest.mark.parametrize(
    "blocknum,should_cache",
    (
        ("0x0", True),
        ("0x1", True),
        ("0x2", True),
        ("0x3", False),
        ("0x4", False),
        ("0x5", False),
    ),
)
def test_blocknum_validation_against_validation_threshold_when_caching_mainnet(
    threshold, endpoint, blocknum, should_cache, sync_provider, request_mocker
):
    w3 = Web3(
        sync_provider(
            cache_allowed_requests=True, request_cache_validation_threshold=threshold
        )
    )
    with request_mocker(
        w3,
        mock_results={
            endpoint: (
                # mock the result to requests that return blocks
                {"number": blocknum, "timestamp": "0x0"}
                if "getBlock" in endpoint
                # mock the result to requests that return transactions
                else {"blockNumber": blocknum}
            ),
            "eth_getBlockByNumber": lambda _method, params: (
                # mock the threshold block to be blocknum "0x2", return
                # blocknum otherwise
                {"number": "0x2", "timestamp": "0x0"}
                if params[0] == threshold.value
                else {"number": params[0], "timestamp": "0x0"}
            ),
            "eth_chainId": "0x1",  # mainnet
        },
    ):
        assert len(w3.provider._request_cache.items()) == 0
        w3.manager.request_blocking(endpoint, [blocknum, False])
        cached_items = len(w3.provider._request_cache.items())
        assert cached_items == 1 if should_cache else cached_items == 0


@pytest.mark.parametrize(
    "threshold",
    (RequestCacheValidationThreshold.FINALIZED, RequestCacheValidationThreshold.SAFE),
)
@pytest.mark.parametrize("endpoint", sorted(BLOCKNUM_IN_PARAMS))
@pytest.mark.parametrize(
    "block_id,blocknum,should_cache",
    (
        ("earliest", "0x0", True),
        ("earliest", "0x2", True),
        ("finalized", "0x2", False),
        ("safe", "0x2", False),
        ("latest", "0x2", False),
        ("pending", None, False),
    ),
)
def test_block_id_param_caching_mainnet(
    threshold, endpoint, block_id, blocknum, should_cache, sync_provider, request_mocker
):
    w3 = Web3(
        sync_provider(
            cache_allowed_requests=True, request_cache_validation_threshold=threshold
        )
    )
    with request_mocker(
        w3,
        mock_results={
            "eth_chainId": "0x1",  # mainnet
            endpoint: "0x0",
            "eth_getBlockByNumber": lambda _method, params: (
                # mock the threshold block to be blocknum "0x2" for all test cases
                {"number": "0x2", "timestamp": "0x0"}
                if params[0] == threshold.value
                else {"number": blocknum, "timestamp": "0x0"}
            ),
        },
    ):
        assert len(w3.provider._request_cache.items()) == 0
        w3.manager.request_blocking(RPCEndpoint(endpoint), [block_id, False])
        cached_items = len(w3.provider._request_cache.items())
        assert cached_items == 1 if should_cache else cached_items == 0


@pytest.mark.parametrize(
    "threshold",
    (RequestCacheValidationThreshold.FINALIZED, RequestCacheValidationThreshold.SAFE),
)
@pytest.mark.parametrize("endpoint", sorted(BLOCKHASH_IN_PARAMS))
@pytest.mark.parametrize(
    "blocknum,should_cache",
    (
        ("0x0", True),
        ("0x1", True),
        ("0x2", True),
        ("0x3", False),
        ("0x4", False),
        ("0x5", False),
    ),
)
def test_blockhash_validation_against_validation_threshold_when_caching_mainnet(
    threshold, endpoint, blocknum, should_cache, sync_provider, request_mocker
):
    w3 = Web3(
        sync_provider(
            cache_allowed_requests=True, request_cache_validation_threshold=threshold
        )
    )
    with request_mocker(
        w3,
        mock_results={
            "eth_chainId": "0x1",  # mainnet
            "eth_getBlockByNumber": lambda _method, params: (
                # mock the threshold block to be blocknum "0x2"
                {"number": "0x2", "timestamp": "0x0"}
                if params[0] == threshold.value
                else {"number": params[0], "timestamp": "0x0"}
            ),
            "eth_getBlockByHash": {"number": blocknum, "timestamp": "0x0"},
            endpoint: "0x0",
        },
    ):
        assert len(w3.provider._request_cache.items()) == 0
        w3.manager.request_blocking(endpoint, [b"\x00" * 32, False])
        cached_items = len(w3.provider._request_cache.items())
        assert cached_items == 1 if should_cache else cached_items == 0


@pytest.mark.parametrize(
    "chain_id,expected_threshold",
    (
        *CHAIN_VALIDATION_THRESHOLD_DEFAULTS.items(),
        (3456787654567654, DEFAULT_VALIDATION_THRESHOLD),
        (11111111111444444444444444, DEFAULT_VALIDATION_THRESHOLD),
        (-11111111111111111117, DEFAULT_VALIDATION_THRESHOLD),
    ),
)
def test_request_caching_validation_threshold_defaults(
    chain_id, expected_threshold, sync_provider, request_mocker
):
    w3 = Web3(sync_provider(cache_allowed_requests=True))
    with request_mocker(w3, mock_results={"eth_chainId": hex(chain_id)}):
        w3.manager.request_blocking(RPCEndpoint("eth_chainId"), [])
        assert w3.provider.request_cache_validation_threshold == expected_threshold
        # assert chain_id is cached
        cache_items = w3.provider._request_cache.items()
        assert len(cache_items) == 1
        assert cache_items[0][1]["result"] == hex(chain_id)


@pytest.mark.parametrize(
    "endpoint", sorted(BLOCKNUM_IN_PARAMS | BLOCK_IN_RESULT | BLOCKHASH_IN_PARAMS)
)
@pytest.mark.parametrize(
    "time_from_threshold,should_cache",
    # -0.2 to give some time for the test to run
    ((-2, True), (-1, True), (-0.2, True), (1, False), (2, False)),
)
@pytest.mark.parametrize(
    "chain_id,expected_threshold_in_seconds",
    [
        (chain_id, threshold)
        for chain_id, threshold in CHAIN_VALIDATION_THRESHOLD_DEFAULTS.items()
        if isinstance(threshold, int)
    ]
    + [
        (3456787654567654, DEFAULT_VALIDATION_THRESHOLD),
        (11111111111444444444444444, DEFAULT_VALIDATION_THRESHOLD),
        (-11111111111111111117, DEFAULT_VALIDATION_THRESHOLD),
    ],
)
def test_sync_validation_against_validation_threshold_time_based(
    endpoint,
    time_from_threshold,
    should_cache,
    chain_id,
    expected_threshold_in_seconds,
    sync_provider,
    request_mocker,
):
    w3 = Web3(sync_provider(cache_allowed_requests=True))
    blocknum = "0x2"
    # mock the timestamp so that we are at the threshold +/- the time_from_threshold
    mocked_time = hex(
        int(round(time.time() - expected_threshold_in_seconds) + time_from_threshold)
    )

    with request_mocker(
        w3,
        mock_results={
            "eth_chainId": hex(chain_id),
            endpoint: lambda *_: (
                # mock the result to requests that return blocks
                {"number": blocknum, "timestamp": mocked_time}
                if "getBlock" in endpoint
                # mock the result to requests that return transactions with the blocknum
                # for our block under test
                else {"blockNumber": blocknum}
            ),
            "eth_getBlockByNumber": lambda _method, params: (
                {"number": blocknum, "timestamp": mocked_time}
            ),
            "eth_getBlockByHash": {"number": blocknum, "timestamp": mocked_time},
        },
    ):
        assert len(w3.provider._request_cache.items()) == 0
        w3.manager.request_blocking(endpoint, [blocknum, False])
        cached_items = w3.provider._request_cache.items()
        assert len(cached_items) == 1 if should_cache else len(cached_items) == 0


@pytest.mark.parametrize(
    "time_from_threshold,should_cache",
    # -0.2 to give some time for the test to run
    ((-2, True), (-1, True), (-0.2, True), (1, False), (2, False)),
)
@pytest.mark.parametrize(
    "chain_id",
    (
        # test that defaults are also overridden by the configured validation threshold
        *CHAIN_VALIDATION_THRESHOLD_DEFAULTS.keys(),
        3456787654567654,
        11111111111444444444444444,
        -11111111111111111117,
    ),
)
@pytest.mark.parametrize(
    "endpoint", sorted(BLOCKNUM_IN_PARAMS | BLOCK_IN_RESULT | BLOCKHASH_IN_PARAMS)
)
def test_validation_against_validation_threshold_time_based_configured(
    time_from_threshold, should_cache, chain_id, endpoint, sync_provider, request_mocker
):
    configured_time_threshold = 60 * 60 * 24 * 7  # 1 week
    w3 = Web3(
        sync_provider(
            cache_allowed_requests=True,
            request_cache_validation_threshold=configured_time_threshold,
        )
    )
    blocknum = "0x2"
    # mock the timestamp so that we are at the threshold +/- the time_from_threshold
    mocked_time = hex(
        int(round(time.time()) - configured_time_threshold + time_from_threshold)
    )

    with request_mocker(
        w3,
        mock_results={
            "eth_chainId": chain_id,
            endpoint: lambda *_: (
                # mock the result to requests that return blocks
                {"number": blocknum, "timestamp": mocked_time}
                if "getBlock" in endpoint
                # mock the result to requests that return transactions with the blocknum
                # for our block under test
                else {"blockNumber": blocknum}
            ),
            "eth_getBlockByNumber": lambda _method, params: (
                {"number": blocknum, "timestamp": mocked_time}
            ),
            "eth_getBlockByHash": {"number": blocknum, "timestamp": mocked_time},
        },
    ):
        assert len(w3.provider._request_cache.items()) == 0
        w3.manager.request_blocking(endpoint, [blocknum, False])
        cached_items = w3.provider._request_cache.items()
        assert len(cached_items) == 1 if should_cache else len(cached_items) == 0


# -- async -- #


def test_async_cacheable_requests_are_the_same_as_sync():
    assert (
        set(CACHEABLE_REQUESTS)
        == set(INTERNAL_VALIDATION_MAP.keys())
        == set(ASYNC_INTERNAL_VALIDATION_MAP.keys())
    ), "make sure the async and sync cacheable requests are the same"


@pytest_asyncio.fixture(params=ASYNC_PROVIDERS)
async def async_provider(request):
    return request.param


async def _async_w3_init(
    async_provider,
    threshold: RequestCacheValidationThreshold | int | None = "empty",
):
    if isinstance(async_provider, PersistentConnectionProvider):
        _async_w3 = await AsyncWeb3(
            provider=async_provider(
                cache_allowed_requests=True,
            )
        )
    else:
        _async_w3 = AsyncWeb3(provider=async_provider(cache_allowed_requests=True))

    if threshold != "empty":
        _async_w3.provider.request_cache_validation_threshold = threshold
    return _async_w3


@pytest_asyncio.fixture
async def async_w3(async_provider, request_mocker):
    _async_w3 = await _async_w3_init(async_provider)
    _async_w3.provider.cacheable_requests += (RPCEndpoint("fake_endpoint"),)
    async with request_mocker(
        _async_w3,
        mock_results={
            "fake_endpoint": lambda *_: uuid.uuid4(),
            "not_on_allowlist": lambda *_: uuid.uuid4(),
            "eth_chainId": "0x1",  # mainnet
        },
    ):
        yield _async_w3

    # clear request cache after each test
    _async_w3.provider._request_cache.clear()


@pytest.mark.asyncio
async def test_async_request_caching_pulls_from_cache(async_w3):
    async_w3.provider._request_cache = simple_cache_return_value_a()
    _result = await async_w3.manager.coro_request("fake_endpoint", [1])
    assert _result == "value-a"


@pytest.mark.asyncio
async def test_async_request_caching_populates_cache(async_w3):
    result = await async_w3.manager.coro_request("fake_endpoint", [])

    _empty_params = await async_w3.manager.coro_request("fake_endpoint", [])
    _non_empty_params = await async_w3.manager.coro_request("fake_endpoint", [1])

    assert _empty_params == result
    assert _non_empty_params != result


@pytest.mark.asyncio
async def test_async_request_caching_does_not_cache_none_responses(
    async_provider, request_mocker
):
    async_w3 = await _async_w3_init(async_provider)
    async_w3.provider.cacheable_requests += (RPCEndpoint("fake_endpoint"),)

    counter = itertools.count()

    def result_cb(_method, _params):
        next(counter)
        return None

    async with request_mocker(async_w3, mock_results={"fake_endpoint": result_cb}):
        await async_w3.manager.coro_request("fake_endpoint", [])
        await async_w3.manager.coro_request("fake_endpoint", [])

    assert next(counter) == 2


@pytest.mark.asyncio
async def test_async_request_caching_does_not_cache_error_responses(
    async_provider, request_mocker
):
    async_w3 = await _async_w3_init(async_provider)
    async_w3.provider.cacheable_requests += (RPCEndpoint("fake_endpoint"),)

    async with request_mocker(
        async_w3,
        mock_errors={"fake_endpoint": lambda *_: {"message": f"msg-{uuid.uuid4()}"}},
    ):
        with pytest.raises(Web3RPCError) as err_a:
            await async_w3.manager.coro_request("fake_endpoint", [])
        with pytest.raises(Web3RPCError) as err_b:
            await async_w3.manager.coro_request("fake_endpoint", [])

    assert str(err_a) != str(err_b)


@pytest.mark.asyncio
async def test_async_request_caching_does_not_cache_non_allowlist_endpoints(
    async_w3,
):
    result_a = await async_w3.manager.coro_request("not_on_allowlist", [])
    result_b = await async_w3.manager.coro_request("not_on_allowlist", [])
    assert result_a != result_b


@pytest.mark.asyncio
async def test_async_request_caching_does_not_share_state_between_providers(
    async_provider,
    request_mocker,
):
    async_w3_a, async_w3_b, async_w3_c, async_w3_a_shared_cache = (
        await _async_w3_init(async_provider),
        await _async_w3_init(async_provider),
        await _async_w3_init(async_provider),
        await _async_w3_init(async_provider),
    )

    # strap async_w3_a_shared_cache with async_w3_a's cache
    async_w3_a_shared_cache.provider._request_cache = async_w3_a.provider._request_cache

    mock_results_a = {RPCEndpoint("eth_chainId"): hex(11111)}
    mock_results_a_shared_cache = {RPCEndpoint("eth_chainId"): hex(00000)}
    mock_results_b = {RPCEndpoint("eth_chainId"): hex(22222)}
    mock_results_c = {RPCEndpoint("eth_chainId"): hex(33333)}

    async with request_mocker(async_w3_a, mock_results=mock_results_a):
        async with request_mocker(async_w3_b, mock_results=mock_results_b):
            async with request_mocker(async_w3_c, mock_results=mock_results_c):
                result_a = await async_w3_a.manager.coro_request("eth_chainId", [])
                result_b = await async_w3_b.manager.coro_request("eth_chainId", [])
                result_c = await async_w3_c.manager.coro_request("eth_chainId", [])

        async with request_mocker(
            async_w3_a_shared_cache, mock_results=mock_results_a_shared_cache
        ):
            # test a shared cache returns 11111, not 00000
            result_a_shared_cache = await async_w3_a_shared_cache.manager.coro_request(
                "eth_chainId", []
            )

    assert result_a == hex(11111)
    assert result_b == hex(22222)
    assert result_c == hex(33333)
    assert result_a_shared_cache == hex(11111)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "threshold",
    (RequestCacheValidationThreshold.FINALIZED, RequestCacheValidationThreshold.SAFE),
)
@pytest.mark.parametrize("endpoint", sorted(BLOCKNUM_IN_PARAMS | BLOCK_IN_RESULT))
@pytest.mark.parametrize(
    "blocknum,should_cache",
    (
        ("0x0", True),
        ("0x1", True),
        ("0x2", True),
        ("0x3", False),
        ("0x4", False),
        ("0x5", False),
    ),
)
async def test_async_blocknum_validation_against_validation_threshold_mainnet(
    threshold, endpoint, blocknum, should_cache, async_provider, request_mocker
):
    async_w3 = await _async_w3_init(async_provider, threshold=threshold)
    async with request_mocker(
        async_w3,
        mock_results={
            endpoint: (
                # mock the result to requests that return blocks
                {"number": blocknum, "timestamp": "0x0"}
                if "getBlock" in endpoint
                # mock the result to requests that return transactions
                else {"blockNumber": blocknum}
            ),
            "eth_getBlockByNumber": lambda _method, params: (
                # mock the threshold block to be blocknum "0x2", return
                # blocknum otherwise
                {"number": "0x2", "timestamp": "0x0"}
                if params[0] == threshold.value
                else {"number": params[0], "timestamp": "0x0"}
            ),
            "eth_chainId": "0x1",  # mainnet
        },
    ):
        assert len(async_w3.provider._request_cache.items()) == 0
        await async_w3.manager.coro_request(endpoint, [blocknum, False])
        cached_items = len(async_w3.provider._request_cache.items())
        assert cached_items == 1 if should_cache else cached_items == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "threshold",
    (RequestCacheValidationThreshold.FINALIZED, RequestCacheValidationThreshold.SAFE),
)
@pytest.mark.parametrize("endpoint", sorted(BLOCKNUM_IN_PARAMS))
@pytest.mark.parametrize(
    "block_id,blocknum,should_cache",
    (
        ("earliest", "0x0", True),
        ("earliest", "0x2", True),
        ("finalized", "0x2", False),
        ("safe", "0x2", False),
        ("latest", "0x2", False),
        ("pending", None, False),
    ),
)
async def test_async_block_id_param_caching_mainnet(
    threshold,
    endpoint,
    block_id,
    blocknum,
    should_cache,
    async_provider,
    request_mocker,
):
    async_w3 = await _async_w3_init(async_provider, threshold=threshold)
    async with request_mocker(
        async_w3,
        mock_results={
            "eth_chainId": "0x1",  # mainnet
            endpoint: "0x0",
            "eth_getBlockByNumber": lambda _method, params: (
                # mock the threshold block to be blocknum "0x2" for all test cases
                {"number": "0x2", "timestamp": "0x0"}
                if params[0] == threshold.value
                else {"number": blocknum, "timestamp": "0x0"}
            ),
        },
    ):
        assert len(async_w3.provider._request_cache.items()) == 0
        await async_w3.manager.coro_request(RPCEndpoint(endpoint), [block_id, False])
        cached_items = len(async_w3.provider._request_cache.items())
        assert cached_items == 1 if should_cache else cached_items == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "threshold",
    (RequestCacheValidationThreshold.FINALIZED, RequestCacheValidationThreshold.SAFE),
)
@pytest.mark.parametrize("endpoint", sorted(BLOCKHASH_IN_PARAMS))
@pytest.mark.parametrize(
    "blocknum,should_cache",
    (
        ("0x0", True),
        ("0x1", True),
        ("0x2", True),
        ("0x3", False),
        ("0x4", False),
        ("0x5", False),
    ),
)
async def test_async_blockhash_validation_against_validation_threshold_mainnet(
    threshold, endpoint, blocknum, should_cache, async_provider, request_mocker
):
    async_w3 = await _async_w3_init(async_provider, threshold=threshold)
    async with request_mocker(
        async_w3,
        mock_results={
            "eth_chainId": "0x1",  # mainnet
            "eth_getBlockByNumber": lambda _method, params: (
                # mock the threshold block to be blocknum "0x2"
                {"number": "0x2", "timestamp": "0x0"}
                if params[0] == threshold.value
                else {"number": params[0], "timestamp": "0x0"}
            ),
            "eth_getBlockByHash": {"number": blocknum, "timestamp": "0x0"},
            endpoint: "0x0",
        },
    ):
        assert len(async_w3.provider._request_cache.items()) == 0
        await async_w3.manager.coro_request(endpoint, [b"\x00" * 32, False])
        cached_items = len(async_w3.provider._request_cache.items())
        assert cached_items == 1 if should_cache else cached_items == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "chain_id,expected_threshold",
    (
        *CHAIN_VALIDATION_THRESHOLD_DEFAULTS.items(),
        (3456787654567654, DEFAULT_VALIDATION_THRESHOLD),
        (11111111111444444444444444, DEFAULT_VALIDATION_THRESHOLD),
        (-11111111111111111117, DEFAULT_VALIDATION_THRESHOLD),
    ),
)
async def test_async_request_caching_validation_threshold_defaults(
    chain_id, expected_threshold, async_provider, request_mocker
):
    async_w3 = await _async_w3_init(async_provider)
    async with request_mocker(async_w3, mock_results={"eth_chainId": hex(chain_id)}):
        await async_w3.manager.coro_request(RPCEndpoint("eth_chainId"), [])
        assert (
            async_w3.provider.request_cache_validation_threshold == expected_threshold
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint", sorted(BLOCKNUM_IN_PARAMS | BLOCK_IN_RESULT | BLOCKHASH_IN_PARAMS)
)
@pytest.mark.parametrize(
    "time_from_threshold,should_cache",
    # -0.2 to give some time for the test to run
    ((-2, True), (-1, True), (-0.2, True), (1, False), (2, False)),
)
@pytest.mark.parametrize(
    "chain_id,expected_threshold_in_seconds",
    [
        (chain_id, threshold)
        for chain_id, threshold in CHAIN_VALIDATION_THRESHOLD_DEFAULTS.items()
        if isinstance(threshold, int)
    ]
    + [
        (3456787654567654, DEFAULT_VALIDATION_THRESHOLD),
        (11111111111444444444444444, DEFAULT_VALIDATION_THRESHOLD),
        (-11111111111111111117, DEFAULT_VALIDATION_THRESHOLD),
    ],
)
async def test_async_validation_against_validation_threshold_time_based(
    endpoint,
    time_from_threshold,
    should_cache,
    chain_id,
    expected_threshold_in_seconds,
    async_provider,
    request_mocker,
):
    async_w3 = await _async_w3_init(async_provider)
    blocknum = "0x2"
    # mock the timestamp so that we are at the threshold +/- the time_from_threshold
    mocked_time = hex(
        int(round(time.time() - expected_threshold_in_seconds) + time_from_threshold)
    )

    async with request_mocker(
        async_w3,
        mock_results={
            "eth_chainId": hex(chain_id),
            endpoint: lambda *_: (
                # mock the result to requests that return blocks
                {"number": blocknum, "timestamp": mocked_time}
                if "getBlock" in endpoint
                # mock the result to requests that return transactions with the blocknum
                # for our block under test
                else {"blockNumber": blocknum}
            ),
            "eth_getBlockByNumber": lambda _method, params: (
                {"number": blocknum, "timestamp": mocked_time}
            ),
            "eth_getBlockByHash": {"number": blocknum, "timestamp": mocked_time},
        },
    ):
        assert len(async_w3.provider._request_cache.items()) == 0
        await async_w3.manager.coro_request(endpoint, [blocknum, False])
        cached_items = async_w3.provider._request_cache.items()
        assert len(cached_items) == 1 if should_cache else len(cached_items) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint", sorted(BLOCKNUM_IN_PARAMS | BLOCK_IN_RESULT | BLOCKHASH_IN_PARAMS)
)
@pytest.mark.parametrize("blocknum", ("0x0", "0x1", "0x2", "0x3", "0x4", "0x5"))
async def test_async_request_caching_with_validation_threshold_set_to_none(
    endpoint, blocknum, async_provider, request_mocker
):
    async_w3 = await _async_w3_init(async_provider, threshold=None)
    async with request_mocker(
        async_w3,
        mock_results={
            # simulate the default settings for mainnet and show that we cache
            # everything before and after the `finalized` block
            "eth_chainId": "0x1",
            endpoint: {"number": blocknum},
            "eth_getBlockByNumber": lambda _method, params: (
                # mock the threshold block to be blocknum "0x2", return
                # blocknum otherwise
                {"number": "0x2", "timestamp": "0x0"}
                if params[0] == "finalized"
                else {"number": blocknum, "timestamp": "0x0"}
            ),
        },
    ):
        assert len(async_w3.provider._request_cache.items()) == 0
        await async_w3.manager.coro_request(endpoint, [blocknum, False])
        assert len(async_w3.provider._request_cache.items()) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "time_from_threshold,should_cache",
    # -0.2 to give some time for the test to run
    ((-2, True), (-1, True), (-0.2, True), (1, False), (2, False)),
)
@pytest.mark.parametrize(
    "chain_id",
    (
        # test that defaults are also overridden by the configured validation threshold
        *CHAIN_VALIDATION_THRESHOLD_DEFAULTS.keys(),
        3456787654567654,
        11111111111444444444444444,
        -11111111111111111117,
    ),
)
@pytest.mark.parametrize(
    "endpoint", sorted(BLOCKNUM_IN_PARAMS | BLOCK_IN_RESULT | BLOCKHASH_IN_PARAMS)
)
async def test_async_validation_against_validation_threshold_time_based_configured(
    time_from_threshold,
    should_cache,
    chain_id,
    endpoint,
    async_provider,
    request_mocker,
):
    configured_time_threshold = 60 * 60 * 24 * 7  # 1 week
    async_w3 = await _async_w3_init(async_provider, threshold=configured_time_threshold)
    blocknum = "0x2"
    # mock the timestamp so that we are at the threshold +/- the time_from_threshold
    mocked_time = hex(
        int(round(time.time()) - configured_time_threshold + time_from_threshold)
    )

    async with request_mocker(
        async_w3,
        mock_results={
            "eth_chainId": chain_id,
            endpoint: lambda *_: (
                # mock the result to requests that return blocks
                {"number": blocknum, "timestamp": mocked_time}
                if "getBlock" in endpoint
                # mock the result to requests that return transactions with the blocknum
                # for our block under test
                else {"blockNumber": blocknum}
            ),
            "eth_getBlockByNumber": lambda _method, params: (
                {"number": blocknum, "timestamp": mocked_time}
            ),
            "eth_getBlockByHash": {"number": blocknum, "timestamp": mocked_time},
        },
    ):
        assert len(async_w3.provider._request_cache.items()) == 0
        await async_w3.manager.coro_request(endpoint, [blocknum, False])
        cached_items = async_w3.provider._request_cache.items()
        assert len(cached_items) == 1 if should_cache else len(cached_items) == 0


@pytest.mark.asyncio
async def test_ws_send_caching_dummy_request_preserves_method_and_params():
    # Regression for gh-3823: on a cache hit the send-caching dummy must
    # carry the original method/params so recv-caching computes the same key.
    async def fake_send(provider, method, params):
        return {"id": 1, "method": method, "params": params}

    wrapped = async_handle_send_caching(fake_send)

    async_w3 = await _async_w3_init(WebSocketProvider)
    provider = async_w3.provider

    method = RPCEndpoint("eth_chainId")
    params: list = []
    cache_key = generate_cache_key(f"{threading.get_ident()}:{(method, params)}")
    provider._request_cache.cache(
        cache_key, {"jsonrpc": "2.0", "id": 99, "result": "0x1"}
    )

    dummy = await wrapped(provider, method, params)

    assert dummy["id"] == -1
    assert dummy["method"] == method
    assert dummy["params"] == params


@pytest.mark.parametrize(
    "input_params,expected",
    [
        ((), ()),
        ({}, {}),
        (None, []),
    ],
    ids=["empty-tuple", "empty-dict", "none"],
)
def test_async_form_request_preserves_params_shape(input_params, expected):
    # Regression for gh-3823: `params or []` collapsed every falsy value
    # (empty tuple, empty dict, etc.) into `[]`, breaking cache-key equality
    # between send-caching and recv-caching for persistent-connection providers.
    provider = AsyncHTTPProvider()
    req = provider.form_request(RPCEndpoint("eth_chainId"), input_params)
    assert req["params"] == expected
    assert type(req["params"]) is type(expected)
