import pytest
import base64
from unittest import (
    mock,
)
from unittest.mock import (
    patch,
)

from eth_utils import (
    is_integer,
    to_bytes,
)

from ens import (
    BaseENS,
)
from ens._normalization import (
    ENSNormalizedName,
    Label,
    TextToken,
)
from ens.exceptions import (
    ENSValidationError,
)
from ens.utils import (
    UriItem,
    _parse_avatar_uri,
    dns_encode_name,
    ens_encode_name,
    init_async_web3,
    init_web3,
    is_valid_name,
    label_to_hash,
    normal_name_to_hash,
    normalize_name,
    raw_name_to_hash,
)
from web3.eth import (
    AsyncEth,
)
from web3.providers.eth_tester import (
    AsyncEthereumTesterProvider,
)


def test_init_web3_adds_expected_middleware():
    w3 = init_web3()
    middleware = w3.middleware_onion.middleware
    assert middleware[0][1] == "stalecheck"


@pytest.mark.parametrize(
    "name,expected",
    (
        # test some allowed cases
        ("tester.eth", b"\x06tester\x03eth\x00"),
        (
            "a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p",
            b"\x01a\x01b\x01c\x01d\x01e\x01f\x01g\x01h\x01i\x01j\x01k\x01l\x01m\x01n\x01o\x01p\x00",  # noqa: E501
        ),
        (
            "1.2.3.4.5.6.7.8.9.10",
            b"\x011\x012\x013\x014\x015\x016\x017\x018\x019\x0210\x00",
        ),
        ("abc.123.def-456.eth", b"\x03abc\x03123\x07def-456\x03eth\x00"),
        ("abc.123.def-456.eth", b"\x03abc\x03123\x07def-456\x03eth\x00"),
        (
            "nhéééééé.eth",
            b"\x0enh\xc3\xa9\xc3\xa9\xc3\xa9\xc3\xa9\xc3\xa9\xc3\xa9\x03eth\x00",
        ),
        ("🌈rainbow.eth", b"\x0b\xf0\x9f\x8c\x88rainbow\x03eth\x00"),
        ("🐔🐔.tk", b"\x08\xf0\x9f\x90\x94\xf0\x9f\x90\x94\x02tk\x00"),
        # test that label length may be less than 255
        (f"{'a' * 255}.b", b"\xff" + (b"a" * 255) + b"\x01b\x00"),
        (f"a.{'b' * 255}", b"\x01a" + b"\xff" + (b"b" * 255) + b"\x00"),
        (f"abc-123.{'b' * 255}", b"\x07abc-123" + b"\xff" + b"b" * 255 + b"\x00"),
    ),
)
def test_dns_encode_name(name, expected):
    assert dns_encode_name(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    (
        (
            f"{'a' * 63}.{'b' * 63}.{'c' * 63}.{'d' * 63}.{'e' * 63}.{'f' * 63}.{'g' * 63}",  # noqa: E501
            b"".join([b"?" + to_bytes(text=label) * 63 for label in "abcdefg"])
            + b"\x00",
        ),
        (
            f"{'a-1' * 21}.{'b-2' * 21}.{'c-3' * 21}.{'d-4' * 21}.{'e-5' * 21}.{'f-6' * 21}",  # noqa: E501
            b"".join(
                [
                    b"?" + to_bytes(text=label) * 21
                    for label in [
                        "a-1",
                        "b-2",
                        "c-3",
                        "d-4",
                        "e-5",
                        "f-6",
                    ]
                ]
            )
            + b"\x00",
        ),
    ),
)
def test_dns_encode_name_validating_total_encoded_name_size(name, expected):
    # This test is important because dns validation technically limits the
    # total encoded domain name size to 255. ENSIP-10 expects the name to be
    # DNS encoded with one of the validation exceptions being that the
    # total encoded size can be any length.
    dns_encoded = dns_encode_name(name)
    assert len(dns_encoded) > 255
    assert dns_encoded == expected


@pytest.mark.parametrize("empty_name", ("", ".", None, " ", "  "))
def test_dns_encode_name_returns_single_zero_byte_for_empty_name(empty_name):
    assert dns_encode_name(empty_name) == b"\00"


@pytest.mark.parametrize(
    "name,invalid_label_index",
    (
        ("a" * 256, 0),
        (f"{'a' * 256}.b", 0),
        (f"a.{'a-b1' * 64}x", 1),
        (f"{'a' * 256}.{'1' * 255}.{'b' * 255}", 0),
        (f"{'a' * 255}.{'1' * 256}.{'b' * 255}", 1),
        (f"{'a' * 255}.{'1' * 255}.{'b' * 256}", 2),
    ),
)
def test_dns_encode_name_raises_validation_error_on_label_lengths_over_63(
    name, invalid_label_index
):
    with pytest.raises(
        ENSValidationError, match=f"Label at position {invalid_label_index} too long"
    ):
        dns_encode_name(name)


def test_dns_encode_name_normalizes_name_before_encoding():
    assert dns_encode_name("Öbb.at") == dns_encode_name("öbb.at")
    assert dns_encode_name("nhÉéÉéÉé.eth") == dns_encode_name("nhéééééé.eth")
    assert dns_encode_name("TESTER.eth") == dns_encode_name("tester.eth")
    assert dns_encode_name("test\u200btest.com") == dns_encode_name("testtest.com")
    assert dns_encode_name("O\u0308bb.at") == dns_encode_name("öbb.at")


