# Windows Installation Guide

## Prerequisites

### 1. Install Python
- Download Python from: https://www.python.org/downloads/
- **Important:** Check "Add Python to PATH" during installation
- Minimum version: Python 3.9+

### 2. Install Git (Optional)
- Download from: https://git-scm.com/
- Or use Git Bash that comes with Git

---

## Setup Steps

### Step 1: Get the Project Files

**Option A: Using Git**
```bash
git clone <repository-url>
cd liberty-funding
```

**Option B: Download ZIP**
1. Download the project as ZIP
2. Extract to `C:\liberty-funding\`

### Step 2: Get Google Service Account Credentials

1. Get the `credentials.json` file from the project owner
2. Place it in the project folder: `C:\liberty-funding\credentials.json`

### Step 3: Share Google Sheet

1. Open your Google Sheet
2. Click **Share**
3. Add this email (from credentials.json):
   ```
   libertad-capital-funding@email-marketing-490517.iam.gserviceaccount.com
   ```
4. Set as **Editor**
5. Click **Done**

---

## Running the Script

### Option 1: Double-Click (Easiest)

Double-click `run.bat` in File Explorer

### Option 2: Command Prompt

```cmd
cd C:\liberty-funding
run.bat
```

### Option 3: Manual

```cmd
cd C:\liberty-funding

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python scripts\run.py
```

---

## Troubleshooting

### "Python not found"
- Reinstall Python and check "Add to PATH"
- Or use full path: `C:\Python312\python.exe`

### "credentials.json not found"
- Make sure the file is in the project folder
- Check the file name is exactly: `credentials.json`

### "Spreadsheet not found"
- Verify the spreadsheet ID in `config\settings.py`
- Make sure you shared the sheet with the service account

### "Module not found"
- Run: `pip install -r requirements.txt`
- Or: `venv\Scripts\pip install -r requirements.txt`

---

## First Run

The script will:
1. Fetch suppressed contacts from GoHighLevel
2. Sync to Google Sheet "suppression register"
3. Update existing rows by email OR add new rows

**Test first (dry run):**
```cmd
set DRY_RUN=true
run.bat
```

**Run for real:**
```cmd
run.bat
```

---

## Configuration

To change settings, edit `config\settings.py`:

```python
# GoHighLevel
API_KEY = "your-api-key"
LOCATION_ID = "your-location-id"

# Google Sheets
SPREADSHEET_ID = "your-spreadsheet-id"
SHEET_NAME = "suppression register"
```
