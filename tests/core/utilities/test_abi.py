import pytest
from collections.abc import Callable, Sequence
from decimal import (
    Decimal,
)
import re
from typing import (
    Any,
)

from eth_abi.codec import (
    ABICodec,
)
from eth_abi.registry import (
    registry as default_registry,
)
from eth_typing import (
    ABI,
    ABIComponent,
    ABIComponentIndexed,
    ABIConstructor,
    ABIElement,
    ABIError,
    ABIEvent,
    ABIFallback,
    ABIFunction,
    ABIReceive,
)
from hexbytes import (
    HexBytes,
)

from web3._utils.abi import (
    ExactLengthBytesEncoder,
    abi_data_tree,
    get_tuple_type_str_parts,
    map_abi_data,
    recursive_dict_to_namedtuple,
)
from web3._utils.abi_element_identifiers import (
    FallbackFn,
    ReceiveFn,
)
from web3._utils.normalizers import (
    BASE_RETURN_NORMALIZERS,
    abi_string_to_text,
    addresses_checksummed,
)
from web3.exceptions import (
    MismatchedABI,
    Web3ValidationError,
    Web3ValueError,
)
from web3.types import (
    ABIElementIdentifier,
)
from web3.utils.abi import (
    get_abi_element,
    get_abi_element_info,
    get_event_abi,
    get_event_log_topics,
)

FUNCTION_ABI_NO_INPUTS = ABIFunction({"type": "function", "name": "myFunction"})

FUNCTION_ABI: ABIFunction = {
    "constant": False,
    "inputs": [
        {
            "components": [
                {"name": "a", "type": "uint256"},
                {"name": "b", "type": "uint256[]"},
                {
                    "components": [
                        {"name": "x", "type": "uint256"},
                        {"name": "y", "type": "uint256"},
                    ],
                    "name": "c",
                    "type": "tuple[]",
                },
            ],
            "name": "s",
            "type": "tuple",
        },
        {
            "components": [
                {"name": "x", "type": "uint256"},
                {"name": "y", "type": "uint256"},
            ],
            "name": "t",
            "type": "tuple",
        },
        {"name": "a", "type": "uint256"},
        {
            "components": [
                {"name": "x", "type": "uint256"},
                {"name": "y", "type": "uint256"},
            ],
            "name": "b",
            "type": "tuple[][]",
        },
    ],
    "name": "f",
    "outputs": [],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function",
}

LOG_TWO_EVENTS_ABI: ABIFunction = {
    "inputs": [{"name": "_arg0", "type": "uint256"}],
    "name": "logTwoEvents",
    "stateMutability": "nonpayable",
    "type": "function",
}

SET_VALUE_ABI: ABIFunction = {
    "inputs": [{"name": "_arg0", "type": "fixed8x1"}],
    "name": "setValue",
    "stateMutability": "nonpayable",
    "type": "function",
}
SET_VALUE_ABI_UFIXED: ABIFunction = {
    "inputs": [{"name": "_arg0", "type": "ufixed256x80"}],
    "name": "setValue",
    "stateMutability": "nonpayable",
    "type": "function",
}
SET_VALUE_WITH_TUPLE_ABI: ABIFunction = {
    "inputs": [
        {"name": "_arg0", "type": "uint256"},
        {
            "type": "tuple",
            "name": "arg1",
            "components": [
                {"name": "a", "type": "uint256"},
                {"name": "b", "type": "uint256"},
            ],
        },
    ],
    "name": "setValue",
    "stateMutability": "nonpayable",
    "type": "function",
}

AMBIGUOUS_EVENT_ABI: ABIEvent = {
    "anonymous": False,
    "inputs": [{"name": "arg0", "type": "uint256"}],
    "name": "LogSingleArg",
    "type": "event",
}
AMBIGUOUS_EVENT_ABI_NO_INPUTS: ABIEvent = {
    "anonymous": False,
    "inputs": [],
    "name": "LogSingleArg",
    "type": "event",
}

CONTRACT_ABI: ABI = [
    LOG_TWO_EVENTS_ABI,
    SET_VALUE_ABI,
    SET_VALUE_ABI_UFIXED,
    SET_VALUE_WITH_TUPLE_ABI,
    FUNCTION_ABI_NO_INPUTS,
]

CONTRACT_ABI_AMBIGUOUS_EVENT: ABI = [
    AMBIGUOUS_EVENT_ABI,
    AMBIGUOUS_EVENT_ABI_NO_INPUTS,
]

