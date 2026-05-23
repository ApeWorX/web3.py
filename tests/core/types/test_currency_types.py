from web3.types import (
    Gwei,
    Wei,
)


def test_wei_arithmetic_preserves_type() -> None:
    value = Wei(5)

    value += Wei(1)

    assert value == 6
    assert isinstance(value, Wei)
    assert isinstance(value + 1, Wei)
    assert isinstance(1 + value, Wei)
    assert isinstance(value - 1, Wei)
    assert isinstance(10 - value, Wei)
    assert isinstance(value * 2, Wei)
    assert isinstance(2 * value, Wei)
    assert isinstance(value // 2, Wei)
    assert isinstance(value % 4, Wei)
    assert isinstance(-value, Wei)
    assert isinstance(+value, Wei)
    assert isinstance(abs(value), Wei)
    quotient, remainder = divmod(value, 4)
    assert isinstance(quotient, Wei)
    assert isinstance(remainder, Wei)


def test_gwei_arithmetic_preserves_type() -> None:
    value = Gwei(5)

    value -= Gwei(1)

    assert value == 4
    assert isinstance(value, Gwei)
    assert isinstance(value + 1, Gwei)
