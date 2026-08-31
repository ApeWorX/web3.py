.. _middleware_internals:

Middleware
==========

``Web3`` is instantiated with layers of middleware by default. They sit between the public
``Web3`` methods and the :doc:`providers`, and are used to perform sanity checks, convert data
types, enable ENS support, and more. Each layer can modify the request and/or response.
While several middleware are enabled by default, others are available for optional use,
and you're free to create your own!

Each middleware layer gets invoked before the request reaches the provider, and then
processes the result after the provider returns, in reverse order. However, it is
possible for a middleware to return early from a call without the request ever getting
to the provider (or even reaching the middleware that are in deeper layers).


.. _Modifying_Middleware:

Configuring Middleware
-----------------------

Middleware can be added, removed, replaced, and cleared at runtime. To make that easier, you
can name the middleware for later reference.

Middleware Order
~~~~~~~~~~~~~~~~

Think of the middleware as being layered in an onion, where you initiate a web3.py request at
the outermost layer of the onion, and the Ethereum node (like geth) receives and responds
to the request inside the innermost layer of the onion. Here is a (simplified) diagram:

.. code-block:: none

                                         New request from web3.py

                                                     |
                                                     |
                                                     v

                                             `````Layer 2``````
                                      ```````                  ```````
                                 `````               |                ````
                              ````                   v                    ````
                           ```                                                ```
                         `.               ````````Layer 1```````                `.`
                       ``             ````                      `````              .`
                     `.            ```               |               ```            `.`
                    .`          ```                  v                  ```           `.
                  `.          `.`                                         ```           .`
                 ``          .`                  `Layer 0`                  ``           .`
                ``         `.               `````        ``````               .           .`
               `.         ``             ```         |        ```              .`          .
               .         ``            `.`           |           ``             .           .
              .         `.            ``       JSON-RPC call       .`            .          .`
              .         .            ``              |              .            ``          .
             ``         .            .               v               .            .          .
             .         .`           .                                .            .          ``
             .         .            .          Ethereum node         .`           .           .
             .         .            .                                .            .           .
             .         ``           `.               |               .            .           .
             .          .            .`              |              .`            .          .
             `.         .`            .`          Response         .`            .`          .
              .          .             `.`           |           `.`            `.           .
              `.          .              ```         |        ````             `.           .
               .          `.               `````     v     ````               `.           ``
                .           .`                 ```Layer 0``                  ``           `.
                 .           `.                                            `.`           `.
                  .            `.                    |                   `.`            `.
                   .`            ```                 |                 ```             .`
                    `.              ```              v             ````              `.`
                      ``               ``````                 `````                 .`
                        ``                   `````Layer 1`````                   `.`
                          ```                                                  ```
                            ````                     |                      ```
                               `````                 v                  ````
                                   ``````                          `````
                                         `````````Layer 2``````````

                                                     |
                                                     v

                                          Returned value in web3.py


The middleware are maintained in ``Web3.middleware_onion``. See below for the API.

When specifying middleware in a list, or retrieving the list of middleware, they will
be returned in the order of outermost layer first and innermost layer last. In the above
example, that means that ``w3.middleware_onion.middleware`` would return the middleware
in the order of: ``[2, 1, 0]``.


.. _middleware_stack_api:

Middleware Stack API
~~~~~~~~~~~~~~~~~~~~

To add or remove items in different layers, use the following API:

.. py:method:: Web3.middleware_onion.add(middleware, name=None)

    Middleware will be added to the outermost layer. That means the new middleware will modify the
    request first, and the response last. You can optionally name it with any hashable object,
    typically a string.

    .. code-block:: python

        >>> w3 = Web3(...)
        >>> w3.middleware_onion.add(web3.middleware.GasPriceStrategyMiddleware)
        # or
        >>> w3.middleware_onion.add(web3.middleware.GasPriceStrategyMiddleware, 'gas_price_strategy')

.. py:method:: Web3.middleware_onion.inject(middleware, name=None, layer=None)

    Inject a named middleware to an arbitrary layer.

    The current implementation only supports injection at the innermost or
    outermost layers. Note that injecting to the outermost layer is equivalent to calling
    :meth:`Web3.middleware_onion.add` .

    .. code-block:: python

        # Either of these will put the gas_price_strategy middleware at the innermost layer
        >>> w3 = Web3(...)
        >>> w3.middleware_onion.inject(web3.middleware.GasPriceStrategyMiddleware, layer=0)
        # or
        >>> w3.middleware_onion.inject(web3.middleware.GasPriceStrategyMiddleware, 'gas_price_strategy', layer=0)

