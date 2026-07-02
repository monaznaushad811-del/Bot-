"""
Input validation helpers for the trading bot CLI.

Keeping validation separate from the CLI and API layers makes it easy to
unit test and reuse (e.g. from a future web UI).
"""
import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP-LIMIT"}

# Binance Futures symbols are uppercase alphanumeric, e.g. BTCUSDT, ETHUSDT.
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,15}$")


class ValidationError(Exception):
    """Raised when user-supplied CLI input fails validation."""


def validate_symbol(symbol: str) -> str:
    if symbol is None:
        raise ValidationError("Symbol is required.")
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected format like BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    if side is None:
        raise ValidationError("Side is required.")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be BUY or SELL.")
    return side


def validate_order_type(order_type: str) -> str:
    if order_type is None:
        raise ValidationError("Order type is required.")
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    return quantity


def validate_price(price, required: bool) -> float:
    if price is None:
        if required:
            raise ValidationError("Price is required for this order type.")
        return None
    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Price must be a number, got '{price}'.")
    if price <= 0:
        raise ValidationError("Price must be greater than 0.")
    return price
