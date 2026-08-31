Web3 Internals
==============


.. warning:: This section of the documentation is for advanced users.  You should probably stay away from these APIs if you don't know what you are doing.

The Web3 library has multiple layers of abstraction between the public api
exposed by the web3 object and the backend or node that web3 is connecting to.

* **Providers** are responsible for the actual communication with the
  blockchain such as sending JSON-RPC requests over HTTP or an IPC socket.
* **Middleware** provide hooks for monitoring and modifying requests and
  responses to and from the provider.
* **Managers** provide thread safety and primitives to allow for asynchronous usage of web3.

Here are some common things you might want to do with these APIs.

* Redirect certain RPC requests to different providers such as sending all
  *read* operations to a provider backed by a remote node and all *write* operations
  to a local node that you control.
* Transparently intercept transactions sent over ``eth_sendTransaction``, sign
  them locally, and then send them through ``eth_sendRawTransaction``.
* Modify the response from an RPC request so that it is returned in different
  format such as converting all integer values to their hexadecimal
  representation.
* Validate the inputs to RPC requests


Request Lifecycle
-----------------

Each web3 RPC call passes through these layers in the following manner.

.. code-block:: none

                   ***********    ************
                   | Request |    | Response |
                   ***********    ************
                       |                ^
                       v                |
                 +-----------------------------+
                 |           Manager           |
                 +-----------------------------+
                       |                ^
                       v                |
                 +-----------------------------+
                 |         Middleware          |
                 +-----------------------------+
                       |                ^
                       v                |
                 +-----------------------------+
                 |          Provider           |
                 +-----------------------------+


You can visualize this relationship like an onion, with the Provider at the
center. The request originates from the ``Manager``, outside of the onion, passing
down through each layer of the onion until it reaches the ``Provider`` at the
center. The ``Provider`` then handles the request, producing a response which will
then pass back out from the center of the onion, through each layer until it is
finally returned by the ``Manager``.


Providers
---------

A provider is responsible for all direct blockchain interactions.  In most
cases this means interacting with the JSON-RPC server for an ethereum node over
HTTP or an IPC socket.  There is however nothing which requires providers to be
RPC based, allowing for providers designed for testing purposes which use an
in-memory EVM to fulfill requests.


Writing your own Provider
~~~~~~~~~~~~~~~~~~~~~~~~~

Writing your own provider requires implementing two required methods as well as
setting the middleware the provider should use.


.. py:method:: BaseProvider.make_request(method, params)

    Each provider class **must** implement this method.  This method **should**
    return a JSON object with either a ``'result'`` key in the case of success,
    or an ``'error'`` key in the case of failure.


    * ``method``  This will be a string representing the JSON-RPC method that
      is being called such as ``'eth_sendTransaction'``.
    * ``params``  This will be a list or other iterable of the parameters for
      the JSON-RPC method being called.


.. py:method:: BaseProvider.is_connected(show_traceback=False)

    This function should return ``True`` or ``False`` depending on whether the
    provider should be considered *connected*.  For example, an IPC socket
    based provider should return ``True`` if the socket is open and ``False``
    if the socket is closed.

    If set to ``True``, the optional ``show_traceback`` boolean will raise a
    ``ProviderConnectionError`` and provide information on why the provider should
    not be considered *connected*.


.. py:attribute:: BaseProvider.middleware

    This should be an iterable of middleware.

You can set a new list of middleware by assigning to ``provider.middleware``,
with the first middleware that processes the request at the beginning of the list.


Provider Configurations
~~~~~~~~~~~~~~~~~~~~~~~

.. _request_caching:

