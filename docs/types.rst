.. _types:

Types
=====

The ``web3.types`` module provides TypedDict definitions and type aliases for
use with static type checkers like mypy and pyright. These types enable IDE
autocompletion and catch type errors at development time.

.. note::

    This documentation covers the most commonly used types. For the complete
    and most up-to-date type definitions, see the source file:
    `web3/types.py <https://github.com/ethereum/web3.py/blob/main/web3/types.py>`_

Importing Types
---------------

All types are available from the ``web3.types`` module:

.. code-block:: python

    from web3.types import BlockData, TxData, TxReceipt, TxParams


Using Types in Your Code
------------------------

Here's an example of using types for better IDE support and type safety:

.. code-block:: python

    from web3 import Web3
    from web3.types import BlockData, TxData, TxReceipt, Wei

    def get_block_info(w3: Web3, block_number: int) -> BlockData:
        """Fetch block with proper type hints."""
        return w3.eth.get_block(block_number)

    def get_transaction_value(tx: TxData) -> Wei:
        """Extract transaction value with IDE autocomplete support."""
        return tx["value"]

    def process_receipt(receipt: TxReceipt) -> bool:
        """Check if transaction succeeded."""
        return receipt["status"] == 1


Block Types
-----------

.. py:class:: BlockData

    Block information returned by ``w3.eth.get_block()``. All fields are optional
    (``total=False``) as not all fields are present in every block.

    .. code-block:: python

        >>> from web3.types import BlockData
        >>> block: BlockData = w3.eth.get_block('latest')
        >>> block["number"]
        4022281
        >>> block["hash"]
        HexBytes('0xe8ad537a...')
        >>> block["gasUsed"]
        21000

    **Fields:**

    - ``baseFeePerGas``: *Wei* - Base fee per gas (EIP-1559)
    - ``blobGasUsed``: *int* - Total blob gas used in block (EIP-4844)
    - ``difficulty``: *int* - Block difficulty (pre-merge)
    - ``excessBlobGas``: *int* - Excess blob gas (EIP-4844)
    - ``extraData``: *HexBytes* - Extra data field
    - ``gasLimit``: *int* - Block gas limit
    - ``gasUsed``: *int* - Total gas used by all transactions
    - ``hash``: *HexBytes* - Block hash
    - ``logsBloom``: *HexBytes* - Bloom filter for logs
    - ``miner``: *ChecksumAddress* - Block producer address (pre-merge: miner, post-merge: fee recipient/proposer)
    - ``mixHash``: *HexBytes* - Mix hash
    - ``nonce``: *HexBytes* - Proof-of-work nonce (pre-merge)
    - ``number``: *BlockNumber* - Block number
    - ``parentBeaconBlockRoot``: *HexBytes* - Parent beacon block root (post-merge)
    - ``parentHash``: *HexBytes* - Parent block hash
    - ``receiptsRoot``: *HexBytes* - Receipts trie root
    - ``requestsHash``: *HexBytes* - Requests hash
    - ``sha3Uncles``: *HexBytes* - Uncles hash
    - ``size``: *int* - Block size in bytes
    - ``stateRoot``: *HexBytes* - State trie root
    - ``timestamp``: *Timestamp* - Unix timestamp
    - ``totalDifficulty``: *int* - Total chain difficulty (pre-merge)
    - ``transactions``: *Sequence[HexBytes] | Sequence[TxData]* - Transaction hashes or full data (homogeneous: either all hashes or all ``TxData``, never mixed)
    - ``transactionsRoot``: *HexBytes* - Transactions trie root
    - ``uncles``: *Sequence[HexBytes]* - Uncle block hashes
    - ``withdrawals``: *Sequence[WithdrawalData]* - Validator withdrawals (post-merge)
    - ``withdrawalsRoot``: *HexBytes* - Withdrawals trie root
    - ``proofOfAuthorityData``: *HexBytes* - POA data (when using POA middleware)


.. py:class:: WithdrawalData

    Validator withdrawal data included in post-merge blocks.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import WithdrawalData, BlockData
        >>> block: BlockData = w3.eth.get_block('latest')
        >>> withdrawal: WithdrawalData = block["withdrawals"][0]
        >>> withdrawal["validator_index"]
        12345
        >>> withdrawal["amount"]
        32000000000  # in Gwei

    **Fields:**

    - ``index``: *int* - Withdrawal index
    - ``validator_index``: *int* - Validator index
    - ``address``: *ChecksumAddress* - Withdrawal recipient address
    - ``amount``: *Gwei* - Withdrawal amount (always in Gwei, not Wei)


