Troubleshooting
===============

.. _setup_environment:

Set up a clean environment
--------------------------

Many things can cause a broken environment. You might be on an unsupported version of Python.
Another package might be installed that has a name or version conflict.
Often, the best way to guarantee a correct environment is with ``virtualenv``, like:

.. code-block:: shell

    # Install pip if it is not available:
    $ which pip || curl https://bootstrap.pypa.io/get-pip.py | python

    # Install virtualenv if it is not available:
    $ which virtualenv || pip install --upgrade virtualenv

    # *If* the above command displays an error, you can try installing as root:
    $ sudo pip install virtualenv

    # Create a virtual environment:
    $ virtualenv -p python3 ~/.venv-py3

    # Activate your new virtual environment:
    $ source ~/.venv-py3/bin/activate

    # With virtualenv active, make sure you have the latest packaging tools
    $ pip install --upgrade pip setuptools

    # Now we can install web3.py...
    $ pip install --upgrade web3

.. NOTE:: Remember that each new terminal session requires you to reactivate your virtualenv, like:
    ``$ source ~/.venv-py3/bin/activate``


.. _instance_troubleshooting:

Why can't I use a particular function?
--------------------------------------

Note that a web3.py instance must be configured before you can use most of its capabilities.
One symptom of not configuring the instance first is an error that looks something like this:
``AttributeError: type object 'Web3' has no attribute 'eth'``.

To properly configure your web3.py instance, specify which provider you're using to connect to the
Ethereum network. An example configuration, if you're connecting to a locally run node, might be:

.. code-block:: python

    >>> from web3 import Web3
    >>> w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

    # now `w3` is available to use:
    >>> w3.is_connected()
    True
    >>> w3.eth.send_transaction(...)

Refer to the :ref:`providers` documentation for further help with configuration.


.. _use_metamask_accounts:

Why isn't my web3 instance connecting to the network?
-----------------------------------------------------
You can check that your instance is connected via the ``is_connected`` method:

.. code-block:: python

    >>> w3.is_connected()
    False

There are a variety of explanations for why you may see ``False`` here. To help you
diagnose the problem, ``is_connected`` has an optional ``show_traceback`` argument:

.. code-block:: python

    >>> w3.is_connected(show_traceback=True)
    # this is an example, your error may differ

    # <long stack trace output>
    ProviderConnectionError: Problem connecting to provider with error: <class 'FileNotFoundError'>: cannot connect to IPC socket at path: None

If you're running a local node, such as Geth, double-check that you've indeed started
the binary and that you've started it from the intended directory - particularly if
you've specified a relative path to its ipc file.

If that does not address your issue, it's probable that you still have a
Provider configuration issue. There are several options for configuring
a Provider, detailed :ref:`here<providers>`.

.. _faucets:

How do I get ether for my test network?
---------------------------------------

Test networks usually have something called a "faucet" to
help get test ether to people who want to use it. The faucet
simply sends you test ether when you visit a web page, or ping a chat bot, etc.

Each test network has its own version of test ether, so each one must maintain
its own faucet. Faucet mechanisms tend to come and go, so a web search for
"ethereum testnet faucet" should give you the most up-to-date options.

How do I use my MetaMask accounts from web3.py?
-----------------------------------------------

Export your private key from MetaMask, and use
the local private key tools in web3.py to sign and send transactions.

See `how to export your private key
<https://ethereum.stackexchange.com/questions/33053/what-is-a-private-key-in-an-ethereum-wallet-like-metamask-and-how-do-i-find-it>`_
and :ref:`eth-account`.

.. _account_troubleshooting:

How do I create an account?
---------------------------

In general, your options for accounts are:

- Import a keystore file for an account and :ref:`extract the private key<extract_geth_pk>`.
- Create an account via the :ref:`eth-account <eth-account>` API, e.g., ``new_acct = w3.eth.account.create()``.
- Use an external service (e.g. Metamask) to generate a new account, then securely import its private key.

.. Warning:: Don't store real value in an account until you are familiar with security best practices.
   If you lose your private key, you lose your account!

Why doesn't my transaction work on another network?
---------------------------------------------------

web3.py is an Ethereum-specific library, which defaults to
`"type 2" EIP-1559 transactions <https://ethereum.org/en/developers/docs/transactions/#typed-transaction-envelope>`_
as of the London network upgrade. Some chains (including Ethereum L2s) do not support
the same transaction types.

If your chain doesn't support this transaction type, you likely need to create a
"legacy" transaction, i.e., include ``gasPrice``, but not ``type``, ``maxFeePerGas``,
or ``maxPriorityFeePerGas`` in your transaction body.

If that doesn't resolve your issue, open a GitHub issue or reach out for help in the community
`Discord`_ server if you're having trouble with an Ethereum-ecosystem chain. If you're
debugging in an alternative ecosystem, please find another appropriate forum to raise
your question.

.. _Discord: https://discord.gg/GHryRvPB84


How do I conform to ABI types?
------------------------------

The web3 library follows the following conventions:

Bytes vs Text
~~~~~~~~~~~~~

