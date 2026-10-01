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

UNIVERSAL_RESOLVER_ADDR = ChecksumAddress(
    HexAddress(HexStr("0xeEeEEEeE14D718C2B47D9923Deab1335E144EeEe"))
)


# --- interface ids --- #

ENS_ADDR_INTERFACE_ID = HexStr("0x3b3b57de")
ENS_NAME_INTERFACE_ID = HexStr("0x691f3431")
ENS_ABI_INTERFACE_ID = HexStr("0x2203ab56")
ENS_PUBLIC_KEY_INTERFACE_ID = HexStr("0xc8690233")
ENS_CONTENT_HASH_INTERFACE_ID = HexStr("0xbc1c58d1")
