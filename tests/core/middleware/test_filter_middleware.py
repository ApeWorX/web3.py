import pytest

from hexbytes import (
    HexBytes,
)
import pytest_asyncio

from web3 import (
    AsyncWeb3,
    Web3,
)
from web3.datastructures import (
    AttributeDict,
)
from web3.middleware import (
    AttributeDictMiddleware,
    LocalFilterMiddleware,
)
from web3.middleware.filter import (
    async_iter_latest_block_ranges,
    block_ranges,
    iter_latest_block_ranges,
)
from web3.providers.async_base import (
    AsyncBaseProvider,
)
from web3.providers.base import (
    BaseProvider,
)


class DummyProvider(BaseProvider):
    def make_request(self, method, params):
        raise NotImplementedError(f"Cannot make request for {method}:{params}")


BLOCK_HASH = "0xfe88c94d860f01a17f961bf4bdfb6e0c6cd10d3fda5cc861e805ca1240c58553"
FILTER_LOG = [
    AttributeDict(
        {
            "address": "0xDc3A9Db694BCdd55EBaE4A89B22aC6D12b3F0c24",
            "blockHash": HexBytes(
                "0xb72256286ca528e09022ffd408856a73ef90e7216ac560187c6e43b4c4efd2f0"
            ),
            "blockNumber": 2217196,
            "data": HexBytes(
                "0x0000000000000000000000000000000000000000000000000000000000000001"
            ),
            "logIndex": 0,
            "topics": [
                HexBytes(
                    "0xe65b00b698ba37c614af350761c735c5f4a82b4ab365a1f1022d49d9dfc8e930"
                ),
                HexBytes(
                    "0x000000000000000000000000754c50465885f1ed1fa1a55b95ee8ecf3f1f4324"
                ),
                HexBytes(
                    "0x296c7fb6ccafa3e689950b947c2895b07357c95b066d5cdccd58c301f41359a3"
                ),
            ],
            "transactionHash": HexBytes(
                "0xfe1289fd3915794b99702202f65eea2e424b2f083a12749d29b4dd51f6dce40d"
            ),
            "transactionIndex": 1,
        }
    )
]


@pytest.fixture(scope="function")
def iter_block_number(start=0):
    def iterator():
        block_number = start
        while True:
            sent_value = yield block_number
            if sent_value is not None:
                block_number = sent_value

    block_number = iterator()
    next(block_number)
    return block_number


@pytest.fixture(scope="function")
def w3(request_mocker, iter_block_number):
    w3_base = Web3(provider=DummyProvider(), middleware=[])
    w3_base.middleware_onion.add(AttributeDictMiddleware)
    w3_base.middleware_onion.add(LocalFilterMiddleware)
    with request_mocker(
        w3_base,
        mock_results={
            "eth_getLogs": lambda *_: FILTER_LOG,
            "eth_getBlockByNumber": lambda *_: {"hash": BLOCK_HASH},
            "net_version": lambda *_: 1,
            "eth_blockNumber": lambda *_: next(iter_block_number),
        },
    ):
        yield w3_base


