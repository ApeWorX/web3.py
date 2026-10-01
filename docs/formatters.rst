.. _formatters:

Formatters
==========

Formatters are a core part of web3.py's data transformation pipeline. They convert
data between Python-friendly formats and the hexadecimal formats required by the
Ethereum JSON-RPC specification. This page explains how formatters work, what the
default formatters do, and how to customize them.

.. note::

    For a deep dive into how requests flow through web3.py, including formatters,
    see the excellent blog post:
    `Web3.py Internals: JSON-RPC Round Trips <https://snakecharmers.ethereum.org/web3py-internals-json-rpc-round-trips/>`_


How Formatters Work
-------------------

When you make a call like ``w3.eth.get_balance("0x123...")``, your request goes
through several transformation steps before reaching the Ethereum node, and the
response goes through similar transformations before being returned to you.

The Request/Response Flow
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    Your Python Code
          |
          v
    +-----------------+
    |  Input Mungers  |  <- Set default values (e.g., block_identifier="latest")
    +-----------------+
          |
          v
    +---------------------+
    | Request Formatters  |  <- Convert Python types to JSON-RPC format
    +---------------------+
          |
          v
    +-----------------+
    |   Middleware    |  <- Additional processing (e.g., ENS resolution)
    +-----------------+
          |
          v
    +-----------------+
    |    Provider     |  <- Send JSON-RPC request to Ethereum node
    +-----------------+
          |
          v
      Ethereum Node
          |
          v
    +-----------------+
    |    Provider     |  <- Receive JSON-RPC response
    +-----------------+
          |
          v
    +-----------------+
    |   Middleware    |  <- Process response
    +-----------------+
          |
          v
    +--------------------+
    | Result Formatters  |  <- Convert JSON-RPC format to Python types
    +--------------------+
          |
          v
    Your Python Code


Types of Formatters
~~~~~~~~~~~~~~~~~~~

web3.py uses several types of formatters:

1. **Request Formatters**: Transform outgoing request parameters from Python types
   to the format expected by Ethereum nodes (e.g., integers to hex strings).

2. **Result Formatters**: Transform incoming response data from JSON-RPC format
   to Python-friendly types (e.g., hex strings to integers or ``HexBytes``).

3. **Error Formatters**: Process error responses to raise appropriate exceptions
   with meaningful messages.

4. **Null Result Formatters**: Handle cases where the response is ``None`` or empty.


Default Formatters
------------------

web3.py includes a comprehensive set of default formatters that handle common
data transformations. These are defined in ``web3._utils.method_formatters``.

Pythonic Request Formatters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``PYTHONIC_REQUEST_FORMATTERS`` convert Python types to JSON-RPC compatible
formats before sending requests:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Transformation
     - Example
   * - Integers to hex strings
     - ``500000`` → ``"0x7a120"``
   * - Block identifiers
     - ``"latest"`` (unchanged) or ``12345`` → ``"0x3039"``
   * - Addresses to checksummed format
     - Validates and formats addresses
   * - Transaction parameters
     - Formats ``gas``, ``gasPrice``, ``value``, ``nonce`` to hex

Example transformations by method:

- **eth_getBalance**: Block number parameter converted to hex
- **eth_call**: Transaction object fields formatted, block identifier converted
- **eth_sendTransaction**: All numeric fields (gas, value, nonce) converted to hex
- **eth_getBlockByNumber**: Block identifier converted to hex
- **eth_getLogs**: ``fromBlock`` and ``toBlock`` converted to hex


Pythonic Result Formatters
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``PYTHONIC_RESULT_FORMATTERS`` convert JSON-RPC responses to Python types:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Method
     - Transformation
     - Example
   * - eth_getBalance
     - Hex to integer
     - ``"0x83a3c396d1a7b40"`` → ``583760663573639744``
   * - eth_blockNumber
     - Hex to integer
     - ``"0xf4240"`` → ``1000000``
   * - eth_getBlock
     - Full block formatting
     - Formats all block fields
   * - eth_getTransaction
     - Full transaction formatting
     - Formats all transaction fields
   * - eth_getTransactionReceipt
     - Receipt formatting
     - Formats logs, status, gas used
   * - eth_chainId
     - Hex to integer
     - ``"0x1"`` → ``1``
   * - eth_gasPrice
     - Hex to integer
     - ``"0x3b9aca00"`` → ``1000000000``


Block Result Formatters
~~~~~~~~~~~~~~~~~~~~~~~

Block responses are formatted with ``BLOCK_RESULT_FORMATTERS``:

