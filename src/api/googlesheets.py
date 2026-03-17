"""Google Sheets API Client"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
from datetime import datetime
from config.settings import GoogleSheetsConfig


class GoogleSheetsClient:
    """Client for Google Sheets API"""

    def __init__(
        self,
        credentials_file: str = None,
        spreadsheet_id: str = None,
        sheet_name: str = None,
    ):
        self.credentials_file = credentials_file or GoogleSheetsConfig.CREDENTIALS_FILE
        self.spreadsheet_id = spreadsheet_id or GoogleSheetsConfig.SPREADSHEET_ID
        self.sheet_name = sheet_name or GoogleSheetsConfig.SHEET_NAME
        self.email_column = GoogleSheetsConfig.EMAIL_COLUMN

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        self.credentials = Credentials.from_service_account_file(
            self.credentials_file, scopes=scope
        )
        self.client = gspread.authorize(self.credentials)

    def get_all_data(self) -> List[Dict]:
        """Get all data from sheet"""
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)
        return sheet.get_all_records()

    def get_email_index(self) -> Dict[str, int]:
        """Build email to row index mapping"""
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)

        headers = sheet.row_values(1)
        email_col_idx = None

        for idx, header in enumerate(headers):
            if header.lower().replace(" ", "") == self.email_column.lower().replace(
                " ", ""
            ):
                email_col_idx = idx + 1
                break

        if email_col_idx is None:
            raise Exception(f"Email column '{self.email_column}' not found in sheet")

        all_values = sheet.col_values(email_col_idx)
        email_map = {}

        for row_idx, email in enumerate(all_values[1:], start=2):
            if email:
                email_map[email.lower().strip()] = row_idx

        return email_map

    def sync_data(self, data: List[Dict], dry_run: bool = False) -> Dict:
        """
        Sync data to Google Sheet - update existing by email or append new

        Args:
            data: List of records to sync
            dry_run: If True, don't actually write

        Returns:
            Dict with 'updated' and 'added' counts
        """
        if not data:
            print("No data to sync")
            return {"updated": 0, "added": 0}

        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)

        headers = sheet.row_values(1)

        email_col_idx = None
        for idx, header in enumerate(headers):
            if header.lower().replace(" ", "") == self.email_column.lower().replace(
                " ", ""
            ):
                email_col_idx = idx + 1
                break

        if email_col_idx is None:
            raise Exception(f"Email column '{self.email_column}' not found")

        email_map = self.get_email_index()

        updated = 0
        added = 0

        for record in data:
            email = record.get("email", "").lower().strip()

            if not email:
                continue

            row_idx = email_map.get(email)

            row_data = []
            for header in headers:
                value = record.get(header, "")
                row_data.append(str(value))

            if row_idx:
                if dry_run:
                    print(f"[DRY RUN] Would update row {row_idx} for {email}")
                else:
                    sheet.update(f"A{row_idx}:K{row_idx}", [row_data])
                updated += 1
            else:
                if dry_run:
                    print(f"[DRY RUN] Would append new row for {email}")
                else:
                    sheet.append_row(row_data)
                    email_map[email] = sheet.row_count
                added += 1

        print(f"Synced: {updated} updated, {added} added")
        return {"updated": updated, "added": added}

    def append_data(self, data: List[Dict], dry_run: bool = False) -> int:
        """Legacy method - append data to Google Sheet"""
        if not data:
            print("No data to append")
            return 0

        if dry_run:
            print(f"[DRY RUN] Would append {len(data)} rows")
            for row in data:
                print(f"  {row}")
            return len(data)

        spreadsheet = self.client.open_by_key(self.spreadsheet_id)

        try:
            sheet = spreadsheet.worksheet(self.sheet_name)
        except gspread.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(self.sheet_name, rows=1000, cols=11)

        headers = list(data[0].keys())

        existing = sheet.row_values(1)
        if not existing:
            sheet.append_row(headers)

        for record in data:
            row = [record.get(h, "") for h in headers]
            sheet.append_row(row)

        print(f"Appended {len(data)} rows to {self.sheet_name}")
        return len(data)


if __name__ == "__main__":
    client = GoogleSheetsClient()
    print("Connected to Google Sheets")
