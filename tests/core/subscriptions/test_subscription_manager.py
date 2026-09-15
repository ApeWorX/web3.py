import pytest
import asyncio
import itertools
import time
from typing import (
    cast,
)
from unittest.mock import (
    AsyncMock,
)

from eth_typing import (
    HexStr,
)
import pytest_asyncio

from web3 import (
    AsyncWeb3,
    PersistentConnectionProvider,
)
from web3.exceptions import (
    SubscriptionHandlerTaskException,
    Web3ValueError,
)
from web3.providers.persistent.request_processor import (
    TaskReliantQueue,
)
from web3.types import (
    RPCResponse,
)
from web3.utils.subscriptions import (
    LogsSubscription,
    NewHeadsSubscription,
    PendingTxSubscription,
)


class MockProvider(PersistentConnectionProvider):
    socket_recv = AsyncMock()
    socket_send = AsyncMock()


@pytest_asyncio.fixture
async def subscription_manager():
    countr = itertools.count()
    w3 = AsyncWeb3(MockProvider())
    w3.eth._subscribe = AsyncMock()
    w3.eth._subscribe.side_effect = lambda *_: f"0x{str(next(countr))}"
    w3.eth._unsubscribe = AsyncMock()
    w3.eth._unsubscribe.return_value = True
    yield w3.subscription_manager


def create_subscription_message(sub_id):
    return cast(
        RPCResponse,
        {
            "jsonrpc": "2.0",
            "method": "eth_subscription",
            "params": {"subscription": sub_id, "result": "0x0"},
        },
    )


@pytest.mark.asyncio
async def test_subscription_default_labels_are_unique(subscription_manager):
    sub1 = NewHeadsSubscription()
    sub2 = NewHeadsSubscription()
    sub3 = NewHeadsSubscription()
    sub4 = NewHeadsSubscription()

    sub_ids = await subscription_manager.subscribe([sub1, sub2, sub3, sub4])
    assert sub_ids == ["0x0", "0x1", "0x2", "0x3"]

    assert sub1.label != sub2.label != sub3.label != sub4.label
    assert sub1.label == "NewHeadsSubscription('newHeads',)"
    assert sub2.label == "NewHeadsSubscription('newHeads',)#2"
    assert sub3.label == "NewHeadsSubscription('newHeads',)#3"
    assert sub4.label == "NewHeadsSubscription('newHeads',)#4"

    # assert no issues unsubscribing
    await subscription_manager.unsubscribe_all()

    assert subscription_manager.subscriptions == []
    assert subscription_manager._subscription_container.subscriptions == []
    assert subscription_manager._subscription_container.subscriptions_by_id == {}
    assert subscription_manager._subscription_container.subscriptions_by_label == {}


@pytest.mark.asyncio
async def test_subscription_manager_raises_for_new_subs_with_the_same_custom_label(
    subscription_manager,
):
    sub1 = NewHeadsSubscription(label="foo")
    sub2 = LogsSubscription(label="foo")

    with pytest.raises(
        Web3ValueError,
        match="Subscription label already exists. Subscriptions must have unique "
        "labels.\n    label: foo",
    ):
        await subscription_manager.subscribe([sub1, sub2])

    # make sure the subscription was subscribed to and not added to the manager
    assert subscription_manager.subscriptions == [sub1]
    sub_container = subscription_manager._subscription_container
    assert len(sub_container) == 1
    assert sub_container.subscriptions == [sub1]
    assert sub_container.subscriptions_by_id == {"0x0": sub1}
    assert sub_container.subscriptions_by_label == {"foo": sub1}


@pytest.mark.asyncio
async def test_subscription_manager_get_by_id(subscription_manager):
    sub = NewHeadsSubscription(label="foo")
    await subscription_manager.subscribe(sub)
    assert subscription_manager.get_by_id("0x0") == sub
    assert subscription_manager.get_by_id("0x1") is None


