# Liberty Funding - Windows Complete Installer
# Save as install.ps1 and run: .\install.ps1

$ErrorActionPreference = "Continue"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Liberty Funding - Complete Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Install Git
Write-Host "[1/6] Installing Git..." -ForegroundColor Yellow
winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements 2>$null
Write-Host "  Done" -ForegroundColor Green

# Install Python
Write-Host "[2/6] Installing Python..." -ForegroundColor Yellow
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements 2>$null
Write-Host "  Done" -ForegroundColor Green

Write-Host ""
Write-Host "  Restart PowerShell if Git/Python not found, then run again" -ForegroundColor Yellow
Write-Host ""

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify
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

if ($git_ok -eq $false -or $python_ok -eq $false) {
    Write-Host "Please restart PowerShell and run script again" -ForegroundColor Yellow
    exit 1
}

# Clone repo
Write-Host "[4/6] Cloning repository..." -ForegroundColor Yellow
$InstallPath = "$env:USERPROFILE\liberty-funding"

if (Test-Path $InstallPath) {
    Write-Host "  Updating..." -ForegroundColor Yellow
    Set-Location $InstallPath
    git pull origin main 2>$null
} else {
    Write-Host "  Cloning..." -ForegroundColor Yellow
    git clone https://github.com/vtion001/liberty-funding.git $InstallPath
    Set-Location $InstallPath
}

# Virtual environment
Write-Host "[5/6] Setting up Python..." -ForegroundColor Yellow
python -m venv venv
& "$InstallPath\venv\Scripts\Activate.ps1"
pip install -q -r requirements.txt

# Credentials
Write-Host "[6/6] Credentials setup..." -ForegroundColor Yellow
$credPath = "$InstallPath\credentials.json"
$envPath = "$InstallPath\.env"

if (-not (Test-Path $credPath)) {
    Write-Host "  Add credentials.json to project folder" -ForegroundColor Yellow
}

if (-not (Test-Path $envPath)) {
    if (Test-Path "$envPath.example") {
        Copy-Item "$envPath.example" $envPath
        Write-Host "  Created .env - edit with API keys" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  DONE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Add credentials.json" -ForegroundColor Cyan
Write-Host "2. Edit .env with API keys" -ForegroundColor Cyan
Write-Host "3. Share Sheet: libertad-capital-funding@...gserviceaccount.com" -ForegroundColor Cyan
Write-Host "4. Run: run.bat" -ForegroundColor Cyan
Write-Host ""
