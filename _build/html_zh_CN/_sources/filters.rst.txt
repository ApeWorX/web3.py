.. _filtering:

Events and Logs
===============

If you're on this page, you're likely looking for an answer to this question:
**How do I know when a specific contract is used?** You have several options:

1. Query blocks for transactions that include the contract address in the ``"to"`` field.
   This contrived example is searching the latest block for any transactions sent to the
   WETH_ contract.

.. code-block:: python

   WETH_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

   block = w3.eth.get_block('latest')
   for tx_hash in block.transactions:
       tx = w3.eth.get_transaction(tx_hash)
       if tx['to'] == WETH_ADDRESS:
           print(f'Found interaction with WETH contract! {tx}')

2. Query for logs emitted by a contract. After instantiating a web3.py Contract object,
   you can :ref:`fetch logs <contract_get_logs>` for any event listed in the ABI.  In this
   example, we query for ``Transfer`` events in the latest block and log out the results.

.. code-block:: python

   WETH_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
   WETH_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'

   weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=WETH_ABI)

   # fetch transfer events in the last block
   logs = weth_contract.events.Transfer().get_logs(from_block=w3.eth.block_number)

   for log in logs:
      print(f"Transfer of {w3.from_wei(log.args.wad, 'ether')} WETH from {log.args.src} to {log.args.dst}")

See an advanced example of fetching log history :ref:`here <advanced_token_fetch>`.

3. Subscribe to events for real-time updates. When using a persistent connection provider
   (:class:`~web3.providers.persistent.WebSocketProvider` or
   :class:`~web3.providers.persistent.AsyncIPCProvider`), the
   :meth:`subscribe() <web3.eth.Eth.subscribe>` method can be used to establish a new
   event subscription. This example subscribes to ``Transfer`` events of the WETH contract.

  .. code-block:: python

    import asyncio
    from web3 import AsyncWeb3, WebSocketProvider
    from eth_abi.abi import decode

    WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


    async def subscribe_to_transfer_events():
        async with AsyncWeb3(WebSocketProvider("...")) as w3:
            transfer_event_topic = w3.keccak(text="Transfer(address,address,uint256)")
            filter_params = {
                "address": WETH_ADDRESS,
                "topics": [transfer_event_topic],
            }
            subscription_id = await w3.eth.subscribe("logs", filter_params)
            print(f"Subscribing to transfer events for WETH at {subscription_id}")

            async for payload in w3.socket.process_subscriptions():
                result = payload["result"]

                from_addr = decode(["address"], result["topics"][1])[0]
                to_addr = decode(["address"], result["topics"][2])[0]
                amount = decode(["uint256"], result["data"])[0]
                print(f"{w3.from_wei(amount, 'ether')} WETH from {from_addr} to {to_addr}")

    asyncio.run(subscribe_to_transfer_events())


  For more usage examples see the docs on :ref:`subscription-examples`.

4. Use a filter.

.. warning ::

  While filters can be a very convenient way to monitor for blocks, transactions, or
  events, they are notoriously unreliable. Both remote and locally hosted nodes have
  a reputation for occasionally dropping filters, and some remote node providers don't
  support filter-related RPC calls at all.

.. py:module:: web3.utils.filters

The :meth:`web3.eth.Eth.filter` method can be used to set up filters for:

* Pending Transactions: ``w3.eth.filter("pending")``

* New Blocks ``w3.eth.filter("latest")``

* Event Logs

    Through the contract instance api:

    .. code-block:: python

        event_filter = my_contract.events.myEvent.create_filter(from_block='latest', argument_filters={'arg1':10})

    Or built manually by supplying `valid filter params <https://github.com/ethereum/execution-apis/blob/bea0266c42919a2fb3ee524fb91e624a23bc17c5/src/schemas/filter.json#L28>`_:

    .. code-block:: python

        event_filter = w3.eth.filter({"address": contract_address})

* Attaching to an existing filter

    .. code-block:: python

        existing_filter = w3.eth.filter(filter_id="0x0")

.. note ::

    Creating event filters requires that your Ethereum node has an API support enabled for filters.
    Note that Infura support for filters does not offer access to `pending` filters.
    To get event logs on other stateless nodes please see :class:`web3.contract.ContractEvents`.



Filter Class
------------

.. py:class:: Filter(web3, filter_id)

.. py:attribute:: Filter.filter_id

    The ``filter_id`` for this filter as returned by the ``eth_newFilter`` RPC
    method when this filter was created.