.. py:class:: Uncle

    Uncle (ommer) block data returned by ``w3.eth.get_uncle_by_block()``.
    All fields are required (``total=True``).

    .. note::

        This is a **legacy type** for pre-merge (Proof of Work) blocks only.
        Uncle blocks do not exist in post-merge (Proof of Stake) Ethereum.

    .. code-block:: python

        >>> from web3.types import Uncle
        >>> uncle: Uncle = w3.eth.get_uncle_by_block(12345678, 0)
        >>> uncle["author"]
        '0x742d35Cc6634C0532925a3b844Bc9e7595f...'
        >>> uncle["number"]
        '0xbc614d'

    **Fields:**

    - ``author``: *ChecksumAddress* - Block author (formatted address)
    - ``difficulty``: *HexStr* - Block difficulty
    - ``extraData``: *HexStr* - Extra data field
    - ``gasLimit``: *HexStr* - Block gas limit
    - ``gasUsed``: *HexStr* - Total gas used
    - ``hash``: *HexBytes* - Block hash
    - ``logsBloom``: *HexStr* - Bloom filter for logs
    - ``miner``: *HexBytes* - Miner address (raw bytes, use ``author`` for formatted address)
    - ``mixHash``: *HexBytes* - Mix hash
    - ``nonce``: *HexStr* - Proof-of-work nonce
    - ``number``: *HexStr* - Block number
    - ``parentHash``: *HexBytes* - Parent block hash
    - ``receiptsRoot``: *HexBytes* - Receipts trie root
    - ``sealFields``: *Sequence[HexStr]* - Seal fields
    - ``sha3Uncles``: *HexBytes* - Uncles hash
    - ``size``: *int* - Block size in bytes
    - ``stateRoot``: *HexBytes* - State trie root
    - ``timestamp``: *Timestamp* - Unix timestamp
    - ``totalDifficulty``: *HexStr* - Total chain difficulty
    - ``transactions``: *Sequence[HexBytes]* - Transaction hashes
    - ``transactionsRoot``: *HexBytes* - Transactions trie root
    - ``uncles``: *Sequence[HexBytes]* - Uncle block hashes


Transaction Types
-----------------

.. py:class:: TxData

    Transaction data returned from the chain (e.g., from ``w3.eth.get_transaction()``).
    All fields are optional (``total=False``) as different transaction types have different fields.

    .. note::

        Fields for newer transaction types:

        - **EIP-2930** (type 1): ``accessList``
        - **EIP-1559** (type 2): ``maxFeePerGas``, ``maxPriorityFeePerGas``
        - **EIP-4844** (type 3): ``blobVersionedHashes``, ``maxFeePerBlobGas``
        - **EIP-7702** (type 4): ``authorizationList``

    .. code-block:: python

        >>> from web3.types import TxData
        >>> tx: TxData = w3.eth.get_transaction(tx_hash)
        >>> tx["from"]
        '0x742d35Cc6634C0532925a3b844Bc9e7595f...'
        >>> tx["value"]
        1000000000000000000
        >>> tx["gasPrice"]
        20000000000

    **Fields:**

    - ``accessList``: *AccessList* - EIP-2930 access list
    - ``authorizationList``: *Sequence[SetCodeAuthorizationData]* - EIP-7702 authorizations (signed, chain-returned data)
    - ``blobVersionedHashes``: *Sequence[HexBytes]* - Blob hashes (EIP-4844)
    - ``blockHash``: *HexBytes* - Hash of containing block
    - ``blockNumber``: *BlockNumber* - Number of containing block
    - ``chainId``: *int* - Chain ID
    - ``data``: *Union[bytes, HexStr]* - Transaction input data (legacy field, prefer ``input``)
    - ``from``: *ChecksumAddress* - Sender address
    - ``gas``: *int* - Gas limit
    - ``gasPrice``: *Wei* - Gas price (type 0 and type 1 transactions)
    - ``hash``: *HexBytes* - Transaction hash
    - ``input``: *HexBytes* - Transaction input data (canonical field)
    - ``maxFeePerBlobGas``: *Wei* - Max fee per blob gas (EIP-4844)
    - ``maxFeePerGas``: *Wei* - Max total fee per gas (EIP-1559)
    - ``maxPriorityFeePerGas``: *Wei* - Max priority fee per gas (EIP-1559)
    - ``nonce``: *Nonce* - Transaction nonce
    - ``r``: *HexBytes* - ECDSA signature r value
    - ``s``: *HexBytes* - ECDSA signature s value
    - ``to``: *ChecksumAddress* - Recipient address
    - ``transactionIndex``: *int* - Index within the block
    - ``type``: *Union[int, HexStr]* - Transaction type (0=legacy, 1=EIP-2930, 2=EIP-1559, 3=EIP-4844, 4=EIP-7702)
    - ``v``: *int* - ECDSA signature recovery id (type 0 transactions)
    - ``value``: *Wei* - Value in Wei
    - ``yParity``: *int* - ECDSA signature recovery parity (type 1+ transactions)


