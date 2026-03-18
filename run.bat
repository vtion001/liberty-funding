@echo off
title Libertad Capital - Suppression Sync
echo.
echo ============================================
echo   Libertad Capital - Suppression Sync
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Install Python 3.9+ from https://python.org
    echo Make sure to check "Add Python to PATH" during install.
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
echo [3/3] Checking dependencies...
pip install -q -r requirements.txt 2>nul

echo.
echo Running suppression sync...
echo.

REM Check for --clear flag
set CLEAR_FLAG=
set PLATFORM_FLAG=

if /i "%1"=="--clear" (
    set CLEAR_FLAG=--clear
    set PLATFORM_FLAG=%~2
    if defined PLATFORM_FLAG (
        echo [WARNING] Clearing existing records for: %PLATFORM_FLAG%
    ) else (
        echo [WARNING] Clearing existing records for: GHL
    )
    echo.
)

python scripts\run.py %CLEAR_FLAG% %PLATFORM_FLAG%

echo.
echo Done. Press any key to close.
pause >nul
