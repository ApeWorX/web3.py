.. _web3-eth:

web3.eth API
============

.. py:module:: web3.eth

.. py:class:: Eth

The ``web3.eth`` object exposes the following properties and methods to
interact with the RPC APIs under the ``eth_`` namespace.

By default, when a property or method returns a mapping of keys to values, it
will return an ``AttributeDict`` which acts like a ``dict`` but you can
access the keys as attributes and cannot modify its fields. For example,
you can find the latest block number in these two ways:

    .. code-block:: python

        >>> block = web3.eth.get_block('latest')
        AttributeDict({
          'hash': '0xe8ad537a261e6fff80d551d8d087ee0f2202da9b09b64d172a5f45e818eb472a',
          'number': 4022281,
          # ... etc ...
        })

        >>> block['number']
        4022281
        >>> block.number
        4022281

        >>> block.number = 4022282
        Traceback # ... etc ...
        TypeError: This data is immutable -- create a copy instead of modifying

This feature is available via the ``AttributeDictMiddleware`` which is a default
middleware.

.. note::
    Accessing an ``AttributeDict`` property via attribute will break type hinting. If
    typing is crucial for your application, accessing via key / value, as well as
    removing the ``AttributeDictMiddleware`` altogether, may be desired.


Properties
----------

The following properties are available on the ``web3.eth`` namespace.


.. py:attribute:: Eth.default_account

    The ethereum address that will be used as the default ``from`` address for
    all transactions. Defaults to empty.


.. py:attribute:: Eth.default_block

    The default block number that will be used for any RPC methods that accept
    a block identifier. Defaults to ``'latest'``.


.. py:attribute:: Eth.syncing

    * Delegates to ``eth_syncing`` RPC Method

    Returns either ``False`` if the node is not syncing or a dictionary
    showing sync status.

    .. code-block:: python

        >>> web3.eth.syncing
        AttributeDict({
            'currentBlock': 2177557,
            'highestBlock': 2211611,
            'knownStates': 0,
            'pulledStates': 0,
            'startingBlock': 2177365,
        })


.. py:attribute:: Eth.max_priority_fee

    * Delegates to ``eth_maxPriorityFeePerGas`` RPC Method

    Returns a suggestion for a max priority fee for dynamic fee transactions in Wei.

    .. code-block:: python

        >>> web3.eth.max_priority_fee
        2000000000


.. py:attribute:: Eth.gas_price

    * Delegates to ``eth_gasPrice`` RPC Method

    Returns the current gas price in Wei.

    .. code-block:: python

        >>> web3.eth.gas_price
        20000000000


.. py:attribute:: Eth.accounts

    * Delegates to ``eth_accounts`` RPC Method

    Returns the list of known accounts.

    .. code-block:: python

        >>> web3.eth.accounts
        ['0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD']


.. py:attribute:: Eth.block_number

    * Delegates to ``eth_blockNumber`` RPC Method

    Returns the number of the most recent block

    Alias for :meth:`~web3.eth.Eth.get_block_number`

    .. code-block:: python

        >>> web3.eth.block_number
        2206939


.. py:attribute:: Eth.chain_id

    * Delegates to ``eth_chainId`` RPC Method

    Returns an integer value for the currently configured "Chain Id" value introduced in `EIP-155 <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md>`_. Returns ``None`` if no Chain Id is available.

    .. code-block:: python

       >>> web3.eth.chain_id
       61

   .. note::

      This property gets called frequently in validation middleware, but `eth_chainId`
      is an allowed method for caching by default. Simply turn on request caching to
      avoid repeated calls to this method.

       .. code-block:: python

          >>> w3.provider.cache_allowed_requests = True


.. _web3-eth-methods:

Methods
-------

The following methods are available on the ``web3.eth`` namespace.


.. py:method:: Eth.get_balance(account, block_identifier=eth.default_block)

    * Delegates to ``eth_getBalance`` RPC Method

    Returns the balance of the given ``account`` at the block specified by
    ``block_identifier``.

    ``account`` may be a checksum address or an ENS name

    .. code-block:: python

        >>> web3.eth.get_balance('0xd3CdA913deB6f67967B99D67aCDFa1712C293601')
        77320681768999138915


.. py:method:: Eth.get_block_number()

    * Delegates to ``eth_blockNumber`` RPC Method

    Returns the number of the most recent block.

    .. code-block:: python

        >>> web3.eth.get_block_number()
        2206939


.. py:method:: Eth.get_storage_at(account, position, block_identifier=eth.default_block)

    * Delegates to ``eth_getStorageAt`` RPC Method

    Returns the value from a storage position for the given ``account`` at the
    block specified by ``block_identifier``.

    ``account`` may be a checksum address or an ENS name

    .. code-block:: python

        >>> web3.eth.get_storage_at('0x6C8f2A135f6ed072DE4503Bd7C4999a1a17F824B', 0)
        '0x00000000000000000000000000000000000000000000000000120a0b063499d4'

.. py:method:: Eth.blob_base_fee

    Fetches the expected base fee for blobs in the next block.

    * Delegates to ``eth_blobBaseFee`` RPC Method

    Returns the expected base fee in Wei.

    .. code-block:: python

        >>> web3.eth.blob_base_fee()
        537070730


