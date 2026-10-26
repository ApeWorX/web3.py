import pytest

import pytest_asyncio

from web3 import (
    AsyncWeb3,
    Web3,
)
from web3.exceptions import (
    NameNotFound,
)
from web3.middleware import (
    ENSNameToAddressMiddleware,
)
from web3.providers.eth_tester import (
    AsyncEthereumTesterProvider,
    EthereumTesterProvider,
)

NAME = "tester.eth"


class TempENS:
    def __init__(self, name_addr_pairs):
        self.registry = dict(name_addr_pairs)

    def address(self, name):
        return self.registry.get(name, None)


@pytest.fixture
def _w3_setup():
    return Web3(provider=EthereumTesterProvider(), middleware=[])


@pytest.fixture
def ens_mapped_address(_w3_setup):
    return _w3_setup.eth.accounts[0]


@pytest.fixture
def ens_addr_account_balance(ens_mapped_address, _w3_setup):
    return _w3_setup.eth.get_balance(ens_mapped_address)


@pytest.fixture
def w3(_w3_setup, ens_mapped_address):
    _w3_setup.ens = TempENS({NAME: ens_mapped_address})
    ENSNameToAddressMiddleware._w3 = _w3_setup
    _w3_setup.middleware_onion.add(ENSNameToAddressMiddleware)
    return _w3_setup


@pytest.mark.parametrize(
    "params",
    (
        [NAME, "latest"],
        [NAME, 0],
        [NAME],
    ),
)
def test_pass_name_resolver_get_balance_list_args(
    w3,
    ens_addr_account_balance,
    params,
):
    assert w3.eth.get_balance(*params) == ens_addr_account_balance


@pytest.mark.parametrize(
    "params",
    (
        {"value": 1, "from": NAME, "to": NAME, "gas": 21000},
        {
            "value": 1,
            "maxPriorityFeePerGas": 10**9,
            "from": NAME,
            "to": NAME,
            "gas": 21000,
        },
        {"value": 1, "to": NAME, "gas": 21000, "from": NAME},
    ),
)
def test_pass_name_resolver_send_transaction_dict_args(
    w3,
    params,
    ens_mapped_address,
):
    tx_hash = w3.eth.send_transaction(params)

    tx = w3.eth.get_transaction(tx_hash)
    assert tx["from"] == ens_mapped_address
    assert tx["to"] == ens_mapped_address


def test_fail_name_resolver(w3):
    with pytest.raises(NameNotFound, match=r".*ethereum\.eth.*"):
        w3.eth.get_balance("ethereum.eth")


# --- async --- #


class AsyncTempENS(TempENS):
    async def address(self, name):
        return self.registry.get(name, None)


@pytest_asyncio.fixture
async def _async_w3_setup():
    return AsyncWeb3(provider=AsyncEthereumTesterProvider(), middleware=[])


@pytest_asyncio.fixture
async def async_ens_mapped_address(_async_w3_setup):
    accts = await _async_w3_setup.eth.accounts
    return accts[0]


@pytest_asyncio.fixture
async def async_ens_addr_account_balance(async_ens_mapped_address, _async_w3_setup):
    return await _async_w3_setup.eth.get_balance(async_ens_mapped_address)


@pytest_asyncio.fixture
async def async_w3(_async_w3_setup, async_ens_mapped_address):
    _async_w3_setup.ens = AsyncTempENS({NAME: async_ens_mapped_address})
    _async_w3_setup.middleware_onion.add(ENSNameToAddressMiddleware)
    return _async_w3_setup


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    (
        [NAME, "latest"],
        [NAME, 0],
        [NAME],
    ),
)
async def test_async_pass_name_resolver_get_balance_list_args(
    async_w3,
    async_ens_addr_account_balance,
    params,
):
    assert await async_w3.eth.get_balance(*params) == async_ens_addr_account_balance


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    (
        {"value": 1, "from": NAME, "to": NAME, "gas": 21000},
        {
            "value": 1,
            "maxPriorityFeePerGas": 10**9,
            "from": NAME,
            "to": NAME,
            "gas": 21000,
        },
        {"value": 1, "to": NAME, "gas": 21000, "from": NAME},
    ),
)
async def test_async_pass_name_resolver_send_transaction_dict_args(
    async_w3,
    params,
    async_ens_mapped_address,
):
    tx_hash = await async_w3.eth.send_transaction(params)

    tx = await async_w3.eth.get_transaction(tx_hash)
    assert tx["from"] == async_ens_mapped_address
    assert tx["to"] == async_ens_mapped_address


@pytest.mark.asyncio
async def test_async_fail_name_resolver(async_w3):
    with pytest.raises(NameNotFound, match=r".*ethereum\.eth.*"):
        await async_w3.eth.get_balance("ethereum.eth")