.. py:class:: TxParams

    Transaction parameters for sending transactions (e.g., to ``w3.eth.send_transaction()``).
    All fields are optional (``total=False``). Use either ``gasPrice`` (legacy) or
    ``maxFeePerGas``/``maxPriorityFeePerGas`` (EIP-1559), not both.

    .. code-block:: python

        >>> from web3.types import TxParams
        >>> tx_params: TxParams = {
        ...     "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f...",
        ...     "to": "0x1234567890123456789012345678901234567890",
        ...     "value": 1000000000000000000,
        ...     "gas": 21000,
        ... }
        >>> w3.eth.send_transaction(tx_params)

    **Fields:**

    - ``accessList``: *AccessList* - EIP-2930 access list
    - ``authorizationList``: *Sequence[SetCodeAuthorizationParams | SignedSetCodeAuthorization]* - EIP-7702 authorizations (use ``SetCodeAuthorizationParams`` for unsigned, ``SignedSetCodeAuthorization`` for pre-signed)
    - ``blobVersionedHashes``: *Sequence[Union[str, HexStr, bytes, HexBytes]]* - Blob hashes (EIP-4844)
    - ``chainId``: *int* - Chain ID
    - ``data``: *Union[bytes, HexStr]* - Contract call data or deployment bytecode
    - ``from``: *Union[Address, ChecksumAddress, str]* - Sender address or ENS name
    - ``gas``: *int* - Gas limit
    - ``gasPrice``: *Wei* - Gas price (type 0 and type 1 transactions)
    - ``maxFeePerBlobGas``: *Union[str, Wei]* - Max fee per blob gas (EIP-4844)
    - ``maxFeePerGas``: *Union[str, Wei]* - Max total fee per gas (EIP-1559)
    - ``maxPriorityFeePerGas``: *Union[str, Wei]* - Max priority fee per gas (EIP-1559)
    - ``nonce``: *Nonce* - Transaction nonce (auto-filled if not provided)
    - ``to``: *Union[Address, ChecksumAddress, str]* - Recipient address or ENS name
    - ``type``: *Union[int, HexStr]* - Transaction type
    - ``value``: *Wei* - Value in Wei to transfer


.. py:class:: TxReceipt

    Transaction receipt returned by ``w3.eth.get_transaction_receipt()`` or
    ``w3.eth.wait_for_transaction_receipt()``. All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import TxReceipt
        >>> receipt: TxReceipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        >>> receipt["status"]
        1  # 1 = success, 0 = failure
        >>> receipt["gasUsed"]
        21000
        >>> receipt["logs"]
        [...]

    **Fields:**

    - ``blockHash``: *HexBytes* - Hash of containing block
    - ``blockNumber``: *BlockNumber* - Number of containing block
    - ``contractAddress``: *Optional[ChecksumAddress]* - Deployed contract address (``None`` if not a deployment)
    - ``cumulativeGasUsed``: *int* - Total gas used in block up to this transaction
    - ``effectiveGasPrice``: *Wei* - Actual gas price paid
    - ``from``: *ChecksumAddress* - Sender address
    - ``gasUsed``: *int* - Gas used by this transaction
    - ``logs``: *list[LogReceipt]* - List of log entries generated
    - ``logsBloom``: *HexBytes* - Bloom filter for logs
    - ``root``: *HexStr* - State root (pre-Byzantium)
    - ``status``: *int* - 1 for success, 0 for failure (post-Byzantium)
    - ``to``: *ChecksumAddress* - Recipient address
    - ``transactionHash``: *HexBytes* - Transaction hash
    - ``transactionIndex``: *int* - Index within the block
    - ``type``: *int* - Transaction type


.. py:class:: SignedTx

    TypedDict representing signed transaction data structure.
    All fields are optional (``total=False``).

    .. note::

        ``w3.eth.account.sign_transaction()`` returns an ``eth_account.SignedTransaction``
        **object** (not a ``SignedTx`` dict). Use the object's attributes:

        .. code-block:: python

            >>> signed = w3.eth.account.sign_transaction(tx_params, private_key)
            >>> signed.raw_transaction  # bytes - RLP encoded transaction
            b'\x02\xf8...'
            >>> signed.hash  # HexBytes - transaction hash
            HexBytes('0xabc123...')
            >>> w3.eth.send_raw_transaction(signed.raw_transaction)

        The ``SignedTx`` TypedDict is provided for type annotations in contexts
        where signed transaction data is represented as a dictionary.

    .. code-block:: python

        >>> from web3.types import SignedTx, TxParams
        >>> # Creating a SignedTx dict manually:
        >>> signed_tx: SignedTx = {
        ...     "raw": b'\xf8...',
        ...     "tx": {"to": "0x...", "value": 1000},
        ... }

    **Fields:**

    - ``raw``: *bytes* - Raw signed transaction bytes (RLP encoded)
    - ``tx``: *TxParams* - Transaction parameters that were signed


