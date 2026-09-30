import pytest
from eth_utils import is_integer
from web3 import AsyncWeb3
from web3.providers.eth_tester import AsyncEthereumTesterProvider


@pytest.fixture
def async_w3():
    return AsyncWeb3(AsyncEthereumTesterProvider())


@pytest.mark.asyncio
async def test_eth_block_number(async_w3):
    block_number = await async_w3.eth.block_number
    assert is_integer(block_number)
    assert block_number >= 0


@pytest.mark.asyncio
async def test_eth_get_block_number(async_w3):
    block_number = await async_w3.eth.get_block_number()
    assert is_integer(block_number)
    assert block_number >= 0


@pytest.mark.asyncio
async def test_eth_get_balance_with_block_identifier(async_w3):
    genesis_block = await async_w3.eth.get_block(0)
    miner_address = genesis_block["miner"]

    balance_genesis = await async_w3.eth.get_balance(miner_address, 0)
    later_balance = await async_w3.eth.get_balance(miner_address, "latest")

    assert is_integer(balance_genesis)
    assert is_integer(later_balance)