@pytest.mark.asyncio
async def test_subscription_manager_get_by_label(subscription_manager):
    sub = NewHeadsSubscription(label="foo")
    await subscription_manager.subscribe(sub)
    assert subscription_manager.get_by_label("foo") == sub
    assert subscription_manager.get_by_label("bar") is None


@pytest.mark.asyncio
async def test_unsubscribe_one_by_one_clears_all_subscriptions(
    subscription_manager,
):
    sub1 = NewHeadsSubscription(label="foo")
    sub2 = PendingTxSubscription(label="bar")
    await subscription_manager.subscribe(sub1)
    await subscription_manager.subscribe(sub2)

    await subscription_manager.unsubscribe(sub1)
    assert subscription_manager.subscriptions == [sub2]

    await subscription_manager.unsubscribe(sub2)
    assert subscription_manager.subscriptions == []


@pytest.mark.asyncio
async def test_unsubscribe_all_clears_all_subscriptions(subscription_manager):
    sub1 = NewHeadsSubscription(label="foo")
    sub2 = PendingTxSubscription(label="bar")
    await subscription_manager.subscribe([sub1, sub2])
    assert subscription_manager.subscriptions == [sub1, sub2]

    await subscription_manager.unsubscribe_all()
    assert subscription_manager.subscriptions == []

    sub_container = subscription_manager._subscription_container
    assert len(sub_container) == 0
    assert sub_container.subscriptions == []
    assert sub_container.subscriptions_by_id == {}
    assert sub_container.subscriptions_by_label == {}


@pytest.mark.asyncio
async def test_unsubscribe_with_one_or_multiple(subscription_manager):
    sub1 = NewHeadsSubscription()
    sub2 = PendingTxSubscription()
    sub3 = NewHeadsSubscription()
    sub4 = LogsSubscription()
    sub5 = NewHeadsSubscription()
    sub6 = PendingTxSubscription()

    (
        sub_id1,
        sub_id2,
        sub_id3,
        sub_id4,
        sub_id5,
        sub_id6,
    ) = await subscription_manager.subscribe([sub1, sub2, sub3, sub4, sub5, sub6])
    assert sub_id1 == "0x0"
    assert sub_id2 == "0x1"
    assert sub_id3 == "0x2"
    assert sub_id4 == "0x3"
    assert sub_id5 == "0x4"
    assert sub_id6 == "0x5"

    assert subscription_manager.subscriptions == [sub1, sub2, sub3, sub4, sub5, sub6]

    # unsubscribe single by hex id
    assert await subscription_manager.unsubscribe(sub_id1) is True
    assert subscription_manager.subscriptions == [sub2, sub3, sub4, sub5, sub6]

    # unsubscribe many by hex id
    assert await subscription_manager.unsubscribe([sub_id2, sub_id3]) is True
    assert subscription_manager.subscriptions == [sub4, sub5, sub6]

    # unsubscribe non-existent hex id
    with pytest.raises(Web3ValueError, match=f"Subscription not found|{0x7}"):
        await subscription_manager.unsubscribe(HexStr("0x7"))

    # unsubscribe by subscription object
    assert await subscription_manager.unsubscribe(sub4) is True
    assert subscription_manager.subscriptions == [sub5, sub6]

    # unsubscribe many by subscription object
    assert await subscription_manager.unsubscribe([sub5, sub6]) is True
    assert subscription_manager.subscriptions == []

    # unsubscribe non-existent subscription object
    with pytest.raises(Web3ValueError, match=f"Subscription not found|{sub5.id}"):
        await subscription_manager.unsubscribe(sub5)


@pytest.mark.asyncio
async def test_unsubscribe_with_subscriptions_reference_does_not_mutate_the_list(
    subscription_manager,
):
    sub1 = NewHeadsSubscription()
    sub2 = LogsSubscription()
    sub3 = PendingTxSubscription()
    sub4 = NewHeadsSubscription()

    await subscription_manager.subscribe([sub1, sub2, sub3, sub4])
    assert subscription_manager.subscriptions == [sub1, sub2, sub3, sub4]

    # assert not mutating in place
    await subscription_manager.unsubscribe(subscription_manager.subscriptions)
    assert subscription_manager.subscriptions == []

    # via unsubscribe all

    await subscription_manager.subscribe([sub1, sub2, sub3, sub4])
    assert subscription_manager.subscriptions == [sub1, sub2, sub3, sub4]

    await subscription_manager.unsubscribe_all()
    assert subscription_manager.subscriptions == []


