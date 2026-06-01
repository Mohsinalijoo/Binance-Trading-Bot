"""Input validation helpers for CLI order arguments."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
VALID_TIME_IN_FORCE = {"GTC", "IOC", "FOK"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class ValidationError(ValueError):
    """Raised when CLI input is invalid."""


def validate_order_input(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    time_in_force: str = "GTC",
) -> dict[str, str | None]:
    normalized_symbol = validate_symbol(symbol)
    normalized_side = validate_choice(side, VALID_SIDES, "side")
    normalized_order_type = validate_choice(order_type, VALID_ORDER_TYPES, "order type")
    normalized_quantity = validate_positive_decimal(quantity, "quantity")
    normalized_time_in_force = validate_choice(time_in_force, VALID_TIME_IN_FORCE, "time in force")

    normalized_price: str | None = None
    if normalized_order_type == "LIMIT":
        if price is None or str(price).strip() == "":
            raise ValidationError("price is required for LIMIT orders.")
        normalized_price = validate_positive_decimal(price, "price")
    elif price is not None and str(price).strip() != "":
        raise ValidationError("price should only be supplied for LIMIT orders.")

    return {
        "symbol": normalized_symbol,
        "side": normalized_side,
        "order_type": normalized_order_type,
        "quantity": normalized_quantity,
        "price": normalized_price,
        "time_in_force": normalized_time_in_force,
    }


def validate_symbol(value: str) -> str:
    symbol = str(value).strip().upper()
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise ValidationError("symbol must look like BTCUSDT, ETHUSDT, or another USDT-M futures symbol.")
    return symbol


def validate_choice(value: str, valid_values: set[str], field_name: str) -> str:
    normalized = str(value).strip().upper()
    if normalized not in valid_values:
        allowed = ", ".join(sorted(valid_values))
        raise ValidationError(f"{field_name} must be one of: {allowed}.")
    return normalized


def validate_positive_decimal(value: str, field_name: str) -> str:
    try:
        decimal_value = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid number.") from exc

    if not decimal_value.is_finite() or decimal_value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")

    return decimal_to_string(decimal_value)


def decimal_to_string(value: Decimal) -> str:
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text