Request Caching
```````````````

.. important::
    Familiarize yourself with the validation logic for request caching before
    enabling it. Since this feature often requires making additional requests under the
    hood to try to guarantee the validity of the data, it may create unnecessary
    overhead for your use case. Validation can be turned off by setting the
    ``request_cache_validation_threshold`` option to ``None``, caching all allowed
    requests, or configured for adjusting performance to your needs.


Request caching can be configured at the provider level via the following configuration
options on the provider instance:

- ``cache_allowed_requests: bool = False``
- ``cacheable_requests: Optional[Set[RPCEndpoint]]``
- ``request_cache_validation_threshold: Optional[Union[RequestCacheValidationThreshold, int]]``

For requests that don't rely on block data (e.g., ``eth_chainId``), enabling request
caching by setting the ``cache_allowed_requests`` option to ``True`` will cache all
responses. This is safe to do.

However, for requests that rely on block data (e.g., ``eth_getBlockByNumber``), it is
not safe to always cache their responses because block data can change - during a
chain reorganization or while finality has not been reached, for example. The
``request_cache_validation_threshold`` option allows configuring a safe threshold for
caching responses that depend on block data. By default, this option is configured
to internal values deemed "safe" for the chain id you are connected to. If you are
connected to mainnet Ethereum, this value is set to the ``finalized`` block number.
If you are connected to another chain, this value is set to a time interval in seconds,
from the current time, that is deemed "safe" for that chain's finality mechanism.

**It's important to understand that, in order to perform these validations, extra
requests are sometimes made to the node to get the appropriate information. For a
transaction request, for example, it is necessary to get the block information to
validate the transaction is beyond the safe threshold. This can create overhead,
especially for high-frequency requests. For this reason, it is important to understand
when to turn on caching and how to configure the validation appropriately for your
use case in order to avoid unnecessary overhead.**

We keep a list of some reasonable values for bigger chains and
use the time interval of 1 hour for everything else. Below is a list of the default
values for internally configured chains:

    - ETH: RequestCacheValidationThreshold.FINALIZED ("finalized" block)
    - ARB1: 7 days
    - ZKSYNC: 1 hour
    - OETH: 3 minutes
    - MATIC: 30 minutes
    - ZKEVM: 1 hour
    - BASE: 7 days
    - SCR: 1 hour
    - GNO: 5 minutes
    - AVAX: 2 minutes
    - BNB: 2 minutes
    - FTM: 1 minute

For Ethereum mainnet, for example, this means that a request's response will be cached
if the block number the request relies on is less than or equal to the ``finalized``
block number. If the block number exceeds the ``finalized`` block number, the response
won't be cached. For all others, the response will be cached if the block timestamp
related to the data that is being requested is older than or equal to the time interval
configured for that chain. For any chain not on this list, the default value is set to
1 hour (this includes all testnets).

This behavior can be modified by setting the ``request_cache_validation_threshold``
option to ``RequestCacheValidationThreshold.SAFE``, which uses the ``safe`` block as
the threshold (Ethereum mainnet only), to your own time interval in seconds (for any
chain, including mainnet Ethereum), or to ``None``, which disables any validation and
caches all requests (this is not recommended for non testnet chains). The
``RequestCacheValidationThreshold`` enum, for mainnet ``finalized`` and ``safe`` values,
is imported from the ``web3.utils`` module.

Note that the ``cacheable_requests`` option can be used to specify a set of RPC
endpoints that are allowed to be cached. By default, this option is set to an internal
list of deemed-safe-to-cache endpoints, excluding endpoints such as ``eth_call``, whose
responses can vary and are not safe to cache. The default list of cacheable requests is
below, with requests validated by the ``request_cache_validation_threshold`` option in
bold:

    - eth_chainId
    - web3_clientVersion
    - net_version
    - **eth_getBlockByNumber**
    - **eth_getRawTransactionByBlockNumberAndIndex**
    - **eth_getBlockTransactionCountByNumber**
    - **eth_getUncleByBlockNumberAndIndex**
    - **eth_getUncleCountByBlockNumber**
    - **eth_getBlockByHash**
    - **eth_getTransactionByHash**
    - **eth_getTransactionByBlockNumberAndIndex**
    - **eth_getTransactionByBlockHashAndIndex**
    - **eth_getBlockTransactionCountByHash**
    - **eth_getRawTransactionByBlockHashAndIndex**
    - **eth_getUncleByBlockHashAndIndex**
    - **eth_getUncleCountByBlockHash**

.. code-block:: python

    from web3 import Web3, HTTPProvider
    from web3.utils import RequestCacheValidationThreshold

    w3 = Web3(HTTPProvider(
        endpoint_uri="...",

        # optional flag to turn on cached requests, defaults to ``False``
        cache_allowed_requests=True,

        # optional, defaults to an internal list of deemed-safe-to-cache endpoints (see above)
        cacheable_requests={"eth_chainId", "eth_getBlockByNumber"},

        # optional, defaults to a value that is based on the chain id (see above)
        request_cache_validation_threshold=60 * 60,  # 1 hour
        # request_cache_validation_threshold=RequestCacheValidationThreshold.SAFE,  # Ethereum mainnet only
    ))

.. _http_retry_requests:

Retry Requests for HTTP Providers
`````````````````````````````````

