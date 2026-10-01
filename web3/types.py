from collections.abc import Callable, Coroutine, Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NewType,
    Optional,
    TypedDict,
    TypeVar,
    Union,
)

from eth_account.datastructures import (
    SignedSetCodeAuthorization,
)
from eth_typing import (
    Address,
    BlockNumber,
    ChecksumAddress,
    Hash32,
    HexStr,
)
from hexbytes import (
    HexBytes,
)

from web3._utils.abi_element_identifiers import (
    FallbackFn,
    ReceiveFn,
)
from web3._utils.compat import (
    NotRequired,
)

if TYPE_CHECKING:
    from web3.contract.base_contract import (
        BaseContractEvent,
        BaseContractFunction,
    )
    from web3.main import (  # noqa: F401
        AsyncWeb3,
        Web3,
    )


TFunc = TypeVar("TFunc", bound=Callable[..., Any])
TParams = TypeVar("TParams")
TReturn = TypeVar("TReturn")
TValue = TypeVar("TValue")

BlockParams = Literal["latest", "earliest", "pending", "safe", "finalized"]
BlockIdentifier = Union[BlockParams, BlockNumber, Hash32, HexStr, HexBytes, int]
LatestBlockParam = Literal["latest"]

ABIElementIdentifier = Union[str, type[FallbackFn], type[ReceiveFn]]

# bytes, hexbytes, or hexstr representing a 32 byte hash
_Hash32 = Union[Hash32, HexBytes, HexStr]

# --- ``TopicFilter`` type for event log filtering with AND/OR patterns --- #
# - ``None``: wildcard, matches any value at this position
# - ``_Hash32``: single topic that must match exactly
# - ``Sequence[Union[None, _Hash32]]``: OR condition, at least one must match
# - ``Sequence[Sequence[...]]``: nested OR conditions
TopicFilter = Union[
    None,
    _Hash32,
    Sequence[None | _Hash32],
    Sequence["TopicFilter"],
]

EnodeURI = NewType("EnodeURI", str)
ENS = NewType("ENS", str)
Nonce = NewType("Nonce", int)
RPCEndpoint = NewType("RPCEndpoint", str)
Timestamp = NewType("Timestamp", int)
Wei = NewType("Wei", int)
Gwei = NewType("Gwei", int)
Formatters = dict[RPCEndpoint, Callable[..., Any]]


class AccessListEntry(TypedDict):
    address: HexStr
    storageKeys: Sequence[HexStr]


AccessList = NewType("AccessList", Sequence[AccessListEntry])


class EventData(TypedDict):
    address: ChecksumAddress
    args: dict[str, Any]
    blockHash: HexBytes
    blockNumber: int
    event: str
    logIndex: int
    transactionHash: HexBytes
    transactionIndex: int


class RPCError(TypedDict):
    code: int
    message: str
    data: NotRequired[str]


class SetCodeAuthorizationData(TypedDict):
    chainId: int
    address: ChecksumAddress
    nonce: Nonce
    yParity: int
    r: int
    s: int


# syntax b/c "from" keyword not allowed w/ class construction
TxData = TypedDict(
    "TxData",
    {
        "accessList": AccessList,
        "authorizationList": Sequence[SetCodeAuthorizationData],
        "blobVersionedHashes": Sequence[HexBytes],
        "blockHash": HexBytes,
        "blockNumber": BlockNumber,
        "chainId": int,
        "data": bytes | HexStr,
        "from": ChecksumAddress,
        "gas": int,
        "gasPrice": Wei,
        "maxFeePerBlobGas": Wei,
        "maxFeePerGas": Wei,
        "maxPriorityFeePerGas": Wei,
        "hash": HexBytes,
        "input": HexBytes,
        "nonce": Nonce,
        "r": HexBytes,
        "s": HexBytes,
        "to": ChecksumAddress,
        "transactionIndex": int,
        "type": int | HexStr,
        "v": int,
        "value": Wei,
        "yParity": int,
    },
    total=False,
)


class SetCodeAuthorizationParams(TypedDict):
    chainId: int
    address: Address | ChecksumAddress | str
    nonce: Nonce
    yParity: int
    r: int
    s: int


