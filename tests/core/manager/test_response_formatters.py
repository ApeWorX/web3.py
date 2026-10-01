import pytest
import re

from eth_utils.toolz import (
    identity,
    merge,
)

from web3._utils.method_formatters import (
    raise_block_not_found,
    raise_block_not_found_for_uncle_at_index,
    raise_transaction_not_found,
)
from web3.exceptions import (
    BadResponseFormat,
    BlockNotFound,
    ContractLogicError,
    MethodUnavailable,
    RequestTimedOut,
    TransactionNotFound,
    Web3RPCError,
)

DEFAULT_BAD_FORMAT_MSG = (
    "The response was in an unexpected format and unable to be parsed."
)
INVALID_JSONRPC_MSG = 'The "jsonrpc" field must be present with a value of "2.0".'
ERROR_OBJ_MSG = (
    'response["error"] must be a valid object as defined by the JSON-RPC '
    "2.0 specification."
)
INVALID_ERROR_CODE_MSG = 'error["code"] is required and must be an integer value.'
INVALID_ERROR_MESSAGE_MSG = 'error["message"] is required and must be a string value.'
METHOD_UNAVAILABLE_MSG = (
    "the method eth_getTransactionByHash does not exist/is not available."
)


VALID_RESULT_OBJ_RESPONSE = {"jsonrpc": "2.0", "id": 1, "result": {"foo": "bar"}}
VALID_RESPONSE_EXTRA_FIELDS = merge(VALID_RESULT_OBJ_RESPONSE, {"unexpected": "field"})
VALID_RESPONSE_STRING_ID = merge(VALID_RESULT_OBJ_RESPONSE, {"id": "1"})

# response fields validation: id, jsonrpc, missing result / error
INVALID_RESPONSE_INVALID_ID = merge(VALID_RESULT_OBJ_RESPONSE, {"id": None})
INVALID_RESPONSE_MISSING_ID = {"jsonrpc": "2.0", "result": {"foo": "bar"}}

INVALID_RESPONSE_INVALID_JSONRPC = merge(VALID_RESULT_OBJ_RESPONSE, {"jsonrpc": "1.0"})
INVALID_RESPONSE_MISSING_JSONRPC = {"id": 1, "result": {"foo": "bar"}}

INVALID_RESPONSE_MISSING_RESULT_OR_ERROR = {"jsonrpc": "2.0", "id": 1}


# valid subscription response
VALID_SUBSCRIPTION_RESPONSE = {
    "jsonrpc": "2.0",
    "method": "eth_subscription",
    "params": {
        "subscription": "0xf13f7073ddef66a8c1b0c9c9f0e543c3",
        "result": {"foo": "bar"},
    },
}

# error object validation
VALID_ERROR_RESPONSE = {
    "jsonrpc": "2.0",
    "id": 1,
    "error": {
        "code": -32000,
        "message": (
            "Requested block number is in a range that is not available yet, because "
            "the ancient block sync is still in progress."
        ),
    },
}
ERROR_RESPONSE_VALID_ID_STRING = merge(VALID_ERROR_RESPONSE, {"id": "1"})
ERROR_RESPONSE_VALID_ID_NONE = merge(VALID_ERROR_RESPONSE, {"id": None})
ERROR_RESPONSE_VALID_METHOD_UNAVAILABLE = merge(
    VALID_ERROR_RESPONSE,
    {"error": {"code": -32601, "message": (METHOD_UNAVAILABLE_MSG)}},
)
ERROR_RESPONSE_REQUEST_TIMED_OUT = merge(
    VALID_ERROR_RESPONSE,
    {"error": {"code": -32002, "message": "Request timed out."}},
)
ERROR_RESPONSE_INVALID_ID = merge(VALID_ERROR_RESPONSE, {"id": b"invalid"})

ERROR_RESPONSE_INVALID_CODE = merge(
    VALID_ERROR_RESPONSE, {"error": {"code": "-32601", "message": ""}}
)
ERROR_RESPONSE_INVALID_MISSING_CODE = merge(
    VALID_ERROR_RESPONSE, {"error": {"message": "msg"}}
)

ERROR_RESPONSE_INVALID_MESSAGE = merge(
    VALID_ERROR_RESPONSE, {"error": {"code": -32000, "message": {}}}
)
ERROR_RESPONSE_INVALID_MISSING_MESSAGE = merge(
    VALID_ERROR_RESPONSE, {"error": {"code": -32000}}
)

ERROR_RESPONSE_INVALID_ERROR_OBJECT = merge(
    VALID_ERROR_RESPONSE, {"error": METHOD_UNAVAILABLE_MSG}
)

# result object validation
VALID_RESPONSE_NULL_RESULT = merge(VALID_RESULT_OBJ_RESPONSE, {"result": None})
VALID_RESPONSE_0x_RESULT = merge(VALID_RESULT_OBJ_RESPONSE, {"result": "0x"})


def raise_contract_logic_error(_response):
    raise ContractLogicError("Test contract logic error.")


