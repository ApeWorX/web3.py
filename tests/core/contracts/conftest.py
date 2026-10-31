import pytest
import functools

import pytest_asyncio

from tests.core.contracts.utils import (
    async_deploy,
    deploy,
)
from tests.utils import (
    async_partial,
)
from web3._utils.abi import (
    get_abi_element_signature,
)
from web3._utils.contract_sources.contract_data.ambiguous_function_contract import (
    AMBIGUOUS_FUNCTION_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.arrays_contract import (
    ARRAYS_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.constructor_contracts import (
    CONSTRUCTOR_WITH_ADDRESS_ARGUMENT_CONTRACT_DATA,
    CONSTRUCTOR_WITH_ARGUMENTS_CONTRACT_DATA,
    SIMPLE_CONSTRUCTOR_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.contract_caller_tester import (
    CONTRACT_CALLER_TESTER_DATA,
)
from web3._utils.contract_sources.contract_data.event_contracts import (
    AMBIGUOUS_EVENT_NAME_CONTRACT_DATA,
    EVENT_CONTRACT_DATA,
    INDEXED_EVENT_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.fallback_function_contract import (
    FALLBACK_FUNCTION_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.function_name_tester_contract import (
    FUNCTION_NAME_TESTER_CONTRACT_ABI,
    FUNCTION_NAME_TESTER_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.math_contract import (
    MATH_CONTRACT_ABI,
    MATH_CONTRACT_BYTECODE,
    MATH_CONTRACT_DATA,
    MATH_CONTRACT_RUNTIME,
)
from web3._utils.contract_sources.contract_data.payable_tester import (
    PAYABLE_TESTER_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.receive_function_contracts import (
    NO_RECEIVE_FUNCTION_CONTRACT_DATA,
    RECEIVE_FUNCTION_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.reflector_contracts import (
    ADDRESS_REFLECTOR_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.revert_contract import (
    REVERT_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.string_contract import (
    STRING_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.tuple_contracts import (
    NESTED_TUPLE_CONTRACT_DATA,
    TUPLE_CONTRACT_ABI,
    TUPLE_CONTRACT_BYTECODE,
    TUPLE_CONTRACT_DATA,
    TUPLE_CONTRACT_RUNTIME,
)
from web3.exceptions import (
    Web3ValueError,
)
from web3.utils.abi import (
    abi_to_signature,
    get_abi_element,
)

# --- function name tester contract --- #


@pytest.fixture(scope="session")
def function_name_tester_contract_abi():
    return FUNCTION_NAME_TESTER_CONTRACT_ABI


@pytest.fixture
def function_name_tester_contract(w3, address_conversion_func):
    function_name_tester_contract_factory = w3.eth.contract(
        **FUNCTION_NAME_TESTER_CONTRACT_DATA
    )
    return deploy(w3, function_name_tester_contract_factory, address_conversion_func)


# --- math contract --- #


@pytest.fixture(scope="session")
def math_contract_bytecode():
    return MATH_CONTRACT_BYTECODE


@pytest.fixture(scope="session")
def math_contract_runtime():
    return MATH_CONTRACT_RUNTIME


@pytest.fixture(scope="session")
def math_contract_abi():
    return MATH_CONTRACT_ABI


@pytest.fixture
def math_contract_factory(w3):
    return w3.eth.contract(**MATH_CONTRACT_DATA)


@pytest.fixture
def math_contract(w3, math_contract_factory, address_conversion_func):
    return deploy(w3, math_contract_factory, address_conversion_func)


# --- tuple contract --- #


@pytest.fixture(scope="session")
def tuple_contract_bytecode():
    return TUPLE_CONTRACT_BYTECODE


@pytest.fixture(scope="session")
def tuple_contract_runtime():
    return TUPLE_CONTRACT_RUNTIME


@pytest.fixture(scope="session")
def tuple_contract_abi():
    return TUPLE_CONTRACT_ABI


@pytest.fixture
def tuple_contract_factory(w3):
    return w3.eth.contract(**TUPLE_CONTRACT_DATA)


@pytest.fixture
def tuple_contract(w3, tuple_contract_factory, address_conversion_func):
    return deploy(w3, tuple_contract_factory, address_conversion_func)


# --- constructor contracts --- #


@pytest.fixture
def simple_constructor_contract_factory(w3):
    return w3.eth.contract(**SIMPLE_CONSTRUCTOR_CONTRACT_DATA)


@pytest.fixture
def contract_with_constructor_args_factory(w3):
    return w3.eth.contract(**CONSTRUCTOR_WITH_ARGUMENTS_CONTRACT_DATA)


@pytest.fixture
def non_strict_contract_with_constructor_args_factory(w3_non_strict_abi):
    return w3_non_strict_abi.eth.contract(**CONSTRUCTOR_WITH_ARGUMENTS_CONTRACT_DATA)


@pytest.fixture
def contract_with_constructor_address_factory(w3):
    return w3.eth.contract(**CONSTRUCTOR_WITH_ADDRESS_ARGUMENT_CONTRACT_DATA)


@pytest.fixture
def contract_with_constructor_address(
    w3, contract_with_constructor_address_factory, address_conversion_func
):
    return deploy(
        w3,
        contract_with_constructor_address_factory,
        address_conversion_func,
        args=["0xd3CdA913deB6f67967B99D67aCDFa1712C293601"],
    )


# --- address reflector contract --- #


@pytest.fixture
def address_reflector_contract(w3, address_conversion_func):
    address_reflector_contract_factory = w3.eth.contract(
        **ADDRESS_REFLECTOR_CONTRACT_DATA
    )
    return deploy(w3, address_reflector_contract_factory, address_conversion_func)


# --- string contract --- #


@pytest.fixture(scope="session")
def string_contract_data():
    return STRING_CONTRACT_DATA


@pytest.fixture
def string_contract_factory(w3, string_contract_data):
    return w3.eth.contract(**STRING_CONTRACT_DATA)


@pytest.fixture
def string_contract(w3, string_contract_factory, address_conversion_func):
    return deploy(
        w3, string_contract_factory, address_conversion_func, args=["Caqalai"]
    )


@pytest.fixture
def non_strict_string_contract(
    w3_non_strict_abi, string_contract_data, address_conversion_func
):
    _non_strict_string_contract_factory = w3_non_strict_abi.eth.contract(
        **string_contract_data
    )
    return deploy(
        w3_non_strict_abi,
        _non_strict_string_contract_factory,
        address_conversion_func,
        args=["Caqalai"],
    )


# --- ambiguous function contract --- #


@pytest.fixture(scope="session")
def ambiguous_function_contract_data():
    return AMBIGUOUS_FUNCTION_CONTRACT_DATA


@pytest.fixture
def ambiguous_function_contract_factory(w3):
    return w3.eth.contract(**AMBIGUOUS_FUNCTION_CONTRACT_DATA)


@pytest.fixture
def ambiguous_function_contract(
    w3, ambiguous_function_contract_factory, address_conversion_func
):
    return deploy(w3, ambiguous_function_contract_factory, address_conversion_func)


# --- emitter contract --- #


@pytest.fixture
def non_strict_emitter(
    w3_non_strict_abi,
    emitter_contract_data,
    wait_for_transaction,
    wait_for_block,
    address_conversion_func,
):
    non_strict_emitter_contract_factory = w3_non_strict_abi.eth.contract(
        **emitter_contract_data
    )
    w3 = w3_non_strict_abi

    wait_for_block(w3)
    deploy_txn_hash = non_strict_emitter_contract_factory.constructor().transact(
        {"gas": 10000000}
    )
    deploy_receipt = wait_for_transaction(w3, deploy_txn_hash)
    contract_address = address_conversion_func(deploy_receipt["contractAddress"])

    bytecode = w3.eth.get_code(contract_address)
    assert bytecode == non_strict_emitter_contract_factory.bytecode_runtime
    emitter_contract = non_strict_emitter_contract_factory(address=contract_address)
    assert emitter_contract.address == contract_address
    return emitter_contract


@pytest.fixture
def emitter(
    w3,
    emitter_contract_data,
    wait_for_transaction,
    wait_for_block,
    address_conversion_func,
):
    emitter_contract_factory = w3.eth.contract(**emitter_contract_data)

    wait_for_block(w3)
    deploy_txn_hash = emitter_contract_factory.constructor().transact({"gas": 30029121})
    deploy_receipt = wait_for_transaction(w3, deploy_txn_hash)
    contract_address = address_conversion_func(deploy_receipt["contractAddress"])

    bytecode = w3.eth.get_code(contract_address)
    assert bytecode == emitter_contract_factory.bytecode_runtime
    _emitter = emitter_contract_factory(address=contract_address)
    assert _emitter.address == contract_address
    return _emitter


# --- event contract --- #


@pytest.fixture
def event_contract(
    w3,
    wait_for_transaction,
    wait_for_block,
    address_conversion_func,
):
    wait_for_block(w3)

    event_contract_factory = w3.eth.contract(**EVENT_CONTRACT_DATA)
    deploy_txn_hash = event_contract_factory.constructor().transact({"gas": 1000000})
    deploy_receipt = wait_for_transaction(w3, deploy_txn_hash)
    contract_address = address_conversion_func(deploy_receipt["contractAddress"])

    bytecode = w3.eth.get_code(contract_address)
    assert bytecode == event_contract_factory.bytecode_runtime
    event_contract = event_contract_factory(address=contract_address)
    assert event_contract.address == contract_address
    return event_contract


@pytest.fixture
def indexed_event_contract(
    w3, wait_for_block, wait_for_transaction, address_conversion_func
):
    wait_for_block(w3)

    indexed_event_contract_factory = w3.eth.contract(**INDEXED_EVENT_CONTRACT_DATA)
    deploy_txn_hash = indexed_event_contract_factory.constructor().transact(
        {"gas": 1000000}
    )
    deploy_receipt = wait_for_transaction(w3, deploy_txn_hash)
    contract_address = address_conversion_func(deploy_receipt["contractAddress"])

    bytecode = w3.eth.get_code(contract_address)
    assert bytecode == indexed_event_contract_factory.bytecode_runtime
    indexed_event_contract = indexed_event_contract_factory(address=contract_address)
    assert indexed_event_contract.address == contract_address
    return indexed_event_contract


@pytest.fixture
def ambiguous_event_contract(
    w3, wait_for_block, wait_for_transaction, address_conversion_func
):
    wait_for_block(w3)

    ambiguous_event_contract_factory = w3.eth.contract(
        **AMBIGUOUS_EVENT_NAME_CONTRACT_DATA
    )
    deploy_txn_hash = ambiguous_event_contract_factory.constructor().transact(
        {"gas": 1000000}
    )
    deploy_receipt = wait_for_transaction(w3, deploy_txn_hash)
    contract_address = address_conversion_func(deploy_receipt["contractAddress"])

    bytecode = w3.eth.get_code(contract_address)
    assert bytecode == ambiguous_event_contract_factory.bytecode_runtime
    ambiguous_event_name_contract = ambiguous_event_contract_factory(
        address=contract_address
    )
    assert ambiguous_event_name_contract.address == contract_address
    return ambiguous_event_name_contract


# --- arrays contract --- #


# bytes_32 = [keccak('0'), keccak('1')]
BYTES32_ARRAY = [
    b"\x04HR\xb2\xa6p\xad\xe5@~x\xfb(c\xc5\x1d\xe9\xfc\xb9eB\xa0q\x86\xfe:\xed\xa6\xbb\x8a\x11m",  # noqa: E501
    b"\xc8\x9e\xfd\xaaT\xc0\xf2\x0cz\xdfa(\x82\xdf\tP\xf5\xa9Qc~\x03\x07\xcd\xcbLg/)\x8b\x8b\xc6",  # noqa: E501
]
BYTES1_ARRAY = [b"\xff", b"\xff", b"\xff", b"\xff"]


@pytest.fixture
def arrays_contract(w3, address_conversion_func):
    arrays_contract_factory = w3.eth.contract(**ARRAYS_CONTRACT_DATA)
    return deploy(
        w3,
        arrays_contract_factory,
        address_conversion_func,
        args=[BYTES32_ARRAY, BYTES1_ARRAY],
    )


@pytest.fixture
def non_strict_arrays_contract(w3_non_strict_abi, address_conversion_func):
    non_strict_arrays_contract_factory = w3_non_strict_abi.eth.contract(
        **ARRAYS_CONTRACT_DATA
    )
    return deploy(
        w3_non_strict_abi,
        non_strict_arrays_contract_factory,
        address_conversion_func,
        args=[BYTES32_ARRAY, BYTES1_ARRAY],
    )


# --- payable tester contract --- #


@pytest.fixture
def payable_tester_contract(w3, address_conversion_func):
    payable_tester_contract_factory = w3.eth.contract(**PAYABLE_TESTER_CONTRACT_DATA)
    return deploy(w3, payable_tester_contract_factory, address_conversion_func)


# --- fixed reflector contract --- #


# no matter the function selector, this will return back the 32 bytes of data supplied
FIXED_REFLECTOR_CONTRACT_BYTECODE = "0x610011566020600460003760206000f3005b61000461001103610004600039610004610011036000f3"  # noqa: E501
# reference source used to generate it:
LLL_SOURCE = "['seq', ['return', 0, ['lll', ['seq', ['calldatacopy', 0, 4, 32], ['return', 0, 32], 'stop' ], 0]]])"  # noqa: E501

FIXED_REFLECTOR_CONTRACT_ABI = [
    {
        "type": "function",
        "constant": False,
        "inputs": [{"type": "fixed8x1"}],
        "name": "reflect",
        "outputs": [{"type": "fixed8x1"}],
    },
    {
        "type": "function",
        "constant": False,
        "inputs": [{"type": "ufixed256x80"}],
        "name": "reflect",
        "outputs": [{"type": "ufixed256x80"}],
    },
    {
        "type": "function",
        "constant": False,
        "inputs": [{"type": "ufixed256x1"}],
        "name": "reflect",
        "outputs": [{"type": "ufixed256x1"}],
    },
    {
        "type": "function",
        "constant": False,
        "inputs": [{"type": "ufixed8x1"}],
        "name": "reflect_short_u",
        "outputs": [{"type": "ufixed8x1"}],
    },
]


@pytest.fixture
def fixed_reflector_contract(w3, address_conversion_func):
    fixed_reflector_contract_factory = w3.eth.contract(
        abi=FIXED_REFLECTOR_CONTRACT_ABI, bytecode=FIXED_REFLECTOR_CONTRACT_BYTECODE
    )
    return deploy(w3, fixed_reflector_contract_factory, address_conversion_func)


# --- test data and functions contracts --- #


@pytest.fixture
def fallback_function_contract(w3, address_conversion_func):
    fallback_function_contract_factory = w3.eth.contract(
        **FALLBACK_FUNCTION_CONTRACT_DATA
    )
    return deploy(w3, fallback_function_contract_factory, address_conversion_func)


@pytest.fixture
def receive_function_contract(w3, address_conversion_func):
    receive_function_contract_factory = w3.eth.contract(
        **RECEIVE_FUNCTION_CONTRACT_DATA
    )
    return deploy(w3, receive_function_contract_factory, address_conversion_func)


@pytest.fixture
def no_receive_function_contract(w3, address_conversion_func):
    no_receive_function_contract_factory = w3.eth.contract(
        **NO_RECEIVE_FUNCTION_CONTRACT_DATA
    )
    return deploy(w3, no_receive_function_contract_factory, address_conversion_func)


@pytest.fixture
def contract_caller_tester_contract(w3, address_conversion_func):
    contract_caller_tester_contract_factory = w3.eth.contract(
        **CONTRACT_CALLER_TESTER_DATA
    )
    return deploy(w3, contract_caller_tester_contract_factory, address_conversion_func)


@pytest.fixture
def revert_contract(w3, address_conversion_func):
    revert_contract_factory = w3.eth.contract(**REVERT_CONTRACT_DATA)
    return deploy(w3, revert_contract_factory, address_conversion_func)


@pytest.fixture
def nested_tuple_contract(w3, address_conversion_func):
    nested_tuple_contract_factory = w3.eth.contract(**NESTED_TUPLE_CONTRACT_DATA)
    return deploy(w3, nested_tuple_contract_factory, address_conversion_func)


TUPLE_CONTRACT_DATA_DECODE_TUPLES = {
    **TUPLE_CONTRACT_DATA,
    "decode_tuples": True,
}


NESTED_TUPLE_CONTRACT_DATA_DECODE_TUPLES = {
    **NESTED_TUPLE_CONTRACT_DATA,
    "decode_tuples": True,
}


@pytest.fixture
def tuple_contract_with_decode_tuples(w3, address_conversion_func):
    tuple_contract_factory = w3.eth.contract(**TUPLE_CONTRACT_DATA_DECODE_TUPLES)
    return deploy(w3, tuple_contract_factory, address_conversion_func)


@pytest.fixture
def nested_tuple_contract_with_decode_tuples(w3, address_conversion_func):
    nested_tuple_contract_factory = w3.eth.contract(
        **NESTED_TUPLE_CONTRACT_DATA_DECODE_TUPLES
    )
    return deploy(w3, nested_tuple_contract_factory, address_conversion_func)


@pytest.fixture
def some_address(address_conversion_func):
    return address_conversion_func("0x5B2063246F2191f18F2675ceDB8b28102e957458")


# --- invoke contract --- #


def invoke_contract(
    api_call_desig="call",
    contract=None,
    contract_function=None,
    func_args=None,
    func_kwargs=None,
    tx_params=None,
):
    function_signature = contract_function
    function_arg_count = len(func_args or ()) + len(func_kwargs or {})
    if function_arg_count == 0:
        function_signature = get_abi_element_signature(contract_function)

    if func_args is None:
        func_args = []
    if func_kwargs is None:
        func_kwargs = {}
    if tx_params is None:
        tx_params = {}
    allowable_call_desig = ["call", "transact", "estimate_gas", "build_transaction"]
    if api_call_desig not in allowable_call_desig:
        raise Web3ValueError(
            f"allowable_invoke_method must be one of: {allowable_call_desig}"
        )

    fn_abi = get_abi_element(
        contract.abi,
        function_signature,
        *func_args,
        abi_codec=contract.w3.codec,
        **func_kwargs,
    )
    function = contract.functions[abi_to_signature(fn_abi)]
    result = getattr(function(*func_args, **func_kwargs), api_call_desig)(tx_params)

    return result


@pytest.fixture
def build_transaction(request):
    return functools.partial(invoke_contract, api_call_desig="build_transaction")


@pytest.fixture
def transact(request):
    return functools.partial(invoke_contract, api_call_desig="transact")


@pytest.fixture
def call(request):
    return functools.partial(invoke_contract, api_call_desig="call")


@pytest.fixture
def estimate_gas(request):
    return functools.partial(invoke_contract, api_call_desig="estimate_gas")


# --- async --- #


@pytest.fixture
def async_math_contract_factory(async_w3):
    return async_w3.eth.contract(**MATH_CONTRACT_DATA)


@pytest_asyncio.fixture
async def async_math_contract(
    async_w3, async_math_contract_factory, address_conversion_func
):
    return await async_deploy(
        async_w3, async_math_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_function_name_tester_contract(async_w3, address_conversion_func):
    function_name_tester_contract_factory = async_w3.eth.contract(
        **FUNCTION_NAME_TESTER_CONTRACT_DATA
    )
    return await async_deploy(
        async_w3, function_name_tester_contract_factory, address_conversion_func
    )


@pytest.fixture
def async_simple_constructor_contract_factory(async_w3):
    return async_w3.eth.contract(**SIMPLE_CONSTRUCTOR_CONTRACT_DATA)


@pytest.fixture
def async_constructor_with_args_contract_factory(async_w3):
    return async_w3.eth.contract(**CONSTRUCTOR_WITH_ARGUMENTS_CONTRACT_DATA)


@pytest.fixture
def async_non_strict_constructor_with_args_contract_factory(async_w3_non_strict_abi):
    return async_w3_non_strict_abi.eth.contract(
        **CONSTRUCTOR_WITH_ARGUMENTS_CONTRACT_DATA
    )


@pytest.fixture
def async_constructor_with_address_arg_contract_factory(async_w3):
    return async_w3.eth.contract(**CONSTRUCTOR_WITH_ADDRESS_ARGUMENT_CONTRACT_DATA)


@pytest_asyncio.fixture
async def async_constructor_with_address_argument_contract(
    async_w3,
    address_conversion_func,
):
    async_constructor_with_address_arg_factory = async_w3.eth.contract(
        **CONSTRUCTOR_WITH_ADDRESS_ARGUMENT_CONTRACT_DATA
    )
    return await async_deploy(
        async_w3,
        async_constructor_with_address_arg_factory,
        address_conversion_func,
        args=["0xd3CdA913deB6f67967B99D67aCDFa1712C293601"],
    )


@pytest_asyncio.fixture
async def async_address_reflector_contract(async_w3, address_conversion_func):
    async_address_reflector_contract_factory = async_w3.eth.contract(
        **ADDRESS_REFLECTOR_CONTRACT_DATA,
    )
    return await async_deploy(
        async_w3, async_address_reflector_contract_factory, address_conversion_func
    )


@pytest.fixture
def async_string_contract_factory(async_w3):
    return async_w3.eth.contract(**STRING_CONTRACT_DATA)


@pytest_asyncio.fixture
async def async_string_contract(
    async_w3, async_string_contract_factory, address_conversion_func
):
    return await async_deploy(
        async_w3,
        async_string_contract_factory,
        address_conversion_func,
        args=["Caqalai"],
    )


@pytest_asyncio.fixture
async def async_arrays_contract(async_w3, address_conversion_func):
    async_arrays_contract_factory = async_w3.eth.contract(**ARRAYS_CONTRACT_DATA)
    return await async_deploy(
        async_w3,
        async_arrays_contract_factory,
        address_conversion_func,
        args=[BYTES32_ARRAY, BYTES1_ARRAY],
    )


@pytest_asyncio.fixture
async def async_non_strict_arrays_contract(
    async_w3_non_strict_abi, address_conversion_func
):
    async_non_strict_arrays_contract_factory = async_w3_non_strict_abi.eth.contract(
        **ARRAYS_CONTRACT_DATA,
    )
    return await async_deploy(
        async_w3_non_strict_abi,
        async_non_strict_arrays_contract_factory,
        address_conversion_func,
        args=[BYTES32_ARRAY, BYTES1_ARRAY],
    )


@pytest_asyncio.fixture
async def async_payable_tester_contract(async_w3, address_conversion_func):
    async_payable_tester_contract_factory = async_w3.eth.contract(
        **PAYABLE_TESTER_CONTRACT_DATA
    )
    return await async_deploy(
        async_w3, async_payable_tester_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_fixed_reflector_contract(async_w3, address_conversion_func):
    async_fixed_reflector_contract_factory = async_w3.eth.contract(
        abi=FIXED_REFLECTOR_CONTRACT_ABI, bytecode=FIXED_REFLECTOR_CONTRACT_BYTECODE
    )
    return await async_deploy(
        async_w3, async_fixed_reflector_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_fallback_function_contract(async_w3, address_conversion_func):
    async_fallback_function_contract_factory = async_w3.eth.contract(
        **FALLBACK_FUNCTION_CONTRACT_DATA
    )
    return await async_deploy(
        async_w3, async_fallback_function_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_no_receive_function_contract(async_w3, address_conversion_func):
    async_no_receive_function_contract_factory = async_w3.eth.contract(
        **NO_RECEIVE_FUNCTION_CONTRACT_DATA
    )
    return await async_deploy(
        async_w3, async_no_receive_function_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_receive_function_contract(async_w3, address_conversion_func):
    async_receive_function_contract_factory = async_w3.eth.contract(
        **RECEIVE_FUNCTION_CONTRACT_DATA
    )
    return await async_deploy(
        async_w3, async_receive_function_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_contract_caller_tester_contract(async_w3, address_conversion_func):
    async_contract_caller_tester_contract_factory = async_w3.eth.contract(
        **CONTRACT_CALLER_TESTER_DATA
    )
    return await async_deploy(
        async_w3,
        async_contract_caller_tester_contract_factory,
        address_conversion_func,
    )


@pytest_asyncio.fixture
async def async_revert_contract(async_w3, address_conversion_func):
    async_revert_contract_factory = async_w3.eth.contract(**REVERT_CONTRACT_DATA)
    return await async_deploy(
        async_w3, async_revert_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_tuple_contract(async_w3, address_conversion_func):
    async_tuple_contract_factory = async_w3.eth.contract(**TUPLE_CONTRACT_DATA)
    return await async_deploy(
        async_w3, async_tuple_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_nested_tuple_contract(async_w3, address_conversion_func):
    async_nested_tuple_contract_factory = async_w3.eth.contract(
        **NESTED_TUPLE_CONTRACT_DATA
    )
    return await async_deploy(
        async_w3, async_nested_tuple_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_tuple_contract_with_decode_tuples(async_w3, address_conversion_func):
    async_tuple_contract_factory = async_w3.eth.contract(
        **TUPLE_CONTRACT_DATA_DECODE_TUPLES
    )
    return await async_deploy(
        async_w3, async_tuple_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_nested_tuple_contract_with_decode_tuples(
    async_w3, address_conversion_func
):
    async_nested_tuple_contract_factory = async_w3.eth.contract(
        **NESTED_TUPLE_CONTRACT_DATA_DECODE_TUPLES
    )
    return await async_deploy(
        async_w3, async_nested_tuple_contract_factory, address_conversion_func
    )


@pytest_asyncio.fixture
async def async_event_contract(
    async_w3, async_wait_for_transaction, async_wait_for_block, address_conversion_func
):
    async_event_contract_factory = async_w3.eth.contract(**EVENT_CONTRACT_DATA)

    await async_wait_for_block(async_w3)
    deploy_txn_hash = await async_event_contract_factory.constructor().transact(
        {"gas": 1000000}
    )
    deploy_receipt = await async_wait_for_transaction(async_w3, deploy_txn_hash)
    contract_address = address_conversion_func(deploy_receipt["contractAddress"])

    bytecode = await async_w3.eth.get_code(contract_address)
    assert bytecode == async_event_contract_factory.bytecode_runtime
    event_contract = async_event_contract_factory(address=contract_address)
    assert event_contract.address == contract_address
    return event_contract


@pytest_asyncio.fixture
async def async_ambiguous_event_contract(async_w3, address_conversion_func):
    async_ambiguous_event_contract_factory = async_w3.eth.contract(
        **AMBIGUOUS_EVENT_NAME_CONTRACT_DATA
    )

    return await async_deploy(
        async_w3, async_ambiguous_event_contract_factory, address_conversion_func
    )


async def async_invoke_contract(
    api_call_desig="call",
    contract=None,
    contract_function=None,
    func_args=None,
    func_kwargs=None,
    tx_params=None,
):
    function_signature = contract_function
    function_arg_count = len(func_args or ()) + len(func_kwargs or {})
    if function_arg_count == 0:
        function_signature = get_abi_element_signature(contract_function)

    if func_args is None:
        func_args = []
    if func_kwargs is None:
        func_kwargs = {}
    if tx_params is None:
        tx_params = {}
    allowable_call_desig = ["call", "transact", "estimate_gas", "build_transaction"]
    if api_call_desig not in allowable_call_desig:
        raise Web3ValueError(
            f"allowable_invoke_method must be one of: {allowable_call_desig}"
        )

    fn_abi = get_abi_element(
        contract.abi,
        function_signature,
        *func_args,
        abi_codec=contract.w3.codec,
        **func_kwargs,
    )
    function = contract.functions[abi_to_signature(fn_abi)]
    result = await getattr(function(*func_args, **func_kwargs), api_call_desig)(
        tx_params
    )

    return result


@pytest.fixture
def async_build_transaction(request):
    return async_partial(async_invoke_contract, api_call_desig="build_transaction")


@pytest.fixture
def async_transact(request):
    return async_partial(async_invoke_contract, api_call_desig="transact")


@pytest.fixture
def async_call(request):
    return async_partial(async_invoke_contract, api_call_desig="call")


@pytest.fixture
def async_estimate_gas(request):
    return async_partial(async_invoke_contract, api_call_desig="estimate_gas")


@pytest_asyncio.fixture
async def async_emitter(
    async_w3,
    emitter_contract_data,
    async_wait_for_transaction,
    async_wait_for_block,
    address_conversion_func,
):
    async_emitter_contract_factory = async_w3.eth.contract(**emitter_contract_data)

    await async_wait_for_block(async_w3)
    deploy_txn_hash = await async_emitter_contract_factory.constructor().transact(
        {"gas": 10000000}
    )
    deploy_receipt = await async_wait_for_transaction(async_w3, deploy_txn_hash)
    contract_address = address_conversion_func(deploy_receipt["contractAddress"])

    bytecode = await async_w3.eth.get_code(contract_address)
    assert bytecode == async_emitter_contract_factory.bytecode_runtime
    _emitter = async_emitter_contract_factory(address=contract_address)
    assert _emitter.address == contract_address
    return _emitter
