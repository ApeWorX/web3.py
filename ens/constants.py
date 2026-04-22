import re

from eth_typing import (
    ChecksumAddress,
    HexAddress,
    HexStr,
)
from hexbytes import (
    HexBytes,
)

ACCEPTABLE_STALE_HOURS = 48

AUCTION_START_GAS_CONSTANT = 25000
AUCTION_START_GAS_MARGINAL = 39000

EMPTY_SHA3_BYTES = HexBytes(b"\0" * 32)
EMPTY_ADDR_HEX = HexAddress(HexStr("0x" + "00" * 20))

REVERSE_REGISTRAR_DOMAIN = "addr.reverse"

ENS_MAINNET_ADDR = ChecksumAddress(
    HexAddress(HexStr("0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e"))
)


# --- interface ids --- #

ENS_ADDR_INTERFACE_ID = HexStr("0x3b3b57de")
ENS_NAME_INTERFACE_ID = HexStr("0x691f3431")
ENS_ABI_INTERFACE_ID = HexStr("0x2203ab56")
ENS_PUBLIC_KEY_INTERFACE_ID = HexStr("0xc8690233")
ENS_TEXT_INTERFACE_ID = HexStr("0x59d1d43c")
ENS_CONTENT_HASH_INTERFACE_ID = HexStr("0xbc1c58d1")
ENS_MULTICHAIN_ADDRESS_INTERFACE_ID = HexStr("0xf1cb7e06")  # ENSIP-9
ENS_EXTENDED_RESOLVER_INTERFACE_ID = HexStr("0x9061b923")  # ENSIP-10

# --- avatar resolution regex --- #
NETWORK_REGEX = re.compile(
    r"""
    (?P<protocol>https?:\/\/[^/]*|ipfs:\/|ipns:\/|ar:\/)?
    (?P<root>\/)?
    (?P<subpath>ipfs\/|ipns\/)?
    (?P<target>[\w\-.]+)
    (?P<subtarget>\/.*)?
    """,
    re.VERBOSE,
)

IPFS_HASH_REGEX = re.compile(
    r"""
    ^(Qm[1-9A-HJ-NP-Za-km-z]{44,}
    |b[A-Za-z2-7]{58,}
    |B[A-Z2-7]{58,}
    |z[1-9A-HJ-NP-Za-km-z]{48,}
    |F[0-9A-F]{50,})
    (\/(?P<target>[\w\-.]+))?
    (?P<subtarget>\/.*)?$
    """,
    re.VERBOSE,
)
BASE64_REGEX = re.compile(r"^data:([a-zA-Z\-/+]*);base64,([^\"].*)")
DATA_URI_REGEX = re.compile(r"^data:([a-zA-Z\-/+]*)?(;[a-zA-Z0-9].*?)?(,)")
