# Prompt for Claude on Server

Copy everything below this line and paste it to Claude on your server:

---

## Task: Create a Production-Ready MCP Server for CrowdStrike

I need you to create a complete, production-ready MCP (Model Context Protocol) Server that exposes CrowdStrike Falcon API tools. This will run as a standalone Docker container AND be usable as a Python SDK.

### Requirements

1. **Language**: All code, comments, and documentation must be in **English**
2. **Quality**: Production-grade code with proper error handling, logging, and documentation
3. **Architecture**: Clean, modular design that's easy to understand and extend
4. **Portability**: Must be easily deployable anywhere via Docker
5. **Best Practices**: Follow Python best practices (type hints, docstrings, etc.)
6. **Dual Usage**: Must work as both a standalone server AND as an importable Python SDK
7. **Code Quality**: Enforce quality with linting, formatting, security scanning, and testing tools

### Technical Stack

- **Python 3.11+**
- **FastAPI** for HTTP layer with SSE transport
- **MCP SDK** (`mcp` package) for protocol implementation
- **FalconPy** (`crowdstrike-falconpy`) for CrowdStrike API
- **Pydantic** for configuration and validation
- **Docker** with multi-stage build

### Code Quality Tools (Required)

| Tool | Purpose |
|------|---------|
| **Ruff** | Fast linting (replaces flake8, isort, pyupgrade) |
| **Black** | Code formatting |
| **Bandit** | Security vulnerability scanning |
| **Safety** | Dependency vulnerability checking |
| **pytest** | Testing framework |
| **pytest-cov** | Test coverage reporting |
| **pytest-asyncio** | Async test support |
| **pre-commit** | Git hooks for automated checks |

### Project Structure

Create this exact structure:

```
mcp-crowdstrike-server/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   └── mcp_crowdstrike/
│       ├── __init__.py             # SDK public exports
│       ├── main.py                 # FastAPI application entry point
│       ├── config.py               # Configuration management
│       ├── server.py               # MCP server setup
│       ├── sdk.py                  # SDK client for programmatic usage
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
│   │   ├── __init__.py
│   │   ├── test_hosts.py
│   │   └── test_detections.py
│   ├── test_sdk/
│   │   ├── __init__.py
│   │   └── test_sdk_client.py      # SDK usage tests
│   └── test_integration/
│       └── test_mcp_protocol.py
├── .env.example                    # Environment variables template
├── .gitignore
├── .pre-commit-config.yaml         # Pre-commit hooks configuration
├── pyproject.toml                  # Project configuration (includes all tools)
├── README.md                       # Project documentation
└── Makefile                        # Common commands (lint, test, format, etc.)
```

### SDK Usage (Dual Mode)

The project must support TWO usage modes:

**Mode 1: As a Server (Docker)**
```bash
docker compose up -d
curl http://localhost:8001/mcp/v1/tools
```

**Mode 2: As a Python SDK (Import)**
```python
from mcp_crowdstrike import CrowdStrikeClient

# Initialize client
client = CrowdStrikeClient(
    client_id="your-id",
    client_secret="your-secret"
)

# Use tools directly
devices = await client.query_devices_by_filter(
    filter="platform_name:'Windows'",
    limit=10
)

# Get device details
details = await client.get_device_details(
    device_ids=devices["device_ids"][:5]
)

# Critical action with confirmation
result = await client.contain_host(device_id="abc123")
```

### SDK Implementation

Create `src/mcp_crowdstrike/sdk.py`:
```python
"""
CrowdStrike MCP SDK

This module provides a Python client for programmatic access to CrowdStrike
tools without running the MCP server.

Example:
    >>> from mcp_crowdstrike import CrowdStrikeClient
    >>> client = CrowdStrikeClient(client_id="...", client_secret="...")
    >>> devices = await client.query_devices_by_filter(limit=10)
"""
```

Create `src/mcp_crowdstrike/__init__.py` with public exports:
```python
"""
MCP CrowdStrike - MCP Server and SDK for CrowdStrike Falcon

Usage as SDK:
    from mcp_crowdstrike import CrowdStrikeClient
    
Usage as Server:
    python -m mcp_crowdstrike.main
"""

from .sdk import CrowdStrikeClient
from .config import Settings

__version__ = "0.1.0"
__all__ = ["CrowdStrikeClient", "Settings", "__version__"]
```

### Tools to Implement

Implement these CrowdStrike tools with full error handling:

