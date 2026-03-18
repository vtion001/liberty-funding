# Libertad Capital - Windows Installation Guide

## Prerequisites

- **Python 3.9+** — [Download from python.org](https://www.python.org/downloads/)
  - During install: **CHECK "Add Python to PATH"**
- **Internet connection**

---

## One-Command Install

Open **PowerShell** and run:

```powershell
irm https://raw.githubusercontent.com/vtion001/liberty-funding/main/install.ps1 | iex
```

This will:
1. Install Git if missing (via winget)
2. Install Python if missing (via winget)
3. Clone/pull the repository to `~\libertad-capital`
4. Create the Python virtual environment
5. Install dependencies
6. Create `.env` from `.env.example`

---

## Manual Install (Step by Step)

### Step 1: Install Python
1. Download from https://www.python.org/downloads/
2. Run installer, **check "Add Python to PATH"**
3. Verify: open PowerShell and type `python --version`

### Step 2: Get the Project
**Option A — Download ZIP:**
1. Go to https://github.com/vtion001/liberty-funding
2. Click **Code** → **Download ZIP**
3. Extract to `C:\libertad-capital\`

**Option B — Git Clone:**
```powershell
git clone https://github.com/vtion001/liberty-funding.git
```

### Step 3: Configure API Keys
1. Open the project folder
2. Copy `.env.example` to `.env`
3. Edit `.env` with your credentials (see API Setup Guide section below)

### Step 4: Google Sheet Setup
1. Create a Google Sheet named "suppression register"
2. Add headers in row 1:
   ```
   DATE ADDED | PLATFORM SOURCE | CONTACT ID | EMAIL | SUPPRESSION SOURCE | REASON | RULE ID | SUPPRESSION TAG | PERMANENT REQUIRED | DND REQUIRED | WORKFLOW REMOVAL REQUIRED
   ```
3. Click **Share** → add this email as **Editor**:
   ```
   libertad-capital-funding@email-marketing-490517.iam.gserviceaccount.com
   ```
4. Copy the spreadsheet ID from the URL:
   `https://docs.google.com/spreadsheets/d/`**`1qktMN2WAXSXtDNn...`**`/edit`
5. Paste it into `.env` as `SPREADSHEET_ID=`

### Step 5: Install Dependencies
```powershell
cd C:\libertad-capital
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 6: Run!
```powershell
run.bat
```

---

## Updating

```powershell
irm https://raw.githubusercontent.com/vtion001/liberty-funding/main/update.ps1 | iex
```

Or manually:
```powershell
cd ~\libertad-capital
git pull origin main
venv\Scripts\activate
pip install -r requirements.txt
```

---

## API Setup Guide

### GoHighLevel Private Integration Token

1. Go to **Settings** → **Private Integrations**
2. Click **Create new Integration**
3. Name it (e.g., "Suppression Sync")
4. Select scopes:
   - `contacts/all` — Read contacts (required)
   - `campaigns/read` — Read campaigns
   - `opportunities/all` — Read opportunities
5. Click **Save** — copy the token immediately (it won't be shown again)
6. Get your **Location ID** from the URL bar when in a sub-account, or from Settings → Business Info

### Zoho OAuth Credentials

1. Go to https://api-console.zoho.com/
2. Create a Server-Based Application
3. Copy **Client ID** and **Client Secret**
4. Generate a **Refresh Token** using the OAuth flow:
   - Authorize: `https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCampaigns.contact.ALL&response_type=code&client_id=YOUR_ID&redirect_uri=https://yourapp.com`
   - Exchange for refresh token at: `https://accounts.zoho.com/oauth/v2/token`

### Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project or select existing: `email-marketing-490517`
3. Go to **IAM & Admin** → **Service Accounts**
4. Create key → download JSON as `credentials.json`
5. Place `credentials.json` in the project root

---

## Troubleshooting

### "Python not found"
- Reinstall Python and check **"Add Python to PATH"**
- Or use full path: `C:\Python312\python.exe`

### "credentials.json not found"
- Make sure the file is in the project folder
- File name must be exactly: `credentials.json`

### "Spreadsheet not found"
- Verify `SPREADSHEET_ID` in `.env`
- Make sure the sheet is shared with the service account email

### "Module not found"
```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

### "401 Unauthorized" on GoHighLevel
- The Private Integration Token may not have the right scopes
- Go back to Settings → Private Integrations and re-create with more scopes

### Dry run first
```powershell
run-dry.bat
```
This runs without writing to the sheet so you can verify data first.
