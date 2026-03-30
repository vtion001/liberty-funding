"""Google Sheets API Client"""

import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
from typing import List, Dict
import time
from config.settings import GoogleSheetsConfig


def col_letter(n: int) -> str:
    """Convert 1-indexed column number to Excel letter (1->A, 2->B, ..., 27->AA)"""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


def normalize_header(h: str) -> str:
    """Normalize sheet header for matching (strip newlines, extra spaces)"""
    return h.replace("\n", " ").strip()


def normalize_key(k: str) -> str:
    """Normalize record key to match normalized sheet header (e.g., platform_source -> Platform Source)"""
    return k.replace("_", " ").title()


class GoogleSheetsClient:
    """Client for Google Sheets API"""

    HEADER_ROW = 1

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
        return sheet.get_all_records(head=3)

    def _get_headers(self, sheet) -> List[str]:
        """Get normalized headers from the sheet"""
        raw = sheet.row_values(self.HEADER_ROW)
        return [normalize_header(h) for h in raw]

    def get_email_index(self) -> Dict[str, int]:
        """Build email to row index mapping"""
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)

        headers = self._get_headers(sheet)
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
        Sync data to Google Sheet - update existing by email or append new.
        Batches writes and retries on rate limit errors.
        """
        if not data:
            print("No data to sync")
            return {"updated": 0, "added": 0}

        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)

        headers = self._get_headers(sheet)

        email_col_idx = None
        for idx, header in enumerate(headers):
            if header.lower().replace(" ", "") == self.email_column.lower().replace(
                " ", ""
            ):
                email_col_idx = idx + 1

        if email_col_idx is None:
            raise Exception(f"Email column '{self.email_column}' not found")

        email_map = self.get_email_index()

        rows_to_update = []
        rows_to_add = []

        for record in data:
            email = record.get("email", "").lower().strip()
            if not email:
                continue

            row_idx = email_map.get(email)

            row_data = []
            for header in headers:
                norm_h = header.lower().replace(" ", "")
                value = ""
                for k, v in record.items():
                    norm_k = k.replace("_", " ").title().lower().replace(" ", "")
                    if norm_k == norm_h:
                        value = str(v)
                        break
                row_data.append(value)

            if row_idx:
                rows_to_update.append((row_idx, row_data))
            else:
                rows_to_add.append(row_data)

        print(f"  To update: {len(rows_to_update)}, To add: {len(rows_to_add)}")

        if dry_run:
            for row_idx, row_data in rows_to_update[:3]:
                print(f"  [DRY] Update row {row_idx}: {row_data[3]}")
            for row_data in rows_to_add[:3]:
                print(f"  [DRY] Add row: {row_data[3]}")
            return {"updated": len(rows_to_update), "added": len(rows_to_add)}

        updated = 0
        added = 0

        BATCH_SIZE = 10
        RETRY_MAX = 5
        RETRY_BASE = 5

        for i in range(0, len(rows_to_update), BATCH_SIZE):
            batch = rows_to_update[i : i + BATCH_SIZE]
            for attempt in range(RETRY_MAX):
                try:
                    for row_idx, row_data in batch:
                        num_cols = len(headers)
                        last_col = col_letter(num_cols)
                        sheet.update(f"A{row_idx}:{last_col}{row_idx}", [row_data])
                    updated += len(batch)
                    break
                except gspread.exceptions.APIError as e:
                    if e.response.status_code == 429:
                        wait = RETRY_BASE * (2**attempt)
                        print(f"  Rate limited, retrying in {wait}s...")
                        time.sleep(wait)
                    else:
                        raise
            time.sleep(1)

        for i in range(0, len(rows_to_add), BATCH_SIZE):
            batch = rows_to_add[i : i + BATCH_SIZE]
            for attempt in range(RETRY_MAX):
                try:
                    sheet.append_rows(batch, value_input_option="USER_ENTERED")
                    added += len(batch)
                    break
                except gspread.exceptions.APIError as e:
                    if e.response.status_code == 429:
                        wait = RETRY_BASE * (2**attempt)
                        print(f"  Rate limited, retrying in {wait}s...")
                        time.sleep(wait)
                    else:
                        raise
            time.sleep(2)

        print(f"  Synced: {updated} updated, {added} added")
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

        headers = self._get_headers(sheet)

        existing = sheet.row_values(self.HEADER_ROW)
        if not existing:
            sheet.append_row(headers)

        for record in data:
            row = [record.get(h, "") for h in headers]
            sheet.append_row(row)

        print(f"Appended {len(data)} rows to {self.sheet_name}")
        return len(data)

    def correct_ghl_rows(self, ghl_data: List[Dict], dry_run: bool = False) -> Dict:
        """
        Update existing GHL rows with correct rule IDs and reason values.
        Finds GHL rows in the sheet and updates them with the latest data.
        Returns counts of updated rows.
        """
        if not ghl_data:
            return {"updated": 0}

        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)

        headers = self._get_headers(sheet)
        email_col_idx = None
        plat_col_idx = None

        for idx, header in enumerate(headers):
            h_norm = normalize_header(header).lower().replace(" ", "")
            if h_norm == "email":
                email_col_idx = idx + 1
            if "platformsource" in h_norm or h_norm == "platform":
                plat_col_idx = idx + 1

        if email_col_idx is None:
            raise Exception("Email column not found")
        if plat_col_idx is None:
            raise Exception("PLATFORM SOURCE column not found")

        all_emails = sheet.col_values(email_col_idx)
        all_platforms = sheet.col_values(plat_col_idx)

        email_to_row = {}
        for row_idx, email in enumerate(all_emails[1:], start=2):
            if email:
                email_to_row[email.lower().strip()] = row_idx

        rows_to_update = []
        for record in ghl_data:
            email = record.get("email", "").lower().strip()
            row_idx = email_to_row.get(email)
            if row_idx:
                rows_to_update.append((row_idx, record))

        print(f"  Found {len(rows_to_update)} existing GHL rows to correct")

        if dry_run:
            for row_idx, record in rows_to_update[:3]:
                print(
                    f"  [DRY] Would update row {row_idx}: {record.get('email')} -> {record.get('rule_id')}"
                )
            return {"updated": len(rows_to_update)}

        updated = 0
        BATCH_SIZE = 5
        RETRY_MAX = 5

        for i in range(0, len(rows_to_update), BATCH_SIZE):
            batch = rows_to_update[i : i + BATCH_SIZE]

            for attempt in range(RETRY_MAX):
                try:
                    for row_idx, record in batch:
                        row_data = []
                        for header in headers:
                            norm_h = header.lower().replace(" ", "")
                            value = ""
                            for k, v in record.items():
                                norm_k = (
                                    k.replace("_", " ").title().lower().replace(" ", "")
                                )
                                if norm_k == norm_h:
                                    value = str(v)
                                    break
                            row_data.append(value)

                        num_cols = len(headers)
                        last_col = col_letter(num_cols)
                        sheet.update(f"A{row_idx}:{last_col}{row_idx}", [row_data])

                    updated += len(batch)
                    break
                except gspread.exceptions.APIError as e:
                    if e.response.status_code == 429:
                        wait = 10 * (2**attempt)
                        print(f"  Rate limited, waiting {wait}s...")
                        time.sleep(wait)
                    else:
                        raise

            time.sleep(2)

        print(f"  Corrected {updated} existing GHL rows")
        return {"updated": updated}

    def clear_platform_rows(
        self, platform_keyword: str = "GHL", dry_run: bool = False
    ) -> int:
        """
        Clear rows where PLATFORM SOURCE contains the keyword.
        Uses batch deletion with rate limit retry.
        Returns count of rows cleared.
        """
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        sheet = spreadsheet.worksheet(self.sheet_name)

        headers = self._get_headers(sheet)

        plat_col_idx = None
        for idx, header in enumerate(headers):
            if normalize_header(header).lower().replace(" ", "") in (
                "platformsource",
                "platformsource",
                "platform",
            ):
                plat_col_idx = idx + 1
                break

        if plat_col_idx is None:
            print("  Could not find PLATFORM SOURCE column")
            return 0

        all_values = sheet.col_values(plat_col_idx)
        rows_to_delete = []

        for row_idx, val in enumerate(all_values[1:], start=2):
            if val and platform_keyword.lower() in val.lower():
                rows_to_delete.append(row_idx)

        if dry_run:
            print(
                f"  [DRY RUN] Would delete {len(rows_to_delete)} rows for platform='{platform_keyword}'"
            )
            return len(rows_to_delete)

        deleted = 0
        BATCH = 5
        RETRY_MAX = 5

        for i in range(0, len(rows_to_delete), BATCH):
            batch = rows_to_delete[i : i + BATCH]

            for attempt in range(RETRY_MAX):
                try:
                    for row_idx in reversed(batch):
                        sheet.delete_rows(row_idx)
                        deleted += 1
                    break
                except gspread.exceptions.APIError as e:
                    if e.response.status_code == 429:
                        wait = 10 * (2**attempt)
                        print(f"  Rate limited, waiting {wait}s...")
                        time.sleep(wait)
                    else:
                        raise
                except Exception as e:
                    print(f"  Error on row batch: {e}")
                    break

            time.sleep(2)

        print(
            f"  Cleared {deleted}/{len(rows_to_delete)} rows for platform='{platform_keyword}'"
        )
        return deleted


if __name__ == "__main__":
    client = GoogleSheetsClient()
    print("Connected to Google Sheets")
