# MCP Server for CrowdStrike - Implementation Plan

## Overview

This document provides a complete implementation plan for a **production-ready MCP (Model Context Protocol) Server** that exposes CrowdStrike Falcon API tools for AI agents.

### Goals
- Create a standalone Docker container running an MCP Server with SSE transport
- Expose CrowdStrike Falcon tools following MCP specification
- Provide a Python SDK for programmatic usage (dual-mode: server + library)
- Follow best practices for security, scalability, and maintainability
- Write clean, well-documented code in English
- Enforce code quality with automated tools
- Make it portable and easy to deploy anywhere

### Code Quality Stack

| Tool | Purpose | Command |
|------|---------|---------|
| **Ruff** | Fast linting (errors, style, imports) | `ruff check src/` |
| **Black** | Code formatting | `black src/` |
| **Bandit** | Security vulnerability scanning | `bandit -r src/` |
| **Safety** | Dependency vulnerability check | `safety check` |
| **pytest** | Testing framework | `pytest` |
| **pytest-cov** | Code coverage (min 80%) | `pytest --cov` |
| **mypy** | Static type checking | `mypy src/` |
| **pre-commit** | Git hooks automation | `pre-commit run --all` |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Server (Docker)                      │
│                                                              │
│   ┌──────────────────┐         ┌──────────────────────────┐ │
│   │  Existing Apps   │         │   MCP Server Container   │ │
│   │  (Django, etc)   │         │                          │ │
│   │                  │         │  ┌────────────────────┐  │ │
│   │    Port 8000     │         │  │   FastAPI + SSE    │  │ │
│   └──────────────────┘         │  │   (HTTP Layer)     │  │ │
│                                │  └─────────┬──────────┘  │ │
│                                │            │             │ │
│                                │  ┌─────────▼──────────┐  │ │
│                                │  │   MCP Protocol     │  │ │
│                                │  │   (Tool Registry)  │  │ │
│                                │  └─────────┬──────────┘  │ │
│                                │            │             │ │
│                                │  ┌─────────▼──────────┐  │ │
│                                │  │   Provider Layer   │  │ │
│                                │  │   (CrowdStrike)    │  │ │
│                                │  └─────────┬──────────┘  │ │
│                                │            │             │ │
│                                │       Port 8001         │ │
│                                └────────────┼────────────┘ │
└─────────────────────────────────────────────┼──────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │  CrowdStrike     │
                                    │  Falcon API      │
                                    └──────────────────┘
