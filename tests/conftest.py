"""
Shared pytest fixtures for MCP CrowdStrike tests.

This module provides reusable fixtures for testing, including:
- Mock settings and configuration
- Mock CrowdStrike provider
- Sample test data
- Test clients
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from mcp_crowdstrike.config import Settings
from mcp_crowdstrike.providers.crowdstrike import CrowdStrikeProvider


@pytest.fixture
def test_settings() -> Settings:
    """
    Create test settings with mock credentials.

    Returns:
        Settings: Test configuration
    """
    return Settings(
        falcon_client_id=SecretStr("test-client-id"),
        falcon_client_secret=SecretStr("test-client-secret"),
        falcon_base_url="https://api.crowdstrike.com",
        server_host="127.0.0.1",
        server_port=8001,
        log_level="DEBUG",
        environment="development",
    )


@pytest.fixture
def mock_crowdstrike_provider(test_settings: Settings) -> CrowdStrikeProvider:
    """
    Create a mock CrowdStrike provider for testing.

    Args:
        test_settings: Test settings fixture

    Returns:
        CrowdStrikeProvider: Mocked provider
    """
    provider = CrowdStrikeProvider(test_settings)

    # Mock OAuth2 client
    provider._oauth2 = MagicMock()
    provider._oauth2.token.return_value = {
        "status_code": 201,
        "body": {
            "access_token": "mock-access-token",
            "expires_in": 1800,
        },
    }

    # Mock service collections
    provider._hosts = MagicMock()
    provider._detects = MagicMock()
    provider._incidents = MagicMock()
    provider._initialized = True

    return provider


@pytest.fixture
def sample_device_data() -> dict:
    """
    Create sample device data for testing.

    Returns:
        dict: Sample device response data
    """
    return {
        "device_ids": [
            "device-id-1",
            "device-id-2",
            "device-id-3",
        ],
        "devices": [
            {
                "device_id": "device-id-1",
                "hostname": "WIN-SERVER-01",
                "platform_name": "Windows",
                "os_version": "Windows Server 2019",
                "local_ip": "192.168.1.100",
                "external_ip": "203.0.113.100",
                "status": "normal",
                "last_seen": "2024-01-15T10:30:00Z",
                "first_seen": "2024-01-01T08:00:00Z",
                "agent_version": "7.10.0",
            },
            {
                "device_id": "device-id-2",
                "hostname": "LINUX-WEB-01",
                "platform_name": "Linux",
                "os_version": "Ubuntu 22.04",
                "local_ip": "192.168.1.101",
                "external_ip": "203.0.113.101",
                "status": "normal",
                "last_seen": "2024-01-15T10:25:00Z",
                "first_seen": "2024-01-01T09:00:00Z",
                "agent_version": "7.10.0",
            },
            {
                "device_id": "device-id-3",
                "hostname": "MAC-LAPTOP-01",
                "platform_name": "Mac",
                "os_version": "macOS 14.0",
                "local_ip": "192.168.1.102",
                "status": "contained",
                "last_seen": "2024-01-15T10:20:00Z",
                "first_seen": "2024-01-05T14:00:00Z",
                "agent_version": "7.09.0",
            },
        ],
    }


@pytest.fixture
def sample_detection_data() -> dict:
    """
    Create sample detection data for testing.

    Returns:
        dict: Sample detection response data
    """
    return {
        "detection_ids": [
            "ldt:detection-id-1",
            "ldt:detection-id-2",
        ],
        "detections": [
            {
                "detection_id": "ldt:detection-id-1",
                "status": "new",
                "severity": "high",
                "tactic": "Initial Access",
                "technique": "Phishing",
                "device": {
                    "device_id": "device-id-1",
                    "hostname": "WIN-SERVER-01",
                },
                "created_timestamp": "2024-01-15T09:00:00Z",
                "first_behavior": "2024-01-15T08:55:00Z",
                "last_behavior": "2024-01-15T09:00:00Z",
            },
            {
                "detection_id": "ldt:detection-id-2",
                "status": "in_progress",
                "severity": "medium",
                "tactic": "Execution",
                "technique": "PowerShell",
                "device": {
                    "device_id": "device-id-2",
                    "hostname": "LINUX-WEB-01",
                },
                "created_timestamp": "2024-01-15T10:00:00Z",
                "first_behavior": "2024-01-15T09:55:00Z",
                "last_behavior": "2024-01-15T10:00:00Z",
            },
        ],
    }


@pytest.fixture
def sample_incident_data() -> dict:
    """
    Create sample incident data for testing.

    Returns:
        dict: Sample incident response data
    """
    return {
        "incident_ids": [
            "inc:incident-id-1",
            "inc:incident-id-2",
        ],
        "incidents": [
            {
                "incident_id": "inc:incident-id-1",
                "status": "New",
                "state": "open",
                "name": "Suspicious Activity on WIN-SERVER-01",
                "description": "Multiple detections indicating potential compromise",
                "hosts": ["device-id-1"],
                "detections": ["ldt:detection-id-1"],
                "start": "2024-01-15T08:55:00Z",
                "end": "2024-01-15T09:00:00Z",
                "tactics": ["Initial Access", "Execution"],
                "techniques": ["Phishing", "PowerShell"],
            },
            {
                "incident_id": "inc:incident-id-2",
                "status": "In Progress",
                "state": "open",
                "name": "Malware Detected on Multiple Hosts",
                "description": "Widespread malware infection detected",
                "hosts": ["device-id-1", "device-id-2"],
                "detections": ["ldt:detection-id-1", "ldt:detection-id-2"],
                "start": "2024-01-15T09:00:00Z",
                "end": "2024-01-15T10:00:00Z",
                "tactics": ["Initial Access", "Persistence"],
                "techniques": ["Phishing", "Registry Run Keys"],
            },
        ],
    }


@pytest.fixture
def mock_hosts_api(
    mock_crowdstrike_provider: CrowdStrikeProvider,
    sample_device_data: dict,
) -> MagicMock:
    """
    Configure mock Hosts API responses.

    Args:
        mock_crowdstrike_provider: Mock provider fixture
        sample_device_data: Sample device data

    Returns:
        MagicMock: Configured mock Hosts API
    """
    hosts_api = mock_crowdstrike_provider._hosts

    # Mock query_devices_by_filter
    hosts_api.query_devices_by_filter.return_value = {
        "status_code": 200,
        "body": {
            "resources": sample_device_data["device_ids"],
            "meta": {
                "pagination": {
                    "total": len(sample_device_data["device_ids"]),
                },
            },
        },
    }

    # Mock get_device_details
    hosts_api.get_device_details.return_value = {
        "status_code": 200,
        "body": {
            "resources": sample_device_data["devices"],
        },
    }

    # Mock perform_action (contain/lift_containment)
    hosts_api.perform_action.return_value = {
        "status_code": 202,
        "body": {
            "resources": [{"id": "device-id-1"}],
        },
    }

    return hosts_api


@pytest.fixture
def mock_detects_api(
    mock_crowdstrike_provider: CrowdStrikeProvider,
    sample_detection_data: dict,
) -> MagicMock:
    """
    Configure mock Detections API responses.

    Args:
        mock_crowdstrike_provider: Mock provider fixture
        sample_detection_data: Sample detection data

    Returns:
        MagicMock: Configured mock Detections API
    """
    detects_api = mock_crowdstrike_provider._detects

    # Mock query_detects
    detects_api.query_detects.return_value = {
        "status_code": 200,
        "body": {
            "resources": sample_detection_data["detection_ids"],
            "meta": {
                "pagination": {
                    "total": len(sample_detection_data["detection_ids"]),
                },
            },
        },
    }

    # Mock get_detect_summaries
    detects_api.get_detect_summaries.return_value = {
        "status_code": 200,
        "body": {
            "resources": sample_detection_data["detections"],
        },
    }

    # Mock update_detects_by_ids
    detects_api.update_detects_by_ids.return_value = {
        "status_code": 200,
        "body": {
            "resources": sample_detection_data["detection_ids"],
        },
    }

    return detects_api


@pytest.fixture
def mock_incidents_api(
    mock_crowdstrike_provider: CrowdStrikeProvider,
    sample_incident_data: dict,
) -> MagicMock:
    """
    Configure mock Incidents API responses.

    Args:
        mock_crowdstrike_provider: Mock provider fixture
        sample_incident_data: Sample incident data

    Returns:
        MagicMock: Configured mock Incidents API
    """
    incidents_api = mock_crowdstrike_provider._incidents

    # Mock query_incidents
    incidents_api.query_incidents.return_value = {
        "status_code": 200,
        "body": {
            "resources": sample_incident_data["incident_ids"],
            "meta": {
                "pagination": {
                    "total": len(sample_incident_data["incident_ids"]),
                },
            },
        },
    }

    # Mock get_incidents
    incidents_api.get_incidents.return_value = {
        "status_code": 200,
        "body": {
            "resources": sample_incident_data["incidents"],
        },
    }

    return incidents_api


@pytest.fixture
def async_test_client(test_settings: Settings) -> TestClient:
    """
    Create a FastAPI test client for integration tests.

    Args:
        test_settings: Test settings fixture

    Returns:
        TestClient: FastAPI test client
    """
    # Import here to avoid circular imports
    from mcp_crowdstrike.main import app

    return TestClient(app)