.. py:method:: Eth.get_proof(account, positions, block_identifier=eth.default_block)

    * Delegates to ``eth_getProof`` RPC Method

    Returns the values from an array of storage positions for the given ``account`` at the
    block specified by ``block_identifier``.

    ``account`` may be a checksum address or an ENS name

    .. code-block:: python

        >>> web3.eth.get_proof('0x6C8f2A135f6ed072DE4503Bd7C4999a1a17F824B', [0], 3391)
        AttributeDict({
            'address': '0x4CB06C43fcdABeA22541fcF1F856A6a296448B6c',
            'accountProof': ['0xf90211a03841a7ddd65c70c94b8efa79190d00f0ab134b26f18dcad508f60a7e74559d0ba0464b07429a05039e22931492d6c6251a860c018ea390045d596b1ac11b5c7aa7a011f4b89823a03c9c4b5a8ab079ee1bc0e2a83a508bb7a5dc7d7fb4f2e95d3186a0b5f7c51c3b2d51d97f171d2b38a4df1a7c0acc5eb0de46beeff4d07f5ed20e19a0b591a2ce02367eda31cf2d16eca7c27fd44dbf0864b64ea8259ad36696eb2a04a02b646a7552b8392ae94263757f699a27d6e9176b4c06b9fc0a722f893b964795a02df05d68bceb88eebf68aafde61d10ab942097afc1c58b8435ffd3895358a742a0c2f16143c4d1db03276c433696dddb3e9f3b113bcd854b127962262e98f43147a0828820316cc02bfefd899aba41340659fd06df1e0a0796287ec2a4110239f6d2a050496598670b04df7bbff3718887fa36437d6d8c7afb4eff86f76c5c7097dcc4a0c14e9060c6b3784e35b9e6ae2ad2984142a75910ccc89eb89dc1e2f44b6c58c2a009804db571d0ce07913e1cbacc4f1dc4fb8265c936f5c612e3a47e91c64d8e9fa063d96f38b3cb51b1665c6641e25ffe24803f2941e5df79942f6a53b7169647e4a0899f71abb18c6c956118bf567fac629b75f7e9526873e429d3d8abb6dbb58021a00fd717235298742623c0b3cafb3e4bd86c0b5ab1f71097b4dd19f3d6925d758da0096437146c16097f2ccc1d3e910d65a4132803baee2249e72c8bf0bcaaeb37e580',
                             '0xf90151a097b17a89fd2c03ee98cb6459c08f51b269da5cee46650e84470f62bf83b43efe80a03b269d284a4c3cf8f8deacafb637c6d77f607eec8d75e8548d778e629612310480a01403217a7f1416830c870087c524dabade3985271f6f369a12b010883c71927aa0f592ac54c879817389663be677166f5022943e2fe1b52617a1d15c2f353f27dda0ac8d015a9e668f5877fcc391fae33981c00577096f0455b42df4f8e8089ece24a003ba34a13e2f2fb4bf7096540b42d4955c5269875b9cf0f7b87632585d44c9a580a0b179e3230b07db294473ae57f0170262798f8c551c755b5665ace1215cee10ca80a0552d24252639a6ae775aa1df700ffb92c2411daea7286f158d44081c8172d072a0772a87d08cf38c4c68bfde770968571abd16fd3835cb902486bd2e515d53c12d80a0413774f3d900d2d2be7a3ad999ffa859a471dc03a74fb9a6d8275455f5496a548080',
                             '0xf869a020d13b52a61d3c1325ce3626a51418adebd6323d4840f1bdd93906359d11c933b846f8440180a01ab7c0b0a2a4bbb5a1495da8c142150891fc64e0c321e1feb70bd5f881951f7ea0551332d96d085185ab4019ad8bcf89c45321e136c261eb6271e574a2edf1461f'
                             ],
            'balance': 0,
            'codeHash': '0x551332d96d085185ab4019ad8bcf89c45321e136c261eb6271e574a2edf1461f',
            'nonce': 1,
            'storageHash': '0x1ab7c0b0a2a4bbb5a1495da8c142150891fc64e0c321e1feb70bd5f881951f7e',
            'storageProof': [
                AttributeDict({
                    'key': '0x00',
                    'value': '0x48656c6c6f00000000000000000000000000000000000000000000000000000a',
                    'proof': ['0xf9019180a01ace80e7bed79fbadbe390876bd1a7d9770edf9462049ef8f4b555d05715d53ea049347a3c2eac6525a3fd7e3454dab19d73b4adeb9aa27d29493b9843f3f88814a085079b4abcd07fd4a5d6c52d35f4c4574aecc85830e90c478ca8c18fcbe590de80a02e3f8ad7ea29e784007f51852b9c3e470aef06b11bac32586a8b691134e4c27da064d2157a14bc31f195f73296ea4dcdbe7698edbf3ca81c44bf7730179d98d94ca09e7dc2597c9b7f72ddf84d7eebb0fe2a2fa2ab54fe668cd14fee44d9b40b1a53a0aa5d4acc7ac636d16bc9655556770bc325e1901fb62dc53770ef9110009e080380a0d5fde962bd2fb5326ddc7a9ca7fe0ee47c5bb3227f838b6d73d3299c22457596a08691410eff46b88f929ef649ea25025f62a5362ca8dc8876e5e1f4fc8e79256d80a0673e88d3a8a4616f676793096b5ae87cff931bd20fb8dd466f97809a1126aad8a08b774a45c2273553e2daf4bbc3a8d44fb542ea29b6f125098f79a4d211b3309ca02fed3139c1791269acb9365eddece93e743900eba6b42a6a8614747752ba268f80',
                              '0xf891808080a0c7d094301e0c54da37b696d85f72de5520b224ab2cf4f045d8db1a3374caf0488080a0fc5581783bfe27fab9423602e1914d719fd71433e9d7dd63c95fe7e58d10c9c38080a0c64f346fc7a21f6679cba8abdf37ca2de8c4fcd8f8bcaedb261b5f77627c93908080808080a0ddef2936a67a3ac7d3d4ff15a935a45f2cc4976c8f0310aed85daf763780e2b480',
                              '0xf843a0200decd9548b62a8d60345a988386fc84ba6bc95484008f6362f93160ef3e563a1a048656c6c6f00000000000000000000000000000000000000000000000000000a'
                              ]
                })
            ]
        })

    * Merkle proof verification using py-trie.

    The following example verifies that the values returned in the ``AttributeDict``
    are included in the state of given trie ``root``.

    .. code-block:: python

        from eth_utils import (
            keccak,
        )
        import rlp
        from rlp.sedes import (
            Binary,
            big_endian_int,
        )
        from trie import (
            HexaryTrie,
        )
        from web3._utils.encoding import (
            pad_bytes,
        )

        def format_proof_nodes(proof):
            trie_proof = []
            for rlp_node in proof:
                trie_proof.append(rlp.decode(bytes(rlp_node)))
            return trie_proof

        def verify_eth_get_proof(proof, root):
            trie_root = Binary.fixed_length(32, allow_empty=True)
            hash32 = Binary.fixed_length(32)

            class _Account(rlp.Serializable):
                fields = [
                            ('nonce', big_endian_int),
                            ('balance', big_endian_int),
                            ('storage', trie_root),
                            ('code_hash', hash32)
                        ]
            acc = _Account(
                proof.nonce, proof.balance, proof.storageHash, proof.codeHash
            )
            rlp_account = rlp.encode(acc)
            trie_key = keccak(bytes.fromhex(proof.address[2:]))

            assert rlp_account == HexaryTrie.get_from_proof(
                root, trie_key, format_proof_nodes(proof.accountProof)
            ), f"Failed to verify account proof {proof.address}"

            for storage_proof in proof.storageProof:
                trie_key = keccak(pad_bytes(b'\x00', 32, storage_proof.key))
                root = proof.storageHash
                if storage_proof.value == b'\x00':
                    rlp_value = b''
                else:
                    rlp_value = rlp.encode(storage_proof.value)

                assert rlp_value == HexaryTrie.get_from_proof(
                    root, trie_key, format_proof_nodes(storage_proof.proof)
                ), f"Failed to verify storage proof {storage_proof.key}"

            return True

        block = w3.eth.get_block(3391)
        proof = w3.eth.get_proof('0x6C8f2A135f6ed072DE4503Bd7C4999a1a17F824B', [0, 1], 3391)
        assert verify_eth_get_proof(proof, block.stateRoot)


.. py:method:: Eth.get_code(account, block_identifier=eth.default_block)

    * Delegates to ``eth_getCode`` RPC Method

    Returns the bytecode for the given ``account`` at the block specified by
    ``block_identifier``.

    ``account`` may be a checksum address or an ENS name

    .. code-block:: python

        # For a contract address.
        >>> web3.eth.get_code('0x6C8f2A135f6ed072DE4503Bd7C4999a1a17F824B')
        '0x6060604052361561027c5760e060020a60003504630199.....'
        # For a private key address.
        >>> web3.eth.get_code('0xd3CdA913deB6f67967B99D67aCDFa1712C293601')
        '0x'


.. py:method:: Eth.get_block(block_identifier=eth.default_block, full_transactions=False)

    * Delegates to ``eth_getBlockByNumber`` or ``eth_getBlockByHash`` RPC Methods

    Returns the block specified by ``block_identifier``.  Delegates to
    ``eth_getBlockByNumber`` if ``block_identifier`` is an integer or one of
    the predefined block parameters ``'latest', 'earliest', 'pending',
    'safe', 'finalized'`` - otherwise delegates to ``eth_getBlockByHash``.
    Throws ``BlockNotFound`` error if the block is not found.

    If ``full_transactions`` is ``True`` then the ``'transactions'`` key will
    contain full transactions objects.  Otherwise it will be an array of
    transaction hashes.

    .. code-block:: python

        >>> web3.eth.get_block(2000000)
        AttributeDict({
            'difficulty': 49824742724615,
            'extraData': '0xe4b883e5bda9e7a59ee4bb99e9b1bc',
            'gasLimit': 4712388,
            'gasUsed': 21000,
            'hash': '0xc0f4906fea23cf6f3cce98cb44e8e1449e455b28d684dfa9ff65426495584de6',
            'logsBloom': '0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
            'miner': '0x61c808d82a3ac53231750dadc13c777b59310bd9',
            'nonce': '0x3b05c6d5524209f1',
            'number': 2000000,
            'parentHash': '0x57ebf07eb9ed1137d41447020a25e51d30a0c272b5896571499c82c33ecb7288',
            'receiptsRoot': '0x84aea4a7aad5c5899bd5cfc7f309cc379009d30179316a2a7baa4a2ea4a438ac',
            'sha3Uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
            'size': 650,
            'stateRoot': '0x96dbad955b166f5119793815c36f11ffa909859bbfeb64b735cca37cbf10bef1',
            'timestamp': 1470173578,
            'totalDifficulty': 44010101827705409388,
            'transactions': ['0xc55e2b90168af6972193c1f86fa4d7d7b31a29c156665d15b9cd48618b5177ef'],
            'transactionsRoot': '0xb31f174d27b99cdae8e746bd138a01ce60d8dd7b224f7c60845914def05ecc58',
            'uncles': [],
        })


