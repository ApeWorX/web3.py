import pytest
from unittest.mock import (
    AsyncMock,
    patch,
)

from eth_typing import (
    BlockNumber,
)
from hexbytes import (
    HexBytes,
)

from web3._utils.async_transactions import (
    async_fill_transaction_defaults,
    async_replace_transaction,
    get_block_gas_limit,
    get_buffered_gas_estimate,
)
from web3._utils.utility_methods import (
    none_in_dict,
)
from web3.constants import (
    DYNAMIC_FEE_TXN_PARAMS,
)
from web3.eth import (
    AsyncEth,
)

SIMPLE_CURRENT_TRANSACTION = {
    "blockHash": None,
    "hash": "0x0",
    "nonce": 2,
    "gasPrice": 10,
}


@pytest.mark.asyncio
async def test_async_get_block_gas_limit_with_block_number(async_w3):
    gas_limit = await get_block_gas_limit(async_w3.eth, BlockNumber(0))
    assert isinstance(gas_limit, int)


@pytest.mark.asyncio
async def test_async_get_block_gas_limit_without_block_number(async_w3):
    gas_limit = await get_block_gas_limit(async_w3.eth)
    assert isinstance(gas_limit, int)


@pytest.mark.asyncio
async def test_async_get_buffered_gas_estimate(async_w3):
    txn_params = {
        "data": b"0x1",
    }
    gas_estimate = await async_w3.eth.estimate_gas(txn_params)
    gas_buffer = 100000
    gas_limit = await get_block_gas_limit(async_w3.eth)  # type: ignore

    buffered_gas_estimate = await get_buffered_gas_estimate(async_w3, txn_params)
    assert isinstance(buffered_gas_estimate, int)
    assert buffered_gas_estimate == min(gas_estimate + gas_buffer, gas_limit)


@pytest.mark.asyncio
async def test_async_replace_transaction_awaits_gas_price_strategy(async_w3):
    async def gas_price_strategy(_async_w3, _tx):
        return 20

    async_w3.eth.set_gas_price_strategy(gas_price_strategy)
    sent_transaction = None

    async def send_transaction(transaction):
        nonlocal sent_transaction
        sent_transaction = transaction
        return HexBytes("0x01")

    with patch.object(async_w3.eth, "send_transaction", side_effect=send_transaction):
        transaction_hash = await async_replace_transaction(
            async_w3,
            SIMPLE_CURRENT_TRANSACTION,
            {"value": 2},
        )

    assert sent_transaction == {
        "value": 2,
        "nonce": 2,
        "gasPrice": 20,
    }
    assert transaction_hash == HexBytes("0x01")


@pytest.mark.asyncio
async def test_async_fill_transaction_defaults_for_all_params(async_w3):
    default_transaction = await async_fill_transaction_defaults(async_w3, {})

    block = await async_w3.eth.get_block("latest")
    assert default_transaction == {
        "chainId": await async_w3.eth.chain_id,
        "data": b"",
        "gas": await async_w3.eth.estimate_gas({}),
        "maxFeePerGas": (
            await async_w3.eth.max_priority_fee + (2 * block["baseFeePerGas"])
        ),
        "maxPriorityFeePerGas": await async_w3.eth.max_priority_fee,
        "value": 0,
    }


@pytest.mark.asyncio()
async def test_async_fill_transaction_defaults_nondynamic_transaction_fee(async_w3):
    gasPrice_transaction = {
        "gasPrice": 10,
    }
    default_transaction = await async_fill_transaction_defaults(
        async_w3, gasPrice_transaction
    )

    assert none_in_dict(DYNAMIC_FEE_TXN_PARAMS, default_transaction)


@pytest.mark.asyncio
async def test_async_default_max_fee_per_gas_uses_max_priority_fee_if_exists_in_tx(
    async_w3,
):
    fixed_base_fee = 500

    async def get_block_func(block_number):
        return {"baseFeePerGas": fixed_base_fee}

    get_block_mock = AsyncMock(side_effect=get_block_func)

    with patch.object(async_w3.eth, "get_block", side_effect=get_block_mock):
        default_transaction = await async_fill_transaction_defaults(
            async_w3, {"maxPriorityFeePerGas": 100}
        )

        assert default_transaction == {
            "chainId": await async_w3.eth.chain_id,
            "data": b"",
            "gas": await async_w3.eth.estimate_gas({}),
            "value": 0,
            "maxPriorityFeePerGas": 100,
            "maxFeePerGas": 1100,
        }


@pytest.mark.asyncio
async def test_async_default_max_fee_per_gas_uses_default_mpfee_per_gas_if_not_in_tx(
    async_w3,
):
    fixed_base_fee = 500

    async def get_block_func(value):
        return {"baseFeePerGas": fixed_base_fee}

    get_block_mock = AsyncMock(side_effect=get_block_func)

    @property
    async def max_priority_fee_mock(arg):
        return 45

    with patch.object(async_w3.eth, "get_block", side_effect=get_block_mock):
        with patch.object(AsyncEth, "max_priority_fee", new=max_priority_fee_mock):
            default_transaction = await async_fill_transaction_defaults(async_w3, {})

            assert default_transaction == {
                "chainId": await async_w3.eth.chain_id,
                "data": b"",
                "gas": await async_w3.eth.estimate_gas({}),
                "value": 0,
                "maxPriorityFeePerGas": 45,
                "maxFeePerGas": 1045,
            }


@pytest.mark.asyncio
async def test_async_fill_transaction_defaults_for_zero_gas_price(async_w3):
    def gas_price_strategy(_w3, tx):
        return 0

    async_w3.eth.set_gas_price_strategy(gas_price_strategy)

    default_transaction = await async_fill_transaction_defaults(async_w3, {})

    assert default_transaction == {
        "chainId": await async_w3.eth.chain_id,
        "data": b"",
        "gas": await async_w3.eth.estimate_gas({}),
        "value": 0,
        "gasPrice": 0,
    }


@pytest.mark.asyncio
async def test_async_fill_transaction_defaults_with_async_gas_price_strategy(
    async_w3,
):
    strategy_calls = 0

    async def gas_price_strategy(_async_w3, _tx):
        nonlocal strategy_calls
        strategy_calls += 1
        return 5

    async_w3.eth.set_gas_price_strategy(gas_price_strategy)

    default_transaction = await async_fill_transaction_defaults(async_w3, {})

    assert default_transaction == {
        "chainId": await async_w3.eth.chain_id,
        "data": b"",
        "gas": await async_w3.eth.estimate_gas({}),
        "value": 0,
        "gasPrice": 5,
    }
    assert strategy_calls == 1