.. code-block:: python

    {
        "baseFeePerGas": to_integer_if_hex,
        "difficulty": to_integer_if_hex,
        "gasLimit": to_integer_if_hex,
        "gasUsed": to_integer_if_hex,
        "number": to_integer_if_hex,
        "size": to_integer_if_hex,
        "timestamp": to_integer_if_hex,
        "totalDifficulty": to_integer_if_hex,
        "hash": to_hexbytes(32),
        "parentHash": to_hexbytes(32),
        "miner": to_checksum_address,
        "transactions": [list of tx hashes or full tx objects],
        # ... and more
    }


Transaction Result Formatters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transaction responses are formatted with ``TRANSACTION_RESULT_FORMATTERS``:

.. code-block:: python

    {
        "blockNumber": to_integer_if_hex,
        "gas": to_integer_if_hex,
        "gasPrice": to_integer_if_hex,
        "nonce": to_integer_if_hex,
        "transactionIndex": to_integer_if_hex,
        "value": to_integer_if_hex,
        "v": to_integer_if_hex,
        "from": to_checksum_address,
        "to": to_checksum_address,
        "hash": to_hexbytes(32),
        "input": HexBytes,
        "r": to_hexbytes(32),
        "s": to_hexbytes(32),
        # ... and more
    }


Log Entry Formatters
~~~~~~~~~~~~~~~~~~~~

Log entries (events) are formatted with ``LOG_ENTRY_FORMATTERS``:

.. code-block:: python

    {
        "blockNumber": to_integer_if_hex,
        "logIndex": to_integer_if_hex,
        "transactionIndex": to_integer_if_hex,
        "address": to_checksum_address,
        "blockHash": to_hexbytes(32),
        "transactionHash": to_hexbytes(32),
        "data": HexBytes,
        "topics": [list of HexBytes(32)],
    }


Using FormattingMiddlewareBuilder
---------------------------------

For custom formatting needs, you can use the ``FormattingMiddlewareBuilder`` class
to create middleware that applies your own formatters.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    from web3 import Web3
    from web3.middleware import FormattingMiddlewareBuilder

    w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

    # Create middleware with custom formatters
    custom_middleware = FormattingMiddlewareBuilder.build(
        request_formatters={
            "eth_myCustomMethod": lambda params: [p.upper() for p in params]
        },
        result_formatters={
            "eth_myCustomMethod": lambda result: result.lower()
        },
    )

    # Add to middleware stack
    w3.middleware_onion.add(custom_middleware)


Request Formatters Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

Request formatters receive the parameters list and should return the transformed
parameters:

.. code-block:: python

    from web3.middleware import FormattingMiddlewareBuilder

    def my_request_formatter(params):
        """Transform request parameters before sending."""
        # params is a list of parameters for the RPC method
        address, block_id = params
        # Ensure address is lowercase
        return [address.lower(), block_id]

    custom_middleware = FormattingMiddlewareBuilder.build(
        request_formatters={
            "eth_getBalance": my_request_formatter,
        }
    )


Result Formatters Example
~~~~~~~~~~~~~~~~~~~~~~~~~

Result formatters receive the result value and should return the transformed result:

.. code-block:: python

    from web3.middleware import FormattingMiddlewareBuilder
    from decimal import Decimal

    def balance_to_ether(result):
        """Convert balance from wei to ether."""
        wei_balance = int(result, 16) if isinstance(result, str) else result
        return Decimal(wei_balance) / Decimal(10**18)

    custom_middleware = FormattingMiddlewareBuilder.build(
        result_formatters={
            "eth_getBalance": balance_to_ether,
        }
    )

    w3.middleware_onion.add(custom_middleware)

    # Now get_balance returns Decimal in ether instead of int in wei
    balance = w3.eth.get_balance("0x...")  # Returns Decimal("1.5") instead of 1500000000000000000


Error Formatters Example
~~~~~~~~~~~~~~~~~~~~~~~~

Error formatters process error responses:

.. code-block:: python

    from web3.middleware import FormattingMiddlewareBuilder

    def custom_error_formatter(error):
        """Add custom error handling."""
        if "revert" in str(error.get("message", "")):
            error["message"] = f"Contract reverted: {error['message']}"
        return error

    custom_middleware = FormattingMiddlewareBuilder.build(
        error_formatters={
            "eth_call": custom_error_formatter,
        }
    )


Dynamic Formatters with Builders
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For formatters that need access to the ``Web3`` instance or need to be built
dynamically per-request, use the ``sync_formatters_builder`` and
``async_formatters_builder`` options:

