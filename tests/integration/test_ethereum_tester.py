import pytest
import functools
from typing import (
    cast,
)

from eth_tester import (
    EthereumTester,
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from eth_typing import (
    ChecksumAddress,
)
from eth_utils import (
    is_checksum_address,
    is_dict,
    is_integer,
)

from web3 import (
    Web3,
)
from web3._utils.contract_sources.contract_data._custom_contract_data import (
    EMITTER_ENUM,
)
from web3._utils.contract_sources.contract_data.panic_errors_contract import (
    PANIC_ERRORS_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.storage_contract import (
    STORAGE_CONTRACT_DATA,
)
from web3._utils.module_testing import (
    EthModuleTest,
    NetModuleTest,
    Web3ModuleTest,
)
from web3._utils.module_testing.eth_module import (
    UNKNOWN_ADDRESS,
)
from web3.exceptions import (
    MethodUnavailable,
    Web3TypeError,
)
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)
from web3.types import (  # noqa: F401
    BlockData,
)

# set up the keyfile account with a known address (same from geth setup)
KEYFILE_ACCOUNT_PKEY = (
    "0x58d23b55bc9cdce1f18c2500f40ff4ab7245df9a89505e9b1fa4851f623d241d"
)
KEYFILE_ACCOUNT_ADDRESS = "0xdC544d1AA88Ff8bbd2F2AeC754B1F1e99e1812fd"


def _deploy_contract(w3, contract_factory):
    deploy_txn_hash = contract_factory.constructor().transact(
        {"from": w3.eth.default_account}
    )
    deploy_receipt = w3.eth.wait_for_transaction_receipt(deploy_txn_hash)
    assert is_dict(deploy_receipt)
    contract_address = deploy_receipt["contractAddress"]
    assert is_checksum_address(contract_address)
    return contract_factory(contract_address)


@pytest.fixture
def eth_tester():
    _eth_tester = EthereumTester()
    return _eth_tester


@pytest.fixture
def eth_tester_provider(eth_tester):
    provider = EthereumTesterProvider(eth_tester)
    return provider


def _eth_tester_state_setup(w3):
    provider = cast(EthereumTesterProvider, w3.provider)
    provider.ethereum_tester.add_account(KEYFILE_ACCOUNT_PKEY)

    # fund the account
    w3.eth.send_transaction(
        {
            "from": ChecksumAddress(w3.eth.default_account),
            "to": KEYFILE_ACCOUNT_ADDRESS,
            "value": w3.to_wei(0.5, "ether"),
            "gas": 21000,
            "gasPrice": 10**9,  # needs to be > base_fee post London
        }
    )


@pytest.fixture
def w3(eth_tester_provider):
    _w3 = Web3(eth_tester_provider)
    _w3.eth.default_account = _w3.eth.accounts[0]
    _eth_tester_state_setup(_w3)
    return _w3


@pytest.fixture
def math_contract_deploy_txn_hash(w3, math_contract_factory):
    deploy_txn_hash = math_contract_factory.constructor().transact(
        {"from": w3.eth.default_account}
    )
    return deploy_txn_hash


@pytest.fixture
def math_contract(w3, math_contract_factory, math_contract_deploy_txn_hash):
    deploy_receipt = w3.eth.wait_for_transaction_receipt(math_contract_deploy_txn_hash)
    assert is_dict(deploy_receipt)
    contract_address = deploy_receipt["contractAddress"]
    assert is_checksum_address(contract_address)
    return math_contract_factory(contract_address)


@pytest.fixture
def math_contract_address(math_contract, address_conversion_func):
    return address_conversion_func(math_contract.address)


@pytest.fixture
def storage_contract(w3):
    contract_factory = w3.eth.contract(**STORAGE_CONTRACT_DATA)
    return _deploy_contract(w3, contract_factory)


@pytest.fixture
def emitter_contract(w3, emitter_contract_factory):
    return _deploy_contract(w3, emitter_contract_factory)


@pytest.fixture
def emitter_contract_address(emitter_contract, address_conversion_func):
    return address_conversion_func(emitter_contract.address)


@pytest.fixture
def empty_block(w3):
    w3.testing.mine()
    block = w3.eth.get_block("latest")
    assert not block["transactions"]
    return block


@pytest.fixture
def block_with_txn(w3):
    txn_hash = w3.eth.send_transaction(
        {
            "from": ChecksumAddress(w3.eth.default_account),
            "to": ChecksumAddress(w3.eth.default_account),
            "value": w3.to_wei(1, "gwei"),
            "gas": 21000,
            "gasPrice": w3.to_wei(10**9, "gwei"),  # needs to be > base_fee post London
        }
    )
    txn = w3.eth.get_transaction(txn_hash)
    block = w3.eth.get_block(txn["blockNumber"])
    return block


@pytest.fixture
def mined_txn_hash(block_with_txn):
    return block_with_txn["transactions"][0]


@pytest.fixture
def block_with_txn_with_log(w3, emitter_contract):
    txn_hash = emitter_contract.functions.logDouble(
        which=EMITTER_ENUM["LogDoubleWithIndex"],
        arg0=12345,
        arg1=54321,
    ).transact({"from": w3.eth.default_account})
    txn = w3.eth.get_transaction(txn_hash)
    block = w3.eth.get_block(txn["blockNumber"])
    return block


@pytest.fixture
def txn_hash_with_log(block_with_txn_with_log):
    return block_with_txn_with_log["transactions"][0]


@pytest.fixture
def revert_contract(w3, revert_contract_factory):
    return _deploy_contract(w3, revert_contract_factory)


#
# Offchain Lookup Contract Setup
#
@pytest.fixture
def offchain_lookup_contract(w3, offchain_lookup_contract_factory):
    return _deploy_contract(w3, offchain_lookup_contract_factory)


@pytest.fixture
def panic_errors_contract(w3):
    panic_errors_contract_factory = w3.eth.contract(**PANIC_ERRORS_CONTRACT_DATA)
    return _deploy_contract(w3, panic_errors_contract_factory)


@pytest.fixture
def keyfile_account_pkey():
    yield KEYFILE_ACCOUNT_PKEY


@pytest.fixture
def keyfile_account_address():
    yield KEYFILE_ACCOUNT_ADDRESS


@pytest.fixture
def keyfile_account_address_dual_type(keyfile_account_address, address_conversion_func):
    yield keyfile_account_address


def not_implemented(method, exc_type=NotImplementedError):
    @functools.wraps(method)
    def inner(*args, **kwargs):
        with pytest.raises(exc_type):
            method(*args, **kwargs)

    return inner


def disable_auto_mine(func):
    @functools.wraps(func)
    def func_wrapper(self, eth_tester, *args, **kwargs):
        snapshot = eth_tester.take_snapshot()
        eth_tester.disable_auto_mine_transactions()
        try:
            func(self, eth_tester, *args, **kwargs)
        finally:
            eth_tester.enable_auto_mine_transactions()
            eth_tester.mine_block()
            eth_tester.revert_to_snapshot(snapshot)

    return func_wrapper


class TestEthereumTesterWeb3Module(Web3ModuleTest):
    def _check_web3_client_version(self, client_version):
        assert client_version.startswith("EthereumTester/")

    test_batch_requests = not_implemented(
        Web3ModuleTest.test_batch_requests, Web3TypeError
    )
    test_batch_requests_raises_for_common_unsupported_methods = not_implemented(
        Web3ModuleTest.test_batch_requests_raises_for_common_unsupported_methods,
        Web3TypeError,
    )
    test_batch_requests_initialized_as_object = not_implemented(
        Web3ModuleTest.test_batch_requests_initialized_as_object, Web3TypeError
    )
    test_batch_requests_cancel = not_implemented(
        Web3ModuleTest.test_batch_requests_cancel, Web3TypeError
    )
    test_batch_requests_clear = not_implemented(
        Web3ModuleTest.test_batch_requests_clear, Web3TypeError
    )

    @pytest.mark.skip("EthereumTesterProvider does not support batch requests")
    def test_batch_requests_concurrently_with_regular_requests(self, w3):
        # batching is not supported by ``EthereumTesterProvider`` and the exception
        # is triggered in a different thread so not caught by it. Skip it here instead.
        pass


class TestEthereumTesterEthModule(EthModuleTest):
    test_eth_sign = not_implemented(EthModuleTest.test_eth_sign, MethodUnavailable)
    test_eth_sign_ens_names = not_implemented(
        EthModuleTest.test_eth_sign_ens_names, MethodUnavailable
    )
    test_eth_sign_typed_data = not_implemented(
        EthModuleTest.test_eth_sign_typed_data, MethodUnavailable
    )
    test_eth_sign_transaction_legacy = not_implemented(
        EthModuleTest.test_eth_sign_transaction_legacy, MethodUnavailable
    )
    test_eth_sign_transaction = not_implemented(
        EthModuleTest.test_eth_sign_transaction, MethodUnavailable
    )
    test_eth_sign_transaction_hex_fees = not_implemented(
        EthModuleTest.test_eth_sign_transaction_hex_fees, MethodUnavailable
    )
    test_eth_sign_transaction_ens_names = not_implemented(
        EthModuleTest.test_eth_sign_transaction_ens_names, MethodUnavailable
    )
    test_eth_get_raw_transaction = not_implemented(
        EthModuleTest.test_eth_get_raw_transaction, MethodUnavailable
    )
    test_eth_get_raw_transaction_raises_error = not_implemented(
        EthModuleTest.test_eth_get_raw_transaction, MethodUnavailable
    )
    test_eth_get_raw_transaction_by_block = not_implemented(
        EthModuleTest.test_eth_get_raw_transaction_by_block, MethodUnavailable
    )
    test_eth_get_raw_transaction_by_block_raises_error = not_implemented(
        EthModuleTest.test_eth_get_raw_transaction_by_block, MethodUnavailable
    )
    test_eth_call_with_override_param_type_check = not_implemented(
        EthModuleTest.test_eth_call_with_override_param_type_check,
        TypeError,
    )
    test_eth_estimate_gas_with_override_param_type_check = not_implemented(
        EthModuleTest.test_eth_estimate_gas_with_override_param_type_check,
        TypeError,
    )
    test_eth_create_access_list = not_implemented(
        EthModuleTest.test_eth_create_access_list,
        MethodUnavailable,
    )
    test_eth_call_with_override_code = not_implemented(
        EthModuleTest.test_eth_call_with_override_code,
        TypeError,
    )
    test_eth_getBlockReceipts_hash = not_implemented(
        EthModuleTest.test_eth_getBlockReceipts_hash,
        MethodUnavailable,
    )
    test_eth_getBlockReceipts_not_found = not_implemented(
        EthModuleTest.test_eth_getBlockReceipts_not_found,
        MethodUnavailable,
    )
    test_eth_getBlockReceipts_with_integer = not_implemented(
        EthModuleTest.test_eth_getBlockReceipts_with_integer,
        MethodUnavailable,
    )
    test_eth_getBlockReceipts_safe = not_implemented(
        EthModuleTest.test_eth_getBlockReceipts_safe,
        MethodUnavailable,
    )
    test_eth_getBlockReceipts_finalized = not_implemented(
        EthModuleTest.test_eth_getBlockReceipts_finalized,
        MethodUnavailable,
    )
    test_eth_simulate_v1 = not_implemented(
        EthModuleTest.test_eth_simulate_v1,
        MethodUnavailable,
    )

    def test_eth_getBlockByHash_pending(self, w3: "Web3") -> None:
        block = w3.eth.get_block("pending")
        assert block["hash"] is not None

    @disable_auto_mine
    def test_eth_get_transaction_receipt_unmined(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_get_transaction_receipt_unmined(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_replace_transaction_legacy(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_replace_transaction_legacy(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_replace_transaction(self, eth_tester, w3, keyfile_account_address):
        super().test_eth_replace_transaction(w3, keyfile_account_address)

    @disable_auto_mine
    @pytest.mark.xfail(
        reason="py-evm does not raise on EIP-1559 transaction underpriced"
    )
    # TODO: This might also be an issue in py-evm worth looking into. See reason above.
    def test_eth_replace_transaction_underpriced(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_replace_transaction_underpriced(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_replace_transaction_incorrect_nonce(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_replace_transaction_incorrect_nonce(
            w3, keyfile_account_address
        )

    @disable_auto_mine
    def test_eth_replace_transaction_gas_price_too_low(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_replace_transaction_gas_price_too_low(
            w3, keyfile_account_address
        )

    @disable_auto_mine
    def test_eth_replace_transaction_gas_price_defaulting_minimum(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_replace_transaction_gas_price_defaulting_minimum(
            w3, keyfile_account_address
        )

    @disable_auto_mine
    def test_eth_replace_transaction_gas_price_defaulting_strategy_higher(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_replace_transaction_gas_price_defaulting_strategy_higher(
            w3, keyfile_account_address
        )

    @disable_auto_mine
    def test_eth_replace_transaction_gas_price_defaulting_strategy_lower(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_replace_transaction_gas_price_defaulting_strategy_lower(
            w3, keyfile_account_address
        )

    @disable_auto_mine
    def test_eth_modify_transaction_legacy(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_modify_transaction_legacy(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_modify_transaction(self, eth_tester, w3, keyfile_account_address):
        super().test_eth_modify_transaction(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_get_logs_without_logs(
        self, eth_tester, w3: "Web3", block_with_txn_with_log: BlockData
    ) -> None:
        # Note: This was the old way the test was written before geth started returning
        # an error when the `toBlock` was before the `fromBlock`

        # Test with block range
        filter_params = {
            "fromBlock": 0,
            "toBlock": block_with_txn_with_log["number"] - 1,
        }
        result = w3.eth.get_logs(filter_params)
        assert len(result) == 0

        # the range is wrong
        filter_params = {
            "fromBlock": block_with_txn_with_log["number"],
            "toBlock": block_with_txn_with_log["number"] - 1,
        }
        result = w3.eth.get_logs(filter_params)
        assert len(result) == 0

        # Test with `address`

        # filter with other address
        filter_params = {
            "fromBlock": 0,
            "address": UNKNOWN_ADDRESS,
        }
        result = w3.eth.get_logs(filter_params)
        assert len(result) == 0

        # Test with multiple `address`

        # filter with other address
        filter_params = {
            "fromBlock": 0,
            "address": [UNKNOWN_ADDRESS, UNKNOWN_ADDRESS],
        }
        result = w3.eth.get_logs(filter_params)
        assert len(result) == 0

    def test_eth_call_old_contract_state(
        self, eth_tester, w3, math_contract, keyfile_account_address
    ):
        super().test_eth_call_old_contract_state(
            w3, math_contract, keyfile_account_address
        )

    def test_eth_chain_id(self, w3):
        chain_id = w3.eth.chain_id
        assert is_integer(chain_id)
        assert chain_id == 131277322940537

    @disable_auto_mine
    def test_eth_wait_for_transaction_receipt_unmined(
        self, eth_tester, w3, keyfile_account_address_dual_type
    ):
        super().test_eth_wait_for_transaction_receipt_unmined(
            w3, keyfile_account_address_dual_type
        )

    def test_eth_call_revert_with_msg(
        self, w3, revert_contract, keyfile_account_address
    ):
        txn_params = revert_contract._prepare_transaction(
            abi_element_identifier="revertWithMessage",
            transaction={
                "from": keyfile_account_address,
                "to": revert_contract.address,
            },
        )
        with pytest.raises(
            TransactionFailed, match="execution reverted: Function has been reverted"
        ):
            w3.eth.call(txn_params)

    def test_eth_call_revert_without_msg(
        self, w3, revert_contract, keyfile_account_address
    ):
        txn_params = revert_contract._prepare_transaction(
            abi_element_identifier="revertWithoutMessage",
            transaction={
                "from": keyfile_account_address,
                "to": revert_contract.address,
            },
        )
        with pytest.raises(TransactionFailed, match="execution reverted"):
            w3.eth.call(txn_params)

    def test_eth_estimate_gas_revert_with_msg(
        self, w3, revert_contract, keyfile_account_address
    ):
        txn_params = revert_contract._prepare_transaction(
            abi_element_identifier="revertWithMessage",
            transaction={
                "from": keyfile_account_address,
                "to": revert_contract.address,
            },
        )
        with pytest.raises(
            TransactionFailed, match="execution reverted: Function has been reverted"
        ):
            w3.eth.estimate_gas(txn_params)

    def test_eth_estimate_gas_revert_without_msg(
        self, w3, revert_contract, keyfile_account_address
    ):
        with pytest.raises(TransactionFailed, match="execution reverted"):
            txn_params = revert_contract._prepare_transaction(
                abi_element_identifier="revertWithoutMessage",
                transaction={
                    "from": keyfile_account_address,
                    "to": revert_contract.address,
                },
            )
            w3.eth.estimate_gas(txn_params)

    def test_eth_call_custom_error_revert_with_msg(
        self,
        w3,
        revert_contract,
        keyfile_account_address,
    ) -> None:
        txn_params = revert_contract._prepare_transaction(
            abi_element_identifier="customErrorWithMessage",
            transaction={
                "from": keyfile_account_address,
                "to": revert_contract.address,
            },
        )
        # test that the error message matches the custom error text from the contract
        with pytest.raises(TransactionFailed, match="You are not authorized"):
            w3.eth.call(txn_params)

    def test_eth_call_custom_error_revert_without_msg(
        self, w3, revert_contract, keyfile_account_address
    ):
        txn_params = revert_contract._prepare_transaction(
            abi_element_identifier="customErrorWithoutMessage",
            transaction={
                "from": keyfile_account_address,
                "to": revert_contract.address,
            },
        )
        with pytest.raises(TransactionFailed, match="execution reverted"):
            w3.eth.call(txn_params)

    def test_eth_estimate_gas_custom_error_revert_with_msg(
        self,
        w3,
        revert_contract,
        keyfile_account_address,
    ) -> None:
        txn_params = revert_contract._prepare_transaction(
            abi_element_identifier="customErrorWithMessage",
            transaction={
                "from": keyfile_account_address,
                "to": revert_contract.address,
            },
        )
        # test that the error message matches the custom error text from the contract
        with pytest.raises(TransactionFailed, match="You are not authorized"):
            w3.eth.estimate_gas(txn_params)

    def test_eth_estimate_gas_custom_error_revert_without_msg(
        self,
        w3,
        revert_contract,
        keyfile_account_address,
    ) -> None:
        txn_params = revert_contract._prepare_transaction(
            abi_element_identifier="customErrorWithoutMessage",
            transaction={
                "from": keyfile_account_address,
                "to": revert_contract.address,
            },
        )
        with pytest.raises(TransactionFailed, match="execution reverted"):
            w3.eth.estimate_gas(txn_params)

    @disable_auto_mine
    def test_eth_send_transaction(self, eth_tester, w3, keyfile_account_address):
        super().test_eth_send_transaction(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_send_transaction_legacy(self, eth_tester, w3, keyfile_account_address):
        super().test_eth_send_transaction_legacy(w3, keyfile_account_address)

    def test_eth_send_raw_transaction(self, eth_tester, w3, keyfile_account_pkey):
        super().test_eth_send_raw_transaction(w3, keyfile_account_pkey)

    @disable_auto_mine
    @pytest.mark.parametrize(
        "max_fee", (1000000000, None), ids=["with_max_fee", "without_max_fee"]
    )
    def test_gas_price_from_strategy_bypassed_for_dynamic_fee_txn(
        self,
        eth_tester,
        w3,
        keyfile_account_address,
        max_fee,
    ):
        super().test_gas_price_from_strategy_bypassed_for_dynamic_fee_txn(
            w3, keyfile_account_address, max_fee
        )

    @disable_auto_mine
    def test_gas_price_from_strategy_bypassed_for_dynamic_fee_txn_no_tip(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_gas_price_from_strategy_bypassed_for_dynamic_fee_txn_no_tip(
            w3,
            keyfile_account_address,
        )

    @disable_auto_mine
    def test_eth_send_transaction_default_fees(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_send_transaction_default_fees(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_send_transaction_hex_fees(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_send_transaction_hex_fees(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_send_transaction_no_gas(self, eth_tester, w3, keyfile_account_address):
        super().test_eth_send_transaction_no_gas(w3, keyfile_account_address)

    @disable_auto_mine
    def test_eth_send_transaction_no_max_fee(
        self, eth_tester, w3, keyfile_account_address
    ):
        super().test_eth_send_transaction_no_max_fee(w3, keyfile_account_address)

    def test_eth_fee_history_with_integer(
        self, w3: "Web3", empty_block: BlockData
    ) -> None:
        super().test_eth_fee_history_with_integer(w3, empty_block)

    def test_eth_get_balance_with_block_identifier(self, w3: "Web3") -> None:
        w3.testing.mine()
        miner_address = w3.eth.get_block(1)["miner"]
        genesis_balance = w3.eth.get_balance(miner_address, 0)
        later_balance = w3.eth.get_balance(miner_address, 1)

        assert is_integer(genesis_balance)
        assert is_integer(later_balance)
        assert later_balance > genesis_balance


class TestEthereumTesterNetModule(NetModuleTest):
    pass
