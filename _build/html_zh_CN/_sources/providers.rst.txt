.. _providers:

Providers
=========

Using Ethereum requires access to an Ethereum node. If you have the means, you're
encouraged to `run your own node`_. (Note that you do not need to stake ether to
run a node.) If you're unable to run your own node, you can use a `remote node`_.

Once you have access to a node, you can connect to it using a **provider**.
Providers generate `JSON-RPC`_ requests and return the response. This is done by submitting
the request to an HTTP, WebSocket, or IPC socket-based server.

.. note::

   web3.py supports one provider per instance. If you have an advanced use case
   that requires multiple providers, create and configure a new web3 instance
   per connection.

If you are already happily connected to your Ethereum node, then you
can skip the rest of this providers section.

.. _run your own node: https://ethereum.org/en/developers/docs/nodes-and-clients/run-a-node/
.. _remote node: https://ethereum.org/en/developers/docs/nodes-and-clients/nodes-as-a-service/
.. _JSON-RPC: https://ethereum.org/en/developers/docs/apis/json-rpc/

.. _choosing_provider:

Choosing a Provider
-------------------

Most nodes have a variety of ways to connect to them. Most commonly:

1. IPC (uses local filesystem: fastest and most secure)
2. WebSocket (works remotely, faster than HTTP)
3. HTTP (more nodes support it)

If you're not sure how to decide, choose this way:

- If you have the option of running web3.py on the same machine as the node, choose IPC.
- If you must connect to a node on a different computer, use WebSocket.
- If your node does not support WebSocket, use HTTP.

Once you have decided how to connect, you'll select and configure the appropriate provider
class:

- :class:`~web3.providers.rpc.HTTPProvider`
- :class:`~web3.providers.ipc.IPCProvider`
- :class:`~web3.providers.async_rpc.AsyncHTTPProvider`
- :class:`~web3.providers.persistent.AsyncIPCProvider` (Persistent Connection Provider)
- :class:`~web3.providers.persistent.WebSocketProvider` (Persistent Connection Provider)

Each provider above links to the documentation on how to properly initialize that
provider. Once you have reviewed the relevant documentation for the provider of your
choice, you are ready to :ref:`get started with web3.py<first_w3_use>`.

Provider via Environment Variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you can set the environment variable ``WEB3_PROVIDER_URI``
before starting your script, and web3 will look for that provider first.

Valid formats for this environment variable are:

- ``file:///path/to/node/rpc-json/file.ipc``
- ``http://192.168.1.2:8545``
- ``https://node.ontheweb.com``
- ``ws://127.0.0.1:8546``


Auto-initialization Provider Shortcuts
--------------------------------------

Geth dev Proof of Authority
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To connect to a ``geth --dev`` Proof of Authority instance with
the POA middleware loaded by default:

.. code-block:: python

    >>> from web3.auto.gethdev import w3

    # confirm that the connection succeeded
    >>> w3.is_connected()
    True

Or, connect to an async web3 instance:

.. code-block:: python

    >>> from web3.auto.gethdev import async_w3
    >>> await async_w3.provider.connect()

    # confirm that the connection succeeded
    >>> await async_w3.is_connected()
    True


Built In Providers
------------------

Web3 ships with the following providers which are appropriate for connecting to
local and remote JSON-RPC servers.


HTTPProvider
~~~~~~~~~~~~

