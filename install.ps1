# Liberty Funding - Deploy Script
# Run this in PowerShell as Administrator

param(
    [string]$RepoUrl = "https://github.com/YOUR_USERNAME/liberty-funding.git",
    [string]$InstallPath = "$env:USERPROFILE\liberty-funding"
)

Write-Host "Liberty Funding - Auto Deploy" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Clone or update
if (Test-Path $InstallPath) {
    Write-Host "[1/4] Updating existing installation..." -ForegroundColor Yellow
    Set-Location $InstallPath
    git pull
} else {
    Write-Host "[1/4] Cloning repository..." -ForegroundColor Yellow
    git clone $RepoUrl $InstallPath
    Set-Location $InstallPath
}

# Create virtual environment
Write-Host "[2/4] Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate and install
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt

# Configure
Write-Host "[4/4] Configuration..." -ForegroundColor Yellow
if (!(Test-Path "config\settings.py")) {
    Copy-Item "config\settings.example.py" "config\settings.py"
    Write-Host "Please edit config\settings.py with your API credentials" -ForegroundColor Red
}

Write-Host ""
Write-Host "Done! Run:" -ForegroundColor Green
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "  python scripts\run.py" -ForegroundColor Cyan