.. py:method:: Eth.get_block_transaction_count(block_identifier)

    * Delegates to ``eth_getBlockTransactionCountByNumber`` or
      ``eth_getBlockTransactionCountByHash`` RPC Methods

    Returns the number of transactions in the block specified by
    ``block_identifier``.  Delegates to
    ``eth_getBlockTransactionCountByNumber`` if ``block_identifier`` is an
    integer or one of the predefined block parameters ``'latest', 'earliest',
    'pending', 'safe', 'finalized'``,
    otherwise delegates to ``eth_getBlockTransactionCountByHash``.
    Throws ``BlockNotFoundError`` if transactions are not found.

    .. code-block:: python

        >>> web3.eth.get_block_transaction_count(46147)
        1
        >>> web3.eth.get_block_transaction_count('0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd')  # block 46147
        1


.. py:method:: Eth.get_uncle_by_block(block_identifier, uncle_index)

    .. warning:: Deprecated. Will be removed in v8.

    * Delegates to ``eth_getUncleByBlockHashAndIndex`` or
      ``eth_getUncleByBlockNumberAndIndex`` RPC methods

    Returns the uncle at the index specified by ``uncle_index``
    from the block specified by ``block_identifier``.  Delegates to
    ``eth_getUncleByBlockNumberAndIndex`` if ``block_identifier`` is an
    integer or one of the predefined block parameters ``'latest', 'earliest',
    'pending'``, otherwise delegates to
    ``eth_getUncleByBlockHashAndIndex``. Throws ``BlockNotFound`` if the block is not found.

    .. code-block:: python

        >>> web3.eth.get_uncle_by_block(56160, 0)
        AttributeDict({
          'author': '0xbe4532e1b1db5c913cf553be76180c1777055403',
          'difficulty': '0x17dd9ca0afe',
          'extraData': '0x476574682f686261722f76312e302e312f6c696e75782f676f312e342e32',
          'gasLimit': '0x2fefd8',
          'gasUsed': '0x0',
          'hash': '0xc78c35720d930f9ef34b4e6fb9d02ffec936f9b02a8f0fa858456e4afd4d5614',
          'logsBloom':'0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
          'miner': '0xbe4532e1b1db5c913cf553be76180c1777055403',
          'mixHash': '0x041e14603f35a82f6023802fec96ef760433292434a39787514f140950597e5e',
          'nonce': '0x5d2b7e3f1af09995',
          'number': '0xdb5e',
          'parentHash': '0xcc30e8a9b15c548d5bf113c834143a8f0e1909fbfea96b2a208dc154293a78cf',
          'receiptsRoot': '0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421',
          'sealFields': ['0xa0041e14603f35a82f6023802fec96ef760433292434a39787514f140950597e5e', '0x885d2b7e3f1af09995'],
          'sha3Uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
          'size': None, 'stateRoot': '0x8ce2b1bf8e25a06a8ca34c647ff5fd0fa48ac725cc07f657ae1645ab8ef68c91',
          'timestamp': '0x55c6a972',
          'totalDifficulty': '0xce4c4f0a0b810b',
          'transactions': [],
          'transactionsRoot': '0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421',
          'uncles': []
        })

        # You can also refer to the block by hash:
        >>> web3.eth.get_uncle_by_block('0x685b2226cbf6e1f890211010aa192bf16f0a0cba9534264a033b023d7367b845', 0)
        AttributeDict({
            ...
        })


.. py:method:: Eth.get_uncle_count(block_identifier)

    .. warning:: Deprecated. Will be removed in v8.

    * Delegates to ``eth_getUncleCountByBlockHash`` or
      ``eth_getUncleCountByBlockNumber`` RPC methods

    Returns the (integer) number of uncles associated with the block specified by ``block_identifier``.
    Delegates to ``eth_getUncleCountByBlockNumber`` if ``block_identifier`` is an
    integer or one of the predefined block parameters ``'latest', 'earliest',
    'pending'``, otherwise delegates to ``eth_getUncleCountByBlockHash``.
    Throws ``BlockNotFound`` if the block is not found.

    .. code-block:: python

        >>> web3.eth.get_uncle_count(56160)
        1

        # You can also refer to the block by hash:
        >>> web3.eth.get_uncle_count('0x685b2226cbf6e1f890211010aa192bf16f0a0cba9534264a033b023d7367b845')
        1


.. py:method:: Eth.get_transaction(transaction_hash)

    * Delegates to ``eth_getTransactionByHash`` RPC Method

    Returns the transaction specified by ``transaction_hash``. If the transaction cannot be found throws :class:`web3.exceptions.TransactionNotFound`.

    .. code-block:: python

        >>> web3.eth.get_transaction('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060')
        AttributeDict({'blockHash': HexBytes('0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd'),
            'blockNumber': 46147,
            'from': '0xA1E4380A3B1f749673E270229993eE55F35663b4',
            'gas': 21000,
            'gasPrice': 50000000000000,
            'hash': HexBytes('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'),
            'input': HexBytes('0x'),
            'nonce': 0,
             'r': HexBytes('0x88ff6cf0fefd94db46111149ae4bfc179e9b94721fffd821d38d16464b3f71d0'),
             's': HexBytes('0x45e0aff800961cfce805daef7016b9b675c137a6a41a548f7b60a3484c06a33a'),
             'to': '0x5DF9B87991262F6BA471F09758CDE1c0FC1De734',
             'transactionIndex': 0,
             'type': 0,
             'v': 28,
             'value': 31337
        })


.. py:method:: Eth.get_raw_transaction(transaction_hash)

    * Delegates to ``eth_getRawTransactionByHash`` RPC Method

    Returns the raw form of transaction specified by ``transaction_hash``.

    If no transaction is found, ``TransactionNotFound`` is raised.

    .. code-block:: python

        >>> web3.eth.get_raw_transaction('0x86fbfe56cce542ff0a2a2716c31675a0c9c43701725c4a751d20ee2ddf8a733d')
        HexBytes('0xf86907843b9aca0082520894dc544d1aa88ff8bbd2f2aec754b1f1e99e1812fd018086eecac466e115a0f9db4e25484b28f486b247a372708d4cd0643fc63e604133afac577f4cc1eab8a044841d84e799d4dc18ba146816a937e8a0be8bc296bd8bb8aea126de5e627e06')


