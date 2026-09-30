import pytest

from eth_typing import (
    HexStr,
)
from hexbytes import (
    HexBytes,
)

from web3._utils.method_formatters import (
    PYTHONIC_RESULT_FORMATTERS,
    get_error_formatters,
    raise_contract_logic_error_on_revert,
    storage_key_to_hexstr,
)
from web3._utils.rpc_abi import (
    RPC,
)
from web3.exceptions import (
    ContractLogicError,
    Web3ValueError,
)
from web3.types import (
    RPCResponse,
)

# OpenEthereum/default case:
REVERT_WITH_MSG = RPCResponse(
    {
        "jsonrpc": "2.0",
        "error": {
            "code": -32015,
            "message": "VM execution error.",
            "data": (
                "Reverted "
                "0x08c379a"
                "00000000000000000000000000000000000000000000000000000000000000020"
                "0000000000000000000000000000000000000000000000000000000000000016"
                "6e6f7420616c6c6f77656420746f206d6f6e69746f7200000000000000000000"
            ),
        },
        "id": 2987,
    }
)

REVERT_WITHOUT_MSG = RPCResponse(
    {
        "jsonrpc": "2.0",
        "error": {
            "code": -32015,
            "message": "VM execution error.",
            "data": "Reverted 0x",
        },
        "id": 2987,
    }
)

OTHER_ERROR = RPCResponse(
    {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "Method not found",
        },
        "id": 1,
    }
)

EIP_7966_TIMEOUT_ERROR = RPCResponse(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": 4,
            "message": "timeout",
            "data": "0x" + ("12" * 32),
        },
    }
)

EIP_7966_UNKNOWN_ERROR = RPCResponse(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": 5,
            "message": "queued",
            "data": "0x" + ("34" * 32),
        },
    }
)

EIP_7966_NONCE_GAP_ERROR = RPCResponse(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": 6,
            "message": "nonce gap",
            "data": "0x5",
        },
    }
)

GETH_RESPONSE = RPCResponse(
    {
        "jsonrpc": "2.0",
        "id": 2,
        "error": {
            "code": 3,
            "message": "execution reverted: Function has been reverted.",
            "data": (
                "0x08c379a0000000000000000000000000000000000000000000000"
                "0000000000000000020000000000000000000000000000000000000"
                "000000000000000000000000001b46756e6374696f6e20686173206"
                "265656e2072657665727465642e0000000000"
            ),
        },
    }
)

GANACHE_RESPONSE = RPCResponse(
    {
        "id": 24,
        "jsonrpc": "2.0",
        "error": {
            "message": "VM Exception while processing transaction: revert Custom revert message",  # noqa: E501
            "code": -32000,
            "data": {
                "stack": "o: VM Exception while processing transaction: revert Custom revert message\n",  # noqa: E501
                "name": "o",
            },
        },
    }
)


SPACENETH_RESPONSE = RPCResponse(
    {
        "jsonrpc": "2.0",
        "error": {
            "code": -32015,
            "message": "VM execution error.",
            "data": "Reverted 0x4f776e6572496420646f6573206e6f7420657869737420696e207265676973747279",  # noqa: E501
        },
        "id": 3,
    }
)

NONE_DATA_RESPONSE = RPCResponse(
    {
        "id": 24,
        "jsonrpc": "2.0",
        "error": {
            "message": "execution reverted",
            "code": -32000,
            "data": None,
        },
    }
)

NONE_MESSAGE_RESPONSE = RPCResponse(
    {
        "id": 24,
        "jsonrpc": "2.0",
        "error": {
            "message": None,
            "code": -32000,
            "data": "execution reverted",
        },
    }
)

NO_DATA_NO_MESSAGE_RESPONSE = RPCResponse(
    {
        "id": 24,
        "jsonrpc": "2.0",
        "error": {
            "message": None,
            "code": -32000,
            "data": None,
        },
    }
)


