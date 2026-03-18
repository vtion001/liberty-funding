# Libertad Capital - Windows Installer
# Run this ONE COMMAND to install everything:
#   irm https://raw.githubusercontent.com/vtion001/libertad-capital/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Libertad Capital - Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$RepoURL = "https://github.com/vtion001/liberty-funding"
$InstallPath = "$env:USERPROFILE\libertad-capital"

# 1. Install Git
Write-Host "[1/6] Checking Git..." -ForegroundColor Yellow
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "  Installing Git..." -ForegroundColor Gray
    winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements --silent 2>$null
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}
Write-Host "  OK" -ForegroundColor Green

# 2. Install Python
Write-Host "[2/6] Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "  Installing Python..." -ForegroundColor Gray
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent 2>$null
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Start-Sleep 3
}
Write-Host "  OK" -ForegroundColor Green

# 3. Clone or pull repo
Write-Host "[3/6] Getting project files..." -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    Set-Location $InstallPath
    git pull origin main 2>$null | Out-Null
    Write-Host "  Updated existing installation" -ForegroundColor Green
} else {
    git clone $RepoURL $InstallPath 2>$null | Out-Null
    Set-Location $InstallPath
    Write-Host "  Cloned to $InstallPath" -ForegroundColor Green
}

# 4. Create venv and install deps
Write-Host "[4/6] Setting up Python environment..." -ForegroundColor Yellow
if (-not (Test-Path "$InstallPath\venv")) {
    python -m venv venv
}
& "$InstallPath\venv\Scripts\Activate.ps1" -ErrorAction SilentlyContinue
pip install -q -r requirements.txt
Write-Host "  Done" -ForegroundColor Green

# 5. Create .env if missing
Write-Host "[5/6] Creating configuration..." -ForegroundColor Yellow
$envFile = "$InstallPath\.env"
if (-not (Test-Path $envFile)) {
    Copy-Item "$InstallPath\.env.example" $envFile
    Write-Host "  Created .env - OPEN IT AND FILL IN YOUR API KEYS" -ForegroundColor Magenta
} else {
    Write-Host "  .env already exists" -ForegroundColor Green
}

# 6. Credentials check
Write-Host "[6/6] Checking credentials..." -ForegroundColor Yellow
$credFile = "$InstallPath\credentials.json"
if (-not (Test-Path $credFile)) {
    Write-Host "  MISSING: credentials.json - add it to the project folder" -ForegroundColor Red
} else {
    Write-Host "  OK: credentials.json found" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  INSTALL COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Edit .env with your API keys:" -ForegroundColor White
Write-Host "   notepad $envFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Share your Google Sheet with:" -ForegroundColor White
Write-Host "   libertad-capital-funding@email-marketing-490517.iam.gserviceaccount.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Test run (dry mode, no changes):" -ForegroundColor White
Write-Host "   run-dry.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Full run:" -ForegroundColor White
Write-Host "   run.bat" -ForegroundColor Cyan
Write-Host ""