Event and Log Types
-------------------

.. py:class:: EventData

    Decoded event log data returned by contract event filters.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import EventData
        >>> events: list[EventData] = contract.events.Transfer().get_logs()
        >>> events[0]["args"]
        {'from': '0x...', 'to': '0x...', 'value': 1000}
        >>> events[0]["event"]
        'Transfer'

    **Fields:**

    - ``address``: *ChecksumAddress* - Contract address that emitted the event
    - ``args``: *dict[str, Any]* - Decoded event arguments
    - ``blockHash``: *HexBytes* - Hash of containing block
    - ``blockNumber``: *int* - Number of containing block
    - ``event``: *str* - Event name
    - ``logIndex``: *int* - Log index within the block
    - ``transactionHash``: *HexBytes* - Transaction hash
    - ``transactionIndex``: *int* - Transaction index within the block


.. py:class:: LogReceipt

    Raw log receipt data from the blockchain.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import LogReceipt
        >>> logs: list[LogReceipt] = w3.eth.get_logs({"address": contract_address})
        >>> logs[0]["topics"]
        [HexBytes('0xddf252ad...'), ...]
        >>> logs[0]["data"]
        HexBytes('0x...')

    **Fields:**

    - ``address``: *ChecksumAddress* - Contract address
    - ``blockHash``: *HexBytes* - Hash of containing block
    - ``blockNumber``: *BlockNumber* - Number of containing block
    - ``data``: *HexBytes* - Non-indexed event data
    - ``logIndex``: *int* - Log index within the block
    - ``removed``: *bool* - Whether log was removed due to chain reorg
    - ``topics``: *Sequence[HexBytes]* - List of indexed event topics
    - ``transactionHash``: *HexBytes* - Transaction hash
    - ``transactionIndex``: *int* - Transaction index within the block


.. py:class:: FilterParams

    Parameters for creating event filters.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import FilterParams
        >>> filter_params: FilterParams = {
        ...     "fromBlock": 1000000,
        ...     "toBlock": "latest",
        ...     "address": "0x...",
        ...     "topics": [None, "0x..."],
        ... }
        >>> w3.eth.get_logs(filter_params)

    **Fields:**

    - ``address``: *Address | ChecksumAddress | list[Address] | list[ChecksumAddress]* - Contract address(es) to filter
    - ``blockHash``: *HexBytes* - Specific block hash (alternative to fromBlock/toBlock)
    - ``fromBlock``: *BlockIdentifier* - Starting block number or tag
    - ``toBlock``: *BlockIdentifier* - Ending block number or tag
    - ``topics``: *Sequence[TopicFilter]* - Topic filters for indexed event parameters


.. py:data:: TopicFilter

    Type alias for event topic filtering with AND/OR pattern matching.

    .. code-block:: python

        # TopicFilter can be:
        # - None: wildcard, matches any value at this position
        # - bytes32 hash: single topic that must match exactly
        # - list of hashes: OR condition, at least one must match

        # Example: Match Transfer events TO a specific address
        >>> filter_params: FilterParams = {
        ...     "topics": [
        ...         "0xddf252ad...",  # Transfer event signature (position 0)
        ...         None,              # Any sender (position 1)
        ...         "0x742d35Cc...",   # Specific recipient (position 2)
        ...     ]
        ... }

        # Example: Match transfers TO address A OR address B
        >>> filter_params: FilterParams = {
        ...     "topics": [
        ...         "0xddf252ad...",
        ...         None,
        ...         ["0xaddr_A...", "0xaddr_B..."],  # OR condition
        ...     ]
        ... }

    **Type definition:**

    ``Union[None, Hash32, Sequence[Union[None, Hash32]], Sequence[TopicFilter]]``


Fee and Gas Types
-----------------

.. py:class:: FeeHistory

    Fee history data returned by ``w3.eth.fee_history()``.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import FeeHistory
        >>> history: FeeHistory = w3.eth.fee_history(10, "latest", [25, 75])
        >>> history["baseFeePerGas"]
        [20000000000, 21000000000, ...]
        >>> history["reward"]
        [[1000000000, 2000000000], ...]

    **Fields:**

    - ``baseFeePerGas``: *list[Wei]* - Base fee per gas for each block (length = block_count + 1)
    - ``gasUsedRatio``: *list[float]* - Gas used ratio (gasUsed/gasLimit) for each block
    - ``oldestBlock``: *BlockNumber* - Oldest block number in the history
    - ``reward``: *list[list[Wei]]* - Priority fee at requested percentiles for each block (outer list = blocks, inner list = percentiles)