ABI_CONSTRUCTOR = ABIConstructor({"type": "constructor"})
ABI_CONSTRUCTOR_WITH_ARGS = ABIConstructor(
    {"type": "constructor", "inputs": [{"name": "x", "type": "address"}]}
)

ABI_FALLBACK = ABIFallback({"type": "fallback"})

ABI_RECEIVE = ABIReceive({"type": "receive"})

ABI_EVENT_TRANSFER = ABIEvent(
    {
        "anonymous": False,
        "name": "Transfer",
        "type": "event",
        "inputs": [
            ABIComponentIndexed({"indexed": True, "name": "from", "type": "address"}),
            ABIComponentIndexed({"indexed": True, "name": "to", "type": "address"}),
            ABIComponentIndexed({"indexed": False, "name": "value", "type": "uint256"}),
        ],
    }
)

ABI_ERROR = ABIError({"type": "error", "name": "error"})


@pytest.fixture()
def contract_abi() -> ABI:
    return CONTRACT_ABI


@pytest.mark.parametrize(
    "input, expected",
    (
        # Well-formed tuple type strings
        ("tuple", ("tuple", None)),
        ("tuple[]", ("tuple", "[]")),
        ("tuple[1]", ("tuple", "[1]")),
        ("tuple[10]", ("tuple", "[10]")),
        ("tuple[19]", ("tuple", "[19]")),
        ("tuple[195]", ("tuple", "[195]")),
        ("tuple[][]", ("tuple", "[][]")),
        ("tuple[1][1]", ("tuple", "[1][1]")),
        ("tuple[1][]", ("tuple", "[1][]")),
        ("tuple[][1]", ("tuple", "[][1]")),
        ("tuple[][][]", ("tuple", "[][][]")),
        ("tuple[1][][]", ("tuple", "[1][][]")),
        ("tuple[][1][]", ("tuple", "[][1][]")),
        ("tuple[][][1]", ("tuple", "[][][1]")),
        # Malformed tuple type strings
        ("tupleasfasdf", None),
        ("uint256", None),
        ("bool", None),
        ("", None),
        ("tupletuple", None),
        ("tuple[0]", None),
        ("tuple[01]", None),
        ("tuple[][0]", None),
        ("tuple[][01]", None),
        ("tuple[0][][]", None),
        ("tuple[][0][]", None),
        ("tuple[][][0]", None),
    ),
)
def test_get_tuple_type_str_parts(
    input: str, expected: tuple[str, str | None] | None
) -> None:
    assert get_tuple_type_str_parts(input) == expected


@pytest.mark.parametrize(
    "types, data, expected",
    [
        (
            ["bool[2]", "bytes"],
            [[True, False], b"\x00\xff"],
            [("bool[2]", [("bool", True), ("bool", False)]), ("bytes", b"\x00\xff")],
        ),
        (
            ["uint256[]"],
            [[0, 2**256 - 1]],
            [("uint256[]", [("uint256", 0), ("uint256", 2**256 - 1)])],
        ),
    ],
)
def test_abi_data_tree(
    types: list[str], data: tuple[list[bool], bytes], expected: list[Any]
) -> None:
    assert abi_data_tree(types, data) == expected


