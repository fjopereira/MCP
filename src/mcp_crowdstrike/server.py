"""
MCP Server implementation for CrowdStrike Falcon.

This module implements the Model Context Protocol (MCP) server interface,
providing standardized access to CrowdStrike Falcon API tools.
"""

from typing import Any

from mcp.server import Server
from mcp.types import Tool as MCPTool, TextContent

from mcp_crowdstrike.config import Settings
from mcp_crowdstrike.providers.crowdstrike import CrowdStrikeProvider
from mcp_crowdstrike.tools.crowdstrike import detections, hosts, incidents
from mcp_crowdstrike.tools.registry import ToolRegistry
from mcp_crowdstrike.utils.logging import get_logger

logger = get_logger(__name__)


class MCPServer:
    """
    MCP Server for CrowdStrike Falcon API.

    This server exposes CrowdStrike Falcon API operations as MCP tools,
    enabling seamless integration with MCP-compatible clients.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the MCP server.

        Args:
            settings: Application settings
        """
        self._settings = settings
        self._provider = CrowdStrikeProvider(settings)
        self._registry: ToolRegistry | None = None
        self._server = Server("mcp-crowdstrike")

        logger.info("MCP Server initialized")

    async def initialize(self) -> None:
        """
        Initialize the server and register all tools.

        Raises:
            ConnectionError: If unable to connect to CrowdStrike API
        """
        logger.info("Initializing MCP server")

        # Initialize CrowdStrike provider
        await self._provider.initialize()

        # Create tool registry
        self._registry = ToolRegistry(self._provider)

        # Register all tool modules
        logger.info("Registering tools")

        self._registry.register_module(
            hosts.get_tools,
            hosts.execute_tool,
        )

        self._registry.register_module(
            detections.get_tools,
            detections.execute_tool,
        )

        self._registry.register_module(
            incidents.get_tools,
            incidents.execute_tool,
        )

        tool_count = len(self._registry.list_tool_names())
        logger.info(
            "MCP server initialization complete",
            extra={"tool_count": tool_count},
        )

    async def shutdown(self) -> None:
        """
        Cleanup server resources.
        """
        logger.info("Shutting down MCP server")
        await self._provider.shutdown()
        logger.info("MCP server shutdown complete")

    def get_tools(self) -> list[dict[str, Any]]:
        """
        Get all available tools in MCP format.

        Returns:
            list[dict[str, Any]]: List of tool definitions

        Raises:
            RuntimeError: If server is not initialized
        """
        if self._registry is None:
            raise RuntimeError("Server not initialized. Call initialize() first.")

        return self._registry.get_all_tools()

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a tool by name with provided arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            dict[str, Any]: Tool execution result

        Raises:
            RuntimeError: If server is not initialized
        """
        if self._registry is None:
            raise RuntimeError("Server not initialized. Call initialize() first.")

        return await self._registry.execute_tool(tool_name, arguments)

    def get_mcp_server(self) -> Server:
        """
        Get the underlying MCP Server instance.

        Returns:
            Server: MCP Server instance
        """
        return self._server

    def setup_handlers(self) -> None:
        """
        Set up MCP protocol handlers.

        This configures the server to handle MCP protocol requests.
        """
        server = self._server

        @server.list_tools()
        async def handle_list_tools() -> list[MCPTool]:
            """Handle MCP list_tools request."""
            if self._registry is None:
                return []

            tools = self._registry.get_all_tools()
            mcp_tools = []

            for tool in tools:
                mcp_tools.append(
                    MCPTool(
                        name=tool["name"],
                        description=tool["description"],
                        inputSchema=tool["inputSchema"],
                    )
                )

            return mcp_tools

        @server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: dict[str, Any],
        ) -> list[TextContent]:
            """Handle MCP call_tool request."""
            if self._registry is None:
                return [
                    TextContent(
                        type="text",
                        text="Server not initialized",
                    )
                ]

            result = await self._registry.execute_tool(name, arguments)

            # Convert result to MCP TextContent format
            import json
            result_text = json.dumps(result, indent=2)

            return [
                TextContent(
                    type="text",
                    text=result_text,
                )
            ]

        logger.info("MCP protocol handlers configured")


async def create_server(settings: Settings | None = None) -> MCPServer:
    """
    Create and initialize an MCP server instance.

    Args:
        settings: Optional application settings. If None, will load from environment.

    Returns:
        MCPServer: Initialized MCP server

    Raises:
        ConnectionError: If unable to connect to CrowdStrike API
    """
    if settings is None:
        from mcp_crowdstrike.config import get_settings
        settings = get_settings()

    server = MCPServer(settings)
    server.setup_handlers()
    await server.initialize()

    return server
