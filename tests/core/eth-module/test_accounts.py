import pytest
from unittest.mock import (
    patch,
)

from eth_account.messages import (
    encode_defunct,
)
from eth_account.signers.local import (
    LocalAccount,
)
from eth_utils import (
    is_bytes,
    is_checksum_address,
    to_bytes,
    to_hex,
)
from eth_utils.toolz import (
    dissoc,
)
from hexbytes import (
    HexBytes,
)

from web3 import (
    Account,
    AsyncWeb3,
    Web3,
)
from web3._utils.empty import (
    Empty,
)
from web3.eth import (
    BaseEth,
)
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)
from web3.providers.eth_tester.main import (
    AsyncEthereumTesterProvider,
)

# from https://github.com/ethereum/tests/blob/3930ca3a9a377107d5792b3e7202f79c688f1a67/BasicTests/txtest.json # noqa: E501
ETH_TEST_TRANSACTIONS = [
    {
        "chainId": None,
        "key": "c85ef7d79691fe79573b1a7064c19c1a9819ebdbd1faaab1a8ec92344438aaf4",
        "nonce": 0,
        "gasPrice": 1000000000000,
        "gas": 10000,
        "to": "0x13978aee95f38490e9769C39B2773Ed763d9cd5F",
        "value": 10000000000000000,
        "data": "",
        "unsigned": "eb8085e8d4a510008227109413978aee95f38490e9769c39b2773ed763d9cd5f872386f26fc1000080808080",  # noqa: E501
        "signed": "f86b8085e8d4a510008227109413978aee95f38490e9769c39b2773ed763d9cd5f872386f26fc10000801ba0eab47c1a49bf2fe5d40e01d313900e19ca485867d462fe06e139e3a536c6d4f4a014a569d327dcda4b29f74f93c0e9729d2f49ad726e703f9cd90dbb0fbf6649f1",  # noqa: E501
    },
    {
        "chainId": None,
        "key": "c87f65ff3f271bf5dc8643484f66b200109caffe4bf98c4cb393dc35740b28c0",
        "nonce": 0,
        "gasPrice": 1000000000000,
        "gas": 10000,
        "to": "",
        "value": 0,
        "data": "6025515b525b600a37f260003556601b596020356000355760015b525b54602052f260255860005b525b54602052f2",  # noqa: E501
        "unsigned": "f83f8085e8d4a510008227108080af6025515b525b600a37f260003556601b596020356000355760015b525b54602052f260255860005b525b54602052f2808080",  # noqa: E501
        "signed": "f87f8085e8d4a510008227108080af6025515b525b600a37f260003556601b596020356000355760015b525b54602052f260255860005b525b54602052f21ba05afed0244d0da90b67cf8979b0f246432a5112c0d31e8d5eedd2bc17b171c694a0bb1035c834677c2e1185b8dc90ca6d1fa585ab3d7ef23707e1a497a98e752d1b",  # noqa: E501
    },
]


@pytest.fixture
def PRIVATE_BYTES():
    return b"unicorns" * 4


@pytest.fixture
def PRIVATE_BYTES_ALT(PRIVATE_BYTES):
    return b"rainbows" * 4


@pytest.fixture
def web3js_key():
    return "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318"


@pytest.fixture
def web3js_password():
    return "test!"


@pytest.fixture(params=["instance", "class"])
def acct(request, w3):
    if request.param == "instance":
        return BaseEth(w3).account
    elif request.param == "class":
        return Account
    raise Exception("Unreachable!")


@pytest.fixture()
def w3():
    return Web3(EthereumTesterProvider())


def test_eth_default_account_is_empty_by_default(w3):
    assert isinstance(w3.eth.default_account, Empty)


def test_eth_account_create_variation(acct):
    account1 = acct.create()
    account2 = acct.create()
    assert account1 != account2


