"""V1: Unit-aware, nonnegative emission calculations."""
from decimal import Decimal, InvalidOperation


def to_decimal(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError('Invalid numeric value') from exc
    if not result.is_finite() or result < 0:
        raise ValueError('Value must be finite and nonnegative')
    return result


def calculate_emissions(quantity, factor):
    return to_decimal(quantity) * to_decimal(factor)
