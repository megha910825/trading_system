#!/usr/bin/env python3
"""
Logging Setup - Centralized logging configuration
All modules should use the get_logger() function to get a configured logger
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Import config
try:
    import config
except ImportError:
    config = None


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    name: str = "trading_system",
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Setup and return a configured logger

    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                If None, uses config.LOG_LEVEL or defaults to INFO
        log_file: Path to log file. If None, uses config.LOG_FILE or no file logging

    Returns:
        Configured logger instance
    """

    # Determine log level
    if level is None:
        level = getattr(config, 'LOG_LEVEL', 'INFO') if config else 'INFO'

    # Determine log file
    if log_file is None:
        log_file = getattr(config, 'LOG_FILE', None) if config else None

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))

    console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_formatter = ColoredFormatter(
        console_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        # Create log directory if needed
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level))

        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file_formatter = logging.Formatter(
            file_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance (convenience function)

    Usage:
        from logging_setup import get_logger
        logger = get_logger(__name__)
        logger.info("Starting analysis...")
        logger.warning("Unexpected data format")
        logger.error("Failed to fetch data: %s", str(e))

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return setup_logging(name)


if __name__ == "__main__":
    # Test logging setup
    logger = get_logger("test")

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    print("\n✓ Logging setup is working correctly")
