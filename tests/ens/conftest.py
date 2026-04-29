import pytest
import asyncio
import json

from eth_tester import (
    EthereumTester,
)
from eth_utils import (
    to_checksum_address,
)
import pytest_asyncio

from ens import (
    ENS,
    AsyncENS,
)
from ens.contract_data import (
    registrar_abi,
    registrar_bytecode,
    registrar_bytecode_runtime,
    resolver_abi,
    resolver_bytecode,
    resolver_bytecode_runtime,
    reverse_registrar_abi,
    reverse_registrar_bytecode,
    reverse_registrar_bytecode_runtime,
    reverse_resolver_abi,
    reverse_resolver_bytecode,
    reverse_resolver_bytecode_runtime,
)
from ens.exceptions import (
    ENSTypeError,
)
from tests.ens._ur_mock import (
    install_async_ur_mock,
    install_ur_mock,
)
from web3 import (
    AsyncWeb3,
    Web3,
)
from web3._utils.contract_sources.contract_data.extended_resolver import (
    EXTENDED_RESOLVER_ABI,
    EXTENDED_RESOLVER_BYTECODE,
    EXTENDED_RESOLVER_RUNTIME,
)
from web3._utils.contract_sources.contract_data.offchain_resolver import (
    OFFCHAIN_RESOLVER_ABI,
    OFFCHAIN_RESOLVER_BYTECODE,
    OFFCHAIN_RESOLVER_RUNTIME,
)
from web3._utils.contract_sources.contract_data.simple_resolver import (
    SIMPLE_RESOLVER_ABI,
    SIMPLE_RESOLVER_BYTECODE,
    SIMPLE_RESOLVER_RUNTIME,
)
from web3.contract import (
    AsyncContract,
    Contract,
)
from web3.providers.eth_tester import (
    AsyncEthereumTesterProvider,
    EthereumTesterProvider,
)


def bytes32(val):
    if isinstance(val, int):
        result = Web3.to_bytes(val)
    else:
        raise ENSTypeError(f"{val!r} could not be converted to bytes")
    if len(result) < 32:
        return result.rjust(32, b"\0")
    else:
        return result


def deploy(w3, Factory, from_address, args=None):
    args = args or []
    factory = Factory(w3)
    deploy_txn = factory.constructor(*args).transact({"from": from_address})
    deploy_receipt = w3.eth.wait_for_transaction_receipt(deploy_txn)
    assert deploy_receipt is not None
    return factory(address=deploy_receipt["contractAddress"])


def DefaultReverseResolver(w3):
    return w3.eth.contract(
        bytecode=reverse_resolver_bytecode,
        bytecode_runtime=reverse_resolver_bytecode_runtime,
        abi=reverse_resolver_abi,
        ContractFactoryClass=Contract,
    )


def ReverseRegistrar(w3):
    return w3.eth.contract(
        bytecode=reverse_registrar_bytecode,
        bytecode_runtime=reverse_registrar_bytecode_runtime,
        abi=reverse_registrar_abi,
        ContractFactoryClass=Contract,
    )


def PublicResolverFactory(w3):
    return w3.eth.contract(
        bytecode=resolver_bytecode,
        bytecode_runtime=resolver_bytecode_runtime,
        abi=resolver_abi,
        ContractFactoryClass=Contract,
    )


def SimpleResolver(w3):
    return w3.eth.contract(
        abi=SIMPLE_RESOLVER_ABI,
        bytecode=SIMPLE_RESOLVER_BYTECODE,
        bytecode_runtime=SIMPLE_RESOLVER_RUNTIME,
        ContractFactoryClass=Contract,
    )


def ExtendedResolver(w3):
    return w3.eth.contract(
        abi=EXTENDED_RESOLVER_ABI,
        bytecode=EXTENDED_RESOLVER_BYTECODE,
        bytecode_runtime=EXTENDED_RESOLVER_RUNTIME,
        ContractFactoryClass=Contract,
    )


def OffchainResolver(w3):
    return w3.eth.contract(
        abi=OFFCHAIN_RESOLVER_ABI,
        bytecode=OFFCHAIN_RESOLVER_BYTECODE,
        bytecode_runtime=OFFCHAIN_RESOLVER_RUNTIME,
        ContractFactoryClass=Contract,
    )


