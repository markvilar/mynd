"""Module for logging functionality."""

from typing import Protocol

import loguru


class Logger(Protocol):
    """Interface for a logger class."""

    def trace(message: str) -> None:
        """Logs the message with trace severity."""
        ...

    def debug(message: str) -> None:
        """Logs the message with debug severity."""
        ...

    def info(message: str) -> None:
        """Logs the message with info severity."""
        ...

    def success(message: str) -> None:
        """Logs the message with success severity."""
        ...

    def warning(message: str) -> None:
        """Logs the message with warning severity."""
        ...

    def error(message: str) -> None:
        """Logs the message with error severity."""
        ...

    def critical(message: str) -> None:
        """Logs the message with critical severity."""
        ...


logger = loguru.logger
