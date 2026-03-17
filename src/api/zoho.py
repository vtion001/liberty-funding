"""Zoho API Client - Supports Zoho Campaigns for bounce data"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import time
from config.settings import ZohoConfig


class ZohoClient:
    """Client for Zoho Campaigns API"""
    
    CAMPAIGNS_API = "https://campaigns.zoho.com/api/v1"
    
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 org_id: str = None, refresh_token: str = None):
        self.client_id = client_id or ZohoConfig.CLIENT_ID
        self.client_secret = client_secret or ZohoConfig.CLIENT_SECRET
        self.org_id = org_id or ZohoConfig.ORGANIZATION_ID
        self.refresh_token = refresh_token or ZohoConfig.REFRESH_TOKEN
        self.timeout = ZohoConfig.TIMEOUT
        
        self._access_token = None
        self._token_expiry = 0
        self._session = requests.Session()
    
    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        current_time = time.time()
        
        if self._access_token and current_time < self._token_expiry:
            return self._access_token
        
        if not self.refresh_token:
            return None
        
        # Try to get token
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()
                self._access_token = result.get("access_token")
                self._token_expiry = current_time + 3500
                return self._access_token
        except:
            pass
        return None
    
    def get_campaigns(self) -> List[Dict]:
        """Get all campaigns from Zoho Campaigns"""
        
        access_token = self._get_access_token()
        if not access_token:
            print("  ⚠️ No access token!")
            return []
        
        headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
        
        print("  Fetching campaigns from Zoho Campaigns...")
        
        try:
            # Get list of campaigns
            url = f"{self.CAMPAIGNS_API}/campaigns"
            params = {"sort_order": "desc", "range": "50"}
            
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            print(f"    Campaigns status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                campaigns = data.get("campaigns", [])
                print(f"    Found {len(campaigns)} campaigns!")
                return campaigns
            else:
                print(f"    Response: {response.text[:300]}")
                
        except Exception as e:
            print(f"    Error: {e}")
        
        return []
    
    def get_campaign_bounces(self, campaign_id: str = None) -> List[Dict]:
        """Get bounce data for a specific campaign or all"""
        
        access_token = self._get_access_token()
        if not access_token:
            return []
        
        headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
        all_bounces = []
        
        # First get campaigns
        campaigns = self.get_campaigns()
        
        for campaign in campaigns[:10]:  # Limit to recent 10
            campaign_name = campaign.get("campaign_name", "Unknown")
            campaign_id = campaign.get("campaign_key")
            
            print(f"  Checking campaign: {campaign_name}")
            
            try:
                # Get campaign reports/bounces
                url = f"{self.CAMPAIGNS_API}/campaigns/{campaign_id}/reports"
                response = requests.get(url, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract bounce info
                    hard_bounce = data.get("hardbounce_count", 0)
                    soft_bounce = data.get("softbounce_count", 0)
                    total_bounce = data.get("bounce_count", hard_bounce + soft_bounce)
                    
                    print(f"    Bounces: Hard={hard_bounce}, Soft={soft_bounce}")
                    
                    if total_bounce > 0:
                        # Get actual bounced recipients
                        bounce_url = f"{self.CAMPAIGNS_API}/campaigns/{campaign_id}/bounces"
                        bounce_resp = requests.get(bounce_url, headers=headers, timeout=self.timeout)
                        
                        if bounce_resp.status_code == 200:
                            bounce_data = bounce_resp.json()
                            recipients = bounce_data.get("bounced_list", [])
                            
                            for rec in recipients:
                                all_bounces.append({
                                    "date_added": datetime.now().strftime("%m/%d/%Y"),
                                    "platform_source": "Zoho Campaigns",
                                    "contact_id": rec.get("contact_id", ""),
                                    "email": rec.get("email", rec.get("email_address", "")),
                                    "suppression_source": rec.get("bounce_type", "Hard Bounce"),
                                    "reason": rec.get("bounce_reason", ""),
                                    "rule_id": "R-SUP-ZOHO-001",
                                    "suppression_tag": "suppress_zoho_campaign",
                                    "campaign": campaign_name,
                                    "permanent_required": "Yes",
                                    "dnd_required": "Yes",
                                    "workflow_removal_required": "Yes",
                                })
                                
            except Exception as e:
                print(f"    Error: {e}")
                continue
        
        return all_bounces
    
    def get_all_bounced_contacts(self) -> List[Dict]:
        """Get all bounced contacts from campaigns"""
        return self.get_campaign_bounces()
    
    def test_connection(self) -> dict:
        """Test Zoho connection"""
        print("Testing Zoho Campaigns API...")
        
        token = self._get_access_token()
        if token:
            print("  ✅ Connected!")
            return {"success": True}
        else:
            print("  ❌ Failed")
            return {"success": False}


if __name__ == "__main__":
    client = ZohoClient()
    client.test_connection()
    
    # Get bounces
    bounces = client.get_all_bounced_contacts()
    print(f"\nTotal bounces: {len(bounces)}")
    for b in bounces[:5]:
        print(f"  {b.get('email')} - {b.get('reason')}")
