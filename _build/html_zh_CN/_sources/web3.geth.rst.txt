Geth API
========

.. py:module:: web3.geth

The ``web3.geth`` object exposes modules that enable you to interact with the JSON-RPC endpoints supported by `Geth <https://github.com/ethereum/go-ethereum/wiki/Management-APIs>`_ that are not defined in the standard set of Ethereum JSONRPC endpoints according to `EIP 1474 <https://github.com/ethereum/EIPs/pull/1474>`_.

GethAdmin API
~~~~~~~~~~~~~

The following methods are available on the ``web3.geth.admin`` namespace.

.. py:module:: web3.geth.admin

The ``web3.geth.admin`` object exposes methods to interact with the RPC APIs under the
``admin_`` namespace that are supported by the Geth client.

.. py:method:: datadir()

    * Delegates to ``admin_datadir`` RPC Method

    Returns the system path of the node's data directory.

    .. code-block:: python

        >>> web3.geth.admin.datadir()
        '/Users/snakecharmers/Library/Ethereum'


.. py:method:: node_info()

    * Delegates to ``admin_nodeInfo`` RPC Method

    Returns information about the currently running node.

    .. code-block:: python

        >>> web3.geth.admin.node_info()
        {
            'enode': 'enode://e54eebad24dce1f6d246bea455ffa756d97801582420b9ed681a2ea84bf376d0bd87ae8dd6dc06cdb862a2ca89ecabe1be1050be35b4e70d62bc1a092cb7e2d3@[::]:30303',
            'id': 'e54eebad24dce1f6d246bea455ffa756d97801582420b9ed681a2ea84bf376d0bd87ae8dd6dc06cdb862a2ca89ecabe1be1050be35b4e70d62bc1a092cb7e2d3',
            'ip': '::',
            'listenAddr': '[::]:30303',
            'name': 'Geth/v1.4.11-stable-fed692f6/darwin/go1.7',
            'ports': {'discovery': 30303, 'listener': 30303},
            'protocols': {
                'eth': {
                    'difficulty': 57631175724744612603,
                    'genesis': '0xd4e56740f876aef8c010b86a40d5f56745a118d0906a34e69aec8c0db1cb8fa3',
                    'head': '0xaaef6b9dd0d34088915f4c62b6c166379da2ad250a88f76955508f7cc81fb796',
                    'network': 1,
                },
            },
        }


.. py:method:: peers()

    * Delegates to ``admin_peers`` RPC Method

    Returns the current peers the node is connected to.

    .. code-block:: python

        >>> web3.geth.admin.peers()
        [
            {
                'caps': ['eth/63'],
                'id': '146e8e3e2460f1e18939a5da37c4a79f149c8b9837240d49c7d94c122f30064e07e4a42ae2c2992d0f8e7e6f68a30e7e9ad31d524349ec9d17effd2426a37b40',
                'name': 'Geth/v1.4.10-stable/windows/go1.6.2',
                'network': {
                    'localAddress': '10.0.3.115:64478',
                    'remoteAddress': '72.208.167.127:30303',
                },
                'protocols': {
                    'eth': {
                        'difficulty': 17179869184,
                        'head': '0xd4e56740f876aef8c010b86a40d5f56745a118d0906a34e69aec8c0db1cb8fa3',
                        'version': 63,
                    },
                }
            },
            {
                'caps': ['eth/62', 'eth/63'],
                'id': '76cb6cd3354be081923a90dfd4cda40aa78b307cc3cf4d5733dc32cc171d00f7c08356e9eb2ea47eab5aad7a15a3419b859139e3f762e1e1ebf5a04f530dcef7',
                'name': 'Geth/v1.4.10-stable-5f55d95a/linux/go1.5.1',
                'network': {
                    'localAddress': '10.0.3.115:64784',
                    'remoteAddress': '60.205.92.119:30303',
                },
                'protocols': {
                    'eth': {
                        'difficulty': 57631175724744612603,
                        'head': '0xaaef6b9dd0d34088915f4c62b6c166379da2ad250a88f76955508f7cc81fb796',
                        'version': 63,
                    },
                },
            },
            ...
        ]


.. py:method:: add_peer(node_url)

    * Delegates to ``admin_addPeer`` RPC Method

    Requests adding a new remote node to the list of tracked static nodes.

    .. code-block:: python

        >>> web3.geth.admin.add_peer('enode://e54eebad24dce1f6d246bea455ffa756d97801582420b9ed681a2ea84bf376d0bd87ae8dd6dc06cdb862a2ca89ecabe1be1050be35b4e70d62bc1a092cb7e2d3@52.71.255.237:30303')
        True


