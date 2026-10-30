import pytest

from web3 import (
    AsyncWeb3,
    Web3,
    constants,
)
from web3.exceptions import (
    Web3ValidationError,
)
from web3.gas_strategies.time_based import (
    construct_time_based_gas_price_strategy,
)
from web3.providers.async_base import (
    AsyncBaseProvider,
)
from web3.providers.base import (
    BaseProvider,
)


def _get_block_by_something(method, params):
    block_identifier = params[0]
    if block_identifier == "latest" or block_identifier == "0x5":
        return {
            "hash": "0x0000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
            "number": 5,
            "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000004",  # noqa: E501
            "transactions": [
                {"gasPrice": 70},
                {"gasPrice": 60},
                {"gasPrice": 60},
                {"gasPrice": 60},
                {"gasPrice": 15},
                {"gasPrice": 5},
                {"gasPrice": 50},
            ],
            "miner": "0x" + "AA" * 20,
            "timestamp": 120,
        }
    elif (
        block_identifier
        == "0x0000000000000000000000000000000000000000000000000000000000000004"
        or block_identifier == "0x4"
    ):
        return {
            "hash": "0x0000000000000000000000000000000000000000000000000000000000000004",  # noqa: E501
            "number": 4,
            "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000003",  # noqa: E501
            "transactions": [
                {"gasPrice": 100},
                {"gasPrice": 80},
                {"gasPrice": 60},
            ],
            "miner": "0x" + "BB" * 20,
            "timestamp": 90,
        }
    elif (
        block_identifier
        == "0x0000000000000000000000000000000000000000000000000000000000000003"
        or block_identifier == "0x3"
    ):
        return {
            "hash": "0x0000000000000000000000000000000000000000000000000000000000000003",  # noqa: E501
            "number": 3,
            "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000002",  # noqa: E501
            "transactions": [
                {"gasPrice": 100},
            ],
            "miner": "0x" + "Cc" * 20,
            "timestamp": 60,
        }
    elif (
        block_identifier
        == "0x0000000000000000000000000000000000000000000000000000000000000002"
        or block_identifier == "0x2"
    ):
        return {
            "hash": "0x0000000000000000000000000000000000000000000000000000000000000002",  # noqa: E501
            "number": 2,
            "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000001",  # noqa: E501
            "transactions": [],
            "miner": "0x" + "Bb" * 20,
            "timestamp": 30,
        }
    elif (
        block_identifier
        == "0x0000000000000000000000000000000000000000000000000000000000000001"
        or block_identifier == "0x1"
    ):
        return {
            "hash": "0x0000000000000000000000000000000000000000000000000000000000000001",  # noqa: E501
            "number": 1,
            "parentHash": constants.HASH_ZERO,
            "transactions": [
                {"gasPrice": 30},
                {"gasPrice": 35},
                {"gasPrice": 65},
            ],
            "miner": "0x" + "Aa" * 20,
            "timestamp": 15,
        }
    elif block_identifier == "0x0":
        return {
            "hash": constants.HASH_ZERO,
            "number": 0,
            "parentHash": None,
            "transactions": [
                {"gasPrice": 30},
                {"gasPrice": 50},
                {"gasPrice": 60},
                {"gasPrice": 30},
                {"gasPrice": 50},
                {"gasPrice": 60},
                {"gasPrice": 30},
                {"gasPrice": 50},
                {"gasPrice": 60},
                {"gasPrice": 30},
                {"gasPrice": 54},
                {"gasPrice": 10000000000000000000000},
            ],
            "miner": "0x" + "Aa" * 20,
            "timestamp": 0,
        }
    else:
        raise AssertionError