def ENSFactory(w3):
    return w3.eth.contract(
        bytecode="6060604052341561000f57600080fd5b60008080526020527fad3228b676f7d3cd4284a5443f17f1962b36e491b30a40b2405849e597ba5fb58054600160a060020a033316600160a060020a0319909116179055610501806100626000396000f300606060405236156100805763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416630178b8bf811461008557806302571be3146100b757806306ab5923146100cd57806314ab9038146100f457806316a25cbd146101175780631896f70a1461014a5780635b0fc9c31461016c575b600080fd5b341561009057600080fd5b61009b60043561018e565b604051600160a060020a03909116815260200160405180910390f35b34156100c257600080fd5b61009b6004356101ac565b34156100d857600080fd5b6100f2600435602435600160a060020a03604435166101c7565b005b34156100ff57600080fd5b6100f260043567ffffffffffffffff60243516610289565b341561012257600080fd5b61012d600435610355565b60405167ffffffffffffffff909116815260200160405180910390f35b341561015557600080fd5b6100f2600435600160a060020a036024351661038c565b341561017757600080fd5b6100f2600435600160a060020a0360243516610432565b600090815260208190526040902060010154600160a060020a031690565b600090815260208190526040902054600160a060020a031690565b600083815260208190526040812054849033600160a060020a039081169116146101f057600080fd5b8484604051918252602082015260409081019051908190039020915083857fce0457fe73731f824cc272376169235128c118b49d344817417c6d108d155e8285604051600160a060020a03909116815260200160405180910390a3506000908152602081905260409020805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03929092169190911790555050565b600082815260208190526040902054829033600160a060020a039081169116146102b257600080fd5b827f1d4f9bbfc9cab89d66e1a1562f2233ccbf1308cb4f63de2ead5787adddb8fa688360405167ffffffffffffffff909116815260200160405180910390a250600091825260208290526040909120600101805467ffffffffffffffff90921674010000000000000000000000000000000000000000027fffffffff0000000000000000ffffffffffffffffffffffffffffffffffffffff909216919091179055565b60009081526020819052604090206001015474010000000000000000000000000000000000000000900467ffffffffffffffff1690565b600082815260208190526040902054829033600160a060020a039081169116146103b557600080fd5b827f335721b01866dc23fbee8b6b2c7b1e14d6f05c28cd35a2c934239f94095602a083604051600160a060020a03909116815260200160405180910390a250600091825260208290526040909120600101805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03909216919091179055565b600082815260208190526040902054829033600160a060020a0390811691161461045b57600080fd5b827fd4735d920b0f87494915f556dd9b54c8f309026070caea5c737245152564d26683604051600160a060020a03909116815260200160405180910390a250600091825260208290526040909120805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a039092169190911790555600a165627a7a7230582050975b6c54a16d216b563f4c4960d6ebc5881eb1ec73c2ef1f87920a251159530029",  # noqa: E501
        bytecode_runtime="606060405236156100805763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416630178b8bf811461008557806302571be3146100b757806306ab5923146100cd57806314ab9038146100f457806316a25cbd146101175780631896f70a1461014a5780635b0fc9c31461016c575b600080fd5b341561009057600080fd5b61009b60043561018e565b604051600160a060020a03909116815260200160405180910390f35b34156100c257600080fd5b61009b6004356101ac565b34156100d857600080fd5b6100f2600435602435600160a060020a03604435166101c7565b005b34156100ff57600080fd5b6100f260043567ffffffffffffffff60243516610289565b341561012257600080fd5b61012d600435610355565b60405167ffffffffffffffff909116815260200160405180910390f35b341561015557600080fd5b6100f2600435600160a060020a036024351661038c565b341561017757600080fd5b6100f2600435600160a060020a0360243516610432565b600090815260208190526040902060010154600160a060020a031690565b600090815260208190526040902054600160a060020a031690565b600083815260208190526040812054849033600160a060020a039081169116146101f057600080fd5b8484604051918252602082015260409081019051908190039020915083857fce0457fe73731f824cc272376169235128c118b49d344817417c6d108d155e8285604051600160a060020a03909116815260200160405180910390a3506000908152602081905260409020805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03929092169190911790555050565b600082815260208190526040902054829033600160a060020a039081169116146102b257600080fd5b827f1d4f9bbfc9cab89d66e1a1562f2233ccbf1308cb4f63de2ead5787adddb8fa688360405167ffffffffffffffff909116815260200160405180910390a250600091825260208290526040909120600101805467ffffffffffffffff90921674010000000000000000000000000000000000000000027fffffffff0000000000000000ffffffffffffffffffffffffffffffffffffffff909216919091179055565b60009081526020819052604090206001015474010000000000000000000000000000000000000000900467ffffffffffffffff1690565b600082815260208190526040902054829033600160a060020a039081169116146103b557600080fd5b827f335721b01866dc23fbee8b6b2c7b1e14d6f05c28cd35a2c934239f94095602a083604051600160a060020a03909116815260200160405180910390a250600091825260208290526040909120600101805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03909216919091179055565b600082815260208190526040902054829033600160a060020a0390811691161461045b57600080fd5b827fd4735d920b0f87494915f556dd9b54c8f309026070caea5c737245152564d26683604051600160a060020a03909116815260200160405180910390a250600091825260208290526040909120805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a039092169190911790555600a165627a7a7230582050975b6c54a16d216b563f4c4960d6ebc5881eb1ec73c2ef1f87920a251159530029",  # noqa: E501
        abi=json.loads(
            '[{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"resolver","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"label","type":"bytes32"},{"name":"owner","type":"address"}],"name":"setSubnodeOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"ttl","type":"uint64"}],"name":"setTTL","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"ttl","outputs":[{"name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"resolver","type":"address"}],"name":"setResolver","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"owner","type":"address"}],"name":"setOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":true,"name":"label","type":"bytes32"},{"indexed":false,"name":"owner","type":"address"}],"name":"NewOwner","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"owner","type":"address"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"resolver","type":"address"}],"name":"NewResolver","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"ttl","type":"uint64"}],"name":"NewTTL","type":"event"}]'  # noqa: E501
        ),
        ContractFactoryClass=Contract,
    )


