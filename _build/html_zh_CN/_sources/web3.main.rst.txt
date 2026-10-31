.. _web3_base:

Web3 API
========

.. contents:: :local:

.. py:module:: web3
.. py:currentmodule:: web3


.. py:class:: Web3(provider)

Each ``Web3`` instance exposes the following APIs.

Providers
~~~~~~~~~

.. py:attribute:: Web3.HTTPProvider

    Convenience API to access :py:class:`web3.providers.rpc.HTTPProvider`

.. py:attribute:: Web3.IPCProvider

    Convenience API to access :py:class:`web3.providers.ipc.IPCProvider`


Attributes
~~~~~~~~~~

.. py:attribute:: Web3.api

    Returns the current Web3 version.

    .. code-block:: python

       >>> web3.api
       "4.7.0"

.. py:attribute:: Web3.client_version

    * Delegates to ``web3_clientVersion`` RPC Method

    Returns the current client version.

    .. code-block:: python

       >>> web3.client_version
       'Geth/v1.4.11-stable-fed692f6/darwin/go1.7'


.. _batch_requests:

Batch Requests
~~~~~~~~~~~~~~

.. py:method:: Web3.batch_requests()

    The JSON-RPC API allows for batch requests, meaning you can send a single request
    that contains an array of request objects. Generally, this may be useful when you want
    to limit the number of requests you send to a node.

    You can choose to build a batch of requests within or outside of a context manager:

    .. code-block:: python

        with w3.batch_requests() as batch:
            batch.add(w3.eth.get_block(6))
            batch.add(w3.eth.get_block(4))
            batch.add(w3.eth.get_block(2))

            responses = batch.execute()
            assert len(responses) == 3

    .. note::

       Within the batching context above, calls are suspended until
       ``batch.execute()`` is called. Calling a method without
       passing it to ``batch.add`` might result in unexpected behavior.

    Using the batch object directly:

    .. code-block:: python

        batch = w3.batch_requests()
        batch.add(w3.eth.get_block(1))
        batch.add(w3.eth.get_block(2))
        responses = batch.execute()
        assert len(responses) == 2

    Contract interactions can be included in batch requests by omitting the ``call()`` method:

    .. code-block:: python

        batch.add(math_contract.functions.multiply7(0))

    Additionally, if you need to make multiple calls of the same function, you can add
    a mapping of the function to its arguments:

    .. code-block:: python

        batch = w3.batch_requests()
        batch.add_mapping(
            {
                math_contract.functions.multiply7: [1, 2],
                w3.eth.get_block: [3, 4],
            }
        )
        responses = batch.execute()
        assert len(responses) == 4

    The ``execute`` method returns a list of responses in the order they were included in
    the batch.

    If you need to abandon or rebuild a batch request, utilize the ``clear`` method:

    .. code-block:: python

        batch = w3.batch_requests()
        batch.add(w3.eth.get_block(1))
        batch.add(w3.eth.get_block(2))
        assert len(batch._requests_info) == 2

        batch.clear()
        assert batch._requests_info == []

    .. note::

        Only read-only operations that exist within modules on the ``Web3`` class
        (e.g. ``w3.eth``, ``w3.net``) are supported by ``batch_requests``.
        Unsupported methods include:

        - :meth:`subscribe <web3.eth.Eth.subscribe>`
        - :meth:`unsubscribe <web3.eth.Eth.unsubscribe>`
        - :meth:`send_raw_transaction <web3.eth.Eth.send_raw_transaction>`
        - :meth:`send_transaction <web3.eth.Eth.send_transaction>`
        - :meth:`sign_transaction <web3.eth.Eth.sign_transaction>`
        - :meth:`sign <web3.eth.Eth.sign>`
        - :meth:`sign_typed_data <web3.eth.Eth.sign_typed_data>`
        - ``w3.provider.make_request()``.

  Async Batch Requests
  ````````````````````

  If using one of the asynchronous providers, you'll need to make use of
  the ``async_execute`` method and the ``async`` and ``await`` keywords as appropriate.

  .. note::

    If performance is a concern, consider using ``asyncio.gather()`` with single
    concurrent requests instead of an asynchronous batch request. It will generally be
    the faster option due to the overhead of batching.

  .. code-block:: python

      # context manager:
      async with w3.batch_requests() as batch:
          batch.add(w3.eth.get_block(6))
          batch.add(w3.eth.get_block(4))
          batch.add(w3.eth.get_block(2))

          responses = await batch.async_execute()
          assert len(responses) == 3

      # object:
      batch = w3.batch_requests()
      batch.add(w3.eth.get_block(1))
      batch.add(w3.eth.get_block(2))
      responses = await batch.async_execute()
      assert len(responses) == 2


