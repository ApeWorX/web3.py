import pytest
import asyncio

from hypothesis import (
    given,
    settings,
    strategies as st,
)
import pytest_asyncio

from tests.core.filtering.utils import (
    MAX_UINT_256,
    _async_emitter_fixture_logic,
    _async_w3_fixture_logic,
    _emitter_fixture_logic,
    _w3_fixture_logic,
)
from tests.utils import (
    _async_wait_for_block_fixture_logic,
    _async_wait_for_transaction_fixture_logic,
)


def not_empty_string(x):
    return x != ""


@st.composite
def dynamic_values(draw):
    non_matching_1 = draw(st.text().filter(not_empty_string))
    exclusions = (non_matching_1, "")
    matching_value = draw(st.text().filter(lambda x: x not in exclusions))
    return {
        "matching": matching_value,
        "non_matching": [
            non_matching_1,
        ],
    }


@st.composite
def fixed_values(draw):
    non_matching_1 = draw(st.integers(min_value=0, max_value=MAX_UINT_256))
    non_matching_2 = draw(st.integers(min_value=0, max_value=MAX_UINT_256))
    non_matching_3 = draw(st.integers(min_value=0, max_value=MAX_UINT_256))
    non_matching_4 = draw(st.integers(min_value=0, max_value=MAX_UINT_256))
    exclusions = (non_matching_1, non_matching_2, non_matching_3, non_matching_4)
    matching_values = draw(
        st.lists(
            elements=st.integers(min_value=0, max_value=MAX_UINT_256).filter(
                lambda x: x not in exclusions
            ),
            min_size=4,
            max_size=4,
        )
    )
    return {
        "matching": matching_values,
        "non_matching": [
            non_matching_1,
            non_matching_2,
            non_matching_3,
            non_matching_4,
        ],
    }


@st.composite
def array_values(draw):
    matching = draw(st.lists(elements=st.binary(min_size=2, max_size=2), min_size=1))
    non_matching = draw(
        st.lists(elements=st.binary(min_size=2, max_size=2), min_size=1).filter(
            lambda x: x != matching
        )
    )
    return (matching, non_matching)


# --- sync --- #


@pytest.fixture(
    scope="module",
    params=[True, False],
    ids=["LocalFilterMiddleware", "node_based_filter"],
)
def w3(request):
    return _w3_fixture_logic(request)


@pytest.fixture(scope="module")
def emitter(
    w3,
    emitter_contract_data,
    wait_for_transaction,
    wait_for_block,
    address_conversion_func,
):
    emitter_contract_factory = w3.eth.contract(**emitter_contract_data)
    return _emitter_fixture_logic(
        w3,
        emitter_contract_factory,
        wait_for_transaction,
        wait_for_block,
        address_conversion_func,
    )


