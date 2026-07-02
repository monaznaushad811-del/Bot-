"""
Logging configuration for the trading bot.

Sets up a logger that writes to both the console and a rotating log file
(logs/trading_bot.log), capturing API requests, responses, and errors.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
)
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the shared 'trading_bot' logger."""
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(level)
    logger.propagate = False

    # Avoid attaching duplicate handlers if setup_logging() is called more than once.
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
