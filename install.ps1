# Liberty Funding - Windows Complete Installer
# Run this in PowerShell (as Administrator for best results)

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Liberty Funding - Complete Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Install Git and Python using winget
Write-Host "[1/6] Installing Git..." -ForegroundColor Yellow
winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements 2>$null
if ($?) { Write-Host "  Git installed!" -ForegroundColor Green } 
else { Write-Host "  Could not install Git automatically" -ForegroundColor Yellow }

Write-Host "[2/6] Installing Python..." -ForegroundColor Yellow
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements 2>$null
if ($?) { Write-Host "  Python installed!" -ForegroundColor Green }
else { Write-Host "  Could not install Python automatically" -ForegroundColor Yellow }

Write-Host ""
Write-Host "  IMPORTANT: Restart PowerShell to use Git/Python" -ForegroundColor Yellow
Write-Host "  Then run this script again" -ForegroundColor Yellow
Write-Host ""

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify installations
Write-Host "[3/6] Verifying installations..." -ForegroundColor Yellow

$git_ok = $false
$python_ok = $false

try { 
    $gitVersion = & git --version 2>&1
    if ($gitVersion -match "git") { 
        Write-Host "  Git: $gitVersion" -ForegroundColor Green
        $git_ok = $true
    }
} catch { Write-Host "  Git: Not found" -ForegroundColor Red }

try { 
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python") { 
        Write-Host "  Python: $pythonVersion" -ForegroundColor Green
        $python_ok = $true
    }
} catch { Write-Host "  Python: Not found" -ForegroundColor Red }

if (-not $git_ok -or -not $python_ok) {
    Write-Host ""
    Write-Host "Please restart PowerShell and run this script again" -ForegroundColor Yellow
    exit 1
}

# Clone repo
Write-Host "[4/6] Cloning repository..." -ForegroundColor Yellow
$InstallPath = "$env:USERPROFILE\liberty-funding"

if (Test-Path $InstallPath) {
    Write-Host "  Updating existing installation..." -ForegroundColor Yellow
    Set-Location $InstallPath
    git pull origin main 2>$null
} else {
    Write-Host "  Cloning to $InstallPath..." -ForegroundColor Yellow
    git clone https://github.com/vtion001/liberty-funding.git $InstallPath
    Set-Location $InstallPath
}

# Create virtual environment
Write-Host "[5/6] Setting up Python environment..." -ForegroundColor Yellow
python -m venv venv
& "$InstallPath\venv\Scripts\Activate.ps1"
pip install -q -r requirements.txt

# Setup credentials
Write-Host "[6/6] Setup credentials..." -ForegroundColor Yellow
$credPath = "$InstallPath\credentials.json"
$envPath = "$InstallPath\.env"

if (-not (Test-Path $credPath)) {
    Write-Host "  Add credentials.json to: $credPath" -ForegroundColor Yellow
}

if (-not (Test-Path $envPath)) {
    if (Test-Path "$envPath.example") {
        Copy-Item "$envPath.example" $envPath
        Write-Host "  Created .env - edit it with your API keys" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Installation complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Add credentials.json to project folder" -ForegroundColor Cyan
Write-Host "2. Edit .env with your API keys" -ForegroundColor Cyan
Write-Host "3. Share Google Sheet with:" -ForegroundColor Cyan
Write-Host "   libertad-capital-funding@...gserviceaccount.com" -ForegroundColor Cyan
Write-Host "4. Run: run.bat" -ForegroundColor Cyan
Write-Host ""
