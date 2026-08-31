from eth_abi import (
    abi,
)
from eth_utils import (
    abi_to_signature,
    function_signature_to_4byte_selector,
)

from web3._utils.error_formatters_utils import (
    decode_custom_error,
)

# --- test ABIs --- #

NO_ARGS_ERROR_ABI = [
    {
        "type": "error",
        "name": "InitialEpochIsYetToArrive",
        "inputs": [],
    },
]

WITH_ARGS_ERROR_ABI = [
    {
        "type": "error",
        "name": "InsufficientBalance",
        "inputs": [
            {"name": "available", "type": "uint256"},
            {"name": "required", "type": "uint256"},
        ],
    },
]

MULTIPLE_ERRORS_ABI = [
    {
        "type": "error",
        "name": "Unauthorized",
        "inputs": [],
    },
    {
        "type": "error",
        "name": "InsufficientBalance",
        "inputs": [
            {"name": "available", "type": "uint256"},
            {"name": "required", "type": "uint256"},
        ],
    },
    {
        "type": "function",
        "name": "transfer",
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
]

MIXED_ABI_NO_ERRORS = [
    {
        "type": "function",
        "name": "transfer",
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
]


def _build_error_data(error_abi_entry):
    """Build hex-encoded revert data for a given error ABI entry with no args."""
    sig = abi_to_signature(error_abi_entry)
    selector = function_signature_to_4byte_selector(sig)
    return "0x" + selector.hex()


def _build_error_data_with_args(error_abi_entry, types, values):
    """Build hex-encoded revert data for a given error ABI entry with args."""
    sig = abi_to_signature(error_abi_entry)
    selector = function_signature_to_4byte_selector(sig)
    encoded_args = abi.encode(types, values)
    return "0x" + selector.hex() + encoded_args.hex()


class TestDecodeCustomError:
    def test_decode_no_args_error(self):
        data = _build_error_data(NO_ARGS_ERROR_ABI[0])
        result = decode_custom_error(NO_ARGS_ERROR_ABI, data)
        assert result == "InitialEpochIsYetToArrive()"

    def test_decode_error_with_args(self):
        data = _build_error_data_with_args(
            WITH_ARGS_ERROR_ABI[0],
            ["uint256", "uint256"],
            [100, 200],
        )
        result = decode_custom_error(WITH_ARGS_ERROR_ABI, data)
        assert result == "InsufficientBalance(available=100, required=200)"

    def test_decode_error_from_multiple_errors_abi(self):
        # match the second error in a mixed ABI
        data = _build_error_data_with_args(
            MULTIPLE_ERRORS_ABI[1],
            ["uint256", "uint256"],
            [50, 999],
        )
        result = decode_custom_error(MULTIPLE_ERRORS_ABI, data)
        assert result == "InsufficientBalance(available=50, required=999)"

    def test_decode_no_args_error_from_multiple(self):
        data = _build_error_data(MULTIPLE_ERRORS_ABI[0])
        result = decode_custom_error(MULTIPLE_ERRORS_ABI, data)
        assert result == "Unauthorized()"

    def test_returns_none_when_no_match(self):
        # use a selector that doesn't match any error in the ABI
        data = "0xdeadbeef"
        result = decode_custom_error(NO_ARGS_ERROR_ABI, data)
        assert result is None

    def test_returns_none_when_no_errors_in_abi(self):
        data = _build_error_data(NO_ARGS_ERROR_ABI[0])
        result = decode_custom_error(MIXED_ABI_NO_ERRORS, data)
        assert result is None

    def test_returns_none_for_short_data(self):
        result = decode_custom_error(NO_ARGS_ERROR_ABI, "0xab")
        assert result is None

    def test_returns_none_for_empty_data(self):
        result = decode_custom_error(NO_ARGS_ERROR_ABI, "0x")
        assert result is None

    def test_works_without_0x_prefix(self):
        sig = abi_to_signature(NO_ARGS_ERROR_ABI[0])
        selector = function_signature_to_4byte_selector(sig)
        data = selector.hex()  # no 0x prefix
        result = decode_custom_error(NO_ARGS_ERROR_ABI, data)
        assert result == "InitialEpochIsYetToArrive()"

    def test_returns_none_for_empty_abi(self):
        result = decode_custom_error([], "0xdeadbeef")
        assert result is None
