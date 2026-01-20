"""
CrowdStrike Falcon Detection Management Tools.

This module implements tools for querying and managing detections
in CrowdStrike Falcon. Detections represent security events and alerts.
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

# Valid detection statuses
VALID_STATUSES = [
    "new",
    "in_progress",
    "true_positive",
    "false_positive",
    "closed",
    "ignored",
    "reopened",
]


def get_tools() -> list[Tool]:
    """
    Get all detection management tools.

    Returns:
        list[Tool]: List of detection management tools
    """
    return [
        Tool(
            name="query_detections",
            description=(
                "Search for detections using FQL (Falcon Query Language) filters. "
                "Supports pagination and sorting. Returns detection IDs that can be "
                "used with get_detection_details."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": (
                            "FQL filter expression (e.g., \"status:'new'+severity:['medium','high']\"). "
                            "Leave empty to query all detections."
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
                            "Sort field and direction (e.g., 'created_timestamp.desc')"
                        ),
                    },
                },
            },
            handler=lambda *args: None,
        ),
        Tool(
            name="get_detection_details",
            description=(
                "Get detailed information about specific detections. "
                "Provide detection IDs from query_detections to retrieve "
                "comprehensive detection information including severity, tactics, "
                "techniques, and host information."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "detection_ids": {
                        "type": "array",
                        "description": "List of detection IDs to retrieve",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 1000,
                    },
                },
                "required": ["detection_ids"],
            },
            handler=lambda *args: None,
        ),
        Tool(
            name="update_detection_status",
            description=(
                "Update the status of one or more detections. "
                "Use this for triage and incident response workflows. "
                f"Valid statuses: {', '.join(VALID_STATUSES)}"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "detection_ids": {
                        "type": "array",
                        "description": "List of detection IDs to update",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "status": {
                        "type": "string",
                        "description": f"New status. Valid values: {', '.join(VALID_STATUSES)}",
                        "enum": VALID_STATUSES,
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional comment explaining the status change",
                    },
                },
                "required": ["detection_ids", "status"],
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
    Execute a detection management tool.

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
    if tool_name == "query_detections":
        return await _query_detections(provider, arguments)
    elif tool_name == "get_detection_details":
        return await _get_detection_details(provider, arguments)
    elif tool_name == "update_detection_status":
        return await _update_detection_status(provider, arguments)
    else:
        return error_response(
            error=f"Unknown tool: {tool_name}",
            tool_name=tool_name,
        )


async def _query_detections(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Query detections using FQL filter.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments

    Returns:
        dict[str, Any]: Query results with detection IDs
    """
    try:
        filter_expr = arguments.get("filter")
        limit = arguments.get("limit", 100)
        offset = arguments.get("offset", 0)
        sort = arguments.get("sort")

        logger.info(
            "Querying detections",
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
        response = provider.detects.query_detects(**query_params)

        # Check response status
        if response.get("status_code") != 200:
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="query_detections",
            )

        # Extract detection IDs
        detection_ids = response.get("body", {}).get("resources", [])
        total = response.get("body", {}).get("meta", {}).get("pagination", {}).get("total", len(detection_ids))

        logger.info(
            "Query completed",
            extra={"detection_count": len(detection_ids), "total": total},
        )

        return success_response(
            data={
                "detection_ids": detection_ids,
            },
            metadata={
                "total": total,
                "limit": limit,
                "offset": offset,
            },
        )

    except Exception as e:
        logger.error(
            "Failed to query detections",
            extra={"error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to query detections: {str(e)}",
            tool_name="query_detections",
        )


async def _get_detection_details(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Get detailed detection information.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments containing detection_ids

    Returns:
        dict[str, Any]: Detection details
    """
    try:
        detection_ids = arguments.get("detection_ids", [])

        if not detection_ids:
            return validation_error_response(
                field="detection_ids",
                message="At least one detection ID is required",
                tool_name="get_detection_details",
            )

        logger.info(
            "Getting detection details",
            extra={"detection_count": len(detection_ids)},
        )

        # Execute query
        response = provider.detects.get_detect_summaries(ids=detection_ids)

        # Check response status
        if response.get("status_code") != 200:
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="get_detection_details",
            )

        # Extract detection details
        detections = response.get("body", {}).get("resources", [])

        logger.info(
            "Detection details retrieved",
            extra={"detection_count": len(detections)},
        )

        return success_response(
            data={
                "detections": detections,
            },
            metadata={
                "count": len(detections),
            },
        )

    except Exception as e:
        logger.error(
            "Failed to get detection details",
            extra={"error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to get detection details: {str(e)}",
            tool_name="get_detection_details",
        )


async def _update_detection_status(
    provider: CrowdStrikeProvider,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Update detection status.

    Args:
        provider: CrowdStrike provider instance
        arguments: Tool arguments containing detection_ids and status

    Returns:
        dict[str, Any]: Update operation result
    """
    try:
        detection_ids = arguments.get("detection_ids", [])
        status = arguments.get("status")
        comment = arguments.get("comment")

        if not detection_ids:
            return validation_error_response(
                field="detection_ids",
                message="At least one detection ID is required",
                tool_name="update_detection_status",
            )

        if not status:
            return validation_error_response(
                field="status",
                message="Status is required",
                tool_name="update_detection_status",
            )

        # Validate status
        if status not in VALID_STATUSES:
            return validation_error_response(
                field="status",
                message=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}",
                tool_name="update_detection_status",
            )

        logger.info(
            "Updating detection status",
            extra={
                "detection_count": len(detection_ids),
                "status": status,
                "has_comment": bool(comment),
            },
        )

        # Build update payload
        update_payload: dict[str, Any] = {
            "ids": detection_ids,
            "status": status,
        }

        if comment:
            update_payload["comment"] = comment

        # Execute update
        response = provider.detects.update_detects_by_ids(**update_payload)

        # Check response status
        if response.get("status_code") not in [200, 202]:
            return api_error_response(
                api_name="CrowdStrike Falcon",
                status_code=response.get("status_code", 500),
                message=str(response.get("body", {}).get("errors", "Unknown error")),
                tool_name="update_detection_status",
            )

        logger.info(
            "Detection status updated successfully",
            extra={"detection_count": len(detection_ids), "status": status},
        )

        return success_response(
            data={
                "updated_count": len(detection_ids),
                "detection_ids": detection_ids,
                "status": status,
            },
        )

    except Exception as e:
        logger.error(
            "Failed to update detection status",
            extra={"error": str(e)},
            exc_info=True,
        )
        return error_response(
            error=f"Failed to update detection status: {str(e)}",
            tool_name="update_detection_status",
        )
