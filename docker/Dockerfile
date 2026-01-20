# Multi-stage Dockerfile for MCP CrowdStrike
# Optimized for production deployment with minimal image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies and build wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --wheel-dir /wheels .

# Stage 2: Runtime
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Fábio Pereira <fjopereira@users.noreply.github.com>"
LABEL description="MCP Server for CrowdStrike Falcon API"
LABEL version="0.1.0"

# Create non-root user
RUN groupadd -r mcp && \
    useradd -r -g mcp -u 1000 -m -s /sbin/nologin mcp

# Set working directory
WORKDIR /app

# Install runtime dependencies (curl for health checks)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /wheels /wheels

# Install Python packages from wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

# Copy application source
COPY --chown=mcp:mcp src/ /app/src/

# Set Python path
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Switch to non-root user
USER mcp

# Run the application
CMD ["python", "-m", "uvicorn", "mcp_crowdstrike.main:app", "--host", "0.0.0.0", "--port", "8001"]
