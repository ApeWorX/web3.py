.. _exceptions:

Exceptions
==========

Public exceptions defined in ``web3.exceptions`` inherit from
``Web3Exception``. This makes it possible to catch errors raised by the core
web3.py API separately from exceptions raised by application code or other
libraries.

Catch the most specific exception that your application can handle, and use
``Web3Exception`` when the same recovery applies to any web3.py error:

.. code-block:: python

    from web3.exceptions import (
        TransactionNotFound,
        Web3Exception,
        Web3RPCError,
    )

    try:
        receipt = w3.eth.get_transaction_receipt(transaction_hash)
    except TransactionNotFound:
        # The transaction is not available yet.
        receipt = None
    except Web3RPCError as exc:
        # The node returned another JSON-RPC error.
        logger.warning(exc.user_message)
    except Web3Exception:
        # A non-RPC web3.py error occurred.
        raise

``Web3Exception`` only covers exceptions defined in ``web3.exceptions``.
Exceptions from third-party libraries or user callbacks are not necessarily
wrapped by web3.py. The ENS API has a separate base exception,
:class:`~ens.exceptions.ENSException`.


Exception hierarchy
-------------------

The hierarchy groups exceptions by the operation that failed. Some commonly
used branches are:

* ``Web3RPCError`` for failures associated with JSON-RPC responses. More
  specific subclasses include ``MethodUnavailable``, ``RequestTimedOut``,
  ``TransactionNotFound``, ``TransactionIndexingInProgress``, and
  ``BlockNotFound``.
* ``Web3ValidationError`` for invalid values detected by web3.py.
  ``ExtraDataLengthError`` is a more specific validation error.
* ``MismatchedABI`` for an ABI that does not match the requested function,
  event, or supplied arguments. Its subclasses include
  ``ABIFunctionNotFound`` and ``ABIEventNotFound``.
* ``ContractLogicError`` for contract reverts, with ``ContractCustomError``,
  ``ContractPanicError``, and ``OffchainLookup`` providing more detail when the
  revert data can be identified.
* ``InvalidTransaction`` for an invalid combination of transaction arguments.
* ``ProviderConnectionError``, ``BadResponseFormat``, and
  ``PersistentConnectionError`` for provider and response handling failures.

web3.py also provides exceptions compatible with common built-in exception
types: ``Web3AssertionError``, ``Web3ValueError``, ``Web3AttributeError``, and
``Web3TypeError``. Each can be caught through either ``Web3Exception`` or its
corresponding built-in exception type.


JSON-RPC errors
---------------

When a valid JSON-RPC response contains an ``error`` object, web3.py first
applies any error formatter registered for that method. A formatter may raise
another ``Web3Exception`` branch; for example, a contract revert from
``eth_call`` raises ``ContractLogicError``. If no formatter raises an exception,
the general validation path raises ``Web3RPCError`` or a recognized subclass.
For example, JSON-RPC error code ``-32601`` raises ``MethodUnavailable``, while
known timeout messages raise ``RequestTimedOut``.

JSON-RPC does not standardize an error code for every failure. Client
implementations can also use different messages for the same condition. Some
specialized exceptions therefore depend on matching error messages returned by
the node. If a client changes its message, web3.py may raise the general
``Web3RPCError`` instead of a more specific subclass. Applications that need to
handle both cases should catch the specific exception first and then
``Web3RPCError``.

``Web3RPCError`` exposes two useful attributes:

``rpc_response``
    The complete JSON-RPC response, when available.

``user_message``
    A concise explanation intended for application-level error reporting. It
    defaults to a general RPC error message when no specific ``user_message``
    is provided.
