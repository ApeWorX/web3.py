import pytest
from unittest.mock import (
    Mock,
)

from web3.eth.base_eth import (
    BaseEth,
)


def test_get_set_gas_price(w3):
    assert w3.eth.gas_price > 0


def test_no_gas_price_strategy_returns_none(w3):
    assert w3.eth.generate_gas_price() is None


def test_set_gas_price_strategy(w3):
    def my_gas_price_strategy(w3, transaction_params):
        return 5

    w3.eth.set_gas_price_strategy(my_gas_price_strategy)
    assert w3.eth.generate_gas_price() == 5


def test_gas_price_strategy_calls(w3):
    transaction = {"to": "0x0", "value": 1000000000}
    my_gas_price_strategy = Mock(return_value=5)
    w3.eth.set_gas_price_strategy(my_gas_price_strategy)
    assert w3.eth.generate_gas_price(transaction) == 5
    my_gas_price_strategy.assert_called_once_with(w3, transaction)


def test_base_eth_keeps_generate_gas_price(w3):
    base_eth = BaseEth(w3)
    base_eth.set_gas_price_strategy(lambda _w3, _transaction_params: 5)

    assert base_eth.generate_gas_price() == 5


@pytest.mark.asyncio
async def test_async_no_gas_price_strategy_returns_none(async_w3):
    assert async_w3.eth.generate_gas_price() is None


@pytest.mark.asyncio
async def test_async_sync_gas_price_strategy_preserves_public_api(async_w3):
    def gas_price_strategy(_async_w3, _transaction_params):
        return 5

    async_w3.eth.set_gas_price_strategy(gas_price_strategy)

    assert async_w3.eth.generate_gas_price() == 5
    assert await async_w3.eth._async_generate_gas_price() == 5