@pytest.mark.parametrize(
    "start, stop, expected",
    [
        (2, 7, [(2, 6), (7, 7)]),
        (0, 12, [(0, 4), (5, 9), (10, 12)]),
        (0, 15, [(0, 4), (5, 9), (10, 14), (15, 15)]),
        (
            0,
            0,
            [
                (0, 0),
            ],
        ),
        (
            1,
            1,
            [
                (1, 1),
            ],
        ),
        (5, 0, TypeError),
    ],
)
def test_block_ranges(start, stop, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            block_ranges(start, stop)
    else:
        actual = tuple(block_ranges(start, stop))
        assert len(actual) == len(expected)
        for actual_item, expected_item in zip(actual, expected):
            assert actual_item == expected_item


@pytest.mark.parametrize(
    "from_block,to_block,current_block,expected",
    [
        (
            0,
            10,
            [10],
            [
                (0, 10),
            ],
        ),
        (
            0,
            55,
            [0, 19, 55],
            [
                (0, 0),
                (1, 19),
                (20, 55),
            ],
        ),
        (
            0,
            None,
            [10],
            [
                (0, 10),
            ],
        ),
        (
            0,
            10,
            [12],
            [
                (None, None),
            ],
        ),
        (
            12,
            10,
            [12],
            [
                (None, None),
            ],
        ),
        (
            12,
            10,
            [None],
            [
                (None, None),
            ],
        ),
        (
            10,
            10,
            [10, 10],
            [
                (10, 10),
                (None, None),
            ],
        ),
    ],
)
def test_iter_latest_block_ranges(
    w3, iter_block_number, from_block, to_block, current_block, expected
):
    latest_block_ranges = iter_latest_block_ranges(w3, from_block, to_block)
    for index, block in enumerate(current_block):
        iter_block_number.send(block)
        expected_tuple = expected[index]
        actual_tuple = next(latest_block_ranges)
        assert actual_tuple == expected_tuple


def test_pending_block_filter_middleware(w3):
    with pytest.raises(NotImplementedError):
        w3.eth.filter("pending")


def test_LocalFilterMiddleware(w3, iter_block_number):
    block_filter = w3.eth.filter("latest")
    block_filter.get_new_entries()
    iter_block_number.send(1)
    assert w3.eth.get_filter_changes(block_filter.filter_id) == [HexBytes(BLOCK_HASH)]

    log_filter = w3.eth.filter(filter_params={"fromBlock": "latest"})
    iter_block_number.send(2)
    log_changes = w3.eth.get_filter_changes(log_filter.filter_id)
    assert log_changes == FILTER_LOG
    assert w3.eth.get_filter_logs(log_filter.filter_id) == FILTER_LOG

    log_filter_from_hex_string = w3.eth.filter(
        filter_params={"fromBlock": "0x0", "toBlock": "0x2"}
    )
    log_filter_from_int = w3.eth.filter(filter_params={"fromBlock": 1, "toBlock": 3})

    filter_ids = (
        block_filter.filter_id,
        log_filter.filter_id,
        log_filter_from_hex_string.filter_id,
        log_filter_from_int.filter_id,
    )

    # Test that all ids are str types
    assert all(isinstance(_filter_id, str) for _filter_id in filter_ids)

    # Test that all ids are unique
    assert len(filter_ids) == len(set(filter_ids))


# --- async --- #


class AsyncDummyProvider(AsyncBaseProvider):
    async def make_request(self, method, params):
        raise NotImplementedError(f"Cannot make request for {method}:{params}")


@pytest_asyncio.fixture(scope="function")
async def async_w3(request_mocker, iter_block_number):
    async_w3_base = AsyncWeb3(provider=AsyncDummyProvider(), middleware=[])
    async_w3_base.middleware_onion.add(AttributeDictMiddleware)
    async_w3_base.middleware_onion.add(LocalFilterMiddleware)

    async with request_mocker(
        async_w3_base,
        mock_results={
            "eth_getLogs": lambda *_: FILTER_LOG,
            "eth_getBlockByNumber": lambda *_: {"hash": BLOCK_HASH},
            "net_version": lambda *_: 1,
            "eth_blockNumber": lambda *_: next(iter_block_number),
        },
    ):
        yield async_w3_base


@pytest.mark.parametrize(
    "from_block,to_block,current_block,expected",
    [
        (
            0,
            10,
            [10],
            [
                (0, 10),
            ],
        ),
        (
            0,
            55,
            [0, 19, 55],
            [
                (0, 0),
                (1, 19),
                (20, 55),
            ],
        ),
        (
            0,
            None,
            [10],
            [
                (0, 10),
            ],
        ),
        (
            0,
            10,
            [12],
            [
                (None, None),
            ],
        ),
        (
            12,
            10,
            [12],
            [
                (None, None),
            ],
        ),
        (
            12,
            10,
            [None],
            [
                (None, None),
            ],
        ),
        (
            10,
            10,
            [10, 10],
            [
                (10, 10),
                (None, None),
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_async_iter_latest_block_ranges(
    async_w3, iter_block_number, from_block, to_block, current_block, expected
):
    latest_block_ranges = async_iter_latest_block_ranges(async_w3, from_block, to_block)
    for index, block in enumerate(current_block):
        iter_block_number.send(block)
        expected_tuple = expected[index]
        actual_tuple = await latest_block_ranges.__anext__()
        assert actual_tuple == expected_tuple


@pytest.mark.asyncio
async def test_async_LocalFilterMiddleware(async_w3, iter_block_number):
    block_filter = await async_w3.eth.filter("latest")
    await block_filter.get_new_entries()
    iter_block_number.send(1)
    block_changes = await async_w3.eth.get_filter_changes(block_filter.filter_id)
    assert block_changes == [HexBytes(BLOCK_HASH)]

    log_filter = await async_w3.eth.filter(filter_params={"fromBlock": "latest"})
    iter_block_number.send(2)
    log_changes = await async_w3.eth.get_filter_changes(log_filter.filter_id)
    assert log_changes == FILTER_LOG
    logs = await async_w3.eth.get_filter_logs(log_filter.filter_id)
    assert logs == FILTER_LOG

    log_filter_from_hex_string = await async_w3.eth.filter(
        filter_params={"fromBlock": "0x0", "toBlock": "0x2"}
    )
    log_filter_from_int = await async_w3.eth.filter(
        filter_params={"fromBlock": 1, "toBlock": 3}
    )

    filter_ids = (
        block_filter.filter_id,
        log_filter.filter_id,
        log_filter_from_hex_string.filter_id,
        log_filter_from_int.filter_id,
    )

    # Test that all ids are str types
    assert all(isinstance(_filter_id, str) for _filter_id in filter_ids)

    # Test that all ids are unique
    assert len(filter_ids) == len(set(filter_ids))