# syntax b/c "from" keyword not allowed w/ class construction
TxParams = TypedDict(
    "TxParams",
    {
        "accessList": AccessList,
        "authorizationList": Sequence[
            SetCodeAuthorizationParams | SignedSetCodeAuthorization
        ],
        "blobVersionedHashes": Sequence[str | HexStr | bytes | HexBytes],
        "chainId": int,
        "data": bytes | HexStr,
        # addr or ens
        "from": Address | ChecksumAddress | str,
        "gas": int,
        # legacy pricing
        "gasPrice": Wei,
        "maxFeePerBlobGas": str | Wei,
        # dynamic fee pricing
        "maxFeePerGas": str | Wei,
        "maxPriorityFeePerGas": str | Wei,
        "nonce": Nonce,
        # addr or ens
        "to": Address | ChecksumAddress | str,
        "type": int | HexStr,
        "value": Wei,
    },
    total=False,
)


class WithdrawalData(TypedDict):
    index: int
    validatorIndex: int
    address: ChecksumAddress
    amount: Gwei


class BlockData(TypedDict, total=False):
    baseFeePerGas: Wei
    difficulty: int
    extraData: HexBytes
    gasLimit: int
    gasUsed: int
    hash: HexBytes
    logsBloom: HexBytes
    miner: ChecksumAddress
    mixHash: HexBytes
    nonce: HexBytes
    number: BlockNumber
    parentHash: HexBytes
    receiptsRoot: HexBytes
    sha3Uncles: HexBytes
    size: int
    stateRoot: HexBytes
    timestamp: Timestamp
    totalDifficulty: int
    transactions: Sequence[HexBytes] | Sequence[TxData]
    transactionsRoot: HexBytes
    uncles: Sequence[HexBytes]
    withdrawals: Sequence[WithdrawalData]
    withdrawalsRoot: HexBytes
    parentBeaconBlockRoot: HexBytes
    blobGasUsed: int
    excessBlobGas: int
    requestsHash: HexBytes

    # ExtraDataToPOAMiddleware replaces extraData w/ proofOfAuthorityData
    proofOfAuthorityData: HexBytes


class LogReceipt(TypedDict):
    address: ChecksumAddress
    blockHash: HexBytes
    blockNumber: BlockNumber
    data: HexBytes
    logIndex: int
    removed: bool
    topics: Sequence[HexBytes]
    transactionHash: HexBytes
    transactionIndex: int


class SubscriptionResponse(TypedDict):
    subscription: HexBytes


class BlockTypeSubscriptionResponse(SubscriptionResponse):
    result: BlockData


class TransactionTypeSubscriptionResponse(SubscriptionResponse):
    result: HexBytes | TxData


class LogsSubscriptionResponse(SubscriptionResponse):
    result: LogReceipt


class SyncProgress(TypedDict):
    isSyncing: bool
    startingBlock: int
    currentBlock: int
    highestBlock: int


class SyncingSubscriptionResponse(SubscriptionResponse):
    result: Literal[False] | SyncProgress


class GethSyncingStatus(TypedDict):
    currentBlock: int
    highestBlock: int
    knownStates: int
    pulledStates: int
    startingBlock: int


class GethSyncingSubscriptionResult(TypedDict):
    syncing: bool
    status: GethSyncingStatus


class GethSyncingSubscriptionResponse(SubscriptionResponse):
    result: GethSyncingSubscriptionResult


EthSubscriptionParams = Union[
    BlockTypeSubscriptionResponse,
    TransactionTypeSubscriptionResponse,
    LogsSubscriptionResponse,
    SyncingSubscriptionResponse,
    GethSyncingSubscriptionResponse,
]

RPCId = Optional[int | str]


class RPCRequest(TypedDict, total=False):
    id: RPCId
    jsonrpc: Literal["2.0"]
    method: RPCEndpoint
    params: Any


class RPCResponse(TypedDict, total=False):
    error: RPCError
    id: RPCId
    jsonrpc: Literal["2.0"]
    result: Any

    # eth_subscribe
    method: Literal["eth_subscription"]
    params: EthSubscriptionParams


EthSubscriptionResult = Union[
    BlockData,  # newHeads
    TxData,  # newPendingTransactions, full_transactions=True
    HexBytes,  # newPendingTransactions, full_transactions=False
    LogReceipt,  # logs
    SyncProgress,  # syncing
    GethSyncingSubscriptionResult,  # geth syncing
]


class FormattedEthSubscriptionResponse(TypedDict):
    subscription: HexStr
    result: EthSubscriptionResult


class CreateAccessListResponse(TypedDict):
    accessList: AccessList
    gasUsed: int