.. py:method:: Web3.middleware_onion.remove(middleware)

    Middleware will be removed from whatever layer it was in. If you added the middleware with
    a name, use the name to remove it. If you added the middleware as an object, use the object
    again later to remove it:

    .. code-block:: python

        >>> w3 = Web3(...)
        >>> w3.middleware_onion.remove(web3.middleware.GasPriceStrategyMiddleware)
        # or
        >>> w3.middleware_onion.remove('gas_price_strategy')

.. py:method:: Web3.middleware_onion.replace(old_middleware, new_middleware)

    Middleware will be replaced from whatever layer it was in. If the middleware was named, it will
    continue to have the same name. If it was un-named, then you will now reference it with the new
    middleware object.

    .. code-block:: python

        >>> from web3.middleware import GasPriceStrategyMiddleware, AttributeDictMiddleware
        >>> w3 = Web3(provider, middleware=[GasPriceStrategyMiddleware, AttributeDictMiddleware])

        >>> w3.middleware_onion.replace(GasPriceStrategyMiddleware, AttributeDictMiddleware)
        # this is now referenced by the new middleware object, so to remove it:
        >>> w3.middleware_onion.remove(AttributeDictMiddleware)

        # or, if it was named

        >>> w3.middleware_onion.replace('gas_price_strategy', AttributeDictMiddleware)
        # this is still referenced by the original name, so to remove it:
        >>> w3.middleware_onion.remove('gas_price_strategy')

.. py:method:: Web3.middleware_onion.clear()

    Empty all the middleware, including the default ones.

    .. code-block:: python

        >>> w3 = Web3(...)
        >>> w3.middleware_onion.clear()
        >>> assert len(w3.middleware_onion) == 0

.. py:attribute:: Web3.middleware_onion.middleware

    Return all the current middleware for the ``Web3`` instance in the appropriate order for importing into a new
    ``Web3`` instance.

    .. code-block:: python

        >>> w3_1 = Web3(...)
        # add uniquely named middleware:
        >>> w3_1.middleware_onion.add(web3.middleware.GasPriceStrategyMiddleware, 'test_middleware')
        # export middleware from first w3 instance
        >>> middleware = w3_1.middleware_onion.middleware

        # import into second instance
        >>> w3_2 = Web3(..., middleware=middleware)
        >>> assert w3_1.middleware_onion.middleware == w3_2.middleware_onion.middleware
        >>> assert w3_2.middleware_onion.get('test_middleware')


Instantiate with Custom Middleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of working from the default list, you can specify a custom list of
middleware when initializing Web3:

.. code-block:: python

    Web3(middleware=[my_middleware1, my_middleware2])

.. warning::
  This will *replace* the default middleware. To keep the default functionality,
  either use ``middleware_onion.add()`` from above, or add the default middleware to
  your list of new middleware.


.. _default_middleware:

Default Middleware
------------------

The following middleware are included by default:

* ``gas_price_strategy``
* ``ens_name_to_address``
* ``attrdict``
* ``validation``
* ``gas_estimate``

The defaults are defined in the ``get_default_middleware()`` method in ``web3/manager.py``.

AttributeDict
~~~~~~~~~~~~~

.. py:class:: web3.middleware.AttributeDictMiddleware

    This middleware recursively converts any dictionary type in the result of a call
    to an ``AttributeDict``. This enables dot-syntax access, like
    ``eth.get_block('latest').number`` in addition to
    ``eth.get_block('latest')['number']``.

    .. note::
        Accessing a property via attribute breaks type hinting. For this reason, this
        feature is available as a middleware, which may be removed if desired.

ENS Name to Address Resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: web3.middleware.ENSNameToAddressMiddleware

    This middleware converts Ethereum Name Service (ENS) names into the
    address that the name points to. For example :meth:`w3.eth.send_transaction <web3.eth.Eth.send_transaction>` will
    accept .eth names in the 'from' and 'to' fields.

    .. note::
        This middleware only converts ENS names on chains where the proper ENS
        contracts are deployed to support this functionality. All other cases will
        result in a ``NameNotFound`` error.