* The term *bytes* is used to refer to the binary representation of a string.
* The term *text* is used to refer to unicode representations of strings.

Hexadecimal Representations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* All hexadecimal values will be returned as text.
* All hexadecimal values will be ``0x`` prefixed.

Ethereum Addresses
~~~~~~~~~~~~~~~~~~

All addresses must be supplied in one of three ways:

* A 20-byte hexadecimal that is checksummed using the `EIP-55
  <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md>`_ spec.
* A 20-byte binary address (python bytes type).
* While connected to an Ethereum Name Service (ENS) supported chain, an ENS name
  (often in the form ``myname.eth``).

Disabling Strict Bytes Type Checking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a boolean flag on the ``Web3`` class and the ``ENS`` class that will disable
strict bytes type checking. This allows bytes values of Python strings and allows byte
strings less than the specified byte size, appropriately padding values that need
padding. To disable stricter checks, set the ``w3.strict_bytes_type_checking``
(or ``ns.strict_bytes_type_checking``) flag to ``False``. This will no longer cause
the ``Web3`` / ``ENS`` instance to raise an error if a Python string is passed in
without a "0x" prefix. It will also render valid byte strings or hex strings
that are below the exact number of bytes specified by the ABI type by padding the value
appropriately, according to the ABI type. See the :ref:`disable-strict-byte-check`
section for an example on using the flag and more details.

.. note::
    If a standalone ``ENS`` instance is instantiated from a ``Web3`` instance, i.e.
    ``ns = ENS.from_web3(w3)``, it will inherit the value of the
    ``w3.strict_bytes_type_checking`` flag from the ``Web3`` instance at the time of
    instantiation.

    Also of note, all modules on the ``Web3`` class will inherit the value of this flag,
    since all modules use the parent ``w3`` object reference under the hood. This means
    that ``w3.eth.w3.strict_bytes_type_checking`` will always have the same value as
    ``w3.strict_bytes_type_checking``.


For more details on the ABI
specification, refer to the
`Solidity ABI Spec <https://docs.soliditylang.org/en/latest/abi-spec.html>`_.


Types by Example
~~~~~~~~~~~~~~~~

Let's use a contrived contract to demonstrate input types in web3.py:

.. code-block:: none

   contract ManyTypes {
       // booleans
       bool public b;

       // unsigned ints
       uint8 public u8;
       uint256 public u256;
       uint256[] public u256s;

       // signed ints
       int8 public i8;

       // addresses
       address public addr;
       address[] public addrs;

       // bytes
       bytes1 public b1;

       // structs
       struct S {
         address sa;
         bytes32 sb;
       }
       mapping(address => S) addrStructs;

       function updateBool(bool x) public { b = x; }
       function updateUint8(uint8 x) public { u8 = x; }
       function updateUint256(uint256 x) public { u256 = x; }
       function updateUintArray(uint256[] memory x) public { u256s = x; }
       function updateInt8(int8 x) public { i8 = x; }
       function updateAddr(address x) public { addr = x; }
       function updateBytes1(bytes1 x) public { b1 = x; }
       function updateMapping(S memory x) public { addrStructs[x.sa] = x; }
   }

Booleans
````````

.. code-block:: python

   contract_instance.functions.updateBool(True).transact()

Unsigned Integers
`````````````````

.. code-block:: python

   contract_instance.functions.updateUint8(255).transact()
   contract_instance.functions.updateUint256(2**256 - 1).transact()
   contract_instance.functions.updateUintArray([1, 2, 3]).transact()

Signed Integers
```````````````

.. code-block:: python

   contract_instance.functions.updateInt8(-128).transact()

Addresses
`````````

.. code-block:: python

   contract_instance.functions.updateAddr("0x0000000000000000000000000000000000000000").transact()

Bytes
`````

.. code-block:: python

   contract_instance.functions.updateBytes1(HexBytes(255)).transact()

Structs
```````

.. code-block:: python

   contract_instance.functions.updateMapping({"sa": "0x0000000000000000000000000000000000000000", "sb": HexBytes(123)}).transact()


How can I optimize Ethereum JSON-RPC API access?
------------------------------------------------

Your Ethereum node JSON-RPC API might be slow when fetching multiple and large requests, especially when running batch jobs. Here are some tips for how to speed up your web3.py application.

- Run your client locally, e.g., `Go Ethereum <https://github.com/ethereum/go-ethereum>`_ or `TurboGeth <https://github.com/ledgerwatch/turbo-geth>`_. The network latency and speed are the major limiting factors for fast API access.

- Use IPC communication instead of HTTP/WebSockets. See :ref:`choosing_provider`.

- Use an optimised JSON decoder. A future iteration of web3.py may change the default decoder or provide an API to configure one, but for now, you may patch the provider class to use `ujson <https://pypi.org/project/ujson/>`_.

.. code-block:: python

    """JSON-RPC decoding optimised for web3.py"""

    from typing import cast

    import ujson

    from web3.providers import JSONBaseProvider
    from web3.types import RPCResponse


    def _fast_decode_rpc_response(raw_response: bytes) -> RPCResponse:
        decoded = ujson.loads(raw_response)
        return cast(RPCResponse, decoded)


    def patch_provider(provider: JSONBaseProvider):
        """Monkey-patch web3.py provider for faster JSON decoding.

        Call this on your provider after construction.

        This greatly improves JSON-RPC API access speeds, when fetching
        multiple and large responses.
        """
        provider.decode_rpc_response = _fast_decode_rpc_response

