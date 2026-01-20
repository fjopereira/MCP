"""
Structured logging utilities for MCP CrowdStrike.

This module provides JSON-formatted structured logging for production observability.
All logs include timestamp, level, message, and optional context fields.
"""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging.

    Adds additional fields and ensures consistent formatting across all logs.
    """

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """
        Add custom fields to the log record.

        Args:
            log_record: The log record dictionary to modify
            record: The original logging.LogRecord
            message_dict: Additional message context
        """
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def get_logger(
    name: str,
    level: str | int = logging.INFO,
    json_format: bool = True,
) -> logging.Logger:
    """
    Get or create a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting (default: True)

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing device", extra={"device_id": "abc123"})
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Configure formatter
    if json_format:
        formatter = CustomJsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def configure_root_logger(level: str | int = logging.INFO) -> None:
    """
    Configure the root logger with structured JSON logging.

    This should be called once at application startup.

    Args:
        level: Logging level for the root logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add JSON handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = CustomJsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds context to all log messages.

    Example:
        >>> base_logger = get_logger(__name__)
        >>> logger = LoggerAdapter(base_logger, {"request_id": "req-123"})
        >>> logger.info("Processing request")  # Will include request_id
    """

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """
        Process the log message to add extra context.

        Args:
            msg: Log message
            kwargs: Keyword arguments for the log call

        Returns:
            tuple[str, dict[str, Any]]: Processed message and kwargs
        """
        # Merge adapter's extra context with call's extra context
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
