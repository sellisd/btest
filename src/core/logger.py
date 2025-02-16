"""Logging configuration for the btest package."""

import logging
from .config import log_config


def setup_logger(name: str) -> logging.Logger:
    """Set up and return a logger instance.

    Args:
        name: Name for the logger, typically __name__ of the module.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:  # Avoid adding handlers if they already exist
        handler = logging.StreamHandler()
        formatter = logging.Formatter(log_config.format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        level = getattr(logging, log_config.level.upper(), logging.INFO)
        logger.setLevel(level)

    return logger


# Create package-level logger
logger = setup_logger("btest")