@pytest.mark.asyncio
async def test_high_throughput_subscription_with_parallelize(
    subscription_manager,
) -> None:
    provider = subscription_manager._w3.provider
    num_msgs = 5_000

    provider._request_processor._handler_subscription_queue = TaskReliantQueue(
        maxsize=num_msgs
    )

    # Turn on task-based processing. This test should fail the time constraint if this
    # is not set to ``True`` (not task-based processing).
    subscription_manager.parallelize = True

    class Counter:
        val: int = 0

    counter = Counter()

    async def high_throughput_handler(handler_context) -> None:
        # if we awaited all `num_msgs`, we would sleep at least 5 seconds total
        await asyncio.sleep(5 / num_msgs)

        handler_context.counter.val += 1
        if handler_context.counter.val == num_msgs:
            await handler_context.subscription.unsubscribe()

    # build a meaningless subscription since we are fabricating the messages
    sub_id = await subscription_manager.subscribe(
        NewHeadsSubscription(
            handler=high_throughput_handler, handler_context={"counter": counter}
        ),
    )
    provider._request_processor.cache_request_information(
        request_id=sub_id,
        method="eth_subscribe",
        params=[],
        response_formatters=((), (), ()),
    )

    # put `num_msgs` messages in the queue
    for _ in range(num_msgs):
        provider._request_processor._handler_subscription_queue.put_nowait(
            create_subscription_message(sub_id)
        )

    start = time.time()
    await subscription_manager.handle_subscriptions()
    stop = time.time()

    assert counter.val == num_msgs

    assert subscription_manager.total_handler_calls == num_msgs
    assert stop - start < 3


@pytest.mark.asyncio
async def test_parallelize_with_error_propagation(
    subscription_manager,
) -> None:
    provider = subscription_manager._w3.provider
    subscription_manager.parallelize = True

    async def high_throughput_handler(_handler_context) -> None:
        raise ValueError("Test error msg.")

    # build a meaningless subscription since we are fabricating the messages
    sub_id = await subscription_manager.subscribe(
        NewHeadsSubscription(handler=high_throughput_handler)
    )
    provider._request_processor.cache_request_information(
        request_id=sub_id,
        method="eth_subscribe",
        params=[],
        response_formatters=((), (), ()),
    )
    provider._request_processor._handler_subscription_queue.put_nowait(
        create_subscription_message(sub_id)
    )

    with pytest.raises(
        SubscriptionHandlerTaskException,
        match="Test error msg.",
    ):
        await subscription_manager.handle_subscriptions()


@pytest.mark.asyncio
async def test_subscription_parallelize_false_overrides_manager_true(
    subscription_manager,
) -> None:
    provider = subscription_manager._w3.provider
    subscription_manager.parallelize = True  # manager parallelizing

    async def test_handler(context) -> None:
        # assert not parallelized
        assert context.subscription.parallelize is False
        assert subscription_manager._tasks == set()
        await context.subscription.unsubscribe()

    sub_id = await subscription_manager.subscribe(
        # parallelize=False overrides manager's parallelization setting
        NewHeadsSubscription(handler=test_handler, parallelize=False)
    )

    provider._request_processor.cache_request_information(
        request_id=sub_id,
        method="eth_subscribe",
        params=[],
        response_formatters=((), (), ()),
    )

    provider._request_processor._handler_subscription_queue.put_nowait(
        create_subscription_message(sub_id)
    )

    await subscription_manager.handle_subscriptions()

    assert subscription_manager.total_handler_calls == 1


