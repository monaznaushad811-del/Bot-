#!/usr/bin/env python3
"""
CLI entry point for the Simplified Trading Bot (Binance Futures Testnet).

Examples
--------
Market order:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

Limit order:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000

Stop-limit order (bonus):
    python cli.py --symbol BTCUSDT --side BUY --type STOP-LIMIT --quantity 0.01 \\
        --price 61000 --stop-price 60900

API credentials can be passed via --api-key/--api-secret, or via the
BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET environment variables.
"""
import argparse
import os
import sys

from bot.client import BasicBot
from bot.logging_config import setup_logging
from bot.orders import OrderManager
from bot.validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simplified trading bot for Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument(
        "--side", required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side",
    )
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP-LIMIT", "market", "limit", "stop-limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument(
        "--price", required=False,
        help="Price (required for LIMIT and STOP-LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price", dest="stop_price", required=False,
        help="Stop trigger price (required for STOP-LIMIT orders)",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("BINANCE_TESTNET_API_KEY"),
        help="Binance Futures Testnet API key (or set BINANCE_TESTNET_API_KEY)",
    )
    parser.add_argument(
        "--api-secret",
        default=os.environ.get("BINANCE_TESTNET_API_SECRET"),
        help="Binance Futures Testnet API secret (or set BINANCE_TESTNET_API_SECRET)",
    )
    return parser


def main(argv=None) -> None:
    logger = setup_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.api_key or not args.api_secret:
        print(
            "Error: API key/secret not provided. Pass --api-key/--api-secret or "
            "set BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET."
        )
        sys.exit(1)

    # --- Validation layer ---
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)

        price_required = order_type in ("LIMIT", "STOP-LIMIT")
        price = validate_price(args.price, required=price_required)

        stop_price = None
        if order_type == "STOP-LIMIT":
            stop_price = validate_price(args.stop_price, required=True)
    except ValidationError as e:
        logger.error("Validation error: %s", e)
        print(f"Input error: {e}")
        sys.exit(1)

    # --- Order request summary ---
    print("=" * 50)
    print("Order Request Summary")
    print("=" * 50)
    print(f"Symbol:      {symbol}")
    print(f"Side:        {side}")
    print(f"Type:        {order_type}")
    print(f"Quantity:    {quantity}")
    if price is not None:
        print(f"Price:       {price}")
    if stop_price is not None:
        print(f"Stop Price:  {stop_price}")
    print("=" * 50)

    # --- Order placement ---
    try:
        bot = BasicBot(args.api_key, args.api_secret, testnet=True)
        order_manager = OrderManager(bot)

        if order_type == "MARKET":
            result = order_manager.place_market_order(symbol, side, quantity)
        elif order_type == "LIMIT":
            result = order_manager.place_limit_order(symbol, side, quantity, price)
        elif order_type == "STOP-LIMIT":
            result = order_manager.place_stop_limit_order(
                symbol, side, quantity, price, stop_price
            )
        else:  # pragma: no cover - guarded by validate_order_type
            raise ValueError(f"Unsupported order type: {order_type}")

    except Exception as e:
        logger.error("Order placement failed: %s", e)
        print(f"\nOrder FAILED: {e}")
        sys.exit(1)

    # --- Order response details ---
    print("\nOrder Response Details")
    print("-" * 50)
    print(f"Order ID:      {result.get('orderId')}")
    print(f"Status:        {result.get('status')}")
    print(f"Executed Qty:  {result.get('executedQty')}")
    avg_price = result.get("avgPrice")
    if avg_price is not None:
        print(f"Avg Price:     {avg_price}")
    print("-" * 50)
    print("\nOrder placed SUCCESSFULLY.")


if __name__ == "__main__":
    main()