.. py:method:: Filter.get_new_entries()

    Retrieve new entries for this filter.

    Logs will be retrieved using the
    :func:`web3.eth.Eth.get_filter_changes` which returns only new entries since the last
    poll.


.. py:method:: Filter.get_all_entries()

    Retrieve all entries for this filter.

    Logs will be retrieved using the
    :func:`web3.eth.Eth.get_filter_logs` which returns all entries that match the given
    filter.


.. py:method:: Filter.format_entry(entry)

    Hook for subclasses to modify the format of the log entries this filter
    returns, or passes to its callback functions.

    By default this returns the ``entry`` parameter unmodified.


.. py:method:: Filter.is_valid_entry(entry)

    Hook for subclasses to add additional programmatic filtering.  The default
    implementation always returns ``True``.


Block and Transaction Filter Classes
------------------------------------

.. py:class:: BlockFilter(...)

``BlockFilter`` is a subclass of :class:`Filter`.

You can setup a filter for new blocks using ``web3.eth.filter('latest')`` which
will return a new :class:`BlockFilter` object.

    .. code-block:: python

        new_block_filter = w3.eth.filter('latest')
        new_block_filter.get_new_entries()

    .. note::

        ``"safe"`` and ``"finalized"`` block identifiers are not yet supported for
        ``eth_newBlockFilter``.

.. py:class:: TransactionFilter(...)

``TransactionFilter`` is a subclass of :class:`Filter`.

You can setup a filter for new blocks using ``web3.eth.filter('pending')`` which
will return a new :class:`TransactionFilter` object.

    .. code-block:: python

        new_transaction_filter = w3.eth.filter('pending')
        new_transaction_filter.get_new_entries()


Event Log Filters
-----------------

You can set up a filter for event logs using the web3.py contract api:
:meth:`web3.contract.Contract.events.your_event_name.create_filter`, which provides some conveniences for
creating event log filters. Refer to the following example:

    .. code-block:: python

        event_filter = my_contract.events.<event_name>.create_filter(from_block="latest", argument_filters={'arg1':10})
        event_filter.get_new_entries()

See :meth:`web3.contract.Contract.events.your_event_name.create_filter()` documentation for more information.

You can set up an event log filter like the one above with ``web3.eth.filter`` by supplying a
dictionary containing the standard filter parameters. Assuming that ``arg1`` is indexed, the
equivalent filter creation would look like:

    .. code-block:: python

        event_signature_hash = web3.keccak(text="eventName(uint32)").hex()
        event_filter = web3.eth.filter({
            "address": myContract_address,
            "topics": [event_signature_hash,
                       "0x000000000000000000000000000000000000000000000000000000000000000a"],
            })

The ``topics`` argument is order-dependent. For non-anonymous events, the first item in the topic list is always the keccack hash of the event signature. Subsequent topic items are the hex encoded values for indexed event arguments. In the above example, the second item is the ``arg1`` value ``10`` encoded to its hex string representation.

In addition to being order-dependent, there are a few more points to recognize when specifying topic filters:

    Given a transaction log with topics [A, B], the following topic filters will yield a match:

    - [] "anything"
    - [A] "A in first position (and anything after)"
    - [None, B] "anything in first position AND B in second position (and anything after)"
    - [A, B] "A in first position AND B in second position (and anything after)"
    - [[A, B], [A, B]] "(A OR B) in first position AND (A OR B) in second position (and anything after)"

See the JSON-RPC documentation for `eth_newFilter <https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_newfilter>`_ more information on the standard filter parameters.

    .. note::

        Though ``"finalized"`` and ``"safe"`` block identifiers are not yet part of the
        specifications for ``eth_newFilter``, they are supported by web3.py and may or
        may not yield expected results depending on the node being accessed.

Creating a log filter by either of the above methods will return a :class:`LogFilter` instance.

.. py:class:: LogFilter(web3, filter_id, log_entry_formatter=None, data_filter_set=None)

The :py:class:`LogFilter` class is a subclass of :class:`Filter`.  See the :class:`Filter`
documentation for inherited methods.

:class:`LogFilter` provides the following additional
methods:

.. py:method:: LogFilter.set_data_filters(data_filter_set)

Provides a means to filter on the log data, in other words the ability to filter on values from
un-indexed event arguments. The parameter ``data_filter_set`` should be a list or set of 32-byte hex encoded values.

Examples: Listening For Events
------------------------------

