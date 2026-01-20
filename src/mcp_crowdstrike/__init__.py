"""
MCP CrowdStrike - MCP Server and SDK for CrowdStrike Falcon

This package provides a dual-mode implementation:
1. **Server Mode**: Run as a standalone MCP server via Docker or uvicorn
2. **SDK Mode**: Import and use as a Python library

Usage as SDK:
    >>> from mcp_crowdstrike import CrowdStrikeClient
    >>> async with CrowdStrikeClient(
    ...     client_id="your-client-id",
    ...     client_secret="your-client-secret"
    ... ) as client:
    ...     devices = await client.query_devices_by_filter(limit=10)
    ...     print(devices)

Usage as Server:
    $ python -m mcp_crowdstrike.main

Author: Fábio Pereira
License: MIT
"""

from mcp_crowdstrike.config import Settings

__version__ = "0.1.0"
__author__ = "Fábio Pereira"
__license__ = "MIT"

# Defer SDK import to avoid circular dependencies and allow optional usage
__all__ = [
    "Settings",
    "__version__",
    "__author__",
    "__license__",
]


def __getattr__(name: str) -> object:
    """Lazy import for CrowdStrikeClient to avoid circular dependencies."""
    if name == "CrowdStrikeClient":
        from mcp_crowdstrike.sdk import CrowdStrikeClient

        return CrowdStrikeClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
