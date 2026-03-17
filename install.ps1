# Liberty Funding - Windows Installer
# Run this in PowerShell

param(
    [string]$InstallPath = "$env:USERPROFILE\liberty-funding"
)

$ErrorActionPreference = "Continue"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Liberty Funding - Installer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check for prerequisites
$prereqs_ok = $true

# Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python") {
        Write-Host "  Found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Not found"
    }
} catch {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "  IMPORTANT: Check 'Add Python to PATH' during install" -ForegroundColor Yellow
    $prereqs_ok = $false
}

# Check Git
Write-Host "[2/5] Checking Git..." -ForegroundColor Yellow
try {
    $gitVersion = & git --version 2>&1
    if ($gitVersion -match "git") {
        Write-Host "  Found: $gitVersion" -ForegroundColor Green
    } else {
        throw "Not found"
    }
} catch {
    Write-Host "  ERROR: Git not found!" -ForegroundColor Red
    Write-Host "  Download: https://git-scm.com/" -ForegroundColor Cyan
    $prereqs_ok = $false
}

if (-not $prereqs_ok) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "  Please install missing prerequisites above" -ForegroundColor Red
    Write-Host "  Then run this script again" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    exit 1
}

# Clone repo
Write-Host "[3/5] Cloning repository..." -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    Write-Host "  Directory exists, updating..." -ForegroundColor Yellow
    Set-Location $InstallPath
    git pull origin main 2>$null
} else {
    Write-Host "  Cloning to $InstallPath..." -ForegroundColor Yellow
    git clone https://github.com/vtion001/liberty-funding.git $InstallPath
    Set-Location $InstallPath
}

# Create virtual environment
Write-Host "[4/5] Setting up Python environment..." -ForegroundColor Yellow
python -m venv venv
& "$InstallPath\venv\Scripts\Activate.ps1"
pip install -q -r requirements.txt

# Credentials
Write-Host "[5/5] Setup credentials..." -ForegroundColor Yellow
$credPath = "$InstallPath\credentials.json"
$envPath = "$InstallPath\.env"

if (-not (Test-Path $credPath)) {
    Write-Host "  WARNING: credentials.json not found!" -ForegroundColor Yellow
    Write-Host "  Copy your Google service account JSON file to:" -ForegroundColor Yellow
    Write-Host "  $credPath" -ForegroundColor Cyan
}

if (-not (Test-Path $envPath)) {
    Write-Host "  WARNING: .env not found!" -ForegroundColor Yellow
    if (Test-Path "$envPath.example") {
        Copy-Item "$envPath.example" $envPath
        Write-Host "  Created .env from template" -ForegroundColor Green
        Write-Host "  Edit $envPath with your API keys" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Installation complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Add credentials.json to the folder" -ForegroundColor Cyan
Write-Host "2. Edit .env with your API keys" -ForegroundColor Cyan
Write-Host "3. Share Google Sheet with:" -ForegroundColor Cyan
Write-Host "   libertad-capital-funding@email-marketing-490517.iam.gserviceaccount.com" -ForegroundColor Cyan
Write-Host "4. Run: run.bat" -ForegroundColor Cyan
Write-Host ""