Gas Price Strategy
~~~~~~~~~~~~~~~~~~

.. py:class:: web3.middleware.GasPriceStrategyMiddleware

  .. warning::

      Gas price strategy is only supported for legacy transactions. The London fork
      introduced ``maxFeePerGas`` and ``maxPriorityFeePerGas`` transaction parameters
      which should be used over ``gasPrice`` whenever possible.

  This adds a ``gasPrice`` to transactions if applicable and when a gas price strategy has
  been set. See :ref:`Gas_Price` for information about how gas price is derived.

Buffered Gas Estimate
~~~~~~~~~~~~~~~~~~~~~

.. py:class:: web3.middleware.BufferedGasEstimateMiddleware

    This adds a gas estimate to transactions if ``gas`` is not present in the transaction
    parameters. Sets gas to:
    ``min(w3.eth.estimate_gas + gas_buffer, gas_limit)``
    where the gas_buffer default is 100,000

Validation
~~~~~~~~~~

.. py:class:: web3.middleware.ValidationMiddleware

    This middleware includes block and transaction validators which perform validations
    for transaction parameters.


Optional Middleware
-------------------

``Web3`` includes optional middleware for common use cases. Below is a list of available
middleware which are not enabled by default.

Stalecheck
~~~~~~~~~~~~

.. py:method:: web3.middleware.StalecheckMiddlewareBuilder

    This middleware checks how stale the blockchain is, and interrupts calls with a failure
    if the blockchain is too old.

    * ``allowable_delay`` is the length in seconds that the blockchain is allowed to be
      behind of ``time.time()``

    Because this middleware takes an argument, you must create the middleware
    with a method call.

    .. code-block:: python

        two_day_stalecheck = StalecheckMiddlewareBuilder.build(60 * 60 * 24 * 2)
        web3.middleware_onion.add(two_day_stalecheck)

    If the latest block in the blockchain is older than 2 days in this example, then the
    middleware will raise a ``StaleBlockchain`` exception on every call except
    ``web3.eth.get_block()``.


.. _geth-poa:

Proof of Authority
~~~~~~~~~~~~~~~~~~

.. py:class:: web3.middleware.ExtraDataToPOAMiddleware

.. important::
    It is **crucial** that this middleware is injected at the 0th layer of the
    middleware onion, using
    ``w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)``, to guarantee
    it is the *first* middleware to process the response and modify the ``extraData``
    field. This ensures it processes the field before any other middleware attempts
    to validate it.

``ExtraDataToPOAMiddleware`` is required to connect to ``geth --dev`` and may
also be needed for other EVM compatible blockchains like Polygon or BNB Chain
(Binance Smart Chain).

If the middleware is not injected at the 0th layer of the middleware onion, you may get
errors like the example below when interacting with your EVM node.

.. code-block:: shell

    web3.exceptions.ExtraDataLengthError: The field extraData is 97 bytes, but should be
    32.  It is quite likely that you are connected to a POA chain. Refer to
    http://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority
    for more details. The full extraData is: HexBytes('...')

The easiest way to connect to a default ``geth --dev`` instance which loads the
middleware is:

.. code-block:: python

    >>> from web3.auto.gethdev import w3

    # confirm that the connection succeeded
    >>> w3.client_version
    'Geth/v1.14.12-stable-4bb3c89d/linux-amd64/go1.22.4'

This example connects to a local ``geth --dev`` instance on Linux with a
unique IPC location and loads the middleware:

.. code-block:: python

    >>> from web3 import Web3, IPCProvider

    # connect to the IPC location started with 'geth --dev --datadir ~/mynode'
    >>> w3 = Web3(IPCProvider('~/mynode/geth.ipc'))

    >>> from web3.middleware import ExtraDataToPOAMiddleware

    # inject the poa compatibility middleware to the innermost layer (0th layer)
    >>> w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    # confirm that the connection succeeded
    >>> w3.client_version
    'Geth/v1.14.12-stable-4bb3c89d/linux-amd64/go1.22.4'