.. py:class:: web3.providers.rpc.HTTPProvider(endpoint_uri, request_kwargs={}, session=None, exception_retry_configuration=ExceptionRetryConfiguration())

    This provider handles interactions with an HTTP or HTTPS based JSON-RPC server.

    * ``endpoint_uri`` should be the full URI to the RPC endpoint such as
      ``'https://localhost:8545'``.  For RPC servers behind HTTP connections
      running on port 80 and HTTPS connections running on port 443 the port can
      be omitted from the URI.
    * ``request_kwargs`` should be a dictionary of keyword arguments which
      will be passed onto each http/https POST request made to your node.
    * ``session`` allows you to pass a ``requests.Session`` object initialized
      as desired.
    * ``exception_retry_configuration`` is an instance of the
      :class:`~web3.providers.rpc.utils.ExceptionRetryConfiguration`
      class which allows you to configure how the provider should handle exceptions
      when making certain requests. Setting this to ``None`` will disable
      exception retries.

    .. code-block:: python

        >>> from web3 import Web3
        >>> w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

    Note that you should create only one HTTPProvider with the same provider URL
    per python process, as the HTTPProvider recycles underlying TCP/IP
    network connections, for better performance. Multiple HTTPProviders with different
    URLs will work as expected.

    Under the hood, the ``HTTPProvider`` uses the python requests library for
    making requests.  If you would like to modify how requests are made, you can
    use the ``request_kwargs`` to do so.  A common use case for this is increasing
    the timeout for each request.


    .. code-block:: python

        >>> from web3 import Web3
        >>> w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545", request_kwargs={'timeout': 60}))


    To tune the connection pool size, you can pass your own ``requests.Session``.

    .. code-block:: python

        >>> from web3 import Web3
        >>> adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)
        >>> session = requests.Session()
        >>> session.mount('http://', adapter)
        >>> session.mount('https://', adapter)
        >>> w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545", session=session))


IPCProvider
~~~~~~~~~~~

.. py:class:: web3.providers.ipc.IPCProvider(ipc_path=None, timeout=10)

    This provider handles interaction with an IPC Socket based JSON-RPC
    server.

    *  ``ipc_path`` is the filesystem path to the IPC socket:

    .. code-block:: python

        >>> from web3 import Web3
        >>> w3 = Web3(Web3.IPCProvider("~/Library/Ethereum/geth.ipc"))

    If no ``ipc_path`` is specified, it will use a default depending on your operating
    system.

    - On Linux and FreeBSD: ``~/.ethereum/geth.ipc``
    - On Mac OS: ``~/Library/Ethereum/geth.ipc``
    - On Windows: ``\\.\pipe\geth.ipc``


AsyncHTTPProvider
~~~~~~~~~~~~~~~~~

.. py:class:: web3.providers.rpc.AsyncHTTPProvider(endpoint_uri, request_kwargs={}, exception_retry_configuration=ExceptionRetryConfiguration())

    This provider handles interactions with an HTTP or HTTPS based JSON-RPC server asynchronously.

    * ``endpoint_uri`` should be the full URI to the RPC endpoint such as
      ``'https://localhost:8545'``.  For RPC servers behind HTTP connections
      running on port 80 and HTTPS connections running on port 443 the port can
      be omitted from the URI.
    * ``request_kwargs`` should be a dictionary of keyword arguments which
      will be passed onto each http/https POST request made to your node.
    * ``exception_retry_configuration`` is an instance of the
      :class:`~web3.providers.rpc.utils.ExceptionRetryConfiguration`
      class which allows you to configure how the provider should handle exceptions
      when making certain requests. Setting this to ``None`` will disable
      exception retries.

    The ``cache_async_session()`` method allows you to use your own
    ``aiohttp.ClientSession`` object.

    .. code-block:: python

        >>> from aiohttp import ClientSession
        >>> from web3 import AsyncWeb3, AsyncHTTPProvider

        >>> w3 = AsyncWeb3(AsyncHTTPProvider(endpoint_uri))

        >>> # If you want to pass in your own session:
        >>> custom_session = ClientSession()
        >>> await w3.provider.cache_async_session(custom_session) # This method is an async method so it needs to be handled accordingly
        >>> # when you're finished, disconnect:
        >>> w3.provider.disconnect()

    Under the hood, the ``AsyncHTTPProvider`` uses the python
    `aiohttp <https://docs.aiohttp.org/en/stable/>`_ library for making requests.

Persistent Connection Providers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Persistent Connection Base Class
++++++++++++++++++++++++++++++++