@pytest.mark.parametrize(
    "response,expected",
    (
        (VALID_RESULT_OBJ_RESPONSE, VALID_RESULT_OBJ_RESPONSE["result"]),
        (VALID_RESPONSE_STRING_ID, VALID_RESPONSE_STRING_ID["result"]),
        # extra fields are ignored
        (VALID_RESPONSE_EXTRA_FIELDS, VALID_RESPONSE_EXTRA_FIELDS["result"]),
        # Response with null result doesn't raise w/o null result formatters
        (VALID_RESPONSE_NULL_RESULT, VALID_RESPONSE_NULL_RESULT["result"]),
        # Response with a result of '0x' doesn't raise w/o null result formatters
        (VALID_RESPONSE_0x_RESULT, VALID_RESPONSE_0x_RESULT["result"]),
        # Subscription response
        (VALID_SUBSCRIPTION_RESPONSE, VALID_SUBSCRIPTION_RESPONSE["params"]),
    ),
)
def test_formatted_response_valid_response_object(w3, response, expected):
    formatted_resp = w3.manager.formatted_response(response, (), identity, identity)
    assert formatted_resp == expected


@pytest.mark.parametrize(
    "response,error,error_message",
    [
        (
            INVALID_RESPONSE_INVALID_JSONRPC,
            BadResponseFormat,
            f"{DEFAULT_BAD_FORMAT_MSG} {INVALID_JSONRPC_MSG} "
            f"The raw response is: {INVALID_RESPONSE_INVALID_JSONRPC}",
        ),
        (
            INVALID_RESPONSE_MISSING_JSONRPC,
            BadResponseFormat,
            f"{DEFAULT_BAD_FORMAT_MSG} {INVALID_JSONRPC_MSG} "
            f"The raw response is: {INVALID_RESPONSE_MISSING_JSONRPC}",
        ),
        (
            INVALID_RESPONSE_INVALID_ID,
            BadResponseFormat,
            f'{DEFAULT_BAD_FORMAT_MSG} "id" must be an integer or a string '
            "representation of an integer. The raw response is: "
            f"{INVALID_RESPONSE_INVALID_ID}",
        ),
        (
            INVALID_RESPONSE_MISSING_ID,
            BadResponseFormat,
            f'{DEFAULT_BAD_FORMAT_MSG} Response must include an "id" field or be '
            "formatted as an `eth_subscription` response. The raw response is: "
            f"{INVALID_RESPONSE_MISSING_ID}",
        ),
        (
            INVALID_RESPONSE_MISSING_RESULT_OR_ERROR,
            BadResponseFormat,
            f'{DEFAULT_BAD_FORMAT_MSG} Response must include either "error" or '
            '"result". The raw response is: '
            f"{INVALID_RESPONSE_MISSING_RESULT_OR_ERROR}",
        ),
    ],
)
def test_formatted_response_invalid_response_object(w3, response, error, error_message):
    with pytest.raises(error, match=re.escape(error_message)):
        w3.manager.formatted_response(response, (), identity, identity)


@pytest.mark.parametrize(
    "response,error,error_message",
    (
        (
            VALID_ERROR_RESPONSE,
            Web3RPCError,
            f"{VALID_ERROR_RESPONSE['error']}",
        ),
        (
            ERROR_RESPONSE_VALID_ID_STRING,
            Web3RPCError,
            f"{ERROR_RESPONSE_VALID_ID_STRING['error']}",
        ),
        (
            ERROR_RESPONSE_VALID_ID_NONE,
            Web3RPCError,
            f"{ERROR_RESPONSE_VALID_ID_NONE['error']}",
        ),
        (
            ERROR_RESPONSE_VALID_METHOD_UNAVAILABLE,
            MethodUnavailable,
            METHOD_UNAVAILABLE_MSG,
        ),
        (
            ERROR_RESPONSE_REQUEST_TIMED_OUT,
            RequestTimedOut,
            f"{ERROR_RESPONSE_REQUEST_TIMED_OUT['error']}",
        ),
    ),
)
def test_formatted_response_valid_error_object(response, w3, error, error_message):
    with pytest.raises(error, match=re.escape(error_message)):
        w3.manager.formatted_response(response, (), identity, identity)