def ENSRegistryFactory(w3):
    return w3.eth.contract(
        bytecode=registrar_bytecode,
        bytecode_runtime=registrar_bytecode_runtime,
        abi=registrar_abi,
        ContractFactoryClass=Contract,
    )


@pytest.fixture
def ens(ens_setup, mocker):
    mocker.patch("web3.middleware.stalecheck._is_fresh", return_value=True)
    ens_setup.w3.eth.default_account = ens_setup.w3.eth.accounts[0]
    install_ur_mock(ens_setup)
    return ens_setup


# session scope for performance
@pytest.fixture(scope="session")
def ens_setup():
    w3 = Web3(EthereumTesterProvider(EthereumTester()))

    # ** Set up ENS contracts **

    # remove account that creates ENS, so test transactions don't have write access
    accounts = w3.eth.accounts
    ens_key = accounts.pop()

    # create ENS contract
    eth_labelhash = w3.keccak(text="eth")
    eth_namehash = bytes32(
        0x93CDEB708B7545DC668EB9280176169D1C33CFD8ED6F04690A0BCC88A93FC4AE
    )
    resolver_namehash = bytes32(
        0xFDD5D5DE6DD63DB72BBC2D487944BA13BF775B50A80805FE6FCABA9B0FBA88F5
    )
    reverse_tld_namehash = bytes32(
        0xA097F6721CE401E757D1223A763FEF49B8B5F90BB18567DDB86FD205DFF71D34
    )
    reverser_namehash = bytes32(
        0x91D1777781884D03A6757A803996E38DE2A42967FB37EEACA72729271025A9E2
    )
    ens_contract = deploy(w3, ENSFactory, ens_key)

    # create public resolver
    public_resolver = deploy(
        w3, PublicResolverFactory, ens_key, args=[ens_contract.address]
    )

    # set 'resolver.eth' to resolve to public resolver
    ens_contract.functions.setSubnodeOwner(b"\0" * 32, eth_labelhash, ens_key).transact(
        {"from": ens_key}
    )

    ens_contract.functions.setSubnodeOwner(
        eth_namehash, w3.keccak(text="resolver"), ens_key
    ).transact({"from": ens_key})

    ens_contract.functions.setResolver(
        resolver_namehash, public_resolver.address
    ).transact({"from": ens_key})

    public_resolver.functions.setAddr(
        resolver_namehash, public_resolver.address
    ).transact({"from": ens_key})

    # create .eth registrar
    eth_registrar = deploy(
        w3,
        ENSRegistryFactory,
        ens_key,
        args=[ens_contract.address, eth_namehash],
    )

    # set '.eth' to resolve to the registrar
    ens_contract.functions.setResolver(eth_namehash, public_resolver.address).transact(
        {"from": ens_key}
    )

    public_resolver.functions.setAddr(eth_namehash, eth_registrar.address).transact(
        {"from": ens_key}
    )

    # create reverse resolver
    reverse_resolver = deploy(
        w3, DefaultReverseResolver, ens_key, args=[ens_contract.address]
    )

    # create reverse registrar
    reverse_registrar = deploy(
        w3,
        ReverseRegistrar,
        ens_key,
        args=[ens_contract.address, reverse_resolver.address],
    )

    # set 'addr.reverse' to resolve to reverse registrar
    ens_contract.functions.setSubnodeOwner(
        b"\0" * 32, w3.keccak(text="reverse"), ens_key
    ).transact({"from": ens_key})

    ens_contract.functions.setSubnodeOwner(
        reverse_tld_namehash, w3.keccak(text="addr"), ens_key
    ).transact({"from": ens_key})

    ens_contract.functions.setResolver(
        reverser_namehash, public_resolver.address
    ).transact({"from": ens_key})

    public_resolver.functions.setAddr(
        reverser_namehash, reverse_registrar.address
    ).transact({"from": ens_key})

    # set owner of tester.eth to an account controlled by tests
    second_account = w3.eth.accounts[2]

    ens_contract.functions.setSubnodeOwner(
        eth_namehash,
        w3.keccak(text="tester"),
        # note that this does not have to be the default, only in the list
        second_account,
    ).transact({"from": ens_key})

    # --- setup simple resolver example --- #

    # create simple resolver
    simple_resolver = deploy(w3, SimpleResolver, ens_key, args=[ens_contract.address])

    # set owner of simple-resolver.eth to an account controlled by tests
    ens_contract.functions.setSubnodeOwner(
        eth_namehash, w3.keccak(text="simple-resolver"), second_account
    ).transact({"from": ens_key})

    # ns.namehash('simple-resolver.eth')
    simple_resolver_namehash = bytes32(
        0x65DB4C1C4F4AB9E6917FA7896CE546B1FE03E9341E98187E3917AFB60AA9835A
    )

    ens_contract.functions.setResolver(
        simple_resolver_namehash, simple_resolver.address
    ).transact({"from": second_account})

    # --- setup extended resolver example --- #

    # create extended resolver
    extended_resolver = deploy(
        w3, ExtendedResolver, ens_key, args=[ens_contract.address]
    )

    # set owner of extended-resolver.eth to an account controlled by tests
    ens_contract.functions.setSubnodeOwner(
        eth_namehash, w3.keccak(text="extended-resolver"), second_account
    ).transact({"from": ens_key})

    # ns.namehash('extended-resolver.eth')
    extended_resolver_namehash = bytes32(
        0xF0A378CC2AFE91730D0105E67D6BB037CC5B8B6BFEC5B5962D9B637FF6497E55
    )

    ens_contract.functions.setResolver(
        extended_resolver_namehash, extended_resolver.address
    ).transact({"from": second_account})

    # --- setup offchain resolver example --- #

    # create offchain resolver
    offchain_resolver = deploy(
        w3,
        OffchainResolver,
        ens_key,
        # use a made up url and mock the call to this endpoint in tests
        args=[
            [
                # for GET request testing
                "https://web3.py/gateway/{sender}/{data}.json",
                # for POST request testing
                "https://web3.py/gateway/{sender}.json",
            ],
            [to_checksum_address("0x4c40caf7f24a545095299972c381862469b080fb")],
        ],
    )

    # set owner of offchainexample.eth to an account controlled by tests
    ens_contract.functions.setSubnodeOwner(
        eth_namehash, w3.keccak(text="offchainexample"), second_account
    ).transact({"from": ens_key})

    # ns.namehash('offchainexample.eth')
    offchain_example_namehash = bytes32(
        0x42041B0018EDD29D7C17154B0C671ACC0502EA0B3693CAFBEADF58E6BEAAA16C
    )

    ens_contract.functions.setResolver(
        offchain_example_namehash, offchain_resolver.address
    ).transact({"from": second_account})

    # --- finish setup --- #

    # make the registrar the owner of the 'eth' name
    ens_contract.functions.setSubnodeOwner(
        b"\0" * 32, eth_labelhash, eth_registrar.address
    ).transact({"from": ens_key})

    # make the reverse registrar the owner of the 'addr.reverse' name
    ens_contract.functions.setSubnodeOwner(
        reverse_tld_namehash, w3.keccak(text="addr"), reverse_registrar.address
    ).transact({"from": ens_key})

    return ENS.from_web3(w3, ens_contract.address)