.. note::
    This class is not meant to be used directly. If your provider class inherits
    from this class, look to these docs for additional configuration options.

.. py:class:: web3.providers.persistent.PersistentConnectionProvider(\
        request_timeout: float = 50.0, \
        subscription_response_queue_size: int = 500, \
        silence_listener_task_exceptions: bool = False \
        max_connection_retries: int = 5, \
        request_information_cache_size: int = 500, \
    )

    This is a base provider class, inherited by the following providers:

        - :class:`~web3.providers.persistent.WebSocketProvider`
        - :class:`~web3.providers.persistent.AsyncIPCProvider`

    It handles interactions with a persistent connection to a JSON-RPC server. Among
    its configuration, it houses all of the
    :class:`~web3.providers.persistent.request_processor.RequestProcessor` logic for
    handling the asynchronous sending and receiving of requests and responses. See
    the :ref:`internals__persistent_connection_providers` section for more details on
    the internals of persistent connection providers.

    * ``request_timeout`` is the timeout in seconds, used when sending data over the
      connection and waiting for a response to be received from the listener task.
      Defaults to ``50.0``.

    * ``subscription_response_queue_size`` is the size of the queue used to store
      subscription responses, defaults to ``500``. While messages are being consumed,
      this queue should never fill up as it is a transient queue and meant to handle
      asynchronous receiving and processing of responses. When in sync with the
      socket stream, this queue should only ever store 1 to a few messages at a time.

    * ``silence_listener_task_exceptions`` is a boolean that determines whether
      exceptions raised by the listener task are silenced. Defaults to ``False``,
      raising any exceptions that occur in the listener task.

    * ``max_connection_retries`` is the maximum number of times to retry a connection
      to the provider when initializing the provider. Defaults to ``5``.

    * ``request_information_cache_size`` specifies the size of the transient cache for
      storing request details, enabling the provider to process responses based on the
      original request information. Defaults to ``500``.

AsyncIPCProvider
++++++++++++++++

.. py:class:: web3.providers.persistent.AsyncIPCProvider(ipc_path=None, max_connection_retries=5)

    This provider handles asynchronous, persistent interaction with an IPC Socket based
    JSON-RPC server.

    *  ``ipc_path`` is the filesystem path to the IPC socket:
    *  ``read_buffer_limit`` is the maximum size of data, in bytes, that can be read
       from the socket at one time. Defaults to 20MB (20 * 1024 * 1024). Raises
       ``ReadBufferLimitReached`` if the limit is reached, suggesting that the buffer
       limit be increased.

    This provider inherits from the
    :class:`~web3.providers.persistent.PersistentConnectionProvider` class. Refer to
    the :class:`~web3.providers.persistent.PersistentConnectionProvider` documentation
    for details on additional configuration options available for this provider.

    If no ``ipc_path`` is specified, it will use a default depending on your operating
    system.

    - On Linux and FreeBSD: ``~/.ethereum/geth.ipc``
    - On Mac OS: ``~/Library/Ethereum/geth.ipc``
    - On Windows: ``\\.\pipe\geth.ipc``

WebSocketProvider
+++++++++++++++++

.. py:class:: web3.providers.persistent.WebSocketProvider(endpoint_uri: str, websocket_kwargs: Dict[str, Any] = {}, use_text_frames: bool = False)

    This provider handles interactions with an WS or WSS based JSON-RPC server.

    * ``endpoint_uri`` should be the full URI to the RPC endpoint such as
      ``'ws://localhost:8546'``.
    * ``websocket_kwargs`` this should be a dictionary of keyword arguments which
      will be passed onto the ws/wss websocket connection.
    * ``use_text_frames`` will ensure websocket data is sent as text frames
      for servers that do not support binary communication.

    This provider inherits from the
    :class:`~web3.providers.persistent.PersistentConnectionProvider` class. Refer to
    the :class:`~web3.providers.persistent.PersistentConnectionProvider` documentation
    for details on additional configuration options available for this provider.

    Under the hood, the ``WebSocketProvider`` uses the python websockets library for
    making requests.  If you would like to modify how requests are made, you can
    use the ``websocket_kwargs`` to do so.  See the `websockets documentation`_ for
    available arguments.


