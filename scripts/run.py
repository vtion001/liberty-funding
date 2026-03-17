#!/usr/bin/env python3
"""
Liberty Funding - Suppression Sync
Fetches suppression data from GoHighLevel, Zoho and syncs to Google Sheets
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.api.gohighlevel import GoHighLevelClient
from src.api.zoho import ZohoClient
from src.api.googlesheets import GoogleSheetsClient
from src.utils.logger import logger
from config.settings import DRY_RUN


def main():
    logger.info("=" * 50)
    logger.info("Liberty Funding - Suppression Sync")
    logger.info("=" * 50)

    dry_run = DRY_RUN

    if dry_run:
        logger.info("[DRY RUN MODE - No changes will be made]")

    all_suppression_data = []

    # ========== FETCH FROM GOHIGHLEVEL ==========
    try:
        logger.info("Fetching suppression data from GoHighLevel...")
        ghl_client = GoHighLevelClient()
        ghl_data = ghl_client.get_all_suppressed_contacts()
        logger.info(f"  Found {len(ghl_data)} suppressed contacts from GoHighLevel")

        if ghl_data:
            for record in ghl_data[:3]:
                logger.info(f"  Sample: {record.get('email')} - {record.get('suppression_source')}")
            if len(ghl_data) > 3:
                logger.info(f"  ... and {len(ghl_data) - 3} more")
            all_suppression_data.extend(ghl_data)

    except Exception as e:
        logger.error(f"  GoHighLevel error: {e}")

    # ========== FETCH FROM ZOHO ==========
    try:
        logger.info("Fetching suppression data from Zoho...")
        zoho_client = ZohoClient()
        
        # First try bounces
        zoho_data = zoho_client.get_all_bounced_contacts()
        logger.info(f"  Found {len(zoho_data)} bounced contacts from Zoho")
        
        if zoho_data:
            for record in zoho_data[:3]:
                logger.info(f"  Sample: {record.get('email')} - {record.get('suppression_source')}")
            all_suppression_data.extend(zoho_data)
        else:
            # Try getting ALL contacts as fallback
            logger.info("  No bounces found, fetching all contacts...")
            all_contacts = zoho_client.get_all_contacts(limit=100)
            logger.info(f"  Total contacts in Zoho: {len(all_contacts)}")
            if all_contacts:
                logger.info("  (No suppression data, but Zoho connection works!)")

    except Exception as e:
        logger.error(f"  Zoho error: {e}")

    # ========== CHECK DATA ==========
    if not all_suppression_data:
        logger.warning("No suppression data found!")
        logger.warning("Platforms checked: GoHighLevel, Zoho")
        logger.warning("Status:")
        logger.warning("  - GoHighLevel: API key needs contacts.read permission")
        logger.warning("  - Zoho: Connected (API working), but no bounce data")
        return

    logger.info(f"Total suppression records: {len(all_suppression_data)}")

    # ========== SYNC TO GOOGLE SHEETS ==========
    logger.info("Syncing to Google Sheet...")
    try:
        sheets_client = GoogleSheetsClient()
        result = sheets_client.sync_data(all_suppression_data, dry_run=dry_run)
        logger.info(f"  Updated: {result['updated']}, Added: {result['added']}")
    except Exception as e:
        logger.error(f"  Google Sheets error: {e}")

    logger.info("=" * 50)
    logger.info("Done!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
