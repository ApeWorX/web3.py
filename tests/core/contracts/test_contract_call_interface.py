import pytest
from decimal import (
    Decimal,
    getcontext,
)
import json
import re

from eth_tester.exceptions import (
    TransactionFailed,
)
from eth_utils import (
    is_address,
)
from hexbytes import (
    HexBytes,
)
import pytest_asyncio

from tests.core.contracts.utils import (
    async_deploy,
    deploy,
)
from web3._utils.abi import (
    recursive_dict_to_namedtuple,
)
from web3._utils.contract_sources.contract_data.bytes_contracts import (
    BYTES32_CONTRACT_DATA,
    BYTES_CONTRACT_DATA,
)
from web3._utils.ens import (
    contract_ens_addresses,
)
from web3.contract.async_contract import (
    AsyncContractFunction,
)
from web3.contract.contract import (
    ContractFunction,
)
from web3.exceptions import (
    ABIReceiveNotFound,
    BadFunctionCallOutput,
    BlockNumberOutOfRange,
    InvalidAddress,
    MismatchedABI,
    NameNotFound,
    NoABIFound,
    NoABIFunctionsFound,
    Web3ValidationError,
)

MULTIPLE_FUNCTIONS = json.loads(
    '[{"constant":false,"inputs":[],"name":"a","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"","type":"bytes32"}],"name":"a","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"","type":"uint256"}],"name":"a","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"","type":"uint8"}],"name":"a","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"","type":"int8"}],"name":"a","outputs":[],"type":"function"}]'  # noqa: E501
)


@pytest.fixture(params=[b"\x04\x06", "0x0406"])
def bytes_contract(w3, request, address_conversion_func):
    bytes_contract_factory = w3.eth.contract(**BYTES_CONTRACT_DATA)
    return deploy(
        w3,
        bytes_contract_factory,
        address_conversion_func,
        args=[request.param],
    )


@pytest.fixture(params=[b"\x04\x06", "0x0406"])
def non_strict_bytes_contract(
    w3_non_strict_abi,
    request,
    address_conversion_func,
):
    non_strict_bytes_contract_factory = w3_non_strict_abi.eth.contract(
        **BYTES_CONTRACT_DATA
    )
    return deploy(
        w3_non_strict_abi,
        non_strict_bytes_contract_factory,
        address_conversion_func,
        args=[request.param],
    )


@pytest.fixture
def call_transaction():
    return {
        "data": "0x61bc221a",
        "to": "0xc305c901078781C232A2a521C2aF7980f8385ee9",
    }


@pytest.fixture
def bytes32_contract_factory(w3):
    return w3.eth.contract(**BYTES32_CONTRACT_DATA)


@pytest.fixture(
    params=[
        "0x0406040604060406040604060406040604060406040604060406040604060406",
        HexBytes("0406040604060406040604060406040604060406040604060406040604060406"),
    ]
)
def bytes32_contract(w3, bytes32_contract_factory, request, address_conversion_func):
    return deploy(
        w3,
        bytes32_contract_factory,
        address_conversion_func,
        args=[request.param],
    )


@pytest.fixture
def undeployed_math_contract(math_contract_factory, address_conversion_func):
    empty_address = address_conversion_func(
        "0x000000000000000000000000000000000000dEaD"
    )
    _undeployed_math_contract = math_contract_factory(address=empty_address)
    return _undeployed_math_contract


@pytest.fixture
def mismatched_math_contract(
    w3, string_contract_factory, math_contract_factory, address_conversion_func
):
    deploy_txn = string_contract_factory.constructor("Caqalai").transact()
    deploy_receipt = w3.eth.wait_for_transaction_receipt(deploy_txn)
    assert deploy_receipt is not None
    address = address_conversion_func(deploy_receipt["contractAddress"])
    _mismatched_math_contract = math_contract_factory(address=address)
    return _mismatched_math_contract


def test_deploy_raises_due_to_strict_byte_checking_by_default(
    w3, bytes32_contract_factory, address_conversion_func
):
    with pytest.raises(TypeError):
        deploy(
            w3,
            bytes32_contract_factory,
            address_conversion_func,
            args=["0406040604060406040604060406040604060406040604060406040604060406"],
        )


def test_invalid_address_in_deploy_arg(
    contract_with_constructor_address_factory,
):
    with pytest.raises(InvalidAddress):
        contract_with_constructor_address_factory.constructor(
            "0xd3cda913deb6f67967b99d67acdfa1712c293601",
        ).transact()


def test_call_with_no_arguments(math_contract, call):
    result = call(contract=math_contract, contract_function="return13")
    assert result == 13


def test_call_no_arguments_no_parens(math_contract):
    assert math_contract.functions.return13.call() == 13


def test_call_with_one_argument(math_contract, call):
    result = call(contract=math_contract, contract_function="multiply7", func_args=[3])
    assert result == 21


@pytest.mark.parametrize(
    "call_args,call_kwargs",
    (
        ((9, 7), {}),
        ((9,), {"b": 7}),
        (tuple(), {"a": 9, "b": 7}),
    ),
)
def test_call_with_multiple_arguments(math_contract, call, call_args, call_kwargs):
    result = call(
        contract=math_contract,
        contract_function="add",
        func_args=call_args,
        func_kwargs=call_kwargs,
    )
    assert result == 16


@pytest.mark.parametrize(
    "call_args,call_kwargs",
    (
        ((9, 7), {}),
        ((9,), {"b": 7}),
        (tuple(), {"a": 9, "b": 7}),
    ),
)
def test_saved_method_call_with_multiple_arguments(
    math_contract, call_args, call_kwargs
):
    math_contract_add = math_contract.functions.add(*call_args, **call_kwargs)
    result = math_contract_add.call()
    assert result == 16


def test_call_get_w3_value(function_name_tester_contract, call):
    result = call(contract=function_name_tester_contract, contract_function="w3")
    assert result is True


def test_call_get_string_value(string_contract, call):
    result = call(contract=string_contract, contract_function="getValue")
    # eth_abi.decode() does not assume implicit utf-8
    # encoding of string return values. Thus, we need to decode
    # ourselves for fair comparison.
    assert result == "Caqalai"


def test_call_get_bytes32_array(arrays_contract, call):
    result = call(contract=arrays_contract, contract_function="getBytes32Value")
    # expected_bytes32_array = [keccak('0'), keccak('1')]
    expected_bytes32_array = [
        b"\x04HR\xb2\xa6p\xad\xe5@~x\xfb(c\xc5\x1d\xe9\xfc\xb9eB\xa0q\x86\xfe:\xed\xa6\xbb\x8a\x11m",  # noqa: E501
        b"\xc8\x9e\xfd\xaaT\xc0\xf2\x0cz\xdfa(\x82\xdf\tP\xf5\xa9Qc~\x03\x07\xcd\xcbLg/)\x8b\x8b\xc6",  # noqa: E501
    ]
    assert result == expected_bytes32_array


def test_call_get_bytes32_const_array(arrays_contract, call):
    result = call(contract=arrays_contract, contract_function="getBytes32ConstValue")
    # expected_bytes32_array = [keccak('A'), keccak('B')]
    expected_bytes32_array = [
        b"\x03x?\xac.\xfe\xd8\xfb\xc9\xadD>Y.\xe3\x0ea\xd6_G\x11@\xc1\x0c\xa1U\xe97\xb45\xb7`",  # noqa: E501
        b"\x1fg[\xff\x07Q_]\xf9g7\x19N\xa9E\xc3lA\xe7\xb4\xfc\xef0{|\xd4\xd0\xe6\x02\xa6\x91\x11",  # noqa: E501
    ]
    assert result == expected_bytes32_array


def test_call_get_byte_array(arrays_contract, call):
    result = call(contract=arrays_contract, contract_function="getByteValue")
    expected_byte_arr = [b"\xff", b"\xff", b"\xff", b"\xff"]
    assert result == expected_byte_arr


def test_call_get_byte_array_non_strict(non_strict_arrays_contract, call):
    result = call(contract=non_strict_arrays_contract, contract_function="getByteValue")
    expected_non_strict_byte_arr = [b"\xff", b"\xff", b"\xff", b"\xff"]
    assert result == expected_non_strict_byte_arr


@pytest.mark.parametrize(
    "args,expected",
    [
        ([b"1"], [b"1"]),
        (["0xDe"], [b"\xde"]),
        (["0xDe", "0xDe"], [b"\xde", b"\xde"]),
    ],
)
def test_set_byte_array(arrays_contract, call, transact, args, expected):
    transact(
        contract=arrays_contract,
        contract_function="setByteValue",
        func_args=[args],
    )
    result = call(contract=arrays_contract, contract_function="getByteValue")

    assert result == expected