.. _subscription-examples:

Using Persistent Connection Providers
+++++++++++++++++++++++++++++++++++++

The ``AsyncWeb3`` class may be used as a context manager, utilizing the ``async with``
syntax, when instantiating with a
:class:`~web3.providers.persistent.PersistentConnectionProvider`. This will
automatically close the connection when the context manager exits and is the
recommended way to initiate a persistent connection to the provider.

A similar example using a ``websockets`` connection as an asynchronous context manager
can be found in the `websockets connection`_ docs.

.. code-block:: python

        >>> import asyncio
        >>> from web3 import AsyncWeb3
        >>> from web3.providers.persistent import (
        ...     AsyncIPCProvider,
        ...     WebSocketProvider,
        ... )

        >>> LOG = True  # toggle debug logging
        >>> if LOG:
        ...     import logging
        ...     # logger = logging.getLogger("web3.providers.AsyncIPCProvider")  # for the AsyncIPCProvider
        ...     logger = logging.getLogger("web3.providers.WebSocketProvider")  # for the WebSocketProvider
        ...     logger.setLevel(logging.DEBUG)
        ...     logger.addHandler(logging.StreamHandler())

        >>> async def context_manager_subscription_example():
        ...     #  async with AsyncWeb3(AsyncIPCProvider("./path/to.filename.ipc") as w3:  # for the AsyncIPCProvider
        ...     async with AsyncWeb3(WebSocketProvider(f"ws://127.0.0.1:8546")) as w3:  # for the WebSocketProvider
        ...         # subscribe to new block headers
        ...         subscription_id = await w3.eth.subscribe("newHeads")
        ...
        ...         async for response in w3.socket.process_subscriptions():
        ...             print(f"{response}\n")
        ...             # handle responses here
        ...
        ...             if some_condition:
        ...                 # unsubscribe from new block headers and break out of
        ...                 # iterator
        ...                 await w3.eth.unsubscribe(subscription_id)
        ...                 break
        ...
        ...         # still an open connection, make any other requests and get
        ...         # responses via send / receive
        ...         latest_block = await w3.eth.get_block("latest")
        ...         print(f"Latest block: {latest_block}")
        ...
        ...         # the connection closes automatically when exiting the context
        ...         # manager (the `async with` block)

        >>> asyncio.run(context_manager_subscription_example())


The ``AsyncWeb3`` class may also be used as an asynchronous iterator, utilizing the
``async for`` syntax, when instantiating with a
:class:`~web3.providers.persistent.PersistentConnectionProvider`. This may be used to
set up an indefinite websocket connection and reconnect automatically if the connection
is lost.

A similar example using a ``websockets`` connection as an asynchronous iterator can
be found in the `websockets connection`_ docs.

.. _`websockets connection`: https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html#websockets.client.connect

.. code-block:: python

    >>> import asyncio
    >>> import websockets
    >>> from web3 import AsyncWeb3
    >>> from web3.providers.persistent import (
    ...     AsyncIPCProvider,
    ...     WebSocketProvider,
    ... )

    >>> async def subscription_iterator_example():
    ...     # async for w3 in AsyncWeb3(AsyncIPCProvider("./path/to/filename.ipc")):  # for the AsyncIPCProvider
    ...     async for w3 in AsyncWeb3(WebSocketProvider(f"ws://127.0.0.1:8546")):  # for the WebSocketProvider
    ...         try:
    ...             ...
    ...         except websockets.ConnectionClosed:
    ...             continue

    # run the example
    >>> asyncio.run(subscription_iterator_example())


Awaiting the instantiation with a
:class:`~web3.providers.persistent.PersistentConnectionProvider`, or instantiating
and awaiting the ``connect()`` method is also possible. Both of these examples are
shown below.

