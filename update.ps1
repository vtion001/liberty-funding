# Libertad Capital - Update Script
# Run this ONE COMMAND to update:
#   irm https://raw.githubusercontent.com/vtion001/liberty-funding/main/update.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Libertad Capital - Updater" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$InstallPath = "$env:USERPROFILE\libertad-capital"

if (-not (Test-Path $InstallPath)) {
    Write-Host "ERROR: Project not found at $InstallPath" -ForegroundColor Red
    Write-Host "Run the installer first:" -ForegroundColor Yellow
    Write-Host "  irm https://raw.githubusercontent.com/vtion001/liberty-funding/main/install.ps1 | iex" -ForegroundColor Cyan
    exit 1
}

Set-Location $InstallPath

Write-Host "Pulling latest updates..." -ForegroundColor Yellow
git pull origin main 2>$null | Out-Null

Write-Host "Updating dependencies..." -ForegroundColor Yellow
& "$InstallPath\venv\Scripts\Activate.ps1" -ErrorAction SilentlyContinue
pip install -q -r requirements.txt

Write-Host ""
Write-Host "READY!" -ForegroundColor Green
Write-Host "  run-dry.bat  (test mode)" -ForegroundColor Cyan
Write-Host "  run.bat      (full run)" -ForegroundColor Cyan
Write-Host ""
