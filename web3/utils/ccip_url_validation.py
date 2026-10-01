import asyncio
from collections.abc import Awaitable, Callable
import ipaddress
import socket
from urllib.parse import (
    urlparse,
)

from web3.exceptions import (
    Web3ValidationError,
)

CcipUrlValidator = Callable[[str], None]
AsyncCcipUrlValidator = Callable[[str], Awaitable[None]]

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("::/128"),
]


def validate_ccip_url_scheme(url: str, allow_http: bool = False) -> None:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()

    if scheme == "https":
        return

    if scheme == "http" and allow_http:
        return

    if scheme == "http":
        raise Web3ValidationError(
            f"CCIP Read request to non-HTTPS URL '{url}' is not allowed. "
            "Set ``ccip_read_allow_http=True`` on the provider to allow HTTP URLs."
        )

    raise Web3ValidationError(
        f"CCIP Read request with scheme '{scheme}' is not allowed. "
        "Only HTTPS URLs are permitted."
    )


def _check_ip_blocked(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(addr in network for network in BLOCKED_IP_NETWORKS)


def validate_ccip_url_host(url: str) -> None:
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise Web3ValidationError(f"CCIP Read URL '{url}' has no hostname.")

    try:
        addrinfos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise Web3ValidationError(
            f"CCIP Read URL hostname '{hostname}' could not be resolved."
        )

    for addrinfo in addrinfos:
        ip_str = str(addrinfo[4][0])
        if _check_ip_blocked(ip_str):
            raise Web3ValidationError(
                f"CCIP Read request to '{url}' is not allowed: "
                f"resolved IP '{ip_str}' is in a blocked private/reserved range."
            )


async def async_validate_ccip_url_host(url: str) -> None:
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise Web3ValidationError(f"CCIP Read URL '{url}' has no hostname.")

    loop = asyncio.get_running_loop()
    try:
        addrinfos = await loop.run_in_executor(None, socket.getaddrinfo, hostname, None)
    except socket.gaierror:
        raise Web3ValidationError(
            f"CCIP Read URL hostname '{hostname}' could not be resolved."
        )

    for addrinfo in addrinfos:
        ip_str = str(addrinfo[4][0])
        if _check_ip_blocked(ip_str):
            raise Web3ValidationError(
                f"CCIP Read request to '{url}' is not allowed: "
                f"resolved IP '{ip_str}' is in a blocked private/reserved range."
            )
