"""
Order placement logic for the trading bot.

Every method here logs the request it is about to make and the response
(or error) it receives, and raises so the CLI layer can report failures.
"""
import logging

from binance.exceptions import BinanceAPIException, BinanceOrderException

logger = logging.getLogger("trading_bot")


class OrderManager:
    """Places MARKET, LIMIT, and (bonus) STOP-LIMIT orders on Binance Futures."""

    def __init__(self, bot):
        self.bot = bot
        self.client = bot.client

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        logger.info(
            "Placing MARKET order | symbol=%s side=%s quantity=%s",
            symbol, side, quantity,
        )
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity,
            )
            logger.info("MARKET order response: %s", order)
            return order
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error("Failed to place MARKET order: %s", e)
            raise

    def place_limit_order(
        self, symbol: str, side: str, quantity: float, price: float,
        time_in_force: str = "GTC",
    ) -> dict:
        logger.info(
            "Placing LIMIT order | symbol=%s side=%s quantity=%s price=%s tif=%s",
            symbol, side, quantity, price, time_in_force,
        )
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce=time_in_force,
            )
            logger.info("LIMIT order response: %s", order)
            return order
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error("Failed to place LIMIT order: %s", e)
            raise

    def place_stop_limit_order(
        self, symbol: str, side: str, quantity: float, price: float,
        stop_price: float, time_in_force: str = "GTC",
    ) -> dict:
        """Bonus: STOP-LIMIT order support (Binance order type 'STOP')."""
        logger.info(
            "Placing STOP-LIMIT order | symbol=%s side=%s quantity=%s "
            "price=%s stop_price=%s tif=%s",
            symbol, side, quantity, price, stop_price, time_in_force,
        )
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="STOP",
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                timeInForce=time_in_force,
            )
            logger.info("STOP-LIMIT order response: %s", order)
            return order
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error("Failed to place STOP-LIMIT order: %s", e)
            raise
