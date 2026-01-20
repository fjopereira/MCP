"""
Mock CrowdStrike Provider for testing without real credentials.

This provider simulates CrowdStrike Falcon API responses with realistic data,
allowing users to test the SDK functionality without requiring actual API credentials.
"""

from typing import Any

from mcp_crowdstrike.providers.base import BaseProvider
from mcp_crowdstrike.utils.logging import get_logger

logger = get_logger(__name__)


class MockCrowdStrikeProvider(BaseProvider):
    """
    Mock CrowdStrike provider for testing without credentials.

    This provider returns simulated data that matches the real CrowdStrike API
    response format, enabling testing and demonstration without API access.
    """

    def __init__(self) -> None:
        """Initialize the mock provider."""
        self._initialized = False
        self._call_count = 0

        # Sample data
        self._sample_devices = [
            {
                "device_id": "mock-device-001",
                "hostname": "WIN-SERVER-DEMO-01",
                "platform_name": "Windows",
                "os_version": "Windows Server 2019",
                "local_ip": "192.168.1.100",
                "external_ip": "203.0.113.100",
                "status": "normal",
                "last_seen": "2024-01-19T10:30:00Z",
                "first_seen": "2024-01-01T08:00:00Z",
                "agent_version": "7.10.0",
            },
            {
                "device_id": "mock-device-002",
                "hostname": "LINUX-WEB-DEMO-01",
                "platform_name": "Linux",
                "os_version": "Ubuntu 22.04",
                "local_ip": "192.168.1.101",
                "external_ip": "203.0.113.101",
                "status": "normal",
                "last_seen": "2024-01-19T10:25:00Z",
                "first_seen": "2024-01-01T09:00:00Z",
                "agent_version": "7.10.0",
            },
            {
                "device_id": "mock-device-003",
                "hostname": "MAC-LAPTOP-DEMO-01",
                "platform_name": "Mac",
                "os_version": "macOS 14.0",
                "local_ip": "192.168.1.102",
                "status": "normal",
                "last_seen": "2024-01-19T10:20:00Z",
                "first_seen": "2024-01-05T14:00:00Z",
                "agent_version": "7.09.0",
            },
        ]

        self._sample_detections = [
            {
                "detection_id": "ldt:mock-detection-001",
                "status": "new",
                "severity": "high",
                "tactic": "Initial Access",
                "technique": "Phishing",
                "device": {
                    "device_id": "mock-device-001",
                    "hostname": "WIN-SERVER-DEMO-01",
                },
                "created_timestamp": "2024-01-19T09:00:00Z",
                "first_behavior": "2024-01-19T08:55:00Z",
                "last_behavior": "2024-01-19T09:00:00Z",
            },
            {
                "detection_id": "ldt:mock-detection-002",
                "status": "in_progress",
                "severity": "medium",
                "tactic": "Execution",
                "technique": "PowerShell",
                "device": {
                    "device_id": "mock-device-002",
                    "hostname": "LINUX-WEB-DEMO-01",
                },
                "created_timestamp": "2024-01-19T10:00:00Z",
                "first_behavior": "2024-01-19T09:55:00Z",
                "last_behavior": "2024-01-19T10:00:00Z",
            },
        ]

        self._sample_incidents = [
            {
                "incident_id": "inc:mock-incident-001",
                "status": "New",
                "state": "open",
                "name": "Suspicious Activity on WIN-SERVER-DEMO-01",
                "description": "Multiple detections indicating potential compromise",
                "hosts": ["mock-device-001"],
                "detections": ["ldt:mock-detection-001"],
                "start": "2024-01-19T08:55:00Z",
                "end": "2024-01-19T09:00:00Z",
                "tactics": ["Initial Access", "Execution"],
                "techniques": ["Phishing", "PowerShell"],
            }
        ]

        logger.info("Mock CrowdStrike provider created (NO REAL CREDENTIALS NEEDED)")

    async def initialize(self) -> None:
        """Initialize the mock provider."""
        logger.info("Initializing Mock CrowdStrike provider (simulated connection)")
        self._initialized = True
        logger.info("Mock provider initialized - using simulated data")

    async def shutdown(self) -> None:
        """Cleanup mock provider resources."""
        logger.info("Shutting down Mock CrowdStrike provider")
        self._initialized = False

    def get_client(self) -> dict[str, Any]:
        """
        Get the mock service collections.

        Returns:
            dict[str, Any]: Dictionary containing mock service collections
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized. Call initialize() first.")

        return {
            "hosts": self,
            "detects": self,
            "incidents": self,
        }

    async def health_check(self) -> bool:
        """
        Perform a mock health check.

        Returns:
            bool: Always returns True for mock provider
        """
        if not self._initialized:
            return False

        logger.info("Mock health check - always healthy (simulated)")
        return True

    @property
    def hosts(self) -> "MockCrowdStrikeProvider":
        """Get the mock Hosts API."""
        if not self._initialized:
            raise RuntimeError("Provider not initialized")
        return self

    @property
    def detects(self) -> "MockCrowdStrikeProvider":
        """Get the mock Detections API."""
        if not self._initialized:
            raise RuntimeError("Provider not initialized")
        return self

    @property
    def incidents(self) -> "MockCrowdStrikeProvider":
        """Get the mock Incidents API."""
        if not self._initialized:
            raise RuntimeError("Provider not initialized")
        return self

    async def refresh_token_if_needed(self) -> None:
        """Mock token refresh (no-op)."""
        logger.debug("Mock token refresh (no-op)")

    # Mock Hosts API methods

    def query_devices_by_filter(self, **kwargs: Any) -> dict[str, Any]:
        """Mock query devices by filter."""
        self._call_count += 1
        logger.info(
            "Mock query_devices_by_filter called",
            extra={"call_count": self._call_count, "params": kwargs},
        )

        limit = kwargs.get("limit", 100)
        offset = kwargs.get("offset", 0)

        device_ids = [d["device_id"] for d in self._sample_devices]
        paginated_ids = device_ids[offset : offset + limit]

        return {
            "status_code": 200,
            "body": {
                "resources": paginated_ids,
                "meta": {
                    "pagination": {
                        "total": len(device_ids),
                    },
                },
            },
        }

    def get_device_details(self, **kwargs: Any) -> dict[str, Any]:
        """Mock get device details."""
        self._call_count += 1
        logger.info(
            "Mock get_device_details called",
            extra={"call_count": self._call_count, "params": kwargs},
        )

        requested_ids = kwargs.get("ids", [])
        devices = [
            d for d in self._sample_devices if d["device_id"] in requested_ids
        ]

        return {
            "status_code": 200,
            "body": {
                "resources": devices,
            },
        }

    def perform_action(self, **kwargs: Any) -> dict[str, Any]:
        """Mock perform action (contain/lift_containment)."""
        self._call_count += 1
        action_name = kwargs.get("action_name", "unknown")
        device_ids = kwargs.get("ids", [])

        logger.warning(
            f"Mock {action_name} action called (SIMULATED - no real action taken)",
            extra={"call_count": self._call_count, "device_ids": device_ids},
        )

        return {
            "status_code": 202,
            "body": {
                "resources": [{"id": did} for did in device_ids],
            },
        }

    # Mock Detections API methods

    def query_detects(self, **kwargs: Any) -> dict[str, Any]:
        """Mock query detections."""
        self._call_count += 1
        logger.info(
            "Mock query_detects called",
            extra={"call_count": self._call_count, "params": kwargs},
        )

        limit = kwargs.get("limit", 100)
        offset = kwargs.get("offset", 0)

        detection_ids = [d["detection_id"] for d in self._sample_detections]
        paginated_ids = detection_ids[offset : offset + limit]

        return {
            "status_code": 200,
            "body": {
                "resources": paginated_ids,
                "meta": {
                    "pagination": {
                        "total": len(detection_ids),
                    },
                },
            },
        }

    def get_detect_summaries(self, **kwargs: Any) -> dict[str, Any]:
        """Mock get detection summaries."""
        self._call_count += 1
        logger.info(
            "Mock get_detect_summaries called",
            extra={"call_count": self._call_count, "params": kwargs},
        )

        requested_ids = kwargs.get("ids", [])
        detections = [
            d for d in self._sample_detections if d["detection_id"] in requested_ids
        ]

        return {
            "status_code": 200,
            "body": {
                "resources": detections,
            },
        }

    def update_detects_by_ids(self, **kwargs: Any) -> dict[str, Any]:
        """Mock update detections."""
        self._call_count += 1
        logger.info(
            "Mock update_detects_by_ids called (SIMULATED)",
            extra={"call_count": self._call_count, "params": kwargs},
        )

        detection_ids = kwargs.get("ids", [])

        return {
            "status_code": 200,
            "body": {
                "resources": detection_ids,
            },
        }

    # Mock Incidents API methods

    def query_incidents(self, **kwargs: Any) -> dict[str, Any]:
        """Mock query incidents."""
        self._call_count += 1
        logger.info(
            "Mock query_incidents called",
            extra={"call_count": self._call_count, "params": kwargs},
        )

        limit = kwargs.get("limit", 100)
        offset = kwargs.get("offset", 0)

        incident_ids = [i["incident_id"] for i in self._sample_incidents]
        paginated_ids = incident_ids[offset : offset + limit]

        return {
            "status_code": 200,
            "body": {
                "resources": paginated_ids,
                "meta": {
                    "pagination": {
                        "total": len(incident_ids),
                    },
                },
            },
        }

    def get_incidents(self, **kwargs: Any) -> dict[str, Any]:
        """Mock get incidents."""
        self._call_count += 1
        logger.info(
            "Mock get_incidents called",
            extra={"call_count": self._call_count, "params": kwargs},
        )

        requested_ids = kwargs.get("ids", [])
        incidents = [
            i for i in self._sample_incidents if i["incident_id"] in requested_ids
        ]

        return {
            "status_code": 200,
            "body": {
                "resources": incidents,
            },
        }