.. py:method:: start_http(host='localhost', port=8545, cors="", apis="eth,net,web3")

    * Delegates to ``admin_startHTTP`` RPC Method

    Starts the HTTP based JSON RPC API webserver on the specified ``host`` and
    ``port``, with the ``rpccorsdomain`` set to the provided ``cors`` value and
    with the APIs specified by ``apis`` enabled.  Returns boolean as to whether
    the server was successfully started.

    .. code-block:: python

        >>> web3.geth.admin.start_http()
        True


.. py:method:: start_ws(host='localhost', port=8546, cors="", apis="eth,net,web3")

    * Delegates to ``admin_startWS`` RPC Method

    Starts the WebSocket based JSON RPC API webserver on the specified ``host``
    and ``port``, with the ``rpccorsdomain`` set to the provided ``cors`` value
    and with the APIs specified by ``apis`` enabled.  Returns boolean as to
    whether the server was successfully started.

    .. code-block:: python

        >>> web3.geth.admin.start_ws()
        True


.. py:method:: stop_http()

    * Delegates to ``admin_stopHTTP`` RPC Method

    Stops the HTTP based JSON RPC server.

    .. code-block:: python

        >>> web3.geth.admin.stop_http()
        True


.. py:method:: stop_ws()

    * Delegates to ``admin_stopWS`` RPC Method

    Stops the WebSocket based JSON RPC server.

    .. code-block:: python

        >>> web3.geth.admin.stop_ws()
        True


.. py:module:: web3.geth.txpool

GethTxPool API
~~~~~~~~~~~~~~

The ``web3.geth.txpool`` object exposes methods to interact with the RPC APIs under
the ``txpool_`` namespace. These methods are only exposed under the ``geth`` namespace
since they are not standard.

The following methods are available on the ``web3.geth.txpool`` namespace.

.. py:method:: TxPool.inspect()

    * Delegates to ``txpool_inspect`` RPC Method

    Returns a textual summary of all transactions currently pending for
    inclusion in the next block(s) as well as ones that are scheduled for
    future execution.

    .. code-block:: python

        >>> web3.geth.txpool.inspect()
        {
            'pending': {
                '0x26588a9301b0428d95e6Fc3A5024fcE8BEc12D51': {
                  31813: ["0x3375Ee30428b2A71c428afa5E89e427905F95F7e: 0 wei + 500000 × 20000000000 gas"]
                },
                '0x2a65Aca4D5fC5B5C859090a6c34d164135398226': {
                  563662: ["0x958c1Fa64B34db746925c6F8a3Dd81128e40355E: 1051546810000000000 wei + 90000 × 20000000000 gas"],
                  563663: ["0x77517B1491a0299A44d668473411676f94e97E34: 1051190740000000000 wei + 90000 × 20000000000 gas"],
                  563664: ["0x3E2A7Fe169c8F8eee251BB00d9fb6d304cE07d3A: 1050828950000000000 wei + 90000 × 20000000000 gas"],
                  563665: ["0xAF6c4695da477F8C663eA2D8B768Ad82Cb6A8522: 1050544770000000000 wei + 90000 × 20000000000 gas"],
                  563666: ["0x139B148094C50F4d20b01cAf21B85eDb711574dB: 1048598530000000000 wei + 90000 × 20000000000 gas"],
                  563667: ["0x48B3Bd66770b0D1EeceFCe090daFeE36257538aE: 1048367260000000000 wei + 90000 × 20000000000 gas"],
                  563668: ["0x468569500925D53e06Dd0993014aD166fD7Dd381: 1048126690000000000 wei + 90000 × 20000000000 gas"],
                  563669: ["0x3DcB4C90477a4b8Ff7190b79b524773CbE3bE661: 1047965690000000000 wei + 90000 × 20000000000 gas"],
                  563670: ["0x6DfeF5BC94b031407FFe71ae8076CA0FbF190963: 1047859050000000000 wei + 90000 × 20000000000 gas"]
                },
                '0x9174E688d7dE157C5C0583Df424EAAB2676aC162': {
                  3: ["0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413: 30000000000000000000 wei + 85000 × 21000000000 gas"]
                },
                '0xb18F9d01323e150096650ab989CfecD39D757Aec': {
                  777: ["0xcD79c72690750F079ae6AB6ccd7e7aEDC03c7720: 0 wei + 1000000 × 20000000000 gas"]
                },
                '0xB2916C870Cf66967B6510B76c07E9d13a5D23514': {
                  2: ["0x576f25199D60982A8f31A8DfF4da8aCB982e6ABa: 26000000000000000000 wei + 90000 × 20000000000 gas"]
                },
                '0xBc0CA4f217E052753614d6B019948824d0d8688B': {
                  0: ["0x2910543Af39abA0Cd09dBb2D50200b3E800A63D2: 1000000000000000000 wei + 50000 × 1171602790622 gas"]
                },
                '0xea674fdde714fd979de3edf0f56aa9716b898ec8': {
                  70148: ["0xe39c55ead9f997f7fa20ebe40fb4649943d7db66: 1000767667434026200 wei + 90000 × 20000000000 gas"]
                }
              },
              'queued': {
                '0x0F6000De1578619320aBA5e392706b131FB1dE6f': {
                  6: ["0x8383534d0bcd0186d326C993031311c0Ac0D9B2d: 9000000000000000000 wei + 21000 × 20000000000 gas"]
                },
                '0x5b30608c678e1ac464A8994C3B33E5CdF3497112': {
                  6: ["0x9773547e27f8303C87089dc42D9288aa2B9d8F06: 50000000000000000000 wei + 90000 × 50000000000 gas"]
                },
                '0x976A3Fc5d6f7d259EBfb4cc2Ae75115475E9867C': {
                  3: ["0x346FB27dE7E7370008f5da379f74dd49F5f2F80F: 140000000000000000 wei + 90000 × 20000000000 gas"]
                },
                '0x9B11bF0459b0c4b2f87f8CEBca4cfc26f294B63A': {
                  2: ["0x24a461f25eE6a318BDef7F33De634A67bb67Ac9D: 17000000000000000000 wei + 90000 × 50000000000 gas"],
                  6: ["0x6368f3f8c2B42435D6C136757382E4A59436a681: 17990000000000000000 wei + 90000 × 20000000000 gas", "0x8db7b4e0ecb095fbd01dffa62010801296a9ac78: 16998950000000000000 wei + 90000 × 20000000000 gas"],
                  7: ["0x6368f3f8c2B42435D6C136757382E4A59436a681: 17900000000000000000 wei + 90000 × 20000000000 gas"]
                }
              }
        }


