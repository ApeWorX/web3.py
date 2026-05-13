import json

import pytest

from web3.types import (
    Gwei,
    Wei,
)


@pytest.mark.parametrize("cls", [Wei, Gwei])
def test_value_is_int_subclass(cls):
    value = cls(5)
    assert isinstance(value, int)
    assert isinstance(value, cls)
    assert value == 5
    assert hash(value) == hash(5)


@pytest.mark.parametrize("cls", [Wei, Gwei])
def test_addition_preserves_type(cls):
    assert type(cls(2) + cls(3)) is cls
    assert type(cls(2) + 3) is cls
    assert type(3 + cls(2)) is cls

    total = cls(0)
    total += cls(7)
    assert total == 7
    assert type(total) is cls


@pytest.mark.parametrize("cls", [Wei, Gwei])
def test_subtraction_preserves_type(cls):
    assert type(cls(5) - cls(2)) is cls
    assert type(cls(5) - 2) is cls
    assert type(10 - cls(2)) is cls


@pytest.mark.parametrize("cls", [Wei, Gwei])
def test_multiplication_by_scalar_preserves_type(cls):
    assert type(cls(5) * 3) is cls
    assert type(3 * cls(5)) is cls
    assert cls(5) * 3 == 15


@pytest.mark.parametrize("cls", [Wei, Gwei])
def test_floor_division_and_mod_preserve_type(cls):
    assert type(cls(10) // 3) is cls
    assert type(cls(10) % 3) is cls
    assert cls(10) // 3 == 3
    assert cls(10) % 3 == 1


@pytest.mark.parametrize("cls", [Wei, Gwei])
def test_unary_operators_preserve_type(cls):
    assert type(-cls(5)) is cls
    assert type(+cls(5)) is cls
    assert type(abs(cls(-5))) is cls
    assert abs(cls(-5)) == 5


@pytest.mark.parametrize("cls", [Wei, Gwei])
def test_true_division_returns_float(cls):
    # Dividing a quantity by a scalar is no longer the same unit, so true
    # division deliberately falls back to int's behaviour and returns float.
    result = cls(10) / 2
    assert isinstance(result, float)
    assert result == 5.0


@pytest.mark.parametrize("cls", [Wei, Gwei])
def test_serializes_as_int(cls):
    assert json.dumps({"v": cls(123)}) == '{"v": 123}'


def test_wei_and_gwei_are_distinct_types():
    assert Wei is not Gwei
    assert type(Wei(1)) is Wei
    assert type(Gwei(1)) is Gwei
    # Mixed operations follow the left-operand's type (standard Python rules
    # for int subclasses), which is fine for typing purposes: the issue is
    # about preserving the *type* of a value through arithmetic, not about
    # encoding cross-unit conversions in the type system.
    assert type(Wei(1) + Gwei(1)) is Wei
    assert type(Gwei(1) + Wei(1)) is Gwei