@pytest.fixture()
def TEST_ADDRESS(address_conversion_func):
    return address_conversion_func("0x000000000000000000000000000000000000dEaD")


# -- async -- #


@pytest_asyncio.fixture(scope="session")
def async_w3():
    _async_w3 = AsyncWeb3(AsyncEthereumTesterProvider())
    return _async_w3


async def async_deploy(async_w3, Factory, from_address, args=None):
    args = args or []
    factory = Factory(async_w3)
    deploy_txn = await factory.constructor(*args).transact({"from": from_address})
    deploy_receipt = await async_w3.eth.wait_for_transaction_receipt(deploy_txn)
    assert deploy_receipt is not None
    return factory(address=deploy_receipt["contractAddress"])


def async_default_reverse_resolver(async_w3):
    return async_w3.eth.contract(
        bytecode=reverse_resolver_bytecode,
        bytecode_runtime=reverse_resolver_bytecode_runtime,
        abi=reverse_resolver_abi,
        ContractFactoryClass=AsyncContract,
    )


def async_reverse_registrar(async_w3):
    return async_w3.eth.contract(
        bytecode=reverse_registrar_bytecode,
        bytecode_runtime=reverse_registrar_bytecode_runtime,
        abi=reverse_registrar_abi,
        ContractFactoryClass=AsyncContract,
    )