@pytest.mark.parametrize(
    "strategy_params,expected",
    (
        # 80 second wait times
        (dict(max_wait_seconds=80, sample_size=5, probability=98), 70),
        (dict(max_wait_seconds=80, sample_size=5, probability=90), 25),
        (dict(max_wait_seconds=80, sample_size=5, probability=50), 11),
        # 60 second wait times
        (dict(max_wait_seconds=60, sample_size=5, probability=98), 92),
        (dict(max_wait_seconds=60, sample_size=5, probability=90), 49),
        (dict(max_wait_seconds=60, sample_size=5, probability=50), 11),
        # 40 second wait times
        (dict(max_wait_seconds=40, sample_size=5, probability=98), 100),
        (dict(max_wait_seconds=40, sample_size=5, probability=90), 81),
        (dict(max_wait_seconds=40, sample_size=5, probability=50), 11),
        # 20 second wait times
        (dict(max_wait_seconds=20, sample_size=5, probability=98), 100),
        (dict(max_wait_seconds=20, sample_size=5, probability=90), 100),
        (dict(max_wait_seconds=20, sample_size=5, probability=50), 36),
        # 80 second wait times, weighted
        (dict(max_wait_seconds=80, sample_size=5, probability=98, weighted=True), 92),
        (dict(max_wait_seconds=80, sample_size=5, probability=90, weighted=True), 49),
        (dict(max_wait_seconds=80, sample_size=5, probability=50, weighted=True), 11),
    ),
)
def test_time_based_gas_price_strategy(strategy_params, expected, request_mocker):
    w3 = Web3(provider=BaseProvider())

    time_based_gas_price_strategy = construct_time_based_gas_price_strategy(
        **strategy_params,
    )
    w3.eth.set_gas_price_strategy(time_based_gas_price_strategy)
    with request_mocker(
        w3,
        mock_results={
            "eth_getBlockByHash": _get_block_by_something,
            "eth_getBlockByNumber": _get_block_by_something,
        },
    ):
        actual = w3.eth.generate_gas_price()
        assert actual == expected


@pytest.mark.parametrize(
    "strategy_params,expected",
    (
        (dict(max_wait_seconds=80, sample_size=5, probability=98), 70),
        (
            dict(
                max_wait_seconds=80,
                sample_size=5,
                probability=98,
                weighted=True,
            ),
            92,
        ),
    ),
)
@pytest.mark.asyncio
async def test_time_based_gas_price_strategy_with_async_web3(
    strategy_params, expected, request_mocker
):
    async_w3 = AsyncWeb3(provider=AsyncBaseProvider())
    time_based_gas_price_strategy = construct_time_based_gas_price_strategy(
        **strategy_params,
    )
    async_w3.eth.set_gas_price_strategy(time_based_gas_price_strategy)

    async with request_mocker(
        async_w3,
        mock_results={
            "eth_getBlockByHash": _get_block_by_something,
            "eth_getBlockByNumber": _get_block_by_something,
        },
    ):
        actual = await async_w3.eth._async_generate_gas_price()

    assert actual == expected


def _get_initial_block(method, params):
    return {
        "hash": constants.HASH_ZERO,
        "number": 0,
        "parentHash": None,
        "transactions": [],
        "miner": "0x" + "Aa" * 20,
        "timestamp": 0,
    }


def _get_gas_price(method, params):
    return 4321


def test_time_based_gas_price_strategy_without_transactions(request_mocker):
    w3 = Web3(provider=BaseProvider())

    time_based_gas_price_strategy = construct_time_based_gas_price_strategy(
        max_wait_seconds=80,
        sample_size=5,
        probability=50,
        weighted=True,
    )
    w3.eth.set_gas_price_strategy(time_based_gas_price_strategy)
    with request_mocker(
        w3,
        mock_results={
            "eth_getBlockByHash": _get_initial_block,
            "eth_getBlockByNumber": _get_initial_block,
            "eth_gasPrice": _get_gas_price,
        },
    ):
        actual = w3.eth.generate_gas_price()
        assert actual == w3.eth.gas_price


