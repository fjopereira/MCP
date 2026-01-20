"""
Base provider interface for API integrations.

This module defines the abstract base class that all providers must implement.
This enables extensibility to other security platforms in the future.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    Abstract base class for API providers.

    All providers must implement these methods to ensure consistent
    initialization, cleanup, and client access patterns.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the provider connection.

        This should handle authentication, connection setup,
        and any other initialization logic.

        Raises:
            ConnectionError: If unable to establish connection
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Cleanup provider resources.

        This should properly close connections, cleanup sessions,
        and release any resources.
        """
        pass

    @abstractmethod
    def get_client(self) -> Any:
        """
        Get the underlying API client.

        Returns:
            Any: The provider's API client instance

        Raises:
            RuntimeError: If provider is not initialized
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Perform a health check to verify the connection is working.

        Returns:
            bool: True if healthy, False otherwise
        """
        pass