.. py:method:: TxPool.status()

    * Delegates to ``txpool_status`` RPC Method

    Returns a textual summary of all transactions currently pending for
    inclusion in the next block(s) as well as ones that are scheduled for
    future execution.

    .. code-block:: python

        {
            pending: 10,
            queued: 7,
        }


.. py:method:: TxPool.content()

    * Delegates to ``txpool_content`` RPC Method

    Returns the exact details of all transactions that are pending or queued.

    .. code-block:: python

        >>> web3.geth.txpool.content()
        {
          'pending': {
            '0x0216D5032f356960Cd3749C31Ab34eEFF21B3395': {
              806: [{
                'blockHash': "0x0000000000000000000000000000000000000000000000000000000000000000",
                'blockNumber': None,
                'from': "0x0216D5032f356960Cd3749C31Ab34eEFF21B3395",
                'gas': "0x5208",
                'gasPrice': None,
                'hash': "0xaf953a2d01f55cfe080c0c94150a60105e8ac3d51153058a1f03dd239dd08586",
                'input': "0x",
                'maxFeePerGas': '0x77359400',
                'maxPriorityFeePerGas': '0x3b9aca00',
                'nonce': "0x326",
                'to': "0x7f69a91A3CF4bE60020fB58B893b7cbb65376db8",
                'transactionIndex': None,
                'value': "0x19a99f0cf456000"
              }]
            },
            '0x24d407e5A0B506E1Cb2fae163100B5DE01F5193C': {
              34: [{
                'blockHash': "0x0000000000000000000000000000000000000000000000000000000000000000",
                'blockNumber': None,
                'from': "0x24d407e5A0B506E1Cb2fae163100B5DE01F5193C",
                'gas': "0x44c72",
                'gasPrice': None,
                'hash': "0xb5b8b853af32226755a65ba0602f7ed0e8be2211516153b75e9ed640a7d359fe",
                'input': "0xb61d27f600000000000000000000000024d407e5a0b506e1cb2fae163100b5de01f5193c00000000000000000000000000000000000000000000000053444835ec580000000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                'maxFeePerGas': '0x77359400',
                'maxPriorityFeePerGas': '0x3b9aca00',
                'nonce': "0x22",
                'to': "0x7320785200f74861B69C49e4ab32399a71b34f1a",
                'transactionIndex': None,
                'value': "0x0"
              }]
            }
          },
          'queued': {
            '0x976A3Fc5d6f7d259EBfb4cc2Ae75115475E9867C': {
              3: [{
                'blockHash': "0x0000000000000000000000000000000000000000000000000000000000000000",
                'blockNumber': None,
                'from': "0x976A3Fc5d6f7d259EBfb4cc2Ae75115475E9867C",
                'gas': "0x15f90",
                'gasPrice': None,
                'hash': "0x57b30c59fc39a50e1cba90e3099286dfa5aaf60294a629240b5bbec6e2e66576",
                'input': "0x",
                'maxFeePerGas': '0x77359400',
                'maxPriorityFeePerGas': '0x3b9aca00',
                'nonce': "0x3",
                'to': "0x346FB27dE7E7370008f5da379f74dd49F5f2F80F",
                'transactionIndex': None,
                'value': "0x1f161421c8e0000"
              }]
            },
            '0x9B11bF0459b0c4b2f87f8CEBca4cfc26f294B63A': {
              2: [{
                'blockHash': "0x0000000000000000000000000000000000000000000000000000000000000000",
                'blockNumber': None,
                'from': "0x9B11bF0459b0c4b2f87f8CEBca4cfc26f294B63A",
                'gas': "0x15f90",
                'gasPrice': None,
                'hash': "0x3a3c0698552eec2455ed3190eac3996feccc806970a4a056106deaf6ceb1e5e3",
                'input': "0x",
                'maxFeePerGas': '0x77359400',
                'maxPriorityFeePerGas': '0x3b9aca00',
                'nonce': "0x2",
                'to': "0x24a461f25eE6a318BDef7F33De634A67bb67Ac9D",
                'transactionIndex': None,
                'value': "0xebec21ee1da40000"
              }],
              6: [{
                'blockHash': "0x0000000000000000000000000000000000000000000000000000000000000000",
                'blockNumber': None,
                'from': "0x9B11bF0459b0c4b2f87f8CEBca4cfc26f294B63A",
                'gas': "0x15f90",
                'gasPrice': None,
                'hash': "0xbbcd1e45eae3b859203a04be7d6e1d7b03b222ec1d66dfcc8011dd39794b147e",
                'input': "0x",
                'maxFeePerGas': '0x77359400',
                'maxPriorityFeePerGas': '0x3b9aca00',
                'nonce': "0x6",
                'to': "0x6368f3f8c2B42435D6C136757382E4A59436a681",
                'transactionIndex': None,
                'value': "0xf9a951af55470000"
              }, {
                'blockHash': "0x0000000000000000000000000000000000000000000000000000000000000000",
                'blockNumber': None,
                'from': "0x9B11bF0459b0c4b2f87f8CEBca4cfc26f294B63A",
                'gas': "0x15f90",
                'gasPrice': None,
                'hash': "0x60803251d43f072904dc3a2d6a084701cd35b4985790baaf8a8f76696041b272",
                'input': "0x",
                'maxFeePerGas': '0x77359400',
                'maxPriorityFeePerGas': '0x3b9aca00',
                'nonce': "0x6",
                'to': "0x8DB7b4e0ECB095FBD01Dffa62010801296a9ac78",
                'transactionIndex': None,
                'value': "0xebe866f5f0a06000"
              }],
            }
          }
        }

