@echo off
REM Setup script for MCP CrowdStrike development environment (Windows)

echo =========================================
echo MCP CrowdStrike - Development Setup
echo =========================================
echo.

REM Check Python version
echo Checking Python version...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% detected
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q .venv
)

python -m venv .venv
echo Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip, setuptools, wheel
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
echo Package managers upgraded
echo.

REM Install project with development dependencies
echo Installing project with development dependencies...
pip install -e ".[dev]"
echo Project installed
echo.

REM Install pre-commit hooks
echo Installing pre-commit hooks...
pre-commit install
pre-commit install --hook-type commit-msg
echo Pre-commit hooks installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo .env file created - Please update with your CrowdStrike credentials
    echo.
) else (
    echo .env file already exists
    echo.
)

echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    .venv\Scripts\activate
echo.
echo 2. Update .env file with your CrowdStrike API credentials
echo.
echo 3. Run tests:
echo    make test
echo.
echo 4. Run linting:
echo    make lint
echo.
echo 5. Run all checks:
echo    make all
echo.
echo For more commands, run: make help
echo.

pause
