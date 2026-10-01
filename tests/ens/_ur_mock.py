"""
Test-only Universal Resolver mock that delegates to the local eth_tester
registry. Simulates the parts of the real UR that the unit tests exercise:
walking the parent chain to find a resolver, then forwarding calldata via
ENSIP-10 `resolve()` (with a fallback to direct eth_call for resolvers that
don't implement it).

This is intentionally permissive about parent-walk semantics — the real UR
rejects walked-up resolvers that don't implement IExtendedResolver, but
enforcing that here would require fixture-level changes beyond the scope of
these unit tests. See the PR description for the deferred follow-up.
"""

from unittest.mock import (
    AsyncMock,
    MagicMock,
)

from eth_tester.exceptions import (
    TransactionFailed,
)

from ens.utils import (
    is_none_or_zero_address,
    normal_name_to_hash,
)
from web3.exceptions import (
    ContractLogicError,
)

_REVERT_EXCS = (TransactionFailed, ContractLogicError)
_ZERO_ADDR = "0x" + "00" * 20
_ZERO_NODE = b"\x00" * 32


def _dns_decode_name(dns_name):
    labels = []
    i = 0
    while i < len(dns_name):
        length = dns_name[i]
        if length == 0:
            break
        i += 1
        labels.append(dns_name[i : i + length].decode("utf-8"))
        i += length
    return ".".join(labels)


def install_ur_mock(ens_instance):
    """Replace `ens_instance._universal_resolver` with a sync mock."""

    def find_resolver(dns_name):
        name = _dns_decode_name(dns_name)
        current = name
        while current:
            node = normal_name_to_hash(current)
            resolver_addr = ens_instance.ens.caller.resolver(node)
            if not is_none_or_zero_address(resolver_addr):
                return resolver_addr, normal_name_to_hash(name), 0
            parts = current.split(".", 1)
            current = parts[1] if len(parts) > 1 else ""
        return _ZERO_ADDR, _ZERO_NODE, 0

    def resolve(dns_name, calldata):
        resolver_addr, _, _ = find_resolver(dns_name)
        if is_none_or_zero_address(resolver_addr):
            raise ContractLogicError("No resolver found")
        try:
            resolver = ens_instance._resolver_contract(address=resolver_addr)
            return resolver.caller.resolve(dns_name, calldata), resolver_addr
        except _REVERT_EXCS:
            pass
        # Fall back to direct eth_call for resolvers without resolve().
        try:
            result = ens_instance.w3.eth.call({"to": resolver_addr, "data": calldata})
        except _REVERT_EXCS as e:
            raise ContractLogicError(str(e)) from e
        return result, resolver_addr

    caller = MagicMock()
    caller.resolve = resolve
    caller.findResolver = find_resolver
    ens_instance._universal_resolver = MagicMock()
    ens_instance._universal_resolver.caller = caller


def install_async_ur_mock(ens_instance):
    """Replace `ens_instance._universal_resolver` with an async mock."""

    async def find_resolver(dns_name):
        name = _dns_decode_name(dns_name)
        current = name
        while current:
            node = normal_name_to_hash(current)
            resolver_addr = await ens_instance.ens.caller.resolver(node)
            if not is_none_or_zero_address(resolver_addr):
                return resolver_addr, normal_name_to_hash(name), 0
            parts = current.split(".", 1)
            current = parts[1] if len(parts) > 1 else ""
        return _ZERO_ADDR, _ZERO_NODE, 0

    async def resolve(dns_name, calldata):
        resolver_addr, _, _ = await find_resolver(dns_name)
        if is_none_or_zero_address(resolver_addr):
            raise ContractLogicError("No resolver found")
        try:
            resolver = ens_instance._resolver_contract(address=resolver_addr)
            result = await resolver.caller.resolve(dns_name, calldata)
            return result, resolver_addr
        except _REVERT_EXCS:
            pass
        try:
            result = await ens_instance.w3.eth.call(
                {"to": resolver_addr, "data": calldata}
            )
        except _REVERT_EXCS as e:
            raise ContractLogicError(str(e)) from e
        return result, resolver_addr

    caller = AsyncMock()
    caller.resolve = resolve
    caller.findResolver = find_resolver
    ens_instance._universal_resolver = MagicMock()
    ens_instance._universal_resolver.caller = caller
