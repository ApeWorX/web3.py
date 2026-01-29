.. _overview:

Overview
========

The purpose of this page is to give you a sense of everything web3.py can do
and to serve as a quick reference guide. You'll find a summary of each feature
with links to learn more.

Configuration
-------------

After installing web3.py (via ``pip install web3``), you'll need to configure
a provider endpoint and any middleware you want to use beyond the defaults.


Providers
~~~~~~~~~

:doc:`providers` are how web3.py connects to a blockchain. The library comes with the
following built-in providers:

- :class:`~web3.providers.rpc.HTTPProvider` for connecting to http and https based JSON-RPC servers.
- :class:`~web3.providers.ipc.IPCProvider` for connecting to ipc socket based JSON-RPC servers.
- :class:`~web3.providers.async_rpc.AsyncHTTPProvider` for connecting to http and https based JSON-RPC servers asynchronously.
- :class:`~web3.providers.persistent.AsyncIPCProvider` for connecting to ipc socket based JSON-RPC servers asynchronously via a persistent connection.
- :class:`~web3.providers.persistent.WebSocketProvider` for connecting to websocket based JSON-RPC servers asynchronously via a persistent connection.

Examples
````````

.. code-block:: python

   >>> from web3 import Web3, AsyncWeb3

   # IPCProvider:
   >>> w3 = Web3(Web3.IPCProvider('./path/to/filename.ipc'))
   >>> w3.is_connected()
   True

   # HTTPProvider:
   >>> w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
   >>> w3.is_connected()
   True

   # AsyncHTTPProvider:
   >>> w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider('http://127.0.0.1:8545'))
   >>> await w3.is_connected()
   True

   # -- Persistent Connection Providers -- #

   # WebSocketProvider:
   >>> w3 = await AsyncWeb3(AsyncWeb3.WebSocketProvider('ws://127.0.0.1:8546'))
   >>> await w3.is_connected()
   True

   # AsyncIPCProvider
   >>> w3 = await AsyncWeb3(AsyncWeb3.AsyncIPCProvider('./path/to/filename.ipc'))
   >>> await w3.is_connected()
   True


For more context, see the :doc:`providers` documentation.


Middleware
~~~~~~~~~~

Your web3.py instance may be further configured via :doc:`middleware`.

web3.py middleware is described using an onion metaphor, where each layer of
middleware may affect both the incoming request and outgoing response from your
provider. The documentation includes a :ref:`visualization <Modifying_Middleware>`
of this idea.

Several middleware are :ref:`included by default <default_middleware>`. You may add to
(:meth:`add <Web3.middleware_onion.add>`, :meth:`inject <Web3.middleware_onion.inject>`,
:meth:`replace <Web3.middleware_onion.replace>`) or disable
(:meth:`remove <Web3.middleware_onion.remove>`,
:meth:`clear <Web3.middleware_onion.clear>`) any of these middleware.


Accounts and Private Keys
-------------------------

Private keys are required to approve any transaction made on your behalf. The manner in
which your key is secured will determine how you create and send transactions in web3.py.

A local node, like `Geth <https://geth.ethereum.org/>`_, may manage your keys for you.
You can reference those keys using the :attr:`web3.eth.accounts <web3.eth.Eth.accounts>`
property.

A hosted node, like `Infura <https://infura.io/>`_, will have no knowledge of your keys.
In this case, you'll need to have your private key available locally for signing
transactions.

Full documentation on the distinction between keys can be found :ref:`here <eth-account>`.
The separate guide to :doc:`transactions` may also help clarify how to manage keys.


Base API
--------

The :ref:`Web3 <web3_base>` class includes a number of convenient utility functions:


Encoding and Decoding Helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- :meth:`Web3.is_encodable() <web3.w3.is_encodable>`
- :meth:`Web3.to_bytes() <web3.Web3.to_bytes>`
- :meth:`Web3.to_hex() <web3.Web3.to_hex>`
- :meth:`Web3.to_int() <web3.Web3.to_int>`
- :meth:`Web3.to_json() <web3.Web3.to_json>`
- :meth:`Web3.to_text() <web3.Web3.to_text>`


Address Helpers
~~~~~~~~~~~~~~~

