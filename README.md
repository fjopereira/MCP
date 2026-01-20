# MCP Server for CrowdStrike Falcon

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Production-ready Model Context Protocol (MCP) server and Python SDK for CrowdStrike Falcon API integration. This dual-mode implementation enables seamless security automation through both server deployment and programmatic access.

## 🎯 Project Overview

This project provides a comprehensive integration with CrowdStrike Falcon, enabling security teams to:

- **Query and manage hosts** across your infrastructure
- **Investigate and triage security detections** in real-time
- **Respond to incidents** with automated workflows
- **Isolate compromised hosts** (network containment) for incident response

### Key Features

- ✅ **Dual-Mode Functionality**: Works as both a Docker server and importable Python SDK
- ✅ **Production-Grade Quality**: Ruff, Black, Bandit, Safety, pytest, pre-commit hooks
- ✅ **80%+ Test Coverage**: Comprehensive unit, integration, and SDK tests
- ✅ **Security-First Design**: No credentials in git, comprehensive .gitignore, audit logging
- ✅ **Professional Standards**: Complete type hints, docstrings, structured logging
- ✅ **9 Powerful Tools**: Host management (4), Detection management (3), Incident management (2)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│  ┌──────────────┐              ┌──────────────────────┐   │
│  │ MCP Client   │              │ Python Application   │   │
│  │ (Claude, etc)│              │ (Direct SDK Usage)   │   │
│  └──────┬───────┘              └──────────┬───────────┘   │
└─────────┼────────────────────────────────┼───────────────┘
          │                                 │
          │ HTTP/SSE                        │ Python Import
          │                                 │
┌─────────▼─────────────────────────────────▼───────────────┐
│                    MCP CrowdStrike                         │
│  ┌──────────────────────────────────────────────────┐    │
│  │  FastAPI Server (main.py)  │  SDK Client (sdk.py)│    │
│  └──────────────┬──────────────┴─────────┬──────────┘    │
│                 │                         │                │
│  ┌──────────────▼──────────────────────────▼──────────┐  │
│  │         MCP Server & Tool Registry                  │  │
│  │  - Tool Discovery      - Execution Routing          │  │
│  │  - Protocol Handling   - Response Formatting        │  │
│  └──────────────┬──────────────────────────────────────┘  │
│                 │                                          │
│  ┌──────────────▼──────────────────────────────────────┐  │
│  │                   Tools Layer                        │  │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────────────┐ │  │
│  │  │  Hosts   │ │ Detections │ │   Incidents      │ │  │
│  │  │ (4 tools)│ │ (3 tools)  │ │   (2 tools)      │ │  │
│  │  └──────────┘ └────────────┘ └──────────────────┘ │  │
│  └──────────────┬──────────────────────────────────────┘  │
│                 │                                          │
│  ┌──────────────▼──────────────────────────────────────┐  │
│  │          CrowdStrike Provider                        │  │
│  │  - OAuth2 Authentication  - Token Management         │  │
│  │  - API Client Management  - Connection Health        │  │
│  └──────────────┬──────────────────────────────────────┘  │
└─────────────────┼────────────────────────────────────────┘
                  │
                  │ HTTPS
                  │
┌─────────────────▼────────────────────────────────────────┐
│             CrowdStrike Falcon API                        │
│  - Hosts API      - Detections API    - Incidents API    │
└───────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Python 3.11+** (required for modern type hints and performance)
- **Docker** (optional, for server mode deployment)
- **CrowdStrike Falcon API Credentials**:
  - Client ID
  - Client Secret
  - Appropriate API scopes (Hosts, Detections, Incidents read/write)

### Obtaining CrowdStrike Credentials

1. Log in to your CrowdStrike Falcon console
2. Navigate to **Support > API Clients & Keys**
3. Create a new API client with the following scopes:
   - **Hosts**: Read, Write (for containment)
   - **Detections**: Read, Write
   - **Incidents**: Read
