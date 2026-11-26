"""Tests for immutable domain values and documented restaurant constraints."""

import subprocess
import sys
import textwrap
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from safeserve_tui.domain import (
    Category,
    Price,
    Quantity,
    SeatCount,
    TableNumber,
)


NUMERIC_VALUES = [
    (Price, "cents", 1, 99_999),
    (Quantity, "value", 1, 50),
    (TableNumber, "value", 1, 99),
    (SeatCount, "value", 1, 20),
]


@pytest.mark.parametrize("primitive, field, minimum, maximum", NUMERIC_VALUES)
def test_numeric_values_accept_inclusive_boundaries(
    primitive, field, minimum, maximum
):
    for value in (minimum, (minimum + maximum) // 2, maximum):
        assert getattr(primitive(value), field) == value


@pytest.mark.parametrize("primitive, field, minimum, maximum", NUMERIC_VALUES)
@pytest.mark.parametrize("boundary", ["below", "above"])
def test_numeric_values_reject_values_outside_the_range(
    primitive, field, minimum, maximum, boundary
):
    value = minimum - 1 if boundary == "below" else maximum + 1

    with pytest.raises(ValueError):
        primitive(value)


@pytest.mark.parametrize("primitive, field, minimum, maximum", NUMERIC_VALUES)
@pytest.mark.parametrize("value", [
    None, True, False, "1", "", 1.0, Decimal("1"), [], {}, Quantity(1),
])
def test_numeric_values_reject_wrong_types(
    primitive, field, minimum, maximum, value
):
    with pytest.raises(TypeError):
        primitive(value)


@pytest.mark.parametrize("primitive, field, minimum, maximum", NUMERIC_VALUES)
def test_numeric_values_reject_negative_integers(
    primitive, field, minimum, maximum
):
    with pytest.raises(ValueError):
        primitive(-1)


@pytest.mark.parametrize("primitive, field, minimum, maximum", NUMERIC_VALUES)
def test_numeric_values_are_immutable(primitive, field, minimum, maximum):
    instance = primitive(minimum)

    with pytest.raises(FrozenInstanceError):
        setattr(instance, field, maximum)

    assert getattr(instance, field) == minimum


@pytest.mark.parametrize("primitive, field, minimum, maximum", NUMERIC_VALUES)
def test_numeric_values_have_value_equality_and_hashes(
    primitive, field, minimum, maximum
):
    first = primitive(minimum)
    second = primitive(minimum)

    assert first == second
    assert hash(first) == hash(second)
    assert first != primitive(maximum)
    assert first != minimum


def test_different_domain_concepts_are_not_equal():
    assert Quantity(1) != TableNumber(1)
    assert TableNumber(1) != SeatCount(1)
    assert Price(1) != Quantity(1)


def test_price_preserves_integer_cents_without_rounding():
    assert Price(1).cents == 1
    assert Price(850).cents == 850
    assert Price(99_999).cents == 99_999


def test_category_contains_exactly_the_documented_values():
    assert {category.value for category in Category} == {
        "ANTIPASTO", "PRIMO", "SECONDO", "CONTORNO", "DOLCE", "BIBITA",
    }


@pytest.mark.parametrize("category", list(Category))
def test_category_accepts_documented_values(category):
    assert Category(category.value) is category
    assert category != category.value


@pytest.mark.parametrize("value", [
    "", "primo", " PRIMO ", "PIZZA", None, 1, True,
])
def test_category_rejects_unknown_values_without_normalizing(value):
    with pytest.raises(ValueError):
        Category(value)


def test_category_value_cannot_be_reassigned():
    category = Category.FIRST_COURSE

    with pytest.raises(AttributeError):
        category.value = "PIZZA"

    assert category.value == "PRIMO"



def test_validation_remains_active_with_python_optimization():
    script = textwrap.dedent(
        """
        from safeserve_tui.domain import (
            Price, Quantity, SeatCount, TableNumber,
        )

        for primitive in (Price, Quantity, SeatCount, TableNumber):
            primitive(1)
            for value, error in (
                (0, ValueError),
                (100_000, ValueError),
                (True, TypeError),
                ("1", TypeError),
            ):
                try:
                    primitive(value)
                except error:
                    pass
                else:
                    raise AssertionError("Invalid value was accepted")
        """
    )
    result = subprocess.run(
        [sys.executable, "-O", "-c", script],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