def test_eth_account_from_key_reproducible(acct, PRIVATE_BYTES):
    account1 = acct.from_key(PRIVATE_BYTES)
    account2 = acct.from_key(PRIVATE_BYTES)
    assert bytes(account1) == PRIVATE_BYTES
    assert bytes(account1) == bytes(account2)
    assert isinstance(str(account1), str)


def test_eth_account_from_key_diverge(acct, PRIVATE_BYTES, PRIVATE_BYTES_ALT):
    account1 = acct.from_key(PRIVATE_BYTES)
    account2 = acct.from_key(PRIVATE_BYTES_ALT)
    assert bytes(account2) == PRIVATE_BYTES_ALT
    assert bytes(account1) != bytes(account2)


def test_eth_account_from_key_seed_restrictions(acct):
    with pytest.raises(ValueError):
        acct.from_key(b"")
    with pytest.raises(ValueError):
        acct.from_key(b"\xff" * 31)
    with pytest.raises(ValueError):
        acct.from_key(b"\xff" * 33)


def test_eth_account_from_key_properties(acct, PRIVATE_BYTES):
    account = acct.from_key(PRIVATE_BYTES)
    assert callable(account.unsafe_sign_hash)
    assert callable(account.sign_transaction)
    assert is_checksum_address(account.address)
    assert account.address == "0xa79F6f349C853F9Ea0B29636779ae3Cb4E3BA729"
    assert account.key == PRIVATE_BYTES


def test_eth_account_create_properties(acct):
    account = acct.create()
    assert callable(account.unsafe_sign_hash)
    assert callable(account.sign_transaction)
    assert is_checksum_address(account.address)
    assert isinstance(account.key, bytes) and len(account.key) == 32


def test_eth_account_recover_transaction_example(acct):
    raw_tx_hex = "0xf8640d843b9aca00830e57e0945b2063246f2191f18f2675cedb8b28102e957458018025a00c753084e5a8290219324c1a3a86d4064ded2d15979b1ea790734aaa2ceaafc1a0229ca4538106819fd3a5509dd383e8fe4b731c6870339556a5c06feb9cf330bb"  # noqa: E501
    from_account = acct.recover_transaction(raw_tx_hex)
    assert from_account == "0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4"


def test_eth_account_recover_transaction_with_literal(acct):
    raw_tx = 0xF8640D843B9ACA00830E57E0945B2063246F2191F18F2675CEDB8B28102E957458018025A00C753084E5A8290219324C1A3A86D4064DED2D15979B1EA790734AAA2CEAAFC1A0229CA4538106819FD3A5509DD383E8FE4B731C6870339556A5C06FEB9CF330BB  # noqa: E501
    from_account = acct.recover_transaction(raw_tx)
    assert from_account == "0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4"


def test_eth_account_recover_message(acct):
    v, r, s = (
        28,
        "0xe6ca9bba58c88611fad66a6ce8f996908195593807c4b38bd528d2cff09d4eb3",
        "0x3e5bfbbf4d3e39b1a2fd816a7680c19ebebaf3a141b239934ad43cb33fcec8ce",
    )
    message_text = "I♥SF"
    message = encode_defunct(text=message_text)
    from_account = acct.recover_message(message, vrs=(v, r, s))
    assert from_account == "0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E"