.. py:method:: Eth.get_transaction_by_block(block_identifier, transaction_index)

    * Delegates to ``eth_getTransactionByBlockNumberAndIndex`` or
      ``eth_getTransactionByBlockHashAndIndex`` RPC Methods

    Returns the transaction at the index specified by ``transaction_index``
    from the block specified by ``block_identifier``.  Delegates to
    ``eth_getTransactionByBlockNumberAndIndex`` if ``block_identifier`` is an
    integer or one of the predefined block parameters ``'latest', 'earliest',
    'pending', 'safe', 'finalized'``, otherwise delegates to
    ``eth_getTransactionByBlockHashAndIndex``.
    If a transaction is not found at specified arguments, throws :class:`web3.exceptions.TransactionNotFound`.

    .. code-block:: python

        >>> web3.eth.get_transaction_by_block(46147, 0)
        AttributeDict({
            'blockHash': '0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd',
            'blockNumber': 46147,
            'from': '0xA1E4380A3B1f749673E270229993eE55F35663b4',
            'gas': 21000,
            'gasPrice': None,
            'hash': '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060',
            'input': '0x',
            'maxFeePerGas': 2000000000,
            'maxPriorityFeePerGas': 1000000000,
            'nonce': 0,
            'to': '0x5DF9B87991262F6BA471F09758CDE1c0FC1De734',
            'transactionIndex': 0,
            'value': 31337,
        })
        >>> web3.eth.get_transaction_by_block('0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd', 0)
        AttributeDict({
            'blockHash': '0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd',
            'blockNumber': 46147,
            'from': '0xA1E4380A3B1f749673E270229993eE55F35663b4',
            'gas': 21000,
            'gasPrice': None,
            'hash': '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060',
            'input': '0x',
            'maxFeePerGas': 2000000000,
            'maxPriorityFeePerGas': 1000000000,
            'nonce': 0,
            'to': '0x5DF9B87991262F6BA471F09758CDE1c0FC1De734',
            'transactionIndex': 0,
            'value': 31337,
        })


.. py:method:: Eth.get_raw_transaction_by_block(block_identifier, transaction_index)

    * Delegates to ``eth_getRawTransactionByBlockNumberAndIndex`` or
      ``eth_getRawTransactionByBlockHashAndIndex`` RPC Methods

    Returns the raw transaction at the index specified by ``transaction_index``
    from the block specified by ``block_identifier``.  Delegates to
    ``eth_getRawTransactionByBlockNumberAndIndex`` if ``block_identifier`` is an
    integer or one of the predefined block parameters ``'latest', 'earliest',
    'pending', 'safe', 'finalized'``, otherwise delegates to
    ``eth_getRawTransactionByBlockHashAndIndex``.
    If a transaction is not found at specified arguments, throws :class:`web3.exceptions.TransactionNotFound`.

    .. code-block:: python

        >>> web3.eth.get_raw_transaction_by_block('latest', 0)
        HexBytes('0x02f87582053901843b9aca00843b9aca008301d8a894e2dfcfa89a45abdc3de91f7a2844b276b8451d2e888ac7230489e8000080c001a028dcd2e11682288c00237f377280bc6a478a6b27e9c2d745262152add1b1dfcba04e7a33b7ce2a37fc3cd3af7bdc7d7beff721664d56508defa188df35afd77c2c')
        >>> web3.eth.get_raw_transaction_by_block(2, 0)
        HexBytes('0x02f87582053901843b9aca00843b9aca008301d8a894e2dfcfa89a45abdc3de91f7a2844b276b8451d2e888ac7230489e8000080c001a028dcd2e11682288c00237f377280bc6a478a6b27e9c2d745262152add1b1dfcba04e7a33b7ce2a37fc3cd3af7bdc7d7beff721664d56508defa188df35afd77c2c')
        >>> web3.eth.get_raw_transaction_by_block('0xca609fb606a04ce6aaec76415cd0b9d8c2bc83ad2a4d17db7fd403ee7d97bf40', 0)
        HexBytes('0x02f87582053901843b9aca00843b9aca008301d8a894e2dfcfa89a45abdc3de91f7a2844b276b8451d2e888ac7230489e8000080c001a028dcd2e11682288c00237f377280bc6a478a6b27e9c2d745262152add1b1dfcba04e7a33b7ce2a37fc3cd3af7bdc7d7beff721664d56508defa188df35afd77c2c')

.. py:method:: Eth.wait_for_transaction_receipt(transaction_hash, timeout=120, poll_latency=0.1)

    Waits for the transaction specified by ``transaction_hash`` to be included in a block, then
    returns its transaction receipt.

    Optionally, specify a ``timeout`` in seconds. If timeout elapses before the transaction
    is added to a block, then :meth:`~Eth.wait_for_transaction_receipt` raises a
    :class:`web3.exceptions.TimeExhausted` exception.

    .. code-block:: python

        >>> web3.eth.wait_for_transaction_receipt('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060')
        # If transaction is not yet in a block, time passes, while the thread sleeps...
        # ...
        # Then when the transaction is added to a block, its receipt is returned:
        AttributeDict({
            'blockHash': HexBytes('0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd'),
            'blockNumber': 46147,
            'contractAddress': None,
            'cumulativeGasUsed': 21000,
            'from': '0xA1E4380A3B1f749673E270229993eE55F35663b4',
            'gasUsed': 21000,
            'logs': [],
            'logsBloom': HexBytes('0x000000000000000000000000000000000000000000000000...0000'),
            'status': 1,
            'to': '0x5DF9B87991262F6BA471F09758CDE1c0FC1De734',
            'transactionHash': HexBytes('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'),
            'transactionIndex': 0,
        })


.. py:method:: Eth.get_transaction_receipt(transaction_hash)

    * Delegates to ``eth_getTransactionReceipt`` RPC Method

    Returns the transaction receipt specified by ``transaction_hash``.  If the transaction cannot be found throws :class:`web3.exceptions.TransactionNotFound`.

    If ``status`` in response equals 1 the transaction was successful. If it is equals 0 the transaction was reverted by EVM.

    .. code-block:: python

        >>> web3.eth.get_transaction_receipt('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060')  # not yet mined
        Traceback # ... etc ...
        TransactionNotFound: Transaction with hash: 0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060 not found.

        # wait for it to be mined....
        >>> web3.eth.get_transaction_receipt('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060')
        AttributeDict({
            'blockHash': '0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd',
            'blockNumber': 46147,
            'contractAddress': None,
            'cumulativeGasUsed': 21000,
            'from': '0xA1E4380A3B1f749673E270229993eE55F35663b4',
            'gasUsed': 21000,
            'logs': [],
            'logsBloom': '0x000000000000000000000000000000000000000000000000...0000',
            'status': 1, # 0 or 1
            'to': '0x5DF9B87991262F6BA471F09758CDE1c0FC1De734',
            'transactionHash': '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060',
            'transactionIndex': 0,
        })


.. py:method:: Eth.get_transaction_count(account, block_identifier=web3.eth.default_block)

    * Delegates to ``eth_getTransactionCount`` RPC Method

    Returns the number of transactions that have been sent from ``account`` as
    of the block specified by ``block_identifier``.

    ``account`` may be a checksum address or an ENS name

    .. code-block:: python

        >>> web3.eth.get_transaction_count('0xd3CdA913deB6f67967B99D67aCDFa1712C293601')
        340


