from typing import (
    Any,
    Dict,
    List,
    Tuple,
)

from eth_account.typed_transactions import (
    AccessListTransaction,
    BlobTransaction,
    DynamicFeeTransaction,
    SetCodeTransaction,
    TypedTransaction,
)
from hexbytes import (
    HexBytes,
)


class Web3Transaction:
    __slots__ = (
        "typed_transaction",
        "_dict",
    )

    def __init__(self, typed_transaction: TypedTransaction):
        self.typed_transaction = typed_transaction
        self._dict = typed_transaction.as_dict()

    @classmethod
    def from_dict(cls, dictionary: Dict[str, Any]) -> "Web3Transaction":
        sanitized_dictionary = dict(dictionary)
        if (
            "transactionIndex" in sanitized_dictionary
            and sanitized_dictionary["transactionIndex"] == 0
        ):
            sanitized_dictionary["transactionIndex"] = "0x0"
        return cls(TypedTransaction.from_dict(sanitized_dictionary))

    @classmethod
    def from_bytes(cls, encoded_transaction: HexBytes) -> "Web3Transaction":
        return cls(TypedTransaction.from_bytes(encoded_transaction))

    def encode(self) -> bytes:
        return self.typed_transaction.encode()

    @property
    def transaction_type(self) -> int:
        return self.typed_transaction.transaction_type

    @property
    def chain_id(self) -> int:
        return self._dict["chainId"]

    @property
    def nonce(self) -> int:
        return self._dict["nonce"]

    @property
    def gas(self) -> int:
        return self._dict["gas"]

    @property
    def to(self) -> bytes:
        return self._dict["to"]

    @property
    def value(self) -> int:
        return self._dict["value"]

    @property
    def data(self) -> bytes:
        return self._dict["data"]

    @property
    def access_list(self) -> Tuple[Any, ...]:
        return self._dict["accessList"]

    @property
    def gas_price(self) -> int:
        if self.transaction_type == AccessListTransaction.transaction_type:
            return self._dict["gasPrice"]
        raise ValueError(
            f"Invalid transaction type {self.transaction_type} for gas_price"
        )

    @property
    def max_priority_fee_per_gas(self) -> int:
        if self.transaction_type in (
            DynamicFeeTransaction.transaction_type,
            BlobTransaction.transaction_type,
            SetCodeTransaction.transaction_type,
        ):
            return self._dict["maxPriorityFeePerGas"]
        raise ValueError(
            f"Invalid transaction type {self.transaction_type} "
            f"for max_priority_fee_per_gas"
        )

    @property
    def max_fee_per_gas(self) -> int:
        if self.transaction_type in (
            DynamicFeeTransaction.transaction_type,
            BlobTransaction.transaction_type,
            SetCodeTransaction.transaction_type,
        ):
            return self._dict["maxFeePerGas"]
        raise ValueError(
            f"Invalid transaction type {self.transaction_type} for max_fee_per_gas"
        )

    @property
    def authorization_list(self) -> List[Any]:
        if self.transaction_type == SetCodeTransaction.transaction_type:
            return self._dict["authorization_list"]
        raise ValueError(
            f"Invalid transaction type {self.transaction_type} for authorization_list"
        )

    @property
    def max_fee_per_blob_gas(self) -> int:
        if self.transaction_type == BlobTransaction.transaction_type:
            return self._dict["maxFeePerBlobGas"]
        raise ValueError(
            f"Invalid transaction type {self.transaction_type} for max_fee_per_blob_gas"
        )

    @property
    def blob_versioned_hashes(self) -> List[Any]:
        if self.transaction_type == BlobTransaction.transaction_type:
            return self._dict["blobVersionedHashes"]
        raise ValueError(
            f"Invalid transaction type {self.transaction_type} "
            f"for blob_versioned_hashes"
        )