Synchronous
~~~~~~~~~~~

    .. code-block:: python

        from web3 import Web3, IPCProvider
        import time

        # instantiate Web3 instance
        w3 = Web3(IPCProvider(...))

        def handle_event(event):
            print(event)

        def log_loop(event_filter, poll_interval):
            while True:
                for event in event_filter.get_new_entries():
                    handle_event(event)
                time.sleep(poll_interval)

        def main():
            block_filter = w3.eth.filter('latest')
            log_loop(block_filter, 2)

        if __name__ == '__main__':
            main()

.. _asynchronous_filters:

Asynchronous Filter Polling
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting with web3 version 4, the ``watch`` method was taken out of the web3 filter objects.
There are many decisions to be made when designing a system regarding threading and concurrency.
Rather than force a decision, web3 leaves these choices up to the user. Below are some example
implementations of asynchronous filter-event handling that can serve as starting points.

Single threaded concurrency with ``async`` and ``await``
````````````````````````````````````````````````````````

Beginning in python 3.5, the ``async`` and ``await`` built-in keywords were added.  These provide a
shared api for coroutines that can be utilized by modules such as the built-in asyncio_.  Below is
an example event loop using asyncio_, that polls multiple web3 filter object, and passes new
entries to a handler.

        .. code-block:: python

            from web3 import Web3, IPCProvider
            import asyncio

            # instantiate Web3 instance
            w3 = Web3(IPCProvider(...))

            def handle_event(event):
                print(event)
                # and whatever

            async def log_loop(event_filter, poll_interval):
                while True:
                    for event in event_filter.get_new_entries():
                        handle_event(event)
                    await asyncio.sleep(poll_interval)

            def main():
                block_filter = w3.eth.filter('latest')
                tx_filter = w3.eth.filter('pending')
                loop = asyncio.get_event_loop()
                try:
                    loop.run_until_complete(
                        asyncio.gather(
                            log_loop(block_filter, 2),
                            log_loop(tx_filter, 2)))
                finally:
                    loop.close()

            if __name__ == '__main__':
                main()

    Read the asyncio_ documentation for more information.

Running the event loop in a separate thread
```````````````````````````````````````````

Here is an extended version of above example, where the event loop is run in a separate thread,
releasing the ``main`` function for other tasks.

        .. code-block:: python

            from web3 import Web3, IPCProvider
            from threading import Thread
            import time

            # instantiate Web3 instance
            w3 = Web3(IPCProvider(...))

            def handle_event(event):
                print(event)
                # and whatever


            def log_loop(event_filter, poll_interval):
                while True:
                    for event in event_filter.get_new_entries():
                        handle_event(event)
                    time.sleep(poll_interval)


            def main():
                block_filter = w3.eth.filter('latest')
                worker = Thread(target=log_loop, args=(block_filter, 5), daemon=True)
                worker.start()
                    # .. do some other stuff

            if __name__ == '__main__':
                main()

Here are some other libraries that provide frameworks for writing asynchronous python:

    * gevent_
    * twisted_
    * celery_


Examples
--------

.. _advanced_token_fetch:

Advanced example: Fetching all token transfer events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, we show how to fetch all events of a certain event type from the Ethereum blockchain. There are three challenges when working with a large set of events:

* How to incrementally update an existing database of fetched events

* How to deal with interruptions in long running processes

* How to deal with `eth_getLogs` JSON-RPC call query limitations

* How to handle Ethereum minor chain reorganisations in (near) real-time data


eth_getLogs limitations
```````````````````````

Ethereum JSON-RPC API servers, like Geth, do not provide an easy way to paginate over events, only over blocks. There's no request that can find the first block with an event or how many events occur within a range of blocks. The only feedback the JSON-RPC service will give you is whether the ``eth_getLogs`` call failed.

In this example script, we provide two kinds of heuristics to deal with this issue. The script scans events in a chunk of blocks (start block number - end block number). Then it uses two methods to find how many events there are likely to be in a block window:

* Dynamically set the block range window size, while never exceeding a threshold (e.g., 10,000 blocks).

* In the case of ``eth_getLogs``, the JSON-RPC call gives a timeout error, decrease the end block number and tries again with a smaller block range window.


Example code
````````````

The following example code is divided into a reusable ``EventScanner`` class and then a demo script that:

* fetches all transfer events for `RCC token <https://etherscan.io/token/0x9b6443b0fb9c241a7fdac375595cea13e6b7807a>`_,

* can incrementally run again to check if there are new events,

* handles interruptions (e.g., CTRL+C abort) gracefully,

* writes all ``Transfer`` events in a single file JSON database, so that other process can consume them,

