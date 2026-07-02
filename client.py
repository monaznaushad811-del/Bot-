"""
Binance Futures Testnet client wrapper.

Wraps the python-binance Client so the rest of the app never has to know
about SDK / endpoint details directly.
"""
import logging

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

logger = logging.getLogger("trading_bot")

# For reference: this is the futures testnet host python-binance routes to
# internally (via FUTURES_TESTNET_URL) whenever Client(..., testnet=True) is used.
TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BasicBot:
    """
    A simplified trading bot wrapper around python-binance's Client,
    configured to talk to the Binance Futures Testnet (USDT-M).

    python-binance automatically routes futures_* calls to
    FUTURES_TESTNET_URL ("https://testnet.binancefuture.com/fapi") whenever
    the client is constructed with testnet=True, so no manual URL override
    is required.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        # ping=False: skip the constructor's spot-market connectivity check,
        # since this bot only talks to the futures testnet.
        self.client = Client(api_key, api_secret, testnet=testnet, ping=False)
        logger.info("Initialized Binance client (testnet=%s)", testnet)

    def get_account_balance(self):
        """Fetch USDT-M futures account balances (useful for sanity checks)."""
        try:
            balances = self.client.futures_account_balance()
            logger.info("Fetched account balance: %s", balances)
            return balances
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error("Error fetching account balance: %s", e)
            raise

    def get_symbol_price(self, symbol: str) -> float:
        """Fetch the latest mark price for a symbol."""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker["price"])
            logger.info("Fetched price for %s: %s", symbol, price)
            return price
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error("Error fetching price for %s: %s", symbol, e)
            raise
