#!/usr/bin/env python3
"""
Liberty Funding - Bounce Rate Automation
Main entry point
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.api.gohighlevel import GoHighLevelClient
from src.api.zoho import ZohoClient
from src.api.googlesheets import GoogleSheetsClient
from src.processors.data_processor import DataProcessor
from src.utils.logger import logger
from config.settings import GoogleSheetsConfig


def main():
    """Main execution"""
    logger.info("=" * 50)
    logger.info("Liberty Funding - Bounce Rate Update")
    logger.info("=" * 50)
    
    try:
        # Step 1: Fetch GoHighLevel data
        logger.info("Fetching GoHighLevel data...")
        ghl_client = GoHighLevelClient()
        ghl_data = ghl_client.get_all_bounce_data()
        logger.info(f"  Got {len(ghl_data)} records from GoHighLevel")
        
    except Exception as e:
        logger.warning(f"  GoHighLevel error: {e}")
        ghl_data = []
    
    try:
        # Step 2: Fetch Zoho data
        logger.info("Fetching Zoho data...")
        zoho_client = ZohoClient()
        zoho_data = zoho_client.get_all_bounce_data()
        logger.info(f"  Got {len(zoho_data)} records from Zoho")
        
    except Exception as e:
        logger.warning(f"  Zoho error: {e}")
        zoho_data = []
    
    # Step 3: Process data
    logger.info("Processing data...")
    processor = DataProcessor()
    processed = processor.process(ghl_data, zoho_data)
    logger.info(f"  Processed {len(processed)} records")
    
    # Print summary
    summary = processor.get_summary()
    logger.info(f"Summary: {summary}")
    
    if not processed:
        logger.warning("No data to update!")
        return
    
    # Step 4: Update Google Sheet
    logger.info("Updating Google Sheet...")
    try:
        sheets_client = GoogleSheetsClient()
        rows = sheets_client.append_data(processed)
        logger.info(f"  Added {rows} rows to sheet")
        
    except Exception as e:
        logger.error(f"  Google Sheets error: {e}")
        logger.info("  Data processed but not uploaded. Check credentials.")
    
    logger.info("=" * 50)
    logger.info("Done!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