.. py:module:: web3.geth.debug

GethDebug API
~~~~~~~~~~~~~~

The ``web3.geth.debug`` object exposes methods to interact with the RPC APIs under the
``debug_`` namespace. These methods are only exposed under the ``geth`` namespace.
Full documentation around options can be found in the
`Geth docs <https://geth.ethereum.org/docs/developers/evm-tracing/built-in-tracers>`_.

.. py:method:: Debug.trace_transaction(transaction_hash)

    * Delegates to ``debug_traceTransaction`` RPC Method

    Returns the trace of the transaction with the given ``transaction_hash`` and ``trace_config``.

    .. code-block:: python

        >>> web3.geth.debug.trace_transaction('0x96014f00980a25dc7275a5eb5ed25ce0dd79c9233628c421ae373601236949b3')
            AttributeDict({
              'gas': 21000,
              'failed': False,
              'returnValue': '',
              'structLogs': []
            })

        >>> web3.geth.debug.trace_transaction('0x96014f00980a25dc7275a5eb5ed25ce0dd79c9233628c421ae373601236949b3', {
                "tracer": "prestateTracer",
            })
            AttributeDict({
              '0x0000000000000000000000000000000000000000': AttributeDict({'balance': 0}),
              '0x7fE3e4C21bDE162214B715AabcE05391301e9F5B': AttributeDict({'balance': 115792089237316195423570985008687907853269984665640564039457584007913129639927}),
              '0x91fe3039271d43d3f8479f60Cc5293Bc8A461b75': AttributeDict({'balance': 0})
            })

        >>> web3.geth.debug.trace_transaction('0x96014f00980a25dc7275a5eb5ed25ce0dd79c9233628c421ae373601236949b3', {
                "tracer": "prestateTracer",
                "traceConfig": {"diffMode": True}
            })
            AttributeDict({
              'post': AttributeDict({
                '0x0000000000000000000000000000000000000000': AttributeDict({'balance': 63000}),
                '0xcF888Cc4FAe8a3D774e574Ef8C6a261958287d04': AttributeDict({
                  'balance': 115792089237316195423570985008687907853269984665640564039457583959368602105927,
                  'nonce': 3
                }),
                '0xD2593D3445a9F0f4c776715f5206FBf4CA6A0475': AttributeDict({'balance': 100000})}),
              'pre': AttributeDict({
                '0x0000000000000000000000000000000000000000': AttributeDict({'balance': 42000}),
                '0xcF888Cc4FAe8a3D774e574Ef8C6a261958287d04': AttributeDict({
                  'balance': 115792089237316195423570985008687907853269984665640564039457583973451623990927,
                  'nonce': 2
                }),
                '0xD2593D3445a9F0f4c776715f5206FBf4CA6A0475': AttributeDict({'balance': 0})
              })
            })

        >>> web3.geth.debug.trace_transaction('0x96014f00980a25dc7275a5eb5ed25ce0dd79c9233628c421ae373601236949b3', {
                "tracer": "callTracer",
                "tracerConfig": {"withLog": False},
            })
            AttributeDict({'calls': [AttributeDict({'from': '0xa0457775a08b175Cbb444eD923556Dc67Ec5Dc11',
              'gas': 154003,
              'gasUsed': 275,
              'input': HexBytes('0xad5c4648'),
              'output': HexBytes('0x000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'),
              'to': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
              'type': 'STATICCALL'}),
              AttributeDict({'from': '0xa0457775a08b175Cbb444eD923556Dc67Ec5Dc11',
              'gas': 150633,
              'gasUsed': 24678,
              'input': HexBytes('0x095ea7b30000000000000000000000007a250d5630b4cf539739df2c5dacb4c659f2488d000000000000000000000000000000000000007e37be2022c0914b2680000000'),
              'output': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000001'),
              'to': '0xec4cF8dCB526080792bC98E1Ef41fB4775777b6B',
              'type': 'CALL',
              'value': 0}),
              AttributeDict({'calls': [AttributeDict({'from': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'gas': 121167,
                'gasUsed': 27504,
                'input': HexBytes('0x23b872dd000000000000000000000000a0457775a08b175cbb444ed923556dc67ec5dc1100000000000000000000000036f0548a77bfb1d5935483d25cc40633b46e2f4d000000000000000000000000000000000000007e37be2022c0914b2680000000'),
                'output': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000001'),
                'to': '0xec4cF8dCB526080792bC98E1Ef41fB4775777b6B',
                'type': 'CALL',
                'value': 0}),
                AttributeDict({'from': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'gas': 89911,
                'gasUsed': 2504,
                'input': HexBytes('0x0902f1ac'),
                'output': HexBytes('0x00000000000000000000000000000000000000000000000053f54ccde429ceb70000000000000000000000000000000000000000001635eb93ecdb339a7dc022000000000000000000000000000000000000000000000000000000006641f6cf'),
                'to': '0x36f0548a77BFb1d5935483D25cc40633b46e2f4d',
                'type': 'STATICCALL'}),
                AttributeDict({'from': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'gas': 86926,
                'gasUsed': 621,
                'input': HexBytes('0x70a0823100000000000000000000000036f0548a77bfb1d5935483d25cc40633b46e2f4d'),
                'output': HexBytes('0x000000000000000000000000000000000000007e37d4560e547e265a1a7dc022'),
                'to': '0xec4cF8dCB526080792bC98E1Ef41fB4775777b6B',
                'type': 'STATICCALL'}),
                AttributeDict({'calls': [AttributeDict({'from': '0x36f0548a77BFb1d5935483D25cc40633b46e2f4d',
                  'gas': 70279,
                  'gasUsed': 29962,
                  'input': HexBytes('0xa9059cbb0000000000000000000000007a250d5630b4cf539739df2c5dacb4c659f2488d00000000000000000000000000000000000000000000000053f53dfc545d56a6'),
                  'output': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000001'),
                  'to': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                  'type': 'CALL',
                  'value': 0}),
                  AttributeDict({'from': '0x36f0548a77BFb1d5935483D25cc40633b46e2f4d',
                  'gas': 40164,
                  'gasUsed': 534,
                  'input': HexBytes('0x70a0823100000000000000000000000036f0548a77bfb1d5935483d25cc40633b46e2f4d'),
                  'output': HexBytes('0x00000000000000000000000000000000000000000000000000000ed18fcc7811'),
                  'to': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                  'type': 'STATICCALL'}),
                  AttributeDict({'from': '0x36f0548a77BFb1d5935483D25cc40633b46e2f4d',
                  'gas': 39233,
                  'gasUsed': 621,
                  'input': HexBytes('0x70a0823100000000000000000000000036f0548a77bfb1d5935483d25cc40633b46e2f4d'),
                  'output': HexBytes('0x000000000000000000000000000000000000007e37d4560e547e265a1a7dc022'),
                  'to': '0xec4cF8dCB526080792bC98E1Ef41fB4775777b6B',
                  'type': 'STATICCALL'})],
                'from': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'gas': 84769,
                'gasUsed': 64940,
                'input': HexBytes('0x022c0d9f00000000000000000000000000000000000000000000000053f53dfc545d56a600000000000000000000000000000000000000000000000000000000000000000000000000000000000000007a250d5630b4cf539739df2c5dacb4c659f2488d00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000'),
                'to': '0x36f0548a77BFb1d5935483D25cc40633b46e2f4d',
                'type': 'CALL',
                'value': 0}),
                AttributeDict({'from': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'gas': 20382,
                'gasUsed': 534,
                'input': HexBytes('0x70a082310000000000000000000000007a250d5630b4cf539739df2c5dacb4c659f2488d'),
                'output': HexBytes('0x00000000000000000000000000000000000000000000000053f53dfc545d56a6'),
                'to': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                'type': 'STATICCALL'}),
                AttributeDict({'calls': [AttributeDict({'from': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                  'gas': 2300,
                  'gasUsed': 83,
                  'input': HexBytes('0x'),
                  'to': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                  'type': 'CALL',
                  'value': 6049809828398585510})],
                'from': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'gas': 19432,
                'gasUsed': 9223,
                'input': HexBytes('0x2e1a7d4d00000000000000000000000000000000000000000000000053f53dfc545d56a6'),
                'to': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                'type': 'CALL',
                'value': 0}),
                AttributeDict({'from': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'gas': 3353,
                'gasUsed': 0,
                'input': HexBytes('0x'),
                'to': '0xE11418f9961248da36b1008b1090235f680AE8f5',
                'type': 'CALL',
                'value': 6049809828398585510})],
              'from': '0xa0457775a08b175Cbb444eD923556Dc67Ec5Dc11',
              'gas': 125270,
              'gasUsed': 122013,
              'input': HexBytes('0x791ac947000000000000000000000000000000000000007e37be2022c0914b2680000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000e11418f9961248da36b1008b1090235f680ae8f5000000000000000000000000000000000000000000000000000000006641fe7f0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000ec4cf8dcb526080792bc98e1ef41fb4775777b6b000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'),
              'to': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
              'type': 'CALL',
              'value': 0})],
            'from': '0xE11418f9961248da36b1008b1090235f680AE8f5',
            'gas': 185574,
            'gasUsed': 144300,
            'input': HexBytes('0x56feb11b000000000000000000000000ec4cf8dcb526080792bc98e1ef41fb4775777b6b000000000000000000000000000000000000007e37be2022c0914b2680000000'),
            'to': '0xa0457775a08b175Cbb444eD923556Dc67Ec5Dc11',
            'type': 'CALL',
            'value': 0})

            >>> w3.geth.debug.trace_transaction(tx_hash, {'tracer': '4byteTracer'})
