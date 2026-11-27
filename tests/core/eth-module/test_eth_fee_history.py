import pytest
from unittest.mock import (
    MagicMock,
    patch,
)


@pytest.mark.parametrize(
    "fee_history_args, expected",
    (
        ((1, "latest"), (1, "latest", [])),
        ((1, "latest", []), (1, "latest", [])),
        ((1, "latest", None), (1, "latest", [])),
        ((1, "latest", [50]), (1, "latest", [50])),
    ),
)
@patch("web3.eth.Eth._fee_history", new=MagicMock())
def test_eth_fee_history_reward_percentiles_default_is_empty_list(
    w3, fee_history_args, expected
) -> None:
    w3.eth.fee_history(*fee_history_args)
    w3.eth._fee_history.assert_called_with(*expected)


def test_eth_fee_history_formats_blob_fee_fields(w3, request_mocker) -> None:
    with request_mocker(
        w3,
        mock_results={
            "eth_feeHistory": {
                "oldestBlock": "0x194824f",
                "reward": [["0x17ba38"], ["0x17ba38"]],
                "baseFeePerGas": ["0x2cfd09f", "0x2b6d3c1", "0x2c19b88"],
                "gasUsedRatio": [0.36114335, 0.5620608],
                "baseFeePerBlobGas": ["0x2cbd59", "0x2d69f0", "0x2d69f0"],
                "blobGasUsedRatio": [0, 0.6666666666666666],
            }
        },
    ):
        fee_history = w3.eth.fee_history(2, "latest", [50])

    assert fee_history["baseFeePerGas"] == [47173791, 45536193, 46242696]
    assert fee_history["baseFeePerBlobGas"] == [2932057, 2976240, 2976240]
    assert fee_history["blobGasUsedRatio"] == [0.0, 0.6666666666666666]
    assert all(isinstance(ratio, float) for ratio in fee_history["blobGasUsedRatio"])


def test_eth_fee_history_null_blob_fee_fields(w3, request_mocker) -> None:
    with request_mocker(
        w3,
        mock_results={
            "eth_feeHistory": {
                "oldestBlock": "0x3",
                "baseFeePerGas": ["0x7", "0x7"],
                "gasUsedRatio": [0.5],
                "baseFeePerBlobGas": None,
                "blobGasUsedRatio": None,
            }
        },
    ):
        fee_history = w3.eth.fee_history(1, "latest")

    assert fee_history["baseFeePerGas"] == [7, 7]
    assert fee_history["baseFeePerBlobGas"] is None
    assert fee_history["blobGasUsedRatio"] is None