@pytest.mark.parametrize(
    "types, data, funcs, expected",
    [
        (
            ["bool[2]", "int256"],
            [[True, False], 9876543210],
            [
                lambda typ, dat: (
                    (typ, "Tru-dat") if typ == "bool" and dat else (typ, dat)
                ),
                lambda typ, dat: (typ, hex(dat)) if typ == "int256" else (typ, dat),
            ],
            [["Tru-dat", False], "0x24cb016ea"],
        ),
        (
            ["address"],
            ["0x5b2063246f2191f18f2675cedb8b28102e957458"],
            BASE_RETURN_NORMALIZERS,
            ["0x5B2063246F2191f18F2675ceDB8b28102e957458"],
        ),
        (
            ["address[]"],
            [["0x5b2063246f2191f18f2675cedb8b28102e957458"] * 2],
            BASE_RETURN_NORMALIZERS,
            [["0x5B2063246F2191f18F2675ceDB8b28102e957458"] * 2],
        ),
        (
            ["(address,address)[]"],
            [
                [
                    (
                        "0x5b2063246f2191f18f2675cedb8b28102e957458",
                        "0xebe0da78ecb266c7ea605dc889c64849f860383f",
                    )
                ]
                * 2
            ],
            BASE_RETURN_NORMALIZERS,
            [
                [
                    (
                        "0x5B2063246F2191f18F2675ceDB8b28102e957458",
                        "0xeBe0DA78ecb266C7EA605DC889c64849F860383F",
                    )
                ]
                * 2
            ],
        ),
        (
            ["(string,address[])"],
            [
                (
                    b"a string",
                    [b"\xf2\xe2F\xbbv\xdf\x87l\xef\x8b8\xae\x84\x13\x0fOU\xde9["],
                )
            ],
            [addresses_checksummed, abi_string_to_text],
            [("a string", ["0xF2E246BB76DF876Cef8b38ae84130F4F55De395b"])],
        ),
    ],
)
def test_map_abi_data(
    types: list[str],
    data: tuple[Any, ...],
    funcs: tuple[Callable[..., Any], ...],
    expected: tuple[Any, ...],
) -> None:
    assert map_abi_data(funcs, types, data) == expected


@pytest.mark.parametrize("arg", (6, 7, 9, 12, 20, 30))
def test_exact_length_bytes_encoder_raises_on_non_multiples_of_8_bit_size(
    arg: tuple[int, ...],
) -> None:
    with pytest.raises(Web3ValueError, match="multiple of 8"):
        _ = ExactLengthBytesEncoder(None, data_byte_size=2, value_bit_size=arg)


@pytest.mark.parametrize(
    "input, expected_output",
    [
        ({"a": 1, "b": 2}, "ABIDecodedNamedTuple(a=1, b=2)"),
        ({"a": 0}, "ABIDecodedNamedTuple(a=0)"),
        ({"a": None}, "ABIDecodedNamedTuple(a=None)"),
        ({"a": False}, "ABIDecodedNamedTuple(a=False)"),
        ({}, "ABIDecodedNamedTuple()"),
        ({"a": {}}, "ABIDecodedNamedTuple(a=ABIDecodedNamedTuple())"),
        ({"a": []}, "ABIDecodedNamedTuple(a=[])"),
        ({"a": [0]}, "ABIDecodedNamedTuple(a=[0])"),
        ({"a": [{}]}, "ABIDecodedNamedTuple(a=[ABIDecodedNamedTuple()])"),
        (
            {"a": {"b": {}}},
            "ABIDecodedNamedTuple(a=ABIDecodedNamedTuple(b=ABIDecodedNamedTuple()))",
        ),
    ],
)
def test_recursive_dict_to_namedtuple(
    input: dict[str, Any], expected_output: str
) -> None:
    named_tuple_output = recursive_dict_to_namedtuple(input)
    output_repr = named_tuple_output.__repr__()
    assert output_repr == expected_output


@pytest.mark.parametrize(
    "abi_element_identifier,args,kwargs,expected_selector,expected_arguments",
    [
        ("logTwoEvents", [100], {}, "0x5818fad7", (100,)),
        ("setValue(fixed8x1)", [Decimal("1")], {}, "0xcf20bde8", (Decimal("1"),)),
        (
            "setValue",
            [1],
            {"arg1": {"a": 2, "b": 0}},
            "0x647c15ed",
            (
                1,
                (
                    2,
                    0,
                ),
            ),
        ),
    ],
)
def test_get_abi_element_info(
    contract_abi: ABI,
    abi_element_identifier: ABIElementIdentifier,
    args: Sequence[Any],
    kwargs: dict[str, Any],
    expected_selector: str,
    expected_arguments: Any,
) -> None:
    function_info = get_abi_element_info(
        contract_abi, abi_element_identifier, *args, **kwargs
    )
    assert function_info["abi"] == get_abi_element(
        contract_abi, abi_element_identifier, *args, **kwargs
    )
    assert function_info["selector"] == expected_selector
    assert function_info["arguments"] == expected_arguments


def test_get_abi_element_info_without_args_and_kwargs(
    contract_abi: ABI,
) -> None:
    function_info = get_abi_element_info(contract_abi, "myFunction")
    assert function_info["abi"] == get_abi_element(contract_abi, "myFunction")
    assert function_info["selector"] == "0xc3780a3a"
    assert function_info["arguments"] == ()


