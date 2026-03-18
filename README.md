# Libertad Capital - Suppression Sync

Automated suppression/bounce data collection from GoHighLevel and Zoho to Google Sheets.

## What It Does

1. **Fetches** suppressed contacts (bounces, unsubscribes, invalid emails) from GoHighLevel and Zoho
2. **Deduplicates** and merges records by email
3. **Syncs** to Google Sheet — updates existing rows or adds new ones

## Quick Start (Windows)

### 1. Install in one command
```powershell
irm https://raw.githubusercontent.com/vtion001/liberty-funding/main/install.ps1 | iex
```

### 2. Configure
Edit the `.env` file created by the installer with your API keys.

### 3. Run
```
run.bat
```

### 4. Test first (no changes written)
```
run-dry.bat
```

## Quick Start (macOS / Linux)

```bash
# Clone
git clone https://github.com/vtion001/liberty-funding.git
cd libertad-capital

# Install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
./run.sh
```

## Project Structure

```
libertad-capital/
├── .env                      # API credentials (DO NOT commit)
├── .env.example              # Template - copy to .env
├── credentials.json           # Google service account (from GCP)
├── requirements.txt
├── run.bat                   # Windows launcher
├── run-dry.bat               # Windows test mode (dry run)
├── run.sh                    # macOS/Linux launcher
├── install.ps1               # Windows installer (IRM)
├── update.ps1                # Windows updater (IRM)
├── config/
│   └── settings.py            # Reads .env
├── src/
│   ├── api/
│   │   ├── gohighlevel.py    # GHL suppressed contacts
│   │   ├── zoho.py           # Zoho Campaigns bounces
│   │   └── googlesheets.py   # Sheet sync
│   └── utils/
│       └── logger.py          # Logging
├── scripts/
│   └── run.py                # Main entry point
└── tests/
```

## Requirements

- Python 3.9+
- Google Cloud service account (credentials.json)
- Google Sheet shared with the service account email
- GoHighLevel Private Integration Token
- Zoho OAuth credentials (optional)

## Google Sheet Setup

1. Create a sheet with tab named `suppression register`
2. Add these headers in row 1:
   - DATE ADDED | PLATFORM SOURCE | CONTACT ID | EMAIL | SUPPRESSION SOURCE | REASON | RULE ID | SUPPRESSION TAG | PERMANENT REQUIRED | DND REQUIRED | WORKFLOW REMOVAL REQUIRED
3. Share the sheet with:
   ```
   libertad-capital-funding@email-marketing-490517.iam.gserviceaccount.com
   ```
4. Copy the spreadsheet ID from the URL and put it in `.env`

## Updating

**Windows:**
```powershell
irm https://raw.githubusercontent.com/vtion001/liberty-funding/main/update.ps1 | iex
```

**macOS/Linux:**
```bash
cd libertad-capital && git pull origin main && pip install -r requirements.txt
```

## Dry Run Mode

Tests the sync without writing to the sheet:
- `run-dry.bat` (Windows)
- `DRY_RUN=true python3 scripts/run.py` (manual)
