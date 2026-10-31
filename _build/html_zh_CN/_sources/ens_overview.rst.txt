.. _ens_overview:

Ethereum Name Service (ENS)
===========================

The Ethereum Name Service (ENS) is analogous to the Domain Name Service. It
enables users and developers to use human-friendly names in place of error-prone
hexadecimal addresses, content hashes, and more.

The :mod:`ens` module is included with web3.py. It provides an interface to look up
domains and addresses, add resolver records, or get and set metadata.


Setup
-----

Create an :class:`~ens.ENS` object (named ``ns`` below) in one of three ways:

1. Automatic detection
2. Specify an instance of a :ref:`provider <providers>`
3. From an existing :class:`web3.Web3` object

.. code-block:: python

    # automatic detection
    from ens.auto import ns

    # or, with a provider
    from web3 import IPCProvider
    from ens import ENS

    provider = IPCProvider(...)
    ns = ENS(provider)

    # or, with a w3 instance
    # Note: This inherits the w3 middleware from the w3 instance and adds a stalecheck middleware to the middleware onion.
    # It also inherits the provider and codec from the w3 instance, as well as the ``strict_bytes_type_checking`` flag value.
    from ens import ENS
    w3 = Web3(...)
    ns = ENS.from_web3(w3)


Asynchronous support is available via the ``AsyncENS`` module:

.. code-block:: python

    from ens import AsyncENS

    ns = AsyncENS(provider)


Note that an ``ens`` module instance is also available on the ``w3`` instance.
The first time it's used, web3.py will create the  ``ens`` instance using
``ENS.from_web3(w3)`` or ``AsyncENS.from_web3(w3)`` as appropriate.

.. code-block:: python

    # instantiate w3 instance
    from web3 import Web3, IPCProvider
    w3 = Web3(IPCProvider(...))

    # use the module
    w3.ens.address('ethereum.eth')


.. py:attribute:: ens.strict_bytes_type_checking

    The ``ENS`` instance has a ``strict_bytes_type_checking`` flag that toggles the flag
    with the same name on the ``Web3`` instance attached to the ``ENS`` instance.
    You may disable the stricter bytes type checking that is loaded by default using
    this flag. For more examples, see :ref:`disable-strict-byte-check`

    If instantiating a standalone ENS instance using ``ENS.from_web3()``, the ENS
    instance will inherit the value of the flag on the Web3 instance at time of
    instantiation.

    .. doctest::

        >>> from web3 import Web3, EthereumTesterProvider
        >>> from ens import ENS
        >>> w3 = Web3(EthereumTesterProvider())

        >>> assert w3.strict_bytes_type_checking  # assert strict by default
        >>> w3.is_encodable('bytes2', b'1')
        False

        >>> w3.strict_bytes_type_checking = False
        >>> w3.is_encodable('bytes2', b'1')  # zero-padded, so encoded to: b'1\x00'
        True

        >>> ns = ENS.from_web3(w3)
        >>> # assert inherited from w3 at time of instantiation via ENS.from_web3()
        >>> assert ns.strict_bytes_type_checking is False
        >>> ns.w3.is_encodable('bytes2', b'1')
        True

        >>> # assert these are now separate instances
        >>> ns.strict_bytes_type_checking = True
        >>> ns.w3.is_encodable('bytes2', b'1')
        False

        >>> # assert w3 flag value remains
        >>> assert w3.strict_bytes_type_checking is False
        >>> w3.is_encodable('bytes2', b'1')
        True

    However, if accessing the ``ENS`` class via the ``Web3`` instance as a module
    (``w3.ens``), since all modules use the same ``Web3`` object reference
    under the hood (the parent ``w3`` object), changing the
    ``strict_bytes_type_checking`` flag value on ``w3`` also changes the flag state
    for ``w3.ens.w3`` and all modules.

    .. doctest::

        >>> from web3 import Web3, EthereumTesterProvider
        >>> w3 = Web3(EthereumTesterProvider())

        >>> assert w3.strict_bytes_type_checking  # assert strict by default
        >>> w3.is_encodable('bytes2', b'1')
        False

        >>> w3.strict_bytes_type_checking = False
        >>> w3.is_encodable('bytes2', b'1')  # zero-padded, so encoded to: b'1\x00'
        True

        >>> assert w3 == w3.ens.w3  # assert same object
        >>> assert not w3.ens.w3.strict_bytes_type_checking
        >>> w3.ens.w3.is_encodable('bytes2', b'1')
        True

        >>> # sanity check on eth module as well
        >>> assert not w3.eth.w3.strict_bytes_type_checking
        >>> w3.eth.w3.is_encodable('bytes2', b'1')
        True


Usage
-----

Name Info
~~~~~~~~~

.. _ens_get_address:

Get the Address for an ENS Name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from ens.auto import ns
    eth_address = ns.address('ens.eth')
    assert eth_address == '0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7'

The ``ENS`` module has no opinion as to which **TLD (Top Level Domain)** you can use,
but will not infer a TLD if it is not provided with the name.

Multichain Address Resolution
+++++++++++++++++++++++++++++

`ENSIP-9 <https://docs.ens.domains/ensip/9>`_
introduced multichain address resolution, allowing users to resolve addresses from
different chains, specified by the coin type index from
`SLIP44 <https://github.com/satoshilabs/slips/blob/master/slip-0044.md>`_. The
``address()`` method on the ``ENS`` class supports multichain address resolution via
the ``coin_type`` keyword argument.