def test_get_abi_element_info_raises_mismatched_abi(contract_abi: ABI) -> None:
    with pytest.raises(
        MismatchedABI,
        match=r"\nABI Not Found!\nNo element named `foo` with 1 argument\(s\).\n",  # noqa: E501
    ):
        args: Sequence[Any] = [1]
        get_abi_element_info(contract_abi, "foo", *args, **{})


@pytest.mark.parametrize(
    "abi,abi_element_identifier,args,kwargs,expected_abi",
    (
        (
            CONTRACT_ABI,
            "setValue(ufixed256x80)",
            [0],
            {},
            SET_VALUE_ABI_UFIXED,
        ),
        (
            CONTRACT_ABI,
            "setValue",
            [0],
            {
                "arg1": {
                    "a": 10000,
                    "b": 987654321,
                }
            },
            SET_VALUE_WITH_TUPLE_ABI,
        ),
        (
            CONTRACT_ABI,
            "logTwoEvents",
            [1],
            {},
            LOG_TWO_EVENTS_ABI,
        ),
        (
            CONTRACT_ABI,
            "logTwoEvents",
            [],  # function name is unique so args are optional
            {},
            LOG_TWO_EVENTS_ABI,
        ),
        (
            [FUNCTION_ABI_NO_INPUTS],
            "myFunction",
            [],
            {},
            FUNCTION_ABI_NO_INPUTS,
        ),
        (
            [ABI_EVENT_TRANSFER],
            "Transfer",
            [
                "0x0000000000000000000000000000000000000000",
                "0x0000000000000000000000000000000000000000",
                1,
            ],
            {},
            ABI_EVENT_TRANSFER,
        ),
        (
            [ABI_ERROR],
            "error",
            [],
            {},
            ABI_ERROR,
        ),
        (
            [ABI_FALLBACK],
            "fallback",
            [],
            {},
            ABI_FALLBACK,
        ),
        (
            [ABI_FALLBACK],
            FallbackFn,
            [],
            {},
            ABI_FALLBACK,
        ),
        (
            [ABI_RECEIVE],
            "receive",
            [],
            {},
            ABI_RECEIVE,
        ),
        (
            [ABI_RECEIVE],
            ReceiveFn,
            [],
            {},
            ABI_RECEIVE,
        ),
        (
            [ABI_CONSTRUCTOR],
            "constructor",
            [],
            {},
            ABI_CONSTRUCTOR,
        ),
        (
            [ABI_CONSTRUCTOR_WITH_ARGS],
            "constructor",
            ["0x0000000000000000000000000000000000000000"],
            {},
            ABI_CONSTRUCTOR_WITH_ARGS,
        ),
        (
            CONTRACT_ABI_AMBIGUOUS_EVENT,
            "LogSingleArg()",
            [],
            {},
            AMBIGUOUS_EVENT_ABI_NO_INPUTS,
        ),
    ),
)
def test_get_abi_element(
    abi: ABI,
    abi_element_identifier: ABIElementIdentifier,
    args: Sequence[Any],
    kwargs: dict[str, Any],
    expected_abi: ABIElement,
) -> None:
    assert (
        get_abi_element(
            abi,
            abi_element_identifier,
            *args,
            **kwargs,
        )
        == expected_abi
    )


