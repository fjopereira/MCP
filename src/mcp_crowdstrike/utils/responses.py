"""
Standardized response utilities for MCP CrowdStrike.

This module provides consistent response formatting across all tools and API endpoints.
All responses follow a standard structure for success and error cases.
"""

from typing import Any


def success_response(
    data: Any,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        data: The response data (can be any JSON-serializable type)
        metadata: Optional metadata (pagination, timing, etc.)

    Returns:
        dict[str, Any]: Standardized success response

    Example:
        >>> success_response({"device_ids": ["abc", "def"]}, {"total": 2})
        {
            "success": True,
            "data": {"device_ids": ["abc", "def"]},
            "metadata": {"total": 2}
        }
    """
    response: dict[str, Any] = {
        "success": True,
        "data": data,
    }

    if metadata is not None:
        response["metadata"] = metadata

    return response


def error_response(
    error: str | list[str],
    tool_name: str | None = None,
    status_code: int | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        error: Error message(s). Can be a single string or list of strings.
        tool_name: Optional name of the tool that generated the error
        status_code: Optional HTTP status code or API error code
        details: Optional additional error details

    Returns:
        dict[str, Any]: Standardized error response

    Example:
        >>> error_response(
        ...     "Device not found",
        ...     tool_name="get_device_details",
        ...     status_code=404
        ... )
        {
            "success": False,
            "error": "Device not found",
            "tool": "get_device_details",
            "status_code": 404
        }
    """
    response: dict[str, Any] = {
        "success": False,
        "error": error if isinstance(error, list) else error,
    }

    if tool_name is not None:
        response["tool"] = tool_name

    if status_code is not None:
        response["status_code"] = status_code

    if details is not None:
        response["details"] = details

    return response


def validation_error_response(
    field: str,
    message: str,
    tool_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a standardized validation error response.

    Args:
        field: The field that failed validation
        message: The validation error message
        tool_name: Optional name of the tool

    Returns:
        dict[str, Any]: Standardized validation error response

    Example:
        >>> validation_error_response(
        ...     "device_id",
        ...     "Device ID is required",
        ...     tool_name="contain_host"
        ... )
        {
            "success": False,
            "error": "Validation error",
            "tool": "contain_host",
            "details": {
                "field": "device_id",
                "message": "Device ID is required"
            }
        }
    """
    return error_response(
        error="Validation error",
        tool_name=tool_name,
        details={
            "field": field,
            "message": message,
        },
    )


def api_error_response(
    api_name: str,
    status_code: int,
    message: str,
    tool_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a standardized API error response.

    Args:
        api_name: Name of the external API (e.g., "CrowdStrike Falcon")
        status_code: HTTP status code from the API
        message: Error message from the API
        tool_name: Optional name of the tool

    Returns:
        dict[str, Any]: Standardized API error response

    Example:
        >>> api_error_response(
        ...     "CrowdStrike Falcon",
        ...     401,
        ...     "Invalid credentials",
        ...     tool_name="query_devices_by_filter"
        ... )
        {
            "success": False,
            "error": "CrowdStrike Falcon API error",
            "tool": "query_devices_by_filter",
            "status_code": 401,
            "details": {
                "api": "CrowdStrike Falcon",
                "message": "Invalid credentials"
            }
        }
    """
    return error_response(
        error=f"{api_name} API error",
        tool_name=tool_name,
        status_code=status_code,
        details={
            "api": api_name,
            "message": message,
        },
    )
