Beacon API
==========

.. warning:: This API Is experimental. Client support is incomplete and the API itself is still evolving.

To use this API, you'll need a beacon node running locally or remotely. To set that up, refer to the documentation of your specific client.

Once you have a running beacon node, import and configure your beacon instance:

.. code-block:: python

    >>> from web3.beacon import Beacon
    >>> beacon = Beacon("http://localhost:5051")

Methods
-------

.. py:method:: Beacon.get_genesis()

    .. code-block:: python

        >>> beacon.get_genesis()
        {
          'data': {
            'genesis_time': '1605700807',
            'genesis_validators_root': '0x9436e8a630e3162b7ed4f449b12b8a5a368a4b95bc46b941ae65c11613bfa4c1',
            'genesis_fork_version': '0x00002009'
          }
        }

.. py:method:: Beacon.get_hash_root(state_id="head")

    .. code-block:: python

        >>> beacon.get_hash_root()
        {
          "data": {
            "root":"0xbb399fda70617a6f198b3d9f1c1cdbd70077677231b84f34e58568c9dc903558"
          }
        }

.. py:method:: Beacon.get_fork_data(state_id="head")

    .. code-block:: python

        >>> beacon.get_fork_data()
        {
          'data': {
            'previous_version': '0x00002009',
            'current_version': '0x00002009',
            'epoch': '0'
          }
        }

.. py:method:: Beacon.get_finality_checkpoint(state_id="head")

    .. code-block:: python

        >>> beacon.get_finality_checkpoint()
        {
          'data': {
            'previous_justified': {
              'epoch': '5024',
              'root': '0x499ba555e8e8be639dd84be1be6d54409738facefc662f37d97065aa91a1a8d4'
            },
            'current_justified': {
              'epoch': '5025',
              'root': '0x34e8a230f11536ab2ec56a0956e1f3b3fd703861f96d4695877eaa48fbacc241'
            },
            'finalized': {
              'epoch': '5024',
              'root': '0x499ba555e8e8be639dd84be1be6d54409738facefc662f37d97065aa91a1a8d4'
            }
          }
        }

.. py:method:: Beacon.get_validators(state_id="head")

    .. code-block:: python

        >>> beacon.get_validators()
         {
           'data': [
             {
               'index': '110280',
               'balance': '32000000000',
               'status': 'pending_queued',
               'validator': {
                 'pubkey': '0x99d37d1f7dd15859995330f75c158346f86d298e2ffeedfbf1b38dcf3df89a7dbd1b34815f3bcd1b2a5588592a35b783',
                 'withdrawal_credentials': '0x00f338cfdb0c22bb85beed9042bd19fff58ad6421c8a833f8bc902b7cca06f5f',
                 'effective_balance': '32000000000',
                 'slashed': False,
                 'activation_eligibility_epoch': '5029',
                 'activation_epoch': '18446744073709551615',
                 'exit_epoch': '18446744073709551615',
                 'withdrawable_epoch': '18446744073709551615'
               }
             },
             ...
           ]
         }

.. py:method:: Beacon.get_validator(validator_id, state_id="head")

    .. code-block:: python

        >>> beacon.get_validator(110280)
        {
          'data': {
            'index': '110280',
            'balance': '32000000000',
            'status': 'pending_queued',
            'validator': {
              'pubkey': '0x99d37d1f7dd15859995330f75c158346f86d298e2ffeedfbf1b38dcf3df89a7dbd1b34815f3bcd1b2a5588592a35b783',
              'withdrawal_credentials': '0x00f338cfdb0c22bb85beed9042bd19fff58ad6421c8a833f8bc902b7cca06f5f',
              'effective_balance': '32000000000',
              'slashed': False,
              'activation_eligibility_epoch': '5029',
              'activation_epoch': '18446744073709551615',
              'exit_epoch': '18446744073709551615',
              'withdrawable_epoch': '18446744073709551615'
            }
          }
        }

.. py:method:: Beacon.get_validator_balances(state_id="head")

    .. code-block:: python

        >>> beacon.get_validator_balances()
        {
          'data': [
            {
              'index': '110278',
              'balance': '32000000000'
            },
            ...
          ]
        }

.. py:method:: Beacon.get_epoch_committees(state_id="head")

    .. code-block:: python

        >>> beacon.get_epoch_committees()
        {
          'data': [
            {
              'slot': '162367',
              'index': '25',
              'validators': ['50233', '36829', '84635', ...],
            },
            ...
          ]
        }