@pytest.mark.parametrize(
    "abi,abi_element_identifier,args,kwargs,expected_error,expected_message",
    (
        (
            CONTRACT_ABI,
            1,
            ["_arg0"],
            {},
            TypeError,
            "Unsupported function identifier",
        ),
        (
            CONTRACT_ABI,
            "setValue",
            [],  # function name is ambiguous and cannot be determined without args
            {},
            MismatchedABI,
            "\nABI Not Found!\n"
            "Found multiple elements named `setValue` that accept 0 argument(s).\n"
            "Provided argument types: ()\n"
            "Provided keyword argument types: {}\n\n"
            "Tried to find a matching ABI element named `setValue`, but encountered "
            "the following problems:\n"
            "Signature: setValue(fixed8x1), type: function\n"
            "Expected 1 argument(s) but received 0 argument(s).\n"
            "Signature: setValue(ufixed256x80), type: function\n"
            "Expected 1 argument(s) but received 0 argument(s).\n"
            "Signature: setValue(uint256,(uint256,uint256)), type: function\n"
            "Expected 2 argument(s) but received 0 argument(s).\n",
        ),
        (
            CONTRACT_ABI,
            "setValue",
            [
                Decimal("0")
            ],  # function name is ambiguous and cannot be determined without args
            {},
            MismatchedABI,
            "\nABI Not Found!\n"
            "Found multiple elements named `setValue` that accept 1 argument(s).\n"
            "Provided argument types: (Decimal)\n"
            "Provided keyword argument types: {}\n\n"
            "Tried to find a matching ABI element named `setValue`, but encountered "
            "the following problems:\n"
            "Signature: setValue(fixed8x1), type: function\n"
            "Argument 1 value `0` is valid.\n"
            "Signature: setValue(ufixed256x80), type: function\n"
            "Argument 1 value `0` is valid.\n"
            "Signature: setValue(uint256,(uint256,uint256)), type: function\n"
            "Expected 2 argument(s) but received 1 argument(s).\n",
        ),
        (
            CONTRACT_ABI,
            "setValue",
            [1, (1, "foo")],
            {},
            MismatchedABI,
            "\nABI Not Found!\n"
            "Found 1 element(s) named `setValue` that accept 2 argument(s).\n"
            "The provided arguments are not valid.\n"
            "Provided argument types: (int,int,str)\n"
            "Provided keyword argument types: {}\n\n"
            "Tried to find a matching ABI element named `setValue`, but encountered "
            "the following problems:\n"
            "Signature: setValue(uint256,(uint256,uint256)), type: function\n"
            "Argument 1 value `1` is valid.\n"
            "Argument 2 value `(1, 'foo')` is not compatible with type `(uint256,uint256)`.\n"  # noqa: E501
            "Signature: setValue(fixed8x1), type: function\n"
            "Expected 1 argument(s) but received 2 argument(s).\n"
            "Signature: setValue(ufixed256x80), type: function\n"
            "Expected 1 argument(s) but received 2 argument(s).\n",
        ),
        (
            CONTRACT_ABI_AMBIGUOUS_EVENT,
            "LogSingleArg",
            [],
            {},
            MismatchedABI,
            "\nABI Not Found!\n"
            "Found multiple elements named `LogSingleArg` that accept 0 argument(s).\n"
            "Provided argument types: ()\n"
            "Provided keyword argument types: {}\n\n"
            "Tried to find a matching ABI element named `LogSingleArg`, but "
            "encountered the following problems:\n"
            "The provided identifier matches multiple elements.\n"
            "If you meant to call `LogSingleArg()`, please specify the full "
            "signature.\n"
            " - signature: LogSingleArg(), type: event\n"
            "Signature: LogSingleArg(uint256), type: event\n"
            "Expected 1 argument(s) but received 0 argument(s).\n",
        ),
        (
            CONTRACT_ABI_AMBIGUOUS_EVENT,
            "noFunc",
            [],
            {},
            MismatchedABI,
            "No element named `noFunc` with 0 argument(s).\n",
        ),
        (
            CONTRACT_ABI_AMBIGUOUS_EVENT,
            "noFunc(uint256)",
            [],
            {},
            MismatchedABI,
            "No element named `noFunc` with 0 argument(s).\n",
        ),
        (
            [
                {"type": "function", "name": "Nonexistent"},
                {"type": "event", "name": "Nonexistent"},
            ],
            "Nonexistent",
            [],
            {},
            MismatchedABI,
            "",
        ),
        (
            [{}],
            "nonexistent",
            [],
            {},
            Web3ValueError,
            "'abi' must contain a list of elements each with a type",
        ),
        (
            {},
            "nonexistent",
            [],
            {},
            Web3ValueError,
            "'abi' is not a list",
        ),
        (
            "ABI",
            "nonexistent",
            [],
            {},
            Web3ValueError,
            "'abi' is not a list",
        ),
    ),
)
def test_get_abi_element_raises_with_invalid_parameters(
    abi: ABI,
    abi_element_identifier: ABIElementIdentifier,
    args: Sequence[Any] | None,
    kwargs: dict[str, Any] | None,
    expected_error: type[Exception],
    expected_message: str,
) -> None:
    with pytest.raises(expected_error, match=re.escape(expected_message)):
        get_abi_element(abi, abi_element_identifier, *args, **kwargs)


