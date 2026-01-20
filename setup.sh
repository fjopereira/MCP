#!/bin/bash
# Setup script for MCP CrowdStrike development environment (Linux/Mac)

set -e

echo "========================================="
echo "MCP CrowdStrike - Development Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi

python3 -m venv .venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip, setuptools, wheel
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel
echo "✓ Package managers upgraded"
echo ""

# Install project with development dependencies
echo "Installing project with development dependencies..."
pip install -e ".[dev]"
echo "✓ Project installed"
echo ""

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg
echo "✓ Pre-commit hooks installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created - Please update with your CrowdStrike credentials"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Update .env file with your CrowdStrike API credentials"
echo ""
echo "3. Run tests:"
echo "   make test"
echo ""
echo "4. Run linting:"
echo "   make lint"
echo ""
echo "5. Run all checks:"
echo "   make all"
echo ""
echo "For more commands, run: make help"
echo ""
