"""
CrowdStrike Falcon Host Management Tools.

This module implements tools for querying and managing hosts (devices)
in CrowdStrike Falcon. Includes critical security operations like host containment.
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
    Get all host management tools.

    Returns:
        list[Tool]: List of host management tools
    """
    return [
        Tool(
            name="query_devices_by_filter",
            description=(
                "Search for hosts using FQL (Falcon Query Language) filters. "
                "Supports pagination and sorting. Returns device IDs that can be "
                "used with get_device_details."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": (
                            "FQL filter expression (e.g., \"platform_name:'Windows'+hostname:'*server*'\"). "
                            "Leave empty to query all devices."
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (1-5000)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 5000,
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
                            "Sort field and direction (e.g., 'hostname.asc', 'last_seen.desc')"
                        ),
                    },
                },
            },
            handler=lambda *args: None,  # Placeholder, will be set by registry
        ),
        Tool(
            name="get_device_details",
            description=(
                "Get detailed information about specific hosts. "
                "Provide device IDs from query_devices_by_filter to retrieve "
                "comprehensive host information including OS, IP, status, and more."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "device_ids": {
                        "type": "array",
                        "description": "List of device IDs to retrieve",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 5000,
                    },
                },
                "required": ["device_ids"],
            },
            handler=lambda *args: None,
        ),
        Tool(
            name="contain_host",
            description=(
                "⚠️ CRITICAL ACTION: Isolate a host from the network (network containment). "
                "This prevents the host from communicating on the network except with "
                "CrowdStrike cloud. Use this for incident response to prevent lateral "
                "movement. This action is logged and audited. Use lift_containment to restore."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID to contain (isolate)",
                    },
                },
                "required": ["device_id"],
            },
            handler=lambda *args: None,
        ),
        Tool(
            name="lift_containment",
            description=(
                "Remove network isolation from a host. "
                "Restores normal network communication after a host has been contained. "
                "Use this after incident response is complete."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID to lift containment from",
                    },
                },
                "required": ["device_id"],
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
    Execute a host management tool.

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
    if tool_name == "query_devices_by_filter":
        return await _query_devices_by_filter(provider, arguments)
    elif tool_name == "get_device_details":
        return await _get_device_details(provider, arguments)
    elif tool_name == "contain_host":
        return await _contain_host(provider, arguments)
    elif tool_name == "lift_containment":
        return await _lift_containment(provider, arguments)
    else:
        return error_response(
            error=f"Unknown tool: {tool_name}",
            tool_name=tool_name,
        )


async def _query_devices_by_filter(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Query devices using FQL filter.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments

    Returns:
        dict[str, Any]: Query results with device IDs
    """
    try:
        filter_expr = arguments.get("filter")
        limit = arguments.get("limit", 100)
        offset = arguments.get("offset", 0)
        sort = arguments.get("sort")

        logger.info(
            "Querying devices",
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
        response = provider.hosts.query_devices_by_filter(**query_params)

        # Check response status
        if response.get("status_code") != 200:
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="query_devices_by_filter",
            )

        # Extract device IDs
        device_ids = response.get("body", {}).get("resources", [])
        total = response.get("body", {}).get("meta", {}).get("pagination", {}).get("total", len(device_ids))

        logger.info(
            "Query completed",
            extra={"device_count": len(device_ids), "total": total},
        )

        return success_response(
            data={
                "device_ids": device_ids,
            },
            metadata={
                "total": total,
                "limit": limit,
                "offset": offset,
            },
        )

    except Exception as e:
        logger.error(
            "Failed to query devices",
            extra={"error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to query devices: {str(e)}",
            tool_name="query_devices_by_filter",
        )


async def _get_device_details(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Get detailed device information.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments containing device_ids

    Returns:
        dict[str, Any]: Device details
    """
    try:
        device_ids = arguments.get("device_ids", [])

        if not device_ids:
            return validation_error_response(
                field="device_ids",
                message="At least one device ID is required",
                tool_name="get_device_details",
            )

        logger.info(
            "Getting device details",
            extra={"device_count": len(device_ids)},
        )

        # Execute query
        response = provider.hosts.get_device_details(ids=device_ids)

        # Check response status
        if response.get("status_code") != 200:
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="get_device_details",
            )

        # Extract device details
        devices = response.get("body", {}).get("resources", [])

        logger.info(
            "Device details retrieved",
            extra={"device_count": len(devices)},
        )

        return success_response(
            data={
                "devices": devices,
            },
            metadata={
                "count": len(devices),
            },
        )

    except Exception as e:
        logger.error(
            "Failed to get device details",
            extra={"error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to get device details: {str(e)}",
            tool_name="get_device_details",
        )


async def _contain_host(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Contain (isolate) a host from the network.

    ⚠️ CRITICAL SECURITY ACTION - This is logged and audited.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments containing device_id

    Returns:
        dict[str, Any]: Containment operation result
    """
    try:
        device_id = arguments.get("device_id")

        if not device_id:
            return validation_error_response(
                field="device_id",
                message="Device ID is required",
                tool_name="contain_host",
            )

        # AUDIT LOG - Critical security action
        logger.warning(
            "CRITICAL ACTION: Initiating host containment",
            extra={
                "device_id": device_id,
                "action": "contain_host",
                "severity": "CRITICAL",
            },
        )

        # Execute containment
        response = provider.hosts.perform_action(
            action_name="contain",
            ids=[device_id],
        )

        # Check response status
        if response.get("status_code") not in [200, 202]:
            logger.error(
                "Host containment failed",
                extra={
                    "device_id": device_id,
                    "status_code": response.get("status_code"),
                    "error": response.get("body", {}).get("errors"),
                },
            )
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="contain_host",
            )

        # AUDIT LOG - Success
        logger.warning(
            "CRITICAL ACTION: Host containment successful",
            extra={
                "device_id": device_id,
                "action": "contain_host",
                "status": "SUCCESS",
                "severity": "CRITICAL",
            },
        )

        return success_response(
            data={
                "device_id": device_id,
                "action": "contained",
                "status": "success",
            },
        )

    except Exception as e:
        logger.error(
            "Failed to contain host",
            extra={"device_id": arguments.get("device_id"), "error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to contain host: {str(e)}",
            tool_name="contain_host",
        )


async def _lift_containment(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Lift containment (restore network access) for a host.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments containing device_id

    Returns:
        dict[str, Any]: Lift containment operation result
    """
    try:
        device_id = arguments.get("device_id")

        if not device_id:
            return validation_error_response(
                field="device_id",
                message="Device ID is required",
                tool_name="lift_containment",
            )

        logger.info(
            "Lifting host containment",
            extra={"device_id": device_id},
        )

        # Execute lift containment
        response = provider.hosts.perform_action(
            action_name="lift_containment",
            ids=[device_id],
        )

        # Check response status
        if response.get("status_code") not in [200, 202]:
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="lift_containment",
            )

        logger.info(
            "Host containment lifted successfully",
            extra={"device_id": device_id},
        )

        return success_response(
            data={
                "device_id": device_id,
                "action": "containment_lifted",
                "status": "success",
            },
        )

    except Exception as e:
        logger.error(
            "Failed to lift containment",
            extra={"device_id": arguments.get("device_id"), "error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to lift containment: {str(e)}",
            tool_name="lift_containment",
        )