MakeRequestFn = Callable[[RPCEndpoint, Any], RPCResponse]
MakeBatchRequestFn = Callable[
    [list[tuple[RPCEndpoint, Any]]], list[RPCResponse] | RPCResponse
]
AsyncMakeRequestFn = Callable[[RPCEndpoint, Any], Coroutine[Any, Any, RPCResponse]]
AsyncMakeBatchRequestFn = Callable[
    [list[tuple[RPCEndpoint, Any]]],
    Coroutine[Any, Any, list[RPCResponse] | RPCResponse],
]


class FormattersDict(TypedDict, total=False):
    error_formatters: Formatters | None
    request_formatters: Formatters | None
    result_formatters: Formatters | None


class FilterParams(TypedDict, total=False):
    address: Address | ChecksumAddress | list[Address] | list[ChecksumAddress]
    blockHash: HexBytes
    fromBlock: BlockIdentifier
    toBlock: BlockIdentifier
    topics: Sequence[TopicFilter]


class FeeHistory(TypedDict):
    baseFeePerGas: list[Wei]
    gasUsedRatio: list[float]
    oldestBlock: BlockNumber
    reward: list[list[Wei]]


class StateOverrideParams(TypedDict, total=False):
    balance: Wei | None
    nonce: int | None
    code: bytes | HexStr | None
    state: dict[HexStr, HexStr] | None
    stateDiff: dict[HexStr, HexStr] | None


StateOverride = dict[str | Address | ChecksumAddress, StateOverrideParams]


GasPriceStrategy = Union[
    Callable[["Web3", TxParams], Wei], Callable[["AsyncWeb3[Any]", TxParams], Wei]
]


# syntax b/c "from" keyword not allowed w/ class construction
TxReceipt = TypedDict(
    "TxReceipt",
    {
        "blockHash": HexBytes,
        "blockNumber": BlockNumber,
        "contractAddress": ChecksumAddress | None,
        "cumulativeGasUsed": int,
        "effectiveGasPrice": Wei,
        "gasUsed": int,
        "from": ChecksumAddress,
        "logs": list[LogReceipt],
        "logsBloom": HexBytes,
        "root": HexStr,
        "status": int,
        "to": ChecksumAddress,
        "transactionHash": HexBytes,
        "transactionIndex": int,
        "type": int,
    },
)

BlockReceipts = list[TxReceipt]


class SignedTx(TypedDict, total=False):
    raw: bytes
    tx: TxParams


class StorageProof(TypedDict):
    key: HexStr
    proof: Sequence[HexStr]
    value: HexBytes


class MerkleProof(TypedDict):
    address: ChecksumAddress
    accountProof: Sequence[HexStr]
    balance: int
    codeHash: HexBytes
    nonce: Nonce
    storageHash: HexBytes
    storageProof: Sequence[StorageProof]


class Protocol(TypedDict):
    difficulty: int
    head: HexStr
    network: int
    version: int


class NodeInfo(TypedDict):
    enode: EnodeURI
    id: HexStr
    ip: str
    listenAddr: str
    name: str
    ports: dict[str, int]
    protocols: dict[str, Protocol]


class Peer(TypedDict, total=False):
    caps: Sequence[str]
    id: HexStr
    name: str
    network: dict[str, str]
    protocols: dict[str, Protocol]


class SyncStatus(TypedDict):
    currentBlock: int
    highestBlock: int
    knownStates: int
    pulledStates: int
    startingBlock: int


class Uncle(TypedDict):
    author: ChecksumAddress
    difficulty: HexStr
    extraData: HexStr
    gasLimit: HexStr
    gasUsed: HexStr
    hash: HexBytes
    logsBloom: HexStr
    miner: HexBytes
    mixHash: HexBytes
    nonce: HexStr
    number: HexStr
    parentHash: HexBytes
    receiptsRoot: HexBytes
    sealFields: Sequence[HexStr]
    sha3Uncles: HexBytes
    size: int
    stateRoot: HexBytes
    timestamp: Timestamp
    totalDifficulty: HexStr
    transactions: Sequence[HexBytes]
    transactionsRoot: HexBytes
    uncles: Sequence[HexBytes]


#
# txpool types
#