.. py:method:: Eth.send_transaction(transaction)

    * Delegates to ``eth_sendTransaction`` RPC Method

    Signs and sends the given ``transaction``

    The ``transaction`` parameter should be a dictionary with the following fields.

    * ``from``: ``bytes or text``, checksum address or ENS name - (optional, default:
      ``web3.eth.defaultAccount``) The address the transaction is sent from.
    * ``to``: ``bytes or text``, checksum address or ENS name - (optional when creating new
      contract) The address the transaction is directed to.
    * ``gas``: ``integer`` - (optional) Integer of the gas
      provided for the transaction execution. It will return unused gas.
    * ``maxFeePerGas``: ``integer or hex`` - (optional) maximum amount you're willing
      to pay, inclusive of ``baseFeePerGas`` and ``maxPriorityFeePerGas``. The difference
      between ``maxFeePerGas`` and ``baseFeePerGas + maxPriorityFeePerGas`` is refunded
      to the user.
    * ``maxPriorityFeePerGas``: ``integer or hex`` - (optional) the part of the fee
      that goes to the miner
    * ``gasPrice``: ``integer`` - Integer of the gasPrice used for each paid gas
      **LEGACY** - unless you have a good reason to use ``gasPrice``, use ``maxFeePerGas``
      and ``maxPriorityFeePerGas`` instead.
    * ``value``: ``integer`` - (optional) Integer of the value send with this
      transaction
    * ``data``: ``bytes or text`` - The compiled code of a contract OR the hash
      of the invoked method signature and encoded parameters. For details see
      `Ethereum Contract ABI <https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI>`_.
    * ``nonce``: ``integer`` - (optional) Integer of a nonce. This allows to
      overwrite your own pending transactions that use the same nonce.

    If the ``transaction`` specifies a ``data`` value but does not specify
    ``gas`` then the ``gas`` value will be populated using the
    :meth:`~web3.eth.Eth.estimate_gas()` function with an additional buffer of ``100000``
    gas up to the ``gasLimit`` of the latest block.  In the event that the
    value returned by :meth:`~web3.eth.Eth.estimate_gas()` method is greater than the
    ``gasLimit`` a ``ValueError`` will be raised.


    .. code-block:: python

        # simple example (web3.py and / or client determines gas and fees, typically defaults to a dynamic fee transaction post London fork)
        >>> web3.eth.send_transaction({
          'to': '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
          'from': web3.eth.accounts[0],
          'value': 12345
        })

        # Dynamic fee transaction, introduced by EIP-1559:
        HexBytes('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331')
        >>> web3.eth.send_transaction({
          'to': '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
          'from': web3.eth.accounts[0],
          'value': 12345,
          'gas': 21000,
          'maxFeePerGas': web3.to_wei(250, 'gwei'),
          'maxPriorityFeePerGas': web3.to_wei(2, 'gwei'),
        })
        HexBytes('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331')

        # Legacy transaction (less efficient)
        HexBytes('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331')
        >>> web3.eth.send_transaction({
          'to': '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
          'from': web3.eth.accounts[0],
          'value': 12345,
          'gas': 21000,
          'gasPrice': web3.to_wei(50, 'gwei'),
        })
        HexBytes('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331')


.. py:method:: Eth.sign_transaction(transaction)

    * Delegates to ``eth_signTransaction`` RPC Method.

    Returns a transaction that's been signed by the node's private key, but not yet submitted.
    The signed tx can be submitted with ``Eth.send_raw_transaction``

    .. code-block:: python

        >>> signed_txn = w3.eth.sign_transaction(dict(
            nonce=w3.eth.get_transaction_count(w3.eth.accounts[0]),
            maxFeePerGas=2000000000,
            maxPriorityFeePerGas=1000000000,
            gas=100000,
            to='0xd3CdA913deB6f67967B99D67aCDFa1712C293601',
            value=1,
            data=b'',
            )
        )
        b"\xf8d\x80\x85\x040\xe24\x00\x82R\x08\x94\xdcTM\x1a\xa8\x8f\xf8\xbb\xd2\xf2\xae\xc7T\xb1\xf1\xe9\x9e\x18\x12\xfd\x01\x80\x1b\xa0\x11\r\x8f\xee\x1d\xe5=\xf0\x87\x0en\xb5\x99\xed;\xf6\x8f\xb3\xf1\xe6,\x82\xdf\xe5\x97lF|\x97%;\x15\xa04P\xb7=*\xef \t\xf0&\xbc\xbf\tz%z\xe7\xa3~\xb5\xd3\xb7=\xc0v\n\xef\xad+\x98\xe3'"  # noqa: E501


.. py:method:: Eth.send_raw_transaction(raw_transaction)

    * Delegates to ``eth_sendRawTransaction`` RPC Method

    Sends a signed and serialized transaction. Returns the transaction hash as a HexBytes object.

    .. code-block:: python

        >>> signed_txn = w3.eth.account.sign_transaction(dict(
            nonce=w3.eth.get_transaction_count(public_address_of_senders_account),
            maxFeePerGas=3000000000,
            maxPriorityFeePerGas=2000000000,
            gas=100000,
            to='0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
            value=12345,
            data=b'',
            type=2,  # (optional) the type is now implicitly set based on appropriate transaction params
            chainId=1,
          ),
          private_key_for_senders_account,
        )
        >>> w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        HexBytes('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331')


.. py:method:: Eth.replace_transaction(transaction_hash, new_transaction)

    * Delegates to ``eth_sendTransaction`` RPC Method

    Sends a transaction that replaces the transaction with ``transaction_hash``.

    The ``transaction_hash`` must be the hash of a pending transaction.

    The ``new_transaction`` parameter should be a dictionary with transaction fields
    as required by :meth:`~web3.eth.Eth.send_transaction`. It will be used to entirely
    replace the transaction of ``transaction_hash`` without using any of the pending
    transaction's values.

    If the ``new_transaction`` specifies a ``nonce`` value, it must match the pending
    transaction's nonce.

    If the ``new_transaction`` specifies ``maxFeePerGas`` and ``maxPriorityFeePerGas``
    values, they must be greater than the pending transaction's values for each field,
    respectively.

    * Legacy Transaction Support (Less Efficient - Not Recommended)

    If the pending transaction specified a ``gasPrice`` value (legacy transaction), the
    ``gasPrice`` value for the ``new_transaction`` must be greater than the pending
    transaction's ``gasPrice``.

    If the ``new_transaction`` does not specify any of ``gasPrice``, ``maxFeePerGas``, or
    ``maxPriorityFeePerGas`` values, one of the following will happen:

    * If the pending transaction has a ``gasPrice`` value, this value will be used with a
      multiplier of 1.125 - This is typically the minimum ``gasPrice`` increase a node requires
      before it accepts a replacement transaction.
    * If a gas price strategy is set, the ``gasPrice`` value from the gas price
      strategy(See :ref:`Gas_Price`) will be used.
    * If none of the above, the client will ultimately decide appropriate values for ``maxFeePerGas``
      and ``maxPriorityFeePerGas``. These will likely be default values and may result in an
      unsuccessful replacement of the pending transaction.

    This method returns the transaction hash of the replacement transaction as a HexBytes object.

    .. code-block:: python

        >>> tx = web3.eth.send_transaction({
                'to': '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
                'from': web3.eth.accounts[0],
                'value': 1000
            })
        HexBytes('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331')
        >>> web3.eth.replace_transaction('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331', {
                'to': '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
                'from': web3.eth.accounts[0],
                'value': 2000
            })
        HexBytes('0x4177e670ec6431606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1528989')


.. py:method:: Eth.modify_transaction(transaction_hash, **transaction_params)

    * Delegates to ``eth_sendTransaction`` RPC Method

    Sends a transaction that modifies the transaction with ``transaction_hash``.

    ``transaction_params`` are keyword arguments that correspond to valid transaction
    parameters as required by :meth:`~web3.eth.Eth.send_transaction`. The parameter values
    will override the pending transaction's values to create the replacement transaction
    to send.

    The same validation and defaulting rules of :meth:`~web3.eth.Eth.replace_transaction` apply.

    This method returns the transaction hash of the newly modified transaction as a HexBytes object.

    .. code-block:: python

        >>> tx = web3.eth.send_transaction({
                'to': '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
                'from': web3.eth.accounts[0],
                'value': 1000
            })
        HexBytes('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331')
        >>> web3.eth.modify_transaction('0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331', value=2000)
        HexBytes('0xec6434e6701771606e55d6b4ca35a1a6b75ee3d73315145a921026d15299d05')