.. _overview_type_conversions:

Encoding and Decoding Helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Web3.to_hex(primitive=None, hexstr=None, text=None)

    Takes a variety of inputs and returns it in its hexadecimal representation.
    It follows the rules for converting to hex in the
    `JSON-RPC spec`_

    .. code-block:: python

        >>> Web3.to_hex(0)
        '0x0'
        >>> Web3.to_hex(1)
        '0x1'
        >>> Web3.to_hex(0x0)
        '0x0'
        >>> Web3.to_hex(0x000F)
        '0xf'
        >>> Web3.to_hex(b'')
        '0x'
        >>> Web3.to_hex(b'\x00\x0F')
        '0x000f'
        >>> Web3.to_hex(False)
        '0x0'
        >>> Web3.to_hex(True)
        '0x1'
        >>> Web3.to_hex(hexstr='0x000F')
        '0x000f'
        >>> Web3.to_hex(hexstr='000F')
        '0x000f'
        >>> Web3.to_hex(text='')
        '0x'
        >>> Web3.to_hex(text='cowmö')
        '0x636f776dc3b6'

.. _JSON-RPC spec: https://github.com/ethereum/wiki/wiki/JSON-RPC#hex-value-encoding

.. py:method:: Web3.to_text(primitive=None, hexstr=None, text=None)

    Takes a variety of inputs and returns its string equivalent.
    Text gets decoded as UTF-8.


    .. code-block:: python

        >>> Web3.to_text(0x636f776dc3b6)
        'cowmö'
        >>> Web3.to_text(b'cowm\xc3\xb6')
        'cowmö'
        >>> Web3.to_text(hexstr='0x636f776dc3b6')
        'cowmö'
        >>> Web3.to_text(hexstr='636f776dc3b6')
        'cowmö'
        >>> Web3.to_text(text='cowmö')
        'cowmö'


.. py:method:: Web3.to_bytes(primitive=None, hexstr=None, text=None)

    Takes a variety of inputs and returns its bytes equivalent.
    Text gets encoded as UTF-8.


    .. code-block:: python

        >>> Web3.to_bytes(0)
        b'\x00'
        >>> Web3.to_bytes(0x000F)
        b'\x0f'
        >>> Web3.to_bytes(b'')
        b''
        >>> Web3.to_bytes(b'\x00\x0F')
        b'\x00\x0f'
        >>> Web3.to_bytes(False)
        b'\x00'
        >>> Web3.to_bytes(True)
        b'\x01'
        >>> Web3.to_bytes(hexstr='0x000F')
        b'\x00\x0f'
        >>> Web3.to_bytes(hexstr='000F')
        b'\x00\x0f'
        >>> Web3.to_bytes(text='')
        b''
        >>> Web3.to_bytes(text='cowmö')
        b'cowm\xc3\xb6'


.. py:method:: Web3.to_int(primitive=None, hexstr=None, text=None)

    Takes a variety of inputs and returns its integer equivalent.


    .. code-block:: python

        >>> Web3.to_int(0)
        0
        >>> Web3.to_int(0x000F)
        15
        >>> Web3.to_int(b'\x00\x0F')
        15
        >>> Web3.to_int(False)
        0
        >>> Web3.to_int(True)
        1
        >>> Web3.to_int(hexstr='0x000F')
        15
        >>> Web3.to_int(hexstr='000F')
        15

.. py:method:: Web3.to_json(obj)

    Takes a variety of inputs and returns its JSON equivalent.


    .. code-block:: python

        >>> Web3.to_json(3)
        '3'
        >>> Web3.to_json({'one': 1})
        '{"one": 1}'


.. _overview_currency_conversions:

Currency Conversions
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Web3.to_wei(value, currency)

    Returns the value in the denomination specified by the ``currency`` argument
    converted to wei.


    .. code-block:: python

        >>> Web3.to_wei(1, 'ether')
        1000000000000000000


.. py:method:: Web3.from_wei(value, currency)

    Returns the value in wei converted to the given currency. The value is returned
    as a ``Decimal`` to ensure precision down to the wei.


    .. code-block:: python

        >>> Web3.from_wei(1000000000000000000, 'ether')
        Decimal('1')


.. _overview_addresses:

Addresses
~~~~~~~~~

.. py:method:: Web3.is_address(value)

    Returns ``True`` if the value is one of the recognized address formats.

    * Allows for both ``0x`` prefixed and non-prefixed values.
    * If the address contains mixed upper and lower cased characters this function also
      checks if the address checksum is valid according to `EIP55`_

    .. code-block:: python

        >>> Web3.is_address('0xd3CdA913deB6f67967B99D67aCDFa1712C293601')
        True


