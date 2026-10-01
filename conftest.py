import pytest
import inspect
import time
import warnings

# Monkey-patch cached_property to use inspect.iscoroutinefunction
# instead of the deprecated asyncio.iscoroutinefunction (deprecated in Python 3.14+)
# cached_property is a dependency of py-evm, so once we remove py-evm
# or once cached_property gets a release, we can remove this.
# https://github.com/pydanny/cached-property/issues/276
import cached_property as _cached_property_module
import pytest_asyncio

from tests.utils import (
    PollDelayCounter,
    _async_wait_for_block_fixture_logic,
    _async_wait_for_transaction_fixture_logic,
)
from web3._utils.threads import (
    Timeout,
)
from web3.main import (
    Web3,
)
from web3.providers.eth_tester import (
    AsyncEthereumTesterProvider,
    EthereumTesterProvider,
)

_cached_property_module.asyncio.iscoroutinefunction = inspect.iscoroutinefunction


@pytest.fixture()
def sleep_interval():
    return PollDelayCounter()


def is_testrpc_provider(provider):
    return isinstance(provider, EthereumTesterProvider)


@pytest.fixture()
def skip_if_testrpc():
    def _skip_if_testrpc(w3):
        if is_testrpc_provider(w3.provider):
            pytest.skip()

    return _skip_if_testrpc


@pytest.fixture(scope="module")
def wait_for_block():
    def _wait_for_block(w3, block_number=1, timeout=None):
        if not timeout:
            timeout = (block_number - w3.eth.block_number) * 3
        poll_delay_counter = PollDelayCounter()
        with Timeout(timeout) as timeout:
            while w3.eth.block_number < block_number:
                w3.manager.request_blocking("evm_mine", [])
                timeout.sleep(poll_delay_counter())

    return _wait_for_block


@pytest.fixture(scope="module")
def wait_for_transaction():
    def _wait_for_transaction(w3, txn_hash, timeout=120):
        poll_delay_counter = PollDelayCounter()
        with Timeout(timeout) as timeout:
            while True:
                txn_receipt = w3.eth.get_transaction_receipt(txn_hash)
                if txn_receipt is not None:
                    break
                time.sleep(poll_delay_counter())
                timeout.check()

        return txn_receipt

    return _wait_for_transaction


@pytest.fixture
def w3():
    w3 = Web3(EthereumTesterProvider())
    w3.eth.default_account = w3.eth.accounts[0]
    return w3


@pytest.fixture(scope="module")
def w3_non_strict_abi():
    w3 = Web3(EthereumTesterProvider())
    w3.eth.default_account = w3.eth.accounts[0]
    w3.strict_bytes_type_checking = False
    return w3


@pytest.fixture(autouse=True)
def print_warnings():
    warnings.simplefilter("always")


# --- async --- #


def is_async_testrpc_provider(provider):
    return isinstance(provider, AsyncEthereumTesterProvider)


@pytest.fixture()
def async_skip_if_testrpc():
    def _skip_if_testrpc(async_w3):
        if is_async_testrpc_provider(async_w3.provider):
            pytest.skip()

    return _skip_if_testrpc


@pytest_asyncio.fixture()
async def async_wait_for_block():
    return _async_wait_for_block_fixture_logic


@pytest_asyncio.fixture()
async def async_wait_for_transaction():
    return _async_wait_for_transaction_fixture_logic