@pytest.mark.parametrize(
    "response,expected",
    (
        (REVERT_WITH_MSG, "execution reverted: not allowed to monitor"),
        (REVERT_WITHOUT_MSG, "execution reverted"),
        (GETH_RESPONSE, "execution reverted: Function has been reverted."),
        (
            GANACHE_RESPONSE,
            "execution reverted: VM Exception while processing transaction: revert Custom revert message",  # noqa: E501
        ),
        (
            SPACENETH_RESPONSE,
            "execution reverted: OwnerId does not exist in registry",
        ),
        (
            NONE_DATA_RESPONSE,
            "execution reverted",
        ),
        (
            NONE_MESSAGE_RESPONSE,
            "execution reverted",
        ),
        (
            NO_DATA_NO_MESSAGE_RESPONSE,
            "execution reverted",
        ),
    ),
    ids=[
        "test-get-revert-reason-with-msg",
        "test-get-revert-reason-without-msg",
        "test-get-geth-revert-reason",
        "test_get-ganache-revert-reason",
        "test_get-spaceneth-revert-reason",
        "test_none-data-response",
        "test_none-message-response",
        "test_no-data-no-message-response",
    ],
)
def test_get_revert_reason(response, expected) -> None:
    with pytest.raises(ContractLogicError, match=expected):
        raise_contract_logic_error_on_revert(response)


def test_get_revert_reason_other_error() -> None:
    assert raise_contract_logic_error_on_revert(OTHER_ERROR) is OTHER_ERROR


def test_get_error_formatters() -> None:
    formatters = get_error_formatters(RPC.eth_call)
    with pytest.raises(ContractLogicError, match="not allowed to monitor"):
        formatters(REVERT_WITH_MSG)
    with pytest.raises(ContractLogicError):
        formatters(REVERT_WITHOUT_MSG)
    assert formatters(OTHER_ERROR) == OTHER_ERROR


def test_eth_send_raw_transaction_sync_result_formatter_receipt() -> None:
    receipt = {
        "transactionHash": "0x" + ("11" * 32),
        "transactionIndex": "0x0",
        "blockHash": "0x" + ("22" * 32),
        "blockNumber": "0x1",
        "cumulativeGasUsed": "0x5208",
        "gasUsed": "0x5208",
        "contractAddress": None,
        "logs": [],
        "logsBloom": "0x" + ("00" * 256),
        "status": "0x1",
        "effectiveGasPrice": "0x1",
        "type": "0x2",
    }
    formatter = PYTHONIC_RESULT_FORMATTERS[RPC.eth_sendRawTransactionSync]
    formatted_receipt = formatter(receipt)

    assert formatted_receipt["transactionHash"] == HexBytes("0x" + ("11" * 32))
    assert formatted_receipt["blockHash"] == HexBytes("0x" + ("22" * 32))
    assert formatted_receipt["blockNumber"] == 1
    assert formatted_receipt["status"] == 1
    assert formatted_receipt["gasUsed"] == 21000


@pytest.mark.parametrize(
    "error_response",
    (
        EIP_7966_TIMEOUT_ERROR,
        EIP_7966_UNKNOWN_ERROR,
        EIP_7966_NONCE_GAP_ERROR,
    ),
)
def test_eth_send_raw_transaction_sync_error_payload_passthrough(
    error_response: RPCResponse,
) -> None:
    formatter = get_error_formatters(RPC.eth_sendRawTransactionSync)
    assert formatter(error_response) == error_response


@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        ("0x" + "a" * 64, HexStr("0x" + "a" * 64)),
        ("a" * 64, HexStr("0x" + "a" * 64)),
        ("0x" + "a" * 63, Web3ValueError),
        ("a" * 63, Web3ValueError),
        (b"a" * 32, HexStr("0x" + "61" * 32)),
        (b"a" * 31, Web3ValueError),
        (b"a" * 33, Web3ValueError),
        (
            7719472615821079694904732333912527190217998977709370935963838933860875309329,  # noqa: E501
            HexStr("0x" + "1" * 64),
        ),
        (3567, Web3ValueError),
        (3.14, Web3ValueError),
    ],
    ids=[
        "valid-0x-hex-string",
        "valid-no-0x-hex-string",
        "invalid-0x-hex-string",
        "invalid-no-0x-hex-string",
        "valid-32-byte-value",
        "invalid-31-byte-value",
        "invalid-33-byte-value",
        "valid-integer",
        "invalid-integer",
        "invalid-float",
    ],
)
def test_storage_key_to_hexstr(input_value, expected_output):
    if isinstance(expected_output, type) and issubclass(expected_output, Exception):
        with pytest.raises(expected_output):
            storage_key_to_hexstr(input_value)
    else:
        assert storage_key_to_hexstr(input_value) == expected_output