* uses the `tqdm <https://pypi.org/project/tqdm/>`_ library for progress bar output in a console,

* only supports ``HTTPS`` providers, because JSON-RPC retry logic depends on the implementation details of the underlying protocol,

* disables the default exception retry configuration because it does not know how to handle the shrinking block range window for ``eth_getLogs``, and

* consumes around 20k JSON-RPC API calls.

The script can be run with: ``python ./eventscanner.py <your JSON-RPC API URL>``.

.. code-block:: python

    """A stateful event scanner for Ethereum-based blockchains using web3.py.

    With the stateful mechanism, you can do one batch scan or incremental scans,
    where events are added wherever the scanner left off.
    """

    import datetime
    import time
    import logging
    from abc import ABC, abstractmethod
    from typing import Tuple, Optional, Callable, List, Iterable, Dict, Any

    from web3 import Web3
    from web3.contract import Contract
    from web3.datastructures import AttributeDict
    from web3.exceptions import BlockNotFound
    from eth_abi.codec import ABICodec

    # Currently this method is not exposed over official web3 API,
    # but we need it to construct eth_getLogs parameters
    from web3._utils.filters import construct_event_filter_params
    from web3._utils.events import get_event_data


    logger = logging.getLogger(__name__)


    class EventScannerState(ABC):
        """Application state that remembers what blocks we have scanned in the case of crash.
        """

        @abstractmethod
        def get_last_scanned_block(self) -> int:
            """Number of the last block we have scanned on the previous cycle.

            :return: 0 if no blocks scanned yet
            """

        @abstractmethod
        def start_chunk(self, block_number: int):
            """Scanner is about to ask data of multiple blocks over JSON-RPC.

            Start a database session if needed.
            """

        @abstractmethod
        def end_chunk(self, block_number: int):
            """Scanner finished a number of blocks.

            Persistent any data in your state now.
            """

        @abstractmethod
        def process_event(self, block_when: datetime.datetime, event: AttributeDict) -> object:
            """Process incoming events.

            This function takes raw events from Web3, transforms them to your application internal
            format, then saves them in a database or some other state.

            :param block_when: When this block was mined

            :param event: Symbolic dictionary of the event data

            :return: Internal state structure that is the result of event transformation.
            """

        @abstractmethod
        def delete_data(self, since_block: int) -> int:
            """Delete any data since this block was scanned.

            Purges any potential minor reorg data.
            """


    class EventScanner:
        """Scan blockchain for events and try not to abuse JSON-RPC API too much.

        Can be used for real-time scans, as it detects minor chain reorganisation and rescans.
        Unlike the easy web3.contract.Contract, this scanner can scan events from multiple contracts at once.
        For example, you can get all transfers from all tokens in the same scan.

        You *should* disable the default ``exception_retry_configuration`` on your provider for Web3,
        because it cannot correctly throttle and decrease the `eth_getLogs` block number range.
        """

        def __init__(self, w3: Web3, contract: Contract, state: EventScannerState, events: List, filters: Dict[str, Any],
                     max_chunk_scan_size: int = 10000, max_request_retries: int = 30, request_retry_seconds: float = 3.0):
            """
            :param contract: Contract
            :param events: List of web3 Event we scan
            :param filters: Filters passed to get_logs
            :param max_chunk_scan_size: JSON-RPC API limit in the number of blocks we query. (Recommendation: 10,000 for mainnet, 500,000 for testnets)
            :param max_request_retries: How many times we try to reattempt a failed JSON-RPC call
            :param request_retry_seconds: Delay between failed requests to let JSON-RPC server to recover
            """

            self.logger = logger
            self.contract = contract
            self.w3 = w3
            self.state = state
            self.events = events
            self.filters = filters

            # Our JSON-RPC throttling parameters
            self.min_scan_chunk_size = 10  # 12 s/block = 120 seconds period
            self.max_scan_chunk_size = max_chunk_scan_size
            self.max_request_retries = max_request_retries
            self.request_retry_seconds = request_retry_seconds

            # Factor how fast we increase the chunk size if results are found
            # # (slow down scan after starting to get hits)
            self.chunk_size_decrease = 0.5

            # Factor how fast we increase chunk size if no results are found
            self.chunk_size_increase = 2.0

        @property
        def address(self):
            return self.token_address

        def get_block_timestamp(self, block_num) -> datetime.datetime:
            """Get Ethereum block timestamp"""
            try:
                block_info = self.w3.eth.get_block(block_num)
            except BlockNotFound:
                # Block was not mined yet,
                # minor chain reorganisation?
                return None
            last_time = block_info["timestamp"]
            return datetime.datetime.utcfromtimestamp(last_time)

        def get_suggested_scan_start_block(self):
            """Get where we should start to scan for new token events.

            If there are no prior scans, start from block 1.
            Otherwise, start from the last end block minus ten blocks.
            We rescan the last ten scanned blocks in the case there were forks to avoid
            misaccounting due to minor single block works (happens once in an hour in Ethereum).
            These heuristics could be made more robust, but this is for the sake of simple reference implementation.
            """

            end_block = self.get_last_scanned_block()
            if end_block:
                return max(1, end_block - self.NUM_BLOCKS_RESCAN_FOR_FORKS)
            return 1

        def get_suggested_scan_end_block(self):
            """Get the last mined block on Ethereum chain we are following."""

            # Do not scan all the way to the final block, as this
            # block might not be mined yet
            return self.w3.eth.block_number - 1

        def get_last_scanned_block(self) -> int:
            return self.state.get_last_scanned_block()

        def delete_potentially_forked_block_data(self, after_block: int):
            """Purge old data in the case of blockchain reorganisation."""
            self.state.delete_data(after_block)

        def scan_chunk(self, start_block, end_block) -> Tuple[int, datetime.datetime, list]:
            """Read and process events between to block numbers.

            Dynamically decrease the size of the chunk if the case JSON-RPC server pukes out.

            :return: tuple(actual end block number, when this block was mined, processed events)
            """

            block_timestamps = {}
            get_block_timestamp = self.get_block_timestamp

            # Cache block timestamps to reduce some RPC overhead
            # Real solution might include smarter models around block
            def get_block_when(block_num):
                if block_num not in block_timestamps:
                    block_timestamps[block_num] = get_block_timestamp(block_num)
                return block_timestamps[block_num]

            all_processed = []

            for event_type in self.events:

                # Callable that takes care of the underlying web3 call
                def _fetch_events(_start_block, _end_block):
                    return _fetch_events_for_all_contracts(self.w3,
                                                           event_type,
                                                           self.filters,
                                                           from_block=_start_block,
                                                           to_block=_end_block)

                # Do `n` retries on `eth_getLogs`,
                # throttle down block range if needed
                end_block, events = _retry_web3_call(
                    _fetch_events,
                    start_block=start_block,
                    end_block=end_block,
                    retries=self.max_request_retries,
                    delay=self.request_retry_seconds)

                for evt in events:
                    idx = evt["logIndex"]  # Integer of the log index position in the block, null when its pending

                    # We cannot avoid minor chain reorganisations, but
                    # at least we must avoid blocks that are not mined yet
                    assert idx is not None, "Somehow tried to scan a pending block"

                    block_number = evt["blockNumber"]

                    # Get UTC time when this event happened (block mined timestamp)
                    # from our in-memory cache
                    block_when = get_block_when(block_number)

                    logger.debug("Processing event %s, block: %s count: %s", evt['event'], block_number, block_number)
                    processed = self.state.process_event(block_when, evt)
                    all_processed.append(processed)

            end_block_timestamp = get_block_when(end_block)
            return end_block, end_block_timestamp, all_processed

        def estimate_next_chunk_size(self, current_chuck_size: int, event_found_count: int):
            """Try to figure out optimal chunk size

            Our scanner might need to scan the whole blockchain for all events

            * We want to minimize API calls over empty blocks

            * We want to make sure that one scan chunk does not try to process too many entries once, as we try to control commit buffer size and potentially asynchronous busy loop

            * Do not overload node serving JSON-RPC API by asking data for too many events at a time

            Currently Ethereum JSON-API does not have an API to tell when a first event occurred in a blockchain
            and our heuristics try to accelerate block fetching (chunk size) until we see the first event.

            These heuristics exponentially increase the scan chunk size depending on if we are seeing events or not.
            When any transfers are encountered, we are back to scanning only a few blocks at a time.
            It does not make sense to do a full chain scan starting from block 1, doing one JSON-RPC call per 20 blocks.
            """

            if event_found_count > 0:
                # When we encounter first events, reset the chunk size window
                current_chuck_size = self.min_scan_chunk_size
            else:
                current_chuck_size *= self.chunk_size_increase

            current_chuck_size = max(self.min_scan_chunk_size, current_chuck_size)
            current_chuck_size = min(self.max_scan_chunk_size, current_chuck_size)
            return int(current_chuck_size)

        def scan(self, start_block, end_block, start_chunk_size=20, progress_callback=Optional[Callable]) -> Tuple[
            list, int]:
            """Perform a token balances scan.

            Assumes all balances in the database are valid before start_block (no forks sneaked in).

            :param start_block: The first block included in the scan

            :param end_block: The last block included in the scan

            :param start_chunk_size: How many blocks we try to fetch over JSON-RPC on the first attempt

            :param progress_callback: If this is an UI application, update the progress of the scan

            :return: [All processed events, number of chunks used]
            """

            assert start_block <= end_block

            current_block = start_block

            # Scan in chunks, commit between
            chunk_size = start_chunk_size
            last_scan_duration = last_logs_found = 0
            total_chunks_scanned = 0

            # All processed entries we got on this scan cycle
            all_processed = []

            while current_block <= end_block:

                self.state.start_chunk(current_block, chunk_size)

                # Print some diagnostics to logs to try to fiddle with real world JSON-RPC API performance
                estimated_end_block = min(current_block + chunk_size, end_block)
                logger.debug(
                    "Scanning token transfers for blocks: %s - %s, chunk size %s, last chunk scan took %s, last logs found %s",
                    current_block, estimated_end_block, chunk_size, last_scan_duration, last_logs_found,
                )

                start = time.time()
                actual_end_block, end_block_timestamp, new_entries = self.scan_chunk(current_block, estimated_end_block)

                # Where does our current chunk scan ends - are we out of chain yet?
                current_end = actual_end_block

                last_scan_duration = time.time() - start
                all_processed += new_entries

                # Print progress bar
                if progress_callback:
                    progress_callback(start_block, end_block, current_block, end_block_timestamp, chunk_size, len(new_entries))

                # Try to guess how many blocks to fetch over `eth_getLogs` API next time
                chunk_size = self.estimate_next_chunk_size(chunk_size, len(new_entries))

                # Set where the next chunk starts
                current_block = current_end + 1
                total_chunks_scanned += 1
                self.state.end_chunk(current_end)

            return all_processed, total_chunks_scanned


    def _retry_web3_call(func, start_block, end_block, retries, delay) -> Tuple[int, list]:
        """A custom retry loop to throttle down block range.

        If our JSON-RPC server cannot serve all incoming `eth_getLogs` in a single request,
        we retry and throttle down block range for every retry.

        For example, Go Ethereum does not indicate what is an acceptable response size.
        It just fails on the server-side with a "context was cancelled" warning.

        :param func: A callable that triggers Ethereum JSON-RPC, as func(start_block, end_block)
        :param start_block: The initial start block of the block range
        :param end_block: The initial start block of the block range
        :param retries: How many times we retry
        :param delay: Time to sleep between retries
        """
        for i in range(retries):
            try:
                return end_block, func(start_block, end_block)
            except Exception as e:
                # Assume this is HTTPConnectionPool(host='localhost', port=8545): Read timed out. (read timeout=10)
                # from Go Ethereum. This translates to the error "context was cancelled" on the server side:
                # https://github.com/ethereum/go-ethereum/issues/20426
                if i < retries - 1:
                    # Give some more verbose info than the default middleware
                    logger.warning(
                        "Retrying events for block range %s - %s (%s) failed with %s , retrying in %s seconds",
                        start_block, end_block, end_block-start_block, e, delay,
                    )
                    # Decrease the `eth_getBlocks` range
                    end_block = start_block + ((end_block - start_block) // 2)
                    # Let the JSON-RPC to recover e.g. from restart
                    time.sleep(delay)
                    continue
                else:
                    logger.warning("Out of retries")
                    raise


    def _fetch_events_for_all_contracts(
            w3,
            event,
            argument_filters: Dict[str, Any],
            from_block: int,
            to_block: int) -> Iterable:
        """Get events using eth_getLogs API.

        This method is detached from any contract instance.

        This is a stateless method, as opposed to create_filter.
        It can be safely called against nodes which do not provide `eth_newFilter` API, like Infura.
        """

        if from_block is None:
            raise Web3TypeError("Missing mandatory keyword argument to get_logs: from_block")

        # Currently no way to poke this using a public web3.py API.
        # This will return raw underlying ABI JSON object for the event
        abi = event._get_event_abi()

        # Depending on the Solidity version used to compile
        # the contract that uses the ABI,
        # it might have Solidity ABI encoding v1 or v2.
        # We just assume the default that you set on Web3 object here.
        # More information here https://eth-abi.readthedocs.io/en/latest/index.html
        codec: ABICodec = w3.codec

        # Here we need to poke a bit into Web3 internals, as this
        # functionality is not exposed by default.
        # Construct JSON-RPC raw filter presentation based on human readable Python descriptions
        # Namely, convert event names to their keccak signatures
        # More information here:
        # https://github.com/ethereum/web3.py/blob/e176ce0793dafdd0573acc8d4b76425b6eb604ca/web3/_utils/filters.py#L71
        data_filter_set, event_filter_params = construct_event_filter_params(
            abi,
            codec,
            address=argument_filters.get("address"),
            argument_filters=argument_filters,
            from_block=from_block,
            to_block=to_block
        )

        logger.debug("Querying eth_getLogs with the following parameters: %s", event_filter_params)

        # Call JSON-RPC API on your Ethereum node.
        # get_logs() returns raw AttributedDict entries
        logs = w3.eth.get_logs(event_filter_params)

        # Convert raw binary data to Python proxy objects as described by ABI
        all_events = []
        for log in logs:
            # Convert raw JSON-RPC log result to human readable event by using ABI data
            # More information how process_log works here
            # https://github.com/ethereum/web3.py/blob/fbaf1ad11b0c7fac09ba34baff2c256cffe0a148/web3/_utils/events.py#L200
            evt = get_event_data(codec, abi, log)
            # Note: This was originally yield,
            # but deferring the timeout exception caused the throttle logic not to work
            all_events.append(evt)
        return all_events


    if __name__ == "__main__":
        # Simple demo that scans all the token transfers of RCC token (11k).
        # The demo supports persistent state by using a JSON file.
        # You will need an Ethereum node for this.
        # Running this script will consume around 20k JSON-RPC calls.
        # With locally running Geth, the script takes 10 minutes.
        # The resulting JSON state file is 2.9 MB.
        import sys
        import json
        from web3.providers.rpc import HTTPProvider

        # We use tqdm library to render a nice progress bar in the console
        # https://pypi.org/project/tqdm/
        from tqdm import tqdm

        # RCC has around 11k Transfer events
        # https://etherscan.io/token/0x9b6443b0fb9c241a7fdac375595cea13e6b7807a
        RCC_ADDRESS = "0x9b6443b0fb9c241a7fdac375595cea13e6b7807a"

        # Reduced ERC-20 ABI, only Transfer event
        ABI = """[
            {
                "anonymous": false,
                "inputs": [
                    {
                        "indexed": true,
                        "name": "from",
                        "type": "address"
                    },
                    {
                        "indexed": true,
                        "name": "to",
                        "type": "address"
                    },
                    {
                        "indexed": false,
                        "name": "value",
                        "type": "uint256"
                    }
                ],
                "name": "Transfer",
                "type": "event"
            }
        ]
        """

        class JSONifiedState(EventScannerState):
            """Store the state of scanned blocks and all events.

            All state is an in-memory dict.
            Simple load/store massive JSON on start up.
            """

            def __init__(self):
                self.state = None
                self.fname = "test-state.json"
                # How many second ago we saved the JSON file
                self.last_save = 0

            def reset(self):
                """Create initial state of nothing scanned."""
                self.state = {
                    "last_scanned_block": 0,
                    "blocks": {},
                }

            def restore(self):
                """Restore the last scan state from a file."""
                try:
                    self.state = json.load(open(self.fname, "rt"))
                    print(f"Restored the state, previously {self.state['last_scanned_block']} blocks have been scanned")
                except (IOError, json.decoder.JSONDecodeError):
                    print("State starting from scratch")
                    self.reset()

            def save(self):
                """Save everything we have scanned so far in a file."""
                with open(self.fname, "wt") as f:
                    json.dump(self.state, f)
                self.last_save = time.time()

            #
            # EventScannerState methods implemented below
            #

            def get_last_scanned_block(self):
                """The number of the last block we have stored."""
                return self.state["last_scanned_block"]

            def delete_data(self, since_block):
                """Remove potentially reorganised blocks from the scan data."""
                for block_num in range(since_block, self.get_last_scanned_block()):
                    if block_num in self.state["blocks"]:
                        del self.state["blocks"][block_num]

            def start_chunk(self, block_number, chunk_size):
                pass

            def end_chunk(self, block_number):
                """Save at the end of each block, so we can resume in the case of a crash or CTRL+C"""
                # Next time the scanner is started we will resume from this block
                self.state["last_scanned_block"] = block_number

                # Save the database file for every minute
                if time.time() - self.last_save > 60:
                    self.save()

            def process_event(self, block_when: datetime.datetime, event: AttributeDict) -> str:
                """Record a ERC-20 transfer in our database."""
                # Events are keyed by their transaction hash and log index
                # One transaction may contain multiple events
                # and each one of those gets their own log index

                # event_name = event.event # "Transfer"
                log_index = event.logIndex  # Log index within the block
                # transaction_index = event.transactionIndex  # Transaction index within the block
                txhash = event.transactionHash.hex()  # Transaction hash
                block_number = event.blockNumber

                # Convert ERC-20 Transfer event to our internal format
                args = event["args"]
                transfer = {
                    "from": args["from"],
                    "to": args.to,
                    "value": args.value,
                    "timestamp": block_when.isoformat(),
                }

                # Create empty dict as the block that contains all transactions by txhash
                if block_number not in self.state["blocks"]:
                    self.state["blocks"][block_number] = {}

                block = self.state["blocks"][block_number]
                if txhash not in block:
                    # We have not yet recorded any transfers in this transaction
                    # (One transaction may contain multiple events if executed by a smart contract).
                    # Create a tx entry that contains all events by a log index
                    self.state["blocks"][block_number][txhash] = {}

                # Record ERC-20 transfer in our database
                self.state["blocks"][block_number][txhash][log_index] = transfer

                # Return a pointer that allows us to look up this event later if needed
                return f"{block_number}-{txhash}-{log_index}"

        def run():

            if len(sys.argv) < 2:
                print("Usage: eventscanner.py http://your-node-url")
                sys.exit(1)

            api_url = sys.argv[1]

            # Enable logs to the stdout.
            # DEBUG is very verbose level
            logging.basicConfig(level=logging.INFO)

            provider = HTTPProvider(api_url)

            # Disable the default JSON-RPC retry configuration
            # as it correctly cannot handle eth_getLogs block range
            provider.exception_retry_configuration = None

            w3 = Web3(provider)

            # Prepare stub ERC-20 contract object
            abi = json.loads(ABI)
            ERC20 = w3.eth.contract(abi=abi)

            # Restore/create our persistent state
            state = JSONifiedState()
            state.restore()

            # chain_id: int, w3: Web3, abi: Dict, state: EventScannerState, events: List, filters: Dict, max_chunk_scan_size: int=10000
            scanner = EventScanner(
                w3=w3,
                contract=ERC20,
                state=state,
                events=[ERC20.events.Transfer],
                filters={"address": RCC_ADDRESS},
                # How many maximum blocks at the time we request from JSON-RPC
                # and we are unlikely to exceed the response size limit of the JSON-RPC server
                max_chunk_scan_size=10000
            )

            # Assume we might have scanned the blocks all the way to the last Ethereum block
            # that mined a few seconds before the previous scan run ended.
            # Because there might have been a minor Ethereum chain reorganisations
            # since the last scan ended, we need to discard
            # the last few blocks from the previous scan results.
            chain_reorg_safety_blocks = 10
            scanner.delete_potentially_forked_block_data(state.get_last_scanned_block() - chain_reorg_safety_blocks)

            # Scan from [last block scanned] - [latest ethereum block]
            # Note that our chain reorg safety blocks cannot go negative
            start_block = max(state.get_last_scanned_block() - chain_reorg_safety_blocks, 0)
            end_block = scanner.get_suggested_scan_end_block()
            blocks_to_scan = end_block - start_block

            print(f"Scanning events from blocks {start_block} - {end_block}")

            # Render a progress bar in the console
            start = time.time()
            with tqdm(total=blocks_to_scan) as progress_bar:
                def _update_progress(start, end, current, current_block_timestamp, chunk_size, events_count):
                    if current_block_timestamp:
                        formatted_time = current_block_timestamp.strftime("%d-%m-%Y")
                    else:
                        formatted_time = "no block time available"
                    progress_bar.set_description(f"Current block: {current} ({formatted_time}), blocks in a scan batch: {chunk_size}, events processed in a batch {events_count}")
                    progress_bar.update(chunk_size)

                # Run the scan
                result, total_chunks_scanned = scanner.scan(start_block, end_block, progress_callback=_update_progress)

            state.save()
            duration = time.time() - start
            print(f"Scanned total {len(result)} Transfer events, in {duration} seconds, total {total_chunks_scanned} chunk scans performed")

        run()


.. _WETH: https://etherscan.io/token/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2#code
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _gevent: https://www.gevent.org/
.. _twisted: https://twistedmatrix.com/
.. _celery: https://www.celeryproject.org/