def async_public_resolver_factory(async_w3):
    return async_w3.eth.contract(
        bytecode=resolver_bytecode,
        bytecode_runtime=resolver_bytecode_runtime,
        abi=resolver_abi,
        ContractFactoryClass=AsyncContract,
    )


def async_simple_resolver(async_w3):
    return async_w3.eth.contract(
        abi=SIMPLE_RESOLVER_ABI,
        bytecode=SIMPLE_RESOLVER_BYTECODE,
        bytecode_runtime=SIMPLE_RESOLVER_RUNTIME,
        ContractFactoryClass=AsyncContract,
    )


def async_extended_resolver(async_w3):
    return async_w3.eth.contract(
        abi=EXTENDED_RESOLVER_ABI,
        bytecode=EXTENDED_RESOLVER_BYTECODE,
        bytecode_runtime=EXTENDED_RESOLVER_RUNTIME,
        ContractFactoryClass=AsyncContract,
    )


def async_offchain_resolver(async_w3):
    return async_w3.eth.contract(
        abi=OFFCHAIN_RESOLVER_ABI,
        bytecode=OFFCHAIN_RESOLVER_BYTECODE,
        bytecode_runtime=OFFCHAIN_RESOLVER_RUNTIME,
        ContractFactoryClass=AsyncContract,
    )


