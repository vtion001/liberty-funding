@echo off
title Libertad Capital - Dry Run (Test Mode)
echo.
echo ============================================
echo   Libertad Capital - DRY RUN (Test Mode)
echo ============================================
echo   No changes will be written to Google Sheet
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Install Python 3.9+ from https://python.org
    echo.
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Create venv if missing
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo [2/3] Activating environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo [3/3] Installing dependencies...
pip install -q -r requirements.txt

echo.
echo Running in DRY RUN mode...
echo.

set DRY_RUN=true
python scripts\run.py

echo.
pause