.. py:method:: Beacon.get_block_headers()

    .. code-block:: python

        >>> beacon.get_block_headers()
        {
          'data': [
            {
              'root': '0xa3873e7b1e0bcc7c59013340cfea59dff16e42e79825e7b8ab6c243dbafd4fe0',
              'canonical': True,
              'header': {
                'message': {
                  'slot': '163587',
                  'proposer_index': '69198',
                  'parent_root': '0xc32558881dbb791ef045c48e3709a0978dc445abee4ae34d30df600eb5fbbb3d',
                  'state_root': '0x4dc0a72959803a84ee0231160b05dda76a91b8f8b77220b4cfc7db160840b8a8',
                  'body_root': '0xa3873e7b1e0bcc7c59013340cfea59dff16e42e79825e7b8ab6c243dbafd4fe0'
                },
                'signature': '0x87b549448d36e5e8b1783944b5511a05f34bb78ad3fcbf71a1adb346eed363d46e50d51ac53cd23bd03d0107d064e05913a6ef10f465f9171aba3b2b8a7a4d621c9e18d5f148813295a2d5aa5053029ccbd88cec72130833de2b4b7addf7faca'
              }
            }
          ]
        }

.. py:method:: Beacon.get_block_header(block_id)

    .. code-block:: python

        >>> beacon.get_block_header(1)
        {
          'data': {
            root': '0x30c04689dd4f6cd4d56eb78f72727d2d16d8b6346724e4a88f546875f11b750d',
            'canonical': True,
            'header': {
              'message': {
                'slot': '1',
                'proposer_index': '61090',
                'parent_root': '0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87',
                'state_root': '0x7773ed5a7e944c6238cd0a5c32170663ef2be9efc594fb43ad0f07ecf4c09d2b',
                'body_root': '0x30c04689dd4f6cd4d56eb78f72727d2d16d8b6346724e4a88f546875f11b750d'
              },
              'signature': '0xa30d70b3e62ff776fe97f7f8b3472194af66849238a958880510e698ec3b8a470916680b1a82f9d4753c023153fbe6db10c464ac532c1c9c8919adb242b05ef7152ba3e6cd08b730eac2154b9802203ead6079c8dfb87f1e900595e6c00b4a9a'
            }
          }
        }

.. py:method:: Beacon.get_block(block_id)

    .. code-block:: python

        >>> beacon.get_block(1)
        {
          'data': {
            'message': {
              'slot': '1',
              'proposer_index': '61090',
              'parent_root': '0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87',
              'state_root': '0x7773ed5a7e944c6238cd0a5c32170663ef2be9efc594fb43ad0f07ecf4c09d2b',
              'body': {
                'randao_reveal': '0x8e245a52a0a680fcfe789013e123880c321f237de10cad108dc55dd47290d7cfe50cdaa003c6f783405efdac48cef44e152493abba40d9f9815a060dd6151cb0635906c9e3c1ad4859cada73ccd2d6b8747e4aeeada7d75d454bcc8672afa813',
                'eth1_data': {
                  'deposit_root': '0x4e910ac762815c13e316e72506141f5b6b441d58af8e0a049cd3341c25728752',
                  'deposit_count': '100596',
                  'block_hash': '0x89cb78044843805fb4dab8abd743fc96c2b8e955c58f9b7224d468d85ef57130'
                },
                'graffiti': '0x74656b752f76302e31322e31342b34342d673863656562663600000000000000',
                'proposer_slashings': [],
                'attester_slashings': [],
                'attestations': [
                  {
                    'aggregation_bits': '0x0080020004000000008208000102000905',
                    'data': {
                      'slot': '0',
                      'index': '7',
                      'beacon_block_root': '0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87',
                      'source': {
                        'epoch': '0',
                        'root': '0x0000000000000000000000000000000000000000000000000000000000000000'
                      },
                      'target': {
                        'epoch': '0',
                        'root': '0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87'
                      }
                    },
                    'signature': '0x967dd2946358db7e426ed19d4576bc75123520ef6a489ca50002222070ee4611f9cef394e5e3071236a93b825f18a4ad07f1d5a1405e6c984f1d71e03f535d13a2156d6ba22cb0c2b148df23a7b8a7293315d6e74b9a26b64283e8393f2ad4c5'
                  }
                ],
                'deposits': [],
                'voluntary_exits': []
              }
            },
            'signature': '0xa30d70b3e62ff776fe97f7f8b3472194af66849238a958880510e698ec3b8a470916680b1a82f9d4753c023153fbe6db10c464ac532c1c9c8919adb242b05ef7152ba3e6cd08b730eac2154b9802203ead6079c8dfb87f1e900595e6c00b4a9a'
          }
        }