@pytest.mark.asyncio
async def test_subscription_parallelize_true_overrides_manager_default_false(
    subscription_manager,
) -> None:
    provider = subscription_manager._w3.provider
    assert subscription_manager.parallelize is False

    async def test_handler(context) -> None:
        # check that the subscription is parallelized
        assert context.subscription.parallelize is True
        assert len(context.async_w3.subscription_manager._tasks) == 1
        assert asyncio.current_task() in context.async_w3.subscription_manager._tasks
        await context.subscription.unsubscribe()

    sub_id = await subscription_manager.subscribe(
        NewHeadsSubscription(handler=test_handler, parallelize=True)
    )

    provider._request_processor.cache_request_information(
        request_id=sub_id,
        method="eth_subscribe",
        params=[],
        response_formatters=((), (), ()),
    )

    provider._request_processor._handler_subscription_queue.put_nowait(
        create_subscription_message(sub_id)
    )

    await subscription_manager.handle_subscriptions()

    assert subscription_manager.total_handler_calls == 1
    assert len(subscription_manager._tasks) == 0  # assert cleaned up


@pytest.mark.asyncio
async def test_mixed_subscription_parallelization_settings(
    subscription_manager,
) -> None:
    provider = subscription_manager._w3.provider
    subscription_manager.parallelize = True  # manager wants parallel

    completion_order = []

    async def fast_parallel_handler(_ctx) -> None:
        await asyncio.sleep(0.05)
        completion_order.append("fast_parallel")
        assert asyncio.current_task() in subscription_manager._tasks

    async def slow_sequential_handler(_ctx) -> None:
        await asyncio.sleep(0.15)
        completion_order.append("slow_sequential")
        assert asyncio.current_task() not in subscription_manager._tasks

    async def medium_default_handler(_ctx) -> None:
        await asyncio.sleep(0.10)
        completion_order.append("medium_default")
        assert asyncio.current_task() in subscription_manager._tasks

        # we assume this should be the last task to complete so unsubscribe only here
        await subscription_manager.unsubscribe_all()

    # subscriptions with different settings
    fast_sub_id = await subscription_manager.subscribe(
        NewHeadsSubscription(handler=fast_parallel_handler, parallelize=True)
    )
    slow_sub_id = await subscription_manager.subscribe(
        NewHeadsSubscription(handler=slow_sequential_handler, parallelize=False)
    )
    medium_sub_id = await subscription_manager.subscribe(
        # uses the manager default parallelization setting (True)
        NewHeadsSubscription(handler=medium_default_handler)
    )

    for sub_id in {slow_sub_id, fast_sub_id, medium_sub_id}:
        provider._request_processor.cache_request_information(
            request_id=sub_id,
            method="eth_subscribe",
            params=[],
            response_formatters=((), (), ()),
        )

    # send messages in order of slow (but main loop), fast (parallel), medium (parallel)
    for sub_id in [slow_sub_id, fast_sub_id, medium_sub_id]:
        provider._request_processor._handler_subscription_queue.put_nowait(
            create_subscription_message(sub_id)
        )

    await subscription_manager.handle_subscriptions()

    # `slow_sequential` should complete first despite taking longest because it
    # blocks the main loop. The next two run in parallel after, so the fastest of the
    # two should complete next, leaving the `medium_default` last.
    assert len(completion_order) == 3
    assert completion_order[0] == "slow_sequential"
    assert "fast_parallel" == completion_order[1]
    assert "medium_default" == completion_order[2]