def async_ENS_factory(async_w3):
    return async_w3.eth.contract(
        bytecode="6060604052341561000f57600080fd5b60008080526020527fad3228b676f7d3cd4284a5443f17f1962b36e491b30a40b2405849e597ba5fb58054600160a060020a033316600160a060020a0319909116179055610501806100626000396000f300606060405236156100805763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416630178b8bf811461008557806302571be3146100b757806306ab5923146100cd57806314ab9038146100f457806316a25cbd146101175780631896f70a1461014a5780635b0fc9c31461016c575b600080fd5b341561009057600080fd5b61009b60043561018e565b604051600160a060020a03909116815260200160405180910390f35b34156100c257600080fd5b61009b6004356101ac565b34156100d857600080fd5b6100f2600435602435600160a060020a03604435166101c7565b005b34156100ff57600080fd5b6100f260043567ffffffffffffffff60243516610289565b341561012257600080fd5b61012d600435610355565b60405167ffffffffffffffff909116815260200160405180910390f35b341561015557600080fd5b6100f2600435600160a060020a036024351661038c565b341561017757600080fd5b6100f2600435600160a060020a0360243516610432565b600090815260208190526040902060010154600160a060020a031690565b600090815260208190526040902054600160a060020a031690565b600083815260208190526040812054849033600160a060020a039081169116146101f057600080fd5b8484604051918252602082015260409081019051908190039020915083857fce0457fe73731f824cc272376169235128c118b49d344817417c6d108d155e8285604051600160a060020a03909116815260200160405180910390a3506000908152602081905260409020805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03929092169190911790555050565b600082815260208190526040902054829033600160a060020a039081169116146102b257600080fd5b827f1d4f9bbfc9cab89d66e1a1562f2233ccbf1308cb4f63de2ead5787adddb8fa688360405167ffffffffffffffff909116815260200160405180910390a250600091825260208290526040909120600101805467ffffffffffffffff90921674010000000000000000000000000000000000000000027fffffffff0000000000000000ffffffffffffffffffffffffffffffffffffffff909216919091179055565b60009081526020819052604090206001015474010000000000000000000000000000000000000000900467ffffffffffffffff1690565b600082815260208190526040902054829033600160a060020a039081169116146103b557600080fd5b827f335721b01866dc23fbee8b6b2c7b1e14d6f05c28cd35a2c934239f94095602a083604051600160a060020a03909116815260200160405180910390a250600091825260208290526040909120600101805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03909216919091179055565b600082815260208190526040902054829033600160a060020a0390811691161461045b57600080fd5b827fd4735d920b0f87494915f556dd9b54c8f309026070caea5c737245152564d26683604051600160a060020a03909116815260200160405180910390a250600091825260208290526040909120805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a039092169190911790555600a165627a7a7230582050975b6c54a16d216b563f4c4960d6ebc5881eb1ec73c2ef1f87920a251159530029",  # noqa: E501
        bytecode_runtime="606060405236156100805763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416630178b8bf811461008557806302571be3146100b757806306ab5923146100cd57806314ab9038146100f457806316a25cbd146101175780631896f70a1461014a5780635b0fc9c31461016c575b600080fd5b341561009057600080fd5b61009b60043561018e565b604051600160a060020a03909116815260200160405180910390f35b34156100c257600080fd5b61009b6004356101ac565b34156100d857600080fd5b6100f2600435602435600160a060020a03604435166101c7565b005b34156100ff57600080fd5b6100f260043567ffffffffffffffff60243516610289565b341561012257600080fd5b61012d600435610355565b60405167ffffffffffffffff909116815260200160405180910390f35b341561015557600080fd5b6100f2600435600160a060020a036024351661038c565b341561017757600080fd5b6100f2600435600160a060020a0360243516610432565b600090815260208190526040902060010154600160a060020a031690565b600090815260208190526040902054600160a060020a031690565b600083815260208190526040812054849033600160a060020a039081169116146101f057600080fd5b8484604051918252602082015260409081019051908190039020915083857fce0457fe73731f824cc272376169235128c118b49d344817417c6d108d155e8285604051600160a060020a03909116815260200160405180910390a3506000908152602081905260409020805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03929092169190911790555050565b600082815260208190526040902054829033600160a060020a039081169116146102b257600080fd5b827f1d4f9bbfc9cab89d66e1a1562f2233ccbf1308cb4f63de2ead5787adddb8fa688360405167ffffffffffffffff909116815260200160405180910390a250600091825260208290526040909120600101805467ffffffffffffffff90921674010000000000000000000000000000000000000000027fffffffff0000000000000000ffffffffffffffffffffffffffffffffffffffff909216919091179055565b60009081526020819052604090206001015474010000000000000000000000000000000000000000900467ffffffffffffffff1690565b600082815260208190526040902054829033600160a060020a039081169116146103b557600080fd5b827f335721b01866dc23fbee8b6b2c7b1e14d6f05c28cd35a2c934239f94095602a083604051600160a060020a03909116815260200160405180910390a250600091825260208290526040909120600101805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03909216919091179055565b600082815260208190526040902054829033600160a060020a0390811691161461045b57600080fd5b827fd4735d920b0f87494915f556dd9b54c8f309026070caea5c737245152564d26683604051600160a060020a03909116815260200160405180910390a250600091825260208290526040909120805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a039092169190911790555600a165627a7a7230582050975b6c54a16d216b563f4c4960d6ebc5881eb1ec73c2ef1f87920a251159530029",  # noqa: E501
        abi=json.loads(
            '[{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"resolver","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"label","type":"bytes32"},{"name":"owner","type":"address"}],"name":"setSubnodeOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"ttl","type":"uint64"}],"name":"setTTL","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"ttl","outputs":[{"name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"resolver","type":"address"}],"name":"setResolver","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"owner","type":"address"}],"name":"setOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":true,"name":"label","type":"bytes32"},{"indexed":false,"name":"owner","type":"address"}],"name":"NewOwner","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"owner","type":"address"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"resolver","type":"address"}],"name":"NewResolver","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"ttl","type":"uint64"}],"name":"NewTTL","type":"event"}]'  # noqa: E501
        ),
        ContractFactoryClass=AsyncContract,
    )


