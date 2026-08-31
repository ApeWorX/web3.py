import pytest

from eth_utils import (
    from_wei_decimals,
    to_wei_decimals,
)
from hexbytes import (
    HexBytes,
)

from web3 import (
    Web3,
)
from web3.datastructures import (
    AttributeDict,
)


@pytest.mark.parametrize(
    "val, expected",
    (
        (b"\x01", b"\x01"),
        (b"\xff", b"\xff"),
        (b"\x00", b"\x00"),
        (0x1, b"\x01"),
        (0x0001, b"\x01"),
        (0xFF, b"\xff"),
        (0, b"\x00"),
        (256, b"\x01\x00"),
        (True, b"\x01"),
        (False, b"\x00"),
    ),
)
def test_to_bytes_primitive(val, expected):
    assert Web3.to_bytes(val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        ("0x", b""),
        ("0x0", b"\x00"),
        ("0x1", b"\x01"),
        ("0", b"\x00"),
        ("1", b"\x01"),
        ("0xFF", b"\xff"),
        ("0x100", b"\x01\x00"),
        ("0x0000", b"\x00\x00"),
        ("0000", b"\x00\x00"),
    ),
)
def test_to_bytes_hexstr(val, expected):
    assert Web3.to_bytes(hexstr=val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        ("cowmö", b"cowm\xc3\xb6"),
        ("", b""),
    ),
)
def test_to_bytes_text(val, expected):
    assert Web3.to_bytes(text=val) == expected


def test_to_text_identity():
    assert Web3.to_text(text="pass-through") == "pass-through"


@pytest.mark.parametrize(
    "val, expected",
    (
        (b"", ""),
        ("0x", ""),
        (b"cowm\xc3\xb6", "cowmö"),
        ("0x636f776dc3b6", "cowmö"),
        (0x636F776DC3B6, "cowmö"),
        ("0xa", "\n"),
    ),
)
def test_to_text(val, expected):
    assert Web3.to_text(val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        ("0x", ""),
        ("0xa", "\n"),
        ("0x636f776dc3b6", "cowmö"),
        ("636f776dc3b6", "cowmö"),
    ),
)
def test_to_text_hexstr(val, expected):
    assert Web3.to_text(hexstr=val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        (b"\x00", 0),
        (b"\x01", 1),
        (b"\x00\x01", 1),
        (b"\x01\x00", 256),
        (True, 1),
        (False, 0),
        ("255", TypeError),
        ("-1", TypeError),
        ("0x0", TypeError),
        ("0x1", TypeError),
    ),
)
def test_to_int(val, expected):
    if isinstance(expected, type):
        with pytest.raises(expected):
            Web3.to_int(val)
    else:
        assert Web3.to_int(val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        ("0", 0),
        ("-1", -1),
        ("255", 255),
        ("0x0", ValueError),
        ("0x1", ValueError),
        ("1.1", ValueError),
        ("a", ValueError),
    ),
)
def test_to_int_text(val, expected):
    if isinstance(expected, type):
        with pytest.raises(expected):
            Web3.to_int(text=val)
    else:
        assert Web3.to_int(text=val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        ("0x0", 0),
        ("0x1", 1),
        ("0x01", 1),
        ("0x10", 16),
        ("0", 0),
        ("1", 1),
        ("01", 1),
        ("10", 16),
    ),
)
def test_to_int_hexstr(val, expected):
    assert Web3.to_int(hexstr=val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        (b"\x00", "0x00"),
        (b"\x01", "0x01"),
        (b"\x10", "0x10"),
        (b"\x01\x00", "0x0100"),
        (b"\x00\x0f", "0x000f"),
        (b"", "0x"),
        (0, "0x0"),
        (1, "0x1"),
        (16, "0x10"),
        (256, "0x100"),
        (0x0, "0x0"),
        (0x0F, "0xf"),
        (False, "0x0"),
        (True, "0x1"),
    ),
)
def test_to_hex(val, expected):
    assert Web3.to_hex(val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        ("", "0x"),
        ("cowmö", "0x636f776dc3b6"),
    ),
)
def test_to_hex_text(val, expected):
    assert Web3.to_hex(text=val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        ("0x0", "0x0"),
        ("0x1", "0x1"),
        ("0x0001", "0x0001"),
        ("0x10", "0x10"),
        ("0xF", "0xf"),
        ("F", "0xf"),
    ),
)
def test_to_hex_cleanup_only(val, expected):
    assert Web3.to_hex(hexstr=val) == expected