@pytest.mark.parametrize(
    "response,null_result_formatters,error,error_message",
    [
        (
            ERROR_RESPONSE_INVALID_CODE,
            identity,
            BadResponseFormat,
            f"{DEFAULT_BAD_FORMAT_MSG} {INVALID_ERROR_CODE_MSG} "
            f"The raw response is: {ERROR_RESPONSE_INVALID_CODE}",
        ),
        (
            ERROR_RESPONSE_INVALID_MISSING_CODE,
            identity,
            BadResponseFormat,
            f"{DEFAULT_BAD_FORMAT_MSG} {INVALID_ERROR_CODE_MSG} "
            f"The raw response is: {ERROR_RESPONSE_INVALID_MISSING_CODE}",
        ),
        (
            ERROR_RESPONSE_INVALID_MESSAGE,
            identity,
            BadResponseFormat,
            f"{DEFAULT_BAD_FORMAT_MSG} {INVALID_ERROR_MESSAGE_MSG} "
            f"The raw response is: {ERROR_RESPONSE_INVALID_MESSAGE}",
        ),
        (
            ERROR_RESPONSE_INVALID_MISSING_MESSAGE,
            identity,
            BadResponseFormat,
            f"{DEFAULT_BAD_FORMAT_MSG} {INVALID_ERROR_MESSAGE_MSG} "
            f"The raw response is: {ERROR_RESPONSE_INVALID_MISSING_MESSAGE}",
        ),
        (
            ERROR_RESPONSE_INVALID_ID,
            identity,
            BadResponseFormat,
            f'{DEFAULT_BAD_FORMAT_MSG} "id" must be an integer or a string '
            "representation of an integer. "
            f"The raw response is: {ERROR_RESPONSE_INVALID_ID}",
        ),
        (
            ERROR_RESPONSE_INVALID_ERROR_OBJECT,
            identity,
            BadResponseFormat,
            f"{DEFAULT_BAD_FORMAT_MSG} {ERROR_OBJ_MSG} The raw response is: "
            f"{ERROR_RESPONSE_INVALID_ERROR_OBJECT}",
        ),
        (
            # Invalid error response w/ null result formatters raises on invalid format
            ERROR_RESPONSE_INVALID_ERROR_OBJECT,  # raises on invalid error object
            raise_block_not_found,  # does not raise `BlockNotFound`
            BadResponseFormat,
            f"{DEFAULT_BAD_FORMAT_MSG} {ERROR_OBJ_MSG} The raw response is: "
            f"{ERROR_RESPONSE_INVALID_ERROR_OBJECT}",
        ),
    ],
)
def test_formatted_response_invalid_error_object(
    response, w3, null_result_formatters, error, error_message
):
    with pytest.raises(error, match=re.escape(error_message)):
        w3.manager.formatted_response(response, (), identity, null_result_formatters)


@pytest.mark.parametrize(
    "error_formatters,null_result_formatters,error,error_message",
    (
        (
            # Valid error response with error formatters raises error in formatter
            raise_contract_logic_error,
            identity,
            ContractLogicError,
            "Test contract logic error.",
        ),
        (
            # Non-null valid error response with no error formatters and null result
            # formatters raises generic `Web3RPCError`, not `BlockNotFound`
            identity,
            raise_block_not_found,
            Web3RPCError,
            f"{VALID_ERROR_RESPONSE['error']}",
        ),
    ),
)
def test_formatted_response_error_responses_with_formatters_raise_expected_exceptions(
    w3, error_formatters, null_result_formatters, error, error_message
):
    with pytest.raises(error, match=re.escape(error_message)):
        w3.manager.formatted_response(
            VALID_ERROR_RESPONSE, (), error_formatters, null_result_formatters
        )


@pytest.mark.parametrize(
    "params,null_result_formatters,error,error_message",
    (
        # raise via null_result_formatters
        (
            (),
            # test raise_block_not_found
            raise_block_not_found,
            BlockNotFound,
            "Unknown block identifier",
        ),
        (
            ("0x03",),  # test with param
            # test raise_block_not_found
            raise_block_not_found,
            BlockNotFound,
            "Block with id: '0x03' not found.",
        ),
        (
            (),
            # test raise_block_not_found_for_uncle_at_index
            raise_block_not_found_for_uncle_at_index,
            BlockNotFound,
            "Unknown block identifier or uncle index",
        ),
        (
            ("0x01",),  # test handles missing param
            # test raise_block_not_found_for_uncle_at_index
            raise_block_not_found_for_uncle_at_index,
            BlockNotFound,
            "Unknown block identifier or uncle index",
        ),
        (
            ("0x01", "0x00"),  # both params
            # test raise_block_not_found_for_uncle_at_index
            raise_block_not_found_for_uncle_at_index,
            BlockNotFound,
            "Uncle at index: 0 of block with id: '0x01' not found.",
        ),
        (
            (),
            # test raise_transaction_not_found
            raise_transaction_not_found,
            TransactionNotFound,
            "Unknown transaction hash",
        ),
        (
            ("0x01",),
            # test raise_transaction_not_found
            raise_transaction_not_found,
            TransactionNotFound,
            "Transaction with hash: '0x01' not found.",
        ),
    ),
)
def test_formatted_response_null_and_0x_results_with_formatters(
    w3, params, null_result_formatters, error, error_message
):
    with pytest.raises(error, match=re.escape(error_message)):
        # test null result response
        w3.manager.formatted_response(
            VALID_RESPONSE_NULL_RESULT, params, identity, null_result_formatters
        )

    with pytest.raises(error, match=re.escape(error_message)):
        # test 0x result response
        w3.manager.formatted_response(
            VALID_RESPONSE_0x_RESULT, params, identity, null_result_formatters
        )
