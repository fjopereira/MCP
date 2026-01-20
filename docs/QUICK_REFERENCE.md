# Quick Reference Guide

## Before Starting

### Prerequisites on Your Server
- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] Git (optional, for version control)
- [ ] At least 1GB free disk space
- [ ] Port 8001 available

### What You'll Need
- [ ] CrowdStrike API credentials (Client ID + Secret)
- [ ] About 30-60 minutes for Claude to generate everything

---

## Step-by-Step Process

### 1. Connect to Your Server
```bash
ssh your-server
```

### 2. Create Project Directory
```bash
mkdir -p ~/projects/mcp-crowdstrike-server
cd ~/projects/mcp-crowdstrike-server
```

### 3. Open Claude (CLI or Web)
```bash
claude  # if using Claude CLI
```

### 4. Paste the Prompt
Copy the entire content from `PROMPT_FOR_SERVER_CLAUDE.md` and paste it.

### 5. Wait for Generation
Claude will create all files. This may take several messages.

### 6. After Generation - Create .env File
```bash
cp .env.example .env
nano .env  # or vim .env
```

Fill in your credentials:
```bash
FALCON_CLIENT_ID=your-actual-client-id
FALCON_CLIENT_SECRET=your-actual-client-secret
```

### 7. Build and Run
```bash
cd docker
docker compose build
docker compose up -d
```

### 8. Verify It's Running
```bash
# Check container status
docker compose ps

# Check logs
docker compose logs -f

# Test health endpoint
curl http://localhost:8001/health
```

---

## Testing the Server

### Test 1: Health Check
```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy"}
```

### Test 2: List Available Tools
```bash
curl http://localhost:8001/mcp/v1/tools | jq .
```

### Test 3: Execute a Tool (Query Devices)
```bash
curl -X POST http://localhost:8001/mcp/v1/tools/query_devices_by_filter \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'
```

### Test 4: Get Device Details
```bash
# First, get a device ID from the previous response
# Then:
curl -X POST http://localhost:8001/mcp/v1/tools/get_device_details \
  -H "Content-Type: application/json" \
  -d '{"device_ids": ["<device-id-from-previous-response>"]}'
```

---

## Code Quality Commands

After Claude generates the project, verify code quality:

```bash
# Install dev dependencies
make dev

# Run all checks
make all

# Individual checks
make lint      # Ruff + mypy
make format    # Black + Ruff fix
make security  # Bandit + Safety
make test      # Pytest with coverage
```

### Expected Output
```
$ make test
========================= test session starts =========================
collected 25 items

tests/test_tools/test_hosts.py ........                          [ 32%]
tests/test_tools/test_detections.py ......                       [ 56%]
tests/test_sdk/test_sdk_client.py ...........                    [100%]

---------- coverage: platform linux, python 3.11.0 ----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/mcp_crowdstrike/__init__.py            5      0   100%
src/mcp_crowdstrike/config.py             25      2    92%
...
-----------------------------------------------------------
TOTAL                                    320     40    87%

========================= 25 passed in 4.32s =========================
```

---

## SDK Usage (Optional Testing)

If you want to test the SDK directly in Python:

```python
# test_sdk.py
import asyncio
from mcp_crowdstrike import CrowdStrikeClient

async def main():
    client = CrowdStrikeClient(
        client_id="your-id",
        client_secret="your-secret"
    )
    
    # Query devices
    result = await client.query_devices_by_filter(
        filter="platform_name:'Windows'",
        limit=5
    )
    print(result)

asyncio.run(main())
```

```bash
python test_sdk.py
```

---

## Share with Your Friend for Testing

Send them this information:

```
MCP Server for CrowdStrike is running!

Endpoint: http://<your-server-ip>:8001

Available endpoints:
- GET  /health                    - Health check
- GET  /mcp/v1/tools             - List all tools
- POST /mcp/v1/tools/{tool_name} - Execute a tool

Example - List tools:
curl http://<your-server-ip>:8001/mcp/v1/tools

Example - Query devices:
curl -X POST http://<your-server-ip>:8001/mcp/v1/tools/query_devices_by_filter \
  -H "Content-Type: application/json" \
  -d '{"filter": "platform_name:Windows", "limit": 10}'
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs mcp-crowdstrike

# Common issues:
# - Missing .env file
# - Invalid credentials
# - Port already in use
```

### Authentication errors
```bash
# Verify credentials are loaded
docker compose exec mcp-crowdstrike env | grep FALCON

# Test credentials directly
curl -X POST https://api.crowdstrike.com/oauth2/token \
  -d "client_id=YOUR_ID&client_secret=YOUR_SECRET"
```

### Port conflict
```bash
# Change port in docker-compose.yml
ports:
  - "8002:8001"  # Use 8002 instead
```

### Need to rebuild
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## Cleanup (If Needed)

### Stop the service
```bash
docker compose down
```

### Remove everything
```bash
docker compose down --rmi all --volumes
cd ..
rm -rf mcp-crowdstrike-server
```

---

## Files Summary

After Claude generates everything, you should have:

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python project config + all tool configs |
| `.pre-commit-config.yaml` | Git hooks configuration |
| `Makefile` | Command shortcuts (lint, test, etc.) |
| `src/mcp_crowdstrike/__init__.py` | SDK public exports |
| `src/mcp_crowdstrike/main.py` | FastAPI entry point |
| `src/mcp_crowdstrike/config.py` | Settings management |
| `src/mcp_crowdstrike/server.py` | MCP protocol handling |
| `src/mcp_crowdstrike/sdk.py` | SDK client class |
| `src/mcp_crowdstrike/providers/` | CrowdStrike client wrapper |
| `src/mcp_crowdstrike/tools/` | Tool implementations |
| `tests/` | Unit and integration tests |
| `docker/Dockerfile` | Container build (multi-stage) |
| `docker/docker-compose.yml` | Service orchestration |
| `README.md` | Documentation with SDK examples |

---

## Success Criteria

You're done when:
- [ ] `curl /health` returns `{"status":"healthy"}`
- [ ] `curl /mcp/v1/tools` returns list of tools
- [ ] A tool execution returns data from CrowdStrike
- [ ] `make lint` passes without errors
- [ ] `make test` passes with 80%+ coverage
- [ ] `make security` shows no critical issues
- [ ] Your friend can connect and test remotely

## Bonus Points (For the Interview)

If you have time, these will impress:
- [ ] Set up pre-commit hooks: `pre-commit install`
- [ ] Run full CI check: `make ci`
- [ ] Test SDK usage directly in Python
- [ ] Show them the coverage HTML report: `make coverage`
