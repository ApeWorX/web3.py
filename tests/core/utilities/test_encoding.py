import pytest
from ast import (
    literal_eval,
)
import datetime
from unittest.mock import (
    Mock,
)

from eth_utils import (
    is_hex,
    to_hex,
)
from hexbytes import (
    HexBytes,
)
from hypothesis import (
    example,
    given,
    strategies as st,
)

from web3._utils.encoding import (
    FriendlyJsonSerde as FriendlyJson,
    Web3JsonEncoder,
    hex_encode_abi_type,
    hexstr_if_str,
    text_if_str,
)
from web3._utils.hypothesis import (
    hexstr_strategy,
)
from web3.datastructures import (
    AttributeDict,
)
from web3.exceptions import (
    Web3TypeError,
    Web3ValueError,
)
from web3.providers import (
    JSONBaseProvider,
)


@pytest.mark.parametrize(
    "abi_type,value,expected",
    [
        ("bool", True, "0x01"),
        ("bool", False, "0x00"),
        ("uint16", 8, "0x0008"),
        ("int16", 8, "0x0008"),
        ("int16", -8, "0xfff8"),
        (
            "address",
            "0x00360d2b7D240Ec0643B6D819ba81A09e40E5bCd",
            "0x00360d2b7D240Ec0643B6D819ba81A09e40E5bCd",
        ),
        ("bytes2", b"T\x02", "0x5402"),
        ("bytes3", b"T\x02", "0x540200"),
        ("bytes4", "0x1234", "0x12340000"),
        ("bytes32", "0x01", "0x01" + "00" * 31),
        ("bytes2", "0x010203", Web3TypeError),
        ("bytes2", b"\x01\x02\x03", Web3TypeError),
        ("bytes", "0x5402", "0x5402"),
        ("bytes", "5402", Web3TypeError),
        ("string", "testing a string!", "0x74657374696e67206120737472696e6721"),
        ("strings", "bad abi!", Web3ValueError),
        ("bool[", True, Web3ValueError),
        ("bool", "string", Web3TypeError),
        ("uint24", -20, Web3TypeError),
    ],
)
def test_hex_encode_abi_type(abi_type, value, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            hex_encode_abi_type(abi_type, value)
        return

    actual = hex_encode_abi_type(abi_type, value)
    assert actual == expected


@given(st.one_of(st.integers(), st.booleans(), st.binary()))
@example(b"")
def test_hexstr_if_str_passthrough(val):
    to_type = Mock(return_value="zoot")
    assert hexstr_if_str(to_type, val) == "zoot"
    assert to_type.call_args == ((val,), {"hexstr": None})


def test_hexstr_if_str_curried():
    converter = hexstr_if_str(to_hex)
    assert converter(255) == "0xff"


@given(hexstr_strategy())
@example("0x")
@example("0")
def test_hexstr_if_str_on_valid_hex(val):
    to_type = Mock(return_value="zoot")
    assert hexstr_if_str(to_type, val) == "zoot"
    assert to_type.call_args == ((None,), {"hexstr": val})


@given(st.text())
def test_hexstr_if_str_on_invalid_hex(val):
    try:
        is_hexstr = is_hex(val) or val == ""
    except ValueError:
        is_hexstr = False

    if not is_hexstr:
        with pytest.raises(Web3ValueError):
            hexstr_if_str(Mock(), val)


@given(st.one_of(st.integers(), st.booleans(), st.binary()))
@example(b"")
def test_text_if_str_passthrough(val):
    to_type = Mock(return_value="zoot")
    assert text_if_str(to_type, val) == "zoot"
    assert to_type.call_args == ((val,), {"text": None})


@given(st.text())
@example("0xa1")  # valid hexadecimal is still interpreted as unicode characters
def test_text_if_str_on_text(val):
    to_type = Mock(return_value="zoot")
    assert text_if_str(to_type, val) == "zoot"
    assert to_type.call_args == ((None,), {"text": val})


@pytest.mark.parametrize(
    "py_obj, exc_type, expected",
    (
        (
            {
                "date": [
                    datetime.datetime(2018, 5, 10, 1, 5, 10).isoformat(),
                    datetime.datetime(2018, 5, 10, 1, 5, 10).isoformat(),
                ],
                "other_date": datetime.datetime(2018, 5, 10, 1, 5, 10)
                .date()
                .isoformat(),
            },
            None,
            '{"date": ["2018-05-10T01:05:10", "2018-05-10T01:05:10"], "other_date": "2018-05-10"}',  # noqa: E501
        ),
        (
            {
                "date": [
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(),
                ],
                "other_date": datetime.datetime.now(datetime.timezone.utc).date(),
            },
            TypeError,
            "Could not encode to JSON: .*'other_date'.*is not JSON serializable",
        ),
        (
            {
                "bytes_obj": b"\x00\x01\x02\x03",
                "hexbytes_obj": HexBytes(b"\x00\x01\x02\x03"),
            },
            None,
            '{"bytes_obj": "0x00010203", "hexbytes_obj": "0x00010203"}',
        ),
        (
            AttributeDict(
                {
                    "transactions": [
                        AttributeDict(
                            {
                                "hash": HexBytes(
                                    "0x142ab034696c09dcfb2a8b086b494f3f4c419e67b6c04d95882f87156a3b6f35"  # noqa: E501
                                ),
                                "nonce": 3,
                                "blockHash": HexBytes(
                                    "0xe14a0029f8ae6f41ab2287871d7f2f0658696ce0a842883147629cc1b300fc89"  # noqa: E501
                                ),
                                "blockNumber": 4322026,
                                "transactionIndex": 2,
                                "from": "0xb17473E95Cc2c37f88C56593Ff8767e10c972359",
                                "to": "0x8daF62dF221D11b470Ca4531305470DaE4A65784",
                                "value": 0,
                                "gasPrice": 3459216019,
                                "maxPriorityFeePerGas": 2500000000,
                                "maxFeePerGas": 4421310622,
                                "gas": 26856,
                                "input": HexBytes("0x3857"),
                                "chainId": 1337,
                                "type": 2,
                                "accessList": [],
                                "v": 1,
                                "s": HexBytes(
                                    "0x6f5216fc207221a11efe2e4c3e3a881a0b5ca286ede538fc9dbc403b2009ea76"  # noqa: E501
                                ),
                                "r": HexBytes(
                                    "0xd148ae70c8cbef3a038e70e6d1639f0951e60a2965820f33bad19d0a6c2b8116"  # noqa: E501
                                ),
                                "yParity": 1,
                            },
                        )
                    ]
                }
            ),
            None,
            """{"transactions": [{
                "hash": "0x142ab034696c09dcfb2a8b086b494f3f4c419e67b6c04d95882f87156a3b6f35",  # noqa: E501
                "nonce": 3,
                "blockHash": "0xe14a0029f8ae6f41ab2287871d7f2f0658696ce0a842883147629cc1b300fc89",  # noqa: E501
                "blockNumber": 4322026,
                "transactionIndex": 2,
                "from": "0xb17473E95Cc2c37f88C56593Ff8767e10c972359",
                "to": "0x8daF62dF221D11b470Ca4531305470DaE4A65784",
                "value": 0,
                "gasPrice": 3459216019,
                "maxPriorityFeePerGas": 2500000000,
                "maxFeePerGas": 4421310622,
                "gas": 26856,
                "input": "0x3857",
                "chainId": 1337,
                "type": 2,
                "accessList": [],
                "v": 1,
                "s": "0x6f5216fc207221a11efe2e4c3e3a881a0b5ca286ede538fc9dbc403b2009ea76",  # noqa: E501
                "r": "0xd148ae70c8cbef3a038e70e6d1639f0951e60a2965820f33bad19d0a6c2b8116",  # noqa: E501
                "yParity": 1,
            }]}""",
        ),
    ),
    ids=("datetime", "datetime_error", "bytes types", "nested attrdict with hexbytes"),
)
def test_friendly_json_encode_with_web3_json_encoder(py_obj, exc_type, expected):
    if exc_type is None:
        assert literal_eval(
            FriendlyJson().json_encode(py_obj, Web3JsonEncoder)
        ) == literal_eval(expected)
    else:
        with pytest.raises(exc_type, match=expected):
            FriendlyJson().json_encode(py_obj)


@pytest.mark.parametrize(
    "json_str, expected",
    (
        (
            '{"date": ["2018-05-10T01:05:10", "2018-05-10T01:05:10"],"other_date": "2018-05-10"}',  # noqa: E501
            dict,
        ),
    ),
)
def test_friendly_json_decode(json_str, expected):
    assert isinstance(FriendlyJson().json_decode(json_str), expected)


@pytest.mark.parametrize(
    "rpc_response, expected",
    (
        (
            '{"jsonrpc": "2.0", "method": "test_method", "params": [], "id": 1}',
            {"jsonrpc": "2.0", "method": "test_method", "params": [], "id": 1},
        ),
    ),
)
def test_decode_rpc_response(rpc_response, expected):
    assert (
        JSONBaseProvider().decode_rpc_response(rpc_response.encode("utf8")) == expected
    )


@pytest.mark.parametrize(
    "rpc_kwargs, exc_type, expected",
    (
        (
            {"id": 1, "method": "test", "params": [], "jsonrpc": "2.0"},
            None,
            '{"id": 0, "method": "test", "params": [], "jsonrpc": "2.0",}',
        ),
        (
            {
                "id": 0,
                "method": "test",
                "params": [datetime.datetime(2018, 5, 10, 1, 5, 10)],
            },
            TypeError,
            r"Could not encode to JSON: .*'params'.* is not JSON serializable",
        ),
    ),
)
def test_encode_rpc_request(rpc_kwargs, exc_type, expected):
    if exc_type is None:
        res = JSONBaseProvider().encode_rpc_request(
            rpc_kwargs["method"], rpc_kwargs["params"]
        )
        assert literal_eval(res.decode("utf8")) == literal_eval(expected)
    else:
        with pytest.raises(exc_type, match=expected):
            JSONBaseProvider().encode_rpc_request(
                rpc_kwargs["method"],
                rpc_kwargs["params"],
            )