.. code-block:: python

    from ens.auto import ns
    eth_address = ns.address('ens.eth', coin_type=60)  # ETH is coin_type 60
    assert eth_address == '0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7'


Get the ENS Name for an Address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    domain = ns.name('0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7')

    # name() also accepts the bytes version of the address
    assert ns.name(b'\xfe\x89\xccz\xbb,A\x83h:\xb7\x16S\xc4\xcd\xc9\xb0-D\xb7') == domain

    # confirm that the name resolves back to the address that you looked up:
    assert ns.address(domain) == '0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7'

.. note:: For accuracy, and as a recommendation from the ENS documentation on
    `reverse resolution <https://docs.ens.domains/web/resolution#reverse-resolution>`_,
    the ``ENS`` module now verifies that the forward resolution matches the address with every call to get the
    ``name()`` for an address. This is the only sure way to know whether the reverse resolution is correct. Anyone can
    claim any name, only forward resolution implies that the owner of the name gave their stamp of approval.

Get the Owner of a Name
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    eth_address = ns.owner('exchange.eth')

....

Set Up Your Name and Address
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Link a Name to an Address
^^^^^^^^^^^^^^^^^^^^^^^^^

You can set up your name so that :meth:`~ens.ENS.address` will show the address it points to. In order to do so,
you must already be the owner of the domain (or its parent).

.. code-block:: python

    ns.setup_address('ens.eth', '0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7')

In the common case where you want to point the name to the owning address, you can skip the address.

.. code-block:: python

    ns.setup_address('ens.eth')

You can claim arbitrarily deep subdomains.

.. code-block:: python

    ns.setup_address('supreme.executive.power.derives.from.a.mandate.from.the.masses.ens.eth')

    # wait for the transaction to be mined, then:
    assert (
        ns.address('supreme.executive.power.derives.from.a.mandate.from.the.masses.ens.eth')
        == '0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7'
    )

.. warning:: Gas costs scale up with the number of subdomains!

Multichain Address Support
++++++++++++++++++++++++++

`ENSIP-9 <https://docs.ens.domains/ensip/9>`_
introduced multichain address resolution, allowing users to resolve addresses from
different chains, specified by the coin type index from
`SLIP44 <https://github.com/satoshilabs/slips/blob/master/slip-0044.md>`_. The
``setup_address()`` method on the ``ENS`` class supports multichain address setup
via the ``coin_type`` keyword argument.

.. code-block:: python

    from ens.auto import ns
    ns.setup_address('ens.eth', coin_type=60)  # ETH is coin_type 60
    assert ns.address('ens.eth', coin_type=60) == '0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7'

Link an Address to a Name
^^^^^^^^^^^^^^^^^^^^^^^^^

You can set up your address so that :meth:`~ens.ENS.name` will show the name that points to it.

This is like Caller ID. It enables you and others to take an account and determine what name points to it. Sometimes
this is referred to as "reverse" resolution. The ENS Reverse Resolver is used for this functionality.

.. code-block:: python

    ns.setup_name('ens.eth', '0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7')

If you don't supply the address, :meth:`~ens.ENS.setup_name` will assume you want the
address returned by :meth:`~ens.ENS.address`.

.. code-block:: python

    ns.setup_name('ens.eth')

If the name doesn't already point to an address, :meth:`~ens.ENS.setup_name` will
call :meth:`~ens.ENS.setup_address` for you.

Wait for the transaction to be mined, then:

.. code-block:: python

    assert ns.name('0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7') == 'ens.eth'

....

Text Records
~~~~~~~~~~~~

Set Text Metadata for an ENS Record
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As the owner of an ENS record, you can add text metadata.
A list of supported fields can be found in the
`ENS documentation <https://docs.ens.domains/resolvers/public#get-text-data>`_.
You'll need to setup the address first, and then the text can be set:

.. code-block:: python

    ns.setup_address('ens.eth', '0xFe89cc7aBB2C4183683ab71653C4cdc9B02D44b7')
    ns.set_text('ens.eth', 'url', 'https://example.com')

A transaction dictionary can be passed as the last argument if desired:

.. code-block:: python

    transaction_dict = {'from': '0x123...'}
    ns.set_text('ens.eth', 'url', 'https://example.com', transaction_dict)

If the transaction dictionary is not passed, sensible defaults will be used, and if
a transaction dictionary is passed but does not have a ``from`` value,
the default will be the ``owner``.

Read Text Metadata for an ENS Record
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Anyone can read the data from an ENS Record:

.. code-block:: python

    url = ns.get_text('ens.eth', 'url')
    assert url == 'https://example.com'

....

Working With Resolvers
~~~~~~~~~~~~~~~~~~~~~~

Get the Resolver for an ENS Record
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can get the resolver for an ENS name via the :meth:`~ens.ENS.resolver` method.

.. code-block:: python

    >>> resolver = ns.resolver('ens.eth')
    >>> resolver.address
    '0x5B2063246F2191f18F2675ceDB8b28102e957458'

....

Wildcard Resolution Support
---------------------------

The ``ENS`` module supports Wildcard Resolution for resolvers that implement the ``ExtendedResolver`` interface
as described in `ENSIP-10 <https://docs.ens.domains/ensip/10>`_.
Resolvers that implement the extended resolver interface should return ``True`` when calling the
``supportsInterface()`` function with the extended resolver interface id ``"0x9061b923"`` and should resolve subdomains
to a unique address.
