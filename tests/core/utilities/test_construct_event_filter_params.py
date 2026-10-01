import pytest

from web3._utils.filters import (
    construct_event_filter_params,
)
from web3.exceptions import (
    InvalidAddress,
    Web3ValueError,
)


def hex_and_pad(i):
    unpadded_hex_value = hex(i).rstrip("L")
    return "0x" + unpadded_hex_value[2:].zfill(64)


@pytest.fixture
def event_abi():
    return {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "name": "arg0", "type": "uint256"},
            {"indexed": True, "name": "arg1", "type": "uint256"},
        ],
        "name": "Event_1",
        "type": "event",
    }


@pytest.mark.parametrize(
    "fn_kwargs,expected",
    (
        pytest.param(
            {},
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
            },
            id="no-args",
        ),
        pytest.param(
            {"topics": ["should-overwrite-topics"]},
            {"topics": ["should-overwrite-topics"]},
            id="overwrite-topics",
        ),
        pytest.param(
            {"address": None},
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
            },
            id="no-address",
        ),
        pytest.param(
            {"contract_address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601"},
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
            },
            id="contract_address-string",
        ),
        pytest.param(
            {
                "contract_address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                "address": "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            },
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": [
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                ],
            },
            id="address-with-contract_address",
        ),
        pytest.param(
            {
                "contract_address": ["0xd3CdA913deB6f67967B99D67aCDFa1712C293601"],
                "address": ["0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413"],
            },
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": [
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                ],
            },
            id="single-item-address-list-with-contract_address-list",
        ),
        pytest.param(
            {"address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601"},
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
            },
            id="address-string",
        ),
        pytest.param(
            {"address": b"\xf2\xe2F\xbbv\xdf\x87l\xef\x8b8\xae\x84\x13\x0fOU\xde9["},
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": b"\xf2\xe2F\xbbv\xdf\x87l\xef\x8b8\xae\x84\x13\x0fOU\xde9[",
            },
            id="address-bytes",
        ),
        pytest.param(
            {
                "contract_address": b"\xf2\xe2F\xbbv\xdf\x87l\xef\x8b8\xae\x84\x13\x0fOU\xde9[",  # noqa: E501
                "address": [
                    b"\xf2\xe2F\xbbv\xdf\x87l\xef\x8b8\xae\x84\x13\x0fOU\xde9[",
                    b"\xf2\xe2F\xbbv\xdf\x87l\xef\x8b8\xae\x84\x13\x0fOU\xde9[",
                ],
            },
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": b"\xf2\xe2F\xbbv\xdf\x87l\xef\x8b8\xae\x84\x13\x0fOU\xde9[",
            },
            id="address-bytes-list",
        ),
        pytest.param(
            {"address": ["0xd3CdA913deB6f67967B99D67aCDFa1712C293601"]},
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
            },
            id="address-list",
        ),
        pytest.param(
            {
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0x1234567890123456789012345678901234567890",
                ]
            },
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0x1234567890123456789012345678901234567890",
                ],
            },
            id="multiple-address",
        ),
        pytest.param(
            {
                "address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                "contract_address": ["0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413"],
            },
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                ],
            },
            id="one-address-with-multiple-contract_address",
        ),
        pytest.param(
            {
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0x1234567890123456789012345678901234567890",
                ],
                "contract_address": "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
            },
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0x1234567890123456789012345678901234567890",
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                ],
            },
            id="multiple-address-with-one-contract_address",
        ),
        pytest.param(
            {
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0x1234567890123456789012345678901234567890",
                ],
                "contract_address": [
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                    "0x1234567890123456789012345678901234567890",
                ],
            },
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0x1234567890123456789012345678901234567890",
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                ],
            },
            id="multiple-address-with-multiple-contract_address",
        ),
        pytest.param(
            {
                "contract_address": "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "from_block": "latest",
                "to_block": "latest",
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0x1234567890123456789012345678901234567890",
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                ],
            },
            {
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": [
                    "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "0x1234567890123456789012345678901234567890",
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                ],
                "fromBlock": "latest",
                "toBlock": "latest",
            },
            id="all-arguments-with-address-list",
        ),
    ),
)
def test_construct_event_filter_params(w3, event_abi, fn_kwargs, expected):
    _, filter_params = construct_event_filter_params(event_abi, w3.codec, **fn_kwargs)
    # Ensure that the filter_params contains the expected keys
    assert filter_params.keys() == expected.keys(), (
        f"Keys don't match. Expected {set(expected.keys())}, got {set(filter_params.keys())}"
    )  # noqa: E501
    # Verify all values in filter_params match the expected values
    for key, value in expected.items():
        if isinstance(value, list) and isinstance(filter_params[key], list):
            assert sorted(filter_params[key]) == sorted(value), (
                f"Expected {key}={value}, got {key}={filter_params.get(key)}"
            )
        else:
            assert filter_params[key] == value, (
                f"Expected {key}={value}, got {key}={filter_params.get(key)}"
            )


@pytest.mark.parametrize(
    "fn_kwargs, expected_exception",
    [
        pytest.param(
            {
                "contract_address": "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
                "topics": [
                    "0xb470a829ed7792f06947f0ca3730a570cb378329ddcf09f2b4efabd6326f51f6"
                ],
                "address": [
                    "0xd3cda913deb6f67967b99d67acdfa1712c293601",
                    "0x1234567890123456789012345678901234567890",
                    "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                ],
                "from_block": 1,
                "to_block": 2,
            },
            InvalidAddress,
            id="invalid-checksum-address",
        ),
        pytest.param(
            {
                "contract_address": "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
            },
            InvalidAddress,
            id="invalid-checksum-contract-address",
        ),
        pytest.param(
            {"address": {"invalid": "0x1234567890123456789012345678901234567890"}},
            Web3ValueError,
            id="unsupported-type-exception",
        ),
    ],
)
def test_construct_event_filter_params_exceptions(
    w3, event_abi, fn_kwargs, expected_exception
):
    with pytest.raises(expected_exception):
        construct_event_filter_params(event_abi, w3.codec, **fn_kwargs)


@pytest.mark.parametrize(
    "fn_kwargs,expected",
    (
        ({}, [[]]),
        ({"argument_filters": {"arg0": 1}}, [[hex_and_pad(1)]]),
        ({"argument_filters": {"arg0": [1]}}, [[hex_and_pad(1)]]),
        (
            {"argument_filters": {"arg0": [1, 2]}},
            [
                [hex_and_pad(1)],
                [hex_and_pad(2)],
            ],
        ),
    ),
)
def test_construct_event_filter_params_for_data_filters(
    w3, event_abi, fn_kwargs, expected
):
    actual, _ = construct_event_filter_params(event_abi, w3.codec, **fn_kwargs)
    assert actual == expected
