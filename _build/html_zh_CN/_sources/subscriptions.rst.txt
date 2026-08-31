.. _subscriptions:

Event Subscriptions
===================

Most Ethereum clients include ``eth_subscribe`` support, allowing you to listen for specific events as they occur. This applies to a limited set of events: new block headers, the syncing status of a node, new pending transactions, and emitted logs from smart contracts.

.. warning::

    Subscriptions require a persistent socket connection between you and the Ethereum client. For that reason, you must use web3.py's :class:`~web3.providers.persistent.WebSocketProvider` or :class:`~web3.providers.persistent.AsyncIPCProvider` to utilize subscriptions. As it is the more common of the two, examples in this guide will leverage the ``WebSocketProvider``.

An introduction to subscriptions
--------------------------------

When you subscribe to an event – new block headers, for example – you'll receive a subscription ID. The Ethereum client will then maintain a connection to your application and send along any related event until you unsubscribe with that ID. That example in code:

.. code-block:: python

    import asyncio
    from web3 import AsyncWeb3, WebSocketProvider

    async def example():
        # connect to a node:
        async with AsyncWeb3(WebSocketProvider("wss://...")) as w3:

        # subscribe to new block headers:
        subscription_id = await w3.eth.subscribe("newHeads")
        print(subscription_id)

        # listen for events as they occur:
        async for response in w3.socket.process_subscriptions():
            # handle each event:
            print(response)

            # unsubscribe:
            if response["number"] > 42012345:
                await w3.eth.unsubscribe(subscription_id)
                break

    asyncio.run(example())


web3.py's ``subscription_manager``
----------------------------------

The example above is the "manual" approach to managing subscriptions. It's not so complicated in the case of listening for new block headers, but things get considerably more complex once you start listening for smart contract event logs or managing multiple subscriptions.
As of v7.7.0, web3.py includes some additional convenient subscription management features. We'll step through them now.

1.) The subscription_manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``w3`` (``AsyncWeb3``) instance has a ``subscription_manager`` module. While you may
still use the ``w3.eth.subscribe`` method from the previous example, the
``subscription_manager`` offers an additional way to start one or more subscriptions and
provides better management of those subscriptions. We're going to pass in a list of
events we want to subscribe to within the ``w3.subscription_manager.subscribe`` method.

.. code-block:: python

    await w3.subscription_manager.subscribe([sub1, sub2, ...])


2.) Subscription types
~~~~~~~~~~~~~~~~~~~~~~

To aid in defining those subscriptions, subscription type classes have been introduced: ``NewHeadsSubscription``, ``PendingTxSubscription``, ``LogsSubscription``, and ``SyncingSubscription``. Each class is context aware, meaning it will throw an error if you provide an unexpected data type.

.. code-block:: python

    from web3.utils.subscriptions import (
        NewHeadsSubscription,
        PendingTxSubscription,
        LogsSubscription,
    )

    sub1 = NewHeadsSubscription(
        label="new-heads-mainnet",  # optional label
        handler=new_heads_handler,
    )

    sub2 = PendingTxSubscription(
        label="pending-tx-mainnet",  # optional label
        full_transactions=True,
        handler=pending_tx_handler,
        # optional parallelization flag (see Parallelizing subscriptions section below)
        parallelize=True,
    )

    sub3 = LogsSubscription(
        label="WETH transfers",  # optional label
        address=weth_contract.address,
        topics=[weth_contract.events.Transfer().topic],
        handler=log_handler,
        # optional `handler_context` args to help parse a response
        handler_context={"transfer_event": weth_contract.events.Transfer()},
    )


3.) Handlers
~~~~~~~~~~~~

In the example above, there is a handler specified for each subscription. These are context-aware functions that you can declare separate from the subscription logic. Within each handler, parse and perform whatever logic you require.
Note that in addition to the result being processed, the ``handler_context`` in each handler provides access to your ``AsyncWeb3`` instance, the subscription instance, and any custom values declared within the ``handler_context`` of the subscription: ``from web3.utils.subscriptions import LogsSubscriptionContext``

.. code-block:: python

    async def new_heads_handler(
        handler_context: LogsSubscriptionContext,
    ) -> None:
        log_receipt = handler_context.result
        print(f"New log: {log_receipt}\n")

        event_data = handler_context.transfer_event.process_log(log_receipt)
        print(f"Log event data: {event_data}\n")

        if log_receipt["blockNumber"] > 42012345:
            await handler_context.subscription.unsubscribe()


4.) handle_subscriptions
~~~~~~~~~~~~~~~~~~~~~~~~

Finally, when all your subscriptions are configured, utilize the handle_subscriptions method to begin processing them. If you need to listen for events on multiple chains, create one w3 instance per chain.

.. code-block:: python

    async def sub_manager():
        ...

        # handle subscriptions via configured handlers:
        await w3.subscription_manager.handle_subscriptions()

        # or, gather one w3 instance per chain:
        await asyncio.gather(
            w3.subscription_manager.handle_subscriptions(),
            l2_w3.subscription_manager.handle_subscriptions(),
        )

    asyncio.run(sub_manager())


5.) Unsubscribing
~~~~~~~~~~~~~~~~~

If you don't want to subscribe indefinitely to an event, you can unsubscribe at any point. The first example in this post demonstrated the manual approach: ``await w3.eth.unsubscribe(subscription_id)``