# syntax b/c "from" keyword not allowed w/ class construction
PendingTx = TypedDict(
    "PendingTx",
    {
        "blockHash": HexBytes,
        "blockNumber": None,
        "from": ChecksumAddress,
        "gas": HexBytes,
        "maxFeePerGas": HexBytes,
        "maxPriorityFeePerGas": HexBytes,
        "gasPrice": HexBytes,
        "hash": HexBytes,
        "input": HexBytes,
        "nonce": HexBytes,
        "to": ChecksumAddress,
        "transactionIndex": None,
        "value": HexBytes,
    },
    total=False,
)


class TxPoolContent(TypedDict, total=False):
    pending: dict[ChecksumAddress, dict[Nonce, list[PendingTx]]]
    queued: dict[ChecksumAddress, dict[Nonce, list[PendingTx]]]


class TxPoolInspect(TypedDict, total=False):
    pending: dict[ChecksumAddress, dict[Nonce, str]]
    queued: dict[ChecksumAddress, dict[Nonce, str]]


class TxPoolStatus(TypedDict, total=False):
    pending: int
    queued: int


#
# debug types
#
class TraceConfig(TypedDict, total=False):
    disableStorage: bool
    disableStack: bool
    enableMemory: bool
    enableReturnData: bool
    tracer: str
    tracerConfig: dict[str, Any]
    timeout: int


class CallTraceLog(TypedDict):
    address: ChecksumAddress
    data: HexBytes
    topics: Sequence[HexBytes]
    position: int


# syntax b/c "from" keyword not allowed w/ class construction
CallTrace = TypedDict(
    "CallTrace",
    {
        "type": str,
        "from": ChecksumAddress,
        "to": ChecksumAddress,
        "value": Wei,
        "gas": int,
        "gasUsed": int,
        "input": HexBytes,
        "output": HexBytes,
        "error": str,
        "revertReason": str,
        "calls": Sequence["CallTrace"],
        "logs": Sequence[CallTraceLog],
    },
    total=False,
)


class TraceData(TypedDict, total=False):
    balance: int
    nonce: int
    code: str
    storage: dict[str, str]


class DiffModeTrace(TypedDict):
    post: dict[ChecksumAddress, TraceData]
    pre: dict[ChecksumAddress, TraceData]


PrestateTrace = dict[ChecksumAddress, TraceData]


# 4byte tracer returns something like:
# { '0x27dc297e-128' : 1 }
# which is: { 4byte signature - calldata size : # of occurrences of key }
FourByteTrace = dict[str, int]


class StructLog(TypedDict):
    pc: int
    op: str
    gas: int
    gasCost: int
    depth: int
    stack: list[HexStr]


class OpcodeTrace(TypedDict, total=False):
    gas: int
    failed: bool
    returnValue: str
    structLogs: list[StructLog]


class BlockStateCallV1(TypedDict):
    blockOverrides: NotRequired[BlockData]
    stateOverrides: NotRequired[StateOverride]
    calls: Sequence[TxParams]


class SimulateV1Payload(TypedDict):
    blockStateCalls: Sequence[BlockStateCallV1]
    validation: NotRequired[bool]
    traceTransfers: NotRequired[bool]


class SimulateV1CallResult(TypedDict):
    returnData: HexBytes
    logs: Sequence[LogReceipt]
    gasUsed: int
    status: int
    error: NotRequired[RPCError]


class SimulateV1Result(BlockData):
    calls: Sequence[SimulateV1CallResult]


#
# web3.geth types
#


class GethWallet(TypedDict):
    accounts: Sequence[dict[str, str]]
    status: str
    url: str


# Contract types

TContractFn = TypeVar("TContractFn", bound="BaseContractFunction")
TContractEvent = TypeVar("TContractEvent", bound="BaseContractEvent")


# Tracing types
BlockTrace = NewType("BlockTrace", dict[str, Any])
FilterTrace = NewType("FilterTrace", dict[str, Any])
TraceMode = Sequence[Literal["trace", "vmTrace", "stateDiff"]]


class TraceFilterParams(TypedDict, total=False):
    after: int
    count: int
    fromAddress: Sequence[Address | ChecksumAddress | ENS]
    fromBlock: BlockIdentifier
    toAddress: Sequence[Address | ChecksumAddress | ENS]
    toBlock: BlockIdentifier


# Subscriptions

SubscriptionType = Literal[
    "newHeads",
    "logs",
    "newPendingTransactions",
    "syncing",
]


class LogsSubscriptionArg(TypedDict, total=False):
    address: Address | ChecksumAddress | ENS | Sequence[Address | ChecksumAddress | ENS]
    topics: Sequence[TopicFilter]
