import pytest
from collections.abc import Callable, Sequence
from typing import (
    Any,
)

from eth_typing import (
    ABIEvent,
)
from eth_utils import (
    encode_hex,
)
from eth_utils.toolz import (
    compose,
    curry,
)

from web3 import (
    Web3,
)
from web3.contract.async_contract import (
    AsyncContractEvent,
)
from web3.contract.contract import (
    Contract,
    ContractEvent,
)

map_repr = compose(list, curry(map, repr))


@pytest.mark.parametrize(
    "method,args,repr_func,expected",
    (
        (
            "all_events",
            (),
            map_repr,
            [
                "<Event LogSingleArg(uint256)>",
                "<Event LogSingleWithIndex(uint256)>",
            ],
        ),
        (
            "get_event_by_signature",
            ("LogSingleArg(uint256)",),
            repr,
            "<Event LogSingleArg(uint256)>",
        ),
        (
            "find_events_by_name",
            ("LogSingleArg",),
            map_repr,
            [
                "<Event LogSingleArg(uint256)>",
            ],
        ),
        (
            "get_event_by_name",
            ("LogSingleArg",),
            repr,
            "<Event LogSingleArg(uint256)>",
        ),
        (
            "find_events_by_selector",
            (
                b"\xf7\x0f\xe6\x89\xe2\x90\xd8\xce+*8\x8a\xc2\x8d\xb3o\xbb\x0e\x16\xa6\xd8\x9ch\x04\xc4a\xf6Z\x1b@\xbb\x15",  # noqa: E501
            ),
            map_repr,
            [
                "<Event LogSingleWithIndex(uint256)>",
            ],
        ),
        (
            "get_event_by_selector",
            (
                b"\xf7\x0f\xe6\x89\xe2\x90\xd8\xce+*8\x8a\xc2\x8d\xb3o\xbb\x0e\x16\xa6\xd8\x9ch\x04\xc4a\xf6Z\x1b@\xbb\x15",  # noqa: E501
            ),
            repr,
            "<Event LogSingleWithIndex(uint256)>",
        ),
        (
            "get_event_by_selector",
            (0xF70FE689E290D8CE2B2A388AC28DB36FBB0E16A6D89C6804C461F65A1B40BB15,),
            repr,
            "<Event LogSingleWithIndex(uint256)>",
        ),
        (
            "get_event_by_selector",
            ("0xf70fe689e290d8ce2b2a388ac28db36fbb0e16a6d89c6804c461f65a1b40bb15",),
            repr,
            "<Event LogSingleWithIndex(uint256)>",
        ),
        (
            "get_event_by_topic",
            ("0x56d2ef3c5228bf5d88573621e325a4672ab50e033749a601e4f4a5e1dce905d4",),
            repr,
            "<Event LogSingleArg(uint256)>",
        ),
    ),
)
def test_find_or_get_events_by_type(
    w3: "Web3",
    method: str,
    args: Sequence[str],
    repr_func: Callable[[Any], str],
    expected: str,
    event_contract: "Contract",
) -> None:
    contract = w3.eth.contract(abi=event_contract.abi)
    contract_event = getattr(contract, method)(*args)
    assert repr_func(contract_event) == expected


def test_find_events_by_identifier(w3: "Web3", event_contract: "Contract") -> None:
    def callable_check(event_abi: ABIEvent) -> bool:
        return event_abi["name"] == "LogSingleArg"

    contract_events = event_contract.find_events_by_identifier(
        event_contract.abi, w3, event_contract.address, callable_check
    )
    assert [repr(evt) for evt in contract_events] == ["<Event LogSingleArg(uint256)>"]


def test_get_event_by_identifier(w3: "Web3", event_contract: "Contract") -> None:
    contract_event = event_contract.get_event_by_identifier(
        [event_contract.events.LogSingleArg], "LogSingleArg"
    )
    assert repr(contract_event) == "<Event LogSingleArg(uint256)>"


def test_events_iterator(math_contract):
    all_events = math_contract.all_events()
    events_iter = math_contract.events

    for event, expected_event in zip(iter(events_iter), all_events):
        assert isinstance(event, ContractEvent)
        assert event.name == expected_event.name


def test_contract_event_topic(event_contract):
    event = event_contract.events.LogSingleArg()
    assert event.topic == encode_hex(event_contract.w3.keccak(text=event.signature))


def test_contract_event_topic_no_parens(event_contract):
    event = event_contract.events.LogSingleArg
    assert event.topic == encode_hex(event_contract.w3.keccak(text=event.signature))


@pytest.mark.parametrize(
    "event_abi,expected_signature",
    (
        (
            {
                "name": "Transfer",
                "type": "event",
                "inputs": [
                    {"type": "address", "name": "from", "indexed": True},
                    {"type": "address", "name": "to", "indexed": True},
                    {"type": "uint256", "name": "value", "indexed": False},
                ],
            },
            "Transfer(address,address,uint256)",
        ),
        (
            {
                "name": "TransferBatch",
                "type": "event",
                "inputs": [
                    {"type": "address", "name": "operator", "indexed": True},
                    {"type": "address", "name": "from", "indexed": True},
                    {"type": "address", "name": "to", "indexed": True},
                    {"type": "uint256[]", "name": "ids", "indexed": False},
                    {"type": "uint256[]", "name": "values", "indexed": False},
                ],
            },
            "TransferBatch(address,address,address,uint256[],uint256[])",
        ),
        (
            {
                "name": "Approval",
                "type": "event",
                "inputs": [
                    {"type": "address", "name": "owner", "indexed": True},
                    {"type": "address", "name": "approved", "indexed": True},
                    {"type": "uint256", "name": "tokenId", "indexed": True},
                ],
            },
            "Approval(address,address,uint256)",
        ),
        (
            {
                "name": "ApprovalForAll",
                "type": "event",
                "inputs": [
                    {"type": "address", "name": "owner", "indexed": True},
                    {"type": "address", "name": "operator", "indexed": True},
                    {"type": "bool", "name": "approved", "indexed": False},
                ],
            },
            "ApprovalForAll(address,address,bool)",
        ),
        (
            {
                "name": "OwnershipTransferred",
                "type": "event",
                "inputs": [
                    {"type": "address", "name": "previousOwner", "indexed": True},
                    {"type": "address", "name": "newOwner", "indexed": True},
                ],
            },
            "OwnershipTransferred(address,address)",
        ),
    ),
)
def test_contract_event_signatures_and_topics(w3, event_abi, expected_signature):
    event = ContractEvent(abi=event_abi)
    assert event.signature == expected_signature
    assert event.topic == encode_hex(w3.keccak(text=expected_signature))

    async_event = AsyncContractEvent(abi=event_abi)
    assert async_event.signature == expected_signature
    assert async_event.topic == encode_hex(w3.keccak(text=expected_signature))


# -- async -- #


def test_async_events_iterator(async_math_contract):
    all_events = async_math_contract.all_events()
    events_iter = async_math_contract.events

    for event, expected_event in zip(iter(events_iter), all_events):
        assert isinstance(event, AsyncContractEvent)
        assert event.name == expected_event.name


def test_async_contract_event_topic(async_event_contract):
    event = async_event_contract.events.LogSingleArg()
    assert event.signature == "LogSingleArg(uint256)"
    assert event.topic == encode_hex(
        async_event_contract.w3.keccak(text=event.signature)
    )


def test_async_contract_event_topic_no_parens(async_event_contract):
    event = async_event_contract.events.LogSingleArg
    assert event.signature == "LogSingleArg(uint256)"
    assert event.topic == encode_hex(
        async_event_contract.w3.keccak(text=event.signature)
    )
