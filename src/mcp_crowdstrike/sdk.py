"""
CrowdStrike Falcon SDK Client.

This module provides a Python SDK for programmatic access to CrowdStrike Falcon API
through the MCP tools. This enables dual-mode functionality - the same code can be
used as a library or as a server.
"""

from typing import Any

from mcp_crowdstrike.config import Settings
from mcp_crowdstrike.providers.crowdstrike import CrowdStrikeProvider
from mcp_crowdstrike.tools.crowdstrike import detections, hosts, incidents
from mcp_crowdstrike.utils.logging import get_logger

logger = get_logger(__name__)


class CrowdStrikeClient:
    """
    CrowdStrike Falcon API Client (SDK mode).

    This client provides high-level methods for interacting with CrowdStrike Falcon API.
    It can be used as a standalone library for building security automation tools.

    Example:
        >>> async with CrowdStrikeClient(
        ...     client_id="your-client-id",
        ...     client_secret="your-client-secret"
        ... ) as client:
        ...     devices = await client.query_devices_by_filter(limit=10)
        ...     print(devices)
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.crowdstrike.com",
    ) -> None:
        """
        Initialize the CrowdStrike client.

        Args:
            client_id: CrowdStrike Falcon API client ID
            client_secret: CrowdStrike Falcon API client secret
            base_url: CrowdStrike Falcon API base URL (default: US-1)
        """
        # Create settings from provided credentials
        import os
        os.environ["FALCON_CLIENT_ID"] = client_id
        os.environ["FALCON_CLIENT_SECRET"] = client_secret
        os.environ["FALCON_BASE_URL"] = base_url

        # Import here to avoid circular dependency
        from pydantic import SecretStr

        self._settings = Settings(
            falcon_client_id=SecretStr(client_id),
            falcon_client_secret=SecretStr(client_secret),
            falcon_base_url=base_url,
        )

        self._provider = CrowdStrikeProvider(self._settings)
        self._initialized = False

        logger.info("CrowdStrike SDK client created")

    async def __aenter__(self) -> "CrowdStrikeClient":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def initialize(self) -> None:
        """
        Initialize the client and connect to CrowdStrike API.

        Raises:
            ConnectionError: If unable to connect to CrowdStrike API
        """
        if self._initialized:
            return

        logger.info("Initializing CrowdStrike SDK client")
        await self._provider.initialize()
        self._initialized = True
        logger.info("CrowdStrike SDK client initialized")

    async def close(self) -> None:
        """
        Close the client and cleanup resources.
        """
        if not self._initialized:
            return

        logger.info("Closing CrowdStrike SDK client")
        await self._provider.shutdown()
        self._initialized = False
        logger.info("CrowdStrike SDK client closed")

    def _ensure_initialized(self) -> None:
        """Ensure client is initialized before making API calls."""
        if not self._initialized:
            raise RuntimeError(
                "Client not initialized. Use 'async with' or call initialize() first."
            )

    # Host Management Methods

    async def query_devices_by_filter(
        self,
        filter: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """
        Search for hosts using FQL filters.

        Args:
            filter: FQL filter expression (e.g., "platform_name:'Windows'")
            limit: Maximum number of results (1-5000)
            offset: Pagination offset
            sort: Sort field and direction (e.g., "hostname.asc")

        Returns:
            dict[str, Any]: Query results with device IDs

        Example:
            >>> devices = await client.query_devices_by_filter(
            ...     filter="platform_name:'Windows'",
            ...     limit=10
            ... )
        """
        self._ensure_initialized()
        arguments = {
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }
        return await hosts.execute_tool(
            self._provider,
            "query_devices_by_filter",
            arguments,
        )

    async def get_device_details(
        self,
        device_ids: list[str],
    ) -> dict[str, Any]:
        """
        Get detailed information about specific hosts.

        Args:
            device_ids: List of device IDs to retrieve

        Returns:
            dict[str, Any]: Device details

        Example:
            >>> details = await client.get_device_details(
            ...     device_ids=["abc123", "def456"]
            ... )
        """
        self._ensure_initialized()
        return await hosts.execute_tool(
            self._provider,
            "get_device_details",
            {"device_ids": device_ids},
        )

    async def contain_host(
        self,
        device_id: str,
    ) -> dict[str, Any]:
        """
        ⚠️ CRITICAL ACTION: Isolate a host from the network.

        This prevents the host from communicating on the network except with
        CrowdStrike cloud. Use this for incident response to prevent lateral
        movement.

        Args:
            device_id: Device ID to contain

        Returns:
            dict[str, Any]: Containment operation result

        Example:
            >>> result = await client.contain_host(device_id="abc123")
        """
        self._ensure_initialized()
        return await hosts.execute_tool(
            self._provider,
            "contain_host",
            {"device_id": device_id},
        )

    async def lift_containment(
        self,
        device_id: str,
    ) -> dict[str, Any]:
        """
        Remove network isolation from a host.

        Args:
            device_id: Device ID to lift containment from

        Returns:
            dict[str, Any]: Lift containment operation result

        Example:
            >>> result = await client.lift_containment(device_id="abc123")
        """
        self._ensure_initialized()
        return await hosts.execute_tool(
            self._provider,
            "lift_containment",
            {"device_id": device_id},
        )

    # Detection Management Methods

    async def query_detections(
        self,
        filter: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """
        Search for detections using FQL filters.

        Args:
            filter: FQL filter expression
            limit: Maximum number of results (1-5000)
            offset: Pagination offset
            sort: Sort field and direction

        Returns:
            dict[str, Any]: Query results with detection IDs

        Example:
            >>> detections = await client.query_detections(
            ...     filter="status:'new'",
            ...     limit=50
            ... )
        """
        self._ensure_initialized()
        arguments = {
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }
        return await detections.execute_tool(
            self._provider,
            "query_detections",
            arguments,
        )

    async def get_detection_details(
        self,
        detection_ids: list[str],
    ) -> dict[str, Any]:
        """
        Get detailed information about specific detections.

        Args:
            detection_ids: List of detection IDs to retrieve

        Returns:
            dict[str, Any]: Detection details

        Example:
            >>> details = await client.get_detection_details(
            ...     detection_ids=["ldt:abc123", "ldt:def456"]
            ... )
        """
        self._ensure_initialized()
        return await detections.execute_tool(
            self._provider,
            "get_detection_details",
            {"detection_ids": detection_ids},
        )

    async def update_detection_status(
        self,
        detection_ids: list[str],
        status: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        """
        Update the status of one or more detections.

        Args:
            detection_ids: List of detection IDs to update
            status: New status (new, in_progress, true_positive, false_positive, closed)
            comment: Optional comment explaining the status change

        Returns:
            dict[str, Any]: Update operation result

        Example:
            >>> result = await client.update_detection_status(
            ...     detection_ids=["ldt:abc123"],
            ...     status="false_positive",
            ...     comment="Benign activity"
            ... )
        """
        self._ensure_initialized()
        arguments = {
            "detection_ids": detection_ids,
            "status": status,
        }
        if comment:
            arguments["comment"] = comment

        return await detections.execute_tool(
            self._provider,
            "update_detection_status",
            arguments,
        )

    # Incident Management Methods

    async def query_incidents(
        self,
        filter: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """
        Search for incidents using FQL filters.

        Args:
            filter: FQL filter expression
            limit: Maximum number of results (1-500)
            offset: Pagination offset
            sort: Sort field and direction

        Returns:
            dict[str, Any]: Query results with incident IDs

        Example:
            >>> incidents = await client.query_incidents(
            ...     filter="status:'New'",
            ...     limit=25
            ... )
        """
        self._ensure_initialized()
        arguments = {
            "filter": filter,
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }
        return await incidents.execute_tool(
            self._provider,
            "query_incidents",
            arguments,
        )

    async def get_incident_details(
        self,
        incident_ids: list[str],
    ) -> dict[str, Any]:
        """
        Get detailed information about specific incidents.

        Args:
            incident_ids: List of incident IDs to retrieve

        Returns:
            dict[str, Any]: Incident details

        Example:
            >>> details = await client.get_incident_details(
            ...     incident_ids=["inc:abc123"]
            ... )
        """
        self._ensure_initialized()
        return await incidents.execute_tool(
            self._provider,
            "get_incident_details",
            {"incident_ids": incident_ids},
        )