The new handler pattern will keep track of the subscription ID for you however, so the same can be accomplished via the ``handler_context`` without an ID:

.. code-block:: python

    async def new_heads_handler(handler_context):
        ...
        if some_condition:
            await handler_context.subscription.unsubscribe()


Lastly, if you're wrapping up the whole show, you can reach for ``unsubscribe_all`` on the subscription_manager:

.. code-block:: python

    await w3.subscription_manager.unsubscribe_all()
    assert subscription_manager.subscriptions == []


An example
----------

Let's put all the pieces together. This example will subscribe to new block headers and transfer events from the WETH contract. It should work as written if you provide a WebSocket RPC URL.

.. code-block:: python

    import asyncio
    from web3 import AsyncWeb3, WebSocketProvider
    from web3.utils.subscriptions import (
        NewHeadsSubscription,
        NewHeadsSubscriptionContext,
        LogsSubscription,
        LogsSubscriptionContext,
    )

    # -- declare handlers --
    async def new_heads_handler(
        handler_context: NewHeadsSubscriptionContext,
    ) -> None:
        header = handler_context.result
        print(f"New block header: {header}\n")

    async def log_handler(
        handler_context: LogsSubscriptionContext,
    ) -> None:
        log_receipt = handler_context.result
        print(f"Log receipt: {log_receipt}\n")

    async def sub_manager():

        # -- initialize provider --
        w3 = await AsyncWeb3(WebSocketProvider("wss://..."))

        # -- subscribe to event(s) --
        await w3.subscription_manager.subscribe(
            [
                NewHeadsSubscription(
                    label="new-heads-mainnet",
                    handler=new_heads_handler
                ),
                LogsSubscription(
                    label="WETH transfers",
                    address=w3.to_checksum_address(
                        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
                    ),
                    topics=["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
                    handler=log_handler,
                ),
            ]
        )

        # -- listen for events --
        await w3.subscription_manager.handle_subscriptions()

    asyncio.run(sub_manager())


Parallelizing subscriptions
---------------------------

.. important::

    Parallelizing subscriptions does not guarantee that events will be processed in the
    order they are received. Most events should still be processed in the order they are
    received, but if a particular handler takes a long time to execute, newer events may
    be processed first. It is recommended to set the ``parallelize`` flag to ``False``
    (default behavior) for subscriptions that depend on the order of events.


If you have multiple subscriptions that can be processed in parallel, you can set the
``parallelize`` flag to ``True`` - either globally on the subscription manager, or
individually on each subscription. This control allows the subscription manager to
handle subscription processing concurrently. This flag can be set on the manager, as a
global setting, or on individual subscriptions. This can help with performance if
subscriptions are independent of each other, or do not rely on some external shared
state (no race conditions are present).

Global parallelization is off by default, meaning all subscriptions will be processed
sequentially unless you set the ``parallelize`` flag to ``True`` on the subscription
manager or individual subscriptions.

.. code-block:: python

    sub1 = NewHeadsSubscription(
        label="new-heads-mainnet",
        handler=new_heads_handler,
        parallelize=True,  # process this subscription in parallel
    )

    sub2 = LogsSubscription(
        label="WETH transfers",
        address=weth_contract.address,
        topics=[weth_contract.events.Transfer().topic],
        handler=log_handler,
        parallelize=False,  # process sequentially (this is the default behavior)
    )

    sub3 = LogsSubscription(
        label="WETH approvals",
        address=weth_contract.address,
        topics=[weth_contract.events.Approval().topic],
        handler=approval_handler,
        parallelize=True,  # process this subscription in parallel
    )

    await w3.subscription_manager.subscribe([sub1, sub2])

Global parallelization can also be set on the subscription manager, which will apply to
all subscriptions unless overridden by an individual subscription's ``parallelize``
flag:

.. code-block:: python

    # or set the parallelize flag globally on the subscription manager:
    w3.subscription_manager.parallelize = True

    # parallelize is set globally, so this will be processed in parallel
    sub1 = NewHeadsSubscription(
        label="new-heads-mainnet",
        handler=new_heads_handler,
    )

    # this will be processed sequentially since ``parallelize`` is set to ``False``,
    # overriding the global setting
    sub2 = LogsSubscription(
        label="WETH transfers",
        address=weth_contract.address,
        topics=[weth_contract.events.Transfer().topic],
        handler=log_handler,
        parallelize=False,  # process sequentially
    )

    # this will also be processed in parallel
    sub3 = LogsSubscription(
        label="WETH approvals",
        address=weth_contract.address,
        topics=[weth_contract.events.Approval().topic],
        handler=approval_handler,
    )

    await w3.subscription_manager.subscribe([sub1, sub2, sub3])


FAQ
---


How can I subscribe to additional events once my application is running?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wherever you have a ``w3`` instance of the ``AsyncWeb3`` object, you can use the ``subscription_manager`` to subscribe to new events.

For example, the handler of one subscription could initialize a new subscription:

.. code-block:: python

    async def log_handler(
        handler_context: LogsSubscriptionContext,
    ) -> None:
        log_receipt = handler_context.result
        print(f"Log receipt: {log_receipt}\n")

        # reference the w3 instance
        w3 = handler_context.async_w3

        # initialize a new subscription
        await w3.subscription_manager.subscribe(
            NewHeadsSubscription(handler=new_heads_handler)
        )
