import pytest

from web3._utils.contract_sources.contract_data.e_r_c_721_token_uri import (
    E_R_C721_TOKEN_URI_ABI,
    E_R_C721_TOKEN_URI_BYTECODE,
    E_R_C721_TOKEN_URI_RUNTIME,
)
from web3._utils.contract_sources.contract_data.e_r_c_1155_token_uri import (
    E_R_C1155_TOKEN_URI_ABI,
    E_R_C1155_TOKEN_URI_BYTECODE,
    E_R_C1155_TOKEN_URI_RUNTIME,
)


def test_get_avatar_image_uri_from_erc721(ens):
    plain_image_uri = "https://euc.li/vitalik.eth"
    address = ens.w3.eth.accounts[2]
    tx_hash = (
        ens.w3.eth.contract(
            bytecode=E_R_C721_TOKEN_URI_BYTECODE,
            bytecode_runtime=E_R_C721_TOKEN_URI_RUNTIME,
            abi=E_R_C721_TOKEN_URI_ABI,
        )
        .constructor()
        .transact({"from": address})
    )
    assert tx_hash
    tx_receipt = ens.w3.eth.wait_for_transaction_receipt(tx_hash)
    assert tx_receipt
    erc721_resolver = ens.w3.eth.contract(
        address=tx_receipt.contractAddress, abi=E_R_C721_TOKEN_URI_ABI
    )
    update_uri_hash = erc721_resolver.functions.setUri(plain_image_uri).transact(
        {"from": address}
    )
    assert update_uri_hash
    assert ens.w3.eth.wait_for_transaction_receipt(update_uri_hash)
    avatar_uri = f"eip155:1/erc721:{erc721_resolver.address}/81123"
    ens.setup_address("tester.eth", address)
    ens.set_text("tester.eth", "avatar", avatar_uri, transact={"from": address})
    assert ens.get_avatar("tester.eth") == plain_image_uri
    # clean up
    ens.setup_address("tester.eth", None)


def test_get_avatar_image_uri_from_erc1155(ens):
    plain_image_uri = "https://euc.li/vitalik.eth"
    address = ens.w3.eth.accounts[2]
    tx_hash = (
        ens.w3.eth.contract(
            bytecode=E_R_C1155_TOKEN_URI_BYTECODE,
            bytecode_runtime=E_R_C1155_TOKEN_URI_RUNTIME,
            abi=E_R_C1155_TOKEN_URI_ABI,
        )
        .constructor()
        .transact({"from": address})
    )
    assert tx_hash
    tx_receipt = ens.w3.eth.wait_for_transaction_receipt(tx_hash)
    assert tx_receipt
    erc1155_resolver = ens.w3.eth.contract(
        address=tx_receipt.contractAddress, abi=E_R_C1155_TOKEN_URI_ABI
    )
    update_uri_hash = erc1155_resolver.functions.setUri(plain_image_uri).transact(
        {"from": address}
    )
    assert update_uri_hash
    assert ens.w3.eth.wait_for_transaction_receipt(update_uri_hash)
    avatar_uri = f"eip155:1/erc1155:{erc1155_resolver.address}/81123167"
    ens.setup_address("tester.eth", address)
    ens.set_text("tester.eth", "avatar", avatar_uri, transact={"from": address})
    assert ens.get_avatar("tester.eth") == plain_image_uri
    # clean up
    ens.setup_address("tester.eth", None)


def test_get_avatar_image_uri_without_gateway(ens):
    plain_image_uri = "https://euc.li/vitalik.eth"
    accounts = ens.w3.eth.accounts
    address = accounts[2]
    ens.setup_address("tester.eth", address)
    ens.set_text("tester.eth", "avatar", plain_image_uri, transact={"from": address})
    assert ens.get_avatar("tester.eth") == plain_image_uri
    # clean up
    ens.setup_address("tester.eth", None)


def test_get_avatar_for_uri_with_unparsable_uri(ens):
    with pytest.raises(ValueError):
        badly_formated_uri = "euc.li/vitalik.eth"
        address = ens.w3.eth.accounts[2]
        ens.setup_address("tester.eth", address)
        ens.set_text(
            "tester.eth", "avatar", badly_formated_uri, transact={"from": address}
        )
        ens.get_avatar("tester.eth")