@pytest.mark.parametrize(
    "signature_bytes",
    [
        # test signature bytes with standard v (0 in this case)
        b'\x0cu0\x84\xe5\xa8)\x02\x192L\x1a:\x86\xd4\x06M\xed-\x15\x97\x9b\x1e\xa7\x90sJ\xaa,\xea\xaf\xc1"\x9c\xa4S\x81\x06\x81\x9f\xd3\xa5P\x9d\xd3\x83\xe8\xfeKs\x1chp3\x95V\xa5\xc0o\xeb\x9c\xf30\xbb\x00',  # noqa: E501
        # test signature bytes with chain-naive v (27 in this case)
        b'\x0cu0\x84\xe5\xa8)\x02\x192L\x1a:\x86\xd4\x06M\xed-\x15\x97\x9b\x1e\xa7\x90sJ\xaa,\xea\xaf\xc1"\x9c\xa4S\x81\x06\x81\x9f\xd3\xa5P\x9d\xd3\x83\xe8\xfeKs\x1chp3\x95V\xa5\xc0o\xeb\x9c\xf30\xbb\x1b',  # noqa: E501
    ],
    ids=["test_sig_bytes_standard_v", "test_sig_bytes_chain_naive_v"],
)
def test_eth_account_recover_signature_bytes(acct, signature_bytes):
    msg = encode_defunct(
        b"\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1"  # noqa: E501
    )
    from_account = acct.recover_message(msg, signature=signature_bytes)
    assert from_account == "0xb7E7385a15fFd29e349BB409C4c0a7d7469601C7"


def test_eth_account_recover_vrs(acct):
    v, r, s = (
        27,
        5634810156301565519126305729385531885322755941350706789683031279718535704513,
        15655399131600894366408541311673616702363115109327707006109616887384920764603,
    )

    msg = encode_defunct(
        b"\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1"  # noqa: E501
    )
    from_account = acct.recover_message(msg, vrs=(v, r, s))
    assert from_account == "0xb7E7385a15fFd29e349BB409C4c0a7d7469601C7"

    from_account = acct.recover_message(msg, vrs=map(to_hex, (v, r, s)))
    assert from_account == "0xb7E7385a15fFd29e349BB409C4c0a7d7469601C7"


def test_eth_account_recover_vrs_standard_v(acct):
    v, r, s = (
        0,
        5634810156301565519126305729385531885322755941350706789683031279718535704513,
        15655399131600894366408541311673616702363115109327707006109616887384920764603,
    )
    msg = encode_defunct(
        b"\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1"  # noqa: E501
    )
    from_account = acct.recover_message(msg, vrs=(v, r, s))
    assert from_account == "0xb7E7385a15fFd29e349BB409C4c0a7d7469601C7"


@pytest.mark.parametrize(
    "message_text, key, expected_bytes, expected_hash, v, r, s, signature",
    (
        (
            "Some data",
            "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318",
            b"Some data",
            HexBytes(
                "0x1da44b586eb0729ff70a73c326926f6ed5a25f5b056e7f47fbc6e58d86871655"
            ),
            28,
            83713930994764734002432606962255364472443135907807238282514898577139886061053,  # noqa: E501
            43435997768575461196683613590576722655951133545204789519877940758262837256233,  # noqa: E501
            HexBytes(
                "0xb91467e570a6466aa9e9876cbcd013baba02900b8979d43fe208a4a4f339f5fd6007e74cd82e037b800186422fc2da167c747ef045e5d18a5f5d4300f8e1a0291c"  # noqa: E501
            ),
        ),
        (
            "10284",
            "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318",
            b"10284",
            HexBytes(
                "0x0a162a5efbba02f38db3114531c8acba39fe676f09f7e471d93e8a06c471821c"
            ),
            27,
            143748089818580655331728101695676826715814583506606354117109114714663470502,
            227853308212209543997879651656855994238138056366857653269155208245074180053,
            HexBytes(
                "0x00515bc8fd32264e21ec0820e8c5123ed58c1195c9ea17cb018b1ad4073cc5a60080f5dcec397a5a8c523082bfa41771568903aa554ec06ba8475ca9050fb7d51b"  # noqa: E501
            ),
        ),
    ),
    ids=["web3js_example", "31byte_r_and_s"],
)
def test_eth_account_sign(
    acct, message_text, key, expected_bytes, expected_hash, v, r, s, signature
):
    message = encode_defunct(text=message_text)
    assert message.body == expected_bytes
    signed_message = Web3.keccak(
        b"\x19Ethereum Signed Message:\n"
        + bytes(f"{len(message.body)}", encoding="utf-8")
        + message.body
    )
    assert signed_message == expected_hash

    signed = acct.sign_message(message, private_key=key)
    assert signed.message_hash == expected_hash
    assert signed.v == v
    assert signed.r == r
    assert signed.s == s
    assert signed.signature == signature

    account = acct.from_key(key)
    assert account.sign_message(message) == signed