EIP-2930 Access List Types
--------------------------

.. py:class:: AccessListEntry

    Access list entry for EIP-2930 transactions.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import AccessListEntry
        >>> entry: AccessListEntry = {
        ...     "address": "0x...",
        ...     "storageKeys": ["0x...", "0x..."],
        ... }

    **Fields:**

    - ``address``: *HexStr* - Contract address to pre-warm
    - ``storageKeys``: *Sequence[HexStr]* - Storage slot keys to pre-warm


State Override Types
--------------------

.. py:class:: StateOverrideParams

    Parameters for overriding account state during ``eth_call``.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import StateOverrideParams
        >>> override: StateOverrideParams = {
        ...     "balance": 1000000000000000000,
        ...     "code": "0x...",
        ... }
        >>> w3.eth.call(tx, state_override={address: override})

    **Fields:**

    - ``balance``: *Wei | None* - Override account balance
    - ``nonce``: *int | None* - Override account nonce
    - ``code``: *bytes | HexStr | None* - Override contract bytecode
    - ``state``: *dict[HexStr, HexStr] | None* - Override full storage state (replaces entire storage)
    - ``stateDiff``: *dict[HexStr, HexStr] | None* - Override specific storage slots (merges with existing)


.. py:data:: StateOverride

    Type alias for mapping addresses to their state overrides.

    .. code-block:: python

        >>> from web3.types import StateOverride, StateOverrideParams
        >>> state_override: StateOverride = {
        ...     "0x742d35Cc6634C0532925a3b844Bc9e7595f...": {
        ...         "balance": 1000000000000000000,
        ...     },
        ...     "0x1234567890123456789012345678901234567890": {
        ...         "code": "0x608060...",
        ...     },
        ... }
        >>> w3.eth.call(tx_params, block_identifier="latest", state_override=state_override)

    **Type definition:**

    ``dict[Union[str, Address, ChecksumAddress], StateOverrideParams]``


Proof Types
-----------

.. py:class:: StorageProof

    Storage slot proof data, part of ``MerkleProof.storageProof``.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import StorageProof, MerkleProof
        >>> proof: MerkleProof = w3.eth.get_proof(address, [storage_key], "latest")
        >>> storage: StorageProof = proof["storageProof"][0]
        >>> storage["key"]
        '0x0000000000000000000000000000000000000000000000000000000000000000'
        >>> storage["value"]
        HexBytes('0x...')

    **Fields:**

    - ``key``: *HexStr* - Storage slot key
    - ``proof``: *Sequence[HexStr]* - Merkle proof for the storage slot
    - ``value``: *HexBytes* - Storage slot value


.. py:class:: MerkleProof

    Account and storage proof returned by ``w3.eth.get_proof()``.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import MerkleProof
        >>> proof: MerkleProof = w3.eth.get_proof(address, [storage_key], "latest")
        >>> proof["balance"]
        1000000000000000000
        >>> proof["storageProof"]
        [{"key": "0x...", "value": "0x...", "proof": [...]}]

    **Fields:**

    - ``address``: *ChecksumAddress* - Account address
    - ``accountProof``: *Sequence[HexStr]* - Merkle proof for account
    - ``balance``: *int* - Account balance in Wei
    - ``codeHash``: *HexBytes* - Hash of account code
    - ``nonce``: *Nonce* - Account nonce
    - ``storageHash``: *HexBytes* - Hash of storage root
    - ``storageProof``: *Sequence[StorageProof]* - Merkle proofs for storage slots


Transaction Pool Types
----------------------

.. py:class:: TxPoolContent

    Transaction pool content from ``w3.geth.txpool.content()``.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import TxPoolContent
        >>> content: TxPoolContent = w3.geth.txpool.content()
        >>> content["pending"]
        {'0x742d35Cc...': {0: [...], 1: [...]}}
        >>> content["queued"]
        {'0x1234567...': {5: [...]}}

    **Fields:**

    - ``pending``: *dict[ChecksumAddress, dict[Nonce, list[PendingTx]]]* - Pending transactions by sender and nonce
    - ``queued``: *dict[ChecksumAddress, dict[Nonce, list[PendingTx]]]* - Queued transactions by sender and nonce


.. py:class:: TxPoolInspect

    Transaction pool inspection from ``w3.geth.txpool.inspect()``.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import TxPoolInspect
        >>> inspect: TxPoolInspect = w3.geth.txpool.inspect()
        >>> inspect["pending"]
        {'0x742d35Cc...': {0: '0x1234...: 0 wei + 21000 gas × 20 gwei'}}
        >>> inspect["queued"]
        {'0x1234567...': {5: '0xabcd...: 1000000 wei + 50000 gas × 25 gwei'}}

    **Fields:**

    - ``pending``: *dict[ChecksumAddress, dict[Nonce, str]]* - Summary of pending transactions
    - ``queued``: *dict[ChecksumAddress, dict[Nonce, str]]* - Summary of queued transactions