@pytest.mark.asyncio
async def test_time_based_gas_price_strategy_without_transactions_async(
    request_mocker,
):
    async_w3 = AsyncWeb3(provider=AsyncBaseProvider())

    time_based_gas_price_strategy = construct_time_based_gas_price_strategy(
        max_wait_seconds=80,
        sample_size=5,
        probability=50,
        weighted=True,
    )
    async_w3.eth.set_gas_price_strategy(time_based_gas_price_strategy)
    async with request_mocker(
        async_w3,
        mock_results={
            "eth_getBlockByHash": _get_initial_block,
            "eth_getBlockByNumber": _get_initial_block,
            "eth_gasPrice": _get_gas_price,
        },
    ):
        actual = await async_w3.eth._async_generate_gas_price()

    assert actual == 4321


@pytest.mark.parametrize(
    "strategy_params_zero,expected_exception_message",
    (
        # 120 second wait times, 0 sample_size
        (
            dict(max_wait_seconds=80, sample_size=0, probability=98),
            "Constrained sample size is 0",
        ),
        (
            dict(max_wait_seconds=80, sample_size=0, probability=90),
            "Constrained sample size is 0",
        ),
        (
            dict(max_wait_seconds=80, sample_size=0, probability=50),
            "Constrained sample size is 0",
        ),
        # 60 second wait times, 0 sample_size
        (
            dict(max_wait_seconds=60, sample_size=0, probability=98),
            "Constrained sample size is 0",
        ),
        (
            dict(max_wait_seconds=60, sample_size=0, probability=90),
            "Constrained sample size is 0",
        ),
        (
            dict(max_wait_seconds=60, sample_size=0, probability=50),
            "Constrained sample size is 0",
        ),
        # 40 second wait times, 0 sample_size
        (
            dict(max_wait_seconds=40, sample_size=0, probability=98),
            "Constrained sample size is 0",
        ),
        (
            dict(max_wait_seconds=40, sample_size=0, probability=90),
            "Constrained sample size is 0",
        ),
        (
            dict(max_wait_seconds=40, sample_size=0, probability=50),
            "Constrained sample size is 0",
        ),
        # 20 second wait times, 0 sample_size
        (
            dict(max_wait_seconds=20, sample_size=0, probability=98),
            "Constrained sample size is 0",
        ),
        (
            dict(max_wait_seconds=20, sample_size=0, probability=90),
            "Constrained sample size is 0",
        ),
        (
            dict(max_wait_seconds=20, sample_size=0, probability=50),
            "Constrained sample size is 0",
        ),
    ),
)
def test_time_based_gas_price_strategy_zero_sample(
    strategy_params_zero, expected_exception_message, request_mocker
):
    with pytest.raises(Web3ValidationError) as excinfo:
        w3 = Web3(provider=BaseProvider())
        time_based_gas_price_strategy_zero = construct_time_based_gas_price_strategy(
            **strategy_params_zero,
        )
        w3.eth.set_gas_price_strategy(time_based_gas_price_strategy_zero)
        with request_mocker(
            w3,
            mock_results={
                "eth_getBlockByHash": _get_block_by_something,
                "eth_getBlockByNumber": _get_block_by_something,
            },
        ):
            w3.eth.generate_gas_price()
    assert str(excinfo.value) == expected_exception_message


@pytest.mark.asyncio
async def test_time_based_gas_price_strategy_zero_sample_async(request_mocker):
    async_w3 = AsyncWeb3(provider=AsyncBaseProvider())
    time_based_gas_price_strategy = construct_time_based_gas_price_strategy(
        max_wait_seconds=80,
        sample_size=0,
        probability=98,
    )
    async_w3.eth.set_gas_price_strategy(time_based_gas_price_strategy)

    with pytest.raises(Web3ValidationError, match="Constrained sample size is 0"):
        async with request_mocker(
            async_w3,
            mock_results={
                "eth_getBlockByHash": _get_block_by_something,
                "eth_getBlockByNumber": _get_block_by_something,
            },
        ):
            await async_w3.eth._async_generate_gas_price()
