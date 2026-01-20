"""
Integration tests for MCP CrowdStrike API endpoints.

This module tests the FastAPI application endpoints end-to-end.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_app() -> TestClient:
    """Create a test client with mocked provider."""
    with patch(
        "mcp_crowdstrike.main.create_server",
        new_callable=AsyncMock,
    ) as mock_create:
        # Create a mock server
        from mcp_crowdstrike.server import MCPServer
        from mcp_crowdstrike.config import Settings
        from pydantic import SecretStr

        settings = Settings(
            falcon_client_id=SecretStr("test-id"),
            falcon_client_secret=SecretStr("test-secret"),
        )

        mock_server = AsyncMock(spec=MCPServer)
        mock_server.get_tools.return_value = [
            {
                "name": "test_tool",
                "description": "Test tool",
                "inputSchema": {"type": "object"},
            }
        ]
        mock_server.execute_tool.return_value = {
            "success": True,
            "data": {"result": "test"},
        }
        mock_server._provider = AsyncMock()
        mock_server._provider.health_check.return_value = True

        mock_create.return_value = mock_server

        from mcp_crowdstrike.main import app

        return TestClient(app)


def test_root_endpoint(test_app: TestClient) -> None:
    """Test root endpoint."""
    response = test_app.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "MCP CrowdStrike"
    assert "endpoints" in data


def test_health_check(test_app: TestClient) -> None:
    """Test health check endpoint."""
    response = test_app.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data


def test_readiness_check(test_app: TestClient) -> None:
    """Test readiness check endpoint."""
    response = test_app.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "provider_healthy" in data


def test_list_tools(test_app: TestClient) -> None:
    """Test list tools endpoint."""
    response = test_app.get("/mcp/v1/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "count" in data
    assert isinstance(data["tools"], list)


def test_execute_tool(test_app: TestClient) -> None:
    """Test tool execution endpoint."""
    response = test_app.post(
        "/mcp/v1/tools/test_tool",
        json={"arguments": {"param": "value"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_execute_tool_missing_body(test_app: TestClient) -> None:
    """Test tool execution with missing request body."""
    response = test_app.post("/mcp/v1/tools/test_tool")
    # Should handle missing body gracefully
    assert response.status_code in [200, 422]  # 422 for validation error
