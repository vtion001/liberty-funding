# Liberty Funding - Bounce Rate Automation

Automated bounce rate data collection from GoHighLevel and Zoho to Google Sheets.

## Project Structure

```
liberty-funding/
├── config/
│   └── settings.py          # Configuration
├── src/
│   ├── api/
│   │   ├── gohighlevel.py   # GoHighLevel API client
│   │   ├── zoho.py          # Zoho API client
│   │   └── googlesheets.py  # Google Sheets client
│   ├── processors/
│   │   └── data_processor.py # Data processing
│   └── utils/
│       └── logger.py         # Logging
├── scripts/
│   └── run.py               # Main entry point
├── tests/                   # Unit tests
├── requirements.txt
└── run.bat                  # Windows launcher
```

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure:
   - Copy `config/settings.example.py` to `config/settings.py`
   - Add API credentials

3. Run:
   ```
   python scripts/run.py
   ```

## Modules

| Module | Purpose |
|--------|---------|
| `api/gohighlevel.py` | Fetch bounce rate from GoHighLevel |
| `api/zoho.py` | Fetch bounce rate from Zoho |
| `api/googlesheets.py` | Update Google Sheet |
| `processors/data_processor.py` | Combine and format data |

## Requirements

- Python 3.9+
- See requirements.txt