.. py:method:: Web3.is_checksum_address(value)

    Returns ``True`` if the value is a valid `EIP55`_ checksummed address


    .. code-block:: python

        >>> Web3.is_checksum_address('0xd3CdA913deB6f67967B99D67aCDFa1712C293601')
        True
        >>> Web3.is_checksum_address('0xd3cda913deb6f67967b99d67acdfa1712c293601')
        False


.. py:method:: Web3.to_checksum_address(value)

    Returns the given address with an `EIP55`_ checksum.


    .. code-block:: python

        >>> Web3.to_checksum_address('0xd3cda913deb6f67967b99d67acdfa1712c293601')
        '0xd3CdA913deB6f67967B99D67aCDFa1712C293601'

.. _EIP55: https://github.com/ethereum/EIPs/issues/55


.. _overview_hashing:

Cryptographic Hashing
~~~~~~~~~~~~~~~~~~~~~

.. py:classmethod:: Web3.keccak(primitive=None, hexstr=None, text=None)

    Returns the Keccak-256 of the given value. Text is encoded to UTF-8 before
    computing the hash, just like Solidity. Any of the following are
    valid and equivalent:

    .. code-block:: python

        >>> Web3.keccak(0x747874)
        >>> Web3.keccak(b'\x74\x78\x74')
        >>> Web3.keccak(hexstr='0x747874')
        >>> Web3.keccak(hexstr='747874')
        >>> Web3.keccak(text='txt')
        HexBytes('0xd7278090a36507640ea6b7a0034b69b0d240766fa3f98e3722be93c613b29d2e')

.. py:classmethod:: Web3.solidity_keccak(abi_types, value)

    Returns the Keccak-256 as it would be computed by the solidity ``keccak``
    function on a *packed* ABI encoding of the ``value`` list contents.  The ``abi_types``
    argument should be a list of solidity type strings which correspond to each
    of the provided values.


    .. code-block:: python

        >>> Web3.solidity_keccak(['bool'], [True])
        HexBytes("0x5fe7f977e71dba2ea1a68e21057beebb9be2ac30c6410aa38d4f3fbe41dcffd2")

        >>> Web3.solidity_keccak(['uint8', 'uint8', 'uint8'], [97, 98, 99])
        HexBytes("0x4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45")

        >>> Web3.solidity_keccak(['uint8[]'], [[97, 98, 99]])
        HexBytes("0x233002c671295529bcc50b76a2ef2b0de2dac2d93945fca745255de1a9e4017e")

        >>> Web3.solidity_keccak(['address'], ["0x49EdDD3769c0712032808D86597B84ac5c2F5614"])
        HexBytes("0x2ff37b5607484cd4eecf6d13292e22bd6e5401eaffcc07e279583bc742c68882")

        >>> Web3.solidity_keccak(['address'], ["ethereumfoundation.eth"])
        HexBytes("0x913c99ea930c78868f1535d34cd705ab85929b2eaaf70fcd09677ecd6e5d75e9")


    Comparable solidity usage:

    .. code-block:: solidity

        bytes32 data1 = keccak256(abi.encodePacked(true));
        assert(data1 == hex"5fe7f977e71dba2ea1a68e21057beebb9be2ac30c6410aa38d4f3fbe41dcffd2");
        bytes32 data2 = keccak256(abi.encodePacked(uint8(97), uint8(98), uint8(99)));
        assert(data2 == hex"4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45");


Check Encodability
~~~~~~~~~~~~~~~~~~~~

.. py:method:: w3.is_encodable(_type, value)

  Returns ``True`` if a value can be encoded as the given type. Otherwise returns ``False``.

   .. code-block:: python

        >>> from web3.auto.gethdev import w3
        >>> w3.is_encodable('bytes2', b'12')
        True
        >>> w3.is_encodable('bytes2', '0x1234')
        True
        >>> w3.is_encodable('bytes2', '1234')  # not 0x-prefixed, no assumptions will be made
        False
        >>> w3.is_encodable('bytes2', b'1')  # does not match specified bytes size
        False
        >>> w3.is_encodable('bytes2', b'123')  # does not match specified bytes size
        False

