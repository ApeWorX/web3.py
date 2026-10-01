from collections.abc import Collection
from typing import (
    Any,
)

from eth_utils import (
    apply_formatters_to_dict,
)
from eth_utils.toolz import (
    concat,
)

from web3.exceptions import (
    Web3AttributeError,
)


def verify_attr(class_name: str, key: str, namespace: Collection[str]) -> None:
    if key not in namespace:
        raise Web3AttributeError(
            f"Property {key} not found on {class_name} class. "
            f"`{class_name}.factory` only accepts keyword arguments which are "
            f"present on the {class_name} class"
        )


class PropertyCheckingFactory(type):
    def __init__(
        cls,
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        **kwargs: dict[str, Any],
    ) -> None:
        # see PEP487.  To accept kwargs in __new__, they need to be
        # filtered out here.
        super().__init__(name, bases, namespace)

    # __new__ must return a class instance
    def __new__(
        mcs,
        name: str,
        bases: tuple[type],
        namespace: dict[str, Any],
        normalizers: dict[str, Any] | None = None,
    ) -> "PropertyCheckingFactory":
        all_bases = set(concat(base.__mro__ for base in bases))
        all_keys = set(concat(base.__dict__.keys() for base in all_bases))

        for key in namespace:
            verify_attr(name, key, all_keys)

        if normalizers:
            processed_namespace = apply_formatters_to_dict(
                normalizers,
                namespace,
            )
        else:
            processed_namespace = namespace

        return super().__new__(mcs, name, bases, processed_namespace)
