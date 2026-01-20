"""
Tool registry for discovering and executing MCP tools.

This module provides a central registry for all available tools,
handles tool discovery, and routes tool execution to the appropriate handlers.
"""

from typing import Any, Callable

from mcp_crowdstrike.providers.crowdstrike import CrowdStrikeProvider
from mcp_crowdstrike.utils.logging import get_logger
from mcp_crowdstrike.utils.responses import error_response

logger = get_logger(__name__)


class Tool:
    """
    Represents an MCP tool with its schema and handler.

    Attributes:
        name: Tool name
        description: Tool description
        input_schema: JSON Schema for tool parameters
        handler: Async function to execute the tool
    """

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        """
        Initialize a tool.

        Args:
            name: Tool name (must be unique)
            description: Human-readable description
            input_schema: JSON Schema defining input parameters
            handler: Async function that executes the tool
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler

    def to_mcp_format(self) -> dict[str, Any]:
        """
        Convert tool to MCP protocol format.

        Returns:
            dict[str, Any]: Tool definition in MCP format
        """
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


class ToolRegistry:
    """
    Central registry for all MCP tools.

    The registry manages tool discovery, registration, and execution routing.
    It automatically discovers tools from registered modules.
    """

    def __init__(self, provider: CrowdStrikeProvider) -> None:
        """
        Initialize the tool registry.

        Args:
            provider: CrowdStrike provider instance for API access
        """
        self._provider = provider
        self._tools: dict[str, Tool] = {}
        logger.info("Tool registry initialized")

    def register_tool(self, tool: Tool) -> None:
        """
        Register a single tool.

        Args:
            tool: Tool instance to register

        Raises:
            ValueError: If a tool with the same name already exists
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool
        logger.info("Tool registered", extra={"tool_name": tool.name})

    def register_module(
        self,
        get_tools_func: Callable[[], list[Tool]],
        execute_func: Callable[..., Any],
    ) -> None:
        """
        Register all tools from a module.

        Args:
            get_tools_func: Function that returns list of tools
            execute_func: Function that executes tools from this module
        """
        tools = get_tools_func()
        for tool in tools:
            # Wrap the execute function with the module's handler
            tool.handler = lambda name, args, func=execute_func: func(
                self._provider, name, args
            )
            self.register_tool(tool)

        logger.info(
            "Module registered",
            extra={"tool_count": len(tools)},
        )

    def get_all_tools(self) -> list[dict[str, Any]]:
        """
        Get all registered tools in MCP format.

        Returns:
            list[dict[str, Any]]: List of tool definitions
        """
        return [tool.to_mcp_format() for tool in self._tools.values()]

    def get_tool(self, name: str) -> Tool | None:
        """
        Get a specific tool by name.

        Args:
            name: Tool name

        Returns:
            Tool | None: Tool instance or None if not found
        """
        return self._tools.get(name)

    async def execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a tool by name with provided arguments.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            dict[str, Any]: Tool execution result

        Raises:
            ValueError: If tool is not found
        """
        tool = self.get_tool(name)

        if tool is None:
            logger.warning("Tool not found", extra={"tool_name": name})
            return error_response(
                error=f"Tool '{name}' not found",
                tool_name=name,
                status_code=404,
            )

        try:
            logger.info(
                "Executing tool",
                extra={
                    "tool_name": name,
                    "arguments": {
                        k: v for k, v in arguments.items() if k not in ["password", "secret", "token"]
                    },
                },
            )

            # Execute the tool handler
            result = await tool.handler(name, arguments)

            logger.info(
                "Tool execution completed",
                extra={"tool_name": name, "success": result.get("success", False)},
            )

            return result

        except Exception as e:
            logger.error(
                "Tool execution failed",
                extra={"tool_name": name, "error": str(e)},
                exc_info=True,
            )

            return error_response(
                error=f"Tool execution failed: {str(e)}",
                tool_name=name,
                status_code=500,
            )

    def list_tool_names(self) -> list[str]:
        """
        Get list of all registered tool names.

        Returns:
            list[str]: List of tool names
        """
        return list(self._tools.keys())