.. py:class:: TxPoolStatus

    Transaction pool status from ``w3.geth.txpool.status()``.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import TxPoolStatus
        >>> status: TxPoolStatus = w3.geth.txpool.status()
        >>> status["pending"]
        12
        >>> status["queued"]
        3

    **Fields:**

    - ``pending``: *int* - Number of pending transactions
    - ``queued``: *int* - Number of queued transactions


.. py:class:: PendingTx

    Pending transaction data from the transaction pool.
    All fields are optional (``total=False``).

    .. note::

        Numeric fields (``gas``, ``gasPrice``, ``nonce``, ``value``, etc.) are
        returned as ``HexBytes`` (hex-encoded), not as integers. You must decode
        them if you need numeric values: ``int(pending_tx["gas"].hex(), 16)``.

    .. code-block:: python

        >>> from web3.types import PendingTx, TxPoolContent
        >>> content: TxPoolContent = w3.geth.txpool.content()
        >>> pending_tx: PendingTx = content["pending"]["0x742d35Cc..."][0][0]
        >>> pending_tx["hash"]
        HexBytes('0xabc123...')
        >>> pending_tx["from"]
        '0x742d35Cc6634C0532925a3b844Bc9e7595f...'

    **Fields:**

    - ``blockHash``: *HexBytes* - Always null for pending transactions
    - ``blockNumber``: *None* - Always null for pending transactions
    - ``from``: *ChecksumAddress* - Sender address
    - ``gas``: *HexBytes* - Gas limit
    - ``gasPrice``: *HexBytes* - Gas price (type 0 and type 1 transactions)
    - ``maxFeePerGas``: *HexBytes* - Max fee per gas (EIP-1559)
    - ``maxPriorityFeePerGas``: *HexBytes* - Max priority fee (EIP-1559)
    - ``hash``: *HexBytes* - Transaction hash
    - ``input``: *HexBytes* - Transaction input data
    - ``nonce``: *HexBytes* - Transaction nonce
    - ``to``: *ChecksumAddress* - Recipient address
    - ``transactionIndex``: *None* - Always null for pending transactions
    - ``value``: *HexBytes* - Value in Wei


Debug and Trace Types
---------------------

.. py:class:: CallTrace

    Call trace data from debug tracing.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import CallTrace
        >>> trace: CallTrace = w3.tracing.trace_call(tx_params, ["trace"], "latest")
        >>> trace["type"]
        'CALL'
        >>> trace["from"]
        '0x742d35Cc6634C0532925a3b844Bc9e7595f...'
        >>> trace["gasUsed"]
        21000

    **Fields:**

    - ``type``: *str* - Call type (CALL, DELEGATECALL, STATICCALL, CREATE, etc.)
    - ``from``: *ChecksumAddress* - Caller address
    - ``to``: *ChecksumAddress* - Callee address
    - ``value``: *Wei* - Value transferred in Wei
    - ``gas``: *int* - Gas provided for the call
    - ``gasUsed``: *int* - Gas used by the call
    - ``input``: *HexBytes* - Call input data
    - ``output``: *HexBytes* - Call output data
    - ``error``: *str* - Error message if call failed
    - ``revertReason``: *str* - Revert reason if reverted
    - ``calls``: *Sequence[CallTrace]* - Nested internal calls
    - ``logs``: *Sequence[CallTraceLog]* - Logs emitted during the call


.. py:class:: CallTraceLog

    Log entry emitted during a traced call.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import CallTrace, CallTraceLog
        >>> trace: CallTrace = w3.tracing.trace_call(tx_params, ["trace"], "latest")
        >>> if trace.get("logs"):
        ...     log: CallTraceLog = trace["logs"][0]
        ...     log["address"]
        ...     '0x6B175474E89094C44Da98b954EescdeCB5...'
        ...     log["topics"]
        ...     [HexBytes('0xddf252ad...'), ...]

    **Fields:**

    - ``address``: *ChecksumAddress* - Contract address that emitted the log
    - ``data``: *HexBytes* - Non-indexed log data
    - ``topics``: *Sequence[HexBytes]* - Indexed log topics
    - ``position``: *int* - Position of the log in the trace