@pytest.mark.parametrize(
    "txn, private_key, expected_raw_tx, tx_hash, r, s, v",
    (
        (
            {
                "to": "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55",
                "value": 1000000000,
                "gas": 2000000,
                "gasPrice": 234567897654321,
                "nonce": 0,
                "chainId": 1,
            },
            "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318",
            HexBytes(
                "0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428"  # noqa: E501
            ),
            HexBytes(
                "0xd8f64a42b57be0d565f385378db2f6bf324ce14a594afc05de90436e9ce01f60"
            ),
            4487286261793418179817841024889747115779324305375823110249149479905075174044,  # noqa: E501
            30785525769477805655994251009256770582792548537338581640010273753578382951464,  # noqa: E501
            37,
        ),
        (
            {
                "to": "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55",
                "value": 0,
                "gas": 31853,
                "gasPrice": 0,
                "nonce": 0,
                "chainId": 1,
            },
            "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318",
            HexBytes(
                "0xf85d8080827c6d94f0109fc8df283027b6285cc889f5aa624eac1f558080269f22f17b38af35286ffbb0c6376c86ec91c20ecbad93f84913a0cc15e7580cd99f83d6e12e82e3544cb4439964d5087da78f74cefeec9a450b16ae179fd8fe20"  # noqa: E501
            ),
            HexBytes(
                "0xb0c5e2c6b29eeb0b9c1d63eaa8b0f93c02ead18ae01cb7fc795b0612d3e9d55a"
            ),
            61739443115046231975538240097110168545680205678104352478922255527799426265,
            232940010090391255679819602567388136081614408698362277324138554019997613600,
            38,
        ),
        (
            {
                "gas": 100000,
                "gasPrice": 1000000000,
                "data": "0x5544",
                "nonce": "0x2",
                "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
                "value": "0x5af3107a4000",
                "type": "0x1",
                "accessList": (
                    {
                        "address": "0x0000000000000000000000000000000000000001",
                        "storageKeys": (
                            "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                        ),
                    },
                ),
                "chainId": 1,
            },
            "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318",
            HexBytes(
                "0x01f8a70102843b9aca00830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544f838f7940000000000000000000000000000000000000001e1a0010000000000000000000000000000000000000000000000000000000000000080a059a827f04246489aca139510f2f82896fd5bd1d34f05228b3fe0c60141db4246a07a28a925eae2e3ee173cf691de2737cbff9160fc527ca4305740a31f154758c5"  # noqa: E501
            ),
            HexBytes(
                "0x5daf67cf0dd95f338e98b7b8ee7635f3667b7127be8f42011536c239f8ed4f50"
            ),
            40552949476267726331782755436085615371483644858950895384477411974599262552646,  # noqa: E501
            55254008827136682571969715431199989606887296450225146219777298167488873715909,  # noqa: E501
            0,
        ),
        (
            {
                "gas": "0x186a0",
                "maxFeePerGas": "0x77359400",
                "maxPriorityFeePerGas": "0x77359400",
                "data": "0x5544",
                "nonce": "0x2",
                "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
                "value": "0x5af3107a4000",
                "type": "0x2",
                "accessList": (
                    {
                        "address": "0x0000000000000000000000000000000000000001",
                        "storageKeys": (
                            "0x0100000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                        ),
                    },
                ),
                "chainId": 1,
            },
            "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318",
            HexBytes(
                "0x02f8ac010284773594008477359400830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544f838f7940000000000000000000000000000000000000001e1a0010000000000000000000000000000000000000000000000000000000000000001a0c5217aec4d576a1b5097c5054ed0157f762dd018f5c2195f0d0190ddca9445c5a0230a35968164ab4318a7042ca0ad4b4178a0d24c2cc000e13dfa24c206317935"  # noqa: E501
            ),
            HexBytes(
                "0xd42048e2a34957ab81f093d757be86453197bec95780d509fb3545d295227a34"
            ),
            89164785507787893778245375805371571349289793451450966346444410690555998389701,  # noqa: E501
            15848988021237185855591648888808312289463551127752258139478457465342262343989,  # noqa: E501
            1,
        ),
        (
            {
                "gas": "0x186a0",
                "maxFeePerGas": "0x77359400",
                "maxPriorityFeePerGas": "0x77359400",
                "data": "0x5544",
                "nonce": "0x2",
                "to": "0x96216849c49358B10257cb55b28eA603c874b05E",
                "value": "0x5af3107a4000",
                "type": "0x2",
                "chainId": 1,
            },
            "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318",
            HexBytes(
                "0x02f873010284773594008477359400830186a09496216849c49358b10257cb55b28ea603c874b05e865af3107a4000825544c080a07cfcd6472c4a29c566df07851c4708cb02523f71075221cc8e668908db58fde0a03b9185c7a719a99f2822dda5ed94c9f90641bd75578f093f15ceb71fc6ba85fc"  # noqa: E501
            ),
            HexBytes(
                "0x20a46a15e0b39815b44f01f3261a8741b095ed2bb4235339fa0e461251f9dc95"
            ),
            56533517577187861348991333001994723803575055479068550930552639362970253065696,  # noqa: E501
            26943574205696802233481851589848298424411617815775925360566652975894417278460,  # noqa: E501
            0,
        ),
    ),
    ids=[
        "web3js_example",
        "31byte_r_and_s",
        "access_list_txn",
        "dynamic_fee_txn",
        "dynamic_fee_txn_hex_fees",
    ],
)
def test_eth_account_sign_transaction(
    acct, txn, private_key, expected_raw_tx, tx_hash, r, s, v
):
    signed = acct.sign_transaction(txn, private_key)
    assert signed.r == r
    assert signed.s == s
    assert signed.v == v
    assert signed.raw_transaction == expected_raw_tx
    assert signed.hash == tx_hash

    account = acct.from_key(private_key)
    assert account.sign_transaction(txn) == signed

    expected_sender = acct.from_key(private_key).address
    assert acct.recover_transaction(signed.raw_transaction) == expected_sender


@pytest.mark.parametrize(
    "transaction_info",
    ETH_TEST_TRANSACTIONS,
)
def test_eth_account_sign_transaction_from_eth_test(acct, transaction_info):
    expected_raw_txn = transaction_info["signed"]
    key = transaction_info["key"]

    transaction = dissoc(transaction_info, "signed", "key", "unsigned")

    # validate r, in order to validate the transaction hash
    # There is some ambiguity about whether `r` will always be deterministically
    # generated from the transaction hash and private key, mostly due to code
    # author's ignorance. The example test fixtures and implementations
    # seem to agree, so far.
    # See ecdsa_raw_sign() in /eth_keys/backends/native/ecdsa.py
    signed = acct.sign_transaction(transaction, key)
    assert signed.r == Web3.to_int(hexstr=expected_raw_txn[-130:-66])

    # confirm that signed transaction can be recovered to the sender
    expected_sender = acct.from_key(key).address
    assert acct.recover_transaction(signed.raw_transaction) == expected_sender


@pytest.mark.parametrize(
    "transaction",
    ETH_TEST_TRANSACTIONS,
)
def test_eth_account_recover_transaction_from_eth_test(acct, transaction):
    raw_txn = transaction["signed"]
    key = transaction["key"]
    expected_sender = acct.from_key(key).address
    assert acct.recover_transaction(raw_txn) == expected_sender


def test_eth_account_encrypt(acct, web3js_key, web3js_password):
    encrypted = acct.encrypt(web3js_key, web3js_password)

    assert encrypted["address"] == "2c7536E3605D9C16a7a3D7b1898e529396a65c23"
    assert encrypted["version"] == 3

    decrypted_key = acct.decrypt(encrypted, web3js_password)

    assert decrypted_key == to_bytes(hexstr=web3js_key)


def test_eth_account_prepared_encrypt(acct, web3js_key, web3js_password):
    account = acct.from_key(web3js_key)
    encrypted = account.encrypt(web3js_password)

    assert encrypted["address"] == "2c7536E3605D9C16a7a3D7b1898e529396a65c23"
    assert encrypted["version"] == 3

    decrypted_key = acct.decrypt(encrypted, web3js_password)

    assert decrypted_key == to_bytes(hexstr=web3js_key)


@pytest.mark.xfail
@pytest.mark.parametrize(
    "expected_txn, raw_tx, expected_tx_hash, r, s, v",
    (
        (
            {
                "to": "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55",
                "value": 1000000000,
                "gas": 2000000,
                "gasPrice": 234567897654321,
                "nonce": 0,
                "chainId": 1,
            },
            HexBytes(
                "0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428"  # noqa: E501
            ),
            HexBytes(
                "0xd8f64a42b57be0d565f385378db2f6bf324ce14a594afc05de90436e9ce01f60"
            ),
            4487286261793418179817841024889747115779324305375823110249149479905075174044,  # noqa: E501
            30785525769477805655994251009256770582792548537338581640010273753578382951464,  # noqa: E501
            37,
        ),
        (
            {
                "to": "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55",
                "value": 0,
                "gas": 31853,
                "gasPrice": 0,
                "nonce": 0,
                "chainId": 1,
            },
            HexBytes(
                "0xf85d8080827c6d94f0109fc8df283027b6285cc889f5aa624eac1f558080269f22f17b38af35286ffbb0c6376c86ec91c20ecbad93f84913a0cc15e7580cd99f83d6e12e82e3544cb4439964d5087da78f74cefeec9a450b16ae179fd8fe20"  # noqa: E501
            ),
            HexBytes(
                "0xb0c5e2c6b29eeb0b9c1d63eaa8b0f93c02ead18ae01cb7fc795b0612d3e9d55a"
            ),
            61739443115046231975538240097110168545680205678104352478922255527799426265,
            232940010090391255679819602567388136081614408698362277324138554019997613600,
            38,
        ),
    ),
    ids=["web3js_example", "31byte_r_and_s"],
)
def test_eth_account_sign_and_send_EIP155_transaction_to_eth_tester(
    w3, expected_txn, raw_tx, expected_tx_hash, r, s, v
):
    actual_tx_hash = w3.eth.send_raw_transaction(raw_tx)
    assert actual_tx_hash == expected_tx_hash
    actual_txn = w3.eth.get_transaction(actual_tx_hash)
    for key in (
        "to",
        "nonce",
        "gas",
        "gasPrice",
        "value",
    ):
        assert actual_txn[key] == expected_txn[key]
    assert actual_txn.r == r
    assert actual_txn.s == s
    assert actual_txn.v == v


# -- async -- #


@pytest.fixture()
def async_w3():
    return AsyncWeb3(AsyncEthereumTesterProvider())


@patch("web3.eth.BaseEth.account", "wired via BaseEth")
def test_account_is_wired_via_base_eth_for_sync_and_async(w3, async_w3):
    # this gives us some comfort that all the `w3` tests would apply for `async_w3` as
    # well, since `Account` is static and not actually awaited
    assert w3.eth.account == "wired via BaseEth"
    assert async_w3.eth.account == "wired via BaseEth"


def test_async_eth_account_creates_account(async_w3):
    account = async_w3.eth.account.create()
    assert isinstance(account, LocalAccount)
    assert is_checksum_address(account.address)
    assert is_bytes(account.key)