``HTTPProvider`` and ``AsyncHTTPProvider`` instances retry certain requests by default
on exceptions. This can be configured via the ``exception_retry_configuration``
property on the provider instance, which takes a
:class:`~web3.providers.rpc.utils.ExceptionRetryConfiguration` class as its value. The
retry mechanism employs an exponential backoff strategy, starting from the initial
value determined by the ``backoff_factor``, and doubling the delay with each attempt,
up to the ``retries`` value. Below is an example showing the default options for the
retry configuration and how to override them.


.. py:class:: web3.providers.rpc.utils.ExceptionRetryConfiguration

    .. py:attribute:: errors

        A tuple of exceptions that the provider should retry on. The default is
        ``HTTPProvider``: ``(ConnectionError, requests.HTTPError, requests.Timeout)``
        and ``AsyncHTTPProvider``: ``(aiohttp.ClientError, asyncio.TimeoutError)``.

    .. py:attribute:: retries

        The number of retries to attempt. The default is 5.

    .. py:attribute:: backoff_factor

        The initial delay multiplier, which doubles with each retry attempt. The default
        is 0.125.

    .. py:attribute:: method_allowlist

        A list of retryable methods. The default is an in-house list of deemed-safe-to-
        retry methods.

.. code-block:: python

    from web3 import Web3, HTTPProvider
    from web3.providers.rpc.utils import (
        REQUEST_RETRY_ALLOWLIST,
        ExceptionRetryConfiguration,
    )

    w3 = Web3(HTTPProvider(
        endpoint_uri="...",
        exception_retry_configuration=ExceptionRetryConfiguration(
            errors=DEFAULT_EXCEPTIONS,

            # number of retries to attempt
            retries=5,

            # initial delay multiplier, doubles with each retry attempt
            backoff_factor=0.125,

            # an in-house default list of retryable methods
            method_allowlist=REQUEST_RETRY_ALLOWLIST,
        ),
    ))

For the different http providers, ``DEFAULT_EXCEPTIONS`` is defined as:

- ``HTTPProvider``: ``(ConnectionError, requests.HTTPError, requests.Timeout)``
- ``AsyncHTTPProvider``: ``(ConnectionError, aiohttp.ClientError, asyncio.TimeoutError)``

Setting ``retry_configuration`` to ``None`` will disable retries on exceptions for the
provider instance.

