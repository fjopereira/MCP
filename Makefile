.PHONY: help install dev lint format security test coverage clean docker-build docker-up docker-down docker-logs all ci

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make dev          - Install development dependencies and pre-commit hooks"
	@echo "  make lint         - Run linting (ruff + mypy)"
	@echo "  make format       - Format code (black + ruff --fix)"
	@echo "  make security     - Run security checks (bandit + safety)"
	@echo "  make test         - Run tests with coverage"
	@echo "  make coverage     - Generate HTML coverage report"
	@echo "  make clean        - Remove cache and build files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker container logs"
	@echo "  make all          - Run format + lint + security + test"
	@echo "  make ci           - Run CI checks (lint + security + test)"

# Install production dependencies
install:
	pip install -e .

# Install development dependencies and setup pre-commit
dev:
	pip install -e ".[dev]"
	pre-commit install
	pre-commit install --hook-type commit-msg

# Run linting
lint:
	@echo "Running ruff..."
	ruff check src tests
	@echo "Running mypy..."
	mypy src

# Format code
format:
	@echo "Running black..."
	black src tests
	@echo "Running ruff --fix..."
	ruff check --fix src tests

# Run security checks
security:
	@echo "Running bandit..."
	bandit -r src -c pyproject.toml
	@echo "Running safety..."
	safety check --json || true

# Run tests with coverage
test:
	pytest

# Generate HTML coverage report
coverage:
	pytest --cov-report=html
	@echo "Coverage report generated at coverage_html/index.html"

# Clean cache and build files
clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage coverage_html dist build

# Docker commands
docker-build:
	cd docker && docker compose build

docker-up:
	cd docker && docker compose up -d

docker-down:
	cd docker && docker compose down

docker-logs:
	cd docker && docker compose logs -f

# Run all checks
all: format lint security test

# CI checks (for continuous integration)
ci: lint security test
