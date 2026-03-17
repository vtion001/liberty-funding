"""Zoho API Client - OAuth2 based"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import time
from config.settings import ZohoConfig


class ZohoClient:
    """Client for Zoho Mail API using OAuth2"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 org_id: str = None, refresh_token: str = None):
        self.client_id = client_id or ZohoConfig.CLIENT_ID
        self.client_secret = client_secret or ZohoConfig.CLIENT_SECRET
        self.org_id = org_id or ZohoConfig.ORGANIZATION_ID
        self.refresh_token = refresh_token or ZohoConfig.REFRESH_TOKEN
        self.base_url = ZohoConfig.BASE_URL
        self.api_base = ZohoConfig.API_BASE
        self.timeout = ZohoConfig.TIMEOUT
        
        self._access_token = None
        self._token_expiry = 0
        self._session = requests.Session()
    
    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        current_time = time.time()
        
        # Return cached token if still valid
        if self._access_token and current_time < self._token_expiry:
            return self._access_token
        
        if not self.refresh_token:
            print("  ⚠️ No refresh token configured!")
            print("  To get a refresh token:")
            print("  1. Go to https://api-console.zoho.com/")
            print("  2. Create a Server-side app")
            print("  3. Add scopes: ZohoMail.messages.READ, ZohoMail.organization.READ")
            print("  4. Generate Grant Token and exchange for Refresh Token")
            return None
        
        # Refresh the token
        token_url = f"{self.api_base}/oauth/v2/token"
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=self.timeout)
            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                # Zoho access tokens expire in 3600 seconds
                self._token_expiry = current_time + 3500
                return self._access_token
            else:
                print(f"  Token refresh error: {response.status_code}")
                print(f"  {response.text[:200]}")
                return None
        except Exception as e:
            print(f"  Exception getting token: {e}")
            return None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request"""
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Zoho-oauthtoken {access_token}"
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers
        
        url = f"{self.base_url}{endpoint}"
        return self._session.request(method, url, timeout=self.timeout, **kwargs)
    
    def get_bounced_contacts(self, limit: int = 100) -> List[Dict]:
        """
        Get bounced email contacts from Zoho Mail
        
        Returns:
            List of bounced contact records
        """
        if not self.refresh_token:
            print("  ⚠️ Zoho refresh token not configured!")
            print("  Please provide Zoho refresh token in .env")
            return []
        
        all_records = []
        
        # Try different endpoints for bounce data
        endpoints = [
            "/api/v1/mails/bounced",
            "/api/v1/bounces",
            "/api/v1/statistics/bounces",
        ]
        
        for endpoint in endpoints:
            print(f"  Trying: {endpoint}")
            
            try:
                # Try GET first
                response = self._make_request(
                    "GET", 
                    endpoint,
                    params={"limit": min(100, limit)}
                )
                
                if response is None:
                    break
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("data") or data.get("bounces") or data.get("list") or []
                    
                    if records:
                        for item in records:
                            record = self._process_bounce(item)
                            if record:
                                all_records.append(record)
                        break
                elif response.status_code == 401:
                    print("    Unauthorized - token may be expired")
                    break
                elif response.status_code == 404:
                    print("    Not found - trying next endpoint")
                    continue
                else:
                    print(f"    Response: {response.text[:100]}")
                    
            except Exception as e:
                print(f"    Exception: {e}")
                continue
        
        if not all_records:
            print("  No bounce data found!")
            print("  Note: Zoho API may require specific organization access")
        
        return all_records[:limit]
    
    def _process_bounce(self, item: dict) -> Optional[Dict]:
        """Process raw bounce data"""
        # Try different email field names
        email = (
            item.get("emailAddress") or 
            item.get("email") or 
            item.get("sender") or
            item.get("bouncedEmail")
        )
        
        if not email:
            return None
        
        reason = item.get("reason") or item.get("bounceReason") or "Unknown"
        
        # Determine bounce type
        is_hard = "hard" in str(reason).lower() if reason else False
        
        record = {
            "date_added": datetime.now().strftime("%m/%d/%Y"),
            "platform_source": "Zoho Mail",
            "contact_id": item.get("id", ""),
            "email": email,
            "suppression_source": "Hard Bounce" if is_hard else "Bounce",
            "reason": reason,
            "rule_id": "R-SUP-ZOHO-001",
            "suppression_tag": "suppress_zoho_bounce",
            "permanent_required": "Yes",
            "dnd_required": "Yes",
            "workflow_removal_required": "Yes",
        }
        
        return record
    
    def get_all_bounced_contacts(self) -> List[Dict]:
        """Get all bounced contacts"""
        return self.get_bounced_contacts(limit=500)
    
    def test_connection(self) -> dict:
        """Test Zoho API connection"""
        print("Testing Zoho API connection...")
        print(f"  Client ID: {self.client_id[:20]}...")
        
        if not self.refresh_token:
            print("  ⚠️ No refresh token configured!")
            return {"success": False, "error": "No refresh token"}
        
        # Try to get access token
        token = self._get_access_token()
        if token:
            print("  ✅ Access token obtained")
            return {"success": True}
        else:
            print("  ❌ Failed to get access token")
            return {"success": False, "error": "Token exchange failed"}


if __name__ == "__main__":
    client = ZohoClient()
    data = client.get_all_bounced_contacts()
    print(f"Got {len(data)} bounced contacts")