.. code-block:: python

    >>> async def await_instantiation_example():
    ...     # w3 = await AsyncWeb3(AsyncIPCProvider("./path/to/filename.ipc"))  # for the AsyncIPCProvider
    ...     w3 = await AsyncWeb3(WebSocketProvider(f"ws://127.0.0.1:8546"))  # for the WebSocketProvider
    ...
    ...     # some code here
    ...
    ...     # manual cleanup
    ...     await w3.provider.disconnect()

    # run the example
    >>> asyncio.run(await_instantiation_example())

.. code-block:: python

    >>> async def await_provider_connect_example():
    ...     # w3 = AsyncWeb3(AsyncIPCProvider("./path/to/filename.ipc"))  # for the AsyncIPCProvider
    ...     w3 = AsyncWeb3(WebSocketProvider(f"ws://127.0.0.1:8546"))  # for the WebSocketProvider
    ...     await w3.provider.connect()
    ...
    ...     # some code here
    ...
    ...     # manual cleanup
    ...     await w3.provider.disconnect()

    # run the example
    >>> asyncio.run(await_provider_connect_example())

:class:`~web3.providers.persistent.PersistentConnectionProvider` classes use the
:class:`~web3.providers.persistent.request_processor.RequestProcessor` class under the
hood to sync up the receiving of responses and response processing for one-to-one and
one-to-many request-to-response requests. Refer to the
:class:`~web3.providers.persistent.request_processor.RequestProcessor`
documentation for details.

AsyncWeb3 with Persistent Connection Providers
++++++++++++++++++++++++++++++++++++++++++++++

When an ``AsyncWeb3`` class is connected to a
:class:`~web3.providers.persistent.PersistentConnectionProvider`, some attributes and
methods become available.

    .. py:attribute:: socket

        The public API for interacting with the websocket connection is available via
        the ``socket`` attribute of the ``Asyncweb3`` class. This attribute is an
        instance of the
        :class:`~web3.providers.persistent.persistent_connection.PersistentConnection`
        class and is the main interface for interacting with the socket connection.


Interacting with the Persistent Connection
++++++++++++++++++++++++++++++++++++++++++

.. py:class:: web3.providers.persistent.persistent_connection.PersistentConnection

    This class handles interactions with a persistent socket connection. It is available
    via the ``socket`` attribute on the ``AsyncWeb3`` class. The
    ``PersistentConnection`` class has the following methods and attributes:

    .. py:attribute:: subscriptions

        This attribute returns the current active subscriptions as a dict mapping
        the subscription ``id`` to a dict of metadata about the subscription
        request.

    .. py:method:: process_subscriptions()

        This method is available for listening to websocket subscriptions indefinitely.
        It is an asynchronous iterator that yields strictly one-to-many
        (e.g. ``eth_subscription`` responses) request-to-response messages from the
        websocket connection. To receive responses for one-to-one request-to-response
        calls, use the standard API for making requests via the appropriate module
        (e.g. ``block_num = await w3.eth.block_number``)

        The responses from this method are formatted by *web3.py* formatters and run
        through the middleware that were present at the time of subscription.
        Examples on how to use this method can be seen above in the
        `Using Persistent Connection Providers`_ section.

    .. py:method:: send(method: RPCEndpoint, params: Sequence[Any])

        This method is available strictly for sending raw requests to the socket,
        if desired. It is not recommended to use this method directly, as the
        responses will not be formatted by *web3.py* formatters or run through the
        middleware. Instead, use the methods available on the respective web3
        module. For example, use ``w3.eth.get_block("latest")`` instead of
        ``w3.socket.send("eth_getBlockByNumber", ["latest", True])``.

    .. py:method:: recv()

        The ``recv()`` method can be used to receive the next response for a request
        from the socket. The response from this method is the raw response. This is not
        the recommended way to receive a response for a request, as it is not formatted
        by *web3.py* formatters or run through the middleware. Instead, use the methods
        available on the respective web3 module
        (e.g. ``block_num = await w3.eth.block_number``) for retrieving responses for
        one-to-one request-to-response calls.

    .. py:method:: make_request(method: RPCEndpoint, params: Sequence[Any])

        This method is available for making requests to the socket and retrieving the
        response. It is not recommended to use this method directly, as the responses
        will not be properly formatted by *web3.py* formatters or run through the
        middleware. Instead, use the methods available on the respective web3 module.
        For example, use ``w3.eth.get_block("latest")`` instead of
        ``w3.socket.make_request("eth_getBlockByNumber", ["latest", True])``.


