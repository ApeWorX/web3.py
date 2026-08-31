# This file is used by the documentation as an example
# of how to write unit tests with web3.py
import pytest

import pytest_asyncio

from web3 import (
    AsyncWeb3,
    EthereumTesterProvider,
    Web3,
)
from web3.providers.eth_tester.main import (
    AsyncEthereumTesterProvider,
)


@pytest.fixture
def tester_provider():
    return EthereumTesterProvider()


@pytest.fixture
def eth_tester(tester_provider):
    return tester_provider.ethereum_tester


@pytest.fixture
def w3(tester_provider):
    return Web3(tester_provider)


@pytest.fixture
def foo_contract(eth_tester, w3):
    # For simplicity of this example we statically define the
    # contract code here. You might read your contracts from a
    # file, or something else to test with in your own code
    #
    # pragma solidity^0.5.3;
    #
    # contract Foo {
    #
    #     string public bar;
    #     event barred(string _bar);
    #
    #     constructor() public {
    #         bar = "hello world";
    #     }
    #
    #     function setBar(string memory _bar) public {
    #         bar = _bar;
    #         emit barred(_bar);
    #     }
    #
    # }

    deploy_address = eth_tester.get_accounts()[0]

    abi = """[{"anonymous":false,"inputs":[{"indexed":false,"name":"_bar","type":"string"}],"name":"barred","type":"event"},{"constant":false,"inputs":[{"name":"_bar","type":"string"}],"name":"setBar","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[],"name":"bar","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]"""  # noqa: E501
    # This bytecode is the output of compiling with
    # solc version:0.5.3+commit.10d17f24.Emscripten.clang
    bytecode = """608060405234801561001057600080fd5b506040805190810160405280600b81526020017f68656c6c6f20776f726c640000000000000000000000000000000000000000008152506000908051906020019061005c929190610062565b50610107565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a357805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518255916020019190600101906100b5565b5b5090506100de91906100e2565b5090565b61010491905b808211156101005760008160009055506001016100e8565b5090565b90565b6103bb806101166000396000f3fe608060405234801561001057600080fd5b5060043610610053576000357c01000000000000000000000000000000000000000000000000000000009004806397bc14aa14610058578063febb0f7e14610113575b600080fd5b6101116004803603602081101561006e57600080fd5b810190808035906020019064010000000081111561008b57600080fd5b82018360208201111561009d57600080fd5b803590602001918460018302840111640100000000831117156100bf57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610196565b005b61011b61024c565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561015b578082015181840152602081019050610140565b50505050905090810190601f1680156101885780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b80600090805190602001906101ac9291906102ea565b507f5f71ad82e16f082de5ff496b140e2fbc8621eeb37b36d59b185c3f1364bbd529816040518080602001828103825283818151815260200191508051906020019080838360005b8381101561020f5780820151818401526020810190506101f4565b50505050905090810190601f16801561023c5780820380516001836020036101000a031916815260200191505b509250505060405180910390a150565b60008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102e25780601f106102b7576101008083540402835291602001916102e2565b820191906000526020600020905b8154815290600101906020018083116102c557829003601f168201915b505050505081565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061032b57805160ff1916838001178555610359565b82800160010185558215610359579182015b8281111561035857825182559160200191906001019061033d565b5b509050610366919061036a565b5090565b61038c91905b80821115610388576000816000905550600101610370565b5090565b9056fea165627a7a72305820ae6ca683d45ee8a71bba45caee29e4815147cd308f772c853a20dfe08214dbb50029"""  # noqa: E501

    # Create our contract class.
    FooContract = w3.eth.contract(abi=abi, bytecode=bytecode)
    # issue a transaction to deploy the contract.
    tx_hash = FooContract.constructor().transact(
        {
            "from": deploy_address,
        }
    )
    # wait for the transaction to be mined
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, 180)
    # instantiate and return an instance of our contract.
    return FooContract(tx_receipt.contractAddress)


def test_initial_greeting(foo_contract):
    hw = foo_contract.caller.bar()
    assert hw == "hello world"


def test_can_update_greeting(w3, foo_contract):
    # send transaction that updates the greeting
    tx_hash = foo_contract.functions.setBar("testing contracts is easy").transact(
        {
            "from": w3.eth.accounts[1],
        }
    )
    w3.eth.wait_for_transaction_receipt(tx_hash, 180)

    # verify that the contract is now using the updated greeting
    hw = foo_contract.caller.bar()
    assert hw == "testing contracts is easy"


