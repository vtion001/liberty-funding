#!/usr/bin/env python3
"""
Setup script - Run this first to configure the system
"""
import os
import json
from pathlib import Path

def main():
    print("=" * 60)
    print("Liberty Funding - Setup")
    print("=" * 60)
    print()
    
    # Get configuration
    print("Enter the following information:")
    print()
    
    # Google Sheets
    print("1. GOOGLE SHEETS")
    spreadsheet_id = input("   Spreadsheet ID: ").strip()
    sheet_name = input("   Sheet name (e.g., 'Bounce Rates'): ").strip()
    
    # Get column headers
    print()
    print("2. COLUMN HEADERS (from your Google Sheet)")
    print("   Enter column headers separated by commas:")
    print("   Example: Date, Source, Campaign, Bounce Rate, Sent, Bounced")
    columns = input("   Columns: ").strip()
    column_list = [c.strip() for c in columns.split(",")]
    
    # GoHighLevel
    print()
    print("3. GOHIGHLEVEL API")
    ghl_key = input("   API Key: ").strip()
    
    # Zoho
    print()
    print("4. ZOHO API")
    zoho_key = input("   API Key: ").strip()
    zoho_org = input("   Organization ID: ").strip()
    
    # Save config
    config = {
        "google_sheets": {
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name,
            "columns": column_list
        },
        "gohighlevel": {
            "api_key": ghl_key
        },
        "zoho": {
            "api_key": zoho_key,
            "organization_id": zoho_org
        }
    }
    
    # Write to settings
    settings_content = f'''"""Auto-generated settings"""
import os

PROJECT_ROOT = __file__.parent

class GoHighLevelConfig:
    API_KEY = "{ghl_key}"
    BASE_URL = "https://api.gohighlevel.com"
    TIMEOUT = 30

class ZohoConfig:
    API_KEY = "{zoho_key}"
    ORGANIZATION_ID = "{zoho_org}"
    BASE_URL = "https://www.zohoapis.com"
    TIMEOUT = 30

class GoogleSheetsConfig:
    CREDENTIALS_FILE = str(PROJECT_ROOT / "credentials.json")
    SPREADSHEET_ID = "{spreadsheet_id}"
    SHEET_NAME = "{sheet_name}"
    COLUMNS = {column_list}

DRY_RUN = False
'''
    
    with open("config/settings.py", "w") as f:
        f.write(settings_content)
    
    print()
    print("=" * 60)
    print("Setup complete!")
    print("Edit config/settings.py to modify settings")
    print("Run: python scripts/run.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
