"""Settings and configuration"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)

# API Configuration
class GoHighLevelConfig:
    """GoHighLevel API settings"""
    API_KEY = os.environ.get("GOHIGHLEVEL_API_KEY", "")
    BASE_URL = os.environ.get("GOHIGHLEVEL_BASE_URL", "https://api.gohighlevel.com")
    TIMEOUT = 30

class ZohoConfig:
    """Zoho API settings"""
    API_KEY = os.environ.get("ZOHO_API_KEY", "")
    ORGANIZATION_ID = os.environ.get("ZOHO_ORG_ID", "")
    BASE_URL = os.environ.get("ZOHO_BASE_URL", "https://www.zohoapis.com")
    TIMEOUT = 30

class GoogleSheetsConfig:
    """Google Sheets settings"""
    CREDENTIALS_FILE = os.environ.get(
        "GOOGLE_CREDENTIALS",
        str(PROJECT_ROOT / "credentials.json")
    )
    SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")
    SHEET_NAME = os.environ.get("SHEET_NAME", "Bounce Rates")

# Logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = str(DATA_DIR / "liberty_funding.log")