.. py:attribute:: w3.strict_bytes_type_checking

    Disable the stricter bytes type checking that is loaded by default. For more
    examples, see :ref:`disable-strict-byte-check`

    .. doctest::

        >>> from web3.auto.gethdev import w3

        >>> w3.is_encodable('bytes2', b'12')
        True

        >>>  # not of exact size bytes2
        >>> w3.is_encodable('bytes2', b'1')
        False

        >>> w3.strict_bytes_type_checking = False

        >>> # zero-padded, so encoded to: b'1\x00'
        >>> w3.is_encodable('bytes2', b'1')
        True

        >>> # re-enable it
        >>> w3.strict_bytes_type_checking = True
        >>> w3.is_encodable('bytes2', b'1')
        False


RPC API Modules
~~~~~~~~~~~~~~~

Each ``Web3`` instance also exposes these namespaced API modules.


.. py:attribute:: Web3.eth

    See :doc:`./web3.eth`

.. py:attribute:: Web3.geth

    See :doc:`./web3.geth`


These internal modules inherit from the ``web3.module.Module`` class which give them some configurations internal to the
web3.py library.


Custom Methods
~~~~~~~~~~~~~~

You may add or overwrite methods within any module using the ``attach_methods`` function.
To create a property instead, set ``is_property`` to ``True``.

.. code-block:: python

   >>> w3.eth.attach_methods({
   ...    'example_method': Method(
   ...      'eth_example',
   ...       mungers=[...],
   ...       request_formatters=[...],
   ...       result_formatters=[...],
   ...       is_property=False,
   ...    ),
   ... })
   >>> w3.eth.example_method()


External Modules
~~~~~~~~~~~~~~~~

External modules can be used to introduce custom or third-party APIs to your ``Web3`` instance. External modules are simply
classes whose methods and properties can be made available within the ``Web3`` instance. Optionally, the external module may
make use of the parent ``Web3`` instance by accepting it as the first argument within the ``__init__`` function:

.. code-block:: python

    >>> class ExampleModule:
    ...     def __init__(self, w3):
    ...         self.w3 = w3
    ...
    ...     def print_balance_of_shaq(self):
    ...         print(self.w3.eth.get_balance('shaq.eth'))


.. warning:: Given the flexibility of external modules, use caution and only import modules from trusted third parties
   and open source code you've vetted!

Configuring external modules can occur either at instantiation of the ``Web3`` instance or by making use of the
``attach_modules()`` method. To instantiate the ``Web3`` instance with external modules use the ``external_modules``
keyword argument:

.. code-block:: python

    >>> from web3 import Web3, HTTPProvider
    >>> from external_module_library import (
    ...     ModuleClass1,
    ...     ModuleClass2,
    ...     ModuleClass3,
    ...     ModuleClass4,
    ...     ModuleClass5,
    ... )
    >>> w3 = Web3(
    ...     HTTPProvider(provider_uri),
    ...     external_modules={
    ...         'module1': ModuleClass1,
    ...         'module2': (ModuleClass2, {
    ...             'submodule1': ModuleClass3,
    ...             'submodule2': (ModuleClass4, {
    ...                 'submodule2a': ModuleClass5,  # submodule children may be nested further if necessary
    ...             })
    ...         })
    ...     }
    ... )

    # `return_zero`, in this case, is an example attribute of the `ModuleClass1` object
    >>> w3.module1.return_zero()
    0
    >>> w3.module2.submodule1.return_one()
    1
    >>> w3.module2.submodule2.submodule2a.return_two()
    2


.. py:method:: w3.attach_modules(modules)

    The ``attach_modules()`` method can be used to attach external modules after the ``Web3`` instance has been
    instantiated.

    Modules are attached via a `dict` with module names as the keys. The values can either be the module classes
    themselves, if there are no submodules, or two-item tuples with the module class as the 0th index and a similarly
    built `dict` containing the submodule information as the 1st index. This pattern may be repeated as necessary.

    .. code-block:: python

        >>> from web3 import Web3, HTTPProvider
        >>> from external_module_library import (
        ...     ModuleClass1,
        ...     ModuleClass2,
        ...     ModuleClass3,
        ...     ModuleClass4,
        ...     ModuleClass5,
        ... )
        >>> w3 = Web3(HTTPProvider(provider_uri))

        >>> w3.attach_modules({
        ...     'module1': ModuleClass1,  # the module class itself may be used for a single module with no submodules
        ...     'module2': (ModuleClass2, {  # a tuple with module class and corresponding submodule dict may be used for modules with submodules
        ...         'submodule1': ModuleClass3,
        ...         'submodule2': (ModuleClass4, {  # this pattern may be repeated as necessary
        ...             'submodule2a': ModuleClass5,
        ...         })
        ...     })
        ... })
        >>> w3.module1.return_zero()
        0
        >>> w3.module2.submodule1.return_one()
        1
        >>> w3.module2.submodule2.submodule2a.return_two()
        2