.. py:method:: Beacon.get_block_root(block_id)

    .. code-block:: python

        >>> beacon.get_block_root(1)
        {
          'data': {
            'root': '0x30c04689dd4f6cd4d56eb78f72727d2d16d8b6346724e4a88f546875f11b750d'
          }
        }

.. py:method:: Beacon.get_block_attestations(block_id)

    .. code-block:: python

        >>> beacon.get_block_attestations(1)
        {
          'data': [
            {
              'aggregation_bits': '0x0080020004000000008208000102000905',
              'data': {
                'slot': '0',
                'index': '7',
                'beacon_block_root': '0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87',
                'source': {
                  'epoch': '0',
                  'root': '0x0000000000000000000000000000000000000000000000000000000000000000'
                },
                'target': {
                  'epoch': '0',
                  'root': '0x6a89af5df908893eedbed10ba4c13fc13d5653ce57db637e3bfded73a987bb87'
                }
              },
              'signature': '0x967dd2946358db7e426ed19d4576bc75123520ef6a489ca50002222070ee4611f9cef394e5e3071236a93b825f18a4ad07f1d5a1405e6c984f1d71e03f535d13a2156d6ba22cb0c2b148df23a7b8a7293315d6e74b9a26b64283e8393f2ad4c5'
            },
            ...
          ]
        }

.. py:method:: Beacon.get_attestations()

    .. code-block:: python

        >>> beacon.get_attestations()
        {'data': []}


.. py:method:: Beacon.get_attester_slashings()

    .. code-block:: python

        >>> beacon.get_attester_slashings()
        {'data': []}

.. py:method:: Beacon.get_proposer_slashings()

    .. code-block:: python

        >>> beacon.get_proposer_slashings()
        {'data': []}

.. py:method:: Beacon.get_voluntary_exits()

    .. code-block:: python

        >>> beacon.get_voluntary_exits()
        {'data': []}


.. py:method:: Beacon.get_fork_schedule()

    .. code-block:: python

        >>> beacon.get_fork_schedule()
        {
          'data': [
            {
              'previous_version': '0x00002009',
              'current_version': '0x00002009',
              'epoch': '0'
            }
          ]
        }

.. py:method:: Beacon.get_spec()

    .. code-block:: python

        >>> beacon.get_spec()
        {
          'data': {
            'DEPOSIT_CONTRACT_ADDRESS': '0x8c5fecdC472E27Bc447696F431E425D02dd46a8c',
            'MIN_ATTESTATION_INCLUSION_DELAY': '1',
            'SLOTS_PER_EPOCH': '32',
            'SHUFFLE_ROUND_COUNT': '90',
            'MAX_EFFECTIVE_BALANCE': '32000000000',
            'DOMAIN_BEACON_PROPOSER': '0x00000000',
            'MAX_ATTESTER_SLASHINGS': '2',
            'DOMAIN_SELECTION_PROOF': '0x05000000',
            ...
          }
        }

.. py:method:: Beacon.get_deposit_contract()

    .. code-block:: python

        >>> beacon.get_deposit_contract()
        {
          'data': {
            'chain_id': '5',
            'address': '0x8c5fecdC472E27Bc447696F431E425D02dd46a8c'
          }
        }

.. py:method:: Beacon.get_beacon_state(state_id="head")

    .. code-block:: python

        >>> beacon.get_beacon_state()
        {
          'data': {
            'genesis_time': '1',
            'genesis_validators_root': '0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2',
            'slot': '1',
            'fork': {
              'previous_version': '0x00000000',
              'current_version': '0x00000000',
              'epoch': '1'
            },
            'latest_block_header': {
              'slot': '1',
              'proposer_index': '1',
              'parent_root': '0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2',
              'state_root': '0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2',
              'body_root': '0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2'
            },
            'block_roots': ['0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2'],
            'state_roots': ['0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2'],
            'historical_roots': ['0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2'],
            'eth1_data': {
              'deposit_root': '0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2',
              'deposit_count': '1',
              'block_hash': '0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2'
            },
            'eth1_data_votes': [...],
            'eth1_deposit_index': '1',
            'validators': [...],
            'balances': [...],
            'randao_mixes': [...],
            'slashings': [...],
            'previous_epoch_attestations': [...],
            'current_epoch_attestations': [...],
            'justification_bits': '0x0f',
            'previous_justified_checkpoint': {
              'epoch': '5736',
              'root': '0xec7ef54f1fd81bada8170dd0cb6be8216f8ee2f445e6936f95f5c6894a4a3b38'
            },
            'current_justified_checkpoint': {
              'epoch': '5737',
              'root': '0x781f0166e34c361ce2c88070c1389145abba2836edcb446338a2ca2b0054826e'
            },
            'finalized_checkpoint': {
              'epoch': '5736',
              'root': '0xec7ef54f1fd81bada8170dd0cb6be8216f8ee2f445e6936f95f5c6894a4a3b38'
            }
          }
        }