4. Save the Client ID and Client Secret securely

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Linux/Mac:**
```bash
git clone https://github.com/fjopereira/MCP.git
cd MCP
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
git clone https://github.com/fjopereira/MCP.git
cd MCP
setup.bat
```

### Option 2: Manual Setup

```bash
# Clone repository
git clone https://github.com/fjopereira/MCP.git
cd MCP

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env with your CrowdStrike credentials
```

### Option 3: Docker Deployment (Server Mode)

```bash
# Clone repository
git clone https://github.com/fjopereira/MCP.git
cd MCP

# Create .env file with credentials
cp .env.example .env
# Edit .env with your CrowdStrike credentials

# Build and start
cd docker
docker compose up -d

# View logs
docker compose logs -f

# Stop server
docker compose down
```

## 💻 Usage

### Server Mode (Docker)

Deploy as a standalone MCP server accessible via HTTP/SSE:

```bash
cd docker
docker compose up -d

# Test health
curl http://localhost:8001/health

# List available tools
curl http://localhost:8001/mcp/v1/tools

# Execute a tool
curl -X POST http://localhost:8001/mcp/v1/tools/query_devices_by_filter \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"limit": 10}}'
```

**Server Endpoints:**
- `GET /health` - Health check
- `GET /ready` - Readiness check (verifies CrowdStrike connection)
- `GET /mcp/v1/tools` - List all available tools
- `POST /mcp/v1/tools/{tool_name}` - Execute a specific tool
- `GET /sse` - SSE stream for MCP protocol

### SDK Mode (Python Library)

Use as a Python library for custom automation:

```python
import asyncio
from mcp_crowdstrike import CrowdStrikeClient

async def main():
    # Create client
    async with CrowdStrikeClient(
        client_id="your-client-id",
        client_secret="your-client-secret"
    ) as client:
        # Query devices
        devices = await client.query_devices_by_filter(
            filter="platform_name:'Windows'",
            limit=10
        )
        print(f"Found {len(devices['data']['device_ids'])} devices")

        # Get device details
        if devices['data']['device_ids']:
            details = await client.get_device_details(
                device_ids=devices['data']['device_ids'][:5]
            )
            for device in details['data']['devices']:
                print(f"  - {device['hostname']}: {device['status']}")

        # Query detections
        detections = await client.query_detections(
            filter="status:'new'+severity:'high'",
            limit=50
        )
        print(f"Found {len(detections['data']['detection_ids'])} high-severity detections")

        # CRITICAL ACTION: Contain a compromised host
        # result = await client.contain_host(device_id="abc123")
        # print(f"Containment status: {result['data']['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🛠️ Available Tools

### Host Management (4 tools)

#### 1. `query_devices_by_filter`
Search for hosts using FQL (Falcon Query Language) filters.

**Parameters:**
- `filter` (string, optional): FQL filter expression
- `limit` (integer, default=100): Maximum results (1-5000)
- `offset` (integer, default=0): Pagination offset
- `sort` (string, optional): Sort field and direction

**Example:**
```python
devices = await client.query_devices_by_filter(
    filter="platform_name:'Windows'+last_seen:>'2024-01-01'",
    limit=100,
    sort="hostname.asc"
)
```

**FQL Filter Examples:**
- `platform_name:'Windows'` - Windows hosts only
- `status:'contained'` - Isolated hosts
- `last_seen:>'2024-01-01'` - Seen after date
- `platform_name:'Linux'+hostname:'*web*'` - Linux hosts with 'web' in hostname

#### 2. `get_device_details`
Get detailed information about specific hosts.

**Parameters:**
- `device_ids` (array, required): List of device IDs

**Example:**
```python
details = await client.get_device_details(
    device_ids=["device-id-1", "device-id-2"]
)
```

#### 3. `contain_host` ⚠️ CRITICAL
Isolate a host from the network (network containment).

**Parameters:**
- `device_id` (string, required): Device ID to contain

**Example:**
```python
result = await client.contain_host(device_id="abc123")
```

**⚠️ Warning**: This is a critical security action that will:
- Prevent the host from communicating on the network
- Maintain connection only to CrowdStrike cloud
- Log the action in audit logs
- Require manual intervention to restore

#### 4. `lift_containment`
Remove network isolation from a host.

**Parameters:**
- `device_id` (string, required): Device ID to lift containment from

**Example:**
```python
result = await client.lift_containment(device_id="abc123")
```

### Detection Management (3 tools)

#### 5. `query_detections`
Search for detections using FQL filters.

**Parameters:**
- `filter` (string, optional): FQL filter expression
- `limit` (integer, default=100): Maximum results (1-5000)
- `offset` (integer, default=0): Pagination offset
- `sort` (string, optional): Sort field and direction

**Example:**
```python
detections = await client.query_detections(
    filter="status:'new'+severity:['medium','high']",
    limit=50,
    sort="created_timestamp.desc"
)
```

#### 6. `get_detection_details`
Get detailed information about specific detections.

**Parameters:**
- `detection_ids` (array, required): List of detection IDs

**Example:**
```python
details = await client.get_detection_details(
    detection_ids=["ldt:abc123", "ldt:def456"]
)
```

#### 7. `update_detection_status`
Update the status of detections for triage.

**Parameters:**
- `detection_ids` (array, required): List of detection IDs
- `status` (string, required): New status (new, in_progress, true_positive, false_positive, closed, ignored, reopened)
- `comment` (string, optional): Comment explaining the change

**Example:**
```python
result = await client.update_detection_status(
    detection_ids=["ldt:abc123"],
    status="false_positive",
    comment="Benign administrative activity"
)
```

### Incident Management (2 tools)

#### 8. `query_incidents`
Search for incidents using FQL filters.

**Parameters:**
- `filter` (string, optional): FQL filter expression
- `limit` (integer, default=100): Maximum results (1-500)
- `offset` (integer, default=0): Pagination offset
- `sort` (string, optional): Sort field and direction

**Example:**
```python
incidents = await client.query_incidents(
    filter="status:'New'+state:'open'",
    limit=25,
    sort="start.desc"
)
```

#### 9. `get_incident_details`
Get detailed information about specific incidents.

**Parameters:**
- `incident_ids` (array, required): List of incident IDs

**Example:**
```python
details = await client.get_incident_details(
    incident_ids=["inc:abc123"]
)
```

## ⚙️ Configuration

### Environment Variables

Configure via `.env` file or environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FALCON_CLIENT_ID` | Yes | - | CrowdStrike Falcon API Client ID |
| `FALCON_CLIENT_SECRET` | Yes | - | CrowdStrike Falcon API Client Secret |
| `FALCON_BASE_URL` | No | `https://api.crowdstrike.com` | API base URL (region-specific) |
| `SERVER_HOST` | No | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | No | `8001` | Server port |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `ENVIRONMENT` | No | `development` | Environment (development, staging, production) |

### Regional API URLs

- **US-1**: `https://api.crowdstrike.com` (default)
- **US-2**: `https://api.us-2.crowdstrike.com`
- **EU-1**: `https://api.eu-1.crowdstrike.com`
- **US-GOV-1**: `https://api.laggar.gcw.crowdstrike.com`

## 🧪 Development

### Setup Development Environment

```bash
# Install development dependencies
make dev

# Run all quality checks
make all

# Run specific checks
make lint      # Ruff + MyPy
make format    # Black + Ruff --fix
make security  # Bandit + Safety
make test      # Pytest with coverage
```

### Code Quality Standards

This project enforces high code quality standards:

- **Linting**: Ruff with strict rules (E, W, F, I, B, C4, UP, ARG, SIM, PTH, PL, RUF)
- **Formatting**: Black with 88 character line length
- **Type Checking**: MyPy in strict mode with complete type hints
- **Security**: Bandit for security issues, Safety for dependency vulnerabilities
- **Testing**: Pytest with 80%+ coverage requirement
- **Pre-commit**: Automated checks before every commit

### Running Tests