Why am I getting Visual C++ or Cython not installed error?
----------------------------------------------------------

Some Windows users that do not have Microsoft Visual C++ version 14.0 or greater installed may see an error message
when installing web3.py as shown below:

.. code-block:: shell

    error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/


To fix this error, download and install Microsoft Visual C++ from here :

`Microsoft Visual C++ Redistributable for Visual Studio <https://visualstudio.microsoft.com/downloads/#microsoft-visual-c-redistributable-for-visual-studio-2019>`_

- `x64 Visual C++ <https://aka.ms/vs/16/release/VC_redist.x64.exe>`_

- `x86 Visual C++ <https://aka.ms/vs/16/release/VC_redist.x86.exe>`_

- `ARM64 Visual C++ <https://aka.ms/vs/16/release/VC_redist.arm64.exe>`_


How do I convert currency denominations?
----------------------------------------

The following denominations are supported:

+--------------+---------------------------------+
| denomination | amount in wei                   |
+--------------+---------------------------------+
| wei          | 1                               |
+--------------+---------------------------------+
| kwei         | 1000                            |
+--------------+---------------------------------+
| babbage      | 1000                            |
+--------------+---------------------------------+
| femtoether   | 1000                            |
+--------------+---------------------------------+
| mwei         | 1000000                         |
+--------------+---------------------------------+
| lovelace     | 1000000                         |
+--------------+---------------------------------+
| picoether    | 1000000                         |
+--------------+---------------------------------+
| gwei         | 1000000000                      |
+--------------+---------------------------------+
| shannon      | 1000000000                      |
+--------------+---------------------------------+
| nanoether    | 1000000000                      |
+--------------+---------------------------------+
| nano         | 1000000000                      |
+--------------+---------------------------------+
| szabo        | 1000000000000                   |
+--------------+---------------------------------+
| microether   | 1000000000000                   |
+--------------+---------------------------------+
| micro        | 1000000000000                   |
+--------------+---------------------------------+
| finney       | 1000000000000000                |
+--------------+---------------------------------+
| milliether   | 1000000000000000                |
+--------------+---------------------------------+
| milli        | 1000000000000000                |
+--------------+---------------------------------+
| ether        | 1000000000000000000             |
+--------------+---------------------------------+
| kether       | 1000000000000000000000          |
+--------------+---------------------------------+
| grand        | 1000000000000000000000          |
+--------------+---------------------------------+
| mether       | 1000000000000000000000000       |
+--------------+---------------------------------+
| gether       | 1000000000000000000000000000    |
+--------------+---------------------------------+
| tether       | 1000000000000000000000000000000 |
+--------------+---------------------------------+

You can use the :meth:`~web3.from_wei` method
to convert a balance to ether (or another denomination).

.. code-block:: python

    >>> web3.from_wei(3841357360894980500000001, 'ether')
    Decimal('3841357.360894980500000001')

To convert back to wei, you can use the inverse function, :meth:`~web3.to_wei`.
Note that Python's default floating point precision is insufficient for this
use case, so it's necessary to cast the value to a
`Decimal <https://docs.python.org/3/library/decimal.html>`_ if it isn't already.

.. code-block:: python

    >>> from decimal import Decimal
    >>> web3.to_wei(Decimal('3841357.360894980500000001'), 'ether')
    3841357360894980500000001

Best practice: If you need to work with multiple currency denominations, default
to wei. A typical workflow may require a conversion from some denomination to
wei, then from wei to whatever you need.

.. code-block:: python

    >>> web3.to_wei(Decimal('0.000000005'), 'ether')
    5000000000
    >>> web3.from_wei(5000000000, 'gwei')
    Decimal('5')


How do I adjust the log levels?
-------------------------------

web3.py internally uses `Python logging subsystem <https://docs.python.org/3/library/logging.html>`_.

If you want to run your application logging in debug mode, below is an example of how to make some JSON-RPC traffic quieter.

.. code-block:: python

    import logging
    import coloredlogs

    def setup_logging(log_level=logging.DEBUG):
        """Setup root logger and quiet some levels."""
        logger = logging.getLogger()

        # Set log format to display the logger name to hunt down verbose logging modules
        fmt = "%(name)-25s %(levelname)-8s %(message)s"

        # Use colored logging output for console with the coloredlogs package
        # https://pypi.org/project/coloredlogs/
        coloredlogs.install(level=log_level, fmt=fmt, logger=logger)

        # Disable logging of JSON-RPC requests and replies
        logging.getLogger("web3.RequestManager").setLevel(logging.WARNING)
        logging.getLogger("web3.providers.HTTPProvider").setLevel(logging.WARNING)
        # logging.getLogger("web3.RequestManager").propagate = False

        # Disable all internal debug logging of requests and urllib3
        # E.g. HTTP traffic
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        return logger
