"""
CrowdStrike Falcon API provider implementation.

This module implements the CrowdStrike Falcon API integration using FalconPy.
It handles OAuth2 authentication, token management, and provides access to
Falcon API service collections.
"""

import time
from typing import Any

from falconpy import Hosts, Incidents, Detects, OAuth2

from mcp_crowdstrike.config import Settings
from mcp_crowdstrike.providers.base import BaseProvider
from mcp_crowdstrike.utils.logging import get_logger

logger = get_logger(__name__)


class CrowdStrikeProvider(BaseProvider):
    """
    CrowdStrike Falcon API provider.

    This provider manages the connection to CrowdStrike Falcon API,
    handles OAuth2 authentication, token refresh, and exposes
    service collections for different API endpoints.

    Security features:
        - HTTPS only communication
        - Automatic token refresh before expiry
        - Credentials never logged
        - Tokens stored in memory only

    Attributes:
        hosts: Falcon Hosts API service collection
        detects: Falcon Detections API service collection
        incidents: Falcon Incidents API service collection
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the CrowdStrike provider.

        Args:
            settings: Application settings containing Falcon credentials
        """
        self._settings = settings
        self._oauth2: OAuth2 | None = None
        self._hosts: Hosts | None = None
        self._detects: Detects | None = None
        self._incidents: Incidents | None = None
        self._token_expiry: float = 0.0
        self._initialized = False

        logger.info(
            "CrowdStrike provider created",
            extra={"base_url": settings.falcon_base_url},
        )

    async def initialize(self) -> None:
        """
        Initialize the CrowdStrike Falcon API connection.

        This performs OAuth2 authentication and initializes service collections.

        Raises:
            ConnectionError: If unable to connect to Falcon API
            ValueError: If authentication fails
        """
        if self._initialized:
            logger.warning("Provider already initialized")
            return

        try:
            logger.info("Initializing CrowdStrike Falcon API connection")

            # Get credentials
            client_id, client_secret = self._settings.get_falcon_credentials()

            # Validate base URL uses HTTPS
            if not self._settings.falcon_base_url.startswith("https://"):
                logger.warning(
                    "Base URL does not use HTTPS - this is insecure!",
                    extra={"base_url": self._settings.falcon_base_url},
                )

            # Initialize OAuth2 client
            self._oauth2 = OAuth2(
                client_id=client_id,
                client_secret=client_secret,
                base_url=self._settings.falcon_base_url,
            )

            # Authenticate and get token
            auth_result = self._oauth2.token()

            if not auth_result or auth_result.get("status_code") != 201:
                error_msg = auth_result.get("body", {}).get(
                    "errors", ["Unknown authentication error"]
                )
                logger.error(
                    "Failed to authenticate with CrowdStrike",
                    extra={"error": error_msg},
                )
                raise ValueError(f"Authentication failed: {error_msg}")

            # Store token expiry time (with 5 minute buffer)
            expires_in = auth_result.get("body", {}).get("expires_in", 1800)
            self._token_expiry = time.time() + expires_in - 300

            logger.info(
                "Successfully authenticated with CrowdStrike",
                extra={"expires_in": expires_in},
            )

            # Initialize service collections
            token = auth_result["body"]["access_token"]

            self._hosts = Hosts(
                access_token=token,
                base_url=self._settings.falcon_base_url,
            )

            self._detects = Detects(
                access_token=token,
                base_url=self._settings.falcon_base_url,
            )

            self._incidents = Incidents(
                access_token=token,
                base_url=self._settings.falcon_base_url,
            )

            self._initialized = True
            logger.info("CrowdStrike provider initialized successfully")

        except Exception as e:
            logger.error(
                "Failed to initialize CrowdStrike provider",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise ConnectionError(f"Failed to initialize provider: {e}") from e

    async def shutdown(self) -> None:
        """
        Cleanup CrowdStrike provider resources.

        Properly closes connections and releases resources.
        """
        logger.info("Shutting down CrowdStrike provider")

        # Revoke token if possible
        if self._oauth2:
            try:
                self._oauth2.revoke(
                    token=self._oauth2.token_value if hasattr(self._oauth2, 'token_value') else None
                )
            except Exception as e:
                logger.warning(
                    "Failed to revoke token during shutdown",
                    extra={"error": str(e)},
                )

        self._oauth2 = None
        self._hosts = None
        self._detects = None
        self._incidents = None
        self._initialized = False

        logger.info("CrowdStrike provider shutdown complete")

    def get_client(self) -> dict[str, Any]:
        """
        Get the CrowdStrike service collections.

        Returns:
            dict[str, Any]: Dictionary containing service collections
                - hosts: Hosts API
                - detects: Detections API
                - incidents: Incidents API

        Raises:
            RuntimeError: If provider is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        return {
            "hosts": self._hosts,
            "detects": self._detects,
            "incidents": self._incidents,
        }

    async def health_check(self) -> bool:
        """
        Perform a health check on the CrowdStrike connection.

        Tests the connection with a lightweight API call.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        if not self._initialized:
            logger.warning("Health check called on uninitialized provider")
            return False

        try:
            # Check if token needs refresh
            if time.time() >= self._token_expiry:
                logger.info("Token expired, re-initializing provider")
                await self.shutdown()
                await self.initialize()

            # Perform lightweight query to test connection
            if self._hosts:
                result = self._hosts.query_devices_by_filter(limit=1)
                if result.get("status_code") == 200:
                    logger.info("Health check passed")
                    return True

            logger.warning("Health check failed - unexpected response")
            return False

        except Exception as e:
            logger.error(
                "Health check failed with exception",
                extra={"error": str(e)},
                exc_info=True,
            )
            return False

    @property
    def hosts(self) -> Hosts:
        """
        Get the Hosts API service collection.

        Returns:
            Hosts: FalconPy Hosts service collection

        Raises:
            RuntimeError: If provider is not initialized
        """
        if not self._initialized or self._hosts is None:
            raise RuntimeError("Provider not initialized")
        return self._hosts

    @property
    def detects(self) -> Detects:
        """
        Get the Detections API service collection.

        Returns:
            Detects: FalconPy Detects service collection

        Raises:
            RuntimeError: If provider is not initialized
        """
        if not self._initialized or self._detects is None:
            raise RuntimeError("Provider not initialized")
        return self._detects

    @property
    def incidents(self) -> Incidents:
        """
        Get the Incidents API service collection.

        Returns:
            Incidents: FalconPy Incidents service collection

        Raises:
            RuntimeError: If provider is not initialized
        """
        if not self._initialized or self._incidents is None:
            raise RuntimeError("Provider not initialized")
        return self._incidents

    async def refresh_token_if_needed(self) -> None:
        """
        Refresh the authentication token if it's close to expiry.

        This should be called before making API requests to ensure
        the token is valid.
        """
        if time.time() >= self._token_expiry:
            logger.info("Token expiring soon, refreshing")
            await self.shutdown()
            await self.initialize()