.. code-block:: python

    from web3 import Web3, HTTPProvider

    w3 = Web3(HTTPProvider(endpoint_uri="...", retry_configuration=None)



Managers
--------

The Manager acts as a gatekeeper for the request/response lifecycle.  It is
unlikely that you will need to change the Manager as most functionality can be
implemented in the Middleware layer.

.. _internals__persistent_connection_providers:

Request Processing for Persistent Connection Providers
------------------------------------------------------

.. py:class:: web3.providers.persistent.request_processor.RequestProcessor

The ``RequestProcessor`` class is responsible for the storing and syncing up of
asynchronous requests to responses for a ``PersistentConnectionProvider``. The
:class:`~web3.providers.persistent.WebSocketProvider` and the
:class:`~web3.providers.persistent.AsyncIPCProvider` are two persistent connection
providers. In order to send a request and receive a response to that same request,
``PersistentConnectionProvider`` instances have to match request *id* values to
response *id* values coming back from the socket connection. Any provider that does
not adhere to the `JSON-RPC 2.0 specification <https://www.jsonrpc.org/specification>`_
in this way will not work with ``PersistentConnectionProvider`` instances. The specifics
of how the request processor handles this are outlined below.

Listening for Responses
~~~~~~~~~~~~~~~~~~~~~~~

Implementations of the ``PersistentConnectionProvider`` class have a message listener
background task that is called when the socket connection is established. This task
is responsible for listening for any and all messages coming in over the socket
connection and storing them in the ``RequestProcessor`` instance internal to the
``PersistentConnectionProvider`` instance. The ``RequestProcessor`` instance is
responsible for storing the messages in the correct cache, either the one-to-one cache
or the one-to-many (subscriptions) queue, depending on whether the message has a
JSON-RPC *id* value or not.


One-To-One Requests
~~~~~~~~~~~~~~~~~~~

One-to-one requests can be summarized as any request that expects only one response
back. An example is using the ``eth`` module API to request the latest block number.

.. code-block:: python

    >>> async def ws_one_to_one_example():
    ...     async with AsyncWeb3(WebSocketProvider(f"ws://127.0.0.1:8546")) as w3:
    ...         # make a request and expect a single response returned on the same line
    ...         latest_block_num = await w3.eth.block_number

    >>> asyncio.run(ws_one_to_one_example())

With persistent socket connections, we have to call ``send()`` and asynchronously
receive responses via another means, generally by calling ``recv()`` or by iterating
on the socket connection for messages. As outlined above, the
``PersistentConnectionProvider`` class has a message listener background task that
handles the receiving of messages.

Due to this asynchronous nature of sending and receiving, in order to make one-to-one
request-to-response calls work, we have to save the request information somewhere so
that, when the response is received, we can match it to the original request that was
made (i.e. the request with a matching *id* to the response that was received). The
stored request information is then used to process the response when it is received,
piping it through the response formatters and middleware internal to the *web3.py*
library.

In order to store the request information, the ``RequestProcessor`` class has an
internal ``RequestInformation`` cache. The ``RequestInformation`` class saves important
information about a request.

.. py:class:: web3._utils.caching.RequestInformation

    .. py:attribute:: method

        The name of the method - e.g. "eth_subscribe".

    .. py:attribute:: params

        The params used when the call was made - e.g. ("newPendingTransactions", True).

    .. py:attribute:: response_formatters

        The formatters that will be used to process the response.

    .. py:attribute:: middleware_response_processors

        Any middleware that processes responses that is present on the instance at the
        time of the request is appended here, in order, so the response may be piped
        through that logic when it comes in.

    .. py:attribute:: subscription_id

        If the request is an ``eth_subscribe`` request, rather than
        popping this information from the cache when the response to the subscription call
        comes in (i.e. the subscription *id*), we save the subscription id with the
        request information so that we can correctly process all subscription messages
        that come in with that subscription *id*. For one-to-one request-to-response
        calls, this value is always ``None``.

One-to-one responses, those that include a JSON-RPC *id* in the response object, are
stored in an internal ``SimpleCache`` class, isolated from any one-to-many responses.
When the ``PersistentConnectionProvider`` is looking for a response internally, it will
expect the message listener task to store the response in this cache. Since the request
*id* is used in the cache key generation, it will then look for a cache key that matches
the response *id* with that of the request *id*. If the cache key is found, the response
is processed and returned to the user. If the cache key is not found, the operation will
time out and raise a ``TimeExhausted`` exception. This timeout can be configured by the
user when instantiating the ``PersistentConnectionProvider`` instance via the
``response_timeout`` keyword argument.

One-To-Many Requests
~~~~~~~~~~~~~~~~~~~~

One-to-many requests can be summarized by any request that expects many responses as a
result of the initial request. The only current example is the ``eth_subscribe``
request. The initial ``eth_subscribe`` request expects only one response, the
subscription *id* value, but it also expects to receive many ``eth_subscription``
messages if and when the request is successful. For this reason, the original request
is considered a one-to-one request so that a subscription *id* can be returned to the
user on the same line. The many responses this call will produce can be handled in one
of a few ways.

The recommended way to handle one-to-many responses is to use the subscription manager
API. The subscription manager API is a public API on the ``AsyncWeb3`` class, when
connected to a ``PersistentConnectionProvider`` instance, that allows the user to
subscribe to a subscription and handle the many responses asynchronously. The
``subscription_manager`` instance is responsible for handling the many responses that
come in over the socket connection, as long as handlers are passed to each subscription
call. The subscription manager can also be used to unsubscribe from a subscription when
the user is done with it.

.. code-block:: python

    >>> async def new_heads_handler(
    ...     handler_context: NewHeadsSubscriptionContext,
    ... ) -> None:
    ...     result = handler_context.result
    ...     print(f"New block header: {result}\n")
    ...     if result["number"] > 1234567:
    ...         await handler_context.subscription.unsubscribe()

    >>> async def ws_subscription_example():
    ...     async with AsyncWeb3(WebSocketProvider(f"ws://127.0.0.1:8546")) as w3:
    ...         # Subscribe to new block headers and receive the subscription_id.
    ...         # A one-to-one call with a trigger for many responses
    ...         subscription_id = await w3.eth.subscribe("newHeads", handler=new_heads_handler)
    ...
    ...         # Handle the subscription messages asynchronously using the subscription
    ...         # manager. This will continue until no more subscriptions are present in
    ...         # the subscription manager, or indefinitely if the `run_forever` flag
    ...         # is set to `True`.
    ...         await w3.subscription_manager.handle_subscriptions(run_forever=False)
    >>> asyncio.run(ws_subscription_example())

The manager can also subscribe to many subscriptions at one time. The
``EthSubscription`` classes, available via ``web3.utils.subscriptions``, provide a
friendly API for managing subscriptions. Since each connection and provider instance
has its own message listener task and subscription manager instance, you can subscribe
to many subscriptions at once and handle the many responses that come in over the socket
connections via handlers. The handlers contain:

- ``async_w3``: The ``AsyncWeb3`` instance that the subscription was made on.
- ``subscription``: The subscription instance that the handler is attached to.
- ``result``: The response that came in over the socket connection for the subscription.

Subscriptions also accept a ``handler_context`` argument that can be used to pass
additional information to the handler when subscribing to a subscription. This can be
used to pass in an event object, for example, that can be used to parse a log event
when it comes in.


.. code-block:: python

    >>> from web3 import (
    ...     AsyncWeb3,
    ...     WebSocketProvider,
    ...     AsyncIPCProvider,
    ... )
    >>> from web3.utils.subscriptions import (
    ...     EthSubscription,
    ...     NewHeadsSubscription,
    ...     NewHeadsSubscriptionContext,
    ...     PendingTxSubscription,
    ...     PendingTxSubscriptionContext,
    ...     LogsSubscription,
    ...     LogsSubscriptionContext,
    ... )

    >>> async def new_heads_handler(
    ...     handler_context: NewHeadsSubscriptionContext,
    ... ) -> None:
    ...     header = handler_context.result
    ...     print(f"New block header: {header}\n")
    ...     if header["number"] > 1234567:
    ...         await handler_context.subscription.unsubscribe()

    >>> async def pending_txs_handler(
    ...     handler_context: PendingTxSubscriptionContext,
    ... ) -> None:
    ...     ...

    >>> async def log_handler(
    ...     handler_context: LogsSubscriptionContext,
    ... ) -> None:
    ...     log_receipt = handler_context.result
    ...     # event is now available in the handler context, because we pass it to in the
    ...     # ``handler_context`` when subscribing to the log
    ...     event_data = handler_context.transfer_event.process_log(log_receipt)
    ...     print(f"Log event data: {event_data}\n")

    >>> async def sub_manager():
    ...     local_w3 = await AsyncWeb3(AsyncIPCProvider(LOCAL_IPC))
    ...
    ...     # subscribe to many subscriptions via the subscription manager with handlers
    ...     weth_contract = local_w3.eth.contract(
    ...         address=local_w3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
    ...         abi=WETH_ABI,
    ...     )
    ...     transfer_event = weth_contract.events.Transfer()
    ...     await local_w3.subscription_manager.subscribe(
    ...         [
    ...             NewHeadsSubscription(label="new-heads-mainnet", handler=new_heads_handler),
    ...             PendingTxSubscription(
    ...                 label="pending-tx-mainnet",  # optional label
    ...                 full_transactions=True,
    ...                 handler=pending_tx_handler,
    ...             ),
    ...             LogsSubscription(
    ...                 label="WETH transfers",  # optional label
    ...                 address=weth_contract.address,
    ...                 topics=[transfer_event.topic],
    ...                 handler=log_handler,
    ...                 # optional ``handler_context`` args to help parse a response
    ...                 handler_context={"transfer_event": transfer_event},
    ...             ),
    ...         ]
    ...     )
    ...
    ...     public_w3 = await AsyncWeb3(WebSocketProvider(PUBLIC_PROVIDER_WS))
    ...     # subscribe via eth_subscribe, with handler and label (optional)
    ...     await public_w3.eth.subscribe("public_newHeads", handler=pending_tx_handler, label="new-heads-public-ws")

    >>>     # This will handle all subscriptions until no more subscriptions are present
    ...     # in either subscription manager instance. If the `run_forever` flag is set
    ...     # to `True` on any manager instance, this will run indefinitely.
    >>>     await asyncio.gather(
    ...         public_w3.subscription_manager.handle_subscriptions(),
    ...         local_w3.subscription_manager.handle_subscriptions(),
    ...     )
    ...
    ...     # close the connections
    ...     await local_w3.provider.disconnect()
    ...     await public_w3.provider.disconnect()

    >>> asyncio.run(sub_manager())


The ``process_subscriptions()`` method on the
:class:`~web3.providers.persistent.PersistentConnection` class, the public API for
interacting with the active persistent socket connection, is also set up to receive
``eth_subscription`` responses over an asynchronous iterator pattern. You can use this
method to listen for raw messages and process them as they come in.

.. code-block:: python

    >>> async def ws_subscription_example():
    ...     async with AsyncWeb3(WebSocketProvider(f"ws://127.0.0.1:8546")) as w3:
    ...         # Subscribe to new block headers and receive the subscription_id.
    ...         # A one-to-one call with a trigger for many responses
    ...         subscription_id = await w3.eth.subscribe("newHeads")
    ...
    ...         # Listen to the socket for the many responses utilizing the
    ...         # ``w3.socket`` ``PersistentConnection`` public API method
    ...         # ``process_subscriptions()``
    ...         async for response in w3.socket.process_subscriptions():
    ...             # Receive only one-to-many responses here so that we don't
    ...             # accidentally return the response for a one-to-one request in this
    ...             # block
    ...
    ...             print(f"{response}\n")
    ...
    ...             if some_condition:
    ...                 # unsubscribe from new block headers, another one-to-one request
    ...                 is_unsubscribed = await w3.eth.unsubscribe(subscription_id)
    ...                 if is_unsubscribed:
    ...                     break

    >>> asyncio.run(ws_subscription_example())

One-to-many responses, those that do not include a JSON-RPC *id* in the response object,
are stored in an internal ``asyncio.Queue`` instance, isolated from any one-to-one
responses. When the ``PersistentConnectionProvider`` is looking for one-to-many
responses internally, it will expect the message listener task to store these messages
in this queue. Since the order of the messages is important, the queue is a FIFO queue.
The ``process_subscriptions()`` method on the ``PersistentConnection`` class is set up
to pop messages from this queue as FIFO over an asynchronous iterator pattern.

If the stream of messages from the socket is not being interrupted by any other
tasks, the queue will generally be in sync with the messages coming in over the
socket. That is, the message listener will put a message in the queue and the
``process_subscriptions()`` method will pop that message from the queue and yield
control of the loop back to the listener. This will continue until the socket
connection is closed or the user unsubscribes from the subscription. If the stream of
messages lags a bit, or the provider is not consuming messages but has subscribed to
a subscription, this internal queue may fill up with messages until it reaches its max
size and then trigger a waiting ``asyncio.Event`` until the provider begins consuming
messages from the queue again. For this reason, it's important to begin consuming
messages from the queue, via the ``process_subscriptions()`` method, as soon as a
subscription is made.