- :meth:`Web3.is_address() <web3.Web3.is_address>`
- :meth:`Web3.is_checksum_address() <web3.Web3.is_checksum_address>`
- :meth:`Web3.to_checksum_address() <web3.Web3.to_checksum_address>`


Currency Conversions
~~~~~~~~~~~~~~~~~~~~

- :meth:`Web3.from_wei() <web3.Web3.from_wei>`
- :meth:`Web3.to_wei() <web3.Web3.to_wei>`


Cryptographic Hashing
~~~~~~~~~~~~~~~~~~~~~

- :meth:`Web3.keccak() <web3.Web3.keccak>`
- :meth:`Web3.solidity_keccak() <web3.Web3.solidity_keccak>`


web3.eth API
------------

The most commonly used APIs for interacting with Ethereum can be found under the
:ref:`web3-eth` namespace.


Fetching Data
~~~~~~~~~~~~~

Viewing account balances (:meth:`get_balance <web3.eth.Eth.get_balance>`), transactions
(:meth:`get_transaction <web3.eth.Eth.get_transaction>`), and block data
(:meth:`get_block <web3.eth.Eth.get_block>`) are some of the most common starting
points in web3.py.


API
```

- :meth:`web3.eth.get_balance() <web3.eth.Eth.get_balance>`
- :meth:`web3.eth.get_block() <web3.eth.Eth.get_block>`
- :meth:`web3.eth.get_block_transaction_count() <web3.eth.Eth.get_block_transaction_count>`
- :meth:`web3.eth.get_code() <web3.eth.Eth.get_code>`
- :meth:`web3.eth.get_proof() <web3.eth.Eth.get_proof>`
- :meth:`web3.eth.get_storage_at() <web3.eth.Eth.get_storage_at>`
- :meth:`web3.eth.get_transaction() <web3.eth.Eth.get_transaction>`
- :meth:`web3.eth.get_transaction_by_block() <web3.eth.Eth.get_transaction_by_block>`
- :meth:`web3.eth.get_transaction_count() <web3.eth.Eth.get_transaction_count>`


Sending Transactions
~~~~~~~~~~~~~~~~~~~~

The most common use cases will be satisfied with
:meth:`send_transaction <web3.eth.Eth.send_transaction>` or the combination of
:meth:`sign_transaction <web3.eth.Eth.sign_transaction>` and
:meth:`send_raw_transaction <web3.eth.Eth.send_raw_transaction>`. For more context,
see the full guide to :doc:`transactions`.

.. note::

   If interacting with a smart contract, a dedicated API exists. See the next
   section, :ref:`Contracts <overview_contracts>`.


API
```

- :meth:`web3.eth.send_transaction() <web3.eth.Eth.send_transaction>`
- :meth:`web3.eth.sign_transaction() <web3.eth.Eth.sign_transaction>`
- :meth:`web3.eth.send_raw_transaction() <web3.eth.Eth.send_raw_transaction>`
- :meth:`web3.eth.replace_transaction() <web3.eth.Eth.replace_transaction>`
- :meth:`web3.eth.modify_transaction() <web3.eth.Eth.modify_transaction>`
- :meth:`web3.eth.wait_for_transaction_receipt() <web3.eth.Eth.wait_for_transaction_receipt>`
- :meth:`web3.eth.get_transaction_receipt() <web3.eth.Eth.get_transaction_receipt>`
- :meth:`web3.eth.sign() <web3.eth.Eth.sign>`
- :meth:`web3.eth.sign_typed_data() <web3.eth.Eth.sign_typed_data>`
- :meth:`web3.eth.estimate_gas() <web3.eth.Eth.estimate_gas>`
- :meth:`web3.eth.generate_gas_price() <web3.eth.Eth.generate_gas_price>`
- :meth:`web3.eth.set_gas_price_strategy() <web3.eth.Eth.set_gas_price_strategy>`


.. _overview_contracts:

Contracts
---------

web3.py can help you deploy, read from, or execute functions on a deployed contract.

Deployment requires that the contract already be compiled, with its bytecode and ABI
available. This compilation step can be done within
`Remix <http://remix.ethereum.org/>`_ or one of the many contract development
frameworks, such as `Ape <https://docs.apeworx.io/ape/stable/index.html>`_.

