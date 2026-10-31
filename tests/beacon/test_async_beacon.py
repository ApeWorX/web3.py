import pytest
from random import (
    randint,
)

from aiohttp.client_exceptions import (
    InvalidURL,
)
import pytest_asyncio

from web3.beacon import (
    AsyncBeacon,
)

# tested against lighthouse which uses port 5052 by default
BASE_URL = "http://localhost:5052"


def _assert_valid_response(response):
    # assert valid response according to Beacon API spec
    assert isinstance(response, dict)
    assert "data" in response


@pytest.fixture
def async_beacon():
    return AsyncBeacon(base_url=BASE_URL, request_timeout=30.0)


@pytest_asyncio.fixture(autouse=True)
async def _cleanup(async_beacon):
    yield
    [
        await session.close()
        for _, session in async_beacon._request_session_manager.session_cache.items()
    ]


# sanity check to make sure the positive test cases are valid
@pytest.mark.asyncio
async def test_async_cl_beacon_raises_exception_on_invalid_url(async_beacon):
    with pytest.raises(InvalidURL):
        await async_beacon._async_make_get_request(
            BASE_URL + "/eth/v1/beacon/nonexistent"
        )


@pytest.mark.asyncio
async def test_async_beacon_user_request_timeout(async_beacon):
    async_beacon.request_timeout = 0.001
    with pytest.raises(TimeoutError):
        await async_beacon.get_validators()


@pytest.mark.asyncio
async def test_async_beacon_request_timeout_type(async_beacon):
    assert isinstance(async_beacon.request_timeout, float)


# Beacon endpoint tests:


@pytest.mark.asyncio
async def test_async_cl_beacon_get_genesis(async_beacon):
    response = await async_beacon.get_genesis()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_hash_root(async_beacon):
    response = await async_beacon.get_hash_root()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_fork_data(async_beacon):
    response = await async_beacon.get_fork_data()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_finality_checkpoint(async_beacon):
    response = await async_beacon.get_finality_checkpoint()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_validators(async_beacon):
    response = await async_beacon.get_validators()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_validator(async_beacon):
    validators_response = await async_beacon.get_validators()
    _assert_valid_response(validators_response)

    validators = validators_response["data"]
    random_validator = validators[randint(0, len(validators))]
    random_validator_pubkey = random_validator["validator"]["pubkey"]

    response = await async_beacon.get_validator(random_validator_pubkey)
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_validator_balances(async_beacon):
    response = await async_beacon.get_validator_balances()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_epoch_committees(async_beacon):
    response = await async_beacon.get_epoch_committees()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_epoch_sync_committees(async_beacon):
    response = await async_beacon.get_epoch_sync_committees()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_epoch_randao(async_beacon):
    response = await async_beacon.get_epoch_randao()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_block_headers(async_beacon):
    response = await async_beacon.get_block_headers()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_block_header(async_beacon):
    response = await async_beacon.get_block_header("head")
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_block(async_beacon):
    response = await async_beacon.get_block("head")
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_block_root(async_beacon):
    response = await async_beacon.get_block_root("head")
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_blinded_blocks(async_beacon):
    response = await async_beacon.get_blinded_blocks("head")
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_rewards(async_beacon):
    response = await async_beacon.get_rewards("head")
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_block_attestations(async_beacon):
    response = await async_beacon.get_block_attestations("head")
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_attestations(async_beacon):
    response = await async_beacon.get_attestations()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_attester_slashings(async_beacon):
    response = await async_beacon.get_attester_slashings()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_proposer_slashings(async_beacon):
    response = await async_beacon.get_proposer_slashings()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_voluntary_exits(async_beacon):
    response = await async_beacon.get_voluntary_exits()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_beacon_get_bls_to_execution_changes(async_beacon):
    response = await async_beacon.get_bls_to_execution_changes()
    _assert_valid_response(response)


# Config endpoint tests:


@pytest.mark.asyncio
async def test_async_cl_config_get_fork_schedule(async_beacon):
    response = await async_beacon.get_fork_schedule()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_config_get_spec(async_beacon):
    response = await async_beacon.get_spec()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_config_get_deposit_contract(async_beacon):
    response = await async_beacon.get_deposit_contract()
    _assert_valid_response(response)


