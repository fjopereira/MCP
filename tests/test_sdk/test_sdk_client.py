"""
Tests for CrowdStrike SDK client.

This module tests the SDK client functionality for programmatic usage.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_crowdstrike.sdk import CrowdStrikeClient


class TestSDKClient:
    """Tests for CrowdStrike SDK client."""

    @pytest.mark.asyncio
    async def test_client_initialization(self) -> None:
        """Test SDK client initialization."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        assert client._settings is not None
        assert not client._initialized

    @pytest.mark.asyncio
    async def test_client_context_manager(self) -> None:
        """Test SDK client as context manager."""
        with patch.object(
            CrowdStrikeClient,
            "initialize",
            new_callable=AsyncMock,
        ) as mock_init, patch.object(
            CrowdStrikeClient,
            "close",
            new_callable=AsyncMock,
        ) as mock_close:
            async with CrowdStrikeClient(
                client_id="test-id",
                client_secret="test-secret",
            ) as client:
                assert client is not None

            mock_init.assert_called_once()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_devices_by_filter(
        self,
        sample_device_data: dict,
    ) -> None:
        """Test query_devices_by_filter method."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        # Mock provider and tools
        with patch.object(
            client._provider,
            "initialize",
            new_callable=AsyncMock,
        ), patch(
            "mcp_crowdstrike.sdk.hosts.execute_tool",
            new_callable=AsyncMock,
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "data": {
                    "device_ids": sample_device_data["device_ids"],
                },
            }

            await client.initialize()
            result = await client.query_devices_by_filter(limit=10)

            assert result["success"] is True
            assert "device_ids" in result["data"]
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_device_details(
        self,
        sample_device_data: dict,
    ) -> None:
        """Test get_device_details method."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        with patch.object(
            client._provider,
            "initialize",
            new_callable=AsyncMock,
        ), patch(
            "mcp_crowdstrike.sdk.hosts.execute_tool",
            new_callable=AsyncMock,
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "data": {
                    "devices": sample_device_data["devices"],
                },
            }

            await client.initialize()
            result = await client.get_device_details(
                device_ids=sample_device_data["device_ids"][:2]
            )

            assert result["success"] is True
            assert "devices" in result["data"]

    @pytest.mark.asyncio
    async def test_contain_host(self) -> None:
        """Test contain_host method."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        with patch.object(
            client._provider,
            "initialize",
            new_callable=AsyncMock,
        ), patch(
            "mcp_crowdstrike.sdk.hosts.execute_tool",
            new_callable=AsyncMock,
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "data": {
                    "device_id": "device-id-1",
                    "action": "contained",
                },
            }

            await client.initialize()
            result = await client.contain_host(device_id="device-id-1")

            assert result["success"] is True
            assert result["data"]["action"] == "contained"

    @pytest.mark.asyncio
    async def test_lift_containment(self) -> None:
        """Test lift_containment method."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        with patch.object(
            client._provider,
            "initialize",
            new_callable=AsyncMock,
        ), patch(
            "mcp_crowdstrike.sdk.hosts.execute_tool",
            new_callable=AsyncMock,
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "data": {
                    "device_id": "device-id-1",
                    "action": "containment_lifted",
                },
            }

            await client.initialize()
            result = await client.lift_containment(device_id="device-id-1")

            assert result["success"] is True
            assert result["data"]["action"] == "containment_lifted"

    @pytest.mark.asyncio
    async def test_query_detections(
        self,
        sample_detection_data: dict,
    ) -> None:
        """Test query_detections method."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        with patch.object(
            client._provider,
            "initialize",
            new_callable=AsyncMock,
        ), patch(
            "mcp_crowdstrike.sdk.detections.execute_tool",
            new_callable=AsyncMock,
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "data": {
                    "detection_ids": sample_detection_data["detection_ids"],
                },
            }

            await client.initialize()
            result = await client.query_detections(limit=100)

            assert result["success"] is True
            assert "detection_ids" in result["data"]

    @pytest.mark.asyncio
    async def test_update_detection_status(self) -> None:
        """Test update_detection_status method."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        with patch.object(
            client._provider,
            "initialize",
            new_callable=AsyncMock,
        ), patch(
            "mcp_crowdstrike.sdk.detections.execute_tool",
            new_callable=AsyncMock,
        ) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "data": {
                    "updated_count": 1,
                    "status": "false_positive",
                },
            }

            await client.initialize()
            result = await client.update_detection_status(
                detection_ids=["ldt:test"],
                status="false_positive",
            )

            assert result["success"] is True
            assert result["data"]["status"] == "false_positive"

    @pytest.mark.asyncio
    async def test_client_not_initialized_error(self) -> None:
        """Test that methods raise error when client not initialized."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        with pytest.raises(RuntimeError, match="not initialized"):
            await client.query_devices_by_filter()

    @pytest.mark.asyncio
    async def test_client_close(self) -> None:
        """Test client cleanup."""
        client = CrowdStrikeClient(
            client_id="test-id",
            client_secret="test-secret",
        )

        with patch.object(
            client._provider,
            "initialize",
            new_callable=AsyncMock,
        ), patch.object(
            client._provider,
            "shutdown",
            new_callable=AsyncMock,
        ) as mock_shutdown:
            await client.initialize()
            assert client._initialized

            await client.close()
            assert not client._initialized
            mock_shutdown.assert_called_once()
