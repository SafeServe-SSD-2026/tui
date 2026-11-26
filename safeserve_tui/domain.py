"""Immutable domain values with runtime validation at construction."""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from typeguard import TypeCheckError, check_type
from valid8 import ValidationError, validate


MIN_PRICE_CENTS: Final[int] = 1
MAX_PRICE_CENTS: Final[int] = 99_999
MIN_QUANTITY: Final[int] = 1
MAX_QUANTITY: Final[int] = 50
MIN_TABLE_NUMBER: Final[int] = 1
MAX_TABLE_NUMBER: Final[int] = 99
MIN_SEAT_COUNT: Final[int] = 1
MAX_SEAT_COUNT: Final[int] = 20


def _validate_bounded_integer(
    value: int, name: str, minimum: int, maximum: int
) -> None:
    """Validate types before ranges, without coercion or rounding."""
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not a boolean")
    try:
        check_type(value, int)
    except TypeCheckError:
        raise TypeError(f"{name} must be an integer") from None
    try:
        validate(name, value, min_value=minimum, max_value=maximum)
    except ValidationError:
        raise ValueError(
            f"{name} must be between {minimum} and {maximum} inclusive"
        ) from None


@dataclass(frozen=True)
class Price:
    """A dish's unit price in integer cents, from 0.01 to 999.99 euros.

    This constraint applies to a single dish, not to an order's total.
    """

    cents: int

    def __post_init__(self) -> None:
        _validate_bounded_integer(
            self.cents, "Price in cents", MIN_PRICE_CENTS, MAX_PRICE_CENTS
        )


@dataclass(frozen=True)
class Quantity:
    """The number of dishes in an order line, from 1 to 50."""

    value: int

    def __post_init__(self) -> None:
        _validate_bounded_integer(
            self.value, "Quantity", MIN_QUANTITY, MAX_QUANTITY
        )


@dataclass(frozen=True)
class TableNumber:
    """A restaurant table number, from 1 to 99."""

    value: int

    def __post_init__(self) -> None:
        _validate_bounded_integer(
            self.value, "Table number", MIN_TABLE_NUMBER, MAX_TABLE_NUMBER
        )


@dataclass(frozen=True)
class SeatCount:
    """The number of seats at a table, from 1 to 20."""

    value: int

    def __post_init__(self) -> None:
        _validate_bounded_integer(
            self.value, "Seat count", MIN_SEAT_COUNT, MAX_SEAT_COUNT
        )


class Category(Enum):
    """Fixed dish categories using the documented domain values."""

    STARTER = "ANTIPASTO"
    FIRST_COURSE = "PRIMO"
    MAIN_COURSE = "SECONDO"
    SIDE_DISH = "CONTORNO"
    DESSERT = "DOLCE"
    DRINK = "BIBITA"