# Debug endpoint tests:


@pytest.mark.asyncio
async def test_async_cl_debug_get_beacon_state(async_beacon):
    response = await async_beacon.get_beacon_state()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_debug_get_beacon_heads(async_beacon):
    response = await async_beacon.get_beacon_heads()
    _assert_valid_response(response)


# Node endpoint tests:


@pytest.mark.asyncio
async def test_async_cl_node_get_node_identity(async_beacon):
    response = await async_beacon.get_node_identity()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_node_get_peers(async_beacon):
    response = await async_beacon.get_peers()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_node_get_peer(async_beacon):
    response = await async_beacon.get_peer("")
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_node_get_peer_count(async_beacon):
    response = await async_beacon.get_peer_count()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_node_get_health(async_beacon):
    response = await async_beacon.get_health()
    assert isinstance(response, int)


@pytest.mark.asyncio
async def test_async_cl_node_get_version(async_beacon):
    response = await async_beacon.get_version()
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_node_get_syncing(async_beacon):
    response = await async_beacon.get_syncing()
    _assert_valid_response(response)


# Blob endpoint tests


@pytest.mark.asyncio
async def test_async_cl_node_get_blob_sidecars(async_beacon):
    response = await async_beacon.get_blob_sidecars("head")
    _assert_valid_response(response)

    # test with indices
    with_indices = await async_beacon.get_blob_sidecars("head", [0, 1])
    _assert_valid_response(with_indices)


# Validator endpoint tests:


@pytest.mark.asyncio
async def test_async_cl_validator_get_attester_duties(async_beacon):
    finality_checkpoint_response = await async_beacon.get_finality_checkpoint()
    _assert_valid_response(finality_checkpoint_response)

    finality_checkpoint = finality_checkpoint_response["data"]
    epoch = finality_checkpoint["finalized"]["epoch"]

    validators_response = await async_beacon.get_validators()
    _assert_valid_response(validators_response)

    validators = validators_response["data"]
    random_validator = validators[randint(0, len(validators))]
    random_validator_index = random_validator["index"]

    response = await async_beacon.get_attester_duties(epoch, [random_validator_index])
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_validator_get_block_proposer_duties(async_beacon):
    finality_checkpoint_response = await async_beacon.get_finality_checkpoint()
    _assert_valid_response(finality_checkpoint_response)

    finality_checkpoint = finality_checkpoint_response["data"]
    epoch = finality_checkpoint["finalized"]["epoch"]

    response = await async_beacon.get_block_proposer_duties(epoch)
    _assert_valid_response(response)


@pytest.mark.asyncio
async def test_async_cl_validator_get_sync_committee_duties(async_beacon):
    finality_checkpoint_response = await async_beacon.get_finality_checkpoint()
    _assert_valid_response(finality_checkpoint_response)

    finality_checkpoint = finality_checkpoint_response["data"]
    epoch = finality_checkpoint["finalized"]["epoch"]

    validators_response = await async_beacon.get_validators()
    _assert_valid_response(validators_response)

    validators = validators_response["data"]
    random_validator = validators[randint(0, len(validators))]
    random_validator_index = random_validator["index"]

    response = await async_beacon.get_sync_committee_duties(
        epoch, [random_validator_index]
    )
    _assert_valid_response(response)


# Rewards endpoint tests:


@pytest.mark.asyncio
async def test_async_cl_validator_get_attestations_rewards(async_beacon):
    finality_checkpoint_response = await async_beacon.get_finality_checkpoint()
    _assert_valid_response(finality_checkpoint_response)

    finality_checkpoint = finality_checkpoint_response["data"]
    epoch = finality_checkpoint["finalized"]["epoch"]

    validators_response = await async_beacon.get_validators()
    _assert_valid_response(validators_response)

    validators = validators_response["data"]
    random_validator = validators[randint(0, len(validators))]
    random_validator_index = random_validator["index"]

    response = await async_beacon.get_attestations_rewards(
        epoch, [random_validator_index]
    )
    _assert_valid_response(response)
