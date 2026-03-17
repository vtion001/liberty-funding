# Liberty Funding - Update Script
# Run this to pull latest updates from GitHub
# Usage: irm https://raw.githubusercontent.com/vtion001/liberty-funding/main/update.ps1 | iex

$ErrorActionPreference = "Continue"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Liberty Funding - Update" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$InstallPath = "$env:USERPROFILE\liberty-funding"

if (-not (Test-Path $InstallPath)) {
    Write-Host "Repository not found at: $InstallPath" -ForegroundColor Red
    Write-Host "Run install script first:" -ForegroundColor Yellow
    Write-Host "  irm https://raw.githubusercontent.com/vtion001/liberty-funding/main/install.ps1 | iex" -ForegroundColor Cyan
    exit 1
}

Write-Host "Pulling latest updates..." -ForegroundColor Yellow
Set-Location $InstallPath

# Refresh PATH to find git
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

try {
    git pull origin main
    Write-Host "Updates pulled successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error pulling updates: $_" -ForegroundColor Red
}

# Update dependencies if requirements changed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
& "$InstallPath\venv\Scripts\Activate.ps1" 2>$null
pip install -q -r requirements.txt 2>$null

Write-Host ""
Write-Host "Ready to run!" -ForegroundColor Green
Write-Host "  run.bat" -ForegroundColor Cyan
Write-Host ""
