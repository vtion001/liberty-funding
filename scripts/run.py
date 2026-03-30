#!/usr/bin/env python3
"""
Libertad Capital - Suppression Sync
Fetches suppression data from multiple GoHighLevel locations, tags by source, syncs to Google Sheets
"""

import sys
import os
import argparse

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pathlib import Path
from dotenv import load_dotenv
from src.api.gohighlevel import GoHighLevelClient
from src.api.googlesheets import GoogleSheetsClient
from src.utils.logger import logger

load_dotenv(Path(project_root) / ".env")


def main():
    parser = argparse.ArgumentParser(description="Libertad Capital - Suppression Sync")
    parser.add_argument("--clear", action="store_true", help="Clear existing rows for the platform before syncing")
    parser.add_argument("--platform", default="all", choices=["GHL", "Zoho", "all"], help="Platform to clear when --clear is used")
    parser.add_argument("--dry", action="store_true", help="Dry run - no changes written to Google Sheets")
    parser.add_argument("--skip-ghl", action="store_true", help="Skip GoHighLevel fetch")
    parser.add_argument("--skip-zoho", action="store_true", help="Skip Zoho fetch")
    parser.add_argument("--account", help="Only run for specific account number (e.g. '1' or '2')")
    args = parser.parse_args()

    dry_run = args.dry

    logger.info("=" * 50)
    logger.info("  Libertad Capital - Suppression Sync")
    logger.info("=" * 50)

    if dry_run:
        logger.info("[DRY RUN MODE - No changes will be made]")

    # Get list of active accounts
    active_raw = os.environ.get("ACTIVE_GHL_ACCOUNTS", "1")
    active_accounts = [a.strip() for a in active_raw.split(",")]

    # Filter by --account flag if specified
    if args.account:
        active_accounts = [a for a in active_accounts if a == args.account]

    all_suppression_data = []

    # ========== FETCH FROM GOHIGHLEVEL ==========
    if not args.skip_ghl:
        for account_num in active_accounts:
            api_key = os.environ.get(f"GOHIGHLEVEL_API_KEY_{account_num}")
            location_id = os.environ.get(f"GHL_LOCATION_ID_{account_num}")
            source_name = os.environ.get(f"GHL_SOURCE_NAME_{account_num}", f"GHL_{account_num}")

            if not api_key or not location_id:
                logger.warning(f"  Account {account_num} not fully configured, skipping")
                continue

            logger.info(f"Fetching from {source_name} ({location_id[:8]}...)...")
            try:
                ghl_client = GoHighLevelClient(
                    api_key=api_key,
                    location_id=location_id,
                    source_name=source_name
                )
                ghl_data = ghl_client.get_all_suppressed_contacts()
                logger.info(f"  Found {len(ghl_data)} suppressed contacts")

                if ghl_data:
                    reasons = {}
                    for r in ghl_data:
                        key = r.get("reason", "Unknown")
                        reasons[key] = reasons.get(key, 0) + 1
                    logger.info(f"  Breakdown: {reasons}")

                all_suppression_data.extend(ghl_data)

            except Exception as e:
                logger.error(f"  {source_name} error: {e}")

    # ========== FETCH FROM ZOHO (disabled) ==========
    if not args.skip_zoho:
        logger.info("Zoho is currently disabled")
        # try:
        #     zoho_client = ZohoClient()
        #     zoho_data = zoho_client.get_all_bounced_contacts()
        #     logger.info(f"  Found {len(zoho_data)} bounced contacts from Zoho")
        #     all_suppression_data.extend(zoho_data)
        # except Exception as e:
        #     logger.error(f"  Zoho error: {e}")

    # ========== CHECK DATA ==========
    if not all_suppression_data:
        logger.warning("No suppression data found!")
        return

    logger.info(f"Total records to sync: {len(all_suppression_data)}")

    # ========== SYNC TO GOOGLE SHEETS ==========
    logger.info("Syncing to Google Sheet...")
    try:
        sheets_client = GoogleSheetsClient()
        result = sheets_client.sync_data(all_suppression_data, dry_run=dry_run)
        logger.info(f"  Synced: Updated={result['updated']}, Added={result['added']}")
    except Exception as e:
        logger.error(f"  Google Sheets error: {e}")

    logger.info("=" * 50)
    logger.info("Done!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
