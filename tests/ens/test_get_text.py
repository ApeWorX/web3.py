import pytest

from eth_utils import (
    ValidationError as EthUtilsValidationError,
)

from ens.exceptions import (
    ResolverNotFound,
)
from web3 import (
    Web3,
)

GET_TEXT_TEST_CASES = (
    ("avatar", "tester.jpeg"),
    ("email", "user@example.com"),
    ("url", "http://example.com"),
    ("description", "a test"),
    ("notice", "this contract is a test contract"),
)


@pytest.mark.parametrize("key,expected", GET_TEXT_TEST_CASES)
def test_set_text_resolver_not_found(ens, key, expected):
    with pytest.raises(ResolverNotFound):
        ens.set_text("tld", key, expected)


def test_set_text_fails_with_bad_address(ens):
    address = ens.w3.eth.accounts[2]
    ens.setup_address("tester.eth", address)
    zero_address = "0x" + "00" * 20
    with pytest.raises(EthUtilsValidationError):
        ens.set_text(
            "tester.eth",
            "url",
            "http://example.com",
            transact={"from": zero_address},
        )

    # teardown
    ens.setup_address("tester.eth", None)


def test_set_text_pass_in_transaction_dict(ens):
    address = ens.w3.eth.accounts[2]
    ens.setup_address("tester.eth", address)
    ens.set_text("tester.eth", "url", "http://example.com", transact={"from": address})
    ens.set_text(
        "tester.eth",
        "avatar",
        "example.jpeg",
        transact={
            "maxFeePerGas": Web3.to_wei(100, "gwei"),
            "maxPriorityFeePerGas": Web3.to_wei(100, "gwei"),
        },
    )
    assert ens.get_text("tester.eth", "url") == "http://example.com"
    assert ens.get_text("tester.eth", "avatar") == "example.jpeg"

    # teardown
    ens.setup_address("tester.eth", None)


@pytest.mark.parametrize("key,expected", GET_TEXT_TEST_CASES)
def test_get_text(ens, key, expected):
    address = ens.w3.eth.accounts[2]
    ens.setup_address("tester.eth", address)
    owner = ens.owner("tester.eth")
    assert address == owner
    ens.set_text("tester.eth", key, expected)
    assert ens.get_text("tester.eth", key) == expected

    # teardown
    ens.setup_address("tester.eth", None)


def test_get_text_resolver_not_found(ens):
    with pytest.raises(ResolverNotFound, match="No resolver found"):
        ens.get_text("tld", "any_key")


def test_get_text_when_resolver_does_not_support_text(ens):
    # With the Universal Resolver, unsupported functions raise ResolverNotFound
    # since the UR call reverts when the resolver doesn't support the function
    with pytest.raises(ResolverNotFound, match="No resolver found"):
        ens.get_text("simple-resolver.eth", "any_key")


# -- async -- #


@pytest.mark.asyncio
@pytest.mark.parametrize("key,expected", GET_TEXT_TEST_CASES)
async def test_async_set_text_resolver_not_found(async_ens, key, expected):
    with pytest.raises(ResolverNotFound):
        await async_ens.set_text("tld", key, expected)


@pytest.mark.asyncio
async def test_async_set_text_fails_with_bad_address(async_ens):
    accounts = await async_ens.w3.eth.accounts
    address = accounts[2]
    await async_ens.setup_address("tester.eth", address)
    zero_address = "0x" + "00" * 20
    with pytest.raises(EthUtilsValidationError):
        await async_ens.set_text(
            "tester.eth",
            "url",
            "http://example.com",
            transact={"from": zero_address},
        )

    # teardown
    await async_ens.setup_address("tester.eth", None)


@pytest.mark.asyncio
async def test_async_set_text_pass_in_transaction_dict(async_ens):
    accounts = await async_ens.w3.eth.accounts
    address = accounts[2]

    await async_ens.setup_address("tester.eth", address)
    await async_ens.set_text(
        "tester.eth", "url", "http://example.com", transact={"from": address}
    )
    await async_ens.set_text(
        "tester.eth",
        "avatar",
        "example.jpeg",
        transact={
            "maxFeePerGas": Web3.to_wei(100, "gwei"),
            "maxPriorityFeePerGas": Web3.to_wei(100, "gwei"),
        },
    )
    assert await async_ens.get_text("tester.eth", "url") == "http://example.com"
    assert await async_ens.get_text("tester.eth", "avatar") == "example.jpeg"

    # teardown
    await async_ens.setup_address("tester.eth", None)


@pytest.mark.asyncio
@pytest.mark.parametrize("key,expected", GET_TEXT_TEST_CASES)
async def test_async_get_text(async_ens, key, expected):
    accounts = await async_ens.w3.eth.accounts
    address = accounts[2]
    await async_ens.setup_address("tester.eth", address)
    owner = await async_ens.owner("tester.eth")
    assert address == owner
    await async_ens.set_text("tester.eth", key, expected)
    assert await async_ens.get_text("tester.eth", key) == expected

    # teardown
    await async_ens.setup_address("tester.eth", None)


@pytest.mark.asyncio
async def test_async_get_text_resolver_not_found(async_ens):
    with pytest.raises(ResolverNotFound, match="No resolver found"):
        await async_ens.get_text("tld", "any_key")


@pytest.mark.asyncio
async def test_async_get_text_when_resolver_does_not_support_text(async_ens):
    # With the Universal Resolver, unsupported functions raise ResolverNotFound
    # since the UR call reverts when the resolver doesn't support the function
    with pytest.raises(ResolverNotFound, match="No resolver found"):
        await async_ens.get_text("simple-resolver.eth", "any_key")