def test_get_abi_element_codec_override(contract_abi: ABI) -> None:
    codec = ABICodec(default_registry)
    args: Sequence[Any] = [1]
    function_abi = get_abi_element(contract_abi, "logTwoEvents", *args, abi_codec=codec)
    expected_abi = {
        "inputs": [{"name": "_arg0", "type": "uint256"}],
        "name": "logTwoEvents",
        "stateMutability": "nonpayable",
        "type": "function",
    }
    assert function_abi == expected_abi


@pytest.mark.parametrize(
    "topics,anonymous,expected_topics",
    [
        (
            [
                "0x87e10a54d1dda06db0fde99bdb2e67e6638ca9d2b5add2e3b5b406525b15824a",
                "0x1",
                "0x2",
            ],
            False,
            ["0x1", "0x2"],
        ),
        (
            [
                "0x111",
            ],
            True,
            ["0x111"],
        ),
    ],
)
def test_get_event_log_topics(
    topics: Sequence[HexBytes], anonymous: bool, expected_topics: Sequence[HexBytes]
) -> None:
    event_abi: ABIEvent = {
        "anonymous": anonymous,
        "inputs": [],
        "name": "LogSingleArg",
        "type": "event",
    }

    assert get_event_log_topics(event_abi, topics) == expected_topics


@pytest.mark.parametrize(
    "topics,expected_error",
    [
        (
            [],
            "Expected non-anonymous event to have 1 or more topics",
        ),
        (
            ["0x1"],
            "The event signature did not match the provided ABI",
        ),
    ],
)
def test_get_event_log_topics_raises_for_bad_topics(
    topics: Sequence[HexBytes], expected_error: str
) -> None:
    event_abi: ABIEvent = {
        "anonymous": False,
        "inputs": [],
        "name": "LogSingleArg",
        "type": "event",
    }

    with pytest.raises(MismatchedABI, match=expected_error):
        get_event_log_topics(event_abi, topics)


@pytest.mark.parametrize(
    "event_name,input_args",
    [
        ("LogSingleArg", [{"name": "arg0", "type": "uint256"}]),
        ("LogSingleWithIndex", [{"name": "arg0", "type": "uint256", "indexed": True}]),
        ("LogNoArg", []),
    ],
)
def test_get_event_abi(event_name: str, input_args: Sequence[ABIComponent]) -> None:
    contract_abi: ABI = [
        {
            "anonymous": False,
            "inputs": [{"name": "arg0", "type": "uint256"}],
            "name": "LogSingleArg",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                ABIComponentIndexed(
                    {"name": "arg0", "type": "uint256", "indexed": True}
                )
            ],
            "name": "LogSingleWithIndex",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [],
            "name": "LogNoArg",
            "type": "event",
        },
    ]
    expected_event_abi = {
        "anonymous": False,
        "inputs": input_args,
        "name": event_name,
        "type": "event",
    }

    input_names = [arg["name"] for arg in input_args]

    with pytest.warns(
        DeprecationWarning,
        match="get_event_abi is deprecated: use get_abi_element instead",
    ):
        assert (
            get_event_abi(contract_abi, event_name, input_names) == expected_event_abi
        )


@pytest.mark.parametrize(
    "name,args,error_type,expected_value",
    (
        (
            None,
            None,
            Web3ValidationError,
            "event_name is required in order to match an event ABI.",
        ),
        ("foo", None, Web3ValueError, "No matching events found"),
    ),
)
def test_get_event_abi_raises_on_error(
    name: str, args: Sequence[str], error_type: type[Exception], expected_value: str
) -> None:
    contract_abi: ABI = [
        {
            "inputs": [
                {"name": "x", "type": "uint256"},
                {"name": "y", "type": "uint256"},
            ],
            "outputs": [
                {"name": "sum", "type": "uint256"},
            ],
            "name": "add",
            "type": "function",
        }
    ]
    with pytest.warns(DeprecationWarning):
        with pytest.raises(error_type, match=expected_value):
            get_event_abi(contract_abi, name, args)


def test_get_event_abi_raises_if_multiple_found() -> None:
    contract_ambiguous_event: ABI = [
        {
            "anonymous": False,
            "inputs": [{"name": "arg0", "type": "uint256"}],
            "name": "LogSingleArg",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [{"name": "arg0", "type": "uint256"}],
            "name": "LogSingleArg",
            "type": "event",
        },
    ]
    with pytest.warns(DeprecationWarning):
        with pytest.raises(ValueError, match="Multiple events found"):
            get_event_abi(contract_ambiguous_event, "LogSingleArg", ["arg0"])