```bash
# Run all tests with coverage
make test

# Run specific test file
pytest tests/test_tools/test_crowdstrike_tools.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
make coverage
open coverage_html/index.html
```

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit:

```bash
# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

## 🐳 Docker Deployment

### Build and Run

```bash
cd docker

# Build image
docker compose build

# Start server
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps

# Stop server
docker compose down
```

### Docker Image Details

- **Base**: Python 3.11-slim
- **Size**: ~180MB (optimized multi-stage build)
- **User**: Non-root (UID 1000)
- **Health Check**: Automatic with `/health` endpoint
- **Logging**: JSON format with log rotation

### Production Deployment

For production deployment on a Linux server:

1. **Install Docker and Docker Compose**:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   ```

2. **Clone and Configure**:
   ```bash
   git clone https://github.com/fjopereira/MCP.git
   cd MCP
   cp .env.example .env
   # Edit .env with production credentials
   ```

3. **Deploy**:
   ```bash
   cd docker
   docker compose up -d
   ```

4. **Verify**:
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8001/ready
   ```

5. **Monitor**:
   ```bash
   docker compose logs -f
   docker stats
   ```

## 📊 Project Structure

```
MCP/
├── src/
│   └── mcp_crowdstrike/
│       ├── __init__.py           # Package initialization
│       ├── config.py             # Configuration management
│       ├── main.py               # FastAPI application
│       ├── server.py             # MCP server implementation
│       ├── sdk.py                # SDK client
│       ├── providers/
│       │   ├── base.py           # Provider interface
│       │   └── crowdstrike.py    # CrowdStrike API integration
│       ├── tools/
│       │   ├── registry.py       # Tool registry
│       │   └── crowdstrike/
│       │       ├── hosts.py      # Host management tools
│       │       ├── detections.py # Detection management tools
│       │       └── incidents.py  # Incident management tools
│       └── utils/
│           ├── logging.py        # Structured logging
│           └── responses.py      # Response formatting
├── tests/
│   ├── conftest.py               # Shared fixtures
│   ├── test_tools/               # Tool tests
│   ├── test_sdk/                 # SDK tests
│   └── test_integration/         # Integration tests
├── docker/
│   ├── Dockerfile                # Multi-stage build
│   └── docker-compose.yml        # Compose configuration
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── .pre-commit-config.yaml       # Pre-commit hooks
├── pyproject.toml                # Project configuration
├── Makefile                      # Development commands
├── setup.sh                      # Linux/Mac setup script
├── setup.bat                     # Windows setup script
└── README.md                     # This file
```

## 🔒 Security

### Security Features

- ✅ **Credential Protection**: SecretStr in Pydantic models prevents accidental logging
- ✅ **HTTPS Enforcement**: API communication over HTTPS only
- ✅ **Token Management**: Automatic token refresh, stored in memory only
- ✅ **Audit Logging**: Critical actions (containment) logged with timestamps
- ✅ **Pre-commit Hooks**: Automatic secret detection before commits
- ✅ **Dependency Scanning**: Safety checks for known vulnerabilities
- ✅ **Code Scanning**: Bandit checks for security anti-patterns
- ✅ **Non-root Docker**: Container runs as non-privileged user

### Best Practices

1. **Never commit credentials**: Use `.env` files (gitignored)
2. **Rotate credentials regularly**: Update API keys periodically
3. **Use least privilege**: Request minimum required API scopes
4. **Monitor logs**: Review audit logs for containment actions
5. **Test in dev first**: Always test in development before production

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and ensure tests pass: `make all`
4. Commit with conventional commits: `git commit -m "feat: add amazing feature"`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `chore:` Build/tooling changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Fábio Pereira**
- GitHub: [@fjopereira](https://github.com/fjopereira)
- Email: fjopereira@users.noreply.github.com

## 🙏 Acknowledgments

- [CrowdStrike FalconPy](https://github.com/CrowdStrike/falconpy) - Official CrowdStrike API SDK
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

---

**Built with ❤️ for security professionals**