@pytest.mark.parametrize(
    "val, expected",
    (
        (AttributeDict({"one": HexBytes("0x1")}), '{"one": "0x01"}'),
        (AttributeDict({"two": HexBytes(2)}), '{"two": "0x02"}'),
        (
            AttributeDict({"three": AttributeDict({"four": 4})}),
            '{"three": {"four": 4}}',
        ),
        ({"three": 3}, '{"three": 3}'),
    ),
)
def test_to_json(val, expected):
    assert Web3.to_json(val) == expected


@pytest.mark.parametrize(
    "tx, expected",
    (
        (
            AttributeDict(
                {
                    "blockHash": HexBytes(
                        "0x849044202a39ae36888481f90d62c3826bca8269c2716d7a38696b4f45e61d83"  # noqa: E501
                    ),
                    "blockNumber": 6928809,
                    "from": "0xDEA141eF43A2fdF4e795adA55958DAf8ef5FA619",
                    "gas": 21000,
                    "gasPrice": 19110000000,
                    "hash": HexBytes(
                        "0x1ccddd19830e998d7cf4d921b19fafd5021c9d4c4ba29680b66fb535624940fc"  # noqa: E501
                    ),
                    "input": "0x",
                    "nonce": 5522,
                    "r": HexBytes(
                        "0x71ef3eed6242230a219d9dc7737cb5a3a16059708ee322e96b8c5774105b9b00"  # noqa: E501
                    ),
                    "s": HexBytes(
                        "0x48a076afe10b4e1ae82ef82b747e9be64e0bbb1cc90e173db8d53e7baba8ac46"  # noqa: E501
                    ),
                    "to": "0x3a84E09D30476305Eda6b2DA2a4e199E2Dd1bf79",
                    "transactionIndex": 8,
                    "v": 27,
                    "value": 2907000000000000,
                }
            ),
            '{"blockHash": "0x849044202a39ae36888481f90d62c3826bca8269c2716d7a38696b4f45e61d83", "blockNumber": 6928809, "from": "0xDEA141eF43A2fdF4e795adA55958DAf8ef5FA619", "gas": 21000, "gasPrice": 19110000000, "hash": "0x1ccddd19830e998d7cf4d921b19fafd5021c9d4c4ba29680b66fb535624940fc", "input": "0x", "nonce": 5522, "r": "0x71ef3eed6242230a219d9dc7737cb5a3a16059708ee322e96b8c5774105b9b00", "s": "0x48a076afe10b4e1ae82ef82b747e9be64e0bbb1cc90e173db8d53e7baba8ac46", "to": "0x3a84E09D30476305Eda6b2DA2a4e199E2Dd1bf79", "transactionIndex": 8, "v": 27, "value": 2907000000000000}',  # noqa: E501
        ),
    ),
)
def test_to_json_with_transaction(tx, expected):
    assert Web3.to_json(tx) == expected


def test_to_wei_decimals_wiring():
    assert Web3.to_wei_decimals("1.5", 6) == to_wei_decimals("1.5", 6)
    assert Web3.to_wei_decimals(2, 6) == 2000000


def test_from_wei_decimals_wiring():
    assert Web3.from_wei_decimals(1500000, 6) == from_wei_decimals(1500000, 6)
    assert Web3.from_wei_decimals(2000000, 6) == 2