.. code-block:: python

    from web3.middleware import FormattingMiddlewareBuilder

    def build_formatters(w3, method):
        """Build formatters dynamically based on method and w3 instance."""
        request_formatters = {}
        result_formatters = {}
        error_formatters = {}

        if method == "eth_getBalance":
            # Access w3 instance for dynamic behavior
            chain_id = w3.eth.chain_id
            if chain_id == 1:  # Mainnet
                result_formatters["eth_getBalance"] = lambda x: int(x, 16)

        return {
            "request_formatters": request_formatters,
            "result_formatters": result_formatters,
            "error_formatters": error_formatters,
        }

    # For async usage
    async def async_build_formatters(async_w3, method):
        """Async version of formatter builder."""
        chain_id = await async_w3.eth.chain_id
        # ... build formatters
        return {
            "request_formatters": {},
            "result_formatters": {},
            "error_formatters": {},
        }

    custom_middleware = FormattingMiddlewareBuilder.build(
        sync_formatters_builder=build_formatters,
        async_formatters_builder=async_build_formatters,
    )


Common Formatter Utilities
--------------------------

web3.py provides several utility functions for building formatters in
``web3._utils.formatters`` and ``eth_utils``:

.. code-block:: python

    from eth_utils import (
        to_checksum_address,
        to_hex,
        to_int,
    )
    from eth_utils.curried import (
        apply_formatter_at_index,
        apply_formatter_if,
        apply_formatter_to_array,
        apply_formatters_to_dict,
        apply_formatters_to_sequence,
    )
    from web3._utils.formatters import (
        apply_key_map,
        hex_to_integer,
        integer_to_hex,
    )

    # Apply formatter to specific index in params list
    formatter = apply_formatter_at_index(to_hex, 1)  # Format 2nd parameter

    # Apply formatter conditionally
    formatter = apply_formatter_if(
        lambda x: isinstance(x, int),  # condition
        to_hex  # formatter to apply if condition is True
    )

    # Apply formatters to each element of an array
    formatter = apply_formatter_to_array(to_checksum_address)

    # Apply different formatters to dict keys
    formatter = apply_formatters_to_dict({
        "gasPrice": to_hex,
        "value": to_hex,
        "from": to_checksum_address,
    })


Built-in Middleware Using Formatters
------------------------------------

Several built-in middleware use the formatting system:

PythonicMiddleware
~~~~~~~~~~~~~~~~~~

The ``PythonicMiddleware`` applies the default Pythonic formatters to convert
between Python types and JSON-RPC formats. This is included in the default
middleware stack.

.. code-block:: python

    from web3.middleware import PythonicMiddleware

    # This is equivalent to:
    PythonicMiddleware = FormattingMiddlewareBuilder.build(
        request_formatters=PYTHONIC_REQUEST_FORMATTERS,
        result_formatters=PYTHONIC_RESULT_FORMATTERS,
    )


ValidationMiddleware
~~~~~~~~~~~~~~~~~~~~

The ``ValidationMiddleware`` uses formatters to validate transaction parameters
like ``chainId`` before sending:

.. code-block:: python

    from web3.middleware import ValidationMiddleware

    # Included by default, validates transactions have correct chainId


EthereumTesterMiddleware
~~~~~~~~~~~~~~~~~~~~~~~~

The ``ethereum_tester_middleware`` uses formatters to transform data between
web3.py and the eth-tester backend:

.. code-block:: python

    from web3.providers.eth_tester.middleware import ethereum_tester_middleware


Best Practices
--------------

1. **Order Matters**: Request formatters are applied in order, and result formatters
   are applied in reverse order. Be mindful of the order when adding multiple
   formatting middleware.

2. **Don't Duplicate**: The default ``PythonicMiddleware`` handles most common
   transformations. Only add custom formatters for specific needs.

3. **Test Your Formatters**: Formatters can silently transform data incorrectly.
   Always test with real RPC calls.

4. **Use Type Hints**: When writing custom formatters, use type hints to catch
   errors early:

   .. code-block:: python

       from typing import Any

       def my_formatter(value: str) -> int:
           return int(value, 16)

5. **Handle Edge Cases**: Always handle ``None`` values and unexpected types:

   .. code-block:: python

       def safe_formatter(value):
           if value is None:
               return None
           return int(value, 16) if isinstance(value, str) else value


See Also
--------

- :ref:`middleware_internals` - How middleware works in web3.py
- :ref:`Modifying_Middleware` - How to add, remove, and configure middleware
- `JSON-RPC Specification <https://www.jsonrpc.org/specification>`_ - The underlying protocol
- `Ethereum JSON-RPC API <https://ethereum.org/en/developers/docs/apis/json-rpc/>`_ - Ethereum-specific methods
