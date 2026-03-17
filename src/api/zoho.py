"""Zoho API Client - Supports both Zoho Mail and Zoho CRM"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import time
from config.settings import ZohoConfig


class ZohoClient:
    """Client for Zoho Mail/CRM API using OAuth2"""
    
    # Different API endpoints for Zoho products
    ZOHO_ACCOUNTS = {
        "mail": "https://accounts.zoho.com",
        "crm": "https://accounts.zoho.com", 
        "workdrive": "https://accounts.zoho.com"
    }
    
    ZOHO_APIS = {
        "mail": "https://mail.zoho.com",
        "crm": "https://www.zohoapis.com/crm",
        "workdrive": "https://www.zohoapis.com/workdrive"
    }
    
    def __init__(self, product: str = "mail", client_id: str = None, client_secret: str = None, 
                 org_id: str = None, refresh_token: str = None):
        self.product = product
        self.client_id = client_id or ZohoConfig.CLIENT_ID
        self.client_secret = client_secret or ZohoConfig.CLIENT_SECRET
        self.org_id = org_id or ZohoConfig.ORGANIZATION_ID
        self.refresh_token = refresh_token or ZohoConfig.REFRESH_TOKEN
        self.timeout = ZohoConfig.TIMEOUT
        
        self._access_token = None
        self._token_expiry = 0
        self._session = requests.Session()
    
    @property
    def accounts_url(self) -> str:
        return self.ZOHO_ACCOUNTS.get(self.product, self.ZOHO_ACCOUNTS["mail"])
    
    @property
    def api_url(self) -> str:
        return self.ZOHO_APIS.get(self.product, self.ZOHO_APIS["mail"])
    
    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        current_time = time.time()
        
        # Return cached token if still valid
        if self._access_token and current_time < self._token_expiry:
            return self._access_token
        
        if not self.refresh_token:
            return None
        
        # Refresh the token
        token_url = f"{self.accounts_url}/oauth/v2/token"
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=self.timeout)
            print(f"    Token request status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                self._token_expiry = current_time + 3500
                print(f"    ✅ Got access token!")
                return self._access_token
            else:
                print(f"    Token error: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"    Exception: {e}")
            return None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make authenticated request"""
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Zoho-oauthtoken {access_token}"
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers
        
        # Use full URL if endpoint starts with http
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = f"{self.api_url}{endpoint}"
        
        print(f"    Requesting: {method} {url}")
        return self._session.request(method, url, timeout=self.timeout, **kwargs)
    
    def get_bounced_contacts(self, limit: int = 100) -> List[Dict]:
        """Get bounced email contacts from Zoho"""
        
        if not self.refresh_token:
            print("  ⚠️ No refresh token configured!")
            return []
        
        all_records = []
        
        # Try different approaches for bounce data
        approaches = [
            # Zoho Mail API
            {"product": "mail", "endpoint": "/api/v1/mails/bounced", "params": {"limit": limit}},
            {"product": "mail", "endpoint": "/api/v1/bounces", "params": {"limit": limit}},
            # Zoho CRM API
            {"product": "crm", "endpoint": "/crm/v2/functions/email_bounce/actions/ invoke", "params": {}},
            {"product": "crm", "endpoint": "/crm/v2/Contacts", "params": {"limit": limit, "sort_by": "modified_time", "sort_order": "desc"}},
        ]
        
        for approach in approaches:
            product = approach["product"]
            endpoint = approach["endpoint"]
            params = approach.get("params", {})
            
            print(f"  Trying {product}: {endpoint}")
            
            # Create temporary client for this product
            temp_client = ZohoClient(
                product=product,
                client_id=self.client_id,
                client_secret=self.client_secret,
                refresh_token=self.refresh_token
            )
            
            response = temp_client._make_request("GET", endpoint, params=params)
            
            if response is None:
                continue
            
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Different parsing for different APIs
                if product == "mail":
                    records = data.get("data") or data.get("bounces") or []
                else:  # CRM
                    records = data.get("data") or []
                
                if records:
                    print(f"    Found {len(records)} records!")
                    for item in records:
                        record = self._process_bounce(item, product)
                        if record:
                            all_records.append(record)
                    break
            elif response.status_code == 401:
                print("    Unauthorized")
                break
            elif response.status_code == 404:
                print("    Not found")
                continue
            else:
                print(f"    Response: {response.text[:100]}")
        
        if not all_records:
            print("  ⚠️ No bounce data found!")
            print("  Note: Zoho API requires proper scopes.")
            print("  For Zoho Mail: ZohoMail.messages.READ")
            print("  For Zoho CRM: ZohoCRM.modules.contacts.READ")
        
        return all_records[:limit]
    
    def _process_bounce(self, item: dict, product: str = "mail") -> Optional[Dict]:
        """Process raw bounce data"""
        # Try different email field names
        email = (
            item.get("emailAddress") or 
            item.get("email") or 
            item.get("sender") or
            item.get("bouncedEmail") or
            item.get("Contact_Email") or
            item.get("Email")
        )
        
        if not email:
            return None
        
        reason = item.get("reason") or item.get("bounceReason") or item.get("Description") or "Unknown"
        
        record = {
            "date_added": datetime.now().strftime("%m/%d/%Y"),
            "platform_source": f"Zoho {product.title()}",
            "contact_id": item.get("id") or item.get("Contact_Id") or "",
            "email": email,
            "suppression_source": "Bounce",
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
        print(f"  Product: {self.product}")
        
        # Try to get access token
        token = self._get_access_token()
        if token:
            print("  ✅ Access token obtained!")
            return {"success": True, "token": token[:20] + "..."}
        else:
            print("  ❌ Failed to get access token")
            return {"success": False, "error": "Token exchange failed"}


if __name__ == "__main__":
    # Test both mail and CRM
    for product in ["mail", "crm"]:
        print(f"\n=== Testing Zoho {product} ===")
        client = ZohoClient(product=product)
        client.test_connection()
