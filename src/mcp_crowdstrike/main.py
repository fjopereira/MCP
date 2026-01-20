"""
FastAPI application entry point for MCP CrowdStrike server.

This module provides the HTTP API interface for the MCP server,
including health checks, tool listing, and tool execution endpoints.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from mcp_crowdstrike.config import get_settings
from mcp_crowdstrike.server import create_server, MCPServer
from mcp_crowdstrike.utils.logging import configure_root_logger, get_logger

# Configure logging
settings = get_settings()
configure_root_logger(level=settings.log_level)
logger = get_logger(__name__)

# Global server instance
_mcp_server: MCPServer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.

    Handles startup and shutdown of the MCP server.
    """
    global _mcp_server

    try:
        logger.info("Starting MCP CrowdStrike server")
        _mcp_server = await create_server(settings)
        logger.info("MCP CrowdStrike server started successfully")
        yield
    except Exception as e:
        logger.error(
            "Failed to start server",
            extra={"error": str(e)},
            exc_info=True,
        )
        raise
    finally:
        if _mcp_server:
            logger.info("Shutting down MCP CrowdStrike server")
            await _mcp_server.shutdown()
            logger.info("MCP CrowdStrike server shut down")


# Create FastAPI application
app = FastAPI(
    title="MCP CrowdStrike",
    description="Model Context Protocol server for CrowdStrike Falcon API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ToolExecuteRequest(BaseModel):
    """Request model for tool execution."""

    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments",
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    environment: str


class ReadyResponse(BaseModel):
    """Readiness check response."""

    ready: bool
    provider_healthy: bool


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> Any:
    """Log all HTTP requests."""
    logger.info(
        "HTTP request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        },
    )

    try:
        response = await call_next(request)
        logger.info(
            "HTTP response",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
        )
        return response
    except Exception as e:
        logger.error(
            "HTTP request failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
            },
            exc_info=True,
        )
        raise


# Health check endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns:
        HealthResponse: Health status
    """
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
    )


@app.get("/ready", response_model=ReadyResponse)
async def readiness_check() -> ReadyResponse:
    """
    Readiness check endpoint.

    Verifies that the CrowdStrike connection is working.

    Returns:
        ReadyResponse: Readiness status
    """
    if _mcp_server is None:
        return ReadyResponse(ready=False, provider_healthy=False)

    try:
        provider_healthy = await _mcp_server._provider.health_check()
        return ReadyResponse(ready=True, provider_healthy=provider_healthy)
    except Exception as e:
        logger.error(
            "Readiness check failed",
            extra={"error": str(e)},
            exc_info=True,
        )
        return ReadyResponse(ready=False, provider_healthy=False)


# MCP endpoints
@app.get("/mcp/v1/tools")
async def list_tools() -> dict[str, Any]:
    """
    List all available MCP tools.

    Returns:
        dict[str, Any]: List of tool definitions

    Raises:
        HTTPException: If server is not initialized
    """
    if _mcp_server is None:
        raise HTTPException(status_code=503, detail="Server not initialized")

    try:
        tools = _mcp_server.get_tools()
        return {
            "tools": tools,
            "count": len(tools),
        }
    except Exception as e:
        logger.error(
            "Failed to list tools",
            extra={"error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tools: {str(e)}",
        )


@app.post("/mcp/v1/tools/{tool_name}")
async def execute_tool(
    tool_name: str,
    request: ToolExecuteRequest,
) -> dict[str, Any]:
    """
    Execute a specific MCP tool.

    Args:
        tool_name: Name of the tool to execute
        request: Tool execution request with arguments

    Returns:
        dict[str, Any]: Tool execution result

    Raises:
        HTTPException: If server is not initialized or execution fails
    """
    if _mcp_server is None:
        raise HTTPException(status_code=503, detail="Server not initialized")

    try:
        result = await _mcp_server.execute_tool(tool_name, request.arguments)
        return result
    except Exception as e:
        logger.error(
            "Tool execution failed",
            extra={
                "tool_name": tool_name,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}",
        )


@app.get("/sse")
async def sse_endpoint(request: Request) -> EventSourceResponse:
    """
    Server-Sent Events endpoint for MCP protocol.

    This provides the standard MCP transport mechanism via SSE.

    Args:
        request: FastAPI request object

    Returns:
        EventSourceResponse: SSE stream
    """
    if _mcp_server is None:
        raise HTTPException(status_code=503, detail="Server not initialized")

    async def event_generator() -> AsyncGenerator[dict[str, Any], None]:
        """Generate SSE events."""
        try:
            # Send initial connection event
            yield {
                "event": "connected",
                "data": '{"status": "connected", "server": "mcp-crowdstrike"}',
            }

            # Keep connection alive
            while True:
                if await request.is_disconnected():
                    break

                # Send heartbeat every 30 seconds
                await asyncio.sleep(30)
                yield {
                    "event": "heartbeat",
                    "data": '{"status": "alive"}',
                }

        except asyncio.CancelledError:
            logger.info("SSE connection cancelled")
        except Exception as e:
            logger.error(
                "SSE error",
                extra={"error": str(e)},
                exc_info=True,
            )

    return EventSourceResponse(event_generator())


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception",
        extra={"error": str(exc)},
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500,
        },
    )


# Root endpoint
@app.get("/")
async def root() -> dict[str, Any]:
    """
    Root endpoint with API information.

    Returns:
        dict[str, Any]: API information
    """
    return {
        "name": "MCP CrowdStrike",
        "version": "0.1.0",
        "description": "Model Context Protocol server for CrowdStrike Falcon API",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "tools": "/mcp/v1/tools",
            "execute": "/mcp/v1/tools/{tool_name}",
            "sse": "/sse",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mcp_crowdstrike.main:app",
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower(),
        reload=settings.environment == "development",
    )