@pytest.mark.parametrize(
    "args,expected",
    [
        ([b"1"], [b"1"]),
        (["0xDe"], [b"\xde"]),
        (["0xDe", "0xDe"], [b"\xde", b"\xde"]),
    ],
)
def test_set_byte_array_non_strict(
    non_strict_arrays_contract, call, transact, args, expected
):
    transact(
        contract=non_strict_arrays_contract,
        contract_function="setByteValue",
        func_args=[args],
    )
    result = call(contract=non_strict_arrays_contract, contract_function="getByteValue")
    assert result == expected


@pytest.mark.parametrize("args", ([""], ["s"]))
def test_set_byte_array_with_invalid_args(arrays_contract, transact, args):
    with pytest.raises(
        MismatchedABI,
        match=r"Found 1 element\(s\) named `setByteValue` that accept 1 argument\(s\).\n",  # noqa: E501
    ):
        transact(
            contract=arrays_contract,
            contract_function="setByteValue",
            func_args=[args],
        )


def test_call_get_byte_const_array_strict_by_default(arrays_contract, call):
    result = call(contract=arrays_contract, contract_function="getByteConstValue")
    expected_byte_arr = [b"\x00", b"\x01"]
    assert result == expected_byte_arr


def test_call_get_byte_const_array_non_strict(non_strict_arrays_contract, call):
    result = call(
        contract=non_strict_arrays_contract,
        contract_function="getByteConstValue",
    )
    expected_byte_arr = [b"\x00", b"\x01"]
    assert result == expected_byte_arr


def test_call_read_address_variable(contract_with_constructor_address, call):
    result = call(
        contract=contract_with_constructor_address,
        contract_function="testAddr",
    )
    assert result == "0xd3CdA913deB6f67967B99D67aCDFa1712C293601"


def test_init_with_ens_name_arg(w3, contract_with_constructor_address_factory, call):
    with contract_ens_addresses(
        contract_with_constructor_address_factory,
        [("arg-name.eth", "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413")],
    ):
        address_contract = deploy(
            w3,
            contract_with_constructor_address_factory,
            args=[
                "arg-name.eth",
            ],
        )

    result = call(contract=address_contract, contract_function="testAddr")
    assert result == "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413"


def test_call_read_bytes_variable(bytes_contract, call):
    result = call(contract=bytes_contract, contract_function="constValue")
    assert result == b"\x01\x23"


def test_call_get_bytes_value_strict_by_default(bytes_contract, call):
    result = call(contract=bytes_contract, contract_function="getValue")
    assert result == b"\x04\x06"


def test_call_get_bytes_value_non_strict(non_strict_bytes_contract, call):
    result = call(contract=non_strict_bytes_contract, contract_function="getValue")
    assert result == b"\x04\x06"


def test_call_read_bytes32_variable(bytes32_contract, call):
    result = call(contract=bytes32_contract, contract_function="constValue")
    assert (
        result
        == b"\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23"  # noqa: E501
    )


def test_call_get_bytes32_value(bytes32_contract, call):
    result = call(contract=bytes32_contract, contract_function="getValue")
    assert (
        result
        == b"\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06"  # noqa: E501
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "0x" + "11" * 20,
            "0x" + "11" * 20,
        ),
        (
            "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
            InvalidAddress,
        ),
        (
            "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
        ),
    ],
)
def test_call_address_reflector_with_address(
    address_reflector_contract, value, expected, call
):
    if not isinstance(expected, str):
        with pytest.raises(expected):
            call(
                contract=address_reflector_contract,
                contract_function="reflect",
                func_args=[value],
            )
    else:
        assert (
            call(
                contract=address_reflector_contract,
                contract_function="reflect",
                func_args=[value],
            )
            == expected
        )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            ["0x" + "11" * 20, "0x" + "22" * 20],
            ["0x" + "11" * 20, "0x" + "22" * 20],
        ),
        (["0x" + "11" * 20, "0x" + "aa" * 20], InvalidAddress),
        (
            [
                "0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4",
                "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            ],
            [
                "0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4",
                "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            ],
        ),
    ],
)
def test_call_address_list_reflector_with_address(
    address_reflector_contract, value, expected, call
):
    if not isinstance(expected, list):
        with pytest.raises(expected):
            call(
                contract=address_reflector_contract,
                contract_function="reflect",
                func_args=[value],
            )
    else:
        assert (
            call(
                contract=address_reflector_contract,
                contract_function="reflect",
                func_args=[value],
            )
            == expected
        )