.. py:method:: Beacon.get_beacon_heads()

    .. code-block:: python

        >>> beacon.get_beacon_heads()
        {
          'data': [
            {
              'slot': '221600',
              'root': '0x9987754077fe6100a60c75d81a51b1ef457d019404d1546a66f4f5d6c23fae45'
            }
          ]
        }

.. py:method:: Beacon.get_blob_sidecars(block_id, indices=[])

    .. code-block:: python

        >>> beacon.get_blob_sidecars(1, indices=[1])
        {
          "data": [
            {
              "index": "1",
              "blob": ..., # omitted
              "kzg_commitment": "0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a",
              "kzg_proof": "0x7FB0A12D11Ffe8A48c2fF80dCA17adbCC1da5F6aADaAEF2b338717dcDEECf6DaB9FD7C4e4265CfBc097cD31dCB19E836",
              "signed_block_header": {
                "message": {
                  "slot": "1",
                  "proposer_index": "1",
                  "parent_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                  "state_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                  "body_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
                },
                "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505"
              },
              "kzg_commitment_inclusion_proof": [
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
                "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
              ]
            }
          ]
        }

.. py:method:: Beacon.get_node_identity()

    .. code-block:: python

        >>> beacon.get_node_identity()
        {
          'data': {
            'peer_id': '16Uiu2HAmLZ1CYVFKpa3wwn4cnknZqosum8HX3GHDhUpEULQc9ixE',
            'enr': 'enr:-KG4QCIp6eCZ6hG_fd93qsw12qmbfsl2rUTfQvwVP4FOTlWeNXYo0Gg9y3WVYIdF6FQC6R0E8CbK0Ywq_6TKMx1BpGlAhGV0aDKQOwiHlQAAIAn__________4JpZIJ2NIJpcIR_AAABiXNlY3AyNTZrMaEDdVT4g1gw86BfbrtLCq2fRBlG0AnMxsXtAQgA327S5FeDdGNwgiMog3VkcIIjKA',
            'p2p_addresses': ['/ip4/127.0.0.1/tcp/9000/p2p/16Uiu2HAmLZ1CYVFKpa3wwn4cnknZqosum8HX3GHDhUpEULQc9ixE'],
            'discovery_addresses': ['/ip4/127.0.0.1/udp/9000/p2p/16Uiu2HAmLZ1CYVFKpa3wwn4cnknZqosum8HX3GHDhUpEULQc9ixE'],
            'metadata': {'seq_number': '0', 'attnets': '0x0000000000000000'}
          }
        }

.. py:method:: Beacon.get_peers()

    .. code-block:: python

        >>> beacon.get_peers()
        {
          'data': [
            {
              'peer_id': '16Uiu2HAkw1yVqF3RtMCBHMbkLZbNhfGcTUdD6Uo4X3wfzPhGVnqv',
              'address': '/ip4/3.127.23.51/tcp/9000',
              'state': 'connected',
              'direction': 'outbound'
            },
            {
              'peer_id': '16Uiu2HAmEJHiCzgS8GwiEYLyM3d148mzvZ9iZzsz8yqayWVPANMG',
              'address': '/ip4/3.88.7.240/tcp/9000',
              'state': 'connected',
              'direction': 'outbound'
            }
          ]
        }

.. py:method:: Beacon.get_peer(peer_id)

    .. code-block:: python

        >>> beacon.get_peer('16Uiu2HAkw1yVqF3RtMCBHMbkLZbNhfGcTUdD6Uo4X3wfzPhGVnqv')
        {
          'data': {
            'peer_id': '16Uiu2HAkw1yVqF3RtMCBHMbkLZbNhfGcTUdD6Uo4X3wfzPhGVnqv',
            'address': '/ip4/3.127.23.51/tcp/9000',
            'state': 'connected',
            'direction': 'outbound'
          }
        }

.. py:method:: Beacon.get_health()

    .. code-block:: python

        >>> beacon.get_health()
        200

.. py:method:: Beacon.get_version()

    .. code-block:: python

        >>> beacon.get_version()
        {
          'data': {
            'version': 'teku/v20.12.0+9-g9392008/osx-x86_64/adoptopenjdk-java-15'
          }
        }

.. py:method:: Beacon.get_syncing()

    .. code-block:: python

        >>> beacon.get_syncing()
        {
          'data': {
            'head_slot': '222270',
            'sync_distance': '190861'
          }
        }
