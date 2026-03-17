"""GoHighLevel API Client"""
import requests
from typing import Dict, List, Optional
from config.settings import GoHighLevelConfig


class GoHighLevelClient:
    """Client for GoHighLevel API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GoHighLevelConfig.API_KEY
        self.base_url = GoHighLevelConfig.BASE_URL
        self.timeout = GoHighLevelConfig.TIMEOUT
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def get_bounce_rate(self, campaign_id: str = None) -> List[Dict]:
        """
        Get bounce rate data from GoHighLevel
        
        Args:
            campaign_id: Optional campaign ID to filter
            
        Returns:
            List of bounce rate records
        """
        # Example endpoint - adjust based on actual GoHighLevel API
        endpoint = f"{self.base_url}/v1/campaigns"
        
        try:
            response = self._session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Process and return bounce rate data
            return self._process_bounce_data(data)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"GoHighLevel API error: {e}")
    
    def _process_bounce_data(self, data: dict) -> List[Dict]:
        """Process raw API data into standardized format"""
        records = []
        
        campaigns = data.get("campaigns", [])
        for campaign in campaigns:
            record = {
                "source": "gohighlevel",
                "campaign_id": campaign.get("id"),
                "campaign_name": campaign.get("name"),
                "bounce_rate": campaign.get("bounce_rate", 0),
                "sent_count": campaign.get("sent", 0),
                "bounce_count": campaign.get("bounced", 0),
                "timestamp": campaign.get("created_at")
            }
            records.append(record)
        
        return records
    
    def get_all_bounce_data(self) -> List[Dict]:
        """Get all bounce rate data"""
        return self.get_bounce_rate()


if __name__ == "__main__":
    client = GoHighLevelClient()
    data = client.get_all_bounce_data()
    print(f"Got {len(data)} records")