.. py:method:: Eth.sign(account, data=None, hexstr=None, text=None)

    * Delegates to ``eth_sign`` RPC Method

    Caller must specify exactly one of: ``data``, ``hexstr``, or ``text``.

    Signs the given data with the private key of the given ``account``.
    The account must be unlocked.

    ``account`` may be a checksum address or an ENS name

    .. code-block:: python

        >>> web3.eth.sign(
              '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
              text='some-text-tö-sign')
        '0x1a8bbe6eab8c72a219385681efefe565afd3accee35f516f8edf5ae82208fbd45a58f9f9116d8d88ba40fcd29076d6eada7027a3b412a9db55a0164547810cc401'

        >>> web3.eth.sign(
              '0x582AC4D8929f58c217d4a52aDD361AE470a8a4cD',
              data=b'some-text-t\xc3\xb6-sign')
        '0x1a8bbe6eab8c72a219385681efefe565afd3accee35f516f8edf5ae82208fbd45a58f9f9116d8d88ba40fcd29076d6eada7027a3b412a9db55a0164547810cc401'

        >>> web3.eth.sign(
              '0xd3CdA913deB6f67967B99D67aCDFa1712C293601',
              hexstr='0x736f6d652d746578742d74c3b62d7369676e')
        '0x1a8bbe6eab8c72a219385681efefe565afd3accee35f516f8edf5ae82208fbd45a58f9f9116d8d88ba40fcd29076d6eada7027a3b412a9db55a0164547810cc401'


.. py:method:: Eth.sign_typed_data(account, jsonMessage)

    * Delegates to ``eth_signTypedData`` RPC Method

    .. note::

        ``eth_signTypedData`` is not currently supported by any major client (Besu, Erigon, Geth, or Nethermind)

    Please note that the ``jsonMessage`` argument is the loaded JSON Object
    and **NOT** the JSON String itself.

    Signs the ``Structured Data`` (or ``Typed Data``) with the private key of the given ``account``.
    The account must be unlocked.

    ``account`` may be a checksum address or an ENS name


.. py:method:: Eth.call(transaction, block_identifier=web3.eth.default_block, state_override=None, ccip_read_enabled=True)

    * Delegates to ``eth_call`` RPC Method

    Executes the given transaction locally without creating a new transaction
    on the blockchain.  Returns the return value of the executed contract.

    The ``transaction`` parameter is handled in the same manner as the
    :meth:`~web3.eth.Eth.send_transaction()` method.

    .. code-block:: python

        >>> myContract.functions.setVar(1).transact()
        HexBytes('0x79af0c7688afba7588c32a61565fd488c422da7b5773f95b242ea66d3d20afda')
        >>> myContract.functions.getVar().call()
        1
        # The above call equivalent to the raw call:
        >>> web3.eth.call({'value': 0, 'gas': 21736, 'maxFeePerGas': 2000000000, 'maxPriorityFeePerGas': 1000000000, 'to': '0xc305c901078781C232A2a521C2aF7980f8385ee9', 'data': '0x477a5c98'})
        HexBytes('0x0000000000000000000000000000000000000000000000000000000000000001')

    In most cases it is better to make contract function call through the :py:class:`web3.contract.Contract` interface.

    Overriding state is a debugging feature available in Geth clients.
    View their `usage documentation <https://geth.ethereum.org/docs/rpc/ns-eth#3-object---state-override-set>`_
    for a list of possible parameters.

    `EIP-3668 <https://eips.ethereum.org/EIPS/eip-3668>`_ introduced support for the ``OffchainLookup`` revert / CCIP
    Read support. In order to properly handle a call to a contract function that reverts with an ``OffchainLookup``
    error for offchain data retrieval, the ``ccip_read_enabled`` flag has been added to the ``eth_call`` method.
    ``ccip_read_enabled`` is optional, yielding the default value for CCIP Read on calls to a global
    ``global_ccip_read_enabled`` flag on the provider which is set to ``True`` by default. This means CCIP Read is
    enabled by default for calls, as is recommended in EIP-3668. Therefore, calls to contract functions that revert with
    an ``OffchainLookup`` will be handled appropriately by default.

    The ``ccip_read_enabled`` flag on the call will always override the value of the global flag on the provider for
    explicit control over specific calls. If the flag on the call is set to ``False``, the call will raise the
    ``OffchainLookup`` instead of properly handling the exception according to EIP-3668. This may be useful for
    "preflighting" a transaction with a call (see :ref:`ccip-read-example` within the examples section).

    If the function called results in a ``revert`` error, a ``ContractLogicError`` will be raised.
    If there is an error message with the error, web3.py attempts to parse the
    message that comes back and return it to the user as the error string.
    As of v6.3.0, the raw data is also returned and
    can be accessed via the ``data`` attribute on ``ContractLogicError``.


.. py:method:: Eth.simulateV1(payload, block_identifier)

    * Delegates to ``eth_simulateV1`` RPC Method

    Executes a simulation for the given payload at the given block. Returns the simulation results.

    .. code-block:: python

        >>> w3.eth.simulateV1(
        ...   {
        ...     "blockStateCalls": [
        ...       {
        ...         "blockOverrides": {
        ...           "baseFeePerGas": Wei(10),
        ...         },
        ...         "stateOverrides": {
        ...           "0xc100000000000000000000000000000000000000": {
        ...             "balance": Wei(500000000),
        ...           }
        ...         },
        ...         "calls": [
        ...           {
        ...             "from": "0xc100000000000000000000000000000000000000",
        ...             "to": "0xc100000000000000000000000000000000000000",
        ...             "maxFeePerGas": Wei(10),
        ...             "maxPriorityFeePerGas": Wei(10),
        ...           }
        ...         ],
        ...       }
        ...     ],
        ...     "validation": True,
        ...     "traceTransfers": True,
        ...   },
        ...   "latest",
        ... )
        [AttributeDict({
          'baseFeePerGas': 10,
          'blobGasUsed': 0,
          'calls': [AttributeDict({
            'returnData': HexBytes('0x'),
            'logs': [],
            'gasUsed': 21000,
            'status': 1
          })],
          'difficulty': 0,
          'excessBlobGas': 0,
          'extraData': HexBytes('0x'),
          'gasLimit': 983527531,
          'gasUsed': 21000,
          'hash': HexBytes('0xb2dba64c905dea42e940d67b8e0f44019f4a61c4833a9cba99c426b748d9e1a4'),
          'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
          'miner': '0x0000000000000000000000000000000000000000',
          'mixHash': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'),
          'nonce': HexBytes('0x0000000000000000'),
          'number': 18,
          'parentBeaconBlockRoot': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'),
          'parentHash': HexBytes('0x71d32db179a1291de86b5f7fa15224292ef9ee6ebb3fa62484896601d9f20d5f'),
          'receiptsRoot': HexBytes('0xf78dfb743fbd92ade140711c8bbc542b5e307f0ab7984eff35d751969fe57efa'),
          'sha3Uncles': HexBytes('0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347'),
          'size': 626,
          'stateRoot': HexBytes('0xbbbe846b616911d13780f58f500f8948e0878ba6f55cae7432da915cab3ba2b6'),
          'timestamp': 1739921487,
          'transactions': [HexBytes('0xfd801060af398c615f1ffb61586604aaf4fc688615cb1ff088531638a9b9e8e6')],
          'transactionsRoot': HexBytes('0xa6bc01d7707e94b62dccb8d097df1db25d6b44fad35463ecc99c9e5822e7aa5f'),
          'uncles': [],
          'withdrawals': [],
          'withdrawalsRoot': HexBytes('0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421')
        })]


