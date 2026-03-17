"""Google Sheets API Client"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict
from datetime import datetime
from config.settings import GoogleSheetsConfig


class GoogleSheetsClient:
    """Client for Google Sheets API"""
    
    def __init__(self, credentials_file: str = None, spreadsheet_id: str = None):
        self.credentials_file = credentials_file or GoogleSheetsConfig.CREDENTIALS_FILE
        self.spreadsheet_id = spreadsheet_id or GoogleSheetsConfig.SPREADSHEET_ID
        self.sheet_name = GoogleSheetsConfig.SHEET_NAME
        
        # Initialize client
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        self.credentials = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=scope
        )
        self.client = gspread.authorize(self.credentials)
    
    def append_data(self, data: List[Dict], dry_run: bool = False) -> int:
        """
        Append data to Google Sheet
        
        Args:
            data: List of records to append
            dry_run: If True, don't actually write
            
        Returns:
            Number of rows added
        """
        if not data:
            print("No data to append")
            return 0
        
        if dry_run:
            print(f"[DRY RUN] Would append {len(data)} rows")
            for row in data:
                print(f"  {row}")
            return len(data)
        
        # Open spreadsheet
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        except gspread.SpreadsheetNotFound:
            raise Exception(f"Spreadsheet not found: {self.spreadsheet_id}")
        
        # Get or create sheet
        try:
            sheet = spreadsheet.worksheet(self.sheet_name)
        except gspread.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(self.sheet_name, rows=1000, cols=10)
        
        # Prepare headers
        headers = list(data[0].keys())
        
        # Check if headers exist
        existing = sheet.row_values(1)
        if not existing:
            sheet.append_row(headers)
        
        # Append data
        for record in data:
            row = [record.get(h, "") for h in headers]
            sheet.append_row(row)
        
        print(f"Appended {len(data)} rows to {self.sheet_name}")
        return len(data)
    
    def get_all_data(self) -> List[Dict]:
        """Get all data from sheet"""
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)
        return sheet.get_all_records()


if __name__ == "__main__":
    client = GoogleSheetsClient()
    # Test connection
    print("Connected to Google Sheets")
