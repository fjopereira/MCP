"""
Tests for CrowdStrike Falcon API tools.

This module tests all CrowdStrike tool implementations including:
- Host management (query, get details, contain, lift containment)
- Detection management (query, get details, update status)
- Incident management (query, get details)
"""

from unittest.mock import MagicMock

import pytest

from mcp_crowdstrike.providers.crowdstrike import CrowdStrikeProvider
from mcp_crowdstrike.tools.crowdstrike import detections, hosts, incidents


# Host Management Tool Tests
class TestHostTools:
    """Tests for host management tools."""

    @pytest.mark.asyncio
    async def test_query_devices_by_filter_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_hosts_api: MagicMock,
        sample_device_data: dict,
    ) -> None:
        """Test successful device query."""
        arguments = {"limit": 10, "offset": 0}

        result = await hosts.execute_tool(
            mock_crowdstrike_provider,
            "query_devices_by_filter",
            arguments,
        )

        assert result["success"] is True
        assert "device_ids" in result["data"]
        assert len(result["data"]["device_ids"]) == len(sample_device_data["device_ids"])
        assert result["metadata"]["total"] == len(sample_device_data["device_ids"])
        mock_hosts_api.query_devices_by_filter.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_devices_by_filter_with_filter(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_hosts_api: MagicMock,
    ) -> None:
        """Test device query with FQL filter."""
        arguments = {
            "filter": "platform_name:'Windows'",
            "limit": 5,
            "sort": "hostname.asc",
        }

        result = await hosts.execute_tool(
            mock_crowdstrike_provider,
            "query_devices_by_filter",
            arguments,
        )

        assert result["success"] is True
        mock_hosts_api.query_devices_by_filter.assert_called_with(
            filter="platform_name:'Windows'",
            limit=5,
            offset=0,
            sort="hostname.asc",
        )

    @pytest.mark.asyncio
    async def test_query_devices_api_error(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_hosts_api: MagicMock,
    ) -> None:
        """Test device query with API error."""
        mock_hosts_api.query_devices_by_filter.return_value = {
            "status_code": 500,
            "body": {"errors": ["Internal server error"]},
        }

        result = await hosts.execute_tool(
            mock_crowdstrike_provider,
            "query_devices_by_filter",
            {"limit": 10},
        )

        assert result["success"] is False
        assert result["status_code"] == 500

    @pytest.mark.asyncio
    async def test_get_device_details_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_hosts_api: MagicMock,
        sample_device_data: dict,
    ) -> None:
        """Test successful device details retrieval."""
        device_ids = sample_device_data["device_ids"][:2]
        arguments = {"device_ids": device_ids}

        result = await hosts.execute_tool(
            mock_crowdstrike_provider,
            "get_device_details",
            arguments,
        )

        assert result["success"] is True
        assert "devices" in result["data"]
        assert len(result["data"]["devices"]) == len(sample_device_data["devices"])
        mock_hosts_api.get_device_details.assert_called_once_with(ids=device_ids)

    @pytest.mark.asyncio
    async def test_get_device_details_missing_ids(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
    ) -> None:
        """Test device details with missing device IDs."""
        result = await hosts.execute_tool(
            mock_crowdstrike_provider,
            "get_device_details",
            {"device_ids": []},
        )

        assert result["success"] is False
        assert "device_ids" in str(result["error"]).lower()

    @pytest.mark.asyncio
    async def test_contain_host_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_hosts_api: MagicMock,
    ) -> None:
        """Test successful host containment."""
        device_id = "device-id-1"
        arguments = {"device_id": device_id}

        result = await hosts.execute_tool(
            mock_crowdstrike_provider,
            "contain_host",
            arguments,
        )

        assert result["success"] is True
        assert result["data"]["device_id"] == device_id
        assert result["data"]["action"] == "contained"
        mock_hosts_api.perform_action.assert_called_once_with(
            action_name="contain",
            ids=[device_id],
        )

    @pytest.mark.asyncio
    async def test_contain_host_missing_id(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
    ) -> None:
        """Test host containment with missing device ID."""
        result = await hosts.execute_tool(
            mock_crowdstrike_provider,
            "contain_host",
            {},
        )

        assert result["success"] is False
        assert "device_id" in str(result["error"]).lower()

    @pytest.mark.asyncio
    async def test_lift_containment_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_hosts_api: MagicMock,
    ) -> None:
        """Test successful containment lift."""
        device_id = "device-id-1"
        arguments = {"device_id": device_id}

        result = await hosts.execute_tool(
            mock_crowdstrike_provider,
            "lift_containment",
            arguments,
        )

        assert result["success"] is True
        assert result["data"]["device_id"] == device_id
        assert result["data"]["action"] == "containment_lifted"
        mock_hosts_api.perform_action.assert_called_once_with(
            action_name="lift_containment",
            ids=[device_id],
        )


