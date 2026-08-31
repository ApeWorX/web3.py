.. _quickstart:

Quickstart
==========

.. contents:: :local:

.. NOTE:: All code starting with a ``$`` is meant to run on your terminal.
    All code starting with a ``>>>`` is meant to run in a python interpreter,
    like `ipython <https://pypi.org/project/ipython/>`_.

Installation
------------

web3.py can be installed (preferably in a :ref:`virtualenv <setup_environment>`)
using ``pip`` as follows:

.. code-block:: shell

   $ pip install web3


.. NOTE:: If you run into problems during installation, you might have a
    broken environment. See the troubleshooting guide to :ref:`setting up a
    clean environment <setup_environment>`.


Using Web3
----------

This library depends on a connection to an Ethereum node. We call these connections
*Providers* and there are several ways to configure them. The full details can be found
in the :ref:`Providers<providers>` documentation. This Quickstart guide will highlight
a couple of the most common use cases.


Test Provider
*************

If you're just learning the ropes or doing some quick prototyping, you can use a test
provider, `eth-tester <https://github.com/ethereum/eth-tester>`_. This provider includes
some accounts prepopulated with test ether and instantly includes each transaction into a block.
web3.py makes this test provider available via ``EthereumTesterProvider``.

.. note::

  The ``EthereumTesterProvider`` requires additional dependencies. Install them via
  ``pip install "web3[tester]"``, then import and instantiate the provider as seen below.

.. code-block:: python

   >>> from web3 import Web3, EthereumTesterProvider
   >>> w3 = Web3(EthereumTesterProvider())
   >>> w3.is_connected()
   True


Local Providers
***************

The hardware requirements are `steep <https://ethereum.org/en/developers/docs/nodes-and-clients/run-a-node/#top>`_,
but the safest way to interact with Ethereum is to run an Ethereum client on your own hardware.
For locally run nodes, an IPC connection is the most secure option, but HTTP and
websocket configurations are also available. By default, the popular `Geth client <https://geth.ethereum.org/>`_
exposes port ``8545`` to serve HTTP requests and ``8546`` for websocket requests. Connecting
to this local node can be done as follows:

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

   # AsyncIPCProvider:
   >>> w3 = await AsyncWeb3(AsyncWeb3.AsyncIPCProvider('./path/to/filename.ipc'))
   >>> await w3.is_connected()
   True


Remote Providers
****************

The quickest way to interact with the Ethereum blockchain is to use a `remote node provider <https://ethereum.org/en/developers/docs/nodes-and-clients/nodes-as-a-service/#popular-node-services>`_.
You can connect to a remote node by specifying the endpoint, just like the previous local node example:

.. code-block:: python

   >>> from web3 import Web3, AsyncWeb3

   >>> w3 = Web3(Web3.HTTPProvider('https://<your-provider-url>'))

   >>> w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider('https://<your-provider-url>'))

   >>> w3 = await AsyncWeb3(AsyncWeb3.WebSocketProvider('wss://<your-provider-url>'))

This endpoint is provided by the remote node service, typically after you create an account.

.. _first_w3_use:


Getting Blockchain Info
-----------------------

It's time to start using web3.py! Once properly configured, the ``w3`` instance will allow you
to interact with the Ethereum blockchain. Try getting all the information about the latest block:

.. code-block:: python

    >>> w3.eth.get_block('latest')
    {'difficulty': 1,
     'gasLimit': 6283185,
     'gasUsed': 0,
     'hash': HexBytes('0x53b983fe73e16f6ed8178f6c0e0b91f23dc9dad4cb30d0831f178291ffeb8750'),
     'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
     'miner': '0x0000000000000000000000000000000000000000',
     'mixHash': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'),
     'nonce': HexBytes('0x0000000000000000'),
     'number': 0,
     'parentHash': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'),
     'proofOfAuthorityData': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000dddc391ab2bf6701c74d0c8698c2e13355b2e4150000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
     'receiptsRoot': HexBytes('0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421'),
     'sha3Uncles': HexBytes('0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347'),
     'size': 622,
     'stateRoot': HexBytes('0x1f5e460eb84dc0606ab74189dbcfe617300549f8f4778c3c9081c119b5b5d1c1'),
     'timestamp': 0,
     'totalDifficulty': 1,
     'transactions': [],
     'transactionsRoot': HexBytes('0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421'),
     'uncles': []}

web3.py can help you read block data, sign and send transactions, deploy and interact with contracts,
and a number of other features.

A few suggestions from here:

- The :doc:`overview` page provides a summary of web3.py's features.
- The :class:`w3.eth <web3.eth.Eth>` API contains the most frequently used methods.
- A guide to :ref:`contracts` includes deployment and usage examples.
- The nuances of :doc:`transactions` are explained in another guide.

.. NOTE:: It is recommended that your development environment have the ``PYTHONWARNINGS=default``
    environment variable set. Some deprecation warnings will not show up
    without this variable being set.
