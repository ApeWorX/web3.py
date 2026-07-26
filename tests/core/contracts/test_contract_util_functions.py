import pytest

from web3._utils.contracts import (
    async_parse_block_identifier,
    async_parse_block_identifier_int,
    parse_block_identifier,
    parse_block_identifier_int,
    validate_payable,
)
from web3.exceptions import (
    BlockNumberOutOfRange,
)


@pytest.mark.parametrize(
    "block_identifier,expected_output",
    (
        (1, 1),
        (-1, 0),
        ("latest", "latest"),
        ("earliest", "earliest"),
        ("pending", "pending"),
        ("safe", "safe"),
        ("finalized", "finalized"),
    ),
)
def test_parse_block_identifier_int_and_string(w3, block_identifier, expected_output):
    block_id = parse_block_identifier(w3, block_identifier)
    assert block_id == expected_output


def test_parse_block_identifier_bytes_and_hex(w3):
    block_0 = w3.eth.get_block(0)
    block_0_hash = block_0["hash"]
    # test retrieve by bytes
    block_id_by_hash = parse_block_identifier(w3, block_0_hash)
    assert block_id_by_hash == 0
    # test retrieve by hexstring
    block_0_hexstring = w3.to_hex(block_0_hash)
    block_id_by_hex = parse_block_identifier(w3, block_0_hexstring)
    assert block_id_by_hex == 0


# a hex-encoded block number (documented as a valid ``block_identifier``) must
# resolve to its integer block number without an extra ``eth_getBlockByHash``
# round-trip, instead of raising ``BlockNumberOutOfRange``. see issue #3646
@pytest.mark.parametrize(
    "block_identifier,expected_output",
    (
        ("0x0", 0),
        ("0x1a", 26),
        ("0XABC", 2748),
        ("0x1510FA4", 22089636),  # odd-length, mixed-case hex from the issue
    ),
)
def test_parse_block_identifier_hex_block_number(w3, block_identifier, expected_output):
    assert parse_block_identifier(w3, block_identifier) == expected_output


@pytest.mark.parametrize(
    "block_identifier",
    (
        1.5,
        "cats",
        -70,
    ),
)
def test_parse_block_identifier_error(w3, block_identifier):
    with pytest.raises(BlockNumberOutOfRange):
        parse_block_identifier(w3, block_identifier)


#  These test negative block number identifiers, which behave like python
#  list slices, with -1 being the latest block and -2 being the block before that.
#  This test is necessary because transaction calls allow negative block indexes,
#  although get_block() does not allow negative block identifiers. Support for
#  negative block identifier will likely be removed in v5.
def test_parse_block_identifier_int(w3):
    last_num = w3.eth.get_block("latest").number
    assert 0 == parse_block_identifier_int(w3, -1 - last_num)


@pytest.mark.parametrize("value", (0, "0x0", "0x00"))
def test_validate_payable(value):
    tx = {"value": value}
    abi = {"payable": False}
    validate_payable(tx, abi)


# -- async -- #


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "block_identifier,expected_output",
    (
        (1, 1),
        (-1, 0),
        ("latest", "latest"),
        ("earliest", "earliest"),
        ("pending", "pending"),
        ("safe", "safe"),
        ("finalized", "finalized"),
    ),
)
async def test_async_parse_block_identifier_int_and_string(
    async_w3, block_identifier, expected_output
):
    block_id = await async_parse_block_identifier(async_w3, block_identifier)
    assert block_id == expected_output


@pytest.mark.asyncio
async def test_async_parse_block_identifier_bytes_and_hex(async_w3):
    block_0 = await async_w3.eth.get_block(0)
    block_0_hash = block_0["hash"]
    # test retrieve by bytes
    block_id_by_hash = await async_parse_block_identifier(async_w3, block_0_hash)
    assert block_id_by_hash == 0
    # test retrieve by hexstring
    block_0_hexstring = async_w3.to_hex(block_0_hash)
    block_id_by_hex = await async_parse_block_identifier(async_w3, block_0_hexstring)
    assert block_id_by_hex == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "block_identifier,expected_output",
    (
        ("0x0", 0),
        ("0x1a", 26),
        ("0XABC", 2748),
        ("0x1510FA4", 22089636),  # odd-length, mixed-case hex from the issue
    ),
)
async def test_async_parse_block_identifier_hex_block_number(
    async_w3, block_identifier, expected_output
):
    block_id = await async_parse_block_identifier(async_w3, block_identifier)
    assert block_id == expected_output


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "block_identifier",
    (
        1.5,
        "cats",
        -70,
    ),
)
async def test_async_parse_block_identifier_error(async_w3, block_identifier):
    with pytest.raises(BlockNumberOutOfRange):
        await async_parse_block_identifier(async_w3, block_identifier)


@pytest.mark.asyncio
async def test_async_parse_block_identifier_int(async_w3):
    latest_block = await async_w3.eth.get_block("latest")
    last_num = latest_block.number
    assert 0 == await async_parse_block_identifier_int(async_w3, -1 - last_num)
