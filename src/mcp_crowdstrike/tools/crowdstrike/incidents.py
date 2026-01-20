"""
CrowdStrike Falcon Incident Management Tools.

This module implements tools for querying and managing incidents
in CrowdStrike Falcon. Incidents represent correlated security events.
"""

from typing import Any

from mcp_crowdstrike.providers.crowdstrike import CrowdStrikeProvider
from mcp_crowdstrike.tools.registry import Tool
from mcp_crowdstrike.utils.logging import get_logger
from mcp_crowdstrike.utils.responses import (
    api_error_response,
    error_response,
    success_response,
    validation_error_response,
)

logger = get_logger(__name__)


def get_tools() -> list[Tool]:
    """
    Get all incident management tools.

    Returns:
        list[Tool]: List of incident management tools
    """
    return [
        Tool(
            name="query_incidents",
            description=(
                "Search for incidents using FQL (Falcon Query Language) filters. "
                "Supports pagination and sorting. Returns incident IDs that can be "
                "used with get_incident_details. Incidents represent correlated "
                "detections and security events."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": (
                            "FQL filter expression (e.g., \"status:'New'+state:'open'\"). "
                            "Leave empty to query all incidents."
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (1-500)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 500,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Pagination offset",
                        "default": 0,
                        "minimum": 0,
                    },
                    "sort": {
                        "type": "string",
                        "description": (
                            "Sort field and direction (e.g., 'start.desc', 'end.asc')"
                        ),
                    },
                },
            },
            handler=lambda *args: None,
        ),
        Tool(
            name="get_incident_details",
            description=(
                "Get detailed information about specific incidents. "
                "Provide incident IDs from query_incidents to retrieve "
                "comprehensive incident information including status, hosts involved, "
                "detections, tactics, techniques, and timeline."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "incident_ids": {
                        "type": "array",
                        "description": "List of incident IDs to retrieve",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 500,
                    },
                },
                "required": ["incident_ids"],
            },
            handler=lambda *args: None,
        ),
    ]


async def execute_tool(
    provider: CrowdStrikeProvider,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute an incident management tool.

    Args:
        provider: CrowdStrike provider instance
        tool_name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        dict[str, Any]: Tool execution result
    """
    # Ensure token is fresh
    await provider.refresh_token_if_needed()

    # Route to appropriate tool handler
    if tool_name == "query_incidents":
        return await _query_incidents(provider, arguments)
    elif tool_name == "get_incident_details":
        return await _get_incident_details(provider, arguments)
    else:
        return error_response(
            error=f"Unknown tool: {tool_name}",
            tool_name=tool_name,
        )


async def _query_incidents(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Query incidents using FQL filter.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments

    Returns:
        dict[str, Any]: Query results with incident IDs
    """
    try:
        filter_expr = arguments.get("filter")
        limit = arguments.get("limit", 100)
        offset = arguments.get("offset", 0)
        sort = arguments.get("sort")

        logger.info(
            "Querying incidents",
            extra={
                "filter": filter_expr,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
        )

        # Build query parameters
        query_params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if filter_expr:
            query_params["filter"] = filter_expr

        if sort:
            query_params["sort"] = sort

        # Execute query
        response = provider.incidents.query_incidents(**query_params)

        # Check response status
        if response.get("status_code") != 200:
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="query_incidents",
            )

        # Extract incident IDs
        incident_ids = response.get("body", {}).get("resources", [])
        total = response.get("body", {}).get("meta", {}).get("pagination", {}).get("total", len(incident_ids))

        logger.info(
            "Query completed",
            extra={"incident_count": len(incident_ids), "total": total},
        )

        return success_response(
            data={
                "incident_ids": incident_ids,
            },
            metadata={
                "total": total,
                "limit": limit,
                "offset": offset,
            },
        )

    except Exception as e:
        logger.error(
            "Failed to query incidents",
            extra={"error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to query incidents: {str(e)}",
            tool_name="query_incidents",
        )


async def _get_incident_details(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Get detailed incident information.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments containing incident_ids

    Returns:
        dict[str, Any]: Incident details
    """
    try:
        incident_ids = arguments.get("incident_ids", [])

        if not incident_ids:
            return validation_error_response(
                field="incident_ids",
                message="At least one incident ID is required",
                tool_name="get_incident_details",
            )

        logger.info(
            "Getting incident details",
            extra={"incident_count": len(incident_ids)},
        )

        # Execute query
        response = provider.incidents.get_incidents(ids=incident_ids)

        # Check response status
        if response.get("status_code") != 200:
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="get_incident_details",
            )

        # Extract incident details
        incidents = response.get("body", {}).get("resources", [])

        logger.info(
            "Incident details retrieved",
            extra={"incident_count": len(incidents)},
        )

        return success_response(
            data={
                "incidents": incidents,
            },
            metadata={
                "count": len(incidents),
            },
        )

    except Exception as e:
        logger.error(
            "Failed to get incident details",
            extra={"error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to get incident details: {str(e)}",
            tool_name="get_incident_details",
        )
