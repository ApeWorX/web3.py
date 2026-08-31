import pytest
import json

from eth_utils import (
    abi_to_signature,
    decode_hex,
    filter_abi_by_type,
    get_abi_input_names,
    get_abi_input_types,
)

from web3._utils.abi import (
    get_name_from_abi_element_identifier,
)
from web3.contract import (
    Contract,
)
from web3.exceptions import (
    ABIEventNotFound,
    ABIFallbackNotFound,
    ABIFunctionNotFound,
    NoABIEventsFound,
    NoABIFound,
    NoABIFunctionsFound,
    Web3AttributeError,
)


def test_class_construction_sets_class_vars(
    w3, math_contract_abi, math_contract_bytecode, math_contract_runtime
):
    math_contract_factory = w3.eth.contract(
        abi=math_contract_abi,
        bytecode=math_contract_bytecode,
        bytecode_runtime=math_contract_runtime,
    )

    assert math_contract_factory.w3 == w3
    assert math_contract_factory.bytecode == decode_hex(math_contract_bytecode)
    assert math_contract_factory.bytecode_runtime == decode_hex(math_contract_runtime)
    assert math_contract_factory.abi == math_contract_abi


def test_error_to_instantiate_base_class():
    with pytest.raises(Web3AttributeError):
        Contract()


def test_abi_as_json_string(w3, math_contract_abi, some_address):
    abi_str = json.dumps(math_contract_abi)

    math_contract_factory = w3.eth.contract(abi=abi_str)
    assert math_contract_factory.abi == math_contract_abi

    math = math_contract_factory(some_address)
    assert math.abi == math_contract_abi


@pytest.mark.parametrize(
    "abi",
    ([{"type": "function", "name": "abi"}], [{"type": "function", "name": "address"}]),
)
def test_contract_init_with_reserved_name(w3, abi):
    with pytest.raises(Web3AttributeError):
        w3.eth.contract(abi=abi)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "abi",
    ([{"type": "function", "name": "abi"}], [{"type": "function", "name": "address"}]),
)
async def test_async_contract_init_with_reserved_name(async_w3, abi):
    with pytest.raises(Web3AttributeError):
        await async_w3.eth.contract(abi=abi)


def test_error_to_call_non_existent_fallback(
    w3, math_contract_abi, math_contract_bytecode, math_contract_runtime
):
    math_contract = w3.eth.contract(
        abi=math_contract_abi,
        bytecode=math_contract_bytecode,
        bytecode_runtime=math_contract_runtime,
    )
    with pytest.raises(ABIFallbackNotFound):
        math_contract.fallback.estimate_gas()


def test_math_contract_events_init_with_class_vars(
    w3, math_contract_abi, math_contract_bytecode, math_contract_runtime
):
    math_contract = w3.eth.contract(
        abi=math_contract_abi,
        bytecode=math_contract_bytecode,
        bytecode_runtime=math_contract_runtime,
    )

    for event_abi in filter_abi_by_type("event", math_contract_abi):
        # Check properties of math_contract.events.EventName
        event_by_name = math_contract.events[event_abi["name"]]
        if event_by_name.abi["inputs"] == event_abi["inputs"]:
            assert event_by_name.name == get_name_from_abi_element_identifier(
                event_abi["name"]
            )
            assert event_by_name.abi == event_abi
            assert event_by_name.abi_element_identifier == abi_to_signature(event_abi)
            assert event_by_name.signature == abi_to_signature(event_abi)
            assert event_by_name.argument_names == tuple(get_abi_input_names(event_abi))
            assert event_by_name.argument_types == tuple(get_abi_input_types(event_abi))

        # Check properties of math_contract.events._EventName(arg_names)
        event_by_signature = math_contract.events[f"_{abi_to_signature(event_abi)}"]
        assert event_by_signature.name == get_name_from_abi_element_identifier(
            abi_to_signature(event_abi)
        )
        assert event_by_signature.abi == event_abi
        assert event_by_signature.abi_element_identifier == abi_to_signature(event_abi)
        assert event_by_signature.signature == abi_to_signature(event_abi)
        assert event_by_signature.argument_names == tuple(
            get_abi_input_names(event_abi)
        )
        assert event_by_signature.argument_types == tuple(
            get_abi_input_types(event_abi)
        )