.. py:class:: TraceFilterParams

    Parameters for filtering traces.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import TraceFilterParams
        >>> params: TraceFilterParams = {
        ...     "fromBlock": 1000000,
        ...     "toBlock": 1000100,
        ...     "fromAddress": ["0x742d35Cc..."],
        ... }
        >>> traces = w3.tracing.trace_filter(params)

    **Fields:**

    - ``after``: *int* - Skip first N results
    - ``count``: *int* - Limit number of results
    - ``fromAddress``: *Sequence[Address | ChecksumAddress | ENS]* - Filter by sender addresses
    - ``fromBlock``: *BlockIdentifier* - Starting block
    - ``toAddress``: *Sequence[Address | ChecksumAddress | ENS]* - Filter by recipient addresses
    - ``toBlock``: *BlockIdentifier* - Ending block


Node Information Types
----------------------

.. py:class:: Protocol

    Protocol information for a node or peer connection.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import Protocol, NodeInfo
        >>> info: NodeInfo = w3.geth.admin.node_info()
        >>> eth_protocol: Protocol = info["protocols"]["eth"]
        >>> eth_protocol["network"]
        1  # Mainnet
        >>> eth_protocol["version"]
        68

    **Fields:**

    - ``difficulty``: *int* - Current network difficulty
    - ``head``: *HexStr* - Hash of the current head block
    - ``network``: *int* - Network ID
    - ``version``: *int* - Protocol version


.. py:class:: NodeInfo

    Node information from ``w3.geth.admin.node_info()``.
    All fields are required (``total=True``).

    .. code-block:: python

        >>> from web3.types import NodeInfo
        >>> info: NodeInfo = w3.geth.admin.node_info()
        >>> info["name"]
        'Geth/v1.10.0-stable/linux-amd64/go1.16'
        >>> info["enode"]
        'enode://abc123...@127.0.0.1:30303'
        >>> info["protocols"]
        {'eth': {'network': 1, 'difficulty': 123456789, ...}}

    **Fields:**

    - ``enode``: *EnodeURI* - Enode URI for connecting to this node
    - ``id``: *HexStr* - Node ID (public key)
    - ``ip``: *str* - IP address
    - ``listenAddr``: *str* - Listen address (ip:port)
    - ``name``: *str* - Node client name and version
    - ``ports``: *dict[str, int]* - Port mappings (discovery, listener)
    - ``protocols``: *dict[str, Protocol]* - Protocol information


.. py:class:: Peer

    Peer information from ``w3.geth.admin.peers()``.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import Peer
        >>> peers: list[Peer] = w3.geth.admin.peers()
        >>> peers[0]["name"]
        'Geth/v1.10.0-stable/linux-amd64/go1.16'
        >>> peers[0]["caps"]
        ['eth/66', 'eth/67', 'snap/1']
        >>> peers[0]["network"]
        {'localAddress': '192.168.1.1:30303', 'remoteAddress': '10.0.0.1:30303'}

    **Fields:**

    - ``caps``: *Sequence[str]* - Peer capabilities
    - ``id``: *HexStr* - Peer ID (public key)
    - ``name``: *str* - Peer client name and version
    - ``network``: *dict[str, str]* - Network information
    - ``protocols``: *dict[str, Protocol]* - Protocol details


RPC Types
---------

.. py:class:: RPCRequest

    JSON-RPC request structure.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import RPCRequest
        >>> request: RPCRequest = {
        ...     "jsonrpc": "2.0",
        ...     "method": "eth_blockNumber",
        ...     "params": [],
        ...     "id": 1,
        ... }
        >>> response = w3.provider.make_request(request["method"], request["params"])

    **Fields:**

    - ``id``: *Optional[Union[int, str]]* - Request ID
    - ``jsonrpc``: *Literal["2.0"]* - JSON-RPC version
    - ``method``: *RPCEndpoint* - RPC method name
    - ``params``: *Any* - Method parameters


.. py:class:: RPCResponse

    JSON-RPC response structure.
    All fields are optional (``total=False``).

    .. code-block:: python

        >>> from web3.types import RPCResponse
        >>> response: RPCResponse = w3.provider.make_request("eth_blockNumber", [])
        >>> response["result"]
        '0x10d4f'  # Block number in hex
        >>> response["jsonrpc"]
        '2.0'
        >>> response["id"]
        1

    **Fields:**

    - ``error``: *RPCError* - Error object (if request failed)
    - ``id``: *Optional[Union[int, str]]* - Request ID
    - ``jsonrpc``: *Literal["2.0"]* - JSON-RPC version
    - ``result``: *Any* - Result data (if request succeeded)
    - ``method``: *Literal["eth_subscription"]* - Only present for subscription notifications
    - ``params``: *EthSubscriptionParams* - Only present for subscription notifications