```

---

## Project Structure

```
mcp-crowdstrike-server/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   └── mcp_crowdstrike/
│       ├── __init__.py
│       ├── main.py                 # FastAPI application entry point
│       ├── config.py               # Configuration management
│       ├── server.py               # MCP server setup
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py             # Abstract base provider
│       │   └── crowdstrike.py      # CrowdStrike implementation
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── registry.py         # Tool registration system
│       │   └── crowdstrike/
│       │       ├── __init__.py
│       │       ├── hosts.py        # Host-related tools
│       │       ├── detections.py   # Detection-related tools
│       │       └── incidents.py    # Incident-related tools
│       └── utils/
│           ├── __init__.py
│           ├── logging.py          # Logging configuration
│           └── responses.py        # Standardized response helpers
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_tools/
│   │   ├── test_hosts.py
│   │   ├── test_detections.py
│   │   └── test_incidents.py
│   └── test_integration/
│       └── test_mcp_protocol.py
├── .env.example                    # Environment variables template
├── .gitignore
├── pyproject.toml                  # Project configuration
├── README.md                       # Project documentation
└── Makefile                        # Common commands
```

---

## Implementation Steps

### Step 1: Create Project Base Structure

Create all directories and base files:
- `docker/` - Container configuration
- `src/mcp_crowdstrike/` - Main application code
- `tests/` - Test suite
- Configuration files at root

### Step 2: Implement Configuration Management

Create `src/mcp_crowdstrike/config.py`:
- Load settings from environment variables
- Validate required credentials
- Support multiple environments (dev, staging, prod)
- Use Pydantic for validation

### Step 3: Implement Base Provider Pattern

Create `src/mcp_crowdstrike/providers/base.py`:
- Abstract base class for all security providers
- Define interface: `initialize()`, `shutdown()`, `get_tools()`
- Enable easy addition of new providers (Sentinel, Splunk, etc.)

### Step 4: Implement CrowdStrike Provider

Create `src/mcp_crowdstrike/providers/crowdstrike.py`:
- Implement CrowdStrike-specific authentication
- Handle token refresh automatically
- Wrap FalconPy SDK with error handling

### Step 5: Implement Tool Registry

Create `src/mcp_crowdstrike/tools/registry.py`:
- Central registry for all tools
- Auto-discovery of tools from providers
- Convert tools to MCP format

### Step 6: Implement CrowdStrike Tools

Create tools in `src/mcp_crowdstrike/tools/crowdstrike/`:

**hosts.py:**
- `query_devices_by_filter` - Search hosts using FQL
- `get_device_details` - Get detailed host information
- `contain_host` - Network isolation (critical action)
- `lift_containment` - Remove network isolation

**detections.py:**
- `query_detections` - Search detections
- `get_detection_details` - Get detection information
- `update_detection_status` - Change detection status

**incidents.py:**
- `query_incidents` - Search incidents
- `get_incident_details` - Get incident information
- `update_incident_status` - Change incident status

### Step 7: Implement MCP Server

Create `src/mcp_crowdstrike/server.py`:
- Set up MCP server instance
- Register tools from registry
- Handle tool execution
- Format responses per MCP spec

### Step 8: Implement HTTP Layer (FastAPI + SSE)

Create `src/mcp_crowdstrike/main.py`:
- FastAPI application with SSE transport
- Health check endpoint
- MCP protocol endpoints
- CORS configuration for testing

### Step 9: Implement Logging and Utilities

Create utility modules:
- Structured logging with JSON format
- Standardized response helpers
- Error handling utilities

### Step 10: Create Docker Configuration

Create `docker/Dockerfile`:
- Multi-stage build for smaller image
- Non-root user for security
- Health check configuration

Create `docker/docker-compose.yml`:
- Service definition
- Environment variable mapping
- Network configuration
- Volume mounts for logs

### Step 11: Write Tests

Create test suite:
- Unit tests for each tool with mocked API responses
- Integration tests for MCP protocol compliance
- Fixtures for common test data

### Step 12: Create Documentation

Create `README.md`:
- Installation instructions
- Configuration guide
- API documentation
- Deployment guide
- Troubleshooting section

---

## Tools to Implement (Priority Order)

### Priority 1: Core Host Operations
| Tool Name | Description | CrowdStrike API |
|-----------|-------------|-----------------|
| `query_devices_by_filter` | Search hosts using FQL filters | Hosts.QueryDevicesByFilter |
| `get_device_details` | Get detailed host information | Hosts.GetDeviceDetails |
| `contain_host` | Isolate host from network | Hosts.PerformActionV2 |
| `lift_containment` | Remove network isolation | Hosts.PerformActionV2 |

### Priority 2: Detection Operations
| Tool Name | Description | CrowdStrike API |
|-----------|-------------|-----------------|
| `query_detections` | Search detections | Detects.QueryDetects |
| `get_detection_details` | Get detection details | Detects.GetDetectSummaries |
| `update_detection_status` | Update status/assignment | Detects.UpdateDetectsByIds |

### Priority 3: Incident Operations
| Tool Name | Description | CrowdStrike API |
|-----------|-------------|-----------------|
| `query_incidents` | Search incidents | Incidents.QueryIncidents |
| `get_incident_details` | Get incident details | Incidents.GetIncidents |
| `update_incident_status` | Update incident | Incidents.PerformIncidentAction |

### Priority 4: IOC Operations
| Tool Name | Description | CrowdStrike API |
|-----------|-------------|-----------------|
| `query_iocs` | Search IOCs | IOC.QueryIOCs |
| `get_ioc_details` | Get IOC details | IOC.GetIndicators |
| `create_ioc` | Create new IOC | IOC.CreateIOC |
| `delete_ioc` | Delete IOC | IOC.DeleteIOCs |

---

## Configuration Variables

```bash
# Required
FALCON_CLIENT_ID=<your-client-id>
FALCON_CLIENT_SECRET=<your-client-secret>

# Optional
FALCON_BASE_URL=https://api.crowdstrike.com  # US-1 default
LOG_LEVEL=INFO
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
ENVIRONMENT=development

# For US-2: https://api.us-2.crowdstrike.com
# For EU-1: https://api.eu-1.crowdstrike.com
```

---

## API Endpoints (MCP over HTTP/SSE)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/mcp/v1/tools` | GET | List available tools |
| `/mcp/v1/tools/{name}` | POST | Execute a tool |
| `/mcp/v1/sse` | GET | SSE stream for MCP protocol |

---

## Security Considerations

1. **Credentials**: Never commit credentials; use environment variables
2. **Network**: Run in isolated Docker network
3. **Authentication**: Consider adding API key for MCP endpoint access
4. **Audit Logging**: Log all tool executions with timestamps
5. **Rate Limiting**: Implement rate limiting on critical tools
6. **Input Validation**: Validate all tool inputs before API calls

---

## Testing Strategy

1. **Unit Tests**: Mock FalconPy responses, test tool logic
2. **Integration Tests**: Test MCP protocol compliance
3. **Manual Tests**: Use MCP Inspector or curl to test endpoints

---

## Deployment Checklist

- [ ] Copy project to server
- [ ] Create `.env` file with credentials
- [ ] Build Docker image: `docker compose build`
- [ ] Start container: `docker compose up -d`
- [ ] Verify health: `curl http://localhost:8001/health`
- [ ] List tools: `curl http://localhost:8001/mcp/v1/tools`
- [ ] Test a tool manually
- [ ] Share endpoint with tester

---

## Rollback Plan

To completely remove:
```bash
docker compose down
docker rmi mcp-crowdstrike-server
rm -rf ./mcp-crowdstrike-server
```

No changes to existing services required.
