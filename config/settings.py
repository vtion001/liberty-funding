"""Settings and configuration"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(exist_ok=True)


class GoHighLevelConfig:
    """GoHighLevel API settings"""

    API_KEY = "pit-7ffb3619-7b11-482f-94bf-af1c319b7e23"
    BASE_URL = "https://api.gohighlevel.com"
    TIMEOUT = 30
    LOCATION_ID = "cyfdRTpFMjTzSBmxBpHk"


class ZohoConfig:
    """Zoho API settings"""

    API_KEY = os.environ.get("ZOHO_API_KEY", "")
    ORGANIZATION_ID = os.environ.get("ZOHO_ORG_ID", "")
    BASE_URL = "https://www.zohoapis.com"
    TIMEOUT = 30


class GoogleSheetsConfig:
    """Google Sheets settings"""

    CREDENTIALS_FILE = str(PROJECT_ROOT / "credentials.json")
    SPREADSHEET_ID = "1qktMN2WAXSXtDNn_UVWe8quJ9ysBjGUDIpWxl45efIA"
    SHEET_NAME = "suppression register"

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
