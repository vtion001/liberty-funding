"""Settings and configuration"""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")


class GoHighLevelConfig:
    """GoHighLevel API settings"""

    API_KEY = os.environ.get("GOHIGHLEVEL_API_KEY", "")
    BASE_URL = "https://services.leadconnectorhq.com"
    API_VERSION = "2021-07-28"
    TIMEOUT = 60
    LOCATION_ID = os.environ.get("GOHIGHLEVEL_LOCATION_ID", "")


class ZohoConfig:
    """Zoho OAuth2 API settings"""

    CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID", "")
    CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET", "")
    ORGANIZATION_ID = os.environ.get("ZOHO_ORG_ID", "")
    REFRESH_TOKEN = os.environ.get("ZOHO_REFRESH_TOKEN", "")
    BASE_URL = "https://mail.zoho.com"
    API_BASE = "https://api.zoho.com"
    TIMEOUT = 30


class GoogleSheetsConfig:
    """Google Sheets settings"""

    CREDENTIALS_FILE = os.environ.get(
        "GOOGLE_CREDENTIALS", str(PROJECT_ROOT / "credentials.json")
    )
    SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")
    SHEET_NAME = os.environ.get("SHEET_NAME", "suppression register")

    COLUMN_MAPPING = {
        "date_added": "DATE ADDED",
        "platform_source": "PLATFORM SOURCE",
        "contact_id": "CONTACT ID",
        "email": "EMAIL",
        "suppression_source": "SUPPRESSION SOURCE",
        "reason": "REASON",
        "rule_id": "RULE ID",
        "suppression_tag": "SUPPRESSION TAG",
        "permanent_required": "PERMANENT REQUIRED",
        "dnd_required": "DND REQUIRED",
        "workflow_removal_required": "WORKFLOW REMOVAL REQUIRED",
    }

    EMAIL_COLUMN = "EMAIL"


LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = str(DATA_DIR / "liberty_funding.log")

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