.. py:class:: RPCError

    JSON-RPC error response.
    ``data`` field is optional, others are required.

    .. code-block:: python

        >>> from web3.types import RPCError, RPCResponse
        >>> response: RPCResponse = w3.provider.make_request("eth_call", [{"to": "0x0"}, "latest"])
        >>> if "error" in response:
        ...     error: RPCError = response["error"]
        ...     error["code"]
        ...     -32000
        ...     error["message"]
        ...     'execution reverted'

    **Fields:**

    - ``code``: *int* - JSON-RPC error code
    - ``message``: *str* - Human-readable error message
    - ``data``: *str* - Additional error data (optional)


Type Aliases
------------

The module also provides useful type aliases:

.. code-block:: python

    from web3.types import (
        Wei,              # int - Value in Wei
        Gwei,             # int - Value in Gwei
        Nonce,            # int - Transaction nonce
        Timestamp,        # int - Unix timestamp
        BlockIdentifier,  # Union of block number, hash, or tag
        BlockParams,      # Literal["latest", "earliest", "pending", "safe", "finalized"]
    )


Integration with Type Checkers
------------------------------

mypy
****

Add web3.py to your mypy configuration:

.. code-block:: ini

    # mypy.ini or pyproject.toml [tool.mypy]
    [mypy]
    plugins = []

    [mypy-web3.*]
    ignore_missing_imports = False

pyright / pylance
*****************

web3.py includes inline type annotations that work out of the box with pyright
and VS Code's Pylance extension.

Example with full typing:

.. code-block:: python

    from web3 import Web3
    from web3.types import BlockData, TxReceipt, Wei

    def analyze_block(w3: Web3, block_id: int) -> dict[str, int]:
        block: BlockData = w3.eth.get_block(block_id, full_transactions=True)

        total_value: Wei = Wei(0)
        for tx in block["transactions"]:
            if isinstance(tx, dict):  # Full transaction data
                total_value = Wei(total_value + tx.get("value", 0))

        return {
            "tx_count": len(block["transactions"]),
            "total_value_wei": total_value,
            "gas_used": block["gasUsed"],
        }


Complete Type Reference
-----------------------

The following types are available in ``web3.types``:

**Block & Chain:**
  ``BlockData``, ``Uncle``, ``WithdrawalData``, ``BlockIdentifier``, ``BlockParams``

**Transactions:**
  ``TxData``, ``TxParams``, ``TxReceipt``, ``SignedTx``, ``PendingTx``, ``BlockReceipts``

**Events & Logs:**
  ``EventData``, ``LogReceipt``, ``FilterParams``, ``LogsSubscriptionArg``

**Fees & Gas:**
  ``FeeHistory``, ``Wei``, ``Gwei``

**Access Lists:**
  ``AccessListEntry``, ``AccessList``, ``CreateAccessListResponse``

**State:**
  ``StateOverrideParams``, ``StateOverride``

**Proofs:**
  ``MerkleProof``, ``StorageProof``

**Transaction Pool:**
  ``TxPoolContent``, ``TxPoolInspect``, ``TxPoolStatus``, ``PendingTx``

**Debug & Tracing:**
  ``CallTrace``, ``CallTraceLog``, ``TraceFilterParams``, ``TraceConfig``,
  ``TraceData``, ``OpcodeTrace``, ``StructLog``, ``DiffModeTrace``,
  ``PrestateTrace``, ``FourByteTrace``

**Node & Network:**
  ``NodeInfo``, ``Peer``, ``Protocol``, ``SyncStatus``, ``SyncProgress``

**RPC:**
  ``RPCRequest``, ``RPCResponse``, ``RPCError``

**Subscriptions:**
  ``SubscriptionType``, ``SubscriptionResponse``, ``EthSubscriptionParams``,
  ``EthSubscriptionResult``, ``FormattedEthSubscriptionResponse``, ``LogsSubscriptionArg``,
  ``BlockTypeSubscriptionResponse``, ``TransactionTypeSubscriptionResponse``,
  ``LogsSubscriptionResponse``, ``SyncingSubscriptionResponse``,
  ``GethSyncingSubscriptionResponse``

**Geth-specific:**
  ``GethWallet``, ``GethSyncingStatus``, ``GethSyncingSubscriptionResult``

**EIP-7702 (Set Code):**
  ``SetCodeAuthorizationData``, ``SetCodeAuthorizationParams``

**Simulation (eth_simulateV1):**
  ``SimulateV1Payload``, ``SimulateV1Result``, ``SimulateV1CallResult``,
  ``BlockStateCallV1``

**Internal/Formatters:**
  ``FormattersDict``, ``Formatters``

**Aliases:**
  ``Wei``, ``Gwei``, ``Nonce``, ``Timestamp``, ``ENS``, ``EnodeURI``,
  ``RPCEndpoint``, ``BlockIdentifier``, ``BlockParams``, ``LatestBlockParam``,
  ``AccessList``, ``BlockTrace``, ``FilterTrace``, ``TraceMode``
