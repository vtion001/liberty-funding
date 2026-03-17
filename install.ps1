# Liberty Funding - Windows Installer
# Run this in PowerShell

param(
    [string]$InstallPath = "$env:USERPROFILE\liberty-funding"
)

$ErrorActionPreference = "Stop"

Write-Host "Liberty Funding - Installer" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "  IMPORTANT: Check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Create install directory
Write-Host ""
Write-Host "Creating installation directory..." -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    Write-Host "  Directory exists, pulling latest..." -ForegroundColor Yellow
    Set-Location $InstallPath
    git pull origin main 2>$null
} else {
    Write-Host "  Cloning repository..." -ForegroundColor Yellow
    git clone https://github.com/vtion001/liberty-funding.git $InstallPath
    Set-Location $InstallPath
}

# Copy credentials
Write-Host ""
Write-Host "Setup credentials.json..." -ForegroundColor Yellow
$credPath = "$InstallPath\credentials.json"
if (-not (Test-Path $credPath)) {
    Write-Host "  WARNING: credentials.json not found!" -ForegroundColor Yellow
    Write-Host "  Please place your Google service account JSON file in:" -ForegroundColor Yellow
    Write-Host "  $credPath" -ForegroundColor Cyan
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate and install
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& "$InstallPath\venv\Scripts\Activate.ps1"
pip install -q -r requirements.txt

Write-Host ""
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Add credentials.json to $InstallPath" -ForegroundColor Cyan
Write-Host "2. Share your Google Sheet with:" -ForegroundColor Cyan
Write-Host "   libertad-capital-funding@email-marketing-490517.iam.gserviceaccount.com" -ForegroundColor Cyan
Write-Host "3. Run: run.bat" -ForegroundColor Cyan
Write-Host ""