# Detection Management Tool Tests
class TestDetectionTools:
    """Tests for detection management tools."""

    @pytest.mark.asyncio
    async def test_query_detections_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_detects_api: MagicMock,
        sample_detection_data: dict,
    ) -> None:
        """Test successful detection query."""
        arguments = {"limit": 100, "offset": 0}

        result = await detections.execute_tool(
            mock_crowdstrike_provider,
            "query_detections",
            arguments,
        )

        assert result["success"] is True
        assert "detection_ids" in result["data"]
        assert len(result["data"]["detection_ids"]) == len(
            sample_detection_data["detection_ids"]
        )
        mock_detects_api.query_detects.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_detection_details_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_detects_api: MagicMock,
        sample_detection_data: dict,
    ) -> None:
        """Test successful detection details retrieval."""
        detection_ids = sample_detection_data["detection_ids"]
        arguments = {"detection_ids": detection_ids}

        result = await detections.execute_tool(
            mock_crowdstrike_provider,
            "get_detection_details",
            arguments,
        )

        assert result["success"] is True
        assert "detections" in result["data"]
        assert len(result["data"]["detections"]) == len(
            sample_detection_data["detections"]
        )
        mock_detects_api.get_detect_summaries.assert_called_once_with(
            ids=detection_ids
        )

    @pytest.mark.asyncio
    async def test_update_detection_status_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_detects_api: MagicMock,
    ) -> None:
        """Test successful detection status update."""
        detection_ids = ["ldt:detection-id-1"]
        arguments = {
            "detection_ids": detection_ids,
            "status": "false_positive",
            "comment": "Test comment",
        }

        result = await detections.execute_tool(
            mock_crowdstrike_provider,
            "update_detection_status",
            arguments,
        )

        assert result["success"] is True
        assert result["data"]["updated_count"] == len(detection_ids)
        assert result["data"]["status"] == "false_positive"
        mock_detects_api.update_detects_by_ids.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_detection_status_invalid_status(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
    ) -> None:
        """Test detection update with invalid status."""
        arguments = {
            "detection_ids": ["ldt:detection-id-1"],
            "status": "invalid_status",
        }

        result = await detections.execute_tool(
            mock_crowdstrike_provider,
            "update_detection_status",
            arguments,
        )

        assert result["success"] is False
        assert "status" in str(result["error"]).lower()

    @pytest.mark.asyncio
    async def test_update_detection_status_missing_ids(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
    ) -> None:
        """Test detection update with missing IDs."""
        arguments = {
            "detection_ids": [],
            "status": "new",
        }

        result = await detections.execute_tool(
            mock_crowdstrike_provider,
            "update_detection_status",
            arguments,
        )

        assert result["success"] is False


# Incident Management Tool Tests
class TestIncidentTools:
    """Tests for incident management tools."""

    @pytest.mark.asyncio
    async def test_query_incidents_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_incidents_api: MagicMock,
        sample_incident_data: dict,
    ) -> None:
        """Test successful incident query."""
        arguments = {"limit": 100, "offset": 0}

        result = await incidents.execute_tool(
            mock_crowdstrike_provider,
            "query_incidents",
            arguments,
        )

        assert result["success"] is True
        assert "incident_ids" in result["data"]
        assert len(result["data"]["incident_ids"]) == len(
            sample_incident_data["incident_ids"]
        )
        mock_incidents_api.query_incidents.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_incidents_with_filter(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_incidents_api: MagicMock,
    ) -> None:
        """Test incident query with filter."""
        arguments = {
            "filter": "status:'New'",
            "limit": 50,
            "sort": "start.desc",
        }

        result = await incidents.execute_tool(
            mock_crowdstrike_provider,
            "query_incidents",
            arguments,
        )

        assert result["success"] is True
        mock_incidents_api.query_incidents.assert_called_with(
            filter="status:'New'",
            limit=50,
            offset=0,
            sort="start.desc",
        )

    @pytest.mark.asyncio
    async def test_get_incident_details_success(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
        mock_incidents_api: MagicMock,
        sample_incident_data: dict,
    ) -> None:
        """Test successful incident details retrieval."""
        incident_ids = sample_incident_data["incident_ids"]
        arguments = {"incident_ids": incident_ids}

        result = await incidents.execute_tool(
            mock_crowdstrike_provider,
            "get_incident_details",
            arguments,
        )

        assert result["success"] is True
        assert "incidents" in result["data"]
        assert len(result["data"]["incidents"]) == len(
            sample_incident_data["incidents"]
        )
        mock_incidents_api.get_incidents.assert_called_once_with(ids=incident_ids)

    @pytest.mark.asyncio
    async def test_get_incident_details_missing_ids(
        self,
        mock_crowdstrike_provider: CrowdStrikeProvider,
    ) -> None:
        """Test incident details with missing IDs."""
        result = await incidents.execute_tool(
            mock_crowdstrike_provider,
            "get_incident_details",
            {"incident_ids": []},
        )

        assert result["success"] is False
        assert "incident_ids" in str(result["error"]).lower()


# Tool Registry Tests
class TestToolRegistration:
    """Tests for tool registration and discovery."""

    def test_hosts_get_tools(self) -> None:
        """Test hosts module tool registration."""
        tools = hosts.get_tools()
        assert len(tools) == 4
        tool_names = [t.name for t in tools]
        assert "query_devices_by_filter" in tool_names
        assert "get_device_details" in tool_names
        assert "contain_host" in tool_names
        assert "lift_containment" in tool_names

    def test_detections_get_tools(self) -> None:
        """Test detections module tool registration."""
        tools = detections.get_tools()
        assert len(tools) == 3
        tool_names = [t.name for t in tools]
        assert "query_detections" in tool_names
        assert "get_detection_details" in tool_names
        assert "update_detection_status" in tool_names

    def test_incidents_get_tools(self) -> None:
        """Test incidents module tool registration."""
        tools = incidents.get_tools()
        assert len(tools) == 2
        tool_names = [t.name for t in tools]
        assert "query_incidents" in tool_names
        assert "get_incident_details" in tool_names