Once the contract object is instantiated, calling ``transact`` on the
:meth:`constructor <web3.contract.Contract.constructor>` method will deploy an
instance of the contract:

.. code-block:: python

   >>> ExampleContract = w3.eth.contract(abi=abi, bytecode=bytecode)
   >>> tx_hash = ExampleContract.constructor().transact()
   >>> tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
   >>> tx_receipt.contractAddress
   '0x8a22225eD7eD460D7ee3842bce2402B9deaD23D3'

Once a deployed contract is loaded into a Contract object, the functions of that
contract are available on the ``functions`` namespace:

.. code-block:: python

   >>> deployed_contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
   >>> deployed_contract.functions.myFunction(42).transact()

If you want to read data from a contract (or see the result of transaction locally,
without executing it on the network), you can use the
:meth:`ContractFunction.call <web3.contract.ContractFunction.call>` method, or the
more concise :attr:`ContractCaller <web3.contract.ContractCaller>` syntax:

.. code-block:: python

   # Using ContractFunction.call
   >>> deployed_contract.functions.getMyValue().call()
   42

   # Using ContractCaller
   >>> deployed_contract.caller().getMyValue()
   42

For more, see the full :ref:`Contracts` documentation.


API
~~~

- :meth:`web3.eth.contract() <web3.eth.Eth.contract>`
- :attr:`Contract.address <web3.contract.Contract.address>`
- :attr:`Contract.abi <web3.contract.Contract.abi>`
- :attr:`Contract.bytecode <web3.contract.Contract.bytecode>`
- :attr:`Contract.bytecode_runtime <web3.contract.Contract.bytecode_runtime>`
- :attr:`Contract.functions <web3.contract.Contract.functions>`
- :attr:`Contract.events <web3.contract.Contract.events>`
- :attr:`Contract.fallback <web3.contract.Contract.fallback.call>`
- :meth:`Contract.constructor() <web3.contract.Contract.constructor>`
- :meth:`Contract.encode_abi() <web3.contract.Contract.encode_abi>`
- :attr:`web3.contract.ContractFunction <web3.contract.ContractFunction>`
- :attr:`web3.contract.ContractEvents <web3.contract.ContractEvents>`


Events, Logs, and Filters
-------------------------

If you want to react to new blocks being mined or specific events being emitted by
a contract, you can leverage ``get_logs``, subscriptions, or filters.

See the :doc:`filters` guide for more information.


API
~~~

- :meth:`web3.eth.subscribe() <web3.eth.Eth.subscribe>`
- :meth:`web3.eth.filter() <web3.eth.Eth.filter>`
- :meth:`web3.eth.get_filter_changes() <web3.eth.Eth.get_filter_changes>`
- :meth:`web3.eth.get_filter_logs() <web3.eth.Eth.get_filter_logs>`
- :meth:`web3.eth.uninstall_filter() <web3.eth.Eth.uninstall_filter>`
- :meth:`web3.eth.get_logs() <web3.eth.Eth.get_logs>`
- :meth:`Contract.events.your_event_name.create_filter() <web3.contract.Contract.events.your_event_name.create_filter>`
- :meth:`Contract.events.your_event_name.build_filter() <web3.contract.Contract.events.your_event_name.build_filter>`
- :meth:`Filter.get_new_entries() <web3.utils.filters.Filter.get_new_entries>`
- :meth:`Filter.get_all_entries() <web3.utils.filters.Filter.get_all_entries>`
- :meth:`Filter.format_entry() <web3.utils.filters.Filter.format_entry>`
- :meth:`Filter.is_valid_entry() <web3.utils.filters.Filter.is_valid_entry>`


Net API
-------

Some basic network properties are available on the ``web3.net`` object:

- :attr:`web3.net.listening`
- :attr:`web3.net.peer_count`
- :attr:`web3.net.version`


ENS
---

`Ethereum Name Service (ENS) <https://ens.domains/>`_ provides the infrastructure
for human-readable addresses. If an address is registered with the ENS registry,
the domain name can be used in place of the address itself. For example, the registered domain
name ``ethereum.eth`` will resolve to the address
``0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe``. web3.py has support for ENS, documented
:ref:`here <ens_overview>`.