Why is ``ExtraDataToPOAMiddleware`` necessary?
''''''''''''''''''''''''''''''''''''''''''''''

There is no strong community consensus on a single Proof-of-Authority (PoA) standard yet.
Some nodes have successful experiments running though. One is go-ethereum (geth),
which uses a prototype PoA for its development mode and the Goerli test network.

Unfortunately, it does deviate from the yellow paper specification, which constrains the
``extraData`` field in each block to a maximum of 32-bytes. Geth is one such example
where PoA uses more than 32 bytes, so this middleware modifies the block data a bit
before returning it.

.. _local-filter:

Locally Managed Log and Block Filters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: web3.middleware.LocalFilterMiddleware

This middleware provides an alternative to ethereum node managed filters. When used, Log and
Block filter logic are handled locally while using the same web3 filter api. Filter results are
retrieved using JSON-RPC endpoints that don't rely on server state.

.. doctest::

    >>> from web3 import Web3, EthereumTesterProvider
    >>> w3 = Web3(EthereumTesterProvider())
    >>> from web3.middleware import LocalFilterMiddleware
    >>> w3.middleware_onion.add(LocalFilterMiddleware)

.. code-block:: python

    #  Normal block and log filter apis behave as before.
    >>> block_filter = w3.eth.filter("latest")

    >>> log_filter = myContract.events.myEvent.build_filter().deploy()

Signing
~~~~~~~

.. py:method:: web3.middleware.SignAndSendRawMiddlewareBuilder

This middleware automatically captures transactions, signs them, and sends them as raw transactions.
The ``from`` field on the transaction, or ``w3.eth.default_account`` must be set to the address of the private key for
this middleware to have any effect.

The ``build`` method for this middleware builder takes a single argument:

   * ``private_key_or_account`` A single private key or a tuple, list or set of private keys.

      Keys can be in any of the following formats:

      * An ``eth_account.LocalAccount`` object
      * An ``eth_keys.PrivateKey`` object
      * A raw private key as a hex string or byte string

.. important::
    Since this middleware signs transactions, it must always run after any middleware
    that modifies the transaction. Therefore, it is recommended to inject the signing
    middleware at the 0th layer of the middleware onion using
    ``w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(...), layer=0)``.
    Ensure that any transaction-modifying middleware exists in a higher layer within the
    onion so that it runs before the signing middleware.

.. note::
    If used with ``ExtraDataToPOAMiddleware``, the injection order doesn't matter, as
    the ``extraData`` field isn't involved in transaction signing. The key is ensuring
    ``SignAndSendRawMiddlewareBuilder`` runs after any middleware that modifies the
    transaction.


.. code-block:: python

   >>> from web3 import Web3, EthereumTesterProvider
   >>> w3 = Web3(EthereumTesterProvider)
   >>> from web3.middleware import SignAndSendRawMiddlewareBuilder
   >>> from eth_account import Account
   >>> acct = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ 1530')
   >>> w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(acct), layer=0)
   >>> w3.eth.default_account = acct.address

:ref:`Hosted nodes<local_vs_hosted>` (like Infura or Alchemy) only support signed
transactions. This often results in ``send_raw_transaction`` being used repeatedly.
Instead, we can automate this process with
``SignAndSendRawMiddlewareBuilder.build(private_key_or_account)``.

.. code-block:: python

    >>> from web3 import Web3
    >>> w3 = Web3(Web3.HTTPProvider('HTTP_ENDPOINT'))
    >>> from web3.middleware import SignAndSendRawMiddlewareBuilder
    >>> from eth_account import Account
    >>> import os
    >>> acct = w3.eth.account.from_key(os.environ.get('PRIVATE_KEY'))
    >>> w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(acct), layer=0)
    >>> w3.eth.default_account = acct.address

    >>> # use `eth_sendTransaction` to automatically sign and send the raw transaction
    >>> w3.eth.send_transaction(tx_dict)
    HexBytes('0x09511acf75918fd03de58141d2fd409af4fd6d3dce48eb3aa1656c8f3c2c5c21')

Similarly, with AsyncWeb3:

.. code-block:: python

    >>> from web3 import AsyncWeb3
    >>> async_w3 = AsyncWeb3(AsyncHTTPProvider('HTTP_ENDPOINT'))
    >>> from web3.middleware import SignAndSendRawMiddlewareBuilder
    >>> from eth_account import Account
    >>> import os
    >>> acct = async_w3.eth.account.from_key(os.environ.get('PRIVATE_KEY'))
    >>> async_w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(acct), layer=0)
    >>> async_w3.eth.default_account = acct.address

    >>> # use `eth_sendTransaction` to automatically sign and send the raw transaction
    >>> await async_w3.eth.send_transaction(tx_dict)
    HexBytes('0x09511acf75918fd03de58141d2fd409af4fd6d3dce48eb3aa1656c8f3c2c5c21')

Now you can send a transaction from acct.address without having to build and sign each raw transaction.

When making use of this signing middleware, when sending dynamic fee transactions (recommended over legacy transactions),
the transaction ``type`` of ``2`` (or ``'0x2'``) is necessary. This is because transaction signing is validated based
on the transaction ``type`` parameter. This value defaults to ``'0x2'`` when ``maxFeePerGas`` and / or
``maxPriorityFeePerGas`` are present as parameters in the transaction as these params imply a dynamic fee transaction.
Since these values effectively replace the legacy ``gasPrice`` value, do not set a ``gasPrice`` for dynamic fee transactions.
Doing so will lead to validation issues.

.. code-block:: python

   # dynamic fee transaction, introduced by EIP-1559:
   >>> dynamic_fee_transaction = {
   ...     'type': '0x2',  # optional - defaults to '0x2' when dynamic fee transaction params are present
   ...     'from': acct.address,  # optional if w3.eth.default_account was set with acct.address
   ...     'to': receiving_account_address,
   ...     'value': 22,
   ...     'maxFeePerGas': 2000000000,  # required for dynamic fee transactions
   ...     'maxPriorityFeePerGas': 1000000000,  # required for dynamic fee transactions
   ... }
   >>> w3.eth.send_transaction(dynamic_fee_transaction)

A legacy transaction still works in the same way as it did before EIP-1559 was introduced:

.. code-block:: python

   >>> legacy_transaction = {
   ...     'to': receiving_account_address,
   ...     'value': 22,
   ...     'gasPrice': 123456,  # optional - if not provided, gas_price_strategy (if exists) or eth_gasPrice is used
   ... }
   >>> w3.eth.send_transaction(legacy_transaction)


Creating Custom Middleware
--------------------------

To write your own middleware, create a class and extend from the base ``Web3Middleware``
class, then override only the parts of the middleware that make sense for your use case.

.. note:: The Middleware API borrows from the Django middleware API introduced
          in version 1.10.0.

If all you need is to modify the params before a request is made, you can override
the ``request_processor`` method, make the necessary tweaks to the params, and pass the
arguments to the next element in the middleware stack. Need to do some processing on the
response? Override the ``response_processor`` method and return the modified response.

The pattern:

.. code-block:: python

    from web3.middleware import Web3Middleware

    class CustomMiddleware(Web3Middleware):

        def request_processor(self, method, params):
            # Pre-request processing goes here before passing to the next middleware.
            return (method, params)

        def response_processor(self, method, response):
            # Response processing goes here before passing to the next middleware.
            return response

        # If your provider is asynchronous, override the async methods instead:

        async def async_request_processor(self, method, params):
            # Pre-request processing goes here before passing to the next middleware.
            return (method, params)

        async def async_response_processor(self, method, response):
            # Response processing goes here before passing to the next middleware.
            return response


If you wish to prevent making a call under certain conditions, you can override the
``wrap_make_request`` method. This allows for defining pre-request processing,
skipping or making the request under certain conditions, as well as response
processing before passing it to the next middleware.


.. code-block:: python

    from web3.middleware import Web3Middleware

    class CustomMiddleware(Web3Middleware):

        def wrap_make_request(self, make_request):
            def middleware(method, params):
                # pre-request processing goes here
                response = make_request(method, params)  # make the request
                # response processing goes here
                return response

            return middleware

        # If your provider is asynchronous, override the async method instead:

        async def async_wrap_make_request(self, make_request):
            async def middleware(method, params):
                # pre-request processing goes here
                response = await make_request(method, params)
                # response processing goes here
                return response

            return middleware


Custom middleware can be added to the stack via the class itself, using the
:ref:`middleware_stack_api`. The ``name`` kwarg is optional. For example:

.. code-block:: python

    from web3 import Web3
    from my_module import (
        CustomMiddleware,
    )

    w3 = Web3(HTTPProvider(endpoint_uri="..."))

    # add the middleware to the stack as the class
    w3.middleware_onion.add(CustomMiddleware, name="custom_middleware")