def test_call_address_reflector_single_name(address_reflector_contract, call):
    with contract_ens_addresses(
        address_reflector_contract,
        [
            (
                "dennisthepeasant.eth",
                "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            )
        ],
    ):
        result = call(
            contract=address_reflector_contract,
            contract_function="reflect",
            func_args=["dennisthepeasant.eth"],
        )
        assert result == "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413"


def test_call_address_reflector_name_array(address_reflector_contract, call):
    names = [
        "autonomouscollective.eth",
        "wedonthavealord.eth",
    ]
    addresses = [
        "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
        "0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4",
    ]

    with contract_ens_addresses(address_reflector_contract, zip(names, addresses)):
        result = call(
            contract=address_reflector_contract,
            contract_function="reflect",
            func_args=[names],
        )

    assert addresses == result


def test_call_rejects_invalid_ens_name(address_reflector_contract, call):
    with contract_ens_addresses(address_reflector_contract, []):
        with pytest.raises(NameNotFound):
            call(
                contract=address_reflector_contract,
                contract_function="reflect",
                func_args=["type0.eth"],
            )


def test_call_missing_function(mismatched_math_contract, call):
    # note: contract being called needs to have a fallback function
    # (StringContract in this case)
    expected_missing_function_error_message = "Could not decode contract function call"
    with pytest.raises(BadFunctionCallOutput) as exception_info:
        call(contract=mismatched_math_contract, contract_function="return13")
    assert expected_missing_function_error_message in str(exception_info.value)


def test_call_undeployed_contract(undeployed_math_contract, call):
    expected_undeployed_call_error_message = (
        "Could not transact with/call contract function"
    )
    with pytest.raises(BadFunctionCallOutput) as exception_info:
        call(contract=undeployed_math_contract, contract_function="return13")
    assert expected_undeployed_call_error_message in str(exception_info.value)


def test_call_fallback_function(fallback_function_contract):
    result = fallback_function_contract.fallback.call()
    assert result == []


@pytest.mark.parametrize(
    "tx_params,contract_name,expected",
    (
        ({"gas": 210000}, "no_receive", "fallback"),
        ({"gas": 210000, "value": 2}, "no_receive", ""),
        ({"value": 2, "gas": 210000, "data": "0x477a5c98"}, "no_receive", ""),
        ({"gas": 210000, "data": "0x477a5c98"}, "no_receive", "fallback"),
        ({"data": "0x477a5c98"}, "receive", "fallback"),
        ({"value": 2}, "receive", "receive"),
    ),
)
def test_call_receive_fallback_function(
    w3,
    tx_params,
    expected,
    call,
    receive_function_contract,
    no_receive_function_contract,
    contract_name,
):
    if contract_name == "receive":
        contract = receive_function_contract
    elif contract_name == "no_receive":
        contract = no_receive_function_contract
    else:
        raise AssertionError("contract must be either receive or no_receive")

    initial_value = call(contract=contract, contract_function="getText")
    assert initial_value == ""
    to = {"to": contract.address}
    merged = {**to, **tx_params}
    w3.eth.send_transaction(merged)
    final_value = call(contract=contract, contract_function="getText")
    assert final_value == expected


def test_call_nonexistent_receive_function(fallback_function_contract):
    with pytest.raises(ABIReceiveNotFound, match="No receive function was found"):
        fallback_function_contract.receive.call()


def test_throws_error_if_block_out_of_range(w3, math_contract):
    w3.provider.make_request(method="evm_mine", params=[20])
    with pytest.raises(BlockNumberOutOfRange):
        math_contract.functions.counter().call(block_identifier=-50)


def test_accepts_latest_block(w3, math_contract):
    w3.provider.make_request(method="evm_mine", params=[5])
    math_contract.functions.incrementCounter().transact()

    late = math_contract.functions.counter().call(block_identifier="latest")
    pend = math_contract.functions.counter().call(block_identifier="pending")

    assert late == 1
    assert pend == 1


def test_accepts_block_hash_as_identifier(w3, math_contract):
    blocks = w3.provider.make_request(method="evm_mine", params=[5])
    math_contract.functions.incrementCounter().transact()
    more_blocks = w3.provider.make_request(method="evm_mine", params=[5])

    old = math_contract.functions.counter().call(block_identifier=blocks["result"][2])
    new = math_contract.functions.counter().call(
        block_identifier=more_blocks["result"][2]
    )

    assert old == 0
    assert new == 1


def test_neg_block_indexes_from_the_end(w3, math_contract):
    w3.provider.make_request(method="evm_mine", params=[5])
    math_contract.functions.incrementCounter().transact()
    math_contract.functions.incrementCounter().transact()
    w3.provider.make_request(method="evm_mine", params=[5])

    output1 = math_contract.functions.counter().call(block_identifier=-7)
    output2 = math_contract.functions.counter().call(block_identifier=-6)

    assert output1 == 1
    assert output2 == 2


def test_returns_data_from_specified_block(w3, math_contract):
    start_num = w3.eth.get_block("latest").number
    w3.provider.make_request(method="evm_mine", params=[5])
    math_contract.functions.incrementCounter().transact()
    math_contract.functions.incrementCounter().transact()

    output1 = math_contract.functions.counter().call(block_identifier=start_num + 6)
    output2 = math_contract.functions.counter().call(block_identifier=start_num + 7)

    assert output1 == 1
    assert output2 == 2


def test_no_functions_match_identifier(arrays_contract):
    with pytest.raises(MismatchedABI):
        arrays_contract.functions.thisFunctionDoesNotExist().call()


def test_function_1_match_identifier_wrong_number_of_args(arrays_contract):
    with pytest.raises(
        MismatchedABI,
        match=re.escape(
            "\nABI Not Found!\n"
            "No element named `setBytes32Value` with 0 argument(s).\n"
            "Provided argument types: ()\n"
            "Provided keyword argument types: {}\n\n"
            "Tried to find a matching ABI element named `setBytes32Value`, but "
            "encountered the following problems:\n"
            "Signature: setBytes32Value(bytes32[]), type: function\n"
            "Expected 1 argument(s) but received 0 argument(s).\n"
        ),
    ):
        arrays_contract.functions.setBytes32Value().call()


def test_function_1_match_identifier_wrong_args_encoding(arrays_contract):
    with pytest.raises(
        MismatchedABI,
        match=re.escape(
            "\nABI Not Found!\n"
            "Found 1 element(s) named `setBytes32Value` that accept 1 argument(s).\n"
            "The provided arguments are not valid.\n"
            "Provided argument types: (str)\n"
            "Provided keyword argument types: {}\n\n"
            "Tried to find a matching ABI element named `setBytes32Value`, but "
            "encountered the following problems:\n"
            "Signature: setBytes32Value(bytes32[]), type: function\n"
            "Argument 1 value `dog` is not compatible with type `bytes32[]`.\n"
        ),
    ):
        arrays_contract.functions.setBytes32Value("dog").call()


@pytest.mark.parametrize(
    "arg1,arg2,message",
    (
        (
            100,
            "dog",
            (
                "\nABI Not Found!\n"
                "No element named `a` with 2 argument(s).\n"
                "Provided argument types: (int,str)\n"
                "Provided keyword argument types: {}\n\n"
                "Tried to find a matching ABI element named `a`, but encountered the "
                "following problems:\n"
                "Signature: a(), type: function\n"
                "Expected 0 argument(s) but received 2 argument(s).\n"
                "Signature: a(bytes32), type: function\n"
                "Expected 1 argument(s) but received 2 argument(s).\n"
                "Signature: a(uint256), type: function\n"
                "Expected 1 argument(s) but received 2 argument(s).\n"
                "Signature: a(uint8), type: function\n"
                "Expected 1 argument(s) but received 2 argument(s).\n"
                "Signature: a(int8), type: function\n"
                "Expected 1 argument(s) but received 2 argument(s).\n"
            ),
        ),
        (
            "dog",
            None,
            (
                "\nABI Not Found!\n"
                "Found multiple elements named `a` that accept 1 argument(s).\n"
                "Provided argument types: (str)\n"
                "Provided keyword argument types: {}\n\n"
                "Tried to find a matching ABI element named `a`, but encountered the "
                "following problems:\n"
                "Signature: a(bytes32), type: function\n"
                "Argument 1 value `dog` is not compatible with type `bytes32`.\n"
                "Signature: a(uint256), type: function\n"
                "Argument 1 value `dog` is not compatible with type `uint256`.\n"
                "Signature: a(uint8), type: function\n"
                "Argument 1 value `dog` is not compatible with type `uint8`.\n"
                "Signature: a(int8), type: function\n"
                "Argument 1 value `dog` is not compatible with type `int8`.\n"
                "Signature: a(), type: function\n"
                "Expected 0 argument(s) but received 1 argument(s).\n"
            ),
        ),
        (
            100,
            None,
            (
                "\nABI Not Found!\n"
                "Found multiple elements named `a` that accept 1 argument(s).\n"
                "Provided argument types: (int)\n"
                "Provided keyword argument types: {}\n\n"
                "Tried to find a matching ABI element named `a`, but encountered the "
                "following problems:\n"
                "Signature: a(bytes32), type: function\n"
                "Argument 1 value `100` is not compatible with type `bytes32`.\n"
                "Signature: a(uint256), type: function\n"
                "Argument 1 value `100` is valid.\n"
                "Signature: a(uint8), type: function\n"
                "Argument 1 value `100` is valid.\n"
                "Signature: a(int8), type: function\n"
                "Argument 1 value `100` is valid.\n"
                "Signature: a(), type: function\n"
                "Expected 0 argument(s) but received 1 argument(s).\n"
            ),
        ),
    ),
)
def test_function_multiple_error_diagnoses(w3, arg1, arg2, message):
    Contract = w3.eth.contract(abi=MULTIPLE_FUNCTIONS)
    with pytest.raises(MismatchedABI, match=re.escape(message)):
        if arg2:
            Contract.functions.a(arg1, arg2).call()
        else:
            Contract.functions.a(arg1).call()


@pytest.mark.parametrize(
    "address",
    (
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # checksummed
        b"\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee",  # noqa: E501
    ),
)
def test_function_wrong_args_for_tuple_collapses_args_in_message(
    address,
    tuple_contract,
):
    with pytest.raises(MismatchedABI) as e:
        tuple_contract.functions.method(
            (1, [2, 3], [(4, [True, [False]], [address])])
        ).call()

    # assert the user arguments are formatted as expected:
    # (int,(int,int),((int,(bool,(bool)),(address))))
    e.match(
        "\\(int,\\(int,int\\),\\(\\(int,\\(bool,\\(bool\\)\\),\\(address\\)\\)\\)\\)"
    )

    # assert the found method signature is formatted as expected:
    # 'method((uint256,uint256[],(int256,bool[2],address[])[]))'
    e.match(
        "\\(\\(uint256,uint256\\[\\],\\(int256,bool\\[2\\],address\\[\\]\\)\\[\\]\\)\\)"  # noqa: E501
    )


@pytest.mark.parametrize(
    "address",
    (
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # checksummed
        b"\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee\xee",  # noqa: E501
    ),
)
def test_function_wrong_args_for_tuple_collapses_kwargs_in_message(
    address, tuple_contract
):
    with pytest.raises(MismatchedABI) as e:
        tuple_contract.functions.method(
            a=(1, [2, 3], [(4, [True, [False]], [address])])  # noqa: E501
        ).call()

    # assert the user keyword arguments are formatted as expected:
    # {'a': '(int,(int,int),((int,(bool,(bool)),(address))))'}
    e.match(
        "{'a': '\\(int,\\(int,int\\),\\(\\(int,\\(bool,\\(bool\\)\\),\\(address\\)\\)\\)\\)'}"  # noqa: E501
    )

    # assert the found method signature is formatted as expected:
    # ['method((uint256,uint256[],(int256,bool[2],address[])[]))']
    e.match(
        "\\(\\(uint256,uint256\\[\\],\\(int256,bool\\[2\\],address\\[\\]\\)\\[\\]\\)\\)"  # noqa: E501
    )


def test_function_no_abi(w3):
    contract = w3.eth.contract()
    with pytest.raises(NoABIFound):
        contract.functions.thisFunctionDoesNotExist().call()


def test_call_abi_no_functions(w3):
    contract = w3.eth.contract(abi=[])
    with pytest.raises(NoABIFunctionsFound):
        contract.functions.thisFunctionDoesNotExist().call()


def test_call_not_sending_ether_to_nonpayable_function(payable_tester_contract, call):
    result = call(contract=payable_tester_contract, contract_function="doNoValueCall")
    assert result == []


def test_call_sending_ether_to_nonpayable_function(payable_tester_contract, call):
    with pytest.raises(Web3ValidationError):
        call(
            contract=payable_tester_contract,
            contract_function="doNoValueCall",
            tx_params={"value": 1},
        )


@pytest.mark.parametrize(
    "function, value",
    (
        # minimum positive unambiguous value (larger than fixed8x1)
        ("reflect(ufixed256x1)", Decimal("25.5")),
        # maximum value (for ufixed256x1)
        ("reflect(ufixed256x1)", Decimal(2**256 - 1) / 10),
        # maximum negative unambiguous value (less than 0 from ufixed*)
        ("reflect(fixed8x1)", Decimal("-0.1")),
        # minimum value (for fixed8x1)
        ("reflect(fixed8x1)", Decimal("-12.8")),
        # only ufixed256x80 type supports 2-80 decimals
        (
            "reflect(ufixed256x80)",
            Decimal(2**256 - 1) / 10**80,
        ),  # maximum allowed value
        (
            "reflect(ufixed256x80)",
            Decimal(1) / 10**80,
        ),  # smallest non-zero value
        # minimum value (for ufixed8x1)
        ("reflect_short_u", 0),
        # maximum value (for ufixed8x1)
        ("reflect_short_u", Decimal("25.5")),
        ("reflect(fixed8x1)", Decimal("12.1")),
        ("reflect(fixed8x1)", Decimal(0)),
        ("reflect(fixed8x1)", 0),
        ("reflect(ufixed256x80)", 0),
        ("reflect", Decimal("12.1")),
        ("reflect", Decimal(0)),
        ("reflect", 0),
        ("reflect", 0),
    ),
)
def test_reflect_fixed_value(fixed_reflector_contract, function, value):
    contract_func = fixed_reflector_contract.functions[function]
    reflected = contract_func(value).call({"gas": 420000})
    assert reflected == value


DEFAULT_DECIMALS = getcontext().prec


@pytest.mark.parametrize(
    "function, value, error",
    (
        # out of range
        (
            "reflect_short_u",
            Decimal("25.6"),
            "Argument 1 value `25.6` is not compatible with type `ufixed8x1`.",
        ),
        (
            "reflect_short_u",
            Decimal("-.1"),
            "Argument 1 value `-0.1` is not compatible with type `ufixed8x1`.",
        ),
        # too many digits for *x1, too large for 256x80
        (
            "reflect(ufixed256x80)",
            Decimal("0.01"),
            "Argument 1 value `0.01` is not compatible with type `ufixed256x80`.",
        ),
        # too many digits
        (
            "reflect_short_u",
            Decimal("0.01"),
            "Argument 1 value `0.01` is not compatible with type `ufixed8x1`.",
        ),
        (
            "reflect_short_u",
            Decimal(f"1e-{DEFAULT_DECIMALS + 1}"),
            "Argument 1 value `1E-29` is not compatible with type `ufixed8x1`.",
        ),
        (
            "reflect_short_u",
            Decimal("25.4" + "9" * DEFAULT_DECIMALS),
            "Argument 1 value `25.49999999999999999999999999999` is not compatible with type `ufixed8x1`.",  # noqa: E501
        ),
        (
            "reflect(ufixed256x80)",
            Decimal(1) / 10**81,
            "Argument 1 value `1E-81` is not compatible with type `ufixed256x80`.",
        ),
        # floats not accepted, for floating point error concerns
        (
            "reflect_short_u",
            0.1,
            "Argument 1 value `0.1` is not compatible with type `ufixed8x1`.",
        ),
    ),
)
def test_invalid_fixed_value_reflections(
    fixed_reflector_contract, function, value, error
):
    contract_func = fixed_reflector_contract.functions[function]
    with pytest.raises(MismatchedABI, match=error):
        contract_func(value).call({"gas": 420000})


@pytest.mark.parametrize(
    "method_input, expected",
    (
        (
            {
                "a": 123,
                "b": [1, 2],
                "c": [
                    {
                        "x": 234,
                        "y": [True, False],
                        "z": [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    },
                    {
                        "x": 345,
                        "y": [False, False],
                        "z": [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    },
                ],
            },
            (
                123,
                [1, 2],
                [
                    (
                        234,
                        [True, False],
                        [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    ),
                    (
                        345,
                        [False, False],
                        [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    ),
                ],
            ),
        ),
        (
            (
                123,
                [1, 2],
                [
                    (
                        234,
                        [True, False],
                        [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    ),
                    (
                        345,
                        [False, False],
                        [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    ),
                ],
            ),
            (
                123,
                [1, 2],
                [
                    (
                        234,
                        [True, False],
                        [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    ),
                    (
                        345,
                        [False, False],
                        [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    ),
                ],
            ),
        ),
    ),
)
def test_call_tuple_contract(tuple_contract, method_input, expected):
    result = tuple_contract.functions.method(method_input).call()
    assert result == expected


@pytest.mark.parametrize(
    "method_input, plain_tuple_output, type_str, namedtuple_repr",
    (
        (
            {
                "a": 123,
                "b": [1, 2],
                "c": [
                    {
                        "x": 234,
                        "y": [True, False],
                        "z": [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    },
                    {
                        "x": 345,
                        "y": [False, False],
                        "z": [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    },
                ],
            },
            (
                123,
                [1, 2],
                [
                    (
                        234,
                        [True, False],
                        [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    ),
                    (
                        345,
                        [False, False],
                        [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    ),
                ],
            ),
            "<class 'web3._utils.abi.abi_decoded_namedtuple_factory.<locals>.ABIDecodedNamedTuple'>",  # noqa: E501
            "ABIDecodedNamedTuple(a=123, b=[1, 2], c=[ABIDecodedNamedTuple(x=234, y=[True, False], z=['0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c', '0xfdF1946A9b40245224488F1a36f4A9ed4844a523', '0xfdF1946A9b40245224488F1a36f4A9ed4844a523']), ABIDecodedNamedTuple(x=345, y=[False, False], z=['0xefd1FF70c185A1C0b125939815225199079096Ee', '0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e'])])",  # noqa: E501
        ),
    ),
)
def test_call_tuple_contract_with_decode_tuples_set(
    tuple_contract_with_decode_tuples,
    method_input,
    plain_tuple_output,
    type_str,
    namedtuple_repr,
):
    result = tuple_contract_with_decode_tuples.functions.method(method_input).call()

    # check contract output matches dict_to_namedtuple output
    namedtuple_from_input = recursive_dict_to_namedtuple(method_input)
    assert result == namedtuple_from_input
    assert str(type(result)) == type_str
    assert result.__repr__() == namedtuple_repr

    # check that the namedtuple output is still a tuple
    assert result == plain_tuple_output

    # check that fields are correct
    assert result._fields == ("a", "b", "c")
    assert result.c[0]._fields == ("x", "y", "z")


@pytest.mark.parametrize(
    "method_input, expected",
    (
        (
            {
                "t": [
                    {
                        "u": [
                            {"x": 1, "y": 2},
                            {"x": 3, "y": 4},
                            {"x": 5, "y": 6},
                        ]
                    },
                    {
                        "u": [
                            {"x": 7, "y": 8},
                            {"x": 9, "y": 10},
                            {"x": 11, "y": 12},
                        ]
                    },
                ]
            },
            (
                [
                    (
                        [
                            (1, 2),
                            (3, 4),
                            (5, 6),
                        ],
                    ),
                    (
                        [
                            (7, 8),
                            (9, 10),
                            (11, 12),
                        ],
                    ),
                ],
            ),
        ),
        (
            (
                [
                    (
                        [
                            (1, 2),
                            (3, 4),
                            (5, 6),
                        ],
                    ),
                    (
                        [
                            (7, 8),
                            (9, 10),
                            (11, 12),
                        ],
                    ),
                ],
            ),
            (
                [
                    (
                        [
                            (1, 2),
                            (3, 4),
                            (5, 6),
                        ],
                    ),
                    (
                        [
                            (7, 8),
                            (9, 10),
                            (11, 12),
                        ],
                    ),
                ],
            ),
        ),
    ),
)
def test_call_nested_tuple_contract(nested_tuple_contract, method_input, expected):
    result = nested_tuple_contract.functions.method(method_input).call()
    assert result == expected


@pytest.mark.parametrize(
    "method_input, plain_tuple_output, type_str, namedtuple_repr",
    (
        (
            {
                "t": [
                    {
                        "u": [
                            {"x": 1, "y": 2},
                            {"x": 3, "y": 4},
                            {"x": 5, "y": 6},
                        ]
                    },
                    {
                        "u": [
                            {"x": 7, "y": 8},
                            {"x": 9, "y": 10},
                            {"x": 11, "y": 12},
                        ]
                    },
                ]
            },
            (
                [
                    (
                        [
                            (1, 2),
                            (3, 4),
                            (5, 6),
                        ],
                    ),
                    (
                        [
                            (7, 8),
                            (9, 10),
                            (11, 12),
                        ],
                    ),
                ],
            ),
            "<class 'web3._utils.abi.abi_decoded_namedtuple_factory.<locals>.ABIDecodedNamedTuple'>",  # noqa: E501
            "ABIDecodedNamedTuple(t=[ABIDecodedNamedTuple(u=[ABIDecodedNamedTuple(x=1, y=2), ABIDecodedNamedTuple(x=3, y=4), ABIDecodedNamedTuple(x=5, y=6)]), ABIDecodedNamedTuple(u=[ABIDecodedNamedTuple(x=7, y=8), ABIDecodedNamedTuple(x=9, y=10), ABIDecodedNamedTuple(x=11, y=12)])])",  # noqa: E501
        ),
    ),
)
def test_call_nested_tuple_contract_with_decode_tuples_set(
    nested_tuple_contract_with_decode_tuples,
    method_input,
    plain_tuple_output,
    type_str,
    namedtuple_repr,
):
    result = nested_tuple_contract_with_decode_tuples.functions.method(
        method_input
    ).call()
    # check contract output matches dict_to_namedtuple output
    namedtuple_from_input = recursive_dict_to_namedtuple(method_input)
    assert result == namedtuple_from_input
    assert str(type(result)) == type_str
    assert result.__repr__() == namedtuple_repr

    # check that the namedtuple output is still a tuple
    assert result == plain_tuple_output

    # check that fields are correct
    assert result._fields == ("t",)
    assert result.t[0]._fields == ("u",)


def test_call_revert_contract(revert_contract):
    with pytest.raises(TransactionFailed, match="Function has been reverted."):
        # eth-tester will do a gas estimation if we don't submit a gas value,
        # which does not contain the revert reason. Avoid that by giving a gas
        # value.
        revert_contract.functions.revertWithMessage().call({"gas": 100000})


def test_changing_default_block_identifier(w3, math_contract):
    assert math_contract.caller.counter() == 0
    assert w3.eth.default_block == "latest"

    math_contract.functions.incrementCounter(7).transact()
    assert math_contract.caller.counter() == 7

    assert math_contract.functions.counter().call(block_identifier=1) == 0
    w3.eth.default_block = 1
    assert math_contract.functions.counter().call(block_identifier=None) == 0
    w3.eth.default_block = 0x2
    assert math_contract.functions.counter().call(block_identifier=None) == 7


def test_functions_iterator(w3, math_contract):
    all_functions = math_contract.all_functions()
    functions_iter = math_contract.functions

    for fn, expected_fn in zip(iter(functions_iter), all_functions):
        assert isinstance(fn, ContractFunction)
        assert fn.name == expected_fn.name
        assert fn.fn_name == expected_fn.fn_name  # alias for name


# -- async -- #


@pytest.fixture
def async_bytes_contract_factory(async_w3):
    return async_w3.eth.contract(**BYTES_CONTRACT_DATA)


@pytest_asyncio.fixture(params=[b"\x04\x06", "0x0406"])
async def async_bytes_contract(
    async_w3,
    request,
    async_bytes_contract_factory,
    address_conversion_func,
):
    return await async_deploy(
        async_w3,
        async_bytes_contract_factory,
        address_conversion_func,
        args=[request.param],
    )


@pytest_asyncio.fixture(
    params=[
        "0x0406040604060406040604060406040604060406040604060406040604060406",
        HexBytes("0406040604060406040604060406040604060406040604060406040604060406"),
    ],
)
async def async_bytes32_contract(async_w3, request, address_conversion_func):
    async_bytes32_contract_factory = async_w3.eth.contract(**BYTES32_CONTRACT_DATA)
    return await async_deploy(
        async_w3,
        async_bytes32_contract_factory,
        address_conversion_func,
        args=[request.param],
    )


@pytest_asyncio.fixture
async def async_undeployed_math_contract(
    async_math_contract_factory, address_conversion_func
):
    empty_address = address_conversion_func(
        "0x000000000000000000000000000000000000dEaD"
    )
    _undeployed_math_contract = async_math_contract_factory(address=empty_address)
    return _undeployed_math_contract


@pytest_asyncio.fixture
async def async_mismatched_math_contract(
    async_w3,
    async_string_contract_factory,
    async_math_contract_factory,
    address_conversion_func,
):
    deploy_txn = await async_string_contract_factory.constructor("Caqalai").transact()
    deploy_receipt = await async_w3.eth.wait_for_transaction_receipt(deploy_txn)
    assert deploy_receipt is not None
    address = address_conversion_func(deploy_receipt["contractAddress"])
    _mismatched_math_contract = async_math_contract_factory(address=address)
    return _mismatched_math_contract


@pytest.mark.asyncio
async def test_async_deploy_raises_due_to_strict_byte_checking_by_default(
    async_w3, async_bytes_contract_factory, address_conversion_func
):
    with pytest.raises(
        TypeError,
        match="One or more arguments could not be encoded to the necessary ABI type. "
        "Expected types are: bytes",
    ):
        await async_deploy(
            async_w3,
            async_bytes_contract_factory,
            address_conversion_func,
            args=["0406"],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("args", ("0x0406", "0406", HexBytes("0406"), b"\x04\x06"))
async def test_async_deploy_with_non_strict_abi_check(
    async_w3_non_strict_abi,
    address_conversion_func,
    args,
):
    async_non_strict_bytes_contract_factory = async_w3_non_strict_abi.eth.contract(
        **BYTES_CONTRACT_DATA
    )
    deployed_contract = await async_deploy(
        async_w3_non_strict_abi,
        async_non_strict_bytes_contract_factory,
        address_conversion_func,
        args=[args],
    )
    assert deployed_contract is not None
    assert is_address(deployed_contract.address)


@pytest.mark.asyncio
async def test_async_invalid_address_in_deploy_arg(
    async_constructor_with_address_arg_contract_factory,
):
    with pytest.raises(InvalidAddress):
        await async_constructor_with_address_arg_contract_factory.constructor(
            "0xd3cda913deb6f67967b99d67acdfa1712c293601",
        ).transact()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "call_args,call_kwargs",
    (
        ((9, 7), {}),
        ((9,), {"b": 7}),
        (tuple(), {"a": 9, "b": 7}),
    ),
)
async def test_async_call_with_multiple_arguments(
    async_math_contract, async_call, call_args, call_kwargs
):
    result = await async_call(
        contract=async_math_contract,
        contract_function="add",
        func_args=call_args,
        func_kwargs=call_kwargs,
    )
    assert result == 16


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "call_args,call_kwargs",
    (
        ((9, 7), {}),
        ((9,), {"b": 7}),
        (tuple(), {"a": 9, "b": 7}),
    ),
)
async def test_async_saved_method_call_with_multiple_arguments(
    async_math_contract, call_args, call_kwargs
):
    math_contract_add = async_math_contract.functions.add(*call_args, **call_kwargs)
    result = await math_contract_add.call()
    assert result == 16


@pytest.mark.asyncio
async def test_async_call_get_w3_value(async_function_name_tester_contract, async_call):
    result = await async_call(
        contract=async_function_name_tester_contract, contract_function="w3"
    )
    assert result is True


@pytest.mark.asyncio
async def test_async_call_get_string_value(async_string_contract, async_call):
    result = await async_call(
        contract=async_string_contract, contract_function="getValue"
    )
    # eth_abi.decode() does not assume implicit utf-8
    # encoding of string return values. Thus, we need to decode
    # ourselves for fair comparison.
    assert result == "Caqalai"


@pytest.mark.asyncio
async def test_async_call_get_bytes32_array(async_arrays_contract, async_call):
    result = await async_call(
        contract=async_arrays_contract, contract_function="getBytes32Value"
    )
    # expected_bytes32_array = [keccak('0'), keccak('1')]
    expected_bytes32_array = [
        b"\x04HR\xb2\xa6p\xad\xe5@~x\xfb(c\xc5\x1d\xe9\xfc\xb9eB\xa0q\x86\xfe:\xed\xa6\xbb\x8a\x11m",  # noqa: E501
        b"\xc8\x9e\xfd\xaaT\xc0\xf2\x0cz\xdfa(\x82\xdf\tP\xf5\xa9Qc~\x03\x07\xcd\xcbLg/)\x8b\x8b\xc6",  # noqa: E501
    ]
    assert result == expected_bytes32_array


@pytest.mark.asyncio
async def test_async_call_get_bytes32_const_array(async_arrays_contract, async_call):
    result = await async_call(
        contract=async_arrays_contract,
        contract_function="getBytes32ConstValue",
    )
    # expected_bytes32_array = [keccak('A'), keccak('B')]
    expected_bytes32_array = [
        b"\x03x?\xac.\xfe\xd8\xfb\xc9\xadD>Y.\xe3\x0ea\xd6_G\x11@\xc1\x0c\xa1U\xe97\xb45\xb7`",  # noqa: E501
        b"\x1fg[\xff\x07Q_]\xf9g7\x19N\xa9E\xc3lA\xe7\xb4\xfc\xef0{|\xd4\xd0\xe6\x02\xa6\x91\x11",  # noqa: E501
    ]
    assert result == expected_bytes32_array


@pytest.mark.asyncio
async def test_async_call_get_byte_array(async_arrays_contract, async_call):
    result = await async_call(
        contract=async_arrays_contract, contract_function="getByteValue"
    )
    expected_byte_arr = [b"\xff", b"\xff", b"\xff", b"\xff"]
    assert result == expected_byte_arr


@pytest.mark.asyncio
async def test_async_call_get_byte_array_non_strict(
    async_non_strict_arrays_contract, async_call
):
    result = await async_call(
        contract=async_non_strict_arrays_contract,
        contract_function="getByteValue",
    )
    expected_non_strict_byte_arr = [b"\xff", b"\xff", b"\xff", b"\xff"]
    assert result == expected_non_strict_byte_arr


@pytest.mark.asyncio
@pytest.mark.parametrize("args,expected", [([b""], [b"\x00"]), (["0x"], [b"\x00"])])
async def test_async_set_byte_array_non_strict(
    async_non_strict_arrays_contract,
    async_call,
    async_transact,
    args,
    expected,
):
    await async_transact(
        contract=async_non_strict_arrays_contract,
        contract_function="setByteValue",
        func_args=[args],
    )
    result = await async_call(
        contract=async_non_strict_arrays_contract,
        contract_function="getByteValue",
    )

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("args,expected", [([b"1"], [b"1"]), (["0xDe"], [b"\xde"])])
async def test_async_set_byte_array_strict_by_default(
    async_arrays_contract, async_call, async_transact, args, expected
):
    await async_transact(
        contract=async_arrays_contract,
        contract_function="setByteValue",
        func_args=[args],
    )
    result = await async_call(
        contract=async_arrays_contract, contract_function="getByteValue"
    )

    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("args", ([""], ["s"]))
async def test_async_set_strict_byte_array_with_invalid_args(
    async_arrays_contract, async_transact, args
):
    with pytest.raises(MismatchedABI):
        await async_transact(
            contract=async_arrays_contract,
            contract_function="setByteValue",
            func_args=[args],
        )


@pytest.mark.asyncio
async def test_async_call_get_byte_const_array_non_strict(
    async_non_strict_arrays_contract, async_call
):
    result = await async_call(
        contract=async_non_strict_arrays_contract,
        contract_function="getByteConstValue",
    )
    expected_byte_arr = [b"\x00", b"\x01"]
    assert result == expected_byte_arr


@pytest.mark.asyncio
async def test_async_call_read_address_variable(
    async_constructor_with_address_argument_contract, async_call
):
    result = await async_call(
        contract=async_constructor_with_address_argument_contract,
        contract_function="testAddr",
    )
    assert result == "0xd3CdA913deB6f67967B99D67aCDFa1712C293601"


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_async_init_with_ens_name_arg(
    async_w3, async_constructor_with_address_arg_contract_factory, async_call
):
    with contract_ens_addresses(
        async_constructor_with_address_arg_contract_factory,
        [("arg-name.eth", "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413")],
    ):
        address_contract = await async_deploy(
            async_w3,
            async_constructor_with_address_arg_contract_factory,
            args=[
                "arg-name.eth",
            ],
        )

    result = await async_call(contract=address_contract, contract_function="testAddr")
    assert result == "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413"


@pytest.mark.asyncio
async def test_async_call_read_bytes_variable(async_bytes_contract, async_call):
    result = await async_call(
        contract=async_bytes_contract, contract_function="constValue"
    )
    assert result == b"\x01\x23"


@pytest.mark.asyncio
async def test_async_call_get_bytes_value(async_bytes_contract, async_call):
    result = await async_call(
        contract=async_bytes_contract, contract_function="getValue"
    )
    assert result == b"\x04\x06"


@pytest.mark.asyncio
async def test_async_call_read_bytes32_variable(async_bytes32_contract, async_call):
    result = await async_call(
        contract=async_bytes32_contract, contract_function="constValue"
    )
    assert (
        result
        == b"\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23\x01\x23"  # noqa: E501
    )


@pytest.mark.asyncio
async def test_async_call_get_bytes32_value(async_bytes32_contract, async_call):
    result = await async_call(
        contract=async_bytes32_contract, contract_function="getValue"
    )
    assert (
        result
        == b"\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06\x04\x06"  # noqa: E501
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "0x" + "11" * 20,
            "0x" + "11" * 20,
        ),
        (
            "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
            InvalidAddress,
        ),
        (
            "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
        ),
    ],
)
async def test_async_call_address_reflector_with_address(
    async_address_reflector_contract, value, expected, async_call
):
    if not isinstance(expected, str):
        with pytest.raises(expected):
            await async_call(
                contract=async_address_reflector_contract,
                contract_function="reflect",
                func_args=[value],
            )
    else:
        assert (
            await async_call(
                contract=async_address_reflector_contract,
                contract_function="reflect",
                func_args=[value],
            )
            == expected
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        (
            ["0x" + "11" * 20, "0x" + "22" * 20],
            ["0x" + "11" * 20, "0x" + "22" * 20],
        ),
        (["0x" + "11" * 20, "0x" + "aa" * 20], InvalidAddress),
        (
            [
                "0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4",
                "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            ],
            [
                "0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4",
                "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            ],
        ),
    ],
)
async def test_async_call_address_list_reflector_with_address(
    async_address_reflector_contract, value, expected, async_call
):
    if not isinstance(expected, list):
        with pytest.raises(expected):
            await async_call(
                contract=async_address_reflector_contract,
                contract_function="reflect",
                func_args=[value],
            )
    else:
        assert (
            await async_call(
                contract=async_address_reflector_contract,
                contract_function="reflect",
                func_args=[value],
            )
            == expected
        )


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_async_call_address_reflector_single_name(
    async_address_reflector_contract, async_call
):
    with contract_ens_addresses(
        async_address_reflector_contract,
        [
            (
                "dennisthepeasant.eth",
                "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            )
        ],
    ):
        result = await async_call(
            contract=async_address_reflector_contract,
            contract_function="reflect",
            func_args=["dennisthepeasant.eth"],
        )
        assert result == "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413"


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_async_call_address_reflector_name_array(
    async_address_reflector_contract, async_call
):
    names = [
        "autonomouscollective.eth",
        "wedonthavealord.eth",
    ]
    addresses = [
        "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
        "0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4",
    ]

    with contract_ens_addresses(
        async_address_reflector_contract, zip(names, addresses)
    ):
        result = await async_call(
            contract=async_address_reflector_contract,
            contract_function="reflect",
            func_args=[names],
        )

    assert addresses == result


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_async_call_rejects_invalid_ens_name(
    async_address_reflector_contract, async_call
):
    with contract_ens_addresses(async_address_reflector_contract, []):
        with pytest.raises(NameNotFound):
            await async_call(
                contract=async_address_reflector_contract,
                contract_function="reflect",
                func_args=["type0.eth"],
            )


@pytest.mark.asyncio
async def test_async_call_missing_function(async_mismatched_math_contract, async_call):
    # note: contract being called needs to have a fallback function
    # (StringContract in this case)
    expected_missing_function_error_message = "Could not decode contract function call"
    with pytest.raises(BadFunctionCallOutput) as exception_info:
        await async_call(
            contract=async_mismatched_math_contract,
            contract_function="return13",
        )
    assert expected_missing_function_error_message in str(exception_info.value)


@pytest.mark.asyncio
async def test_async_call_undeployed_contract(
    async_undeployed_math_contract, async_call
):
    expected_undeployed_call_error_message = (
        "Could not transact with/call contract function"
    )
    with pytest.raises(BadFunctionCallOutput) as exception_info:
        await async_call(
            contract=async_undeployed_math_contract,
            contract_function="return13",
        )
    assert expected_undeployed_call_error_message in str(exception_info.value)


@pytest.mark.asyncio
async def test_async_call_fallback_function(async_fallback_function_contract):
    result = await async_fallback_function_contract.fallback.call()
    assert result == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tx_params,contract_name,expected",
    (
        ({"gas": 210000}, "no_receive", "fallback"),
        ({"gas": 210000, "value": 2}, "no_receive", ""),
        ({"value": 2, "gas": 210000, "data": "0x477a5c98"}, "no_receive", ""),
        ({"gas": 210000, "data": "0x477a5c98"}, "no_receive", "fallback"),
        ({"data": "0x477a5c98"}, "receive", "fallback"),
        ({"value": 2}, "receive", "receive"),
    ),
)
async def test_async_call_receive_fallback_function(
    async_w3,
    tx_params,
    expected,
    async_call,
    async_receive_function_contract,
    async_no_receive_function_contract,
    contract_name,
):
    if contract_name == "receive":
        contract = async_receive_function_contract
    elif contract_name == "no_receive":
        contract = async_no_receive_function_contract
    else:
        raise AssertionError("contract must be either receive or no_receive")

    initial_value = await async_call(contract=contract, contract_function="getText")
    assert initial_value == ""
    to = {"to": contract.address}
    merged = {**to, **tx_params}
    await async_w3.eth.send_transaction(merged)
    final_value = await async_call(contract=contract, contract_function="getText")
    assert final_value == expected


@pytest.mark.asyncio
async def test_async_call_nonexistent_receive_function(
    async_fallback_function_contract,
):
    with pytest.raises(ABIReceiveNotFound, match="No receive function was found"):
        await async_fallback_function_contract.receive.call()


@pytest.mark.asyncio
async def test_async_throws_error_if_block_out_of_range(async_w3, async_math_contract):
    await async_w3.provider.make_request(method="evm_mine", params=[20])
    with pytest.raises(BlockNumberOutOfRange):
        await async_math_contract.functions.counter().call(block_identifier=-50)


@pytest.mark.asyncio
async def test_async_accepts_latest_block(async_w3, async_math_contract):
    await async_w3.provider.make_request(method="evm_mine", params=[5])
    await async_math_contract.functions.incrementCounter().transact()

    late = await async_math_contract.functions.counter().call(block_identifier="latest")
    pend = await async_math_contract.functions.counter().call(
        block_identifier="pending"
    )

    assert late == 1
    assert pend == 1


@pytest.mark.asyncio
async def test_async_accepts_block_hash_as_identifier(async_w3, async_math_contract):
    blocks = await async_w3.provider.make_request(method="evm_mine", params=[5])
    await async_math_contract.functions.incrementCounter().transact()
    more_blocks = await async_w3.provider.make_request(method="evm_mine", params=[5])

    old = await async_math_contract.functions.counter().call(
        block_identifier=blocks["result"][2]
    )
    new = await async_math_contract.functions.counter().call(
        block_identifier=more_blocks["result"][2]
    )

    assert old == 0
    assert new == 1


@pytest.mark.asyncio
async def test_async_neg_block_indexes_from_the_end(async_w3, async_math_contract):
    await async_w3.provider.make_request(method="evm_mine", params=[5])
    await async_math_contract.functions.incrementCounter().transact()
    await async_math_contract.functions.incrementCounter().transact()
    await async_w3.provider.make_request(method="evm_mine", params=[5])

    output1 = await async_math_contract.functions.counter().call(block_identifier=-7)
    output2 = await async_math_contract.functions.counter().call(block_identifier=-6)

    assert output1 == 1
    assert output2 == 2


@pytest.mark.asyncio
async def test_async_no_functions_match_identifier(async_arrays_contract):
    with pytest.raises(MismatchedABI):
        await async_arrays_contract.functions.thisFunctionDoesNotExist().call()


@pytest.mark.asyncio
async def test_async_function_1_match_identifier_wrong_number_of_args(
    async_arrays_contract,
):
    with pytest.raises(
        MismatchedABI,
        match=re.escape(
            "No element named `setBytes32Value` with 0 argument(s).\n"
            "Provided argument types: ()\n"
            "Provided keyword argument types: {}\n\n"
            "Tried to find a matching ABI element named `setBytes32Value`, but "
            "encountered the following problems:\n"
            "Signature: setBytes32Value(bytes32[]), type: function\n"
            "Expected 1 argument(s) but received 0 argument(s).\n"
        ),
    ):
        await async_arrays_contract.functions.setBytes32Value().call()


@pytest.mark.asyncio
async def test_async_function_1_match_identifier_wrong_args_encoding(
    async_arrays_contract,
):
    with pytest.raises(
        MismatchedABI,
        match=re.escape(
            "\nABI Not Found!\n"
            "Found 1 element(s) named `setBytes32Value` that accept 1 argument(s).\n"
            "The provided arguments are not valid.\n"
            "Provided argument types: (str)\n"
            "Provided keyword argument types: {}\n\n"
            "Tried to find a matching ABI element named `setBytes32Value`, but "
            "encountered the following problems:\n"
            "Signature: setBytes32Value(bytes32[]), type: function\n"
            "Argument 1 value `dog` is not compatible with type `bytes32[]`.\n"
        ),
    ):
        await async_arrays_contract.functions.setBytes32Value("dog").call()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "arg1,arg2,message",
    (
        (100, "dog", "No element named `a` with 2 argument(s)."),
        (
            "dog",
            None,
            "Found multiple elements named `a` that accept 1 argument(s).",
        ),
        (
            100,
            None,
            "Found multiple elements named `a` that accept 1 argument(s).",
        ),
    ),
)
async def test_async_function_multiple_error_diagnoses(async_w3, arg1, arg2, message):
    Contract = async_w3.eth.contract(abi=MULTIPLE_FUNCTIONS)
    with pytest.raises(MismatchedABI, match=re.escape(message)):
        if arg2:
            await Contract.functions.a(arg1, arg2).call()
        else:
            await Contract.functions.a(arg1).call()


@pytest.mark.asyncio
async def test_async_function_no_abi(async_w3):
    contract = async_w3.eth.contract()
    with pytest.raises(NoABIFound):
        await contract.functions.thisFunctionDoesNotExist().call()


@pytest.mark.asyncio
async def test_async_call_abi_no_functions(async_w3):
    contract = async_w3.eth.contract(abi=[])
    with pytest.raises(NoABIFunctionsFound):
        await contract.functions.thisFunctionDoesNotExist().call()


@pytest.mark.asyncio
async def test_async_call_not_sending_ether_to_nonpayable_function(
    async_payable_tester_contract, async_call
):
    result = await async_call(
        contract=async_payable_tester_contract,
        contract_function="doNoValueCall",
    )
    assert result == []


@pytest.mark.asyncio
async def test_async_call_sending_ether_to_nonpayable_function(
    async_payable_tester_contract, async_call
):
    with pytest.raises(Web3ValidationError):
        await async_call(
            contract=async_payable_tester_contract,
            contract_function="doNoValueCall",
            tx_params={"value": 1},
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "function, value",
    (
        # minimum positive unambiguous value (larger than fixed8x1)
        ("reflect(ufixed256x1)", Decimal("25.5")),
        # maximum value (for ufixed256x1)
        ("reflect(ufixed256x1)", Decimal(2**256 - 1) / 10),
        # maximum negative unambiguous value (less than 0 from ufixed*)
        ("reflect(fixed8x1)", Decimal("-0.1")),
        # minimum value (for fixed8x1)
        ("reflect(fixed8x1)", Decimal("-12.8")),
        # only ufixed256x80 type supports 2-80 decimals
        (
            "reflect(ufixed256x80)",
            Decimal(2**256 - 1) / 10**80,
        ),  # maximum allowed value
        (
            "reflect(ufixed256x80)",
            Decimal(1) / 10**80,
        ),  # smallest non-zero value
        # minimum value (for ufixed8x1)
        ("reflect_short_u", 0),
        # maximum value (for ufixed8x1)
        ("reflect_short_u", Decimal("25.5")),
        ("reflect(fixed8x1)", Decimal("12.1")),
        ("reflect(fixed8x1)", Decimal(0)),
        ("reflect(fixed8x1)", 0),
        ("reflect(ufixed256x80)", 0),
        ("reflect", Decimal("12.1")),
        ("reflect", Decimal(0)),
        ("reflect", 0),
        ("reflect", 0),
    ),
)
async def test_async_reflect_fixed_value(
    async_fixed_reflector_contract, function, value
):
    contract_func = async_fixed_reflector_contract.functions[function]
    reflected = await contract_func(value).call({"gas": 420000})
    assert reflected == value


DEFAULT_DECIMALS = getcontext().prec

NO_MATCHING_ARGUMENTS = "The provided arguments are not valid.\n"
MULTIPLE_MATCHING_ELEMENTS = (
    r"Found multiple elements named `.*` that accept 1 argument\(s\).\n"
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "function, value, error",
    (
        # out of range
        ("reflect_short_u", Decimal("25.6"), NO_MATCHING_ARGUMENTS),
        ("reflect_short_u", Decimal("-.1"), NO_MATCHING_ARGUMENTS),
        # too many digits for *x1, too large for 256x80
        ("reflect(ufixed256x80)", Decimal("0.01"), MULTIPLE_MATCHING_ELEMENTS),
        # too many digits
        ("reflect_short_u", Decimal("0.01"), NO_MATCHING_ARGUMENTS),
        (
            "reflect_short_u",
            Decimal(f"1e-{DEFAULT_DECIMALS + 1}"),
            NO_MATCHING_ARGUMENTS,
        ),
        (
            "reflect_short_u",
            Decimal("25.4" + "9" * DEFAULT_DECIMALS),
            NO_MATCHING_ARGUMENTS,
        ),
        (
            "reflect(ufixed256x80)",
            Decimal(1) / 10**81,
            MULTIPLE_MATCHING_ELEMENTS,
        ),
        # floats not accepted, for floating point error concerns
        ("reflect_short_u", 0.1, NO_MATCHING_ARGUMENTS),
    ),
)
async def test_async_invalid_fixed_value_reflections(
    async_fixed_reflector_contract, function, value, error
):
    contract_func = async_fixed_reflector_contract.functions[function]
    with pytest.raises(MismatchedABI, match=error):
        await contract_func(value).call({"gas": 420000})


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_input, expected",
    (
        (
            {
                "a": 123,
                "b": [1, 2],
                "c": [
                    {
                        "x": 234,
                        "y": [True, False],
                        "z": [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    },
                    {
                        "x": 345,
                        "y": [False, False],
                        "z": [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    },
                ],
            },
            (
                123,
                [1, 2],
                [
                    (
                        234,
                        [True, False],
                        [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    ),
                    (
                        345,
                        [False, False],
                        [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    ),
                ],
            ),
        ),
        (
            (
                123,
                [1, 2],
                [
                    (
                        234,
                        [True, False],
                        [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    ),
                    (
                        345,
                        [False, False],
                        [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    ),
                ],
            ),
            (
                123,
                [1, 2],
                [
                    (
                        234,
                        [True, False],
                        [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    ),
                    (
                        345,
                        [False, False],
                        [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    ),
                ],
            ),
        ),
    ),
)
async def test_async_call_tuple_contract(async_tuple_contract, method_input, expected):
    result = await async_tuple_contract.functions.method(method_input).call()
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_input, plain_tuple_output, type_str, namedtuple_repr",
    (
        (
            {
                "a": 123,
                "b": [1, 2],
                "c": [
                    {
                        "x": 234,
                        "y": [True, False],
                        "z": [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    },
                    {
                        "x": 345,
                        "y": [False, False],
                        "z": [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    },
                ],
            },
            (
                123,
                [1, 2],
                [
                    (
                        234,
                        [True, False],
                        [
                            "0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                            "0xfdF1946A9b40245224488F1a36f4A9ed4844a523",
                        ],
                    ),
                    (
                        345,
                        [False, False],
                        [
                            "0xefd1FF70c185A1C0b125939815225199079096Ee",
                            "0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e",
                        ],
                    ),
                ],
            ),
            "<class 'web3._utils.abi.abi_decoded_namedtuple_factory.<locals>.ABIDecodedNamedTuple'>",  # noqa: E501
            "ABIDecodedNamedTuple(a=123, b=[1, 2], c=[ABIDecodedNamedTuple(x=234, y=[True, False], z=['0x4AD7E79d88650B01EEA2B1f069f01EE9db343d5c', '0xfdF1946A9b40245224488F1a36f4A9ed4844a523', '0xfdF1946A9b40245224488F1a36f4A9ed4844a523']), ABIDecodedNamedTuple(x=345, y=[False, False], z=['0xefd1FF70c185A1C0b125939815225199079096Ee', '0xf35C0784794F3Cd935F5754d3a0EbcE95bEf851e'])])",  # noqa: E501
        ),
    ),
)
async def test_async_call_tuple_contract_with_decode_tuples_set(
    async_tuple_contract_with_decode_tuples,
    method_input,
    plain_tuple_output,
    type_str,
    namedtuple_repr,
):
    result = await async_tuple_contract_with_decode_tuples.functions.method(
        method_input
    ).call()

    # check contract output matches dict_to_namedtuple output
    namedtuple_from_input = recursive_dict_to_namedtuple(method_input)
    assert result == namedtuple_from_input
    assert str(type(result)) == type_str
    assert result.__repr__() == namedtuple_repr

    # check that the namedtuple output is still a tuple
    assert result == plain_tuple_output

    # check that fields are correct
    assert result._fields == ("a", "b", "c")
    assert result.c[0]._fields == ("x", "y", "z")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_input, expected",
    (
        (
            {
                "t": [
                    {
                        "u": [
                            {"x": 1, "y": 2},
                            {"x": 3, "y": 4},
                            {"x": 5, "y": 6},
                        ]
                    },
                    {
                        "u": [
                            {"x": 7, "y": 8},
                            {"x": 9, "y": 10},
                            {"x": 11, "y": 12},
                        ]
                    },
                ]
            },
            (
                [
                    (
                        [
                            (1, 2),
                            (3, 4),
                            (5, 6),
                        ],
                    ),
                    (
                        [
                            (7, 8),
                            (9, 10),
                            (11, 12),
                        ],
                    ),
                ],
            ),
        ),
        (
            (
                [
                    (
                        [
                            (1, 2),
                            (3, 4),
                            (5, 6),
                        ],
                    ),
                    (
                        [
                            (7, 8),
                            (9, 10),
                            (11, 12),
                        ],
                    ),
                ],
            ),
            (
                [
                    (
                        [
                            (1, 2),
                            (3, 4),
                            (5, 6),
                        ],
                    ),
                    (
                        [
                            (7, 8),
                            (9, 10),
                            (11, 12),
                        ],
                    ),
                ],
            ),
        ),
    ),
)
async def test_async_call_nested_tuple_contract(
    async_nested_tuple_contract, method_input, expected
):
    result = await async_nested_tuple_contract.functions.method(method_input).call()
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_input, plain_tuple_output, type_str, namedtuple_repr",
    (
        (
            {
                "t": [
                    {
                        "u": [
                            {"x": 1, "y": 2},
                            {"x": 3, "y": 4},
                            {"x": 5, "y": 6},
                        ]
                    },
                    {
                        "u": [
                            {"x": 7, "y": 8},
                            {"x": 9, "y": 10},
                            {"x": 11, "y": 12},
                        ]
                    },
                ]
            },
            (
                [
                    (
                        [
                            (1, 2),
                            (3, 4),
                            (5, 6),
                        ],
                    ),
                    (
                        [
                            (7, 8),
                            (9, 10),
                            (11, 12),
                        ],
                    ),
                ],
            ),
            "<class 'web3._utils.abi.abi_decoded_namedtuple_factory.<locals>.ABIDecodedNamedTuple'>",  # noqa: E501
            "ABIDecodedNamedTuple(t=[ABIDecodedNamedTuple(u=[ABIDecodedNamedTuple(x=1, y=2), ABIDecodedNamedTuple(x=3, y=4), ABIDecodedNamedTuple(x=5, y=6)]), ABIDecodedNamedTuple(u=[ABIDecodedNamedTuple(x=7, y=8), ABIDecodedNamedTuple(x=9, y=10), ABIDecodedNamedTuple(x=11, y=12)])])",  # noqa: E501
        ),
    ),
)
async def test_async_call_nested_tuple_contract_with_decode_tuples_set(
    async_nested_tuple_contract_with_decode_tuples,
    method_input,
    plain_tuple_output,
    type_str,
    namedtuple_repr,
):
    result = await async_nested_tuple_contract_with_decode_tuples.functions.method(
        method_input
    ).call()

    # check contract output matches dict_to_namedtuple output
    namedtuple_from_input = recursive_dict_to_namedtuple(method_input)
    assert result == namedtuple_from_input
    assert str(type(result)) == type_str
    assert result.__repr__() == namedtuple_repr

    # check that the namedtuple output is still a tuple
    assert result == plain_tuple_output

    # check that fields are correct
    assert result._fields == ("t",)
    assert result.t[0]._fields == ("u",)


@pytest.mark.asyncio
async def test_async_call_revert_contract(async_revert_contract):
    with pytest.raises(TransactionFailed, match="Function has been reverted."):
        # eth-tester will do a gas estimation if we don't submit a gas value,
        # which does not contain the revert reason. Avoid that by giving a gas
        # value.
        await async_revert_contract.functions.revertWithMessage().call({"gas": 100000})


@pytest.mark.asyncio
async def test_async_call_with_no_arguments(async_math_contract, call):
    result = await async_math_contract.functions.return13().call()
    assert result == 13


@pytest.mark.asyncio
async def test_async_call_with_no_arguments_no_parens(async_math_contract, call):
    result = await async_math_contract.functions.return13.call()
    assert result == 13


@pytest.mark.asyncio
async def test_async_call_with_one_argument(async_math_contract, call):
    result = await async_math_contract.functions.multiply7(3).call()
    assert result == 21


@pytest.mark.asyncio
async def test_async_returns_data_from_specified_block(async_w3, async_math_contract):
    start_num = await async_w3.eth.get_block("latest")
    await async_w3.provider.make_request(method="evm_mine", params=[5])
    await async_math_contract.functions.incrementCounter().transact()
    await async_math_contract.functions.incrementCounter().transact()

    output1 = await async_math_contract.functions.counter().call(
        block_identifier=start_num.number + 6
    )
    output2 = await async_math_contract.functions.counter().call(
        block_identifier=start_num.number + 7
    )

    assert output1 == 1
    assert output2 == 2


@pytest.mark.asyncio
async def test_async_changing_default_block_identifier(async_w3, async_math_contract):
    assert await async_math_contract.caller.counter() == 0
    assert async_w3.eth.default_block == "latest"

    await async_math_contract.functions.incrementCounter(7).transact()
    assert await async_math_contract.caller.counter() == 7

    assert await async_math_contract.functions.counter().call(block_identifier=1) == 0
    async_w3.eth.default_block = 1
    assert (
        await async_math_contract.functions.counter().call(block_identifier=None) == 0
    )
    async_w3.eth.default_block = 0x2
    assert (
        await async_math_contract.functions.counter().call(block_identifier=None) == 7
    )


def test_async_functions_iterator(async_w3, async_math_contract):
    all_functions = async_math_contract.all_functions()
    functions_iter = async_math_contract.functions

    for fn, expected_fn in zip(iter(functions_iter), all_functions):
        assert isinstance(fn, AsyncContractFunction)
        assert fn.name == expected_fn.name
        assert fn.fn_name == expected_fn.fn_name  # alias for name