LegacyWebSocketProvider
~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

        ``LegacyWebSocketProvider`` is deprecated and is likely to be removed in a
        future major release. Please use ``WebSocketProvider`` instead.

.. py:class:: web3.providers.legacy_websocket.LegacyWebSocketProvider(endpoint_uri[, websocket_timeout, websocket_kwargs])

    This provider handles interactions with an WS or WSS based JSON-RPC server.

    * ``endpoint_uri`` should be the full URI to the RPC endpoint such as
      ``'ws://localhost:8546'``.
    * ``websocket_timeout`` is the timeout in seconds, used when receiving or
      sending data over the connection. Defaults to 10.
    * ``websocket_kwargs`` this should be a dictionary of keyword arguments which
      will be passed onto the ws/wss websocket connection.

    .. code-block:: python

        >>> from web3 import Web3
        >>> w3 = Web3(Web3.LegacyWebSocketProvider("ws://127.0.0.1:8546"))

    Under the hood, ``LegacyWebSocketProvider`` uses the python ``websockets`` library for
    making requests.  If you would like to modify how requests are made, you can
    use the ``websocket_kwargs`` to do so.  See the `websockets documentation`_ for
    available arguments.

    .. _`websockets documentation`: https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html#websockets.client.WebSocketClientProtocol

    Unlike HTTP connections, the timeout for WS connections is controlled by a
    separate ``websocket_timeout`` argument, as shown below.


    .. code-block:: python

        >>> from web3 import Web3
        >>> w3 = Web3(Web3.LegacyWebSocketProvider("ws://127.0.0.1:8546", websocket_timeout=60))


AutoProvider
~~~~~~~~~~~~

:class:`~web3.providers.auto.AutoProvider` is the default used when initializing
:class:`web3.Web3` without any providers. There's rarely a reason to use it
explicitly.

.. py:currentmodule:: web3.providers.eth_tester

EthereumTesterProvider
~~~~~~~~~~~~~~~~~~~~~~

.. warning:: Experimental:  This provider is experimental. There are still significant
    gaps in functionality. However it is being actively developed and supported.

.. py:class:: EthereumTesterProvider(ethereum_tester=None, api_endpoints=None)
.. py:class:: AsyncEthereumTesterProvider(ethereum_tester=None, api_endpoints=None)

    This provider integrates with the ``eth-tester`` library. The ``ethereum_tester``
    constructor argument should be an instance of the :class:`~eth_tester.EthereumTester`
    or a subclass of :class:`~eth_tester.backends.base.BaseChainBackend` class provided
    by the ``eth-tester`` library. The ``api_endpoints`` argument should be a ``dict``
    of RPC endpoints. You can see the structure and defaults `here <https://github.com/ethereum/web3.py/blob/283b536c7d53e605c61468941e3fc07a6c5d0c09/web3/providers/eth_tester/defaults.py#L228>`_.
    If you would like a custom ``eth-tester`` instance to test with, see the
    ``eth-tester`` library `documentation <https://github.com/ethereum/eth-tester>`_
    for details.

    .. code-block:: python

        >>> from web3 import Web3, EthereumTesterProvider
        >>> w3 = Web3(EthereumTesterProvider())

.. NOTE:: To install the needed dependencies to use EthereumTesterProvider, you can
    install the pip extras package that has the correct interoperable versions of the
    ``eth-tester`` and ``py-evm`` dependencies needed: e.g. ``pip install "web3[tester]"``
