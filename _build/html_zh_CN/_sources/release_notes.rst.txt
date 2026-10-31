Release Notes
=============

v7 Breaking Changes Summary
   See the :ref:`v7 Migration Guide<migrating_v6_to_v7>`

.. towncrier release notes start

web3.py v7.13.0 (2025-08-04)
----------------------------

Bugfixes
~~~~~~~~

- Raise ``BadResponseFormat`` from within ``FormattingMiddleware`` if the raw response is not a dict. (`#3735 <https://github.com/ethereum/web3.py/issues/3735>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix broken link to external ``eth_gasPrice`` documentation. (`#3717 <https://github.com/ethereum/web3.py/issues/3717>`__)


Features
~~~~~~~~

- Support parallelization of subscription handling globally via the subscription manager ``parallelize`` flag, and on a per-subscription basis via the ``parallelize`` flag on the subscription itself. (`#3709 <https://github.com/ethereum/web3.py/issues/3709>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Update integration test suite fixture to test against geth ``v1.16.2``. (`#1162 <https://github.com/ethereum/web3.py/issues/1162>`__)
- Add missing async tests for ``FormattingMiddleware`` as a sanity check. (`#3735 <https://github.com/ethereum/web3.py/issues/3735>`__)


web3.py v7.12.1 (2025-07-14)
----------------------------

Bugfixes
~~~~~~~~

- Fix ``AutoProvider`` batching setup by adding a proxy batch request. (`#3712 <https://github.com/ethereum/web3.py/issues/3712>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Update integrations tests to use geth ``v1.16.0``. (`#3727 <https://github.com/ethereum/web3.py/issues/3727>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3698 <https://github.com/ethereum/web3.py/issues/3698>`__, `#3710 <https://github.com/ethereum/web3.py/issues/3710>`__


web3.py v7.12.0 (2025-05-22)
----------------------------

Bugfixes
~~~~~~~~

- Thread safety for batching and better consistency with ``PersistentConnectionProvider`` implementations:

    - Make request batching threadsafe by using ``contextvars.ContextVar`` rather than a global flag for setting the batching state.
    - Deterministically match responses with request ids for ``PersistentConnectionProvider`` batch requests. (`#3705 <https://github.com/ethereum/web3.py/issues/3705>`__)


Deprecations
~~~~~~~~~~~~

- Deprecate ``ens_encode_name`` in favor of ``dns_encode_name``. (`#3700 <https://github.com/ethereum/web3.py/issues/3700>`__)


Features
~~~~~~~~

- Introduce ``ens.utils.dns_encode_name`` as a rename of the current ``ens_encode_name``, for consistency across other language implementations and with the ENS docs. Returns ``HexBytes`` instead of ``bytes``. (`#3700 <https://github.com/ethereum/web3.py/issues/3700>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Update some types in ``web3._utils.method_formatters`` (`#3669 <https://github.com/ethereum/web3.py/issues/3669>`__)
- Fix issues and start running the core tests with `pytest-xdist`, effectively reducing the CI test times by ~75-80%. (`#3705 <https://github.com/ethereum/web3.py/issues/3705>`__)


Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- optimize message formatting for logging (`#3643 <https://github.com/ethereum/web3.py/issues/3643>`__)
- Optimize web3._utils.decorators.reject_recursive_repeats (`#3668 <https://github.com/ethereum/web3.py/issues/3668>`__)
- optimize Method.method_selector_function (`#3696 <https://github.com/ethereum/web3.py/issues/3696>`__)
- optimize map_abi_data (`#3697 <https://github.com/ethereum/web3.py/issues/3697>`__)


web3.py v7.11.1 (2025-05-12)
----------------------------

Bugfixes
~~~~~~~~

- Fix contract event ``FilterParams`` to validate and normalize ``address`` parameters. (`#3618 <https://github.com/ethereum/web3.py/issues/3618>`__)
- Properly handle ``PersistentConnectionClosedOK`` for ``subscription_manager.handle_subscriptions()``. (`#3690 <https://github.com/ethereum/web3.py/issues/3690>`__)


Deprecations
~~~~~~~~~~~~

- Deprecate eth.get_uncle* methods. Will be removed in v8. (`#3683 <https://github.com/ethereum/web3.py/issues/3683>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Re-compile test contracts with new Solidity ``v0.8.30`` and re-generate integration test fixture to test against latest geth ``v1.15.11``. (`#3692 <https://github.com/ethereum/web3.py/issues/3692>`__)
- Remove old test fixtures when generating a new test fixture. (`#3693 <https://github.com/ethereum/web3.py/issues/3693>`__)
- Address some flaky tests due to a geth bug in state synchronization. (`#3695 <https://github.com/ethereum/web3.py/issues/3695>`__)


web3.py v7.11.0 (2025-04-29)
----------------------------

Bugfixes
~~~~~~~~

- Checks that ``PersistentConnectionProvider`` response cache value is a dict before attempting to access it like one. Also adds checks to ``make_batch_request`` to make sure it is in batching mode before being called and is not after. (`#3642 <https://github.com/ethereum/web3.py/issues/3642>`__)
- Moves base providers' ``_is_batching`` and ``_batch_request_func_cache`` from class to instance attrs to help with thread safety. (`#3661 <https://github.com/ethereum/web3.py/issues/3661>`__)


Features
~~~~~~~~

- Support for Prague network upgrade, mainly ``requests_hash`` and ``authorization_list`` formatters. Add support for serializing ``SignedSetCodeTransaction`` (`eth-account` pydantic model) directly added to transaction dicts. (`#3659 <https://github.com/ethereum/web3.py/issues/3659>`__)
- Allow setting the ``request_information_cache_size`` for ``PersistentConnectionProvider`` implementations. (`#3662 <https://github.com/ethereum/web3.py/issues/3662>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Update some outdated TODO notes in code & remove old un-tested uncles tests as no longer relevant post-merge. (`#3605 <https://github.com/ethereum/web3.py/issues/3605>`__)
- Run each integration test in isolation and parallelize, instead of running them all within a single `geth` (for example) process. This prevents muddied test contexts. (`#3659 <https://github.com/ethereum/web3.py/issues/3659>`__)
- Bound hypothesis integers in some tests to a max of uint256 value (`#3665 <https://github.com/ethereum/web3.py/issues/3665>`__)
- AsyncENS tests were xfailing for the wrong reason. (`#3675 <https://github.com/ethereum/web3.py/issues/3675>`__)


Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- Optimize performance for:

  * web3._utils.utility_methods.all_in_dict
  * web3._utils.utility_methods.any_in_dict
  * web3._utils.utility_methods.none_in_dict (`#3667 <https://github.com/ethereum/web3.py/issues/3667>`__)
- optimize web3._utils.rpc_abi.apply_abi_formatters_to_dict (`#3671 <https://github.com/ethereum/web3.py/issues/3671>`__)


web3.py v7.10.0 (2025-03-27)
----------------------------

Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3653 <https://github.com/ethereum/web3.py/issues/3653>`__


web3.py v7.9.0 (2025-03-12)
---------------------------

Bugfixes
~~~~~~~~

- Prevent mutating list of subscriptions when unsubscribing via the ``subscription_manager`` by iterating over a copy of the provided list. (`#3604 <https://github.com/ethereum/web3.py/issues/3604>`__)
- Batching can now be used with the AutoProvider (`#3607 <https://github.com/ethereum/web3.py/issues/3607>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update and clean up Contributing docs. (`#3610 <https://github.com/ethereum/web3.py/issues/3610>`__)


Features
~~~~~~~~

- Add ``use_text_frames`` flag for ``WebSocketProvider`` to work around websocket servers that don't support binary frames (`#3619 <https://github.com/ethereum/web3.py/issues/3619>`__)
- Sync and async support for ``eth_simulateV1`` RPC method. (`#3622 <https://github.com/ethereum/web3.py/issues/3622>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Renames a test so pytest finds it. (`#3606 <https://github.com/ethereum/web3.py/issues/3606>`__)
- Merge template, replacing ``bumpversion`` with ``bump-my-version``. (`#3610 <https://github.com/ethereum/web3.py/issues/3610>`__)
- Update integration test fixture to use latest geth version ``v1.15.5``. (`#3636 <https://github.com/ethereum/web3.py/issues/3636>`__)
- Use ``-U`` to install latest `py-geth` version for CI geth steps. This is usually a requirement if we're missing the binary for the newly-generated fixture geth version. (`#3637 <https://github.com/ethereum/web3.py/issues/3637>`__)
- Re-compile test contracts with newly released Solidity ``v0.8.29``. (`#3640 <https://github.com/ethereum/web3.py/issues/3640>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3623 <https://github.com/ethereum/web3.py/issues/3623>`__


web3.py v7.8.0 (2025-02-03)
---------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- The bugfix to match ``unsubscribe`` to ``subscribe`` for multiple subscriptions breaks the function signature for ``unsubscribe``, changing the ``subscription`` argument to ``subscriptions``. (`#3585 <https://github.com/ethereum/web3.py/issues/3585>`__)


Bugfixes
~~~~~~~~

- Handle the case when a single RPC error response is returned for a batch request, instead of always expecting a list of responses. (`#3585 <https://github.com/ethereum/web3.py/issues/3585>`__)
- Don't raise on non-unique default subscription labels (no label provided). Only raise if a non-unique custom label is explicitly set for a subscription. (`#3594 <https://github.com/ethereum/web3.py/issues/3594>`__)
- Fix bugs related to subscription manager: ``run_forever`` can start with ``0`` subscriptions and remains alive, ``unsubscribe`` accepts single or multiple subs as objects or hexstrs, ``subscribe`` for many subs returns a list of hexstr ids. (`#3595 <https://github.com/ethereum/web3.py/issues/3595>`__)
- Fix issue where ``.values()`` raised a ``KeyError`` in ``NamedTupledOnion`` (`#3596 <https://github.com/ethereum/web3.py/issues/3596>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Include ``topic`` attribute in ``ContractEvent`` docs. (`#3586 <https://github.com/ethereum/web3.py/issues/3586>`__)
- Introduce Event Subscriptions docs guide (`#3600 <https://github.com/ethereum/web3.py/issues/3600>`__)


Features
~~~~~~~~

- New ``Beacon`` and ``AsyncBeacon`` endpoints: ``get_peer_count``, ``get_attester_duties``, ``get_block_proposer_duties``, ``get_sync_committee_duties``, and ``get_attestation_rewards``. (`#3504 <https://github.com/ethereum/web3.py/issues/3504>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Move duplicate code into ``BaseContract`` class from ``Contract`` and ``AsyncContract``. (`#3579 <https://github.com/ethereum/web3.py/issues/3579>`__)
- Address flaky tests in CI runs. (`#3583 <https://github.com/ethereum/web3.py/issues/3583>`__)
- Update copyright year from 2024 to 2025 in the LICENSE file. (`#3592 <https://github.com/ethereum/web3.py/issues/3592>`__)


Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- Avoid unnecessary extra call to resolver when resolving an ENS address with no ``coin_type`` specified (default). (`#3584 <https://github.com/ethereum/web3.py/issues/3584>`__)


web3.py v7.7.0 (2025-01-15)
---------------------------

Bugfixes
~~~~~~~~

- Add a ``disconnect`` method to the AsyncHTTPProvider that closes all sessions and clears the cache (`#3557 <https://github.com/ethereum/web3.py/issues/3557>`__)
- Fix a bug related to building the ipc path for connecting to a geth ``--dev`` instance via ``web3.auto.gethdev``. (`#3576 <https://github.com/ethereum/web3.py/issues/3576>`__)


Features
~~~~~~~~

- Add a subscription manager to persistent connection providers, with support for handler methods for ``eth_subscribe`` subscriptions. (`#3554 <https://github.com/ethereum/web3.py/issues/3554>`__)
- Implement a ``topic`` property for contract events to retrieve the topic for the event. (`#3578 <https://github.com/ethereum/web3.py/issues/3578>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3546 <https://github.com/ethereum/web3.py/issues/3546>`__


Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- Improve ``AttributeDict.recursive()`` and ``AttributeDictMiddleware`` performance, effectively speeding up response processing for attrdict middleware by nearly 2x. (`#3575 <https://github.com/ethereum/web3.py/issues/3575>`__)


web3.py v7.6.1 (2024-12-18)
---------------------------

Bugfixes
~~~~~~~~

- Include an end-of-line delimiter when sending messages via IPC with the ``IPCProvider`` and ``AsyncIPCProvider``. (`#3537 <https://github.com/ethereum/web3.py/issues/3537>`__)
- Contract functions and events no longer initialize for each call. Retrieval of overloaded functions and events is now deterministic. Any ambiguity will result in an exception being raised. (`#3540 <https://github.com/ethereum/web3.py/issues/3540>`__)
- Bump the eth-tester version to one that works in the tester dependency extras (`#3555 <https://github.com/ethereum/web3.py/issues/3555>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update ENS-related links (`#3563 <https://github.com/ethereum/web3.py/issues/3563>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Upgrade Geth Fixture to 1.14.12 (`#3533 <https://github.com/ethereum/web3.py/issues/3533>`__)
- Delete ``ARCHITECTURE.md`` as unused (`#3547 <https://github.com/ethereum/web3.py/issues/3547>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3525 <https://github.com/ethereum/web3.py/issues/3525>`__


web3.py v7.6.0 (2024-11-22)
---------------------------

Bugfixes
~~~~~~~~

- Update the `ContractEvents` class to raise a `NoABIFound` exception if the `Contract` is initialized without an `ABI` and an attempt to access an event is made. This exception makes `ContractEvents` consistent with `ContractFunctions`. (`#3491 <https://github.com/ethereum/web3.py/issues/3491>`__)


Features
~~~~~~~~

- Contracts with overloaded functions or events are now supported. The Contract initializes functions and events using an identifier to distinguish between them. The identifier is the function or event signature, which consists of the name and the parameter types. (`#3491 <https://github.com/ethereum/web3.py/issues/3491>`__)
- - Support for ``w3.eth.blob_base_fee``
  - Async support for ``w3.eth.blob_base_fee`` (`#3527 <https://github.com/ethereum/web3.py/issues/3527>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Pin ``websockets<14`` due to breaking changes (`#3529 <https://github.com/ethereum/web3.py/issues/3529>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3491 <https://github.com/ethereum/web3.py/issues/3491>`__


web3.py v7.5.0 (2024-11-06)
---------------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Polish docs index page (`#3522 <https://github.com/ethereum/web3.py/issues/3522>`__)


Features
~~~~~~~~

- Add support for Geth Debug traceTransaction. (`#3334 <https://github.com/ethereum/web3.py/issues/3334>`__)
- New contract methods to obtain event elements from a contract ABI using a name, signature, selector, or topic. (`#3472 <https://github.com/ethereum/web3.py/issues/3472>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add python 3.13 support (`#3493 <https://github.com/ethereum/web3.py/issues/3493>`__)
- Compile test contracts with newly released Solidity ``v0.8.28`` to ensure compatibility. (`#3515 <https://github.com/ethereum/web3.py/issues/3515>`__)


web3.py v7.4.0 (2024-10-16)
---------------------------

Bugfixes
~~~~~~~~

- Fix a bug where CCIP-Read expected a ``{sender}`` in the url for a POST request. If ``{data}`` is missing from the url, assume a POST request is being made regardless of whether ``{sender}`` is present. (`#3291 <https://github.com/ethereum/web3.py/issues/3291>`__)
- Fix a bug where non-mainnet chains could not cache requests based on missing ``finalized`` block number. (`#3508 <https://github.com/ethereum/web3.py/issues/3508>`__)
- Send ``json``, not ``data`` with CCIP-Read POST requests. (`#3512 <https://github.com/ethereum/web3.py/issues/3512>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update the request caching documentation to clarify on when to reach for request caching and how to configure the request validation threshold for certain endpoints. (`#3508 <https://github.com/ethereum/web3.py/issues/3508>`__)


Features
~~~~~~~~

- Allow a time interval, in seconds, to be used as the ``request_cache_validation_threshold`` for request caching. Keep a list of internal default values based on the chain id for some of the bigger chains. (`#3508 <https://github.com/ethereum/web3.py/issues/3508>`__)


web3.py v7.3.1 (2024-10-14)
---------------------------

Bugfixes
~~~~~~~~

- Properly wrap ``AsyncBeacon.request_timeout`` float in a ``aiohttp.ClientTimeout`` when making requests. (`#3503 <https://github.com/ethereum/web3.py/issues/3503>`__)
- Changes related to an `eth-typing` bugfix, input types for ``ABIEvent``: ``ABIComponent`` -> ``ABIComponentIndexed``. (`#3510 <https://github.com/ethereum/web3.py/issues/3510>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix ``EthereumTesterProvider`` signature in docs, added an ``eth_tester`` example. (`#3500 <https://github.com/ethereum/web3.py/issues/3500>`__)
- Fix `pip install -e ".[dev]"` command in linux README. (`#3505 <https://github.com/ethereum/web3.py/issues/3505>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Update the ENSIP-15 to the latest spec and update the test suite. (`#3501 <https://github.com/ethereum/web3.py/issues/3501>`__)


web3.py v7.3.0 (2024-09-25)
---------------------------

Bugfixes
~~~~~~~~

- Base default ``maxFeePerGas`` calculation off of existing ``maxPriorityFeePerGas`` key instead of separate RPC call (`#3052 <https://github.com/ethereum/web3.py/issues/3052>`__)
- Add back dependency extra for 'tester'. (`#3480 <https://github.com/ethereum/web3.py/issues/3480>`__)
- Fix a bug where sensitive requests that make use of block data should not be cached until some validation threshold deems it is safe to do so, when request caching is turned on. (`#3483 <https://github.com/ethereum/web3.py/issues/3483>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update ``contract.encode_abi`` signature in docs and migration guide (`#3473 <https://github.com/ethereum/web3.py/issues/3473>`__)
- Update documentation around ``SignAndSendRawMiddlewareBuilder`` injection into the middleware onion. It should be injected lower in the stack than any middleware that modifies the transaction, in order to ensure those modified fields are signed. (`#3488 <https://github.com/ethereum/web3.py/issues/3488>`__)
- Docs cleanups related to ``test`` vs ``tester`` install extras. (`#3496 <https://github.com/ethereum/web3.py/issues/3496>`__)


Features
~~~~~~~~

- Add a configuration for request caching that sets a threshold for validating cached requests that make use of block data. This can be turned off altogether by setting the threshold to ``None``. (`#3483 <https://github.com/ethereum/web3.py/issues/3483>`__)
- Add a configuration option for the ``read_buffer_limit`` for ``AsyncIPCProvider`` in order to control the expected message size limit (defaults to 20MB). Add ``ReadBufferLimitReached`` for when the read limit is reached, extend from ``PersistentConnectionError``. (`#3492 <https://github.com/ethereum/web3.py/issues/3492>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Test warning cleanup (`#3468 <https://github.com/ethereum/web3.py/issues/3468>`__)
- Re-compile test contracts with recently released Solidity ``v0.8.27``. (`#3475 <https://github.com/ethereum/web3.py/issues/3475>`__)
- Re-organize the install extras. Re-define the ``test`` extra to always include the ``tester`` extra since it's needed for testing. (`#3495 <https://github.com/ethereum/web3.py/issues/3495>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3490 <https://github.com/ethereum/web3.py/issues/3490>`__


Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- Improve logic for reading from the async IPC socket in order to properly handle and adjust the handling of large messages. This improves reading speeds in general. (`#3492 <https://github.com/ethereum/web3.py/issues/3492>`__)


web3.py v7.2.0 (2024-08-29)
---------------------------

Bugfixes
~~~~~~~~

- Fix a bug with newer ``hexbytes`` versions that yield non-0x-prefixed hex for ``HexBytes``: ``raw_transaction.hex()`` -> ``raw_transaction.to_0x_hex()``. (`#3471 <https://github.com/ethereum/web3.py/issues/3471>`__)


Features
~~~~~~~~

- HTTPProvider and AsyncHTTPProvider's get_request_headers is now available on both the class and the instance (`#3467 <https://github.com/ethereum/web3.py/issues/3467>`__)


web3.py v7.1.0 (2024-08-28)
---------------------------

Bugfixes
~~~~~~~~

- Specify a unique ``__hash__()`` for unhashable ``Web3Middleware`` types and use this hash as the middleware onion key when a name is not provided for the middleware. This fixes a bug where different middleware were given the same name and therefore raised errors. (`#3463 <https://github.com/ethereum/web3.py/issues/3463>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix bug in filters example code (`#3455 <https://github.com/ethereum/web3.py/issues/3455>`__)
- Update ``v6`` -> ``v7`` migration guide with examples for importing and adding middleware, as well as examples on how to use the ``MiddlewareBuilder`` classes. (`#3462 <https://github.com/ethereum/web3.py/issues/3462>`__)


Features
~~~~~~~~

- Add sync and async support for beacon ``/eth/v1/beacon/blob_sidecars`` endpoint. (`#3407 <https://github.com/ethereum/web3.py/issues/3407>`__)
- Allow user to call ContractFunctions without parentheses (`#3444 <https://github.com/ethereum/web3.py/issues/3444>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Refactor and DRY up CI run setup and reduce surface area for errors. Include pre-releases in CI runs for internally maintained libraries to try and catch any conflicts. (`#3452 <https://github.com/ethereum/web3.py/issues/3452>`__)
- Bump `py-geth` to ``>=5.0.0`` from ``>=5.0.0b1`` now that stable has been released. This only matters for the ``test`` install extra (CI and dev purposes). (`#3458 <https://github.com/ethereum/web3.py/issues/3458>`__)


web3.py v7.0.0 (2024-08-21)
---------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Update `eth-utils` and `eth-typing` to latest major versions

  `eth-utils` v5 and `eth-typing` v5 (`#3450 <https://github.com/ethereum/web3.py/issues/3450>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Improve batch request documentation. (`#3448 <https://github.com/ethereum/web3.py/issues/3448>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fix Release Notes formatting (`#3454 <https://github.com/ethereum/web3.py/issues/3454>`__)


web3.py v7.0.0-beta.9 (2024-08-01)
----------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

* Upgrades to use latest ``ABI`` utilities and typings from ``eth-utils`` and ``eth-typing``.

  * Typings for ``ABI`` components are now available in the ``eth-typing`` package. ``ABI`` types previously in ``web3.types`` have been removed.
  * New versions of existing ABI functions were added to ``eth-utils`` and are now exposed in `web3.py` via ``web3.utils.abi``.
  * ABI exceptions have been renamed in ``web3.exceptions``. The ``ABIEventFunctionNotFound`` and ``FallbackNotFound`` exceptions have been removed. Use ``ABIEventNotFound`` and ``ABIFallbackNotFound`` instead.
  * ``MismatchedABI`` exceptions are raised instead of a ``Web3ValidationError`` for ABI related errors.
  * ``encode_abi`` arguments have been updated to use ``abi_element_name`` instead of ``fn_name``. (`#3408 <https://github.com/ethereum/web3.py/issues/3408>`__)

- Remove ``Web3ValidationError`` dependence / inheritance from `eth-utils` ``ValidationError``. (`#3443 <https://github.com/ethereum/web3.py/issues/3443>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Use autodoc and update ABI functions with docstrings and doctests. (`#3408 <https://github.com/ethereum/web3.py/issues/3408>`__)


Features
~~~~~~~~

* Utilities to extract function and event ``ABI`` attributes from a contract. Utilities in the ``web3.utils.abi`` module parse ABI elements and check encodability of provided arguments. ABI functions in ``eth-utils`` are exposed by the ``web3.utils.abi`` module.

  * ``get_abi_element_info`` returns an ``ABIElementInfo`` TypedDict with the ``abi``, ``selector``, and ``arguments``.
  * ``get_abi_element`` returns the ``ABI`` of a function, event, or error given the name and arguments.
  * ``check_if_arguments_can_be_encoded`` returns true if the arguments can be encoded with the given ABI.
  * ``get_event_abi`` returns the ``ABI`` of an event given the name.
  * ``get_event_log_topics`` returns the log topics of an event given the name.
  * ``log_topics_to_bytes`` returns the log topics as bytes. (`#3408 <https://github.com/ethereum/web3.py/issues/3408>`__)

- Add explicit stream kwarg to HTTPProvider so that timeout can be more finely tuned. (`#3428 <https://github.com/ethereum/web3.py/issues/3428>`__)
- Implement a ``RequestTimedOut`` exception, extending from ``Web3RPCError``, for when requests to the node time out. (`#3440 <https://github.com/ethereum/web3.py/issues/3440>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Run ``mypy`` locally using ``pre-commit`` hook, instead of within ``pre-commit`` container (`#3414 <https://github.com/ethereum/web3.py/issues/3414>`__)
- Mitigate inconsistently failing tests for CI runs with appropriate ``flaky`` or ``pytest.mark.xfail()`` decorators. (`#3440 <https://github.com/ethereum/web3.py/issues/3440>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3408 <https://github.com/ethereum/web3.py/issues/3408>`__, `#3445 <https://github.com/ethereum/web3.py/issues/3445>`__


web3.py v7.0.0-beta.8 (2024-07-24)
----------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Refactor the public ``socket`` api for persistent connection providers to properly define ``send()``, ``recv()``, and ``make_request()`` (send and wait for response) methods for interacting with the open socket. (`#3433 <https://github.com/ethereum/web3.py/issues/3433>`__)
- Format entries in ``accessList`` ``storageKeys`` to be ``HexStr`` instead of ``HexBytes`` (`#3434 <https://github.com/ethereum/web3.py/issues/3434>`__)


Bugfixes
~~~~~~~~

- Handle ``ConnectionClosedOK`` case for ``WebSocketProvider``. If a persistent connection is closed gracefully, log and raise a silent ``PersistentConnectionClosedOK`` exception, triggering an end to the message listener task and breaking out of the ``process_subscriptions()`` iterator. (`#3432 <https://github.com/ethereum/web3.py/issues/3432>`__)


Features
~~~~~~~~

- Add ``popitem()`` functionality to the ``SimpleCache`` class as well as an async utility method to wait for the next item, ``async_await_and_popitem()``. (`#3433 <https://github.com/ethereum/web3.py/issues/3433>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Refactor some common logic for persistent connection providers back into the base ``PersistentConnectionProvider`` class to reduce code duplication and improve maintainability. (`#3433 <https://github.com/ethereum/web3.py/issues/3433>`__)


web3.py v7.0.0-beta.7 (2024-06-26)
----------------------------------

Bugfixes
~~~~~~~~

- Change the ``exception_retry_configuration`` typing on http providers to be an ``Optional``, as setting this property to ``None`` effectively turns off retries on exceptions for requests. (`#3412 <https://github.com/ethereum/web3.py/issues/3412>`__)
- A bugfix, pre-release, to update the ``Beacon`` APIs (sync and async) to properly use the new ``HTTPSessionManager``. (`#3421 <https://github.com/ethereum/web3.py/issues/3421>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add an ``eth_subscribe`` example to the events guide (`#3403 <https://github.com/ethereum/web3.py/issues/3403>`__)


Features
~~~~~~~~

- Properly handle ``InsufficientDataBytes`` errors when processing receipts (`#3388 <https://github.com/ethereum/web3.py/issues/3388>`__)
- Provide explicit ``__all__`` exports for providers in `web3/providers/__init__.py`; update `web3/__init__.py` to include all provider classes including base classes. (`#3409 <https://github.com/ethereum/web3.py/issues/3409>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Re-compile test contracts with Solidity v0.8.25 to ensure compatibility. (`#3307 <https://github.com/ethereum/web3.py/issues/3307>`__)
- Increase allowable range of eth-tester: 0.11.x and 0.12.x (`#3400 <https://github.com/ethereum/web3.py/issues/3400>`__)
- Remove uses of signHash in tests, require eth-account >=0.13.0 in doctests (`#3404 <https://github.com/ethereum/web3.py/issues/3404>`__)
- Use a ``HTTPSessionManager`` to manage sessions for http providers, rather than have them share a single session manager / cache. (`#3412 <https://github.com/ethereum/web3.py/issues/3412>`__)


web3.py v7.0.0-beta.6 (2024-05-15)
----------------------------------

Bugfixes
~~~~~~~~

- Properly propagate exceptions from the message listener task to the main loop for persistent connection providers. (`#3378 <https://github.com/ethereum/web3.py/issues/3378>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Prunes the node onboarding text (`#3371 <https://github.com/ethereum/web3.py/issues/3371>`__)
- Stale example cleanup (`#3374 <https://github.com/ethereum/web3.py/issues/3374>`__)
- Merge migration guides into one page (`#3379 <https://github.com/ethereum/web3.py/issues/3379>`__)
- Simplify titles of docs guides (`#3381 <https://github.com/ethereum/web3.py/issues/3381>`__)
- Move ABI Types guide into the Troubleshooting page (`#3382 <https://github.com/ethereum/web3.py/issues/3382>`__)
- Distribute examples into relevant guides and delete Example page (`#3383 <https://github.com/ethereum/web3.py/issues/3383>`__)
- Add subscribe/unsubscribe API (`#3386 <https://github.com/ethereum/web3.py/issues/3386>`__)
- Introduces batch request API (`#3393 <https://github.com/ethereum/web3.py/issues/3393>`__)


Features
~~~~~~~~

- Add support for request batching via ``w3.batch_requests()`` context manager (sync and async). (`#3370 <https://github.com/ethereum/web3.py/issues/3370>`__)
- Allow request cache configuration on provider ``__init__()`` for all provider classes. (`#3395 <https://github.com/ethereum/web3.py/issues/3395>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Merge the python project template, notably adding python 3.12 support (`#3363 <https://github.com/ethereum/web3.py/issues/3363>`__)
- Increase python-asyncio dependency to be >=0.21.2,<0.23 (`#3369 <https://github.com/ethereum/web3.py/issues/3369>`__)
- Bump to ``mypy==1.10.0`` for ``pre-commit`` (`#3377 <https://github.com/ethereum/web3.py/issues/3377>`__)
- Move signed.rawTransaction -> signed.raw_transaction in eth module tests (`#3380 <https://github.com/ethereum/web3.py/issues/3380>`__)


web3.py v7.0.0-beta.5 (2024-04-26)
----------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Snake-case remaining arguments ``fromBlock``, ``toBlock``, and ``blockHash`` in contract and filter methods where they are passed in as kwargs. (`#3353 <https://github.com/ethereum/web3.py/issues/3353>`__)
- Employ an exponential backoff strategy using the ``backoff_factor`` in ``ExceptionRetryConfiguration`` for ``HTTPProvider`` and ``AsyncHTTPProvider``. Reduce the default initial delay to ``0.125`` seconds. (`#3358 <https://github.com/ethereum/web3.py/issues/3358>`__)
- Validate JSON-RPC responses more strictly against the JSON-RPC 2.0 specifications. ``BlockNumberOutofRange`` -> ``BlockNumberOutOfRange``. (`#3359 <https://github.com/ethereum/web3.py/issues/3359>`__)


Deprecations
~~~~~~~~~~~~

- ``messageHash`` and ``rawTransaction`` from ``eth-account`` have been deprecated for snake_case versions (`#3348 <https://github.com/ethereum/web3.py/issues/3348>`__)


Features
~~~~~~~~

- Raise ``Web3RPCError`` on JSON-RPC errors rather than ``Web3ValueError``. Raise ``MethodNotSupported`` exception when a method is not supported within *web3.py*; keep ``MethodUnavailable`` for when a method is not available on the current provider (JSON-RPC error). (`#3359 <https://github.com/ethereum/web3.py/issues/3359>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Bump ``eth-account`` dependency to ``>=0.12.2`` (`#3348 <https://github.com/ethereum/web3.py/issues/3348>`__)


Removals
~~~~~~~~

- Remove the deprecated ``personal`` namespace and all references to it. (`#3350 <https://github.com/ethereum/web3.py/issues/3350>`__)


web3.py v7.0.0-beta.4 (2024-04-11)
----------------------------------

Bugfixes
~~~~~~~~

- Fix misused call to `endpoint_uri` for all cases of ``PersistentConnectionProvider`` by being able to retrieve either the ``ipc_path`` or the ``endpoint_uri`` from the base class with ``endpoint_uri_or_ipc_path`` property. (`#3319 <https://github.com/ethereum/web3.py/issues/3319>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix ``eth_createAccessList`` docs to reflect the correct behavior. (`#3327 <https://github.com/ethereum/web3.py/issues/3327>`__)


Features
~~~~~~~~

- Use in-house exception wrappers for common Python exceptions, such as ``ValueError``, ``TypeError``, ``AttributeError``, and ``AssertionError``, for better control over exception handling. (`#3300 <https://github.com/ethereum/web3.py/issues/3300>`__)
- Add request formatter for ``maxFeePerBlobGas`` when sending blob transactions. Add formatters for ``blobGasPrice`` and ``blobGasUsed`` for *eth_getTransactionReceipt*. (`#3322 <https://github.com/ethereum/web3.py/issues/3322>`__)
- Add formatters to ensure that the result of a ``eth_createAccessList`` response can be plugged directly into an ``accessList`` in a transaction. (`#3327 <https://github.com/ethereum/web3.py/issues/3327>`__)
- Add Cancun support to ``EthereumTesterProvider``; update Cancun-related fields in some internal types. (`#3332 <https://github.com/ethereum/web3.py/issues/3332>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Use ``pre-commit`` for linting, run updated lint tools and fix errors (`#3297 <https://github.com/ethereum/web3.py/issues/3297>`__)
- Dependency updates: ``eth-abi>=5.0.1``, ``eth-account>=0.12.0`` ``eth-typing>=4.0.0`` and ``hexbytes>=1.2.0`` with relevant changes to support these. (`#3298 <https://github.com/ethereum/web3.py/issues/3298>`__)
- Remove code conditionally necessary for ``python<=3.7`` (`#3317 <https://github.com/ethereum/web3.py/issues/3317>`__)


web3.py v7.0.0-beta.3 (2024-03-28)
----------------------------------

Bugfixes
~~~~~~~~

- Fix ``process_log()`` when parsing logs for events with indexed and non-indexed inputs. ``get_event_data()`` now compares log topics and event ABIs as hex values. (`#3289 <https://github.com/ethereum/web3.py/issues/3289>`__)
- Fix ``process_log`` for ``HexStr`` inputs. Explicit type coercion of entry ``topics`` and ``data`` values. (`#3293 <https://github.com/ethereum/web3.py/issues/3293>`__)
- Fix typing for json data argument to ``eth_signTypedData``. (`#3308 <https://github.com/ethereum/web3.py/issues/3308>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add note about middlewares change to v7 migration guide. (`#3277 <https://github.com/ethereum/web3.py/issues/3277>`__)
- Rearrange v7 migration guide and include upgrade path from WebsocketProviderV2 (`#3310 <https://github.com/ethereum/web3.py/issues/3310>`__)


Features
~~~~~~~~

- Add support for ``eth_getRawTransactionByHash`` RPC method (`#3247 <https://github.com/ethereum/web3.py/issues/3247>`__)
- Add ``user_message`` kwarg for human readable ``Web3Exception`` messages. (`#3263 <https://github.com/ethereum/web3.py/issues/3263>`__)
- Add formatters for type 3 transaction fields ``maxFeePerBlobGas`` and ``blobVersionedHashes``. (`#3314 <https://github.com/ethereum/web3.py/issues/3314>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add a daily CI run (`#3272 <https://github.com/ethereum/web3.py/issues/3272>`__)
- Add linting for non-inclusive language with ``blocklint``. (`#3275 <https://github.com/ethereum/web3.py/issues/3275>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3304 <https://github.com/ethereum/web3.py/issues/3304>`__


Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- Importing ``ens._normalization`` is deferred until the first call of ``ens.utils.normalize_name`` in order to speed up ``import web3``. (`#3285 <https://github.com/ethereum/web3.py/issues/3285>`__)
- Utilize ``async`` functionality when popping responses from request manager cache for persistent connection providers. (`#3306 <https://github.com/ethereum/web3.py/issues/3306>`__)


Removals
~~~~~~~~

- Remove ``Contract.encodeABI()`` in favor of ``Contract.encode_abi()`` to follow standard conventions. (`#3281 <https://github.com/ethereum/web3.py/issues/3281>`__)


web3.py v7.0.0-beta.2 (2024-03-11)
----------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Move ``middlewares`` -> ``middleware`` (`#3276 <https://github.com/ethereum/web3.py/issues/3276>`__)


Bugfixes
~~~~~~~~

- Fix/update methods and decorators in ``web3/_utils/abi.py`` to address issues raised by ``mypy`` (`#3269 <https://github.com/ethereum/web3.py/issues/3269>`__)
- Catch all types of ``eth-abi`` ``DecodingError`` in ``EthereumTesterProvider->_make_request()`` (`#3271 <https://github.com/ethereum/web3.py/issues/3271>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Remove annual user survey prompt from docs (`#3218 <https://github.com/ethereum/web3.py/issues/3218>`__)
- Introduce feedback form banner prompt on docs (`#3253 <https://github.com/ethereum/web3.py/issues/3253>`__)
- Refresh of the middleware docs (`#3266 <https://github.com/ethereum/web3.py/issues/3266>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3259 <https://github.com/ethereum/web3.py/issues/3259>`__, `#3262 <https://github.com/ethereum/web3.py/issues/3262>`__


Removals
~~~~~~~~

- Remove the ``ethpm`` module and related docs, tests, and dependencies (`#3261 <https://github.com/ethereum/web3.py/issues/3261>`__)


web3.py v7.0.0-beta.1 (2024-02-28)
----------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Refactor the middleware setup so that request processors and response processors are separated. This will allow for more flexibility in the future and aid in the implementation of features such as batched requests. This PR also closes out a few outstanding issues and will be the start of the breaking changes for `web3.py` ``v7``. Review PR for a full list of changes. (`#3169 <https://github.com/ethereum/web3.py/issues/3169>`__)
- Use a message listener background task for ``WebsocketProviderV2`` rather than relying on ``ws.recv()`` blocking. Some breaking changes to API, notably ``listen_to_websocket`` -> ``process_subscriptions``. (`#3179 <https://github.com/ethereum/web3.py/issues/3179>`__)
- Drop dependency on ``lru-dict`` library. (`#3196 <https://github.com/ethereum/web3.py/issues/3196>`__)
- Drop support for python 3.7 (`#3198 <https://github.com/ethereum/web3.py/issues/3198>`__)
- Return iterable of ``ABIFunction``s from the ``BaseContractFunctions`` iterator. (`#3200 <https://github.com/ethereum/web3.py/issues/3200>`__)
- Name changes internal to the library related to ``v7``: ``WebsocketProvider`` -> ``LegacyWebSocketProvider``, ``WebsocketProviderV2`` -> ``WebSocketProvider`` (`#3225 <https://github.com/ethereum/web3.py/issues/3225>`__)
- ``CallOverride`` type change to ``StateOverride`` to reflect better the type name for the state override. ``eth_call`` is also not the only method with this param, making the name more generic. (`#3227 <https://github.com/ethereum/web3.py/issues/3227>`__)
- Rename `beacon/main.py` -> `beacon/beacon.py` (`#3233 <https://github.com/ethereum/web3.py/issues/3233>`__)
- ``EthereumTesterProvider`` now returns ``input`` for `eth_getTransaction*` for better consistency with JSON-RPC spec. (`#3235 <https://github.com/ethereum/web3.py/issues/3235>`__)
- Change the signature for the async version of ``wait_for_transaction_receipt()`` to use ``Optional[float]`` instead of ``float``. (`#3237 <https://github.com/ethereum/web3.py/issues/3237>`__)
- ``get_default_ipc_path()`` and ``get_dev_ipc_path()`` now return the path value without checking if the ``geth.ipc`` file exists. (`#3245 <https://github.com/ethereum/web3.py/issues/3245>`__)


Bugfixes
~~~~~~~~

- Fix return type of ``AsyncContract.constructor`` (`#3192 <https://github.com/ethereum/web3.py/issues/3192>`__)
- Handle new geth errors related to waiting for a transaction receipt while transactions are still being indexed. (`#3216 <https://github.com/ethereum/web3.py/issues/3216>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Documentation was updated to reflect early changes to ``v7`` from ``v6``. A ``v6`` -> ``v7`` migration guide was also started and will be added to as ``v7`` breaking changes are introduced. (`#3211 <https://github.com/ethereum/web3.py/issues/3211>`__)
- Remove ENS v6 breaking change warning from v7 (`#3254 <https://github.com/ethereum/web3.py/issues/3254>`__)


Features
~~~~~~~~

- Add AsyncIPCProvider (`#2984 <https://github.com/ethereum/web3.py/issues/2984>`__)
- Implement ``state_override`` parameter for ``eth_estimateGas`` method. (`#3164 <https://github.com/ethereum/web3.py/issues/3164>`__)
- Upgrade `eth-tester` to ``v0.10.0-b.1`` and turn on ``eth_feeHistory`` support for ``EthereumTesterProvider``. (`#3172 <https://github.com/ethereum/web3.py/issues/3172>`__)
- Add formatters for new ``Cancun`` network upgrade block header fields: ``blobGasUsed``, ``excessBlobGas``, and ``parentBeaconBlockRoot``. (`#3223 <https://github.com/ethereum/web3.py/issues/3223>`__)
- Contract event ``get_logs`` results sorted by each ``ContractEvent`` ``logIndex``. (`#3228 <https://github.com/ethereum/web3.py/issues/3228>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Create test fixture for latest ``geth`` version. Run tests with ``geth`` in ``--dev`` mode. (`#3191 <https://github.com/ethereum/web3.py/issues/3191>`__)
- Validate geth version used to generate the integration test fixture against the version in the binary that is used to run the tests. (`#3193 <https://github.com/ethereum/web3.py/issues/3193>`__)
- Internal change to ``WebsocketProviderV2`` before release: raise exceptions in message listener task by default; opting to silence them via a flag. (`#3202 <https://github.com/ethereum/web3.py/issues/3202>`__)
- Compile contracts with and test against new Solidity version ``v0.8.24``. (`#3204 <https://github.com/ethereum/web3.py/issues/3204>`__)
- Formatting updates for ``black==24.1.0``. (`#3207 <https://github.com/ethereum/web3.py/issues/3207>`__)
- Allow HTTP provider request retry configuration to be turned off appropriately. Internal change since ``v7`` has not yet been released. (`#3211 <https://github.com/ethereum/web3.py/issues/3211>`__)
- Upgraded geth fixture version (`#3231 <https://github.com/ethereum/web3.py/issues/3231>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#2964 <https://github.com/ethereum/web3.py/issues/2964>`__, `#3248 <https://github.com/ethereum/web3.py/issues/3248>`__


Performance Improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- Remove call to ``parse_block_identifier`` when initializing ``ContractCaller`` functions. (`#3257 <https://github.com/ethereum/web3.py/issues/3257>`__)


Removals
~~~~~~~~

- ``normalize_request_parameters`` middleware was in a stale state and not being used or tested. This middleware has been removed. (`#3211 <https://github.com/ethereum/web3.py/issues/3211>`__)
- Remove deprecated ``geth.miner`` namespace and methods. (`#3236 <https://github.com/ethereum/web3.py/issues/3236>`__)


web3.py v6.14.0 (2024-01-10)
----------------------------

Bugfixes
~~~~~~~~

- Change ``fee_history`` default behavior. If ``reward_percentiles`` arg not included, pass it to the provider as an empty list instead of ``None``. (`#3185 <https://github.com/ethereum/web3.py/issues/3185>`__)
- Use ``importlib.metadata`` for version info if python>=3.8 (`#3187 <https://github.com/ethereum/web3.py/issues/3187>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Remove docs reference for removed ``protocol_version`` RPC method (`#3183 <https://github.com/ethereum/web3.py/issues/3183>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Re-define how async vs sync core test suites are ran. (`#3180 <https://github.com/ethereum/web3.py/issues/3180>`__)
- Add basic import and version tests for the ``web3`` module (`#3187 <https://github.com/ethereum/web3.py/issues/3187>`__)


web3.py v6.13.0 (2023-12-20)
----------------------------

Features
~~~~~~~~

- Implement async ``eth_createAccessList`` RPC method to create an EIP-2930 access list. (`#3167 <https://github.com/ethereum/web3.py/issues/3167>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add flaky async Geth integration tests to CI (`#3170 <https://github.com/ethereum/web3.py/issues/3170>`__)
- Fix wrong test reference for ``EthereumTesterProvider`` integration test suite. (`#3171 <https://github.com/ethereum/web3.py/issues/3171>`__)
- Small fix for integration tests for ``tox`` to recognize independent patterns for each test run. (`#3173 <https://github.com/ethereum/web3.py/issues/3173>`__)


web3.py v6.12.0 (2023-12-11)
----------------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Make downloadable versions of docs available in ``pdf``, ``htmlzip``, and ``epub`` formats (`#3153 <https://github.com/ethereum/web3.py/issues/3153>`__)
- Add 2023 user survey fine art banner in the docs (`#3159 <https://github.com/ethereum/web3.py/issues/3159>`__)
- Polish the community resources docs page (`#3162 <https://github.com/ethereum/web3.py/issues/3162>`__)


Features
~~~~~~~~

- Implement ``createAccessList`` RPC endpoint to create an EIP-2930 access list. (`#2381 <https://github.com/ethereum/web3.py/issues/2381>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Run flaky eth-tester tests on CI (`#3157 <https://github.com/ethereum/web3.py/issues/3157>`__)
- Pin ``pytest-asyncio`` dependency to <0.23 (`#3160 <https://github.com/ethereum/web3.py/issues/3160>`__)


web3.py v6.11.4 (2023-11-27)
----------------------------

Bugfixes
~~~~~~~~

- Fix collision of ``w3`` variable when initializing contract with function of the same name (`#3147 <https://github.com/ethereum/web3.py/issues/3147>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3148 <https://github.com/ethereum/web3.py/issues/3148>`__


web3.py v6.11.3 (2023-11-08)
----------------------------

Bugfixes
~~~~~~~~

- When coming back through the middleware onion after a request is made, we have the response ``id``. Use it to match to the cached request information and process the response accordingly. (`#3140 <https://github.com/ethereum/web3.py/issues/3140>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Adds Discord bot template repo to Resources page (`#3143 <https://github.com/ethereum/web3.py/issues/3143>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Additional contract ``abi`` documentation to make it a clear requirement for contract instances. (`#2539 <https://github.com/ethereum/web3.py/issues/2539>`__)
- Fix type annotations for ``web3`` constants. (`#3138 <https://github.com/ethereum/web3.py/issues/3138>`__)
- Add upper pin to deprecated dependency ``lru-dict`` whose new minor version release introduced a typing issue with CI lint builds. (`#3144 <https://github.com/ethereum/web3.py/issues/3144>`__)
- Recompile test contracts with new Solidity version ``v0.8.23`` to ensure compatibility. (`#3146 <https://github.com/ethereum/web3.py/issues/3146>`__)


web3.py v6.11.2 (2023-10-30)
----------------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix formatting in documentation for creating an account. (`#3128 <https://github.com/ethereum/web3.py/issues/3128>`__)
- Fix broken links for Apeworx and Sepolia faucet (`#3130 <https://github.com/ethereum/web3.py/issues/3130>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Speed up the core test suite by splitting up sync and async tests. This reduces the CI build times to ~8min from ~12min. (`#3111 <https://github.com/ethereum/web3.py/issues/3111>`__)
- Re-compile test contracts with Solidity ``v0.8.22`` to ensure compatibility with this latest Solidity version. (`#3134 <https://github.com/ethereum/web3.py/issues/3134>`__)
- Improvements on yielding to the event loop while searching in response caches and calling ``recv()`` on the websocket connection for ``WebSocketProviderV2``. (`#3135 <https://github.com/ethereum/web3.py/issues/3135>`__)


web3.py v6.11.1 (2023-10-18)
----------------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update ``WebsocketProviderV2`` documentation. Document a general overview of the ``RequestProcessor`` class and its internal caches. (`#3125 <https://github.com/ethereum/web3.py/issues/3125>`__)


Features
~~~~~~~~

- Properly define an ``__await__()`` method on the ``_PersistentConnectionWeb3`` class so a persistent connection may be initialized using the ``await`` pattern. Integration tests added for initializing the persistent connection using the ``await`` pattern. (`#3125 <https://github.com/ethereum/web3.py/issues/3125>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Updates and refactoring for the ``WebsocketProviderV2`` class and its internal supporting classes and logic. Separation of one-to-one and one-to-many request responses. Storing of one-to-many responses in a ``deque`` and one-to-one responses in a ``SimpleCache`` class. Provide an async lock around the websocket ``recv()``. (`#3125 <https://github.com/ethereum/web3.py/issues/3125>`__)
- Add upper pin to ``hexbytes`` dependency to due incoming breaking change (`#3127 <https://github.com/ethereum/web3.py/issues/3127>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#3114 <https://github.com/ethereum/web3.py/issues/3114>`__, `#3129 <https://github.com/ethereum/web3.py/issues/3129>`__


web3.py v6.11.0 (2023-10-11)
----------------------------

Breaking Changes (to Beta APIs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Refactor the async iterator pattern for message streams from the websocket connection for ``WebsocketProviderV2`` to a proper async iterator. This allows for a more natural usage of the iterator pattern and mimics the behavior of the underlying ``websockets`` library. (`#3116 <https://github.com/ethereum/web3.py/issues/3116>`__)


Bugfixes
~~~~~~~~

- Use hashes to compare equality of two ``AttributeDict`` classes (`#3104 <https://github.com/ethereum/web3.py/issues/3104>`__)
- Fix issues with formatting middleware, such as ``async_geth_poa_middleware`` and subscription responses for ``WebsocketProviderV2``. (`#3116 <https://github.com/ethereum/web3.py/issues/3116>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Change ``docker-compose`` to ``docker compose`` in the Contributing docs examples. (`#3107 <https://github.com/ethereum/web3.py/issues/3107>`__)
- Updates to the ``WebsocketProviderV2`` documentation async iterator example for iterating over a persistent stream of messages from the websocket connection via ``async for``. (`#3116 <https://github.com/ethereum/web3.py/issues/3116>`__)
- Update outdated node and private key management verbiage. (`#3117 <https://github.com/ethereum/web3.py/issues/3117>`__)


Features
~~~~~~~~

- Allow passing in a ``float`` for a ``request_timeout`` for requests for the ``Beacon`` class. Update some Beacon API endpoints (sync and async). (`#3106 <https://github.com/ethereum/web3.py/issues/3106>`__)
- Add ``allow_list`` kwarg for ``exception_retry_middleware`` to allow for a custom list of RPC endpoints. Add a sleep between retries and a customizable ``backoff_factor`` to control the sleep time between retry attempts. (`#3120 <https://github.com/ethereum/web3.py/issues/3120>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Refactor logic for the ``input_munger()`` method on the ``Method`` class. (`#2987 <https://github.com/ethereum/web3.py/issues/2987>`__)
- Pin mypy to v1.4.1, the last to support py37 (`#3122 <https://github.com/ethereum/web3.py/issues/3122>`__)


web3.py v6.10.0 (2023-09-21)
----------------------------

Breaking Changes (to Beta APIs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Breaking change to the API for interacting with a persistent websocket connection via ``AsyncWeb3`` and ``WebsocketProviderV2``. This change internalizes the ``provider.ws`` property and opts for a ``w3.ws`` API achieved via a new ``WebsocketConnection`` class. With these changes, ``eth_subscription`` messages now return the subscription id as the ``subscription`` param and the formatted message as the ``result`` param. (`#3096 <https://github.com/ethereum/web3.py/issues/3096>`__)


Bugfixes
~~~~~~~~

- Return `w3.eth.gas_price` when calculating time based gas price strategy for an empty chain. (`#1149 <https://github.com/ethereum/web3.py/issues/1149>`__)
- Update `LogReceipt` and `TxReceipt` declarations. Remove `LogReceipt`'s `payload` and `topic` attributes. Refactor `LogEntry` to `LogReceipt`. (`#3043 <https://github.com/ethereum/web3.py/issues/3043>`__)
- Fixes ``AsyncEth.max_priority_fee_per_gas``. It wasn't falling back to ``eth_feeHistory`` since the ``MethodUnavailable`` error was introduced. (`#3084 <https://github.com/ethereum/web3.py/issues/3084>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update ``WebsocketProviderV2`` documentation to reflect the new public websocket API via the ``WebsocketConnection`` class. (`#3096 <https://github.com/ethereum/web3.py/issues/3096>`__)


Features
~~~~~~~~

- Improved error messaging for exceptions from malformed JSON-RPC responses. (`#3053 <https://github.com/ethereum/web3.py/issues/3053>`__)
- Enable filtering by non-indexed arguments for contract event ``get_logs()``. (`#3078 <https://github.com/ethereum/web3.py/issues/3078>`__)
- Add ``eth_maxPriorityFeePerGas`` to ``exception_retry_middleware`` whitelist (`#3090 <https://github.com/ethereum/web3.py/issues/3090>`__)
- Sync responses for ``WebsocketProviderV2`` open connections with requests via matching RPC ``id`` values. (`#3096 <https://github.com/ethereum/web3.py/issues/3096>`__)
- Properly JSON encode ``AttributeDict``, ``bytes``, and ``HexBytes`` when sending a JSON-RPC request by utilizing the in-house ``Web3JsonEncoder`` class. (`#3101 <https://github.com/ethereum/web3.py/issues/3101>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fix an issue with an IPC test present only on MacOSX. (`#929 <https://github.com/ethereum/web3.py/issues/929>`__)
- Ignore flake8 rule F401 (unused import) in all ``__init__.py`` files (`#3097 <https://github.com/ethereum/web3.py/issues/3097>`__)


web3.py v6.9.0 (2023-08-23)
---------------------------

Bugfixes
~~~~~~~~

- Fix the type for ``input`` in ``TxData`` from ``HexStr`` -> ``HexBytes``. (`#3074 <https://github.com/ethereum/web3.py/issues/3074>`__)
- Fix an issue with ``WebsocketProviderV2`` when responses to a request aren't found in the cache (``None`` values). (`#3075 <https://github.com/ethereum/web3.py/issues/3075>`__)
- Re-expose some websockets constants found in ``web3.providers.websocket.websocket`` via ``web3.providers.websocket``. (`#3076 <https://github.com/ethereum/web3.py/issues/3076>`__)
- Return ``NotImplemented`` constant, rather than raising ``NotImplementedError`` for ``NamedElementOnion.__add__()``, based on Python standards. (`#3080 <https://github.com/ethereum/web3.py/issues/3080>`__)
- Only release ``async_lock`` if it's locked to begin with. (`#3083 <https://github.com/ethereum/web3.py/issues/3083>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add MEV blocking tutorial to Resources docs page (`#3072 <https://github.com/ethereum/web3.py/issues/3072>`__)
- Fix documentation around current state of ``get_logs()`` usage and arguments. (`#3073 <https://github.com/ethereum/web3.py/issues/3073>`__)
- Add an Ape hackathon kit to Resources documentation page (`#3082 <https://github.com/ethereum/web3.py/issues/3082>`__)


web3.py v6.8.0 (2023-08-02)
---------------------------

Bugfixes
~~~~~~~~

- Fix the type for the optional param asking for "full transactions" when subscribing to ``newPendingTransactions`` via ``eth_subscribe`` to ``bool``. (`#3067 <https://github.com/ethereum/web3.py/issues/3067>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Change docs to reflect AsyncHTTPProvider does accept ENS names now (`#3070 <https://github.com/ethereum/web3.py/issues/3070>`__)


Features
~~~~~~~~

- Return structured JSON-RPC errors for missing or unimplemented eth-tester methods. (`#3061 <https://github.com/ethereum/web3.py/issues/3061>`__)
- ENS name-to-address support for ``eth_subscribe``. (`#3066 <https://github.com/ethereum/web3.py/issues/3066>`__)
- Asynchronous iterator support for ``AsyncWeb3`` with ``WebsocketProviderV2`` using ``async for`` syntax. (`#3067 <https://github.com/ethereum/web3.py/issues/3067>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Minor fixes to type hinting in the core tests setup fixtures. (`#3069 <https://github.com/ethereum/web3.py/issues/3069>`__)


web3.py v6.7.0 (2023-07-26)
---------------------------

Bugfixes
~~~~~~~~

- Test wheel build in separate directory and virtualenv (`#3046 <https://github.com/ethereum/web3.py/issues/3046>`__)
- Handle case where data gets returned as ``None`` in a JSON-RPC error response (`#3054 <https://github.com/ethereum/web3.py/issues/3054>`__)
- Fixed default windows IPC provider path to work with python 3.11 (`#3058 <https://github.com/ethereum/web3.py/issues/3058>`__)
- Fix return type for ``rpc_gas_price_strategy`` to ``int`` but also only convert the ``strategy_based_gas_price`` to ``hex`` if it is an ``int`` in the ``gas_price_strategy_middleware``. (`#3065 <https://github.com/ethereum/web3.py/issues/3065>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add note to Release Notes about v5 end-of-life and v6.6.0 yank (`#3045 <https://github.com/ethereum/web3.py/issues/3045>`__)
- Add documentation for ``WebsocketProviderV2`` (beta). (`#3048 <https://github.com/ethereum/web3.py/issues/3048>`__)


Features
~~~~~~~~

- Add ENSIP-9 (Multichain Address Resolution) support for ``address()`` and ``setup_address()`` for ``ENS`` and ``AsyncENS`` classes. (`#3030 <https://github.com/ethereum/web3.py/issues/3030>`__)
- Support for ``eth_subscribe`` and ``eth_unsubscribe`` methods has been added with the introduction of a new websocket provider, ``WebsocketProviderV2``. (`#3048 <https://github.com/ethereum/web3.py/issues/3048>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added recursive typing to ``ABIFunctionComponents`` type (`#3063 <https://github.com/ethereum/web3.py/issues/3063>`__)
- Upgrade eth-tester requirement to v0.9.0-b.1 (`#3064 <https://github.com/ethereum/web3.py/issues/3064>`__)


web3.py v6.6.1 (2023-07-12)
---------------------------

Bugfixes
~~~~~~~~

- Add ``ens/specs`` to MANIFEST.in (`#3039 <https://github.com/ethereum/web3.py/issues/3039>`__)


web3.py v6.6.0 (2023-07-12)
---------------------------

**Note: This release was missing the required ``ens/specs`` directory, so it was yanked
from Pypi in favor of v6.6.1**

Breaking Changes
~~~~~~~~~~~~~~~~

- ENS name normalization now uses ENSIP-15 by default. This is technically a breaking change introduced by ENS but, according to ENSIP-15, 99% of existing names should be unaffected. (`#3024 <https://github.com/ethereum/web3.py/issues/3024>`__)


Bugfixes
~~~~~~~~

- Handle ``None`` in the formatting middleware (`#2546 <https://github.com/ethereum/web3.py/issues/2546>`__)
- Fix for a possible bug in ``construct_sign_and_send_raw_middleware`` where the signed transaction was sent as bytes and expected to be converted to hex by formatting later on. It is now explicitly sent as the hex string hash within the middleware. (`#2936 <https://github.com/ethereum/web3.py/issues/2936>`__)
- Fixes ``max_priority_fee_per_gas``. It wasn't falling back to ``eth_feeHistory`` since the ``MethodUnavailable`` error was introduced. (`#3002 <https://github.com/ethereum/web3.py/issues/3002>`__)
- Properly initialize logger in ``AsyncHTTPProvider``. (`#3026 <https://github.com/ethereum/web3.py/issues/3026>`__)
- Fix ``AsyncWeb3.solidity_keccak`` to match ``Web3.solidity_keccak``. (`#3034 <https://github.com/ethereum/web3.py/issues/3034>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Replaced transaction examples with unused account addresses. (`#2011 <https://github.com/ethereum/web3.py/issues/2011>`__)
- Removed obsolete docs for camelCase miner methods and ``deploy`` (`#2039 <https://github.com/ethereum/web3.py/issues/2039>`__)
- Update documentation relating to ENS only being available on mainnet. ENS is available on all networks where the ENS contracts are deployed. (`#3012 <https://github.com/ethereum/web3.py/issues/3012>`__)
- Add first steps section and tidy up learning resources (`#3013 <https://github.com/ethereum/web3.py/issues/3013>`__)
- Replace references to ``jasoncarver.eth`` with ``ens.eth``. (`#3020 <https://github.com/ethereum/web3.py/issues/3020>`__)
- Adds "Hackathon Helpers" section to Resources page (`#3035 <https://github.com/ethereum/web3.py/issues/3035>`__)


Features
~~~~~~~~

- Update ENS Resolver ABI (`#1839 <https://github.com/ethereum/web3.py/issues/1839>`__)
- ``async_http_retry_request_middleware``, an async http request retry middleware for ``AsyncHTTPProvider``. (`#3009 <https://github.com/ethereum/web3.py/issues/3009>`__)
- Add ``eth_getStorageAt()`` support for ``EthereumTesterProvider``. (`#3011 <https://github.com/ethereum/web3.py/issues/3011>`__)
- Add async support for ENS name-to-address resolution via ``async_name_to_address_middleware``. (`#3012 <https://github.com/ethereum/web3.py/issues/3012>`__)
- Add async support for the sign-and-send raw transaction middleware via ``construct_async_sign_and_send_raw_middleware()``. (`#3025 <https://github.com/ethereum/web3.py/issues/3025>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Remove some warnings from test output (`#2991 <https://github.com/ethereum/web3.py/issues/2991>`__)
- Introduced the logic for ENSIP-15 ENS name normalization. Originally this was done via a flag in this PR but changed to the default behavior in #3024 before release. (`#3000 <https://github.com/ethereum/web3.py/issues/3000>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#2997 <https://github.com/ethereum/web3.py/issues/2997>`__, `#3011 <https://github.com/ethereum/web3.py/issues/3011>`__, `#3023 <https://github.com/ethereum/web3.py/issues/3023>`__, `#3037 <https://github.com/ethereum/web3.py/issues/3037>`__


Removals
~~~~~~~~

- Removed references to deprecated middlewares with new tests to check default middlewares (`#2972 <https://github.com/ethereum/web3.py/issues/2972>`__)


web3.py v6.5.0 (2023-06-15)
---------------------------

Bugfixes
~~~~~~~~

- Properly create a fresh cache for each instance of ``simple_cache_middleware`` if no cache is provided. Fixes a bug when using this middleware with multiple instances of ``Web3``. (`#2979 <https://github.com/ethereum/web3.py/issues/2979>`__)
- Fix potential race condition when writing cache entries in ``simple_cache_middleware`` (`#2981 <https://github.com/ethereum/web3.py/issues/2981>`__)
- Catch ``UnicodeDecodeError`` for contract revert messages that cannot be decoded and issue a warning instead, raising a ``ContractLogicError`` with the raw ``data`` from the response. (`#2989 <https://github.com/ethereum/web3.py/issues/2989>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Introduces resources page to documentation (`#2957 <https://github.com/ethereum/web3.py/issues/2957>`__)
- Completed docstrings for ``ContractFunction`` and ``AsyncContractFunction`` classes (`#2960 <https://github.com/ethereum/web3.py/issues/2960>`__)
- Added 'unsupported by any current clients' note to the ``Eth.sign_typed_data`` docs (`#2961 <https://github.com/ethereum/web3.py/issues/2961>`__)
- Removed list of ``AsyncHTTPProvider``-supported methods, it supports them all now (`#2962 <https://github.com/ethereum/web3.py/issues/2962>`__)
- Modernize the filtering guide, emphasizing ``get_logs`` (`#2968 <https://github.com/ethereum/web3.py/issues/2968>`__)
- Removed references to defunct providers in ``IPCProvider`` docs (`#2971 <https://github.com/ethereum/web3.py/issues/2971>`__)
- Update Matomo analytics script to move to cloud services (`#2978 <https://github.com/ethereum/web3.py/issues/2978>`__)


Features
~~~~~~~~

- Add the ``sign_typed_data`` method to the ``AsyncEth`` class (`#2920 <https://github.com/ethereum/web3.py/issues/2920>`__)
- Add support for Solidity ``Panic`` errors, available since Solidity 0.8.0. Raises ``ContractPanicError`` with appropriate messaging based on the known panic error codes. (`#2986 <https://github.com/ethereum/web3.py/issues/2986>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``lint-roll`` - dropped ``isort`` ``--recursive`` flag, not needed as of their ``v5``, added black (`#2930 <https://github.com/ethereum/web3.py/issues/2930>`__)
- Moved ``ethpm`` deprecation warning to only show when the module is explicitly enabled (`#2983 <https://github.com/ethereum/web3.py/issues/2983>`__)
- Update make release to check remote upstream is pointing to ethereum/web3.py. (`#2988 <https://github.com/ethereum/web3.py/issues/2988>`__)
- Removed `pluggy` from dev requirements (`#2992 <https://github.com/ethereum/web3.py/issues/2992>`__)


Miscellaneous Changes
~~~~~~~~~~~~~~~~~~~~~

- `#2960 <https://github.com/ethereum/web3.py/issues/2960>`__, `#2965 <https://github.com/ethereum/web3.py/issues/2965>`__


web3.py v6.4.0 (2023-05-15)
---------------------------

Bugfixes
~~~~~~~~

- fix AttributeDicts unhashable if they contain lists recursively tupleizing them (`#2908 <https://github.com/ethereum/web3.py/issues/2908>`__)


Deprecations
~~~~~~~~~~~~

- add deprecation notice for the `ethPM` module (`#2953 <https://github.com/ethereum/web3.py/issues/2953>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- remove reference to the ability to specify a list of providers - you can't anymore (`#2949 <https://github.com/ethereum/web3.py/issues/2949>`__)
- add deprecation notice for the `ethPM` module (`#2953 <https://github.com/ethereum/web3.py/issues/2953>`__)


Features
~~~~~~~~

- Update ``eth-tester`` to pull in Shanghai changes and make additional changes to fully support Shanghai with ``eth-tester``. (`#2958 <https://github.com/ethereum/web3.py/issues/2958>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- bump sphinx and readthedocs py versions (`#2945 <https://github.com/ethereum/web3.py/issues/2945>`__)
- re-compile test contracts with Solidity ``v0.8.20`` (`#2951 <https://github.com/ethereum/web3.py/issues/2951>`__)
- Set towncrier settings in `pyproject.toml` to match the python project template and change newfragment type "doc" to "docs" (`#2959 <https://github.com/ethereum/web3.py/issues/2959>`__)


v6.3.0 (2023-05-03)
-------------------

Features
~~~~~~~~

- Add support for custom revert errors (`#2795 <https://github.com/ethereum/web3.py/issues/2795>`__)
- Add the ``modify_transaction`` method to the ``AsyncEth`` class (`#2825 <https://github.com/ethereum/web3.py/issues/2825>`__)
- add show_traceback flag to is_connected to allow user to see connection error reason (`#2912 <https://github.com/ethereum/web3.py/issues/2912>`__)
- Add a ``data`` attribute on the ``ContractLogicError`` class that returns raw data returned by the node. (`#2922 <https://github.com/ethereum/web3.py/issues/2922>`__)
- Add support via result formatters for ``reward`` type trace actions on tracing calls. (`#2929 <https://github.com/ethereum/web3.py/issues/2929>`__)


Bugfixes
~~~~~~~~

- Typing was being ignored for the ``get_ipc_path`` and ``get_dev_ipc_path`` functions because of a missing ``None`` return. Those two methods now explicitly return ``None`` and have an ``Optional`` in their type definition. (`#2917 <https://github.com/ethereum/web3.py/issues/2917>`__)
- fix AsyncEventFilterBuilder looking for Web3 instead of AsyncWeb3 (`#2931 <https://github.com/ethereum/web3.py/issues/2931>`__)
- Add check for null withdrawal field on get_block response (`#2941 <https://github.com/ethereum/web3.py/issues/2941>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add a decision tree guide for sending transactions (`#2919 <https://github.com/ethereum/web3.py/issues/2919>`__)
- Update references to master branch (`#2933 <https://github.com/ethereum/web3.py/issues/2933>`__)
- Cleanup Quickstart guide and next steps (`#2935 <https://github.com/ethereum/web3.py/issues/2935>`__)
- Cleanup Overview page links and context (`#2938 <https://github.com/ethereum/web3.py/issues/2938>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added ``build`` to towncrier commands in Makefile (`#2915 <https://github.com/ethereum/web3.py/issues/2915>`__)
- Update win wheel CI builds to use ``python -m tox -r`` instead of specifying the ``tox`` executable directly. (`#2923 <https://github.com/ethereum/web3.py/issues/2923>`__)
- update pip and tox install on CI containers (`#2927 <https://github.com/ethereum/web3.py/issues/2927>`__)


v6.2.0 (2023-04-12)
-------------------

Features
~~~~~~~~

- Adds async version of `eth_getUncleCount` methods (`#2822 <https://github.com/ethereum/web3.py/issues/2822>`__)
- Add the ``sign_transaction`` method to the ``AsyncEth`` class (`#2827 <https://github.com/ethereum/web3.py/issues/2827>`__)
- Add the ``replace_transaction`` method to the ``AsyncEth`` class (`#2847 <https://github.com/ethereum/web3.py/issues/2847>`__)


Bugfixes
~~~~~~~~

- Use ``TraceFilterParams`` instead of ``FilterParams`` for ``trace_filter`` typing (`#2913 <https://github.com/ethereum/web3.py/issues/2913>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add welcome banner for Ethereum newcomers (`#2905 <https://github.com/ethereum/web3.py/issues/2905>`__)
- Added breaking changes from pr2448 to v6 migration guide (`#2907 <https://github.com/ethereum/web3.py/issues/2907>`__)


v6.1.0 (2023-04-05)
-------------------

Features
~~~~~~~~

- Add tracing functionality back in via the ``tracing`` module, add formatters for human-readable input and output, and attach this module to ``Web3`` on init / make it a default module. (`#2851 <https://github.com/ethereum/web3.py/issues/2851>`__)
- Add result formatters for ``withdrawals_root`` and ``withdrawals`` as part of ``Shanghai`` hard fork support. (`#2868 <https://github.com/ethereum/web3.py/issues/2868>`__)
- add eth_chainId to exception_retry_middleware whitelist (`#2892 <https://github.com/ethereum/web3.py/issues/2892>`__)


Bugfixes
~~~~~~~~

- Mark `test_async_eth_sign` with `@pytest.mark.asyncio` (`#2858 <https://github.com/ethereum/web3.py/issues/2858>`__)
- fix readthedocs broken version selector (`#2883 <https://github.com/ethereum/web3.py/issues/2883>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- remove camelCased method deprecation notices from web3.eth docs (`#2882 <https://github.com/ethereum/web3.py/issues/2882>`__)
- Add doc blurb about multiple HTTPProviders with the same URL (`#2889 <https://github.com/ethereum/web3.py/issues/2889>`__)
- fix styling and external link formatting (`#2897 <https://github.com/ethereum/web3.py/issues/2897>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Bump pytest from 6.2.5 to 7+ because of CI ``DeprecationWarning`` (`#2863 <https://github.com/ethereum/web3.py/issues/2863>`__)
- Require eth-abi v4 stable (`#2886 <https://github.com/ethereum/web3.py/issues/2886>`__)
- remove unused docs dependencies and bump version of remaining (`#2890 <https://github.com/ethereum/web3.py/issues/2890>`__)
- Update go-ethereum integration test fixture to use the latest version of geth - ``v1.11.5``. (`#2896 <https://github.com/ethereum/web3.py/issues/2896>`__)
- Update ``geth_steps`` in CircleCI builds to pip install the proper version of ``py-geth``. (`#2898 <https://github.com/ethereum/web3.py/issues/2898>`__)
- Update CircleCI windows orb path since it now uses python 3.11. (`#2899 <https://github.com/ethereum/web3.py/issues/2899>`__)
- Bump go version used in CI jobs that install and run go-ethereum and parameterize the version in circleci config file for ease of configuration. (`#2900 <https://github.com/ethereum/web3.py/issues/2900>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#2887 <https://github.com/ethereum/web3.py/issues/2887>`__


v6.0.0 (2023-03-14)
-------------------

Bugfixes
~~~~~~~~

- fix dict_to_namedtuple unable to handle empty dict as input (`#2867
  <https://github.com/ethereum/web3.py/issues/2867>`__)


v6.0.0-beta.11 (2023-02-24)
---------------------------

Features
~~~~~~~~

- Add the ``sign`` method to the ``AsyncEth`` class (`#2833
  <https://github.com/ethereum/web3.py/issues/2833>`__)


Bugfixes
~~~~~~~~

- More accurately define the ``eth_call`` return type as ``HexBytes`` since the
  response is converted to ``HexBytes`` in the pythonic formatters and there
  are differences between ``HexBytes`` and ``bytes`` types. (`#2842
  <https://github.com/ethereum/web3.py/issues/2842>`__)
- Set default block_identifier in ContractFunction.call() to None (`#2846
  <https://github.com/ethereum/web3.py/issues/2846>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Remove unused module lines to instantiate the AsyncHTTPProvider (`#2789
  <https://github.com/ethereum/web3.py/issues/2789>`__)
- Typos fix in docs (`#2817
  <https://github.com/ethereum/web3.py/issues/2817>`__)
- Add/cleanup docs for the ``AsyncHTTPProvider`` in light of the new
  ``AsyncWeb3`` class (`#2821
  <https://github.com/ethereum/web3.py/issues/2821>`__)
- Remove user survey banner following close of survey (`#2831
  <https://github.com/ethereum/web3.py/issues/2831>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Do not invoke ``setup.py`` directly; use ``python -m build`` where
  appropriate. (`#2714 <https://github.com/ethereum/web3.py/issues/2714>`__)
- clean up ignored unused imports (`#2838
  <https://github.com/ethereum/web3.py/issues/2838>`__)
- Recompile test contracts with the new Solidity version ``0.8.19``. (`#2840
  <https://github.com/ethereum/web3.py/issues/2840>`__)
- Update ``py-geth`` version and re-generate integration test fixture with geth
  ``v1.11.2``. (`#2841 <https://github.com/ethereum/web3.py/issues/2841>`__)


Breaking changes
~~~~~~~~~~~~~~~~

- Use ``AsyncWeb3`` class and preserve typing for the async api calls. (`#2819
  <https://github.com/ethereum/web3.py/issues/2819>`__)
- Fix typing for ``CallOverrideParams`` and add proper request formatters for
  call state overrides. (`#2843
  <https://github.com/ethereum/web3.py/issues/2843>`__)
- Remove python warning and doc notes related to unstable async providers.
  (`#2845 <https://github.com/ethereum/web3.py/issues/2845>`__)


v6.0.0-beta.10 (2023-02-15)
---------------------------

Features
~~~~~~~~

- add decode_tuples option to contract instantiation (`#2799
  <https://github.com/ethereum/web3.py/issues/2799>`__)


Bugfixes
~~~~~~~~

- Fix ``ethpm`` import issues after making ``ipfshttpclient`` optional. (`#2775
  <https://github.com/ethereum/web3.py/issues/2775>`__)
- Fix for recently-broken ``eth-tester`` exception message parsing for some
  exception cases. (`#2783
  <https://github.com/ethereum/web3.py/issues/2783>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Added a v6 Migraion Guide (`#2778
  <https://github.com/ethereum/web3.py/issues/2778>`__)
- Rebrand the library to lowercase "web3.py" (`#2804
  <https://github.com/ethereum/web3.py/issues/2804>`__)
- remove references to Rinkeby or replace with Goerli (`#2815
  <https://github.com/ethereum/web3.py/issues/2815>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Organize the ``eth`` module into separate files for better readability.
  (`#2753 <https://github.com/ethereum/web3.py/issues/2753>`__)
- Rename the newly-split ``eth`` module files to match convention. (`#2772
  <https://github.com/ethereum/web3.py/issues/2772>`__)
- Re-compile all test contracts with latest Solidity version. Refactor test
  fixtures. Adds a script that compiles all test contracts to the same
  directory with selected Solidity version. (`#2797
  <https://github.com/ethereum/web3.py/issues/2797>`__)
- Updates to ``isort`` and ``black`` required some formatting changes and isort
  config refactoring. (`#2802
  <https://github.com/ethereum/web3.py/issues/2802>`__)
- Compile test contracts using newly-released Solidity version ``0.8.18``.
  (`#2803 <https://github.com/ethereum/web3.py/issues/2803>`__)


Breaking changes
~~~~~~~~~~~~~~~~

- All exceptions inherit from a custom class. EthPM exceptions inherit from
  EthPMException, ENS exceptions inherit from ENSException, and all other
  web3.py exceptions inherit from Web3Exception (`#1478
  <https://github.com/ethereum/web3.py/issues/1478>`__)
- Reorganized contract to contract.py, async_contract.py, base_contract.py and
  utils.py. In this change there was a small breaking change where the
  constructor of BaseContractCaller contract_function_class was defaulting to a
  ContractFunction now there is no default. This was done to separate the base
  class from the implementation. (`#2567
  <https://github.com/ethereum/web3.py/issues/2567>`__)
- When calling a contract, use ``w3.eth.default_block`` if no block_identifier
  is specified instead of ``latest``. (`#2777
  <https://github.com/ethereum/web3.py/issues/2777>`__)
- Strict bytes type checking is now default for ``web3.py``. This change also
  adds a boolean flag on the ``Web3`` class for turning this feature on and
  off, as well as a flag on the ``ENS`` class for control over a standalone
  ``ENS`` instance. (`#2788
  <https://github.com/ethereum/web3.py/issues/2788>`__)
- When a method is not supported by a node provider, raise a MethodUnavailable
  error instead of the generic ValueError. (`#2796
  <https://github.com/ethereum/web3.py/issues/2796>`__)
- ``dict`` to ``AttributeDict`` conversion is no longer a default result
  formatter. This conversion is now done via a default middleware that may be
  removed. (`#2805 <https://github.com/ethereum/web3.py/issues/2805>`__)
- Removed deprecated ``manager.request_async`` and associated methods. (`#2810
  <https://github.com/ethereum/web3.py/issues/2810>`__)
- removed Rinkeby from list of allowed chains in EthPM (`#2815
  <https://github.com/ethereum/web3.py/issues/2815>`__)


v6.0.0-beta.9 (2023-01-03)
--------------------------

Features
~~~~~~~~

- Add async ``w3.eth.get_block_transaction_count`` (`#2687
  <https://github.com/ethereum/web3.py/issues/2687>`__)
- Support Python 3.11 (`#2699
  <https://github.com/ethereum/web3.py/issues/2699>`__)
- Load the ``AsyncHTTPProvider`` with default async middleware and default
  async modules, just as the ``HTTPProvider``. (`#2736
  <https://github.com/ethereum/web3.py/issues/2736>`__)
- Add support for Nethermind/Gnosis revert reason formatting (`#2739
  <https://github.com/ethereum/web3.py/issues/2739>`__)
- Added async functionality to filter (`#2744
  <https://github.com/ethereum/web3.py/issues/2744>`__)
- Get contract address from ``CREATE`` and ``CREATE2`` opcodes (`#2762
  <https://github.com/ethereum/web3.py/issues/2762>`__)


Bugfixes
~~~~~~~~

- Fixing abi encoding for multidimensional arrays. (`#2764
  <https://github.com/ethereum/web3.py/issues/2764>`__)


Performance improvements
~~~~~~~~~~~~~~~~~~~~~~~~

- Some minor performance improvements to the ``SimpleCache`` class and simple
  cache middlewares (sync and async). (`#2719
  <https://github.com/ethereum/web3.py/issues/2719>`__)
- Remove unnecessary ``await`` for ``generate_gas_price()`` method as it does
  not need to be awaited. Move this method to ``BaseEth`` to be used directly
  by both ``Eth`` and ``AsyncEth`` modules. (`#2735
  <https://github.com/ethereum/web3.py/issues/2735>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add user survey to docs banner (`#2720
  <https://github.com/ethereum/web3.py/issues/2720>`__)
- Document improvements for private key info and account funding. (`#2722
  <https://github.com/ethereum/web3.py/issues/2722>`__)
- Include eth-tester install note in quickstart (`#2755
  <https://github.com/ethereum/web3.py/issues/2755>`__)


Deprecations and Removals
~~~~~~~~~~~~~~~~~~~~~~~~~

- Removal of Infura auto provider support. (`#2706
  <https://github.com/ethereum/web3.py/issues/2706>`__)
- Removal of ``version`` module. (`#2729
  <https://github.com/ethereum/web3.py/issues/2729>`__)
- Remove already-deprecated ``start_rpc`` and ``stop_rpc`` from the
  ``w3.geth.admin`` module. (`#2731
  <https://github.com/ethereum/web3.py/issues/2731>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Use regex pattern for ``black`` command for ``tox`` / ``make lint`` linting
  commands. (`#2727 <https://github.com/ethereum/web3.py/issues/2727>`__)
- Use regex pattern for ``mypy`` command for ``tox`` / ``make lint`` linting
  commands. (`#2734 <https://github.com/ethereum/web3.py/issues/2734>`__)
- Remove internal method ``apply_formatter_to_array`` and use the method with
  the same name from the ``eth-utils`` library. (`#2737
  <https://github.com/ethereum/web3.py/issues/2737>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#2751 <https://github.com/ethereum/web3.py/issues/2751>`__


Breaking changes
~~~~~~~~~~~~~~~~

- Snakecase the processReceipt, processLog, createFilter, and getLogs methods
  (`#2709 <https://github.com/ethereum/web3.py/issues/2709>`__)
- Remove Parity module and references. (`#2718
  <https://github.com/ethereum/web3.py/issues/2718>`__)
- Make the ``ipfshttpclient`` library opt-in via a web3 install extra. This
  only affects the ``ethpm`` ``ipfs`` backends, which rely on the library.
  (`#2730 <https://github.com/ethereum/web3.py/issues/2730>`__)


v6.0.0-beta.8 (2022-11-14)
--------------------------

Features
~~~~~~~~

- Async support for caching certain methods via
  ``async_simple_cache_middleware`` as well as constructing custom async
  caching middleware via ``async_construct_simple_cache_middleware``.
  ``SimpleCache`` class was also added to the public ``utils`` module. (`#2579
  <https://github.com/ethereum/web3.py/issues/2579>`__)
- Remove upper pins on dependencies (`#2648
  <https://github.com/ethereum/web3.py/issues/2648>`__)
- Async support for beacon api. (`#2689
  <https://github.com/ethereum/web3.py/issues/2689>`__)
- If the loop for a cached async session is closed, or the session itself was
  closed, create a new session at that cache key and properly close and evict
  the stale session. (`#2713
  <https://github.com/ethereum/web3.py/issues/2713>`__)


Bugfixes
~~~~~~~~

- bump `sphinx_rtd_theme` version to fix missing unordered list bullets (`#2688
  <https://github.com/ethereum/web3.py/issues/2688>`__)
- Fix bug to generate unique cache keys when multi-threading & with unique
  event loops for async. (`#2690
  <https://github.com/ethereum/web3.py/issues/2690>`__)
- Properly release ``async_lock`` for session requests if an exception is
  raised during a task. (`#2695
  <https://github.com/ethereum/web3.py/issues/2695>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- move definition of RTD install requirements file from their dashboard into
  `.readthedocs.yml`, and remove unused `sphinx-better-theme` from requirements
  (`#2688 <https://github.com/ethereum/web3.py/issues/2688>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#2690 <https://github.com/ethereum/web3.py/issues/2690>`__, `#2694
  <https://github.com/ethereum/web3.py/issues/2694>`__


Breaking changes
~~~~~~~~~~~~~~~~

- Remove support for dictionary-based caches, for simple-cache-middleware, in
  favor of the internal ``SimpleCache`` class. (`#2579
  <https://github.com/ethereum/web3.py/issues/2579>`__)
- Snakecase the clientVersion method (`#2686
  <https://github.com/ethereum/web3.py/issues/2686>`__)
- change instances of `createFilter` to `create_filter` (`#2692
  <https://github.com/ethereum/web3.py/issues/2692>`__)
- Remove ``SolidityError`` in favor of ``ContractLogicError`` (`#2697
  <https://github.com/ethereum/web3.py/issues/2697>`__)
- Snakecase the solidityKeccak method (`#2702
  <https://github.com/ethereum/web3.py/issues/2702>`__)
- Snakecase the fromWeb3 method (`#2703
  <https://github.com/ethereum/web3.py/issues/2703>`__)
- Snakecase the toBytes, toHex, toInt, toJSON, and toText methods (`#2707
  <https://github.com/ethereum/web3.py/issues/2707>`__)
- Snakecase the toAddress, isChecksumAddress, and toChecksumAddress methods
  (`#2708 <https://github.com/ethereum/web3.py/issues/2708>`__)


v6.0.0-beta.7 (2022-10-19)
--------------------------

Bugfixes
~~~~~~~~

- Protobuf dependency had a DoS-able bug. It was fixed in v4.21.6. See:
  https://nvd.nist.gov/vuln/detail/CVE-2022-1941 (`#2666
  <https://github.com/ethereum/web3.py/issues/2666>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Added Chainstack link to quickstart docs. (`#2677
  <https://github.com/ethereum/web3.py/issues/2677>`__)


Deprecations and Removals
~~~~~~~~~~~~~~~~~~~~~~~~~

- Remove Ropsten auto provider and the relevant references to Ropsten across
  the repo (`#2672 <https://github.com/ethereum/web3.py/issues/2672>`__)


Internal Changes - for web3.py Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Clean up remaining uses of deprecated ``eth_abi`` methods. (`#2668
  <https://github.com/ethereum/web3.py/issues/2668>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#2671 <https://github.com/ethereum/web3.py/issues/2671>`__, `#2682
  <https://github.com/ethereum/web3.py/issues/2682>`__


v6.0.0-beta.6 (2022-09-26)
--------------------------

Bugfixes
~~~~~~~~

- Protobuf dependency breaks at version ``3.20.2`` and above; pin to ``3.20.1``
  for now. (`#2657 <https://github.com/ethereum/web3.py/issues/2657>`__)


Features
~~~~~~~~

- Add new predefined block identifiers ``safe`` and ``finalized``. (`#2652
  <https://github.com/ethereum/web3.py/issues/2652>`__)


v6.0.0-beta.5 (2022-09-19)
--------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Removed IBAN since it was an unused feature (`#2537
  <https://github.com/ethereum/web3.py/issues/2537>`__)
- Update eth-tester dependency to v0.7.0-beta.1; Update eth-account version to
  >=0.7.0,<0.8.0 (`#2623 <https://github.com/ethereum/web3.py/issues/2623>`__)
- Remove ``WEB3_INFURA_API_KEY`` environment variable in favor of
  ``WEB3_INFURA_PROJECT_ID``. Change ``InfuraKeyNotFound`` exception to
  ``InfuraProjectIdNotFound`` (`#2634
  <https://github.com/ethereum/web3.py/issues/2634>`__)
- Remove Kovan auto provider (`#2635
  <https://github.com/ethereum/web3.py/issues/2635>`__)
- Snakecase the `isConnected` method (`#2643
  <https://github.com/ethereum/web3.py/issues/2643>`__)
- Snakecase the ``toWei`` and ``fromWei`` methods (`#2647
  <https://github.com/ethereum/web3.py/issues/2647>`__)


Bugfixes
~~~~~~~~

- Fix ``eth-tester`` key remapping for ``logsBloom`` and ``receiptsRoot``
  (`#1630 <https://github.com/ethereum/web3.py/issues/1630>`__)
- Improve upon issues with session caching - better support for multithreading
  and make sure session eviction from cache does not happen prematurely.
  (`#2409 <https://github.com/ethereum/web3.py/issues/2409>`__)
- Allow classes to inherit from the ``Web3`` class by attaching modules
  appropriately. (`#2592 <https://github.com/ethereum/web3.py/issues/2592>`__)
- fixed bug in how async_eth_tester_middleware fills default fields (`#2600
  <https://github.com/ethereum/web3.py/issues/2600>`__)
- Allow hex for ``value`` field when validating via ``validate_payable()``
  contracts method (`#2602
  <https://github.com/ethereum/web3.py/issues/2602>`__)
- Update Beacon API to v2.3.0 (`#2616
  <https://github.com/ethereum/web3.py/issues/2616>`__)
- Move ``flaky`` option to top-level conftest.py (`#2642
  <https://github.com/ethereum/web3.py/issues/2642>`__)


Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

- Update Proof of Authority middleware (`geth_poa_middleware`) documentation
  for better clarity. (`#2538
  <https://github.com/ethereum/web3.py/issues/2538>`__)
- Add some missing supported async middlewares to docs. (`#2574
  <https://github.com/ethereum/web3.py/issues/2574>`__)
- Introduce AsyncENS and availability on w3 instance in ENS guide. (`#2585
  <https://github.com/ethereum/web3.py/issues/2585>`__)
- Fix typo in eth.call docs (`#2613
  <https://github.com/ethereum/web3.py/issues/2613>`__)
- remove section for deleted `account.recoverHash` method (`#2615
  <https://github.com/ethereum/web3.py/issues/2615>`__)
- examples docs gave incorrect return type for `eth.get_transaction`, fixed
  (`#2617 <https://github.com/ethereum/web3.py/issues/2617>`__)
- minor typo fix in contracts overview (`#2628
  <https://github.com/ethereum/web3.py/issues/2628>`__)
- fix bug in `Deploying new contracts` example (`#2646
  <https://github.com/ethereum/web3.py/issues/2646>`__)


Features
~~~~~~~~

- Support for ``Account`` class access in ``AsyncEth`` via
  ``async_w3.eth.account`` (`#2580
  <https://github.com/ethereum/web3.py/issues/2580>`__)
- Expose public abi utility methods: ``get_abi_output_names()`` and
  ``get_abi_input_names()`` (`#2596
  <https://github.com/ethereum/web3.py/issues/2596>`__)
- update all references to deprecated `eth_abi.encode_abi` to `eth_abi.encode`
  (`#2621 <https://github.com/ethereum/web3.py/issues/2621>`__)
- update all references to deprecated `eth_abi.decode_abi` to `eth_abi.decode`
  (`#2636 <https://github.com/ethereum/web3.py/issues/2636>`__)
- Add Sepolia auto provider (`#2639
  <https://github.com/ethereum/web3.py/issues/2639>`__)


Misc
~~~~

- `#2603 <https://github.com/ethereum/web3.py/issues/2603>`__, `#2622
  <https://github.com/ethereum/web3.py/issues/2622>`__, `#2630
  <https://github.com/ethereum/web3.py/issues/2630>`__, `#2638
  <https://github.com/ethereum/web3.py/issues/2638>`__


v6.0.0-beta.4 (2022-07-13)
--------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- sha3 and soliditySha3 were previously deprecated and now removed (`#2479
  <https://github.com/ethereum/web3.py/issues/2479>`__)
- Remove deprecated methods from Geth, Parity and Net modules (`#2480
  <https://github.com/ethereum/web3.py/issues/2480>`__)
- Provide better messaging to wrong arguments for contract functions,
  especially for ``tuple`` argument types. (`#2556
  <https://github.com/ethereum/web3.py/issues/2556>`__)


Bugfixes
~~~~~~~~

- Properly format ``block_number`` for ``eth_getTransactionCount`` when using
  ``EthereumTesterProvider`` (`#1801
  <https://github.com/ethereum/web3.py/issues/1801>`__)
- removed `Optional` type hints for `passphrase` arguments that aren't actually
  optional (`#2511 <https://github.com/ethereum/web3.py/issues/2511>`__)
- Fix `is_dynamic_fee_transaction` and `TRANSACTION_DEFAULTS` when
  `gas_price_strategy` returns zero (`#2562
  <https://github.com/ethereum/web3.py/issues/2562>`__)


Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

- Remove deprecated methods from Geth, Parity, and Net modules (`#2480
  <https://github.com/ethereum/web3.py/issues/2480>`__)
- replace double- with single-quotes to make f-string valid (`#2504
  <https://github.com/ethereum/web3.py/issues/2504>`__)
- added geth personal_sign and personal_ec_recover documentation (`#2511
  <https://github.com/ethereum/web3.py/issues/2511>`__)


Features
~~~~~~~~

- Add transaction result formatters for `type` and `chainId` to convert values
  to ``int`` if ``hexadecimal`` if the field is not null (`#2491
  <https://github.com/ethereum/web3.py/issues/2491>`__)
- Add a global flag on the provider for enabling / disabling CCIP Read for
  calls: ``global_ccip_read_enabled`` (defaults to ``True``). (`#2499
  <https://github.com/ethereum/web3.py/issues/2499>`__)
- Deprecate Geth Admin StartRPC and StopRPC for StartHTTP and StopHTTP (`#2507
  <https://github.com/ethereum/web3.py/issues/2507>`__)
- Added Async support for ENS (`#2547
  <https://github.com/ethereum/web3.py/issues/2547>`__)
- support multi-dimensional arrays for ABI tuples types (`#2555
  <https://github.com/ethereum/web3.py/issues/2555>`__)


Misc
~~~~

- `#2345 <https://github.com/ethereum/web3.py/issues/2345>`__, `#2483
  <https://github.com/ethereum/web3.py/issues/2483>`__, `#2505
  <https://github.com/ethereum/web3.py/issues/2505>`__, `#2513
  <https://github.com/ethereum/web3.py/issues/2513>`__, `#2514
  <https://github.com/ethereum/web3.py/issues/2514>`__, `#2515
  <https://github.com/ethereum/web3.py/issues/2515>`__, `#2516
  <https://github.com/ethereum/web3.py/issues/2516>`__, `#2518
  <https://github.com/ethereum/web3.py/issues/2518>`__, `#2520
  <https://github.com/ethereum/web3.py/issues/2520>`__, `#2521
  <https://github.com/ethereum/web3.py/issues/2521>`__, `#2522
  <https://github.com/ethereum/web3.py/issues/2522>`__, `#2523
  <https://github.com/ethereum/web3.py/issues/2523>`__, `#2524
  <https://github.com/ethereum/web3.py/issues/2524>`__, `#2525
  <https://github.com/ethereum/web3.py/issues/2525>`__, `#2527
  <https://github.com/ethereum/web3.py/issues/2527>`__, `#2530
  <https://github.com/ethereum/web3.py/issues/2530>`__, `#2531
  <https://github.com/ethereum/web3.py/issues/2531>`__, `#2534
  <https://github.com/ethereum/web3.py/issues/2534>`__, `#2542
  <https://github.com/ethereum/web3.py/issues/2542>`__, `#2544
  <https://github.com/ethereum/web3.py/issues/2544>`__, `#2550
  <https://github.com/ethereum/web3.py/issues/2550>`__, `#2551
  <https://github.com/ethereum/web3.py/issues/2551>`__, `#2559
  <https://github.com/ethereum/web3.py/issues/2559>`__


v6.0.0-beta.3 (2022-06-01)
--------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Removed deprecated methods from eth and geth (`#1416
  <https://github.com/ethereum/web3.py/issues/1416>`__)


Bugfixes
~~~~~~~~

- Fix bug in _is_latest_block_number_request in cache middleware (`#2185
  <https://github.com/ethereum/web3.py/issues/2185>`__)
- Increase cache size to allow for 20 entries. (`#2477
  <https://github.com/ethereum/web3.py/issues/2477>`__)
- format receipt.type to int and log.data to HexBytes (`#2482
  <https://github.com/ethereum/web3.py/issues/2482>`__)
- Only thread lock for methods attempting to access the cache for caching
  middleware. (`#2496 <https://github.com/ethereum/web3.py/issues/2496>`__)


Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

- Fix typo in simple_cache_middleware example (`#2449
  <https://github.com/ethereum/web3.py/issues/2449>`__)
- Fix dict type hints in EventScanner example (`#2469
  <https://github.com/ethereum/web3.py/issues/2469>`__)
- Add clarification around ValueError and Local Signing middleware (`#2474
  <https://github.com/ethereum/web3.py/issues/2474>`__)


Features
~~~~~~~~

- Add async version of contract functionality (`#2270
  <https://github.com/ethereum/web3.py/issues/2270>`__)
- ENSIP-10 / wildcard resolution support for ENS module (`#2411
  <https://github.com/ethereum/web3.py/issues/2411>`__)
- CCIP Read support and finalize implementation of and add tests for ENS
  offchain resolution support (`#2457
  <https://github.com/ethereum/web3.py/issues/2457>`__)


Misc
~~~~

- `#2454 <https://github.com/ethereum/web3.py/issues/2454>`__, `#2450
  <https://github.com/ethereum/web3.py/issues/2450>`__, `#2462
  <https://github.com/ethereum/web3.py/issues/2462>`__, `#2471
  <https://github.com/ethereum/web3.py/issues/2471>`__, `#2478
  <https://github.com/ethereum/web3.py/issues/2478>`__


v6.0.0-beta.2 (2022-04-27)
--------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Audit ``.rst`` and ``.py`` files and convert all Web3 instance variable names
  to ``w3`` to avoid confusion with the ``web3`` module. (`#1183
  <https://github.com/ethereum/web3.py/issues/1183>`__)
- Update dependency requirements: - eth-utils - eth-abi - eth-tester -
  eth-account - eth-typing (`#2342
  <https://github.com/ethereum/web3.py/issues/2342>`__)
- Add ``attach_methods()`` to ``Module`` class to facilitate attaching methods
  to modules. (`#2383 <https://github.com/ethereum/web3.py/issues/2383>`__)
- Move IOError -> OSError (`#2434
  <https://github.com/ethereum/web3.py/issues/2434>`__)


Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

- Clarify info about Infura filters over HTTP (`#2322
  <https://github.com/ethereum/web3.py/issues/2322>`__)
- Document reading private keys from environment variables (`#2380
  <https://github.com/ethereum/web3.py/issues/2380>`__)
- Add example for the ``construct_sign_and_send_raw_middleware`` when connected
  to a hosted node (`#2410
  <https://github.com/ethereum/web3.py/issues/2410>`__)
- Doc fix: Pending transaction filter returns a ``TransactionFilter`` not a
  ``BlockFilter`` (`#2444 <https://github.com/ethereum/web3.py/issues/2444>`__)


Features
~~~~~~~~

- Add 'get_text' method to look up ENS text record values (`#2286
  <https://github.com/ethereum/web3.py/issues/2286>`__)
- For ``ENS.name()``, validate that the forward resolution returns the same
  address as provided by the user as per the ENS documentation recommendation
  for Reverse Resolution. (`#2420
  <https://github.com/ethereum/web3.py/issues/2420>`__)
- Add sync chain_id to ``simple_middleware_cache`` (`#2425
  <https://github.com/ethereum/web3.py/issues/2425>`__)


Misc
~~~~

- `#2369 <https://github.com/ethereum/web3.py/issues/2369>`__, `#2372
  <https://github.com/ethereum/web3.py/issues/2372>`__, `#2418
  <https://github.com/ethereum/web3.py/issues/2418>`__


v6.0.0-beta.1 (2022-02-28)
--------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Update ``websockets`` dependency to v10+ (`#2324
  <https://github.com/ethereum/web3.py/issues/2324>`__)
- Remove support for the unsupported Python 3.6 Also removes outdated Parity
  tests (`#2343 <https://github.com/ethereum/web3.py/issues/2343>`__)
- Update Sphinx requirement to ``>=4.2.0,<5`` (`#2362
  <https://github.com/ethereum/web3.py/issues/2362>`__)


Bugfixes
~~~~~~~~

- Fix types for ``gas``, and ``gasLimit``: ``Wei -> int``. Also fix types for
  ``effectiveGasPrice``: (``int -> Wei``) (`#2330
  <https://github.com/ethereum/web3.py/issues/2330>`__)


Features
~~~~~~~~

- Added session caching to the AsyncHTTPProvider (`#2016
  <https://github.com/ethereum/web3.py/issues/2016>`__)
- Add support for Python 3.10 (`#2175
  <https://github.com/ethereum/web3.py/issues/2175>`__)
- Added 'Breaking Changes' and 'Deprecations' categories to our release notes
  (`#2340 <https://github.com/ethereum/web3.py/issues/2340>`__)
- Add async `eth.get_storage_at` method (`#2350
  <https://github.com/ethereum/web3.py/issues/2350>`__)
- Upgrade ``jsonschema`` version to ``>=4.0.0<5`` (`#2361
  <https://github.com/ethereum/web3.py/issues/2361>`__)


Misc
~~~~

- `#2353 <https://github.com/ethereum/web3.py/issues/2353>`__, `#2365
  <https://github.com/ethereum/web3.py/issues/2365>`__


v5.28.0 (2022-02-09)
--------------------

Features
~~~~~~~~

- Added Async functions for Geth Personal and Admin modules (`#1413
  <https://github.com/ethereum/web3.py/issues/1413>`__)
- async support for formatting, validation, and geth poa middlewares (`#2098
  <https://github.com/ethereum/web3.py/issues/2098>`__)
- Calculate a default ``maxPriorityFeePerGas`` using ``eth_feeHistory`` when
  ``eth_maxPriorityFeePerGas`` is not available, since the latter is not a part
  of the Ethereum JSON-RPC specs and only supported by certain clients. (`#2259
  <https://github.com/ethereum/web3.py/issues/2259>`__)
- Allow NamedTuples in ABI inputs (`#2312
  <https://github.com/ethereum/web3.py/issues/2312>`__)
- Add async `eth.syncing` method (`#2331
  <https://github.com/ethereum/web3.py/issues/2331>`__)


Bugfixes
~~~~~~~~

- remove `ens.utils.dict_copy` decorator (`#1423
  <https://github.com/ethereum/web3.py/issues/1423>`__)
- The exception retry middleware whitelist was missing a comma between
  ``txpool`` and ``testing`` (`#2327
  <https://github.com/ethereum/web3.py/issues/2327>`__)
- Properly initialize external modules that do not inherit from the
  ``web3.module.Module`` class (`#2328
  <https://github.com/ethereum/web3.py/issues/2328>`__)


v5.27.0 (2022-01-31)
--------------------

Features
~~~~~~~~

- Added Async functions for Geth TxPool (`#1413
  <https://github.com/ethereum/web3.py/issues/1413>`__)
- external modules are no longer required to inherit from the
  ``web3.module.Module`` class (`#2304
  <https://github.com/ethereum/web3.py/issues/2304>`__)
- Add async `eth.get_logs` method (`#2310
  <https://github.com/ethereum/web3.py/issues/2310>`__)
- add Async access to `default_account` and `default_block` (`#2315
  <https://github.com/ethereum/web3.py/issues/2315>`__)
- Update eth-tester and eth-account dependencies to pull in bugfix from
  eth-keys (`#2320 <https://github.com/ethereum/web3.py/issues/2320>`__)


Bugfixes
~~~~~~~~

- Fixed issues with parsing tuples and nested tuples in event logs (`#2211
  <https://github.com/ethereum/web3.py/issues/2211>`__)
- In ENS the contract function to resolve an ENS address was being called twice
  in error. One of those calls was removed. (`#2318
  <https://github.com/ethereum/web3.py/issues/2318>`__)
- ``to_hexbytes`` block formatters no longer throw when value is ``None``
  (`#2321 <https://github.com/ethereum/web3.py/issues/2321>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- fix typo in `eth.account` docs (`#2111
  <https://github.com/ethereum/web3.py/issues/2111>`__)
- explicitly add `output_values` to contracts example (`#2293
  <https://github.com/ethereum/web3.py/issues/2293>`__)
- update imports for `AsyncHTTPProvider` sample code (`#2302
  <https://github.com/ethereum/web3.py/issues/2302>`__)
- fixed broken link to filter schema (`#2303
  <https://github.com/ethereum/web3.py/issues/2303>`__)
- add github link to the main docs landing page (`#2313
  <https://github.com/ethereum/web3.py/issues/2313>`__)
- fix typos and update referenced `geth` version (`#2326
  <https://github.com/ethereum/web3.py/issues/2326>`__)


Misc
~~~~

- `#2217 <https://github.com/ethereum/web3.py/issues/2217>`__


v5.26.0 (2022-01-06)
--------------------

Features
~~~~~~~~

- Add ``middlewares`` property to ``NamedElementOnion`` /
  ``web3.middleware_onion``. Returns current middlewares in proper order for
  importing into a new ``Web3`` instance (`#2239
  <https://github.com/ethereum/web3.py/issues/2239>`__)
- Add async ``eth.hashrate`` method (`#2243
  <https://github.com/ethereum/web3.py/issues/2243>`__)
- Add async ``eth.chain_id`` method (`#2251
  <https://github.com/ethereum/web3.py/issues/2251>`__)
- Add async ``eth.mining`` method (`#2252
  <https://github.com/ethereum/web3.py/issues/2252>`__)
- Add async ``eth.get_transaction_receipt`` and
  ``eth.wait_for_transaction_receipt`` methods (`#2265
  <https://github.com/ethereum/web3.py/issues/2265>`__)
- Add async `eth.accounts` method (`#2284
  <https://github.com/ethereum/web3.py/issues/2284>`__)
- Support for attaching external modules to the ``Web3`` instance when
  instantiating the ``Web3`` instance, via the ``external_modules`` argument,
  or via the new ``attach_modules()`` method (`#2288
  <https://github.com/ethereum/web3.py/issues/2288>`__)


Bugfixes
~~~~~~~~

- Fixed doctest that wasn't running in ``docs/contracts.rst`` (`#2213
  <https://github.com/ethereum/web3.py/issues/2213>`__)
- Key mapping fix to eth-tester middleware for access list storage keys (`#2224
  <https://github.com/ethereum/web3.py/issues/2224>`__)
- Inherit ``Web3`` instance middlewares when instantiating ``ENS`` with
  ``ENS.fromWeb3()`` method (`#2239
  <https://github.com/ethereum/web3.py/issues/2239>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix example docs to show a TransactionNotFound error, instead of None (`#2199
  <https://github.com/ethereum/web3.py/issues/2199>`__)
- fix typo in ethpm.rst (`#2277
  <https://github.com/ethereum/web3.py/issues/2277>`__)
- Clarify provider usage in Quickstart docs (`#2287
  <https://github.com/ethereum/web3.py/issues/2287>`__)
- Address common BSC usage question (`#2289
  <https://github.com/ethereum/web3.py/issues/2289>`__)


Misc
~~~~

- `#1729 <https://github.com/ethereum/web3.py/issues/1729>`__, `#2233
  <https://github.com/ethereum/web3.py/issues/2233>`__, `#2242
  <https://github.com/ethereum/web3.py/issues/2242>`__, `#2260
  <https://github.com/ethereum/web3.py/issues/2260>`__, `#2261
  <https://github.com/ethereum/web3.py/issues/2261>`__, `#2283
  <https://github.com/ethereum/web3.py/issues/2283>`__


v5.25.0 (2021-11-19)
--------------------

Features
~~~~~~~~

- Support for ``w3.eth.get_raw_transaction_by_block``, and async support for
  ``w3.eth.get_raw_transaction_by_block`` (`#2209
  <https://github.com/ethereum/web3.py/issues/2209>`__)


Bugfixes
~~~~~~~~

- BadResponseFormat error thrown instead of KeyError when a response gets sent
  back without a ``result`` key. (`#2188
  <https://github.com/ethereum/web3.py/issues/2188>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Correct link to Websocket library documentation (`#2173
  <https://github.com/ethereum/web3.py/issues/2173>`__)
- Doc update to make it clearer that enable_unstable_package_management()
  method is on the web3 instance (`#2208
  <https://github.com/ethereum/web3.py/issues/2208>`__)


Misc
~~~~

- `#2102 <https://github.com/ethereum/web3.py/issues/2102>`__, `#2179
  <https://github.com/ethereum/web3.py/issues/2179>`__, `#2191
  <https://github.com/ethereum/web3.py/issues/2191>`__, `#2201
  <https://github.com/ethereum/web3.py/issues/2201>`__, `#2205
  <https://github.com/ethereum/web3.py/issues/2205>`__, `#2212
  <https://github.com/ethereum/web3.py/issues/2212>`__


v5.24.0 (2021-09-27)
--------------------

Features
~~~~~~~~

- Add async ``eth.send_raw_transaction`` method (`#2135
  <https://github.com/ethereum/web3.py/issues/2135>`__)
- Updated eth-account version to v0.5.6 - adds support for signing typed
  transactions without needing to explicitly set the transaction type and now
  accepts correct JSON-RPC structure for accessList for typed transactions
  (`#2157 <https://github.com/ethereum/web3.py/issues/2157>`__)


Bugfixes
~~~~~~~~

- Encode block_count as hex before making eth_feeHistory RPC call (`#2117
  <https://github.com/ethereum/web3.py/issues/2117>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix typo in AsyncHTTPProvider docs (`#2131
  <https://github.com/ethereum/web3.py/issues/2131>`__)
- Update AsyncHTTPProvider doc Supported Methods to include
  ``web3.eth.send_raw_transaction()``. (`#2135
  <https://github.com/ethereum/web3.py/issues/2135>`__)
- Improve messaging around usage and implementation questions, directing users
  to the appropriate channel (`#2138
  <https://github.com/ethereum/web3.py/issues/2138>`__)
- Clarify some contract ``ValueError`` error messages. (`#2146
  <https://github.com/ethereum/web3.py/issues/2146>`__)
- Updated docs for w3.eth.account.sign_transaction to reflect that transaction
  type is no longer needed to successfully sign typed transactions and to
  illustrate how to structure an optional accessList parameter in a typed
  transaction (`#2157 <https://github.com/ethereum/web3.py/issues/2157>`__)


Misc
~~~~

- `#2105 <https://github.com/ethereum/web3.py/issues/2105>`__


v5.23.1 (2021-08-27)
--------------------

Features
~~~~~~~~

- Add constants for the zero address, zero hash, max int, and wei per ether. (`#2109 <https://github.com/ethereum/web3.py/issues/2109>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Renamed "1559 transaction" to "dynamic fee transaction" where appropriate to keep consistency among the general code base for 1559 transaction (type=2) naming (`#2118 <https://github.com/ethereum/web3.py/issues/2118>`__)
- Update AsyncHTTPProvider doc example to include modules and middlewares keyword arguments (`#2123 <https://github.com/ethereum/web3.py/issues/2123>`__)


Misc
~~~~

- `#2110 <https://github.com/ethereum/web3.py/issues/2110>`__, `#2118 <https://github.com/ethereum/web3.py/issues/2118>`__, `#2122 <https://github.com/ethereum/web3.py/issues/2122>`__


v5.23.0 (2021-08-12)
--------------------

Features
~~~~~~~~

- Add support for eth_feeHistory RPC method (`#2038 <https://github.com/ethereum/web3.py/issues/2038>`__)
- Add support for eth_maxPriorityFeePerGas RPC method (`#2100 <https://github.com/ethereum/web3.py/issues/2100>`__)


Bugfixes
~~~~~~~~

- Hot fix for string interpolation issue with contract function call decoding exception to facilitate extracting a meaningful message from the eth_call response (`#2096 <https://github.com/ethereum/web3.py/issues/2096>`__)
- Bypass adding a ``gasPrice`` via the gas price strategy, if one is set, when EIP-1559 transaction params are used for ``send_transaction`` (`#2099 <https://github.com/ethereum/web3.py/issues/2099>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update feeHistory docs (`#2104 <https://github.com/ethereum/web3.py/issues/2104>`__)


v5.22.0 (2021-08-02)
--------------------

Features
~~~~~~~~

- Add support for eth_getRawTransactionByHash RPC method (`#2039 <https://github.com/ethereum/web3.py/issues/2039>`__)
- Add AsyncNet module (`#2044 <https://github.com/ethereum/web3.py/issues/2044>`__)
- Add async ``eth.get_balance``, ``eth.get_code``, ``eth.get_transaction_count`` methods. (`#2056 <https://github.com/ethereum/web3.py/issues/2056>`__)
- eth_signTransaction support for eip-1559 params 'maxFeePerGas' and 'maxPriorityFeePerGas' (`#2082 <https://github.com/ethereum/web3.py/issues/2082>`__)
- Add support for async ``w3.eth.call``. (`#2083 <https://github.com/ethereum/web3.py/issues/2083>`__)


Bugfixes
~~~~~~~~

- If a transaction hash was passed as a string rather than a HexByte to ``w3.eth.wait_for_transaction_receipt``, and the time was exhausted before the transaction is in the chain, the error being raised was a TypeError instead of the correct TimeExhausted error. This is because the ``to_hex`` method in the TimeExhausted error message expects a primitive as the first argument, and a string doesn't qualify as a primitive. Fixed by converting the transaction_hash to HexBytes instead. (`#2068 <https://github.com/ethereum/web3.py/issues/2068>`__)
- Hot fix for a string interpolation issue in message when BadFunctionCallOutput is raised for call_contract_function() (`#2069 <https://github.com/ethereum/web3.py/issues/2069>`__)
- ``fill_transaction_defaults()`` no longer sets a default ``gasPrice`` if 1559 fees are present in the transaction parameters. This fixes sign-and-send middleware issues with 1559 fees. (`#2092 <https://github.com/ethereum/web3.py/issues/2092>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Clarify that ``send_transaction``, ``modify_transaction``, and ``replace_transaction`` return HexByte objects instead of strings. (`#2058 <https://github.com/ethereum/web3.py/issues/2058>`__)
- Added troubleshooting section for Microsoft Visual C++ error on Windows machines (`#2077 <https://github.com/ethereum/web3.py/issues/2077>`__)
- Updated the sign-and-send middleware docs to include EIP-1559 as well as legacy transaction examples (`#2092 <https://github.com/ethereum/web3.py/issues/2092>`__)


Misc
~~~~

- `#2073 <https://github.com/ethereum/web3.py/issues/2073>`__, `#2080 <https://github.com/ethereum/web3.py/issues/2080>`__, `#2085 <https://github.com/ethereum/web3.py/issues/2085>`__


v5.21.0 (2021-07-12)
--------------------

Features
~~~~~~~~

- Adds support for EIP 1559 transaction keys: `maxFeePerGas` and `maxPriorityFeePerGas` (`#2060 <https://github.com/ethereum/web3.py/issues/2060>`__)


Bugfixes
~~~~~~~~

- Bugfix where an error response got passed to a function expecting a block identifier.

  Split out null result formatters from the error formatters and added some tests. (`#2022 <https://github.com/ethereum/web3.py/issues/2022>`__)
- Fix broken tests and use the new 1559 params for most of our test transactions. (`#2053 <https://github.com/ethereum/web3.py/issues/2053>`__)
- Set a default maxFeePerGas value consistent with Geth (`#2055 <https://github.com/ethereum/web3.py/issues/2055>`__)
- Fix bug in geth PoA middleware where a ``None`` response should throw a ``BlockNotFound`` error, but was instead throwing an ``AttributeError`` (`#2064 <https://github.com/ethereum/web3.py/issues/2064>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Added general documentation on unit and integration testing and how to contribute to our test suite. (`#2053 <https://github.com/ethereum/web3.py/issues/2053>`__)


v5.20.1 (2021-07-01)
--------------------

Bugfixes
~~~~~~~~

- Have the geth dev IPC auto connection check for the ``WEB3_PROVIDER_URI`` environment variable. (`#2023 <https://github.com/ethereum/web3.py/issues/2023>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Remove reference to allowing multiple providers in docs (`#2018 <https://github.com/ethereum/web3.py/issues/2018>`__)
- Update "Contract Deployment Example" docs to use ``py-solc-x`` as ``solc`` is no longer maintained. (`#2020 <https://github.com/ethereum/web3.py/issues/2020>`__)
- Detail using unreleased Geth builds in CI (`#2037 <https://github.com/ethereum/web3.py/issues/2037>`__)
- Clarify that a missing trie node error could occur when using ``block_identifier`` with ``.call()``
  on a node that isn't running in archive mode (`#2048 <https://github.com/ethereum/web3.py/issues/2048>`__)


Misc
~~~~

- `#1938 <https://github.com/ethereum/web3.py/issues/1938>`__, `#2015 <https://github.com/ethereum/web3.py/issues/2015>`__, `#2021 <https://github.com/ethereum/web3.py/issues/2021>`__, `#2025 <https://github.com/ethereum/web3.py/issues/2025>`__, `#2028 <https://github.com/ethereum/web3.py/issues/2028>`__, `#2029 <https://github.com/ethereum/web3.py/issues/2029>`__, `#2035 <https://github.com/ethereum/web3.py/issues/2035>`__


v5.20.0 (2021-06-09)
--------------------

Features
~~~~~~~~

- Add new AsyncHTTPProvider. No middleware or session caching support yet.

  Also adds async ``w3.eth.gas_price``, and async ``w3.isConnected()`` methods. (`#1978 <https://github.com/ethereum/web3.py/issues/1978>`__)
- Add ability for AsyncHTTPProvider to accept middleware

  Also adds async gas_price_strategy middleware, and moves gas estimate to middleware.

  AsyncEthereumTesterProvider now inherits from AsyncBase (`#1999 <https://github.com/ethereum/web3.py/issues/1999>`__)
- Support state_override in contract function call. (`#2005 <https://github.com/ethereum/web3.py/issues/2005>`__)


Bugfixes
~~~~~~~~

- Test ethpm caching + bump Sphinx version. (`#1977 <https://github.com/ethereum/web3.py/issues/1977>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Clarify solidityKeccak documentation. (`#1971 <https://github.com/ethereum/web3.py/issues/1971>`__)
- Improve contributor documentation context and ordering. (`#2008 <https://github.com/ethereum/web3.py/issues/2008>`__)
- Add docs for unstable AsyncHTTPProvider (`#2017 <https://github.com/ethereum/web3.py/issues/2017>`__)


Misc
~~~~

- `#1979 <https://github.com/ethereum/web3.py/issues/1979>`__, `#1980 <https://github.com/ethereum/web3.py/issues/1980>`__, `#1993 <https://github.com/ethereum/web3.py/issues/1993>`__, `#2002 <https://github.com/ethereum/web3.py/issues/2002>`__


v5.19.0 (2021-04-28)
--------------------

Features
~~~~~~~~

- Handle optional ``eth_call`` state override param. (`#1921 <https://github.com/ethereum/web3.py/issues/1921>`__)
- Add list_storage_keys deprecate listStorageKeys (`#1944 <https://github.com/ethereum/web3.py/issues/1944>`__)
- Add net_peers deprecate netPeers (`#1946 <https://github.com/ethereum/web3.py/issues/1946>`__)
- Add trace_replay_transaction deprecate traceReplayTransaction (`#1949 <https://github.com/ethereum/web3.py/issues/1949>`__)
- Add add_reserved_peer deprecate addReservedPeer (`#1951 <https://github.com/ethereum/web3.py/issues/1951>`__)
- Add ``parity.set_mode``, deprecate ``parity.setMode`` (`#1954 <https://github.com/ethereum/web3.py/issues/1954>`__)
- Add ``parity.trace_raw_transaction``, deprecate ``parity.traceRawTransaction`` (`#1955 <https://github.com/ethereum/web3.py/issues/1955>`__)
- Add ``parity.trace_call``, deprecate ``parity.traceCall`` (`#1957 <https://github.com/ethereum/web3.py/issues/1957>`__)
- Add trace_filter deprecate traceFilter (`#1960 <https://github.com/ethereum/web3.py/issues/1960>`__)
- Add trace_block, deprecate traceBlock (`#1961 <https://github.com/ethereum/web3.py/issues/1961>`__)
- Add trace_replay_block_transactions, deprecate traceReplayBlockTransactions (`#1962 <https://github.com/ethereum/web3.py/issues/1962>`__)
- Add ``parity.trace_transaction``, deprecate ``parity.traceTransaction`` (`#1963 <https://github.com/ethereum/web3.py/issues/1963>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Document ``eth_call`` state overrides. (`#1965 <https://github.com/ethereum/web3.py/issues/1965>`__)


Misc
~~~~

- `#1774 <https://github.com/ethereum/web3.py/issues/1774>`__, `#1805 <https://github.com/ethereum/web3.py/issues/1805>`__, `#1945 <https://github.com/ethereum/web3.py/issues/1945>`__, `#1964 <https://github.com/ethereum/web3.py/issues/1964>`__


v5.18.0 (2021-04-08)
--------------------

Features
~~~~~~~~

- Add ``w3.eth.modify_transaction`` deprecate ``w3.eth.modifyTransaction`` (`#1886 <https://github.com/ethereum/web3.py/issues/1886>`__)
- Add ``w3.eth.get_transaction_receipt``, deprecate ``w3.eth.getTransactionReceipt`` (`#1893 <https://github.com/ethereum/web3.py/issues/1893>`__)
- Add ``w3.eth.wait_for_transaction_receipt`` deprecate ``w3.eth.waitForTransactionReceipt`` (`#1896 <https://github.com/ethereum/web3.py/issues/1896>`__)
- Add ``w3.eth.set_contract_factory`` deprecate ``w3.eth.setContractFactory`` (`#1900 <https://github.com/ethereum/web3.py/issues/1900>`__)
- Add ``w3.eth.generate_gas_price`` deprecate ``w3.eth.generateGasPrice`` (`#1905 <https://github.com/ethereum/web3.py/issues/1905>`__)
- Add ``w3.eth.set_gas_price_strategy`` deprecate ``w3.eth.setGasPriceStrategy`` (`#1906 <https://github.com/ethereum/web3.py/issues/1906>`__)
- Add ``w3.eth.estimate_gas`` deprecate ``w3.eth.estimateGas`` (`#1913 <https://github.com/ethereum/web3.py/issues/1913>`__)
- Add ``w3.eth.sign_typed_data`` deprecate ``w3.eth.signTypedData`` (`#1915 <https://github.com/ethereum/web3.py/issues/1915>`__)
- Add ``w3.eth.get_filter_changes`` deprecate ``w3.eth.getFilterChanges`` (`#1916 <https://github.com/ethereum/web3.py/issues/1916>`__)
- Add ``eth.get_filter_logs``, deprecate ``eth.getFilterLogs`` (`#1919 <https://github.com/ethereum/web3.py/issues/1919>`__)
- Add ``eth.uninstall_filter``, deprecate ``eth.uninstallFilter`` (`#1920 <https://github.com/ethereum/web3.py/issues/1920>`__)
- Add ``w3.eth.get_logs`` deprecate ``w3.eth.getLogs`` (`#1925 <https://github.com/ethereum/web3.py/issues/1925>`__)
- Add ``w3.eth.submit_hashrate`` deprecate ``w3.eth.submitHashrate`` (`#1926 <https://github.com/ethereum/web3.py/issues/1926>`__)
- Add ``w3.eth.submit_work`` deprecate ``w3.eth.submitWork`` (`#1927 <https://github.com/ethereum/web3.py/issues/1927>`__)
- Add ``w3.eth.get_work``, deprecate ``w3.eth.getWork`` (`#1934 <https://github.com/ethereum/web3.py/issues/1934>`__)
- Adds public get_block_number method. (`#1937 <https://github.com/ethereum/web3.py/issues/1937>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add ABI type examples to docs (`#1890 <https://github.com/ethereum/web3.py/issues/1890>`__)
- Promote the new Ethereum Python Discord server on the README. (`#1898 <https://github.com/ethereum/web3.py/issues/1898>`__)
- Escape reserved characters in install script of Contributing docs. (`#1909 <https://github.com/ethereum/web3.py/issues/1909>`__)
- Add detailed event filtering examples. (`#1910 <https://github.com/ethereum/web3.py/issues/1910>`__)
- Add docs example for tuning log levels. (`#1928 <https://github.com/ethereum/web3.py/issues/1928>`__)
- Add some performance tips in troubleshooting docs. (`#1929 <https://github.com/ethereum/web3.py/issues/1929>`__)
- Add existing contract interaction to docs examples. (`#1933 <https://github.com/ethereum/web3.py/issues/1933>`__)
- Replace Gitter links with the Python Discord server. (`#1936 <https://github.com/ethereum/web3.py/issues/1936>`__)


Misc
~~~~

- `#1887 <https://github.com/ethereum/web3.py/issues/1887>`__, `#1907 <https://github.com/ethereum/web3.py/issues/1907>`__, `#1917 <https://github.com/ethereum/web3.py/issues/1917>`__, `#1930 <https://github.com/ethereum/web3.py/issues/1930>`__, `#1935 <https://github.com/ethereum/web3.py/issues/1935>`__


v5.17.0 (2021-02-24)
--------------------

Features
~~~~~~~~

- Added ``get_transaction_count``, and deprecated ``getTransactionCount`` (`#1844 <https://github.com/ethereum/web3.py/issues/1844>`__)
- Add ``w3.eth.send_transaction``, deprecate ``w3.eth.sendTransaction`` (`#1878 <https://github.com/ethereum/web3.py/issues/1878>`__)
- Add ``web3.eth.sign_transaction``, deprecate ``web3.eth.signTransaction`` (`#1879 <https://github.com/ethereum/web3.py/issues/1879>`__)
- Add ``w3.eth.send_raw_transaction``, deprecate ``w3.eth.sendRawTransaction`` (`#1880 <https://github.com/ethereum/web3.py/issues/1880>`__)
- Add ``w3.eth.replace_transaction`` deprecate ``w3.eth.replaceTransaction`` (`#1882 <https://github.com/ethereum/web3.py/issues/1882>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix return type of ``send_transaction`` in docs. (`#686 <https://github.com/ethereum/web3.py/issues/686>`__)


v5.16.0 (2021-02-04)
--------------------

Features
~~~~~~~~

- Added ``get_block_transaction_count``, and deprecated ``getBlockTransactionCount`` (`#1841 <https://github.com/ethereum/web3.py/issues/1841>`__)
- Move ``defaultAccount`` to ``default_account``. Deprecate ``defaultAccount``. (`#1848 <https://github.com/ethereum/web3.py/issues/1848>`__)
- Add ``eth.default_block``, deprecate ``eth.defaultBlock``.
  Also adds ``parity.default_block``, and deprecates ``parity.defaultBlock``. (`#1849 <https://github.com/ethereum/web3.py/issues/1849>`__)
- Add ``eth.gas_price``, deprecate ``eth.gasPrice`` (`#1850 <https://github.com/ethereum/web3.py/issues/1850>`__)
- Added ``eth.block_number`` property. Deprecated ``eth.blockNumber`` (`#1851 <https://github.com/ethereum/web3.py/issues/1851>`__)
- Add ``eth.chain_id``, deprecate ``eth.chainId`` (`#1852 <https://github.com/ethereum/web3.py/issues/1852>`__)
- Add ``eth.protocol_version``, deprecate ``eth.protocolVersion`` (`#1853 <https://github.com/ethereum/web3.py/issues/1853>`__)
- Add ``eth.get_code``, deprecate ``eth.getCode`` (`#1856 <https://github.com/ethereum/web3.py/issues/1856>`__)
- Deprecate ``eth.getProof``, add ``eth.get_proof`` (`#1857 <https://github.com/ethereum/web3.py/issues/1857>`__)
- Add ``eth.get_transaction``, deprecate ``eth.getTransaction`` (`#1858 <https://github.com/ethereum/web3.py/issues/1858>`__)
- Add ``eth.get_transaction_by_block``, deprecate ``eth.getTransactionByBlock`` (`#1859 <https://github.com/ethereum/web3.py/issues/1859>`__)
- Add get_uncle_by_block, deprecate getUncleByBlock (`#1862 <https://github.com/ethereum/web3.py/issues/1862>`__)
- Add get_uncle_count, deprecate getUncleCount (`#1863 <https://github.com/ethereum/web3.py/issues/1863>`__)


Bugfixes
~~~~~~~~

- Fix event filter creation if the event ABI contains a ``values`` key. (`#1807 <https://github.com/ethereum/web3.py/issues/1807>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Remove v5 breaking changes link from the top of the release notes. (`#1837 <https://github.com/ethereum/web3.py/issues/1837>`__)
- Add account creation troubleshooting docs. (`#1855 <https://github.com/ethereum/web3.py/issues/1855>`__)
- Document passing a struct into a contract function. (`#1860 <https://github.com/ethereum/web3.py/issues/1860>`__)
- Add instance configuration troubleshooting docs. (`#1865 <https://github.com/ethereum/web3.py/issues/1865>`__)
- Clarify nonce lookup in sendRawTransaction docs. (`#1866 <https://github.com/ethereum/web3.py/issues/1866>`__)
- Updated docs for web3.eth methods: eth.getTransactionReceipt and eth.waitForTransactionReceipt (`#1868 <https://github.com/ethereum/web3.py/issues/1868>`__)


v5.15.0 (2021-01-15)
--------------------

Features
~~~~~~~~

- Add ``get_storage_at`` method and deprecate ``getStorageAt``. (`#1828 <https://github.com/ethereum/web3.py/issues/1828>`__)
- Add ``eth.get_block`` method and deprecate ``eth.getBlock``. (`#1829 <https://github.com/ethereum/web3.py/issues/1829>`__)


Bugfixes
~~~~~~~~

- PR #1585 changed the error that was coming back from eth-tester when the Revert opcode was called,
  which broke some tests in downstream libraries. This PR reverts back to raising the original error. (`#1813 <https://github.com/ethereum/web3.py/issues/1813>`__)
- Added a new ``ContractLogicError`` for when a contract reverts a transaction.
  ``ContractLogicError`` will replace ``SolidityError``, in v6. (`#1814 <https://github.com/ethereum/web3.py/issues/1814>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Introduce Beacon API documentation (`#1836 <https://github.com/ethereum/web3.py/issues/1836>`__)


Misc
~~~~

- `#1602 <https://github.com/ethereum/web3.py/issues/1602>`__, `#1827 <https://github.com/ethereum/web3.py/issues/1827>`__, `#1831 <https://github.com/ethereum/web3.py/issues/1831>`__, `#1833 <https://github.com/ethereum/web3.py/issues/1833>`__, `#1834 <https://github.com/ethereum/web3.py/issues/1834>`__


v5.14.0 (2021-01-05)
--------------------

Bugfixes
~~~~~~~~

- Remove docs/web3.* from the gitignore to allow for the beacon docs to be added to git,
  and add ``beacon`` to the default web3 modules that get loaded. (`#1824 <https://github.com/ethereum/web3.py/issues/1824>`__)
- Remove auto-documenting from the Beacon API (`#1825 <https://github.com/ethereum/web3.py/issues/1825>`__)


Features
~~~~~~~~

- Introduce experimental Ethereum 2.0 beacon node API (`#1758 <https://github.com/ethereum/web3.py/issues/1758>`__)
- Add new get_balance method on Eth class. Deprecated getBalance. (`#1806 <https://github.com/ethereum/web3.py/issues/1806>`__)


Misc
~~~~

- `#1815 <https://github.com/ethereum/web3.py/issues/1815>`__, `#1816 <https://github.com/ethereum/web3.py/issues/1816>`__


v5.13.1 (2020-12-03)
--------------------

Bugfixes
~~~~~~~~

- Handle revert reason parsing for Ganache (`#1794 <https://github.com/ethereum/web3.py/issues/1794>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Document Geth and Parity/OpenEthereum fixture generation (`#1787 <https://github.com/ethereum/web3.py/issues/1787>`__)


Misc
~~~~

- `#1778 <https://github.com/ethereum/web3.py/issues/1778>`__, `#1780 <https://github.com/ethereum/web3.py/issues/1780>`__, `#1790 <https://github.com/ethereum/web3.py/issues/1790>`__, `#1791 <https://github.com/ethereum/web3.py/issues/1791>`__, `#1796 <https://github.com/ethereum/web3.py/issues/1796>`__


v5.13.0 (2020-10-29)
--------------------

Features
~~~~~~~~

- Raise `SolidityError` exceptions that contain the revert reason when a `call` fails. (`#941 <https://github.com/ethereum/web3.py/issues/941>`__)


Bugfixes
~~~~~~~~

- Update eth-tester dependency to fix tester environment install version conflict. (`#1782 <https://github.com/ethereum/web3.py/issues/1782>`__)


Misc
~~~~

- `#1757 <https://github.com/ethereum/web3.py/issues/1757>`__, `#1767 <https://github.com/ethereum/web3.py/issues/1767>`__


v5.12.3 (2020-10-21)
--------------------

Misc
~~~~

- `#1752 <https://github.com/ethereum/web3.py/issues/1752>`__, `#1759 <https://github.com/ethereum/web3.py/issues/1759>`__, `#1773 <https://github.com/ethereum/web3.py/issues/1773>`__, `#1775 <https://github.com/ethereum/web3.py/issues/1775>`__


v5.12.2 (2020-10-12)
--------------------

Bugfixes
~~~~~~~~

- Address the use of multiple providers in the docs (`#1701 <https://github.com/ethereum/web3.py/issues/1701>`__)
- Remove stale connection errors from docs (`#1737 <https://github.com/ethereum/web3.py/issues/1737>`__)
- Allow ENS name resolution for methods that use the ``Method`` class (`#1749 <https://github.com/ethereum/web3.py/issues/1749>`__)


Misc
~~~~

- `#1727 <https://github.com/ethereum/web3.py/issues/1727>`__, `#1728 <https://github.com/ethereum/web3.py/issues/1728>`__, `#1733 <https://github.com/ethereum/web3.py/issues/1733>`__, `#1735 <https://github.com/ethereum/web3.py/issues/1735>`__, `#1741 <https://github.com/ethereum/web3.py/issues/1741>`__, `#1746 <https://github.com/ethereum/web3.py/issues/1746>`__, `#1748 <https://github.com/ethereum/web3.py/issues/1748>`__, `#1753 <https://github.com/ethereum/web3.py/issues/1753>`__, `#1768 <https://github.com/ethereum/web3.py/issues/1768>`__


v5.12.1 (2020-09-02)
--------------------

Misc
~~~~

- `#1708 <https://github.com/ethereum/web3.py/issues/1708>`__, `#1709 <https://github.com/ethereum/web3.py/issues/1709>`__, `#1715 <https://github.com/ethereum/web3.py/issues/1715>`__, `#1722 <https://github.com/ethereum/web3.py/issues/1722>`__, `#1724 <https://github.com/ethereum/web3.py/issues/1724>`__


v5.12.0 (2020-07-16)
--------------------

Features
~~~~~~~~

- Update `web3.pm` and `ethpm` module to EthPM v3 specification. (`#1652 <https://github.com/ethereum/web3.py/issues/1652>`__)
- Allow consumer to initialize `HttpProvider` with their own `requests.Session`.  This allows the `HttpAdapter` connection pool to be tuned as desired. (`#1469 <https://github.com/ethereum/web3.py/issues/1469>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Use ethpm v3 packages in examples documentation. (`#1683 <https://github.com/ethereum/web3.py/issues/1683>`__)
- Modernize the deploy contract example. (`#1679 <https://github.com/ethereum/web3.py/issues/1679>`__)
- Add contribution guidelines and a code of conduct. (`#1691 <https://github.com/ethereum/web3.py/issues/1691>`__)


Misc
~~~~

- `#1687 <https://github.com/ethereum/web3.py/issues/1687>`__
- `#1690 <https://github.com/ethereum/web3.py/issues/1690>`__


v5.12.0-beta.3 (2020-07-15)
---------------------------

Bugfixes
~~~~~~~~

- Include ethpm-spec solidity examples in distribution. (`#1686 <https://github.com/ethereum/web3.py/issues/1686>`__)


v5.12.0-beta.2 (2020-07-14)
---------------------------

Bugfixes
~~~~~~~~

- Support ethpm-spec submodule in distributions. (`#1682 <https://github.com/ethereum/web3.py/issues/1682>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Modernize the deploy contract example. (`#1679 <https://github.com/ethereum/web3.py/issues/1679>`__)
- Use ethpm v3 packages in examples documentation. (`#1683 <https://github.com/ethereum/web3.py/issues/1683>`__)


v5.12.0-beta.1 (2020-07-09)
---------------------------

Features
~~~~~~~~

- Allow consumer to initialize `HttpProvider` with their own `requests.Session`.  This allows the `HttpAdapter` connection pool to be tuned as desired. (`#1469 <https://github.com/ethereum/web3.py/issues/1469>`__)
- Update `web3.pm` and `ethpm` module to EthPM v3 specification. (`#1652 <https://github.com/ethereum/web3.py/issues/1652>`__)


Bugfixes
~~~~~~~~

- Update outdated reference url in ethpm docs and tests. (`#1680 <https://github.com/ethereum/web3.py/issues/1680>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add a :meth:`~web3.eth.Eth.getBalance` example and provide more context for using the `fromWei` and `toWei` utility methods. (`#1676 <https://github.com/ethereum/web3.py/issues/1676>`__)
- Overhaul the Overview documentation to provide a tour of major features. (`#1681 <https://github.com/ethereum/web3.py/issues/1681>`__)


v5.11.1 (2020-06-17)
--------------------

Bugfixes
~~~~~~~~

- Added formatter rules for eth_tester middleware to allow :meth:`~web3.eth.Eth.getBalance` by using integer block numbers (`#1660 <https://github.com/ethereum/web3.py/issues/1660>`__)
- Fix type annotations within the ``eth.py`` module. Several arguments that defaulted to ``None`` were not declared ``Optional``. (`#1668 <https://github.com/ethereum/web3.py/issues/1668>`__)
- Fix type annotation warning when using string URI to instantiate an HTTP or WebsocketProvider. (`#1669 <https://github.com/ethereum/web3.py/issues/1669>`__)
- Fix type annotations within the ``web3`` modules. Several arguments that defaulted to ``None`` were not declared ``Optional``. (`#1670 <https://github.com/ethereum/web3.py/issues/1670>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Breaks up links into three categories (Intro, Guides, and API) and adds content to the index page: a lib introduction and some "Getting Started" links. (`#1671 <https://github.com/ethereum/web3.py/issues/1671>`__)
- Fills in some gaps in the Quickstart guide and adds provider connection details for local nodes. (`#1673 <https://github.com/ethereum/web3.py/issues/1673>`__)


v5.11.0 (2020-06-03)
--------------------

Features
~~~~~~~~

- Accept a block identifier in the ``Contract.estimateGas`` method. Includes a related upgrade of eth-tester to v0.5.0-beta.1. (`#1639 <https://github.com/ethereum/web3.py/issues/1639>`__)
- Introduce a more specific validation error, ``ExtraDataLengthError``. This enables tools to detect when someone may be connected to a POA network, for example, and provide a smoother developer experience. (`#1666 <https://github.com/ethereum/web3.py/issues/1666>`__)


Bugfixes
~~~~~~~~

- Correct the type annotations of `FilterParams.address` (`#1664 <https://github.com/ethereum/web3.py/issues/1664>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Corrects the return value of ``getTransactionReceipt``, description of caching middleware, and deprecated method names. (`#1663 <https://github.com/ethereum/web3.py/issues/1663>`__)
- Corrects documentation of websocket timeout configuration. (`#1665 <https://github.com/ethereum/web3.py/issues/1665>`__)


v5.10.0 (2020-05-18)
--------------------

Features
~~~~~~~~

- An update of ``eth-tester`` includes a change of the default fork from Constantinople to Muir Glacier.  `#1636 <https://github.com/ethereum/web3.py/issues/1636>`__


Bugfixes
~~~~~~~~

- ``my_contract.events.MyEvent`` was incorrectly annotated so that ``MyEvent`` was marked as a ``ContractEvent`` instance. Fixed to be a class type, i.e., ``Type[ContractEvent]``. (`#1646 <https://github.com/ethereum/web3.py/issues/1646>`__)
- IPCProvider correctly handled ``pathlib.Path`` input, but warned against its type. Fixed to permit Path objects in addition to strings. (`#1647 <https://github.com/ethereum/web3.py/issues/1647>`__)


Misc
~~~~

- `#1636 <https://github.com/ethereum/web3.py/issues/1636>`__


v5.9.0 (2020-04-30)
-------------------

Features
~~~~~~~~

- Upgrade eth-account to use v0.5.2+. eth-account 0.5.2 adds support for hd accounts

  Also had to pin eth-keys to get dependencies to resolve. (`#1622 <https://github.com/ethereum/web3.py/issues/1622>`__)


Bugfixes
~~~~~~~~

- Fix local_filter_middleware new entries bug (`#1514 <https://github.com/ethereum/web3.py/issues/1514>`__)
- ENS ``name`` and ENS ``address`` can return ``None``. Fixes return types. (`#1633 <https://github.com/ethereum/web3.py/issues/1633>`__)


v5.8.0 (2020-04-23)
-------------------

Features
~~~~~~~~

- Introduced ``list_wallets`` method to the ``GethPersonal`` class. (`#1516 <https://github.com/ethereum/web3.py/issues/1516>`__)
- Added block_identifier parameter to `ContractConstructor.estimateGas` method. (`#1588 <https://github.com/ethereum/web3.py/issues/1588>`__)
- Add snake_case methods to Geth and Parity Personal Modules.

  Deprecate camelCase methods. (`#1589 <https://github.com/ethereum/web3.py/issues/1589>`__)
- Added new weighted keyword argument to the time based gas price strategy.

  If ``True``, it will more give more weight to more recent block times. (`#1614 <https://github.com/ethereum/web3.py/issues/1614>`__)
- Adds support for Solidity's new(ish) receive function.

  Adds a new contract API that mirrors the existing fallback API: ``contract.receive`` (`#1623 <https://github.com/ethereum/web3.py/issues/1623>`__)


Bugfixes
~~~~~~~~

- Fixed hasattr overloader method in the web3.ContractEvent, web3.ContractFunction,
  and web3.ContractCaller classes by implementing a try/except handler
  that returns False if an exception is raised in the __getattr__ overloader method
  (since __getattr__ HAS to be called in every __hasattr__ call).

  Created two new Exception classes, 'ABIEventFunctionNotFound' and 'ABIFunctionNotFound',
  which inherit from both AttributeError and MismatchedABI, and replaced the MismatchedABI
  raises in ContractEvent, ContractFunction, and ContractCaller with a raise to the created class
  in the __getattr__ overloader method of the object. (`#1594 <https://github.com/ethereum/web3.py/issues/1594>`__)
- Change return type of rpc_gas_price_strategy from int to Wei (`#1612 <https://github.com/ethereum/web3.py/issues/1612>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix typo in "Internals" docs. Changed asyncronous --> asynchronous (`#1607 <https://github.com/ethereum/web3.py/issues/1607>`__)
- Improve documentation that introduces and troubleshoots Providers. (`#1609 <https://github.com/ethereum/web3.py/issues/1609>`__)
- Add documentation for when to use each transaction method. (`#1610 <https://github.com/ethereum/web3.py/issues/1610>`__)
- Remove incorrect web3 for w3 in doc example (`#1615 <https://github.com/ethereum/web3.py/issues/1615>`__)
- Add examples for using web3.contract via the ethpm module. (`#1617 <https://github.com/ethereum/web3.py/issues/1617>`__)
- Add dark mode to documentation. Also fixes a bunch of formatting issues in docs. (`#1626 <https://github.com/ethereum/web3.py/issues/1626>`__)


Misc
~~~~

- `#1545 <https://github.com/ethereum/web3.py/issues/1545>`__


v5.7.0 (2020-03-16)
-------------------

Features
~~~~~~~~

- Add snake_case methods for the net module

  Also moved net module to use ModuleV2 instead of Module (`#1592 <https://github.com/ethereum/web3.py/issues/1592>`__)


Bugfixes
~~~~~~~~

- Fix return type of eth_getCode. Changed from Hexstr to HexBytes. (`#1601 <https://github.com/ethereum/web3.py/issues/1601>`__)


Misc
~~~~

- `#1590 <https://github.com/ethereum/web3.py/issues/1590>`__


v5.6.0 (2020-02-26)
-------------------

Features
~~~~~~~~

- Add snake_case methods to Geth Miner class, deprecate camelCase methods (`#1579 <https://github.com/ethereum/web3.py/issues/1579>`__)
- Add snake_case methods for the net module, deprecate camelCase methods (`#1581 <https://github.com/ethereum/web3.py/issues/1581>`__)
- Add PEP561 type marker (`#1583 <https://github.com/ethereum/web3.py/issues/1583>`__)


Bugfixes
~~~~~~~~

- Increase replacement tx minimum gas price bump

  Parity/OpenEthereum requires a replacement transaction's
  gas to be a minimum of 12.5% higher than the original
  (vs. Geth's 10%). (`#1570 <https://github.com/ethereum/web3.py/issues/1570>`__)


v5.5.1 (2020-02-10)
-------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Documents the `getUncleCount` method. (`#1534 <https://github.com/ethereum/web3.py/issues/1534>`__)


Misc
~~~~

- `#1576 <https://github.com/ethereum/web3.py/issues/1576>`__


v5.5.0 (2020-02-03)
-------------------

Features
~~~~~~~~

- ENS had to release a new registry to push a bugfix. See
  `this article <https://medium.com/the-ethereum-name-service/ens-registry-migration-bug-fix-new-features-64379193a5a>`_
  for background information. web3.py uses the new registry for all default ENS interactions, now. (`#1573 <https://github.com/ethereum/web3.py/issues/1573>`__)


Bugfixes
~~~~~~~~

- Minor bugfix in how ContractCaller looks up abi functions. (`#1552 <https://github.com/ethereum/web3.py/issues/1552>`__)
- Update modules to use compatible typing-extensions import. (`#1554 <https://github.com/ethereum/web3.py/issues/1554>`__)
- Make 'from' and 'to' fields checksum addresses in returned transaction receipts (`#1562 <https://github.com/ethereum/web3.py/issues/1562>`__)
- Use local Trinity's IPC socket if it is available, for newer versions of Trinity. (`#1563 <https://github.com/ethereum/web3.py/issues/1563>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Add Matomo Tracking to Docs site.

  Matomo is an Open Source web analytics platform that allows us
  to get better insights and optimize for our audience without
  the negative consequences of other compareable platforms.

  Read more: https://matomo.org/why-matomo/ (`#1541 <https://github.com/ethereum/web3.py/issues/1541>`__)
- Fix web3 typo in docs (`#1559 <https://github.com/ethereum/web3.py/issues/1559>`__)


Misc
~~~~

- `#1521 <https://github.com/ethereum/web3.py/issues/1521>`__, `#1546 <https://github.com/ethereum/web3.py/issues/1546>`__, `#1571 <https://github.com/ethereum/web3.py/issues/1571>`__


v5.4.0 (2019-12-06)
-------------------

Features
~~~~~~~~

- Add __str__ to IPCProvider (`#1536 <https://github.com/ethereum/web3.py/issues/1536>`__)


Bugfixes
~~~~~~~~

- Add required typing-extensions library to setup.py (`#1544 <https://github.com/ethereum/web3.py/issues/1544>`__)


v5.3.1 (2019-12-05)
-------------------

Bugfixes
~~~~~~~~

- Only apply hexbytes formatting to r and s values in transaction if present (`#1531 <https://github.com/ethereum/web3.py/issues/1531>`__)
- Update eth-utils dependency which contains mypy bugfix. (`#1537 <https://github.com/ethereum/web3.py/issues/1537>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update Contract Event documentation to show correct example (`#1515 <https://github.com/ethereum/web3.py/issues/1515>`__)
- Add documentation to methods that raise an error in v5 instead of returning ``None`` (`#1527 <https://github.com/ethereum/web3.py/issues/1527>`__)


Misc
~~~~

- `#1518 <https://github.com/ethereum/web3.py/issues/1518>`__, `#1532 <https://github.com/ethereum/web3.py/issues/1532>`__


v5.3.0 (2019-11-14)
-------------------

Features
~~~~~~~~

- Support handling ENS domains in ERC1319 URIs. (`#1489 <https://github.com/ethereum/web3.py/issues/1489>`__)


Bugfixes
~~~~~~~~

- Make local block filter return empty list when when no blocks mined (`#1255 <https://github.com/ethereum/web3.py/issues/1255>`__)
- Google protobuf dependency was updated to `3.10.0` (`#1493 <https://github.com/ethereum/web3.py/issues/1493>`__)
- Infura websocket provider works when no secret key is present (`#1501 <https://github.com/ethereum/web3.py/issues/1501>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update Quickstart instructions to use the auto Infura module instead of the more complicated web3 auto module (`#1482 <https://github.com/ethereum/web3.py/issues/1482>`__)
- Remove outdated py.test command from readme (`#1483 <https://github.com/ethereum/web3.py/issues/1483>`__)


Misc
~~~~

- `#1461 <https://github.com/ethereum/web3.py/issues/1461>`__, `#1471 <https://github.com/ethereum/web3.py/issues/1471>`__, `#1475 <https://github.com/ethereum/web3.py/issues/1475>`__, `#1476 <https://github.com/ethereum/web3.py/issues/1476>`__, `#1479 <https://github.com/ethereum/web3.py/issues/1479>`__, `#1488 <https://github.com/ethereum/web3.py/issues/1488>`__, `#1492 <https://github.com/ethereum/web3.py/issues/1492>`__, `#1498 <https://github.com/ethereum/web3.py/issues/1498>`__


v5.2.2 (2019-10-21)
-------------------

Features
~~~~~~~~

- Add poll_latency to waitForTransactionReceipt (`#1453 <https://github.com/ethereum/web3.py/issues/1453>`__)


Bugfixes
~~~~~~~~

- Fix flaky Parity whisper module test (`#1473 <https://github.com/ethereum/web3.py/issues/1473>`__)


Misc
~~~~

- `#1472 <https://github.com/ethereum/web3.py/issues/1472>`__, `#1474 <https://github.com/ethereum/web3.py/issues/1474>`__


v5.2.1 (2019-10-17)
-------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Update documentation for unlock account duration (`#1464 <https://github.com/ethereum/web3.py/issues/1464>`__)
- Clarify module installation command for OSX>=10.15 (`#1467 <https://github.com/ethereum/web3.py/issues/1467>`__)


Misc
~~~~

- `#1468 <https://github.com/ethereum/web3.py/issues/1468>`__


v5.2.0 (2019-09-26)
-------------------

Features
~~~~~~~~

- Add ``enable_strict_bytes_type_checking`` flag to web3 instance (`#1419 <https://github.com/ethereum/web3.py/issues/1419>`__)
- Move Geth Whisper methods to snake case and deprecate camel case methods (`#1433 <https://github.com/ethereum/web3.py/issues/1433>`__)


Bugfixes
~~~~~~~~

- Add null check to logsbloom formatter (`#1445 <https://github.com/ethereum/web3.py/issues/1445>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Reformat autogenerated towncrier release notes (`#1460 <https://github.com/ethereum/web3.py/issues/1460>`__)


Web3 5.1.0 (2019-09-18)
-----------------------

Features
~~~~~~~~

- Add ``contract_types`` property to ``Package`` class. (`#1440 <https://github.com/ethereum/web3.py/issues/1440>`__)


Bugfixes
~~~~~~~~

- Fix flaky parity integration test in the whisper module (`#1147 <https://github.com/ethereum/web3.py/issues/1147>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Remove whitespace, move ``topics`` key -> ``topic`` in Geth docs (`#1425 <https://github.com/ethereum/web3.py/issues/1425>`__)
- Enforce stricter doc checking, turning warnings into errors to fail CI builds
  to catch issues quickly.

  Add missing ``web3.tools.rst`` to the table of contents and fix incorrectly formatted
  JSON example. (`#1437 <https://github.com/ethereum/web3.py/issues/1437>`__)
- Add example using Geth POA Middleware with Infura Rinkeby Node (`#1444 <https://github.com/ethereum/web3.py/issues/1444>`__)


Misc
~~~~

- `#1446 <https://github.com/ethereum/web3.py/issues/1446>`__, `#1451 <https://github.com/ethereum/web3.py/issues/1451>`__


v5.0.2
------
Released August 22, 2019

- Bugfixes

  - [ethPM] Fix bug in package id and release id fetching strategy
    - `#1427 <https://github.com/ethereum/web3.py/pull/1427>`_

v5.0.1
------
Released August 15, 2019

- Bugfixes

  - [ethPM] Add begin/close chars to package name regex
    - `#1418 <https://github.com/ethereum/web3.py/pull/1418>`_
  - [ethPM] Update deployments to work when only abi available
    - `#1417 <https://github.com/ethereum/web3.py/pull/1417>`_
  - Fix tuples handled incorrectly in ``decode_function_input``
    - `#1410 <https://github.com/ethereum/web3.py/pull/1410>`_

- Misc

  - Eliminate ``signTransaction`` warning
    - `#1404 <https://github.com/ethereum/web3.py/pull/1404>`_

v5.0.0
------
Released August 1, 2019

- Features

  - ``web3.eth.chainId`` now returns an integer instead of hex
    - `#1394 <https://github.com/ethereum/web3.py/pull/1394>`_

- Bugfixes

  - Deprecation Warnings now show for methods that have a
    ``@combomethod`` decorator
    - `#1401 <https://github.com/ethereum/web3.py/pull/1401>`_

- Misc

  - [ethPM] Add ethPM to the docker file
    - `#1405 <https://github.com/ethereum/web3.py/pull/1405>`_

- Docs

  - Docs are updated to use checksummed addresses
    - `#1390 <https://github.com/ethereum/web3.py/pull/1390>`_
  - Minor doc formatting fixes
    - `#1338 <https://github.com/ethereum/web3.py/pull/1338>`_ &
    `#1345 <https://github.com/ethereum/web3.py/pull/1345>`_



v5.0.0-beta.5
-------------
Released July 31, 2019

*This is intended to be the final release before the stable v5 release.*

- Features

  - Parity operating mode can be read and set
    - `#1355 <https://github.com/ethereum/web3.py/pull/1355>`_
  - Process a single event log, instead of a whole transaction
    receipt
    - `#1354 <https://github.com/ethereum/web3.py/pull/1354>`_

- Docs

  - Remove doctest dependency on ethtoken
    - `#1395 <https://github.com/ethereum/web3.py/pull/1395>`_

- Bugfixes

  - [ethPM] Bypass IPFS validation for large files
    - `#1393 <https://github.com/ethereum/web3.py/pull/1393>`_

- Misc

  - [ethPM] Update default Registry solidity contract
    - `#1400 <https://github.com/ethereum/web3.py/pull/1400>`_
  - [ethPM] Update web3.pm to use new simple Registry implementation
    - `#1398 <https://github.com/ethereum/web3.py/pull/1398>`_
  - Update dependency requirement formatting for releasing
    - `#1403 <https://github.com/ethereum/web3.py/pull/1403>`_


v5.0.0-beta.4
-------------
Released July 18,2019



- Features

  - [ethPM] Update registry uri to support basic uris w/o package id
    - `#1389 <https://github.com/ethereum/web3.py/pull/1389>`_

- Docs

  - Clarify in docs the return of ``Eth.sendRawTransaction()`` as
    a HexBytes object, not a string.
    - `#1384 <https://github.com/ethereum/web3.py/pull/1384>`_

- Misc

  - [ethPM] Migrate tests over from pytest-ethereum
    - `#1385 <https://github.com/ethereum/web3.py/pull/1385>`_

v5.0.0-beta.3
-------------
Released July 15, 2019

- Features

  - Add eth_getProof support
    - `#1185 <https://github.com/ethereum/web3.py/pull/1185>`_
  - Implement web3.pm.get_local_package()
    - `#1372 <https://github.com/ethereum/web3.py/pull/1372>`_
  - Update registry URIs to support chain IDs
    - `#1382 <https://github.com/ethereum/web3.py/pull/1382>`_
  - Add error flags to ``event.processReceipt``
    - `#1366 <https://github.com/ethereum/web3.py/pull/1366>`_

- Bugfixes

  - Remove full IDNA processing in favor of UTS46
    - `#1364 <https://github.com/ethereum/web3.py/pull/1364>`_

- Misc

  - Migrate py-ethpm library to web3/ethpm
    - `#1379 <https://github.com/ethereum/web3.py/pull/1379>`_
  - Relax canonical address requirement in ethPM
    - `#1380 <https://github.com/ethereum/web3.py/pull/1380>`_
  - Replace ethPM's infura strategy with web3's native infura support
    - `#1383 <https://github.com/ethereum/web3.py/pull/1383>`_
  - Change ``combine_argument_formatters`` to ``apply_formatters_to_sequence``
    - `#1360 <https://github.com/ethereum/web3.py/pull/1360>`_
  - Move ``pytest.xfail`` instances to ``@pytest.mark.xfail``
    - `#1376 <https://github.com/ethereum/web3.py/pull/1376>`_
  - Change ``net.version`` to ``eth.chainId`` in default
    transaction params
    - `#1378 <https://github.com/ethereum/web3.py/pull/1378>`_


v5.0.0-beta.2
-------------
Released May 13, 2019

- Features

  - Mark deprecated sha3 method as static
    - `#1350 <https://github.com/ethereum/web3.py/pull/1350>`_
  - Upgrade to eth-account v0.4.0
    - `#1348 <https://github.com/ethereum/web3.py/pull/1348>`_

- Docs

  - Add note about web3[tester] in documentation
    - `#1325 <https://github.com/ethereum/web3.py/pull/1325>`_

- Misc

  - Replace ``web3._utils.toolz`` imports with ``eth_utils.toolz``
    - `#1317 <https://github.com/ethereum/web3.py/pull/1317>`_


v5.0.0-beta.1
-------------
Released May 6, 2019

- Features

  - Add support for tilda in provider IPC Path
    - `#1049 <https://github.com/ethereum/web3.py/pull/1049>`_
  - EIP 712 Signing Supported
    - `#1319 <https://github.com/ethereum/web3.py/pull/1319>`_

- Docs

  - Update contract example to use ``compile_standard``
    - `#1263 <https://github.com/ethereum/web3.py/pull/1263>`_
  - Fix typo in middleware docs
    - `#1339 <https://github.com/ethereum/web3.py/pull/1339>`_


v5.0.0-alpha.11
---------------
Released April 24, 2019

- Docs

  - Add documentation for web3.py unit tests
    - `#1324 <https://github.com/ethereum/web3.py/pull/1324>`_

- Misc

  - Update deprecated collections.abc imports
    - `#1334 <https://github.com/ethereum/web3.py/pull/1334>`_
  - Fix documentation typo
    - `#1335 <https://github.com/ethereum/web3.py/pull/1335>`_
  - Upgrade eth-tester version
    - `#1332 <https://github.com/ethereum/web3.py/pull/1332>`_


v5.0.0-alpha.10
---------------
Released April 15, 2019

- Features

  - Add getLogs by blockHash
    - `#1269 <https://github.com/ethereum/web3.py/pull/1269>`_
  - Implement chainId endpoint
    - `#1295 <https://github.com/ethereum/web3.py/pull/1295>`_
  - Moved non-standard JSON-RPC endpoints to applicable
    Parity/Geth docs. Deprecated ``web3.version`` for ``web3.api``
    - `#1290 <https://github.com/ethereum/web3.py/pull/1290>`_
  - Moved Whisper endpoints to applicable Geth or Parity namespace
    - `#1308 <https://github.com/ethereum/web3.py/pull/1308>`_
  - Added support for Goerli provider
    - `#1286 <https://github.com/ethereum/web3.py/pull/1286>`_
  - Added addReservedPeer to Parity module
    - `#1311 <https://github.com/ethereum/web3.py/pull/1311>`_

- Bugfixes

  - Cast gas price values to integers in gas strategies
    - `#1297 <https://github.com/ethereum/web3.py/pull/1297>`_
  - Missing constructor function no longer ignores constructor args
    - `#1316 <https://github.com/ethereum/web3.py/pull/1316>`_

- Misc

  - Require eth-utils >= 1.4, downgrade Go version for integration tests
    - `#1310 <https://github.com/ethereum/web3.py/pull/1310>`_
  - Fix doc build warnings
    - `#1331 <https://github.com/ethereum/web3.py/pull/1331>`_
  - Zip Fixture data
    - `#1307 <https://github.com/ethereum/web3.py/pull/1307>`_
  - Update Geth version for integration tests
    - `#1301 <https://github.com/ethereum/web3.py/pull/1301>`_
  - Remove unneeded testrpc
    - `#1322 <https://github.com/ethereum/web3.py/pull/1322>`_
  - Add ContractCaller docs to v5 migration guide
    - `#1323 <https://github.com/ethereum/web3.py/pull/1323>`_



v5.0.0-alpha.9
--------------
Released March 26, 2019

- Breaking Changes

  - Raise error if there is no Infura API Key
    - `#1294 <https://github.com/ethereum/web3.py/pull/1294>`_ &
    - `#1299 <https://github.com/ethereum/web3.py/pull/1299>`_

- Misc

  - Upgraded Parity version for integration testing
    - `#1292 <https://github.com/ethereum/web3.py/pull/1292>`_

v5.0.0-alpha.8
--------------
Released March 20, 2019

- Breaking Changes

  - Removed ``web3/utils`` directory in favor of ``web3/_utils``
    - `#1282 <https://github.com/ethereum/web3.py/pull/1282>`_
  - Relocated personal RPC endpoints to Parity and Geth class
    - `#1211 <https://github.com/ethereum/web3.py/pull/1211>`_
  - Deprecated ``web3.net.chainId()``, ``web3.eth.getCompilers()``,
    and ``web3.eth.getTransactionFromBlock()``. Removed ``web3.eth.enableUnauditedFeatures()``
    - `#1270 <https://github.com/ethereum/web3.py/pull/1270>`_
  - Relocated eth_protocolVersion and web3_clientVersion
    - `#1274 <https://github.com/ethereum/web3.py/pull/1274>`_
  - Relocated ``web3.txpool`` to ``web3.geth.txpool``
    - `#1275 <https://github.com/ethereum/web3.py/pull/1275>`_
  - Relocated admin module to Geth namespace
    - `#1288 <https://github.com/ethereum/web3.py/pull/1288>`_
  - Relocated miner module to Geth namespace
    - `#1287 <https://github.com/ethereum/web3.py/pull/1287>`_

- Features

  - Implement ``eth_submitHashrate`` and ``eth_submitWork`` JSONRPC endpoints.
    - `#1280 <https://github.com/ethereum/web3.py/pull/1280>`_
  - Implement ``web3.eth.signTransaction``
    - `#1277 <https://github.com/ethereum/web3.py/pull/1277>`_

- Docs

  - Added v5 migration docs
    - `#1284 <https://github.com/ethereum/web3.py/pull/1284>`_

v5.0.0-alpha.7
--------------
Released March 11, 2019

- Breaking Changes

  - Updated JSON-RPC calls that lookup txs or blocks to raise
    an error if lookup fails
    - `#1218 <https://github.com/ethereum/web3.py/pull/1218>`_ and
    `#1268 <https://github.com/ethereum/web3.py/pull/1268>`_

- Features

  - Tuple ABI support
    - `#1235 <https://github.com/ethereum/web3.py/pull/1235>`_

- Bugfixes

  - One last ``middleware_stack`` was still hanging on.
    Changed to ``middleware_onion``
    - `#1262 <https://github.com/ethereum/web3.py/pull/1262>`_

v5.0.0-alpha.6
--------------
Released February 25th, 2019

- Features

  - New ``NoABIFound`` error for cases where there is no ABI
    - `#1247 <https://github.com/ethereum/web3.py/pull/1247>`_

- Misc

  - Interact with Infura using an API Key. Key will be required after March 27th.
    - `#1232 <https://github.com/ethereum/web3.py/pull/1232>`_
  - Remove ``process_type`` utility function in favor of
    eth-abi functionality
    - `#1249 <https://github.com/ethereum/web3.py/pull/1249>`_


v5.0.0-alpha.5
--------------

Released February 13th, 2019

- Breaking Changes

  - Remove deprecated ``buildTransaction``, ``call``, ``deploy``,
    ``estimateGas``, and ``transact`` methods
    - `#1232 <https://github.com/ethereum/web3.py/pull/1232>`_

- Features

  - Adds ``Web3.toJSON`` method
    - `#1173 <https://github.com/ethereum/web3.py/pull/1173>`_
  - Contract Caller API Implemented
    - `#1227 <https://github.com/ethereum/web3.py/pull/1227>`_
  - Add Geth POA middleware to use Rinkeby with Infura Auto
    - `#1234 <https://github.com/ethereum/web3.py/pull/1234>`_
  - Add manifest and input argument validation to ``pm.release_package()``
    - `#1237 <https://github.com/ethereum/web3.py/pull/1237>`_

- Misc

  - Clean up intro and block/tx sections in Filter docs
    - `#1223 <https://github.com/ethereum/web3.py/pull/1223>`_
  - Remove unnecessary ``EncodingError`` exception catching
    - `#1224 <https://github.com/ethereum/web3.py/pull/1224>`_
  - Improvements to ``merge_args_and_kwargs`` utility function
    - `#1228 <https://github.com/ethereum/web3.py/pull/1228>`_
  - Update vyper registry assets
    - `#1242 <https://github.com/ethereum/web3.py/pull/1242>`_


v5.0.0-alpha.4
--------------

Released January 23rd, 2019

- Breaking Changes

  - Rename ``middleware_stack`` to ``middleware_onion``
    - `#1210 <https://github.com/ethereum/web3.py/pull/1210>`_
  - Drop already deprecated ``web3.soliditySha3``
    - `#1217 <https://github.com/ethereum/web3.py/pull/1217>`_
  - ENS: Stop inferring ``.eth`` TLD on domain names
    - `#1205 <https://github.com/ethereum/web3.py/pull/1205>`_

- Bugfixes

  - Validate ``ethereum_tester`` class in ``EthereumTesterProvider``
    - `#1217 <https://github.com/ethereum/web3.py/pull/1217>`_
  - Support ``getLogs()`` method without creating filters
    - `#1192 <https://github.com/ethereum/web3.py/pull/1192>`_

- Features

  - Stablize the ``PM`` module
    - `#1125 <https://github.com/ethereum/web3.py/pull/1125>`_
  - Implement async ``Version`` module
    - `#1166 <https://github.com/ethereum/web3.py/pull/1166>`_

- Misc

  - Update .gitignore to ignore ``.DS_Store`` and ``.mypy_cache/``
    - `#1215 <https://github.com/ethereum/web3.py/pull/1215>`_
  - Change CircleCI badge link to CircleCI project
    - `#1214 <https://github.com/ethereum/web3.py/pull/1214>`_


v5.0.0-alpha.3
--------------

Released January 15th, 2019

- Breaking Changes

  - Remove ``web3.miner.hashrate`` and ``web3.version.network``
    - `#1198 <https://github.com/ethereum/web3.py/pull/1198>`_
  - Remove ``web3.providers.tester.EthereumTesterProvider``
    and ``web3.providers.tester.TestRPCProvider``
    - `#1199 <https://github.com/ethereum/web3.py/pull/1199>`_
  - Change ``manager.providers`` from list to single ``manager.provider``
    - `#1200 <https://github.com/ethereum/web3.py/pull/1200>`_
  - Replace deprecated ``web3.sha3`` method with ``web3.keccak`` method
    - `#1207 <https://github.com/ethereum/web3.py/pull/1207>`_
  - Drop auto detect testnets for IPCProvider
    - `#1206 <https://github.com/ethereum/web3.py/pull/1206>`_

- Bugfixes

  - Add check to make sure blockHash exists
    - `#1158 <https://github.com/ethereum/web3.py/pull/1158>`_

- Misc

  - Remove some unreachable code in `providers/base.py`
    - `#1160 <https://github.com/ethereum/web3.py/pull/1160>`_
  - Migrate tester provider results from middleware to defaults
    - `#1188 <https://github.com/ethereum/web3.py/pull/1188>`_
  - Fix doc formatting for build_filter method
    - `#1187 <https://github.com/ethereum/web3.py/pull/1187>`_
  - Add ERC20 example in docs
    - `#1178 <https://github.com/ethereum/web3.py/pull/1178>`_
  - Code style improvements
    - `#1194 <https://github.com/ethereum/web3.py/pull/1194>`_
    & `#1191 <https://github.com/ethereum/web3.py/pull/1191>`_
  - Convert Web3 instance variables to w3
    - `#1186 <https://github.com/ethereum/web3.py/pull/1186>`_
  - Update eth-utils dependencies and clean up other dependencies
    - `#1195 <https://github.com/ethereum/web3.py/pull/1195>`_


v5.0.0-alpha.2
--------------

Released December 20th, 2018

- Breaking Changes

  - Remove support for python3.5, drop support for eth-abi v1
    - `#1163 <https://github.com/ethereum/web3.py/pull/1163>`_
- Features

  - Support for custom ReleaseManager was fixed
    - `#1165 <https://github.com/ethereum/web3.py/pull/1165>`_

- Misc

  - Fix doctest nonsense with unicorn token
    - `3b2047 <https://github.com/ethereum/web3.py/commit/3b20479ea52>`_
  - Docs for installing web3 in FreeBSD
    - `#1156 <https://github.com/ethereum/web3.py/pull/1156>`_
  - Use latest python in readthedocs
    - `#1162 <https://github.com/ethereum/web3.py/pull/1162>`_
  - Use twine in release script
    - `#1164 <https://github.com/ethereum/web3.py/pull/1164>`_
  - Upgrade eth-tester, for eth-abi v2 support
    - `#1168 <https://github.com/ethereum/web3.py/pull/1168>`_

v5.0.0-alpha.1
--------------

Released December 13th, 2018

- Features

  - Add Rinkeby and Kovan Infura networks; made mainnet the default
    - `#1150 <https://github.com/ethereum/web3.py/pull/1150>`_
  - Add parity-specific ``listStorageKeys`` RPC
    - `#1145 <https://github.com/ethereum/web3.py/pull/1145>`_
  - Deprecated ``Web3.soliditySha3``; use ``Web3.solidityKeccak`` instead.
    - `#1139 <https://github.com/ethereum/web3.py/pull/1139>`_
  - Add default trinity locations to IPC path guesser
    - `#1121 <https://github.com/ethereum/web3.py/pull/1121>`_
  - Add wss to ``AutoProvider``
    - `#1110 <https://github.com/ethereum/web3.py/pull/1110>`_
  - Add timeout for ``WebsocketProvider``
    - `#1109 <https://github.com/ethereum/web3.py/pull/1109>`_
  - Receipt timeout raises ``TimeExhausted``
    - `#1070 <https://github.com/ethereum/web3.py/pull/1070>`_
  - Allow specification of block number for ``eth_estimateGas``
    - `#1046 <https://github.com/ethereum/web3.py/pull/1046>`_


- Misc

  - Removed ``web3._utils.six`` support
    - `#1116 <https://github.com/ethereum/web3.py/pull/1116>`_
  - Upgrade eth-utils to 1.2.0
    - `#1104 <https://github.com/ethereum/web3.py/pull/1104>`_
  - Require Python version 3.5.3 or greater
    - `#1095 <https://github.com/ethereum/web3.py/pull/1095>`_
  - Bump websockets version to 7.0.0
    - `#1146 <https://github.com/ethereum/web3.py/pull/1146>`_
  - Bump parity test binary to 1.11.11
    - `#1064 <https://github.com/ethereum/web3.py/pull/1064>`_


v4.8.2
--------

Released November 15, 2018

- Misc

  - Reduce unneeded memory usage
    - `#1138 <https://github.com/ethereum/web3.py/pull/1138>`_

v4.8.1
--------

Released October 28, 2018

- Features

  - Add timeout for WebsocketProvider
    - `#1119 <https://github.com/ethereum/web3.py/pull/1119>`_
  - Reject transactions that send ether to non-payable contract functions
    - `#1115 <https://github.com/ethereum/web3.py/pull/1115>`_
  - Add Auto Infura Ropsten support: ``from web3.auto.infura.ropsten import w3``
    - `#1124 <https://github.com/ethereum/web3.py/pull/1124>`_
  - Auto-detect trinity IPC file location
    - `#1129 <https://github.com/ethereum/web3.py/pull/1129>`_
- Misc

  - Require Python >=3.5.3
    - `#1107 <https://github.com/ethereum/web3.py/pull/1107>`_
  - Upgrade eth-tester and eth-utils
    - `#1085 <https://github.com/ethereum/web3.py/pull/1085>`_
  - Configure readthedocs dependencies
    - `#1082 <https://github.com/ethereum/web3.py/pull/1082>`_
  - soliditySha3 docs fixup
    - `#1100 <https://github.com/ethereum/web3.py/pull/1100>`_
  - Update ropsten faucet links in troubleshooting docs

v4.7.2
--------

Released September 25th, 2018

- Bugfixes

  - IPC paths starting with ``~`` are appropriately resolved to the home directory
    - `#1072 <https://github.com/ethereum/web3.py/pull/1072>`_
  - You can use the local signing middleware with :class:`bytes`-type addresses
    - `#1069 <https://github.com/ethereum/web3.py/pull/1069>`_

v4.7.1
--------

Released September 11th, 2018

- Bugfixes

  - `old pip bug <https://github.com/pypa/pip/issues/4614>`_ used during
    release made it impossible for non-windows users to install 4.7.0.

v4.7.0
--------

Released September 10th, 2018

- Features

  - Add traceFilter method to the parity module.
    - `#1051 <https://github.com/ethereum/web3.py/pull/1051>`_
  - Move :mod:`~web3.utils.datastructures` to public namespace :mod:`~web3.datastructures`
    to improve support for type checking.
    - `#1038 <https://github.com/ethereum/web3.py/pull/1038>`_
  - Optimization to contract calls
    - `#944 <https://github.com/ethereum/web3.py/pull/944>`_
- Bugfixes

  - ENS name resolution only attempted on mainnet by default.
    -  `#1037 <https://github.com/ethereum/web3.py/pull/1037>`_
  - Fix attribute access error when attributedict middleware is not used.
    - `#1040 <https://github.com/ethereum/web3.py/pull/1040>`_
- Misc
  - Upgrade eth-tester to 0.1.0-beta.32, and remove integration tests for py-ethereum.
  - Upgrade eth-hash to 0.2.0 with pycryptodome 3.6.6 which resolves a vulnerability.

v4.6.0
--------

Released Aug 24, 2018

- Features

  - Support for Python 3.7, most notably in :class:`~web3.providers.websocket.WebsocketProvider`
    -  `#996 <https://github.com/ethereum/web3.py/pull/996>`_
  - You can now decode a transaction's data to its original function call and arguments with:
    :meth:`contract.decode_function_input() <web3.contract.Contract.decode_function_input>` - `#991
    <https://github.com/ethereum/web3.py/pull/991>`_
  - Support for :class:`~web3.providers.ipc.IPCProvider` in FreeBSD (and more readme docs) - `#1008
    <https://github.com/ethereum/web3.py/pull/1008>`_
- Bugfixes

  - Fix crash in time-based gas strategies with small number of transactions - `#983
    <https://github.com/ethereum/web3.py/pull/983>`_
  - Fx crash when passing multiple addresses to :meth:`w3.eth.getLogs() <web3.eth.Eth.getLogs>` -
    `#1005 <https://github.com/ethereum/web3.py/pull/1005>`_
- Misc

  - Disallow configuring filters with both manual and generated topic lists - `#976
    <https://github.com/ethereum/web3.py/pull/976>`_
  - Add support for the upcoming eth-abi v2, which does ABI string decoding differently - `#974
    <https://github.com/ethereum/web3.py/pull/974>`_
  - Add a lot more filter tests - `#997
    <https://github.com/ethereum/web3.py/pull/997>`_
  - Add more tests for filtering with ``None``. Note that geth & parity differ here. - `#985
    <https://github.com/ethereum/web3.py/pull/985>`_
  - Follow-up on Parity bug that we reported upstream (`parity#7816
    <https://github.com/paritytech/parity-ethereum/issues/7816>`_): they resolved in 1.10. We
    removed xfail on that test. - `#992
    <https://github.com/ethereum/web3.py/pull/992>`_
  - Docs: add an example of interacting with an ERC20 contract - `#995
    <https://github.com/ethereum/web3.py/pull/995>`_
  - A couple doc typo fixes

      - `#1006 <https://github.com/ethereum/web3.py/pull/1006>`_
      - `#1010 <https://github.com/ethereum/web3.py/pull/1010>`_

v4.5.0
--------

Released July 30, 2018

- Features

  - Accept addresses supplied in :class:`bytes` format (which does not provide checksum validation)
  - Improve estimation of gas prices
- Bugfixes

  - Can now use a block number with :meth:`~web3.eth.Eth.getCode` when connected to
    :class:`~web3.providers.eth_tester.EthereumTesterProvider` (without crashing)
- Misc

  - Test Parity 1.11.7
  - Parity integration tests upgrade to use sha256 instead of md5
  - Fix some filter docs
  - eth-account upgrade to v0.3.0
  - eth-tester upgrade to v0.1.0-beta.29

v4.4.1
--------

Released June 29, 2018

- Bugfixes

  - eth-pm package was renamed (old one deleted) which broke the web3 release.
    eth-pm was removed from the web3.py install until it's stable.

- Misc

  - :class:`~web3.providers.ipc.IPCProvider` now accepts a :class:`pathlib.Path`
    argument for the IPC path
  - Docs explaining the new custom autoproviders in web3

v4.4.0
--------

Released June 21, 2018

- Features

  - Add support for https in WEB3_PROVIDER_URI environment variable
  - Can send websocket connection parameters in :class:`~web3.providers.websocket.WebsocketProvider`
  - Two new auto-initialization options:

    - ``from web3.auto.gethdev import w3``
    - ``from web3.auto.infura import w3``
      (After setting the ``INFURA_API_KEY`` environment variable)
  - Alpha support for a new package management tool based on ethpm-spec
- Bugfixes

  - Can now receive large responses in :class:`~web3.providers.websocket.WebsocketProvider` by
    specifying a large ``max_size`` in the websocket connection parameters.
- Misc

  - Websockets dependency upgraded to v5
  - Raise deprecation warning on :meth:`~web3.eth.Eth.getTransactionFromBlock`
  - Fix docs for :meth:`~web3.eth.Eth.waitForTransactionReceipt`
  - Developer Dockerfile now installs testing dependencies

v4.3.0
--------

Released June 6, 2018

- Features

  - Support for the ABI types like: `fixedMxN
    <http://solidity.readthedocs.io/en/v0.4.24/abi-spec.html#types>`_
    which is used by Vyper.
  - In-flight transaction-signing middleware: Use local keys as if they were hosted keys
    using the new ``sign_and_send_raw_middleware``
  - New :meth:`~web3.eth.Eth.getUncleByBlock` API
  - New name :meth:`~web3.eth.Eth.getTransactionByBlock`, which replaces the deprecated
    :meth:`~web3.eth.Eth.getTransactionFromBlock`
  - Add several new Parity trace functions
  - New API to resolve ambiguous function calls, for example:

    - Two functions with the same name that accept similar argument types, like
      ``myfunc(uint8)`` and ``myfunc(int8)``, and you want to call
      ``contract.functions.myfunc(1).call()``
    - See how to use it at: :ref:`ambiguous-contract-functions`
- Bugfixes

  - Gas estimation doesn't crash, when 0 blocks are available. (ie~ on the genesis block)
  - Close out all HTTPProvider sessions, to squash warnings on exit
  - Stop adding Contract address twice to the filter. It was making some nodes unhappy
- Misc

  - Friendlier json encoding/decoding failure error messages
  - Performance improvements, when the responses from the node are large
    (by reducing the number of times we evaluate if the response is valid json)
  - Parity CI test fixes (ugh, environment setup hell, thanks to the
    community for cleaning this up!)
  - Don't crash when requesting a transaction that was created with the parity bug
    (which allowed an unsigned transaction to be included, so ``publicKey`` is ``None``)
  - Doc fixes: addresses must be checksummed (or ENS names on mainnet)
  - Enable local integration testing of parity on non-Debian OS
  - README:

    - Testing setup for devs
    - Change the build badge from Travis to Circle CI
  - Cache the parity binary in Circle CI, to reduce the impact of their binary API going down
  - Dropped the dot: ``py.test`` -> ``pytest``

v4.2.1
--------

Released May 9, 2018

- Bugfixes

  - When :meth:`getting a transaction <web3.eth.Eth.getTransaction>`
    with data attached and trying to :meth:`modify it <web3.eth.Eth.modifyTransaction>`
    (say, to increase the gas price), the data was not being reattached in
    the new transaction.
  - :meth:`web3.personal.sendTransaction` was crashing when using a transaction
    generated with ``buildTransaction()``
- Misc

  - Improved error message when connecting to a geth-style PoA network
  - Improved error message when address is not checksummed
  - Started in on support for ``fixedMxN`` ABI arguments
  - Lots of documentation upgrades, including:

    - Guide for understanding nodes/networks/connections
    - Simplified Quickstart with notes for common issues
    - A new Troubleshooting section
  - Potential pypy performance improvements (use toolz instead of cytoolz)
  - eth-tester upgraded to beta 24

v4.2.0
--------

Released Apr 25, 2018

- Removed audit warning and opt-in requirement for ``w3.eth.account``. See more in:
  :ref:`eth-account`
- Added an API to look up contract functions: ``fn = contract.functions['function_name_here']``
- Upgrade Whisper (shh) module to use v6 API
- Bugfix: set 'to' field of transaction to empty when using
  ``transaction = contract.constructor().buildTransaction()``
- You can now specify `nonce` in ``buildTransaction()``
- Distinguish between chain id and network id -- currently always return `None` for
  :attr:`~web3.net.Net.chainId`
- Better error message when trying to use a contract function that has 0 or >1 matches
- Better error message when trying to install on a python version <3.5
- Installs pypiwin32 during pip install, for a better Windows experience
- Cleaned up a lot of test warnings by upgrading from deprecated APIs, especially
  from the deprecated ``contract.deploy(txn_dict, args=contract_args)``
  to the new ``contract.constructor(*contract_args).transact(txn_dict)``
- Documentation typo fixes
- Better template for Pull Requests

v4.1.0
--------

Released Apr 9, 2018

- New :class:`~web3.providers.websocket.WebsocketProvider`.
  If you're looking for better performance than HTTP, check out websockets.
- New :meth:`w3.eth.waitForTransactionReceipt() <web3.eth.Eth.waitForTransactionReceipt>`
- Added name collision detection to ConciseContract and ImplicitContract
- Bugfix to allow fromBlock set to 0 in createFilter, like
  ``contract.events.MyEvent.createFilter(fromBlock=0, ...)``
- Bugfix of ENS automatic connection
- eth-tester support for Byzantium
- New migration guide for v3 -> v4 upgrade
- Various documentation updates
- Pinned eth-account to older version

v4.0.0
-----------------

Released Apr 2, 2018

- Marked beta.13 as stable
- Documentation tweaks

v4.0.0-beta.13
-----------------

Released Mar 27, 2018

*This is intended to be the final release before the stable v4 release.*

- Add support for geth 1.8 (fixed error on :meth:`~web3.eth.Eth.getTransactionReceipt`)
- You can now call a contract method at a specific block
  with the ``block_identifier`` keyword argument, see:
  :meth:`~web3.contract.ContractFunction.call`
- In preparation for stable release, disable ``w3.eth.account`` by default,
  until a third-party audit is complete & resolved.
- New API for contract deployment, which enables gas estimation, local signing, etc.
  See :meth:`~web3.contract.Contract.constructor`.
- Find contract events with :ref:`contract.events.$my_event.createFilter() <contract_create_filter>`
- Support auto-complete for contract methods.
- Upgrade most dependencies to stable

  - eth-abi
  - eth-utils
  - hexbytes
  - *not included: eth-tester and eth-account*
- Switch the default EthereumTesterProvider backend from eth-testrpc to eth-tester:
  :class:`web3.providers.eth_tester.EthereumTesterProvider`
- A lot of documentation improvements
- Test node integrations over a variety of providers
- geth 1.8 test suite


v4.0.0-beta.12
-----------------

A little hiccup on release. Skipped.

v4.0.0-beta.11
-----------------

Released Feb 28, 2018

- New methods to modify or replace pending transactions
- A compatibility option for connecting to ``geth --dev`` -- see :ref:`geth-poa`
- A new :attr:`web3.net.chainId`
- Create a filter object from an existing filter ID.
- eth-utils v1.0.1 (stable) compatibility


v4.0.0-beta.10
-----------------

Released Feb 21, 2018

- bugfix: Compatibility with eth-utils v1-beta2
  (the incompatibility was causing fresh web3.py installs to fail)
- bugfix: crash when sending the output of ``contract.functions.myFunction().buildTransaction()``
  to :meth:`~web3.eth.Eth.sendTransaction`. Now, having a chainID key does not crash
  sendTransaction.
- bugfix: a TypeError when estimating gas like:
  ``contract.functions.myFunction().estimateGas()`` is fixed
- Added parity integration tests to the continuous integration suite!
- Some py3 and docs cleanup

v4.0.0-beta.9
-------------

Released Feb 8, 2018

- Access event log parameters as attributes
- Support for specifying nonce in eth-tester
- `Bugfix <https://github.com/ethereum/web3.py/pull/616>`_
  dependency conflicts between eth-utils, eth-abi, and eth-tester
- Clearer error message when invalid keywords provided to contract constructor function
- New docs for working with private keys + set up doctests
- First parity integration tests
- replace internal implementation of w3.eth.account with
  :class:`eth_account.account.Account`

v4.0.0-beta.8
-------------

Released Feb 7, 2018, then recalled. It added 32MB of test data to git history,
so the tag was deleted, as well as the corresponding release.
(Although the release would not have contained that test data)

v4.0.0-beta.7
-------------

Released Jan 29, 2018

- Support for :meth:`web3.eth.Eth.getLogs` in eth-tester with py-evm
- Process transaction receipts with Event ABI, using
  `Contract.events.myEvent(*args, **kwargs).processReceipt(transaction_receipt)`
  see :ref:`event-log-object` for the new type.
- Add timeout parameter to :class:`web3.providers.ipc.IPCProvider`
- bugfix: make sure `idna` package is always installed
- Replace ethtestrpc with py-evm, in all tests
- Dockerfile fixup
- Test refactoring & cleanup
- Reduced warnings during tests

v4.0.0-beta.6
-------------

Released Jan 18, 2018

- New contract function call API: `my_contract.functions.my_func().call()` is preferred over the now
  deprecated `my_contract.call().my_func()` API.
- A new, sophisticated gas estimation algorithm, based on the https://ethgasstation.info approach.
  You must opt-in to the new approach, because it's quite slow. We recommend using the new caching middleware.
  See :meth:`web3.gas_strategies.time_based.construct_time_based_gas_price_strategy`
- New caching middleware that can cache based on time, block, or indefinitely.
- Automatically retry JSON-RPC requests over HTTP, a few times.
- ConciseContract now has the address directly
- Many eth-tester fixes. :class:`web3.providers.eth_tester.main.EthereumTesterProvider` is now a
  legitimate alternative to :class:`web3.providers.tester.EthereumTesterProvider`.
- ethtest-rpc removed from testing. Tests use eth-tester only, on pyethereum. Soon it will be
  eth-tester with py-evm.
- Bumped several dependencies, like eth-tester
- Documentation updates

v4.0.0-beta.5
-------------

Released Dec 28, 2017

* Improvements to working with eth-tester, using :class:`~web3.providers.eth_tester.EthereumTesterProvider`:

  * Bugfix the key names in event logging
  * Add support for :meth:`~web3.eth.Eth.sendRawTransaction`
* :class:`~web3.providers.ipc.IPCProvider` now automatically retries on a broken connection, like when you restart your node
* New gas price engine API, laying groundwork for more advanced gas pricing strategies

v4.0.0-beta.4
-------------

Released Dec 7, 2017

* New :meth:`~web3.contract.Contract.buildTransaction` method to prepare contract transactions, offline
* New automatic provider detection, for ``w3 = Web3()`` initialization
* Set environment variable `WEB3_PROVIDER_URI` to suggest a provider for automatic detection
* New API to set providers like: ``w3.providers = [IPCProvider()]``
* Crashfix: :meth:`web3.eth.Eth.filter` when retrieving logs with the argument 'latest'
* Bump eth-tester to v0.1.0-beta.5, with bugfix for filtering by topic
* Removed GPL lib ``pylru``, now believed to be in full MIT license compliance.

v4.0.0-beta.3
-------------

Released Dec 1, 2017

* Fix encoding of ABI types: ``bytes[]`` and ``string[]``
* Windows connection error bugfix
* Bugfix message signatures that were broken ~1% of the time (zero-pad ``r`` and ``s``)
* Autoinit web3 now produces None instead of raising an exception on ``from web3.auto import w3``
* Clearer errors on formatting failure (includes field name that failed)
* Python modernization, removing Py2 compatibility cruft
* Update dependencies with changed names, now:

  * ``eth-abi``
  * ``eth-keyfile``
  * ``eth-keys``
  * ``eth-tester``
  * ``eth-utils``
* Faster Travis CI builds, with cached geth binary

v4.0.0-beta.2
-------------

Released Nov 22, 2017

Bug Fixes:

* :meth:`~web3.eth.Eth.sendRawTransaction` accepts raw bytes
* :meth:`~web3.eth.Eth.contract` accepts an ENS name as contract address
* :meth:`~web3.account.Account.signTransaction` returns the expected hash (*after* signing the transaction)
* :class:`~web3.account.Account` methods can all be called statically, like: ``Account.sign(...)``
* :meth:`~web3.eth.Eth.getTransactionReceipt` returns the ``status`` field as an ``int``
* :meth:`Web3.soliditySha3` looks up ENS names if they are supplied with an "address" ABI
* If running multiple threads with the same w3 instance, ``ValueError: Recursively called ...`` is no longer raised

Plus, various python modernization code cleanups, and testing against geth 1.7.2.

v4.0.0-beta.1
-------------

* Python 3 is now required
* ENS names can be used anywhere that a hex address can
* Sign transactions and messages with local private keys
* New filter mechanism: :meth:`~web3.utils.filters.Filter.get_all_entries` and :meth:`~web3.utils.filters.Filter.get_new_entries`
* Quick automatic initialization with ``from web3.auto import w3``
* All addresses must be supplied with an EIP-55 checksum
* All addresses are returned with a checksum
* Renamed ``Web3.toDecimal()`` to ``toInt()``, see: :ref:`overview_type_conversions`
* All filter calls are synchronous, gevent integration dropped
* Contract :meth:`~web3.contract.Contract.eventFilter` has replaced both ``Contract.on()`` and ``Contract.pastEvents()``
* Contract arguments of ``bytes`` ABI type now accept hex strings.
* Contract arguments of ``string`` ABI type now accept python ``str``.
* Contract return values of ``string`` ABI type now return python ``str``.
* Many methods now return a ``bytes``-like object where they used to return a hex string, like in :meth:`Web3.sha3()`
* IPC connection left open and reused, rather than opened and closed on each call
* A number of deprecated methods from v3 were removed

3.16.1
------

* Addition of ``ethereum-tester`` as a dependency


3.16.0
------

* Addition of *named* middlewares for easier manipulation of middleware stack.
* Provider middlewares can no longer be modified during runtime.
* Experimental custom ABI normalization API for Contract objects.


3.15.0
------

* Change docs to use RTD theme
* Experimental new ``EthereumTesterProvider`` for the ``ethereum-tester`` library.
* Bugfix for ``function`` type abi encoding via ``ethereum-abi-utils`` upgrade to ``v0.4.1``
* Bugfix for ``Web3.toHex`` to conform to RPC spec.


3.14.2
------

* Fix PyPi readme text.


3.14.1
------

* Fix PyPi readme text.

3.14.0
------

* New ``stalecheck_middleware``
* Improvements to ``Web3.toHex`` and ``Web3.toText``.
* Improvements to ``Web3.sha3`` signature.
* Bugfixes for ``Web3.eth.sign`` api


3.13.5
------

* Add experimental ``fixture_middleware``
* Various bugfixes introduced in middleware API introduction and migration to
  formatter middleware.


3.13.4
------

* Bugfix for formatter handling of contract creation transaction.



3.13.3
------

* Improved testing infrastructure.


3.13.2
------

* Bugfix for retrieving filter changes for both new block filters and pending
  transaction filters.


3.13.1
------

* Fix mispelled ``attrdict_middleware`` (was spelled ``attrdict_middlware``).


3.13.0
------

* New Middleware API
* Support for multiple providers
* New ``web3.soliditySha3``
* Remove multiple functions that were never implemented from the original web3.
* Deprecated ``web3.currentProvider`` accessor.  Use ``web3.provider`` now instead.
* Deprecated password prompt within ``web3.personal.newAccount``.


3.12.0
------

* Bugfix for abi filtering to correctly handle ``constructor`` and ``fallback`` type abi entries.

3.11.0
------

* All web3 apis which accept ``address`` parameters now enforce checksums if the address *looks* like it is checksummed.
* Improvements to error messaging with when calling a contract on a node that may not be fully synced
* Bugfix for ``web3.eth.syncing`` to correctly handle ``False``

3.10.0
------

* Web3 now returns ``web3.utils.datastructures.AttributeDict`` in places where it previously returned a normal ``dict``.
* ``web3.eth.contract`` now performs validation on the ``address`` parameter.
* Added ``web3.eth.getWork`` API

3.9.0
-----

* Add validation for the ``abi`` parameter of ``eth``
* Contract return values of ``bytes``, ``bytesXX`` and ``string`` are no longer converted to text types and will be returned in their raw byte-string format.

3.8.1
-----

* Bugfix for ``eth_sign`` double hashing input.
* Removed deprecated ``DelegatedSigningManager``
* Removed deprecate ``PrivateKeySigningManager``

3.8.0
-----

* Update pyrlp dependency to ``>=0.4.7``
* Update eth-testrpc dependency to ``>=1.2.0``
* Deprecate ``DelegatedSigningManager``
* Deprecate ``PrivateKeySigningManager``

3.7.1
-----

* upstream version bump for bugfix in eth-abi-utils

3.7.0
-----

* deprecate ``eth.defaultAccount`` defaulting to the coinbase account.

3.6.2
-----

* Fix error message from contract factory creation.
* Use ``ethereum-utils`` for utility functions.

3.6.1
-----

* Upgrade ``ethereum-abi-utils`` dependency for upstream bugfix.

3.6.0
-----

* Deprecate ``Contract.code``: replaced by ``Contract.bytecode``
* Deprecate ``Contract.code_runtime``: replaced by ``Contract.bytecode_runtime``
* Deprecate ``abi``, ``code``, ``code_runtime`` and ``source`` as arguments for the ``Contract`` object.
* Deprecate ``source`` as a property of the ``Contract`` object
* Add ``Contract.factory()`` API.
* Deprecate the ``construct_contract_factory`` helper function.

3.5.3
-----

* Bugfix for how ``requests`` library is used.  Now reuses session.

3.5.2
-----

* Bugfix for construction of ``request_kwargs`` within HTTPProvider

3.5.1
-----

* Allow ``HTTPProvider`` to be imported from ``web3`` module.
* make ``HTTPProvider`` accessible as a property of ``web3`` instances.

3.5.0
-----

* Deprecate ``web3.providers.rpc.RPCProvider``
* Deprecate ``web3.providers.rpc.KeepAliveRPCProvider``
* Add new ``web3.providers.rpc.HTTPProvider``
* Remove hard dependency on gevent.

3.4.4
-----

* Bugfix for ``web3.eth.getTransaction`` when the hash is unknown.

3.4.3
-----

* Bugfix for event log data decoding to properly handle dynamic sized values.
* New ``web3.tester`` module to access extra RPC functionality from ``eth-testrpc``

3.4.2
-----

* Fix package so that ``eth-testrpc`` is not required.

3.4.1
-----

* Force gevent<1.2.0 until this issue is fixed: https://github.com/gevent/gevent/issues/916

3.4.0
-----

* Bugfix for contract instances to respect ``web3.eth.defaultAccount``
* Better error reporting when ABI decoding fails for contract method response.

3.3.0
-----

* New ``EthereumTesterProvider`` now available.  Faster test runs than ``TestRPCProvider``
* Updated underlying eth-testrpc requirement.

3.2.0
-----

* ``web3.shh`` is now implemented.
* Introduced ``KeepAliveRPCProvider`` to correctly recycle HTTP connections and use HTTP keep alive

3.1.1
-----

* Bugfix for contract transaction sending not respecting the
  ``web3.eth.defaultAccount`` configuration.

3.1.0
-----

* New DelegatedSigningManager and PrivateKeySigningManager classes.

3.0.2
-----

* Bugfix or IPCProvider not handling large JSON responses well.

3.0.1
-----

* Better RPC compliance to be compatable with the Parity JSON-RPC server.

3.0.0
-----

* ``Filter`` objects now support controlling the interval through which they poll
  using the ``poll_interval`` property

2.9.0
-----

* Bugfix generation of event topics.
* Web3.Iban now allows access to Iban address tools.

2.8.1
-----

* Bugfix for ``geth.ipc`` path on linux systems.

2.8.0
-----

* Changes to the ``Contract`` API:
    * ``Contract.deploy()`` parameter arguments renamed to args
    * ``Contract.deploy()`` now takes args and kwargs parameters to allow
      constructing with keyword arguments or positional arguments.
    * ``Contract.pastEvents`` now allows you to specify a ``fromBlock or
      ``toBlock.`` Previously these were forced to be ``'earliest'`` and
      ``web3.eth.blockNumber`` respectively.
    * ``Contract.call``, ``Contract.transact`` and ``Contract.estimateGas`` are now
      callable as class methods as well as instance methods. When called this
      way, an address must be provided with the transaction parameter.
    * ``Contract.call``, ``Contract.transact`` and ``Contract.estimateGas`` now allow
      specifying an alternate address for the transaction.
* ``RPCProvider`` now supports the following constructor arguments.
    * ``ssl`` for enabling SSL
    * ``connection_timeout`` and ``network_timeout`` for controlling the timeouts
      for requests.

2.7.1
-----

* Bugfix: Fix KeyError in merge_args_and_kwargs helper fn.

2.7.0
-----

* Bugfix for usage of block identifiers 'latest', 'earliest', 'pending'
* Sphinx documentation
* Non-data transactions now default to 90000 gas.
* Web3 object now has helpers set as static methods rather than being set at
  initialization.
* RPCProvider now takes a ``path`` parameter to allow configuration for requests
  to go to paths other than ``/``.

2.6.0
-----

* TestRPCProvider no longer dumps logging output to stdout and stderr.
* Bugfix for return types of ``address[]``
* Bugfix for event data types of ``address``

2.5.0
-----

* All transactions which contain a ``data`` element will now have their gas
  automatically estimated with 100k additional buffer.  This was previously
  only true with transactions initiated from a ``Contract`` object.

2.4.0
-----

* Contract functions can now be called using keyword arguments.

2.3.0
-----

* Upstream fixes for filters
* Filter APIs ``on`` and ``pastEvents`` now callable as both instance and class methods.

2.2.0
-----

* The filters that come back from the contract ``on`` and ``pastEvents`` methods
  now call their callbacks with the same data format as ``web3.js``.

2.1.1
-----

* Cast RPCProvider port to an integer.

2.1.0
-----

* Remove all monkeypatching

2.0.0
-----

* Pull in downstream updates to proper gevent usage.
* Fix ``eth_sign``
* Bugfix with contract operations mutating the transaction object that is passed in.
* More explicit linting ignore statements.

1.9.0
-----

* BugFix: fix for python3 only ``json.JSONDecodeError`` handling.

1.8.0
-----

* BugFix: ``RPCProvider`` not sending a content-type header
* Bugfix: ``web3.toWei`` now returns an integer instead of a decimal.Decimal

1.7.1
-----

* ``TestRPCProvider`` can now be imported directly from ``web3``

1.7.0
-----

* Add ``eth.admin`` interface.
* Bugfix: Format the return value of ``web3.eth.syncing``
* Bugfix: IPCProvider socket interactions are now more robust.

1.6.0
-----

* Downstream package upgrades for ``eth-testrpc`` and ``ethereum-tester-client`` to
  handle configuration of the Homestead and DAO fork block numbers.

1.5.0
-----

* Rename ``web3.contract._Contract`` to ``web3.contract.Contract``
  to expose it for static analysis and auto completion tools
* Allow passing string parameters to functions
* Automatically compute gas requirements for contract deployment and
* transactions.
* Contract Filters
* Block, Transaction, and Log filters
* ``web3.eth.txpool`` interface
* ``web3.eth.mining`` interface
* Fixes for encoding.

1.4.0
-----

* Bugfix to allow address types in constructor arguments.

1.3.0
-----

* Partial implementation of the ``web3.eth.contract`` interface.

1.2.0
-----

* Restructure project modules to be more *flat*
* Add ability to run test suite without the *slow* tests.
* Breakup ``encoding`` utils into smaller modules.
* Basic pep8 formatting.
* Apply python naming conventions to internal APIs
* Lots of minor bugfixes.
* Removal of dead code left behind from ``1.0.0`` refactor.
* Removal of ``web3/solidity`` module.

1.1.0
-----

* Add missing ``isConnected()`` method.
* Add test coverage for ``setProvider()``

1.0.1
-----

* Specify missing ``pyrlp`` and ``gevent`` dependencies

1.0.0
-----

* Massive refactor to the majority of the app.

0.1.0
-----

* Initial release