.. py:method:: Eth.create_access_list(transaction, block_identifier=web3.eth.default_block)

    * Delegates to ``eth_createAccessList`` RPC Method

    This method creates an `EIP-2930 <https://eips.ethereum.org/EIPS/eip-2930>`_ type ``accessList`` based on a given
    ``transaction``. The ``accessList`` contains all storage slots and addresses read and written by the transaction,
    except for the sender account and the precompiles. This method uses the same ``transaction`` call object and
    ``block_identifier`` object as :meth:`~web3.eth.Eth.call()`. An ``accessList`` can be used to access contracts that
    became inaccessible due to gas cost increases.

    The ``transaction`` parameter is handled in the same manner as the
    :meth:`~web3.eth.Eth.send_transaction()` method.
    The optional ``block_identifier`` parameter is a block_number or ``latest`` or ``pending``. Default is ``latest``.

    .. code-block:: python

        >>> w3.eth.create_access_list(
        ...     {
        ...         "to": to_checksum_address("0xF0109fC8DF283027b6285cc889F5aA624EaC1F55"),
        ...         "gasPrice": 10**11,
        ...         "value": 0,
        ...         "data": "0x608060806080608155",
        ...     },
        ...     "pending",
        ... )
        AttributeDict({
            "accessList": [
                AttributeDict({
                    "address": "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe",
                    "storageKeys": [
                        "0x0000000000000000000000000000000000000000000000000000000000000003",
                        "0x0000000000000000000000000000000000000000000000000000000000000007",
                    ]
                }),
                AttributeDict({
                    "address": "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                    "storageKeys": []
                }),
            ],
            "gasUsed": 21000
        })

    The method ``eth_createAccessList`` returns a list of addresses and storage keys used by the transaction, plus the gas
    consumed when the ``accessList`` is included. Like ``eth_estimateGas``, this is an estimation; the list could change when
    the transaction is actually finalized. Adding an ``accessList`` to your transaction does not necessarily result in lower
    gas usage compared to a transaction without an ``accessList``.

.. py:method:: Eth.fee_history(block_count, newest_block, reward_percentiles=None)

    * Delegates to ``eth_feeHistory`` RPC Method

    Returns transaction fee data for up to 1,024 blocks.

    :param block_count: The number of blocks in the requested range. Depending on the client, this
        value should be either a :py:class:`int` between 1 and 1024 or a hexstring.
        Less than requested may be returned if not all blocks are available.
    :type block_count: int or hexstring
    :param newest_block: The newest, highest-numbered, block in the requested range. This value may be an
        :py:class:`int` or one of the predefined block parameters ``'latest'``, ``'earliest'``, or ``'pending'``.
    :type newest_block: int or BlockParams
    :param reward_percentiles: *(optional)* A monotonically increasing list of percentile :py:class:`float` values to
        sample from each block's effective priority fees per gas in ascending order, weighted by gas used.
    :type reward_percentiles: List[float] or None
    :return: An ``AttributeDict`` containing the following keys:

    * **oldestBlock** *(int)* -- The oldest, lowest-numbered, block in the range requested as a ``BlockNumber`` type
      with :py:class:`int` value.
    * **baseFeePerGas** *(List[Wei])* -- An array of block base fees per gas. This includes the next block after the
      newest of the returned range, because this value can be derived from the newest block. Zeroes are returned for
      pre-EIP-1559 blocks.
    * **gasUsedRatio** *(List[float])* -- An array of ``gasUsed``/``gasLimit`` float values for the requested blocks.
    * **reward** *(List[List[Wei]])* -- *(optional)* A two-dimensional array of effective priority fees per gas at the
      requested block percentiles.

    .. code-block:: python

        >>> w3.eth.fee_history(4, 'latest', [10, 90])
        AttributeDict({
            'oldestBlock': 3,
            'reward': [[220, 7145389], [1000000, 6000213], [550, 550], [125, 12345678]],
            'baseFeePerGas': [202583058, 177634473, 155594425, 136217133, 119442408],
            'gasUsedRatio': [0.007390479689642084, 0.0036988514889990873, 0.0018512333048507866, 0.00741217041320997]
        })


.. py:method:: Eth.estimate_gas(transaction, block_identifier=None, state_override=None)

    * Delegates to ``eth_estimateGas`` RPC Method

    Executes the given transaction locally without creating a new transaction
    on the blockchain.  Returns amount of gas consumed by execution which can
    be used as a gas estimate.

    The ``transaction`` and ``block_identifier`` parameters are handled in the
    same manner as the :meth:`~web3.eth.Eth.send_transaction()` method.

    The ``state_override`` is useful when there is a chain of transaction calls.
    It overrides state so that the gas estimate of a transaction is accurate in
    cases where prior calls produce side effects.

    .. code-block:: python

        >>> web3.eth.estimate_gas({'to': '0xd3CdA913deB6f67967B99D67aCDFa1712C293601', 'from':web3.eth.accounts[0], 'value': 12345})
        21000


.. py:method:: Eth.generate_gas_price(transaction_params=None)

    Uses the selected gas price strategy to calculate a gas price. This method
    returns the gas price denominated in wei.

    The ``transaction_params`` argument is optional however some gas price strategies
    may require it to be able to produce a gas price.

    .. code-block:: python

        >>> web3.eth.generate_gas_price()
        20000000000

    .. note::
        For information about how gas price can be customized in web3 see
        :ref:`Gas_Price`.


.. py:method:: Eth.set_gas_price_strategy(gas_price_strategy)

    Set the selected gas price strategy. It must be a method of the signature
    ``(web3, transaction_params)`` and return a gas price denominated in wei.


.. py:method:: Eth.subscribe(subscription_identifier, subscription_params)

      * Delegates to ``eth_subscribe`` RPC Method

      Only available on persistent connection providers:
      :class:`~web3.providers.persistent.WebSocketProvider` and
      :class:`~web3.providers.persistent.AsyncIPCProvider`.

      Returns a subscription ID that can be used to track a particular subscription to, or unsubscribe from, an event.
      For usage examples see the docs on :ref:`subscription-examples`.

      .. code-block:: python

          >>> subscription_id = await web3.eth.subscribe('newHeaders')
          >>> subscription_id
          '0xbd63bb89e7475591a0a6fc9014307bc4'


.. py:method:: Eth.unsubscribe(subscription_id)

      * Delegates to ``eth_unsubscribe`` RPC Method

      Only available on persistent connection providers:
      :class:`~web3.providers.persistent.WebSocketProvider` and
      :class:`~web3.providers.persistent.AsyncIPCProvider`.

      Returns ``True`` if successfully unsubscribed. For usage examples see the docs on
      :ref:`subscription-examples`.

      .. code-block:: python

          >>> result = await web3.eth.unsubscribe(subscription_id)
          >>> result
          True


Filters
-------

The following methods are available on the ``web3.eth`` object for interacting
with the filtering API.