@pytest.mark.asyncio
async def test_performance_difference_with_subscription_overrides(
    subscription_manager,
) -> None:
    provider = subscription_manager._w3.provider
    assert subscription_manager.parallelize is False

    manager_tasks = subscription_manager._tasks

    async def parallel_handler(_ctx) -> None:
        await asyncio.sleep(0.1)
        assert asyncio.current_task() in manager_tasks
        if len(manager_tasks) >= 3:
            await subscription_manager.unsubscribe_all()

    # create 3 subscriptions, override all to parallel despite manager default False
    for _ in range(3):
        sub_id = await subscription_manager.subscribe(
            NewHeadsSubscription(handler=parallel_handler, parallelize=True)
        )
        provider._request_processor.cache_request_information(
            request_id=sub_id,
            method="eth_subscribe",
            params=[],
            response_formatters=((), (), ()),
        )
        provider._request_processor._handler_subscription_queue.put_nowait(
            create_subscription_message(sub_id)
        )

    await subscription_manager.handle_subscriptions()

    assert subscription_manager.total_handler_calls == 3
    assert len(manager_tasks) == 0  # all tasks cleaned up


@pytest.mark.asyncio
async def test_eth_subscribe_api_call_with_all_kwargs(subscription_manager):
    async_w3 = subscription_manager._w3
    provider = subscription_manager._w3.provider

    label = "test_subscription"
    test_ctx = "test context"

    async def parallel_handler(context) -> None:
        assert asyncio.current_task() in subscription_manager._tasks
        assert context.test_ctx == test_ctx
        sub = subscription_manager.get_by_id(context.subscription.id)
        assert sub.label == label

        await context.subscription.unsubscribe()

    sub_id = await async_w3.eth.subscribe(
        "newHeads",
        handler=parallel_handler,
        handler_context={"test_ctx": test_ctx},
        label=label,
        parallelize=True,
    )
    provider._request_processor.cache_request_information(
        request_id=sub_id,
        method="eth_subscribe",
        params=[],
        response_formatters=((), (), ()),
    )
    provider._request_processor._handler_subscription_queue.put_nowait(
        create_subscription_message(sub_id)
    )

    await subscription_manager.handle_subscriptions()

    assert subscription_manager.total_handler_calls == 1
    assert len(async_w3.subscription_manager._tasks) == 0


@pytest.mark.asyncio
async def test_message_listener_does_not_stall_when_handler_queue_is_full(
    subscription_manager,
) -> None:
    """
    Regression test: when the response queue has cleared ``_listen_event`` and
    the handler queue is the slow consumer, ``cache_raw_response`` must not
    wait on ``_listen_event`` for a reset that only the response-queue consumer
    can perform. The listener must keep draining as the handler consumer
    processes messages.
    """
    provider = subscription_manager._w3.provider

    class Counter:
        val: int = 0

    counter = Counter()
    tiny_queue_size = 2

    async def slow_handler(handler_context) -> None:
        await asyncio.sleep(0.01)
        handler_context.counter.val += 1

    sub_id = await subscription_manager.subscribe(
        NewHeadsSubscription(handler=slow_handler, handler_context={"counter": counter}),
    )
    provider._request_processor.cache_request_information(
        request_id=sub_id,
        method="eth_subscribe",
        params=[],
        response_formatters=((), (), ()),
    )

    # shrink the handler queue so it fills quickly with a slow consumer
    provider._request_processor._handler_subscription_queue = TaskReliantQueue(
        maxsize=tiny_queue_size
    )

    # simulate a prior response-queue backpressure clearing the listen event:
    # with only handler subscriptions routed, only the handler consumer can
    # free capacity, and it never resets _listen_event.
    provider._listen_event.clear()

    num_msgs = 6
    rp = provider._request_processor
    msg = create_subscription_message(sub_id)

    async def drain_handler_queue() -> None:
        for _ in range(num_msgs):
            await rp.cache_raw_response(msg, subscription=True)

    caching_task = asyncio.ensure_future(drain_handler_queue())

    async def consume_handler_queue() -> None:
        queue = rp._handler_subscription_queue
        processed = 0
        while processed < num_msgs:
            response = await asyncio.wait_for(queue.get(), timeout=5)
            processed += 1

    await asyncio.wait_for(
        asyncio.gather(caching_task, consume_handler_queue()), timeout=10
    )

    # the listener never waited forever: all messages were queued and drained
    assert rp._handler_subscription_queue.qsize() == 0