def test_tuple_contract_events_init_with_class_vars(
    w3, tuple_contract_abi, tuple_contract_bytecode, tuple_contract_runtime
):
    tuple_contract = w3.eth.contract(
        abi=tuple_contract_abi,
        bytecode=tuple_contract_bytecode,
        bytecode_runtime=tuple_contract_runtime,
    )

    for event_abi in filter_abi_by_type("event", tuple_contract_abi):
        # Check properties of tuple_contract.events.EventName
        event_by_name = tuple_contract.events[event_abi["name"]]
        if event_by_name.abi["inputs"] == event_abi["inputs"]:
            assert event_by_name.name == get_name_from_abi_element_identifier(
                event_abi["name"]
            )
            assert event_by_name.abi == event_abi
            assert event_by_name.abi_element_identifier == abi_to_signature(event_abi)
            assert event_by_name.signature == abi_to_signature(event_abi)
            assert event_by_name.argument_names == tuple(get_abi_input_names(event_abi))
            assert event_by_name.argument_types == tuple(get_abi_input_types(event_abi))

        # Check properties of tuple_contract.events._EventName(arg_names)
        event_by_signature = tuple_contract.events[f"_{abi_to_signature(event_abi)}"]
        assert event_by_signature.name == get_name_from_abi_element_identifier(
            abi_to_signature(event_abi)
        )
        assert event_by_signature.abi == event_abi
        assert event_by_signature.abi_element_identifier == abi_to_signature(event_abi)
        assert event_by_signature.signature == abi_to_signature(event_abi)
        assert event_by_signature.argument_names == tuple(
            get_abi_input_names(event_abi)
        )
        assert event_by_signature.argument_types == tuple(
            get_abi_input_types(event_abi)
        )


def test_math_contract_functions_init_with_class_vars(
    w3, math_contract_abi, math_contract_bytecode, math_contract_runtime
):
    math_contract = w3.eth.contract(
        abi=math_contract_abi,
        bytecode=math_contract_bytecode,
        bytecode_runtime=math_contract_runtime,
    )

    for function_abi in filter_abi_by_type("function", math_contract_abi):
        # Check properties of math_contract.functions.FunctionName
        function_by_name = math_contract.functions[function_abi["name"]]
        if function_by_name.abi["inputs"] == function_abi["inputs"]:
            assert function_by_name.name == get_name_from_abi_element_identifier(
                function_abi["name"]
            )
            assert function_by_name.abi == function_abi
            assert function_by_name.abi_element_identifier == abi_to_signature(
                function_abi
            )
            assert function_by_name.signature == abi_to_signature(function_abi)
            assert function_by_name.argument_names == tuple(
                get_abi_input_names(function_abi)
            )
            assert function_by_name.argument_types == tuple(
                get_abi_input_types(function_abi)
            )

        # Check properties of math_contract.functions._functionName(arg_names)
        function_by_signature = math_contract.functions[abi_to_signature(function_abi)]
        assert function_by_signature.name == get_name_from_abi_element_identifier(
            abi_to_signature(function_abi)
        )
        assert function_by_signature.abi == function_abi
        assert function_by_signature.abi_element_identifier == abi_to_signature(
            function_abi
        )
        assert function_by_signature.signature == abi_to_signature(function_abi)
        assert function_by_signature.argument_names == tuple(
            get_abi_input_names(function_abi)
        )
        assert function_by_signature.argument_types == tuple(
            get_abi_input_types(function_abi)
        )