.. py:method:: Eth.filter(filter_params)

    * Delegates to ``eth_newFilter``, ``eth_newBlockFilter``, and
      ``eth_newPendingTransactionFilter`` RPC Methods.

    This method delegates to one of three RPC methods depending on the value of
    ``filter_params``.

    * If ``filter_params`` is the string ``'pending'`` then a new filter is
      registered using the ``eth_newPendingTransactionFilter`` RPC method.
      This will create a new filter that will be called for each new unmined
      transaction that the node receives.
    * If ``filter_params`` is the string ``'latest'`` then a new filter is
      registered using the ``eth_newBlockFilter`` RPC method.  This will create
      a new filter that will be called each time the node receives a new block.
    * If ``filter_params`` is a dictionary then a new filter is registered
      using the ``eth_newFilter`` RPC method.  This will create a new filter
      that will be called for all log entries that match the provided
      ``filter_params``.

    This method returns a ``web3.utils.filters.Filter`` object which can then
    be used to either directly fetch the results of the filter or to register
    callbacks which will be called with each result of the filter.

    When creating a new log filter, the ``filter_params`` should be a
    dictionary with the following keys. Note that the keys are camel-cased
    strings, as is expected in a JSON-RPC request.

    * ``fromBlock``: ``integer/tag`` - (optional, default: "latest") Integer
      block number, or one of predefined block identifiers
      "latest", "pending", "earliest", "safe", or "finalized".
    * ``toBlock``: ``integer/tag`` - (optional, default: "latest") Integer
      block number, or one of predefined block identifiers
      "latest", "pending", "earliest", "safe", or "finalized".
    * ``address``: ``string`` or list of ``strings``, each 20 Bytes -
      (optional) Contract address or a list of addresses from which logs should
      originate.
    * ``topics``: list of 32 byte ``strings`` or ``null`` - (optional) Array of
      topics that should be used for filtering.  Topics are order-dependent.
      This parameter can also be a list of topic lists in which case filtering
      will match any of the provided topic arrays.

    .. note::

        Though ``"latest"`` and ``"safe"`` block identifiers are not yet part of the
        specifications for ``eth_newFilter``, they are supported by web3.py and may or
        may not yield expected results depending on the node being accessed.

    See :doc:`./filters` for more information about filtering.

    .. code-block:: python

        >>> web3.eth.filter('latest')
        <BlockFilter at 0x10b72dc28>
        >>> web3.eth.filter('pending')
        <TransactionFilter at 0x10b780340>
        >>> web3.eth.filter({'fromBlock': 1000000, 'toBlock': 1000100, 'address': '0x6C8f2A135f6ed072DE4503Bd7C4999a1a17F824B'})
        <LogFilter at 0x10b7803d8>

.. py:method:: Eth.get_filter_changes(self, filter_id)

    * Delegates to ``eth_getFilterChanges`` RPC Method.

    Returns all new entries which occurred since the last call to this method
    for the given ``filter_id``

    .. code-block:: python

        >>> filter = web3.eth.filter()
        >>> web3.eth.get_filter_changes(filter.filter_id)
        [
            {
                'address': '0xDc3A9Db694BCdd55EBaE4A89B22aC6D12b3F0c24',
                'blockHash': '0xb72256286ca528e09022ffd408856a73ef90e7216ac560187c6e43b4c4efd2f0',
                'blockNumber': 2217196,
                'data': '0x0000000000000000000000000000000000000000000000000000000000000001',
                'logIndex': 0,
                'topics': ['0xe65b00b698ba37c614af350761c735c5f4a82b4ab365a1f1022d49d9dfc8e930',
                '0x000000000000000000000000754c50465885f1ed1fa1a55b95ee8ecf3f1f4324',
                '0x296c7fb6ccafa3e689950b947c2895b07357c95b066d5cdccd58c301f41359a3'],
                'transactionHash': '0xfe1289fd3915794b99702202f65eea2e424b2f083a12749d29b4dd51f6dce40d',
                'transactionIndex': 1,
            },
            ...
        ]


.. py:method:: Eth.get_filter_logs(self, filter_id)

    * Delegates to ``eth_getFilterLogs`` RPC Method.

    Returns all entries for the given ``filter_id``

    .. code-block:: python

        >>> filter = web3.eth.filter()
        >>> web3.eth.get_filter_logs(filter.filter_id)
        [
            {
                'address': '0xDc3A9Db694BCdd55EBaE4A89B22aC6D12b3F0c24',
                'blockHash': '0xb72256286ca528e09022ffd408856a73ef90e7216ac560187c6e43b4c4efd2f0',
                'blockNumber': 2217196,
                'data': '0x0000000000000000000000000000000000000000000000000000000000000001',
                'logIndex': 0,
                'topics': ['0xe65b00b698ba37c614af350761c735c5f4a82b4ab365a1f1022d49d9dfc8e930',
                '0x000000000000000000000000754c50465885f1ed1fa1a55b95ee8ecf3f1f4324',
                '0x296c7fb6ccafa3e689950b947c2895b07357c95b066d5cdccd58c301f41359a3'],
                'transactionHash': '0xfe1289fd3915794b99702202f65eea2e424b2f083a12749d29b4dd51f6dce40d',
                'transactionIndex': 1,
            },
            ...
        ]


.. py:method:: Eth.uninstall_filter(self, filter_id)

    * Delegates to ``eth_uninstallFilter`` RPC Method.

    Uninstalls the filter specified by the given ``filter_id``.  Returns
    boolean as to whether the filter was successfully uninstalled.

    .. code-block:: python

        >>> filter = web3.eth.filter()
        >>> web3.eth.uninstall_filter(filter.filter_id)
        True
        >>> web3.eth.uninstall_filter(filter.filter_id)
        False  # already uninstalled.


.. py:method:: Eth.get_logs(filter_params)

    This is the equivalent of: creating a new
    filter, running :meth:`~Eth.get_filter_logs`, and then uninstalling the filter. See
    :meth:`~Eth.filter` for details on allowed filter parameters.


Contracts
---------

.. py:method:: Eth.contract(address=None, contract_name=None, ContractFactoryClass=Contract, **contract_factory_kwargs)

    If ``address`` is provided, then this method will return an instance of the
    contract defined by ``abi``. The address may be a checksum string,
    or an ENS name like ``'mycontract.eth'``.

    .. code-block:: python

        from web3 import Web3

        w3 = Web3(...)

        contract = w3.eth.contract(address='0x000000000000000000000000000000000000dEaD', abi=...)

        # alternatively:
        contract = w3.eth.contract(address='mycontract.eth', abi=...)

    .. note::

        If you use an ENS name to initialize a contract, the contract will be looked up by
        name on each use. If the name could ever change maliciously, first
        :ref:`ens_get_address`, and then create the contract with the checksum address.


    If ``address`` is *not* provided, the newly created contract class will be returned. That
    class will then be initialized by supplying the address.

    .. code-block:: python

        from web3 import Web3

        w3 = Web3(...)

        Contract = w3.eth.contract(abi=...)

        # later, initialize contracts with the same metadata at different addresses:
        contract1 = Contract(address='0x000000000000000000000000000000000000dEaD')
        contract2 = Contract(address='mycontract.eth')

    ``contract_name`` will be used as the name of the contract class.  If it is
    ``None`` then the name of the ``ContractFactoryClass`` will be used.

    ``ContractFactoryClass`` will be used as the base Contract class.

    The following arguments are accepted for contract class creation.

    :param abi: Application Binary Interface. Usually provided since an ``abi`` is required to interact with any contract.
    :type abi: ABI
    :param asm: Assembly code generated by the compiler
    :param ast: Abstract Syntax Tree of the contract generated by the compiler
    :param bytecode: Bytecode of the contract generated by the compiler
    :param bytecode_runtime: Bytecode stored at the contract address, excludes the constructor and initialization code
    :param clone_bin:
    :param dev_doc:
    :param decode_tuples: Optionally convert tuples/structs to named tuples
    :param interface:
    :param metadata: Contract Metadata generated by the compiler
    :param opcodes: Opcodes for the contract generated by the compiler
    :param src_map:
    :param src_map_runtime:
    :param user_doc:
    :return: Instance of the contract
    :rtype: Contract
    :raises TypeError: If the address is not provided
    :raises AttributeError: If the contract class is not initialized

    See the :doc:`web3.contract` documentation for more information about Contracts.


.. py:method:: Eth.set_contract_factory(contractFactoryClass)

    Modify the default contract factory from ``Contract`` to ``contractFactoryClass``.
    Future calls to ``Eth.contract()`` will then default to ``contractFactoryClass``.