def async_ENS_registry_factory(async_w3):
    return async_w3.eth.contract(
        bytecode=registrar_bytecode,
        bytecode_runtime=registrar_bytecode_runtime,
        abi=registrar_abi,
        ContractFactoryClass=AsyncContract,
    )


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# add session scope with above session-scoped `event_loop` for better performance
@pytest_asyncio.fixture(scope="session")
async def async_ens_setup(async_w3):
    # ** Set up ENS contracts **

    # remove account that creates ENS, so test transactions don't have write access
    accounts = await async_w3.eth.accounts
    ens_key = accounts.pop()
    async_w3.eth.default_account = accounts[0]

    # create ENS contract
    eth_labelhash = async_w3.keccak(text="eth")
    eth_namehash = bytes32(
        0x93CDEB708B7545DC668EB9280176169D1C33CFD8ED6F04690A0BCC88A93FC4AE
    )
    resolver_namehash = bytes32(
        0xFDD5D5DE6DD63DB72BBC2D487944BA13BF775B50A80805FE6FCABA9B0FBA88F5
    )
    reverse_tld_namehash = bytes32(
        0xA097F6721CE401E757D1223A763FEF49B8B5F90BB18567DDB86FD205DFF71D34
    )  # noqa: E501
    reverser_namehash = bytes32(
        0x91D1777781884D03A6757A803996E38DE2A42967FB37EEACA72729271025A9E2
    )
    ens_contract = await async_deploy(async_w3, async_ENS_factory, ens_key)

    # create public resolver
    public_resolver = await async_deploy(
        async_w3, async_public_resolver_factory, ens_key, args=[ens_contract.address]
    )

    # set 'resolver.eth' to resolve to public resolver
    await ens_contract.functions.setSubnodeOwner(
        b"\0" * 32, eth_labelhash, ens_key
    ).transact({"from": ens_key})

    await ens_contract.functions.setSubnodeOwner(
        eth_namehash, async_w3.keccak(text="resolver"), ens_key
    ).transact({"from": ens_key})

    await ens_contract.functions.setResolver(
        resolver_namehash, public_resolver.address
    ).transact({"from": ens_key})

    await public_resolver.functions.setAddr(
        resolver_namehash, public_resolver.address
    ).transact({"from": ens_key})

    # create .eth registrar
    eth_registrar = await async_deploy(
        async_w3,
        async_ENS_registry_factory,
        ens_key,
        args=[ens_contract.address, eth_namehash],
    )

    # set '.eth' to resolve to the registrar
    await ens_contract.functions.setResolver(
        eth_namehash, public_resolver.address
    ).transact({"from": ens_key})

    await public_resolver.functions.setAddr(
        eth_namehash, eth_registrar.address
    ).transact({"from": ens_key})

    # create reverse resolver
    reverse_resolver = await async_deploy(
        async_w3, async_default_reverse_resolver, ens_key, args=[ens_contract.address]
    )

    # create reverse registrar
    reverse_registrar = await async_deploy(
        async_w3,
        async_reverse_registrar,
        ens_key,
        args=[ens_contract.address, reverse_resolver.address],
    )

    # set 'addr.reverse' to resolve to reverse registrar
    await ens_contract.functions.setSubnodeOwner(
        b"\0" * 32, async_w3.keccak(text="reverse"), ens_key
    ).transact({"from": ens_key})

    await ens_contract.functions.setSubnodeOwner(
        reverse_tld_namehash, async_w3.keccak(text="addr"), ens_key
    ).transact({"from": ens_key})

    await ens_contract.functions.setResolver(
        reverser_namehash, public_resolver.address
    ).transact({"from": ens_key})

    await public_resolver.functions.setAddr(
        reverser_namehash, reverse_registrar.address
    ).transact({"from": ens_key})

    # set owner of tester.eth to an account controlled by tests
    second_accounts = await async_w3.eth.accounts
    second_account = second_accounts[2]

    await ens_contract.functions.setSubnodeOwner(
        eth_namehash,
        async_w3.keccak(text="tester"),
        # note that this does not have to be the default, only in the list
        second_account,
    ).transact({"from": ens_key})

    # --- setup simple resolver example --- #

    # create simple resolver
    simple_resolver = await async_deploy(
        async_w3, async_simple_resolver, ens_key, args=[ens_contract.address]
    )

    # set owner of simple-resolver.eth to an account controlled by tests
    await ens_contract.functions.setSubnodeOwner(
        eth_namehash, async_w3.keccak(text="simple-resolver"), second_account
    ).transact({"from": ens_key})

    # ns.namehash('simple-resolver.eth')
    simple_resolver_namehash = bytes32(
        0x65DB4C1C4F4AB9E6917FA7896CE546B1FE03E9341E98187E3917AFB60AA9835A
    )

    await ens_contract.functions.setResolver(
        simple_resolver_namehash, simple_resolver.address
    ).transact({"from": second_account})

    # --- setup extended resolver example --- #

    # create extended resolver
    extended_resolver = await async_deploy(
        async_w3, async_extended_resolver, ens_key, args=[ens_contract.address]
    )

    # set owner of extended-resolver.eth to an account controlled by tests
    await ens_contract.functions.setSubnodeOwner(
        eth_namehash, async_w3.keccak(text="extended-resolver"), second_account
    ).transact({"from": ens_key})

    # ns.namehash('extended-resolver.eth')
    extended_resolver_namehash = bytes32(
        0xF0A378CC2AFE91730D0105E67D6BB037CC5B8B6BFEC5B5962D9B637FF6497E55
    )

    await ens_contract.functions.setResolver(
        extended_resolver_namehash, extended_resolver.address
    ).transact({"from": second_account})

    # --- setup offchain resolver example --- #

    # create offchain resolver
    offchain_resolver = await async_deploy(
        async_w3,
        async_offchain_resolver,
        ens_key,
        # use a made up url and mock the call to this endpoint in tests
        args=[
            [
                # for GET request testing
                "https://web3.py/gateway/{sender}/{data}.json",
                # for POST request testing
                "https://web3.py/gateway/{sender}.json",
            ],
            [to_checksum_address("0x4c40caf7f24a545095299972c381862469b080fb")],
        ],
    )

    # set owner of offchainexample.eth to an account controlled by tests
    await ens_contract.functions.setSubnodeOwner(
        eth_namehash, async_w3.keccak(text="offchainexample"), second_account
    ).transact({"from": ens_key})

    # ns.namehash('offchainexample.eth')
    offchain_example_namehash = bytes32(
        0x42041B0018EDD29D7C17154B0C671ACC0502EA0B3693CAFBEADF58E6BEAAA16C
    )

    await ens_contract.functions.setResolver(
        offchain_example_namehash, offchain_resolver.address
    ).transact({"from": second_account})

    # --- finish setup --- #

    # make the registrar the owner of the 'eth' name
    await ens_contract.functions.setSubnodeOwner(
        b"\0" * 32, eth_labelhash, eth_registrar.address
    ).transact({"from": ens_key})

    # make the reverse registrar the owner of the 'addr.reverse' name
    await ens_contract.functions.setSubnodeOwner(
        reverse_tld_namehash, async_w3.keccak(text="addr"), reverse_registrar.address
    ).transact({"from": ens_key})

    return AsyncENS.from_web3(async_w3, ens_contract.address)


@pytest_asyncio.fixture
async def async_ens(async_ens_setup, mocker):
    mocker.patch("web3.middleware.stalecheck._is_fresh", return_value=True)
    accounts = await async_ens_setup.w3.eth.accounts
    async_ens_setup.w3.eth.default_account = accounts[0]
    install_async_ur_mock(async_ens_setup)
    return async_ens_setup