**Hosts (hosts.py):**
```python
# Tool: query_devices_by_filter
# Description: Search for hosts using FQL (Falcon Query Language) filters
# Parameters: filter (str, optional), limit (int, default=100), offset (int, default=0), sort (str, optional)
# Returns: List of device IDs matching the filter

# Tool: get_device_details  
# Description: Get detailed information about one or more hosts
# Parameters: device_ids (list[str], required)
# Returns: Detailed host information (hostname, IP, OS, status, etc.)

# Tool: contain_host
# Description: Isolate a host from the network (CRITICAL ACTION)
# Parameters: device_id (str, required)
# Returns: Containment operation status

# Tool: lift_containment
# Description: Remove network isolation from a host
# Parameters: device_id (str, required)
# Returns: Operation status
```

**Detections (detections.py):**
```python
# Tool: query_detections
# Description: Search for detections using filters
# Parameters: filter (str, optional), limit (int, default=100), sort (str, optional)
# Returns: List of detection IDs

# Tool: get_detection_details
# Description: Get detailed information about detections
# Parameters: detection_ids (list[str], required)
# Returns: Detection details (severity, tactic, technique, host info, etc.)

# Tool: update_detection_status
# Description: Update the status of a detection
# Parameters: detection_ids (list[str], required), status (str: new/in_progress/true_positive/false_positive/closed)
# Returns: Update operation status
```

**Incidents (incidents.py):**
```python
# Tool: query_incidents
# Description: Search for incidents
# Parameters: filter (str, optional), limit (int, default=100), sort (str, optional)
# Returns: List of incident IDs

# Tool: get_incident_details
# Description: Get detailed information about incidents
# Parameters: incident_ids (list[str], required)
# Returns: Incident details (status, hosts involved, detections, etc.)
```

### Configuration

The server should read these environment variables:

```bash
# Required
FALCON_CLIENT_ID=<client-id>
FALCON_CLIENT_SECRET=<client-secret>

# Optional with defaults
FALCON_BASE_URL=https://api.crowdstrike.com
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### API Endpoints

Implement these HTTP endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check, returns `{"status": "healthy"}` |
| `/ready` | GET | Readiness check (verifies CrowdStrike connection) |
| `/mcp/v1/tools` | GET | List all available tools with schemas |
| `/mcp/v1/tools/{tool_name}` | POST | Execute a specific tool |
| `/sse` | GET | SSE stream for MCP protocol (standard MCP transport) |

### Code Quality Requirements

1. **Type Hints**: All functions must have complete type annotations
2. **Docstrings**: All public functions/classes must have Google-style docstrings
3. **Error Handling**: Wrap all external calls in try/except with meaningful error messages
4. **Logging**: Use structured logging (JSON format) for all operations
5. **Validation**: Validate all inputs using Pydantic models
6. **Comments**: Add comments explaining non-obvious logic

### Docker Requirements

**Dockerfile:**
- Use multi-stage build (builder + runtime)
- Base image: `python:3.11-slim`
- Run as non-root user
- Include health check
- Optimize layer caching

**docker-compose.yml:**
- Service name: `mcp-crowdstrike`
- Expose port 8001
- Load environment from `.env` file
- Include restart policy
- Add logging configuration

### Testing Requirements

Create tests using pytest with:
- Mocked FalconPy responses (don't call real API)
- Test each tool's success and error cases
- Test input validation
- Use fixtures for common test data
- **Minimum 80% code coverage**
- Test SDK client separately from server

### Code Quality Configuration

**pyproject.toml must include these tool configurations:**

```toml
[project]
name = "mcp-crowdstrike"
version = "0.1.0"
description = "MCP Server and SDK for CrowdStrike Falcon integration"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "mcp>=1.0.0",
    "crowdstrike-falconpy>=1.4.0",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "httpx>=0.26.0",
    "sse-starlette>=1.8.0",
    "python-json-logger>=2.0.0",
]

[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "httpx>=0.26.0",  # For TestClient
    
    # Code Quality
    "ruff>=0.1.9",
    "black>=23.12.0",
    "bandit>=1.7.6",
    "safety>=2.3.5",
    
    # Pre-commit
    "pre-commit>=3.6.0",
    
    # Type checking
    "mypy>=1.8.0",
]

[project.scripts]
mcp-crowdstrike = "mcp_crowdstrike.main:main"

[project.urls]
Homepage = "https://github.com/yourusername/mcp-crowdstrike"
Documentation = "https://github.com/yourusername/mcp-crowdstrike#readme"
Repository = "https://github.com/yourusername/mcp-crowdstrike"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# ============================================================
# RUFF - Fast Python Linter
# ============================================================
[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate (commented-out code)
    "PL",     # Pylint
    "RUF",    # Ruff-specific rules
]
ignore = [
    "E501",   # line too long (handled by black)
    "PLR0913", # too many arguments
]