def test_tuple_contract_functions_init_with_class_vars(
    w3, tuple_contract_abi, tuple_contract_bytecode, tuple_contract_runtime
):
    tuple_contract = w3.eth.contract(
        abi=tuple_contract_abi,
        bytecode=tuple_contract_bytecode,
        bytecode_runtime=tuple_contract_runtime,
    )

    for function_abi in filter_abi_by_type("function", tuple_contract_abi):
        # Check properties of tuple_contract.functions.FunctionName
        function_by_name = tuple_contract.functions[function_abi["name"]]
        if function_by_name.abi["inputs"] == function_abi["inputs"]:
            assert function_by_name.name == get_name_from_abi_element_identifier(
                function_abi["name"]
            )
            assert function_by_name.abi == function_abi
            assert function_by_name.abi_element_identifier == abi_to_signature(
                function_abi
            )
            assert function_by_name.signature == abi_to_signature(function_abi)
            assert function_by_name.argument_names == tuple(
                get_abi_input_names(function_abi)
            )
            assert function_by_name.argument_types == tuple(
                get_abi_input_types(function_abi)
            )

        # Check properties of tuple_contract.functions._functionName(arg_names)
        function_by_signature = tuple_contract.functions[abi_to_signature(function_abi)]
        assert function_by_signature.name == get_name_from_abi_element_identifier(
            abi_to_signature(function_abi)
        )
        assert function_by_signature.abi == function_abi
        assert function_by_signature.abi_element_identifier == abi_to_signature(
            function_abi
        )
        assert function_by_signature.signature == abi_to_signature(function_abi)
        assert function_by_signature.argument_names == tuple(
            get_abi_input_names(function_abi)
        )
        assert function_by_signature.argument_types == tuple(
            get_abi_input_types(function_abi)
        )


@pytest.mark.parametrize(
    "abi,namespace,expected_exception",
    (
        ([{"type": "event", "name": "AnEvent"}], "functions", NoABIFunctionsFound),
        ([{"type": "function", "name": "aFunction"}], "events", NoABIEventsFound),
        ([{"type": "function", "name": "aFunction"}], "functions", ABIFunctionNotFound),
        ([{"type": "event", "name": "AnEvent"}], "events", ABIEventNotFound),
    ),
)
def test_appropriate_exceptions_based_on_namespaces(
    w3, abi, namespace, expected_exception
):
    contract = w3.eth.contract(abi=abi)

    namespace_instance = getattr(contract, namespace)

    with pytest.raises(expected_exception):
        namespace_instance.doesNotExist()


@pytest.mark.parametrize(
    "namespace",
    ("functions", "events"),
)
def test_appropriate_exceptions_based_on_namespaces_no_abi(w3, namespace):
    contract = w3.eth.contract()

    namespace_instance = getattr(contract, namespace)

    with pytest.raises(NoABIFound):
        namespace_instance.doesNotExist()


@pytest.mark.parametrize(
    "abi,namespace,expected_exception",
    (
        ([{"type": "event", "name": "AnEvent"}], "functions", NoABIFunctionsFound),
        ([{"type": "function", "name": "aFunction"}], "events", NoABIEventsFound),
        ([{"type": "function", "name": "aFunction"}], "functions", ABIFunctionNotFound),
        ([{"type": "event", "name": "AnEvent"}], "events", ABIEventNotFound),
    ),
)
def test_async_appropriate_exceptions_based_on_namespaces(
    async_w3, abi, namespace, expected_exception
):
    contract = async_w3.eth.contract(abi=abi)

    namespace_instance = getattr(contract, namespace)

    with pytest.raises(expected_exception):
        namespace_instance.doesNotExist()


@pytest.mark.parametrize(
    "namespace",
    ("functions", "events"),
)
def test_async_appropriate_exceptions_based_on_namespaces_no_abi(async_w3, namespace):
    # Initialize without ABI
    contract = async_w3.eth.contract()

    namespace_instance = getattr(contract, namespace)

    with pytest.raises(NoABIFound):
        namespace_instance.doesNotExist()
