from collections.abc import Iterator
from typing import (
    Any,
)

from eth_typing import (
    HexStr,
)

from web3.utils import (
    EthSubscription,
)


class SubscriptionContainer:
    def __init__(self) -> None:
        self.subscriptions: list[EthSubscription[Any]] = []
        self.subscriptions_by_id: dict[HexStr, EthSubscription[Any]] = {}
        self.subscriptions_by_label: dict[str, EthSubscription[Any]] = {}

    def __len__(self) -> int:
        return len(self.subscriptions)

    def __iter__(self) -> Iterator[EthSubscription[Any]]:
        return iter(self.subscriptions)

    def add_subscription(self, subscription: EthSubscription[Any]) -> None:
        self.subscriptions.append(subscription)
        self.subscriptions_by_id[subscription.id] = subscription
        self.subscriptions_by_label[subscription.label] = subscription

    def remove_subscription(self, subscription: EthSubscription[Any]) -> None:
        self.subscriptions.remove(subscription)
        self.subscriptions_by_id.pop(subscription.id)
        self.subscriptions_by_label.pop(subscription.label)

    def get_by_id(self, sub_id: HexStr) -> EthSubscription[Any]:
        return self.subscriptions_by_id.get(sub_id)

    def get_by_label(self, label: str) -> EthSubscription[Any]:
        return self.subscriptions_by_label.get(label)

    @property
    def handler_subscriptions(self) -> list[EthSubscription[Any]]:
        return [sub for sub in self.subscriptions if sub._handler is not None]

    def get_handler_subscription_by_id(
        self, sub_id: HexStr
    ) -> EthSubscription[Any] | None:
        sub = self.get_by_id(sub_id)
        if sub and sub._handler:
            return sub
        return None