[tool.ruff.per-file-ignores]
"tests/*" = ["ARG", "PLR2004"]

[tool.ruff.isort]
known-first-party = ["mcp_crowdstrike"]

# ============================================================
# BLACK - Code Formatter
# ============================================================
[tool.black]
line-length = 88
target-version = ["py311"]
include = '\.pyi?$'
exclude = '''
/(
    \.git
    | \.hg
    | \.mypy_cache
    | \.ruff_cache
    | \.venv
    | _build
    | build
    | dist
)/
'''

# ============================================================
# BANDIT - Security Linter
# ============================================================
[tool.bandit]
exclude_dirs = ["tests", ".venv"]
skips = ["B101"]  # Allow assert in tests

# ============================================================
# PYTEST - Testing
# ============================================================
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--cov=src/mcp_crowdstrike",
    "--cov-report=term-missing",
    "--cov-report=html:coverage_html",
    "--cov-fail-under=80",
]
markers = [
    "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]

# ============================================================
# COVERAGE - Test Coverage
# ============================================================
[tool.coverage.run]
source = ["src/mcp_crowdstrike"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]

# ============================================================
# MYPY - Type Checking
# ============================================================
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = [
    "falconpy.*",
    "sse_starlette.*",
]
ignore_missing_imports = true
```

**Create `.pre-commit-config.yaml`:**

```yaml
# Pre-commit hooks configuration
# Install: pre-commit install
# Run manually: pre-commit run --all-files

repos:
  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: no-commit-to-branch
        args: ['--branch', 'main', '--branch', 'master']

  # Ruff - Fast Python linter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Black - Code formatter
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  # Bandit - Security linter
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]

  # Safety - Dependency vulnerability check
  - repo: https://github.com/Lucas-C/pre-commit-hooks-safety
    rev: v1.3.2
    hooks:
      - id: python-safety-dependencies-check
        files: pyproject.toml

  # Commitizen - Conventional commits
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.13.0
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

**Create `Makefile` with common commands:**

```makefile
.PHONY: help install dev lint format security test coverage clean docker-build docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  make install     - Install production dependencies"
	@echo "  make dev         - Install development dependencies"
	@echo "  make lint        - Run linters (ruff, bandit)"
	@echo "  make format      - Format code (black, ruff)"
	@echo "  make security    - Run security checks (bandit, safety)"
	@echo "  make test        - Run tests with coverage"
	@echo "  make coverage    - Generate coverage report"
	@echo "  make clean       - Remove cache and build files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up   - Start Docker container"
	@echo "  make docker-down - Stop Docker container"
	@echo "  make all         - Run format, lint, security, test"

# Installation
install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

# Code Quality
lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

security:
	bandit -c pyproject.toml -r src/
	safety check

# Testing
test:
	pytest

coverage:
	pytest --cov-report=html
	@echo "Coverage report generated in coverage_html/"

# Cleanup
clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	rm -rf *.egg-info build dist
	rm -rf coverage_html .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Docker
docker-build:
	cd docker && docker compose build

docker-up:
	cd docker && docker compose up -d

docker-down:
	cd docker && docker compose down

docker-logs:
	cd docker && docker compose logs -f

# Combined targets
all: format lint security test
	@echo "All checks passed!"

ci: lint security test
	@echo "CI checks passed!"
```

### Documentation

**README.md must include:**
1. Project overview
2. Prerequisites
3. Quick start guide
4. Configuration reference
5. API documentation
6. Tool reference with examples
7. Deployment instructions
8. Troubleshooting guide

### Example Tool Implementation Pattern

Follow this pattern for all tools:

```python
"""
CrowdStrike Host Tools

This module provides MCP tools for interacting with CrowdStrike Falcon
host/device management capabilities.
"""

from typing import Any
from mcp.types import Tool

from ..providers.crowdstrike import CrowdStrikeProvider
from ..utils.logging import get_logger
from ..utils.responses import success_response, error_response

logger = get_logger(__name__)


def get_tools() -> list[Tool]:
    """
    Returns the list of host-related tools.
    
    Each tool includes:
    - name: Unique identifier for the tool
    - description: What the tool does (used by AI to decide when to call)
    - inputSchema: JSON Schema defining expected parameters
    """
    return [
        Tool(
            name="query_devices_by_filter",
            description=(
                "Search for hosts/devices in CrowdStrike Falcon using FQL filters. "
                "Returns device IDs matching the criteria. Use this to find machines "
                "by hostname, platform, status, last seen date, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": (
                            "FQL filter string. Examples: "
                            "'platform_name:Windows', "
                            "'hostname:*server*', "
                            "'last_seen:>='2024-01-01'"
                        )
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return (1-5000)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 5000
                    },
                    "offset": {
                        "type": "integer", 
                        "description": "Pagination offset",
                        "default": 0,
                        "minimum": 0
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort field and direction. Example: 'hostname.asc'"
                    }
                },
                "required": []
            }
        ),
        # ... more tools
    ]


async def execute_tool(
    provider: CrowdStrikeProvider,
    tool_name: str,
    arguments: dict[str, Any]
) -> dict[str, Any]:
    """
    Execute a host-related tool.
    
    Args:
        provider: Initialized CrowdStrike provider instance
        tool_name: Name of the tool to execute
        arguments: Tool parameters from the MCP request
        
    Returns:
        Standardized response dict with success/error status
        
    Raises:
        ValueError: If tool_name is not recognized
    """
    logger.info(
        "Executing tool",
        extra={"tool": tool_name, "arguments": arguments}
    )
    
    try:
        if tool_name == "query_devices_by_filter":
            return await _query_devices_by_filter(provider, arguments)
        elif tool_name == "get_device_details":
            return await _get_device_details(provider, arguments)
        elif tool_name == "contain_host":
            return await _contain_host(provider, arguments)
        elif tool_name == "lift_containment":
            return await _lift_containment(provider, arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
            
    except Exception as e:
        logger.error(
            "Tool execution failed",
            extra={"tool": tool_name, "error": str(e)},
            exc_info=True
        )
        return error_response(str(e), tool_name)


async def _query_devices_by_filter(
    provider: CrowdStrikeProvider,
    args: dict[str, Any]
) -> dict[str, Any]:
    """
    Search for devices using FQL filter.
    
    Args:
        provider: CrowdStrike provider instance
        args: Tool arguments containing filter, limit, offset, sort
        
    Returns:
        Response with device_ids list and pagination metadata
    """
    response = provider.hosts.query_devices_by_filter(
        filter=args.get("filter"),
        limit=args.get("limit", 100),
        offset=args.get("offset", 0),
        sort=args.get("sort")
    )
    
    if response["status_code"] == 200:
        resources = response["body"].get("resources", [])
        meta = response["body"].get("meta", {})
        
        return success_response({
            "device_ids": resources,
            "total": len(resources),
            "pagination": meta.get("pagination", {})
        })
    
    return error_response(
        response["body"].get("errors", [{"message": "Unknown error"}]),
        "query_devices_by_filter",
        status_code=response["status_code"]
    )
```

### Now Create Everything

Please create all the files following this specification. Start with:

1. `pyproject.toml` - Project configuration with ALL tool configs (ruff, black, pytest, etc.)
2. `.pre-commit-config.yaml` - Pre-commit hooks
3. `Makefile` - Common commands
4. `src/mcp_crowdstrike/__init__.py` - Package init with SDK exports
5. `src/mcp_crowdstrike/config.py` - Configuration
6. `src/mcp_crowdstrike/providers/base.py` - Base provider
7. `src/mcp_crowdstrike/providers/crowdstrike.py` - CrowdStrike provider
8. `src/mcp_crowdstrike/tools/registry.py` - Tool registry
9. `src/mcp_crowdstrike/tools/crowdstrike/hosts.py` - Host tools
10. `src/mcp_crowdstrike/tools/crowdstrike/detections.py` - Detection tools
11. `src/mcp_crowdstrike/tools/crowdstrike/incidents.py` - Incident tools
12. `src/mcp_crowdstrike/utils/logging.py` - Logging setup
13. `src/mcp_crowdstrike/utils/responses.py` - Response helpers
14. `src/mcp_crowdstrike/sdk.py` - SDK client for programmatic usage
15. `src/mcp_crowdstrike/server.py` - MCP server
16. `src/mcp_crowdstrike/main.py` - FastAPI app
17. `docker/Dockerfile` - Docker image (multi-stage)
18. `docker/docker-compose.yml` - Compose configuration
19. `tests/conftest.py` - Test fixtures
20. `tests/test_tools/test_hosts.py` - Host tool tests
21. `tests/test_sdk/test_sdk_client.py` - SDK client tests
22. `.env.example` - Environment template
23. `.gitignore` - Git ignore rules (include Python, coverage, IDE files)
24. `README.md` - Complete documentation with SDK usage examples

Create each file completely, don't skip any content. The code should:
- Pass `make lint` without errors
- Pass `make security` without critical issues
- Pass `make test` with 80%+ coverage
- Be ready to run immediately after creation