def test_updating_greeting_emits_event(w3, foo_contract):
    # send transaction that updates the greeting
    tx_hash = foo_contract.functions.setBar("testing contracts is easy").transact(
        {
            "from": w3.eth.accounts[1],
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, 180)

    # get all of the `barred` logs for the contract
    logs = foo_contract.events.barred.get_logs()
    assert len(logs) == 1

    # verify that the log's data matches the expected value
    event = logs[0]
    assert event.blockHash == receipt.blockHash
    assert event.args._bar == "testing contracts is easy"


def test_functions_abi_state_mutability(w3, foo_contract):
    assert foo_contract.functions.setBar.state_mutability == "nonpayable"
    assert foo_contract.functions.bar.state_mutability == "view"


def test_functions_abi_type(w3, foo_contract):
    assert foo_contract.functions.setBar.type == "function"
    assert foo_contract.functions.bar.type == "function"


def test_functions_abi_inputs(w3, foo_contract):
    assert foo_contract.functions.setBar.inputs == [{"name": "_bar", "type": "string"}]
    assert foo_contract.functions.bar.inputs == []


def test_functions_abi_outputs(w3, foo_contract):
    assert foo_contract.functions.setBar.outputs == []
    assert foo_contract.functions.bar.outputs == [{"name": "", "type": "string"}]


def test_events_abi(w3, foo_contract):
    assert foo_contract.events.barred.type == "event"
    assert foo_contract.events.barred.anonymous is False
    assert foo_contract.events.barred.inputs == [
        {"indexed": False, "name": "_bar", "type": "string"}
    ]


@pytest.fixture
def async_eth_tester():
    return AsyncEthereumTesterProvider().ethereum_tester


@pytest_asyncio.fixture()
async def async_w3():
    async_w3 = AsyncWeb3(AsyncEthereumTesterProvider())
    accounts = await async_w3.eth.accounts
    async_w3.eth.default_account = accounts[0]
    return async_w3


@pytest_asyncio.fixture()
async def async_foo_contract(async_w3):
    # For simplicity of this example we statically define the
    # contract code here. You might read your contracts from a
    # file, or something else to test with in your own code
    #
    # pragma solidity^0.5.3;
    #
    # contract Foo {
    #
    #     string public bar;
    #     event barred(string _bar);
    #
    #     constructor() public {
    #         bar = "hello world";
    #     }
    #
    #     function setBar(string memory _bar) public {
    #         bar = _bar;
    #         emit barred(_bar);
    #     }
    #
    # }

    abi = """[{"anonymous":false,"inputs":[{"indexed":false,"name":"_bar","type":"string"}],"name":"barred","type":"event"},{"constant":false,"inputs":[{"name":"_bar","type":"string"}],"name":"setBar","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[],"name":"bar","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]"""  # noqa: E501
    # This bytecode is the output of compiling with
    # solc version:0.5.3+commit.10d17f24.Emscripten.clang
    bytecode = """608060405234801561001057600080fd5b506040805190810160405280600b81526020017f68656c6c6f20776f726c640000000000000000000000000000000000000000008152506000908051906020019061005c929190610062565b50610107565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a357805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518255916020019190600101906100b5565b5b5090506100de91906100e2565b5090565b61010491905b808211156101005760008160009055506001016100e8565b5090565b90565b6103bb806101166000396000f3fe608060405234801561001057600080fd5b5060043610610053576000357c01000000000000000000000000000000000000000000000000000000009004806397bc14aa14610058578063febb0f7e14610113575b600080fd5b6101116004803603602081101561006e57600080fd5b810190808035906020019064010000000081111561008b57600080fd5b82018360208201111561009d57600080fd5b803590602001918460018302840111640100000000831117156100bf57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610196565b005b61011b61024c565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561015b578082015181840152602081019050610140565b50505050905090810190601f1680156101885780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b80600090805190602001906101ac9291906102ea565b507f5f71ad82e16f082de5ff496b140e2fbc8621eeb37b36d59b185c3f1364bbd529816040518080602001828103825283818151815260200191508051906020019080838360005b8381101561020f5780820151818401526020810190506101f4565b50505050905090810190601f16801561023c5780820380516001836020036101000a031916815260200191505b509250505060405180910390a150565b60008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102e25780601f106102b7576101008083540402835291602001916102e2565b820191906000526020600020905b8154815290600101906020018083116102c557829003601f168201915b505050505081565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061032b57805160ff1916838001178555610359565b82800160010185558215610359579182015b8281111561035857825182559160200191906001019061033d565b5b509050610366919061036a565b5090565b61038c91905b80821115610388576000816000905550600101610370565b5090565b9056fea165627a7a72305820ae6ca683d45ee8a71bba45caee29e4815147cd308f772c853a20dfe08214dbb50029"""  # noqa: E501

    # Create our contract class.
    FooContract = async_w3.eth.contract(abi=abi, bytecode=bytecode)
    # issue a transaction to deploy the contract.
    tx_hash = await FooContract.constructor().transact(
        {
            "from": async_w3.eth.default_account,
        }
    )
    # wait for the transaction to be mined
    tx_receipt = await async_w3.eth.wait_for_transaction_receipt(tx_hash, 180)
    # instantiate and return an instance of our contract.
    return FooContract(tx_receipt["contractAddress"])


@pytest.mark.asyncio
async def test_async_initial_greeting(async_foo_contract):
    hw = await async_foo_contract.caller.bar()
    assert hw == "hello world"


@pytest.mark.asyncio
async def test_async_can_update_greeting(async_w3, async_foo_contract):
    tx_hash = await async_foo_contract.functions.setBar(
        "testing contracts is easy",
    ).transact(
        {
            "from": async_w3.eth.default_account,
        }
    )
    await async_w3.eth.wait_for_transaction_receipt(tx_hash, 180)

    # verify that the contract is now using the updated greeting
    hw = await async_foo_contract.caller.bar()
    assert hw == "testing contracts is easy"


@pytest.mark.asyncio
async def test_async_updating_greeting_emits_event(async_w3, async_foo_contract):
    # send transaction that updates the greeting
    tx_hash = await async_foo_contract.functions.setBar(
        "testing contracts is easy",
    ).transact(
        {
            "from": async_w3.eth.default_account,
        }
    )
    receipt = await async_w3.eth.wait_for_transaction_receipt(tx_hash, 180)

    # get all of the `barred` logs for the contract
    logs = await async_foo_contract.events.barred.get_logs()
    assert len(logs) == 1

    # verify that the log's data matches the expected value
    event = logs[0]
    assert event.blockHash == receipt.blockHash
    assert event.args._bar == "testing contracts is easy"
