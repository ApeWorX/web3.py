import pytest

from hexbytes import (
    HexBytes,
)

from web3.utils.transaction import (
    Web3Transaction,
)

ACCESS_LIST_TRANSACTION_TEST_CASE = {
    "expected_raw_transaction": "0x01f8e782076c22843b9aca00830186a09409616c3d61b3331fc4109a9e41a8bdb7d9776609865af3107a400086616263646566f872f85994de0b295669a9fd93d5f28d9ec85e40f4cb697baef842a00000000000000000000000000000000000000000000000000000000000000003a00000000000000000000000000000000000000000000000000000000000000007d694bb9bc244d798123fde783fcc1c72d3bb8c189413c001a08289e85fa00f8f7f78a53cf147a87b2a7f0d27e64d7571f9d06a802e365c3430a017dc77eae36c88937db4a5179f57edc6119701652f3f1c6f194d1210d638a061",  # noqa: 501
    "transaction": {
        "gas": "0x186a0",
        "gasPrice": "0x3b9aca00",
        "data": "0x616263646566",
        "nonce": "0x22",
        "to": "0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
        "value": "0x5af3107a4000",
        "accessList": (  # test case from EIP-2930
            {
                "address": "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae",
                "storageKeys": (
                    "0x0000000000000000000000000000000000000000000000000000000000000003",  # noqa: E501
                    "0x0000000000000000000000000000000000000000000000000000000000000007",  # noqa: E501
                ),
            },
            {
                "address": "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
                "storageKeys": (),
            },
        ),
        "chainId": "0x76c",
        "v": "0x1",
        "r": "0x8289e85fa00f8f7f78a53cf147a87b2a7f0d27e64d7571f9d06a802e365c3430",
        "s": "0x17dc77eae36c88937db4a5179f57edc6119701652f3f1c6f194d1210d638a061",
    },
}
DYNAMIC_FEE_TRANSACTION_TEST_CASE = {
    "expected_raw_transaction": "0x02f8758205390284773594008477359400830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544c001a0c3000cd391f991169ebfd5d3b9e93c89d31a61c998a21b07a11dc6b9d66f8a8ea022cfe8424b2fbd78b16c9911da1be2349027b0a3c40adf4b6459222323773f74",  # noqa: 501
    "transaction": {
        "gas": "0x186a0",
        "maxFeePerGas": "0x77359400",
        "maxPriorityFeePerGas": "0x77359400",
        "data": "0x5544",
        "nonce": "0x2",
        "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
        "value": "0x5af3107a4000",
        "type": "0x2",
        "chainId": "0x539",
        "accessList": (),
        "v": "0x1",
        "r": "0xc3000cd391f991169ebfd5d3b9e93c89d31a61c998a21b07a11dc6b9d66f8a8e",
        "s": "0x22cfe8424b2fbd78b16c9911da1be2349027b0a3c40adf4b6459222323773f74",
    },
}


@pytest.mark.parametrize(
    "txn",
    [
        Web3Transaction.from_dict(ACCESS_LIST_TRANSACTION_TEST_CASE["transaction"]),
        Web3Transaction.from_bytes(
            HexBytes(ACCESS_LIST_TRANSACTION_TEST_CASE["expected_raw_transaction"])
        ),
    ],
)
def test_access_list_transaction(txn):
    assert txn.typed_transaction.transaction_type == 1
    assert txn.chain_id == 1_900
    assert txn.nonce == 34
    assert txn.gas == 100_000
    assert txn.to == b"\tal=a\xb33\x1f\xc4\x10\x9a\x9eA\xa8\xbd\xb7\xd9wf\t"
    assert txn.value == 100_000_000_000_000
    assert txn.data == b"abcdef"
    assert txn.gas_price == 1_000_000_000


def test_encode_access_list_transaction():
    txn = Web3Transaction.from_dict(ACCESS_LIST_TRANSACTION_TEST_CASE["transaction"])
    assert txn.encode() == HexBytes(
        ACCESS_LIST_TRANSACTION_TEST_CASE["expected_raw_transaction"]
    )


@pytest.mark.parametrize(
    "txn",
    [
        Web3Transaction.from_dict(DYNAMIC_FEE_TRANSACTION_TEST_CASE["transaction"]),
        Web3Transaction.from_bytes(
            HexBytes(DYNAMIC_FEE_TRANSACTION_TEST_CASE["expected_raw_transaction"])
        ),
    ],
)
def test_dynamic_fee_transaction(txn):
    assert txn.typed_transaction.transaction_type == 2
    assert txn.chain_id == 1_337
    assert txn.nonce == 2
    assert txn.gas == 100_000
    assert txn.to == b"\x96!hI\xc4\x93X\xb1\x02W\xcbU\xb2\x8e\xa6\x03\xc8t\xb0^"
    assert txn.value == 100_000_000_000_000
    assert txn.data == b"UD"
    assert txn.max_priority_fee_per_gas == 2_000_000_000
    assert txn.max_fee_per_gas == 2_000_000_000


def test_encode_dynamic_fee_transaction():
    txn = Web3Transaction.from_dict(DYNAMIC_FEE_TRANSACTION_TEST_CASE["transaction"])
    assert txn.encode() == HexBytes(
        DYNAMIC_FEE_TRANSACTION_TEST_CASE["expected_raw_transaction"]
    )
