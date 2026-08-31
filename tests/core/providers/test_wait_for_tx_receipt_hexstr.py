from hexbytes import HexBytes
import pytest
from web3 import Web3
from web3.exceptions import TimeExhausted

def _send_dummy_tx(w3: Web3):
    a0, a1 = w3.eth.accounts[:2]
    tx_hash = w3.eth.send_transaction({"from": a0, "to": a1, "value": 1})
    return tx_hash

def test_wait_for_tx_receipt_accepts_hex_string_success():
    w3 = Web3(Web3.EthereumTesterProvider())
    tx_hash = _send_dummy_tx(w3)
    tx_hash_hexstr = tx_hash.hex()

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash_hexstr, timeout=60)
    assert receipt is not None
    assert receipt["transactionHash"] in (tx_hash, HexBytes(tx_hash_hexstr))

def test_wait_for_tx_receipt_accepts_hex_string_timeout():
    w3 = Web3(Web3.EthereumTesterProvider())

    # Use a bogus tx hash (never mined) to force timeout
    bogus_hex = "0x" + "00" * 32

    # Very short timeout so it raises quickly
    with pytest.raises(TimeExhausted):
        w3.eth.wait_for_transaction_receipt(
            bogus_hex,
            timeout=0.1,
            poll_latency=0.05,
        )