@pytest.mark.parametrize(
    "name,hashed",
    (
        (None, "0x" + ("00" * 32)),
        ("", "0x" + ("00" * 32)),
        ("eth", "0x93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae"),
        (
            "foo.eth",
            "0xde9b09fd7c5f901e23a3f19fecc54828e9c848539801e86591bd9801b019f84f",
        ),
    ),
)
def test_normal_name_to_hash(name, hashed):
    assert normal_name_to_hash(name).to_0x_hex() == hashed


@pytest.mark.parametrize(
    "utility_method",
    (
        normalize_name,
        is_valid_name,
        BaseENS.namehash,
        BaseENS.nameprep,
        dns_encode_name,
        raw_name_to_hash,
    ),
)
def test_name_utility_methods_normalize_the_name_using_ensip15(utility_method):
    # we already have tests for `normalize_name_ensip15` so we just need to make sure
    # the utility methods call it under the hood with the correct arguments
    with patch(
        "ens._normalization.normalize_name_ensip15"
    ) as normalize_name_ensip15_mock:
        utility_method("foo.eth")
        normalize_name_ensip15_mock.assert_called_once_with("foo.eth")


def test_label_to_hash_normalizes_name_using_ensip15():
    normalized_name = ENSNormalizedName(
        [
            Label("test", [TextToken([102, 111, 111])]),  # "foo"
            Label("test", [TextToken([101, 116, 104])]),  # "eth"
        ]
    )
    assert normalized_name.as_text == "foo.eth"

    with patch(
        "ens._normalization.normalize_name_ensip15"
    ) as mock_normalize_name_ensip15:
        for label in normalized_name.labels:
            mock_normalize_name_ensip15.return_value = ENSNormalizedName([label])

            label_to_hash(label.text)
            mock_normalize_name_ensip15.assert_called_once_with(label.text)
            mock_normalize_name_ensip15.reset_mock()

    assert label_to_hash("foo").to_0x_hex() == (
        "0x41b1a0649752af1b28b3dc29a1556eee781e4a4c3a1f7f53f90fa834de098c4d"
    )


@mock.patch("ens.utils.dns_encode_name")
def test_ens_encode_name_issues_deprecation_warning_and_calls_dns_encode_name(
    mock_dns_encode_name,
):
    with pytest.warns(DeprecationWarning, match=r"``ens_encode_name`` is deprecated"):
        ens_encode_name("foo")

    mock_dns_encode_name.assert_called_once_with("foo")


# -- async -- #


@pytest.mark.asyncio
async def test_init_async_web3_adds_expected_async_middleware():
    async_w3 = init_async_web3()
    middleware = async_w3.middleware_onion.middleware
    assert middleware[0][1] == "stalecheck"


@pytest.mark.asyncio
async def test_init_async_web3_adds_async_eth():
    async_w3 = init_async_web3()
    assert isinstance(async_w3.eth, AsyncEth)


@pytest.mark.asyncio
async def test_init_async_web3_with_provider_argument_adds_async_eth():
    async_w3 = init_async_web3(AsyncEthereumTesterProvider())

    assert isinstance(async_w3.provider, AsyncEthereumTesterProvider)
    assert isinstance(async_w3.eth, AsyncEth)

    latest_block = await async_w3.eth.get_block("latest")
    assert latest_block
    assert is_integer(latest_block["number"])


def test_ipfs_path_normalizes_to_gateway():
    # use a simple ipfs path form that network_regex will match (subpath "ipfs/")
    uri = "ipfs/QmTestHash123"
    item = _parse_avatar_uri(uri)
    assert isinstance(item, UriItem)
    assert item.uri == "https://ipfs.io/ipfs/QmTestHash123"
    assert item.is_on_chain is False
    assert item.is_encoded is False


def test_inline_svg_converted_to_data_uri():
    svg = "<svg xmlns='http://www.w3.org/2000/svg'><rect width='10' height='10'/></svg>"
    item = _parse_avatar_uri(svg)
    assert isinstance(item, UriItem)
    assert item.is_on_chain is True
    assert item.is_encoded is False
    assert item.uri.startswith("data:image/svg+xml;base64,")
    # verify the payload decodes back to the original svg (utf-8)
    payload_b64 = item.uri.split(",", 1)[1]
    decoded = base64.b64decode(payload_b64).decode("utf-8")
    assert decoded == svg


def test_data_base64_detected_as_encoded():
    data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA"
    item = _parse_avatar_uri(data_uri)
    assert isinstance(item, UriItem)
    assert item.is_on_chain is True
    assert item.is_encoded is True
    assert item.uri == data_uri


def test_arweave_gateway_replacement():
    original = "https://arweave.net/someid/g.png"
    custom = {"arweave": "https://mygateway.test"}
    item = _parse_avatar_uri(original, gateway_urls=custom)
    assert isinstance(item, UriItem)
    assert item.uri == "https://mygateway.test/someid/g.png"
    assert item.is_on_chain is False
    assert item.is_encoded is False
