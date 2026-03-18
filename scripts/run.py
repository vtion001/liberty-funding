#!/usr/bin/env python3
"""
Libertad Capital - Suppression Sync
Fetches suppression data from GoHighLevel, Zoho and syncs to Google Sheets
"""

import sys
import os
import argparse

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.api.gohighlevel import GoHighLevelClient
from src.api.zoho import ZohoClient
from src.api.googlesheets import GoogleSheetsClient
from src.utils.logger import logger


def main():
    parser = argparse.ArgumentParser(description="Libertad Capital - Suppression Sync")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing rows for the platform before syncing (WARNING: deletes rows!)",
    )
    parser.add_argument(
        "--platform",
        default="GHL",
        choices=["GHL", "Zoho", "all"],
        help="Platform to clear when --clear is used (default: GHL)",
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        help="Dry run - no changes written to Google Sheets",
    )
    parser.add_argument(
        "--skip-ghl",
        action="store_true",
        help="Skip GoHighLevel fetch",
    )
    parser.add_argument(
        "--skip-zoho",
        action="store_true",
        help="Skip Zoho fetch",
    )
    args = parser.parse_args()

    dry_run = args.dry

    logger.info("=" * 50)
    logger.info("  Libertad Capital - Suppression Sync")
    logger.info("=" * 50)

    if dry_run:
        logger.info("[DRY RUN MODE - No changes will be made]")

    if args.clear:
        if dry_run:
            logger.info(f"[DRY RUN] Would clear rows for: {args.platform}")
        else:
            try:
                sheets_client = GoogleSheetsClient()
                if args.platform in ("GHL", "all"):
                    deleted = sheets_client.clear_platform_rows("GHL", dry_run=dry_run)
                    logger.info(f"  Cleared {deleted} GHL rows")
                if args.platform in ("Zoho", "all"):
                    deleted = sheets_client.clear_platform_rows("Zoho", dry_run=dry_run)
                    logger.info(f"  Cleared {deleted} Zoho rows")
            except Exception as e:
                logger.error(f"  Clear error: {e}")

    all_suppression_data = []

    # ========== FETCH FROM GOHIGHLEVEL ==========
    if not args.skip_ghl:
        try:
            logger.info("Fetching suppression data from GoHighLevel...")
            ghl_client = GoHighLevelClient()
            ghl_data = ghl_client.get_all_suppressed_contacts()
            logger.info(f"  Found {len(ghl_data)} suppressed contacts")

            if ghl_data:
                reasons = {}
                for r in ghl_data:
                    reasons[r.get("reason", "Unknown")] = (
                        reasons.get(r.get("reason", "Unknown"), 0) + 1
                    )
                logger.info(f"  Breakdown: {reasons}")

            all_suppression_data.extend(ghl_data)

        except Exception as e:
            logger.error(f"  GoHighLevel error: {e}")

    # ========== FETCH FROM ZOHO ==========
    if not args.skip_zoho:
        try:
            logger.info("Fetching suppression data from Zoho...")
            zoho_client = ZohoClient()

            zoho_data = zoho_client.get_all_bounced_contacts()
            logger.info(f"  Found {len(zoho_data)} bounced contacts from Zoho")

            if zoho_data:
                reasons = {}
                for r in zoho_data:
                    reasons[r.get("reason", "Unknown")] = (
                        reasons.get(r.get("reason", "Unknown"), 0) + 1
                    )
                logger.info(f"  Breakdown: {reasons}")

            all_suppression_data.extend(zoho_data)

        except Exception as e:
            logger.error(f"  Zoho error: {e}")

    # ========== CHECK DATA ==========
    if not all_suppression_data:
        logger.warning("No suppression data found!")
        return

    logger.info(f"Total records to sync: {len(all_suppression_data)}")

    # ========== SYNC TO GOOGLE SHEETS ==========
    logger.info("Syncing to Google Sheet...")
    try:
        sheets_client = GoogleSheetsClient()

        if ghl_data:
            logger.info("  Correcting existing GHL rows with updated rule IDs...")
            corrected = sheets_client.correct_ghl_rows(ghl_data, dry_run=dry_run)
            logger.info(f"  Corrected: {corrected['updated']} rows")

        result = sheets_client.sync_data(all_suppression_data, dry_run=dry_run)
        logger.info(f"  Synced: Updated={result['updated']}, Added={result['added']}")
    except Exception as e:
        logger.error(f"  Google Sheets error: {e}")

    logger.info("=" * 50)
    logger.info("Done!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