@pytest.mark.asyncio
async def test_async_get_avatar_image_uri_from_erc721(async_ens):
    plain_image_uri = "https://euc.li/vitalik.eth"
    accounts = await async_ens.w3.eth.accounts
    address = accounts[2]

    tx_hash = (
        await async_ens.w3.eth.contract(
            bytecode=E_R_C721_TOKEN_URI_BYTECODE,
            bytecode_runtime=E_R_C721_TOKEN_URI_RUNTIME,
            abi=E_R_C721_TOKEN_URI_ABI,
        )
        .constructor()
        .transact({"from": address})
    )
    assert tx_hash is not None
    tx_receipt = await async_ens.w3.eth.wait_for_transaction_receipt(tx_hash)
    assert tx_receipt is not None
    erc721_resolver = async_ens.w3.eth.contract(
        address=tx_receipt.contractAddress, abi=E_R_C721_TOKEN_URI_ABI
    )
    update_uri_hash = await erc721_resolver.functions.setUri(plain_image_uri).transact(
        {"from": address}
    )
    assert update_uri_hash is not None
    assert (
        await async_ens.w3.eth.wait_for_transaction_receipt(update_uri_hash) is not None
    )
    avatar_uri = f"eip155:1/erc721:{erc721_resolver.address}/811231"
    await async_ens.setup_address("tester.eth", address)
    await async_ens.set_text(
        "tester.eth", "avatar", avatar_uri, transact={"from": address}
    )
    result = await async_ens.get_avatar("tester.eth")
    assert result == plain_image_uri
    # clean up
    await async_ens.setup_address("tester.eth", None)


@pytest.mark.asyncio
async def test_async_get_avatar_image_uri_from_erc1155(async_ens):
    plain_image_uri = "https://euc.li/vitalik.eth"
    accounts = await async_ens.w3.eth.accounts
    address = accounts[2]

    tx_hash = (
        await async_ens.w3.eth.contract(
            bytecode=E_R_C1155_TOKEN_URI_BYTECODE,
            bytecode_runtime=E_R_C1155_TOKEN_URI_RUNTIME,
            abi=E_R_C1155_TOKEN_URI_ABI,
        )
        .constructor()
        .transact({"from": address})
    )
    assert tx_hash
    tx_receipt = await async_ens.w3.eth.wait_for_transaction_receipt(tx_hash)
    assert tx_receipt
    erc1155_resolver = async_ens.w3.eth.contract(
        address=tx_receipt.contractAddress, abi=E_R_C1155_TOKEN_URI_ABI
    )
    update_uri_hash = await erc1155_resolver.functions.setUri(plain_image_uri).transact(
        {"from": address}
    )
    assert update_uri_hash
    assert (
        await async_ens.w3.eth.wait_for_transaction_receipt(update_uri_hash) is not None
    )
    avatar_uri = f"eip155:1/erc1155:{erc1155_resolver.address}/8112316"
    await async_ens.setup_address("tester.eth", address)
    await async_ens.set_text(
        "tester.eth", "avatar", avatar_uri, transact={"from": address}
    )
    result = await async_ens.get_avatar("tester.eth")
    assert result == plain_image_uri
    # clean up
    await async_ens.setup_address("tester.eth", None)


@pytest.mark.asyncio
async def test_async_get_avatar_image_uri_without_gateway(async_ens):
    plain_image_uri = "https://euc.li/vitalik.eth"
    accounts = await async_ens.w3.eth.accounts
    address = accounts[2]
    await async_ens.setup_address("tester.eth", address)
    await async_ens.set_text(
        "tester.eth", "avatar", plain_image_uri, transact={"from": address}
    )
    result = await async_ens.get_avatar("tester.eth")
    assert result == plain_image_uri
    # clean up
    await async_ens.setup_address("tester.eth", None)


@pytest.mark.asyncio
async def test_async_get_avatar_for_uri_with_unparsable_uri(async_ens):
    badly_formated_uri = "euc.li/vitalik.eth"
    accounts = await async_ens.w3.eth.accounts
    address = accounts[2]
    await async_ens.setup_address("tester.eth", address)
    with pytest.raises(ValueError):
        await async_ens.set_text(
            "tester.eth", "avatar", badly_formated_uri, transact={"from": address}
        )
        await async_ens.get_avatar("tester.eth")
    # clean up
    await async_ens.setup_address("tester.eth", None)
