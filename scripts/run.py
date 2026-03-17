#!/usr/bin/env python3
"""
Liberty Funding - Suppression Sync
Main entry point - fetches suppression data from GoHighLevel and syncs to Google Sheets
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.api.gohighlevel import GoHighLevelClient
from src.api.googlesheets import GoogleSheetsClient
from src.utils.logger import logger
from config.settings import DRY_RUN


def main():
    """Main execution"""
    logger.info("=" * 50)
    logger.info("Liberty Funding - Suppression Sync")
    logger.info("=" * 50)

    dry_run = DRY_RUN

    if dry_run:
        logger.info("[DRY RUN MODE - No changes will be made]")

    try:
        logger.info("Fetching suppression data from GoHighLevel...")
        ghl_client = GoHighLevelClient()
        suppression_data = ghl_client.get_all_suppressed_contacts()
        logger.info(f"  Found {len(suppression_data)} suppressed contacts")

        if suppression_data:
            for record in suppression_data[:3]:
                logger.info(
                    f"  Sample: {record.get('email')} - {record.get('suppression_source')}"
                )
            if len(suppression_data) > 3:
                logger.info(f"  ... and {len(suppression_data) - 3} more")

    except Exception as e:
        logger.error(f"  GoHighLevel error: {e}")
        suppression_data = []

    if not suppression_data:
        logger.warning("No suppression data found!")
        return

    logger.info("Syncing to Google Sheet...")
    try:
        sheets_client = GoogleSheetsClient()
        result = sheets_client.sync_data(suppression_data, dry_run=dry_run)
        logger.info(f"  Updated: {result['updated']}, Added: {result['added']}")

    except Exception as e:
        logger.error(f"  Google Sheets error: {e}")
        logger.info("  Data processed but not uploaded. Check credentials.")

    logger.info("=" * 50)
    logger.info("Done!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
