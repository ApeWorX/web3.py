"""Tests for w3.eth.sign_authorization() (EIP-7702 DevEx helper).

Covers both the sync Eth and async AsyncEth variants.  The helper is a
thin local-signing convenience wrapper — it does NOT send an RPC call for
the signature itself, but it *does* read chain state (chainId,
get_transaction_count) when those values are not supplied explicitly.
"""
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

import pytest

from eth_account import Account
from eth_account.datastructures import SignedSetCodeAuthorization

from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from web3.providers.eth_tester.main import AsyncEthereumTesterProvider


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

# A well-known test private key (never use in production)
_PRIVATE_KEY = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
_ACCOUNT = Account.from_key(_PRIVATE_KEY)

# A stable contract address to delegate to
_CONTRACT_ADDR = "0xaBcD000000000000000000000000000000001234"


@pytest.fixture()
def w3():
    return Web3(EthereumTesterProvider())


@pytest.fixture()
async def async_w3():
    return Web3(AsyncEthereumTesterProvider())  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# sync tests
# ---------------------------------------------------------------------------


class TestSignAuthorization:
    """Tests for Eth.sign_authorization (sync)."""

    def test_returns_signed_set_code_authorization(self, w3: Web3) -> None:
        """sign_authorization returns a SignedSetCodeAuthorization object."""
        auth = w3.eth.sign_authorization(_CONTRACT_ADDR, _PRIVATE_KEY)
        assert isinstance(auth, SignedSetCodeAuthorization)

    def test_address_matches_input(self, w3: Web3) -> None:
        """The authorization address field matches the supplied contract address."""
        auth = w3.eth.sign_authorization(_CONTRACT_ADDR, _PRIVATE_KEY)
        assert auth.address == w3.to_checksum_address(_CONTRACT_ADDR)

    def test_auto_populates_chain_id(self, w3: Web3) -> None:
        """chain_id is auto-populated from the connected network when omitted."""
        auth = w3.eth.sign_authorization(_CONTRACT_ADDR, _PRIVATE_KEY)
        assert auth.chainId == w3.eth.chain_id

    def test_explicit_chain_id_overrides_auto(self, w3: Web3) -> None:
        """An explicit chain_id kwarg is used instead of the network's chain ID."""
        auth = w3.eth.sign_authorization(
            _CONTRACT_ADDR, _PRIVATE_KEY, chain_id=999
        )
        assert auth.chainId == 999

    def test_chain_id_zero_creates_chain_agnostic_auth(self, w3: Web3) -> None:
        """chain_id=0 produces an authorization replayable on any EVM network."""
        auth = w3.eth.sign_authorization(
            _CONTRACT_ADDR, _PRIVATE_KEY, chain_id=0
        )
        assert auth.chainId == 0

    def test_auto_populates_nonce_from_tx_count(self, w3: Web3) -> None:
        """nonce defaults to the on-chain transaction count of the signing account."""
        expected_nonce = w3.eth.get_transaction_count(_ACCOUNT.address)
        auth = w3.eth.sign_authorization(_CONTRACT_ADDR, _PRIVATE_KEY)
        assert auth.nonce == expected_nonce

    def test_explicit_nonce_overrides_auto(self, w3: Web3) -> None:
        """An explicit nonce kwarg is used instead of the on-chain count."""
        auth = w3.eth.sign_authorization(
            _CONTRACT_ADDR, _PRIVATE_KEY, nonce=42
        )
        assert auth.nonce == 42

    def test_signature_fields_present(self, w3: Web3) -> None:
        """The returned auth includes signature fields (yParity, r, s)."""
        auth = w3.eth.sign_authorization(_CONTRACT_ADDR, _PRIVATE_KEY)
        assert hasattr(auth, "yParity")
        assert hasattr(auth, "r")
        assert hasattr(auth, "s")

    def test_chain_id_rpc_not_called_when_explicit(self, w3: Web3) -> None:
        """w3.eth.chain_id is NOT accessed when chain_id is supplied explicitly."""
        with patch.object(
            type(w3.eth), "chain_id", new_callable=lambda: property(MagicMock(side_effect=AssertionError("chain_id should not be called")))
        ):
            # If chain_id property were accessed, this would raise
            try:
                auth = w3.eth.sign_authorization(
                    _CONTRACT_ADDR, _PRIVATE_KEY, chain_id=1
                )
                assert auth.chainId == 1
            except AssertionError:
                pytest.fail("w3.eth.chain_id was unexpectedly accessed")

    def test_nonce_rpc_not_called_when_explicit(self, w3: Web3) -> None:
        """w3.eth.get_transaction_count is NOT called when nonce is supplied explicitly."""
        original_gtc = w3.eth.get_transaction_count
        calls = []

        def spy(*args, **kwargs):
            calls.append((args, kwargs))
            return original_gtc(*args, **kwargs)

        with patch.object(w3.eth, "get_transaction_count", side_effect=spy):
            w3.eth.sign_authorization(
                _CONTRACT_ADDR, _PRIVATE_KEY, nonce=7
            )
        assert calls == [], "get_transaction_count should not be called when nonce is explicit"

    def test_result_usable_as_authorization_list_item(self, w3: Web3) -> None:
        """The result can be placed directly in an authorizationList transaction field."""
        auth = w3.eth.sign_authorization(_CONTRACT_ADDR, _PRIVATE_KEY)
        # Build a minimal type-4 tx params dict — just checking structure
        tx_params = {
            "from": _ACCOUNT.address,
            "to": _ACCOUNT.address,
            "gas": 21000,
            "maxFeePerGas": w3.to_wei(1, "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
            "nonce": w3.eth.get_transaction_count(_ACCOUNT.address),
            "chainId": w3.eth.chain_id,
            "authorizationList": [auth],
        }
        # Just verify the dict is accepted by sign_transaction (structural test)
        signed = _ACCOUNT.sign_transaction(tx_params)
        assert signed.raw_transaction


# ---------------------------------------------------------------------------
# async tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestAsyncSignAuthorization:
    """Tests for AsyncEth.sign_authorization."""

    async def test_returns_signed_set_code_authorization(
        self, async_w3: Web3
    ) -> None:
        auth = await async_w3.eth.sign_authorization(  # type: ignore[attr-defined]
            _CONTRACT_ADDR, _PRIVATE_KEY
        )
        assert isinstance(auth, SignedSetCodeAuthorization)

    async def test_auto_populates_chain_id(self, async_w3: Web3) -> None:
        auth = await async_w3.eth.sign_authorization(  # type: ignore[attr-defined]
            _CONTRACT_ADDR, _PRIVATE_KEY
        )
        chain_id = await async_w3.eth.chain_id  # type: ignore[misc]
        assert auth.chainId == chain_id

    async def test_explicit_chain_id(self, async_w3: Web3) -> None:
        auth = await async_w3.eth.sign_authorization(  # type: ignore[attr-defined]
            _CONTRACT_ADDR, _PRIVATE_KEY, chain_id=1337
        )
        assert auth.chainId == 1337

    async def test_explicit_nonce(self, async_w3: Web3) -> None:
        auth = await async_w3.eth.sign_authorization(  # type: ignore[attr-defined]
            _CONTRACT_ADDR, _PRIVATE_KEY, nonce=5
        )
        assert auth.nonce == 5