@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
@given(vals=dynamic_values())
@settings(max_examples=5, deadline=None)
def test_topic_filters_with_dynamic_arguments(
    w3, emitter, wait_for_transaction, create_filter, api_style, vals
):
    if api_style == "build_filter":
        filter_builder = emitter.events.LogDynamicArgs.build_filter()
        filter_builder.args["arg0"].match_single(vals["matching"])
        event_filter = filter_builder.deploy(w3)
    else:
        event_filter = create_filter(
            emitter, ["LogDynamicArgs", {"filter": {"arg0": vals["matching"]}}]
        )

    txn_hashes = [
        emitter.functions.logDynamicArgs(
            arg0=vals["matching"], arg1=vals["matching"]
        ).transact(
            {"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9, "gas": 60000}
        ),
        emitter.functions.logDynamicArgs(
            arg0=vals["non_matching"][0], arg1=vals["non_matching"][0]
        ).transact(
            {"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9, "gas": 60000}
        ),
    ]

    for txn_hash in txn_hashes:
        wait_for_transaction(w3, txn_hash)

    log_entries = event_filter.get_new_entries()
    assert len(log_entries) == 1
    assert log_entries[0]["transactionHash"] == txn_hashes[0]


@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
@given(vals=fixed_values())
@settings(max_examples=5, deadline=None)
def test_topic_filters_with_fixed_arguments(
    w3,
    emitter,
    wait_for_transaction,
    create_filter,
    api_style,
    vals,
):
    if api_style == "build_filter":
        filter_builder = emitter.events.LogQuadrupleWithIndex.build_filter()
        filter_builder.args["arg0"].match_single(vals["matching"][0])
        filter_builder.args["arg1"].match_single(vals["matching"][1])
        filter_builder.args["arg2"].match_single(vals["matching"][2])
        filter_builder.args["arg3"].match_single(vals["matching"][3])
        event_filter = filter_builder.deploy(w3)
    else:
        event_filter = create_filter(
            emitter,
            [
                "LogQuadrupleWithIndex",
                {
                    "filter": {
                        "arg0": vals["matching"][0],
                        "arg1": vals["matching"][1],
                        "arg2": vals["matching"][2],
                        "arg3": vals["matching"][3],
                    }
                },
            ],
        )

    txn_hashes = []
    txn_hashes.append(
        emitter.functions.logQuadruple(
            which=11,
            arg0=vals["matching"][0],
            arg1=vals["matching"][1],
            arg2=vals["matching"][2],
            arg3=vals["matching"][3],
        ).transact({"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9, "gas": 60000})
    )
    txn_hashes.append(
        emitter.functions.logQuadruple(
            which=11,
            arg0=vals["non_matching"][0],
            arg1=vals["non_matching"][1],
            arg2=vals["non_matching"][2],
            arg3=vals["non_matching"][3],
        ).transact({"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9, "gas": 60000})
    )

    for txn_hash in txn_hashes:
        wait_for_transaction(w3, txn_hash)

    log_entries = event_filter.get_new_entries()
    assert len(log_entries) == 1
    assert log_entries[0]["transactionHash"] == txn_hashes[0]


@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
@given(vals=array_values())
@settings(max_examples=5, deadline=None)
def test_topic_filters_with_list_arguments(
    w3, emitter, wait_for_transaction, create_filter, api_style, vals
):
    matching, non_matching = vals

    if api_style == "build_filter":
        filter_builder = emitter.events.LogListArgs.build_filter()
        filter_builder.args["arg0"].match_single(matching)
        event_filter = filter_builder.deploy(w3)
        txn_hashes = []
        txn_hashes.append(
            emitter.functions.logListArgs(arg0=matching, arg1=matching).transact(
                {"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9}
            )
        )
        txn_hashes.append(
            emitter.functions.logListArgs(
                arg0=non_matching, arg1=non_matching
            ).transact({"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9})
        )

        for txn_hash in txn_hashes:
            wait_for_transaction(w3, txn_hash)

        log_entries = event_filter.get_new_entries()
        assert len(log_entries) == 1
        assert log_entries[0]["transactionHash"] == txn_hashes[0]
    else:
        with pytest.raises(TypeError):
            create_filter(emitter, ["LogListArgs", {"filter": {"arg0": matching}}])


# --- async --- #


@pytest_asyncio.fixture(scope="module")
async def async_wait_for_block():
    return _async_wait_for_block_fixture_logic


@pytest_asyncio.fixture(scope="module")
async def async_wait_for_transaction():
    return _async_wait_for_transaction_fixture_logic


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(
    scope="module",
    params=[True, False],
    ids=["LocalFilterMiddleware", "node_based_filter"],
)
async def async_w3(request):
    return await _async_w3_fixture_logic(request)


@pytest_asyncio.fixture(scope="module")
async def async_emitter(
    async_w3,
    emitter_contract_data,
    async_wait_for_transaction,
    async_wait_for_block,
    address_conversion_func,
):
    async_emitter_contract_factory = async_w3.eth.contract(**emitter_contract_data)

    return await _async_emitter_fixture_logic(
        async_w3,
        async_emitter_contract_factory,
        async_wait_for_transaction,
        async_wait_for_block,
        address_conversion_func,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
@given(vals=dynamic_values())
@settings(max_examples=5, deadline=None)
async def test_async_topic_filters_with_dynamic_arguments(
    async_w3,
    async_emitter,
    async_wait_for_transaction,
    async_create_filter,
    api_style,
    vals,
):
    if api_style == "build_filter":
        filter_builder = async_emitter.events.LogDynamicArgs.build_filter()
        filter_builder.args["arg0"].match_single(vals["matching"])
        event_filter = await filter_builder.deploy(async_w3)
    else:
        event_filter = await async_create_filter(
            async_emitter, ["LogDynamicArgs", {"filter": {"arg0": vals["matching"]}}]
        )

    txn_hashes = [
        await async_emitter.functions.logDynamicArgs(
            arg0=vals["matching"], arg1=vals["matching"]
        ).transact(
            {"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9, "gas": 60000}
        ),
        await async_emitter.functions.logDynamicArgs(
            arg0=vals["non_matching"][0], arg1=vals["non_matching"][0]
        ).transact(
            {"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9, "gas": 60000}
        ),
    ]

    for txn_hash in txn_hashes:
        await async_wait_for_transaction(async_w3, txn_hash)

    log_entries = await event_filter.get_new_entries()
    assert len(log_entries) == 1
    assert log_entries[0]["transactionHash"] == txn_hashes[0]


@pytest.mark.asyncio
@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
@given(vals=fixed_values())
@settings(max_examples=5, deadline=None)
async def test_async_topic_filters_with_fixed_arguments(
    async_w3,
    async_emitter,
    async_wait_for_transaction,
    async_create_filter,
    api_style,
    vals,
):
    if api_style == "build_filter":
        filter_builder = async_emitter.events.LogQuadrupleWithIndex.build_filter()
        filter_builder.args["arg0"].match_single(vals["matching"][0])
        filter_builder.args["arg1"].match_single(vals["matching"][1])
        filter_builder.args["arg2"].match_single(vals["matching"][2])
        filter_builder.args["arg3"].match_single(vals["matching"][3])
        event_filter = await filter_builder.deploy(async_w3)
    else:
        event_filter = await async_create_filter(
            async_emitter,
            [
                "LogQuadrupleWithIndex",
                {
                    "filter": {
                        "arg0": vals["matching"][0],
                        "arg1": vals["matching"][1],
                        "arg2": vals["matching"][2],
                        "arg3": vals["matching"][3],
                    }
                },
            ],
        )

    txn_hashes = []
    txn_hashes.append(
        await async_emitter.functions.logQuadruple(
            which=11,
            arg0=vals["matching"][0],
            arg1=vals["matching"][1],
            arg2=vals["matching"][2],
            arg3=vals["matching"][3],
        ).transact({"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9, "gas": 60000})
    )
    txn_hashes.append(
        await async_emitter.functions.logQuadruple(
            which=11,
            arg0=vals["non_matching"][0],
            arg1=vals["non_matching"][1],
            arg2=vals["non_matching"][2],
            arg3=vals["non_matching"][3],
        ).transact({"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9, "gas": 60000})
    )

    for txn_hash in txn_hashes:
        await async_wait_for_transaction(async_w3, txn_hash)

    log_entries = await event_filter.get_new_entries()
    assert len(log_entries) == 1
    assert log_entries[0]["transactionHash"] == txn_hashes[0]


@pytest.mark.asyncio
@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
@given(vals=array_values())
@settings(max_examples=5, deadline=None)
async def test_async_topic_filters_with_list_arguments(
    async_w3,
    async_emitter,
    async_wait_for_transaction,
    async_create_filter,
    api_style,
    vals,
):
    matching, non_matching = vals

    if api_style == "build_filter":
        filter_builder = async_emitter.events.LogListArgs.build_filter()
        filter_builder.args["arg0"].match_single(matching)
        event_filter = await filter_builder.deploy(async_w3)
        txn_hashes = []
        txn_hashes.append(
            await async_emitter.functions.logListArgs(
                arg0=matching, arg1=matching
            ).transact({"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9})
        )
        txn_hashes.append(
            await async_emitter.functions.logListArgs(
                arg0=non_matching, arg1=non_matching
            ).transact({"maxFeePerGas": 10**9, "maxPriorityFeePerGas": 10**9})
        )

        for txn_hash in txn_hashes:
            await async_wait_for_transaction(async_w3, txn_hash)

        log_entries = await event_filter.get_new_entries()
        assert len(log_entries) == 1
        assert log_entries[0]["transactionHash"] == txn_hashes[0]
    else:
        with pytest.raises(TypeError):
            await async_create_filter(
                async_emitter, ["LogListArgs", {"filter": {"arg0": matching}}]
            )
