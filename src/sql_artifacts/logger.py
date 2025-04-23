"""
Centralized logger configuration for the sql_artifacts package.

This module provides a reusable `get_logger()` function that returns a properly
configured logger instance for consistent and readable logging throughout the
project.

Key Features:
- Ensures that log handlers are only added once (avoids duplicate logs).
- Formats logs with timestamps, log level, logger name, and message.
- Outputs to stdout using StreamHandler.
- Supports `LOG_LEVEL` environment variable for dynamic verbosity.

Usage:
    from sql_artifacts.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Hello, logging world!")

Set log level via environment:
    LOG_LEVEL=DEBUG python my_script.py
"""

import logging
import os


def get_logger(name: str = "sql_artifacts") -> logging.Logger:
    """
    Returns a logger instance with standardized formatting and output behavior.

    Args:
        name (str): Name of the logger, typically __name__ for module-level loggers.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if not logger.handlers:
        # Set up stream output to terminal
        handler = logging.StreamHandler()

        # Define log message format
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

        # Determine log level from env var, fallback to INFO
        level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        logger.setLevel(level)

        logger.debug(f"Logger initialized at level: {level_name}")

    return logger
