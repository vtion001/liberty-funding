"""Zoho API Client"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
from config.settings import ZohoConfig


class ZohoClient:
    """Client for Zoho Mail API"""
    
    def __init__(self, api_key: str = None, org_id: str = None):
        self.api_key = api_key or ZohoConfig.API_KEY
        self.org_id = org_id or ZohoConfig.ORGANIZATION_ID
        self.base_url = ZohoConfig.BASE_URL
        self.timeout = ZohoConfig.TIMEOUT
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Zoho-oauthtoken {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def get_bounce_rate(self, campaign_id: str = None) -> List[Dict]:
        """
        Get bounce rate from Zoho Mail
        
        Args:
            campaign_id: Optional campaign ID to filter
            
        Returns:
            List of bounce rate records
        """
        # Example endpoint - adjust based on actual Zoho API
        endpoint = f"{self.base_url}/api/v1/campaigns"
        
        try:
            response = self._session.get(
                endpoint, 
                timeout=self.timeout,
                params={"org_id": self.org_id} if self.org_id else {}
            )
            response.raise_for_status()
            data = response.json()
            
            return self._process_bounce_data(data)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Zoho API error: {e}")
    
    def _process_bounce_data(self, data: dict) -> List[Dict]:
        """Process raw API data into standardized format"""
        records = []
        
        campaigns = data.get("campaigns", [])
        for campaign in campaigns:
            record = {
                "source": "zoho",
                "campaign_id": campaign.get("id"),
                "campaign_name": campaign.get("campaign_name"),
                "bounce_rate": campaign.get("bounce_percentage", 0),
                "sent_count": campaign.get("total_sent", 0),
                "bounce_count": campaign.get("bounced", 0),
                "timestamp": campaign.get("sent_time")
            }
            records.append(record)
        
        return records
    
    def get_all_bounce_data(self) -> List[Dict]:
        """Get all bounce rate data"""
        return self.get_bounce_rate()


if __name__ == "__main__":
    client = ZohoClient()
    data = client.get_all_bounce_data()
    print(f"Got {len(data)} records")
