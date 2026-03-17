"""Zoho API Client - Fetches contacts and checks for suppression status"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import time
from config.settings import ZohoConfig


class ZohoClient:
    """Client for Zoho Mail/CRM API using OAuth2"""
    
    ZOHO_ACCOUNTS = {
        "mail": "https://accounts.zoho.com",
        "crm": "https://accounts.zoho.com", 
    }
    
    ZOHO_APIS = {
        "mail": "https://mail.zoho.com",
        "crm": "https://www.zohoapis.com/crm",
    }
    
    def __init__(self, product: str = "crm", client_id: str = None, client_secret: str = None, 
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
        return self.ZOHO_ACCOUNTS.get(self.product, self.ZOHO_ACCOUNTS["crm"])
    
    @property
    def api_url(self) -> str:
        return self.ZOHO_APIS.get(self.product, self.ZOHO_APIS["crm"])
    
    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        current_time = time.time()
        
        if self._access_token and current_time < self._token_expiry:
            return self._access_token
        
        if not self.refresh_token:
            return None
        
        token_url = f"{self.accounts_url}/oauth/v2/token"
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
                self._token_expiry = current_time + 3500
                return self._access_token
        except:
            pass
        return None
    
    def get_all_contacts(self, limit: int = 200) -> List[Dict]:
        """Get ALL contacts from Zoho CRM"""
        
        access_token = self._get_access_token()
        if not access_token:
            print("  ⚠️ No access token!")
            return []
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }
        
        all_contacts = []
        
        # Get contacts from CRM
        print(f"  Fetching contacts from Zoho CRM...")
        
        try:
            url = f"{self.api_url}/v2/Contacts"
            params = {"per_page": min(200, limit)}
            
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("data", [])
                print(f"    Found {len(contacts)} contacts!")
                
                for contact in contacts:
                    record = self._process_contact(contact)
                    if record:
                        all_contacts.append(record)
                        
        except Exception as e:
            print(f"    Error: {e}")
        
        return all_contacts
    
    def _process_contact(self, contact: dict) -> Optional[Dict]:
        """Process contact and check for suppression indicators"""
        
        # Get email
        email = (
            contact.get("Email") or 
            contact.get("email") or
            contact.get("Contact_Email") or
            # Try nested structure
            contact.get("Email", {}).get("value") if isinstance(contact.get("Email"), dict) else None
        )
        
        if not email:
            return None
        
        # Check for suppression indicators
        suppression_source = None
        reason = None
        rule_id = None
        suppression_tag = None
        
        # Check various fields for suppression status
        status = str(contact.get("Status", "")).lower() if contact.get("Status") else ""
        lead_status = str(contact.get("Lead_Status", "")).lower() if contact.get("Lead_Status") else ""
        
        # Check custom fields
        for key, value in contact.items():
            if value and isinstance(value, str):
                value_lower = value.lower()
                if "bounce" in value_lower or "hard bounce" in value_lower:
                    suppression_source = "Hard Bounce"
                    reason = value
                    rule_id = "R-SUP-ZOHO-001"
                    suppression_tag = "suppress_bounce"
                    break
                elif "unsubscrib" in value_lower:
                    suppression_source = "Unsubscribed"
                    reason = value
                    rule_id = "R-SUP-ZOHO-002"
                    suppression_tag = "suppress_unsubscribed"
                    break
                elif "invalid" in value_lower and "email" in value_lower:
                    suppression_source = "Invalid Email"
                    reason = value
                    rule_id = "R-SUP-ZOHO-003"
                    suppression_tag = "suppress_invalid"
                    break
        
        # If no specific suppression, check if contact should be suppressed
        if not suppression_source:
            # For now, we'll return all contacts but mark as "Active"
            # Only return contacts that have suppression indicators
            return None
        
        record = {
            "date_added": datetime.now().strftime("%m/%d/%Y"),
            "platform_source": "Zoho CRM",
            "contact_id": contact.get("id") or contact.get("id") or "",
            "email": email,
            "suppression_source": suppression_source,
            "reason": reason,
            "rule_id": rule_id,
            "suppression_tag": suppression_tag,
            "permanent_required": "Yes",
            "dnd_required": "Yes",
            "workflow_removal_required": "Yes",
        }
        
        return record
    
    def get_all_bounced_contacts(self) -> List[Dict]:
        """Get all contacts with bounce/suppression status"""
        return self.get_all_contacts(limit=500)
    
    def test_connection(self) -> dict:
        """Test Zoho API connection"""
        print("Testing Zoho API connection...")
        
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
    data = client.get_all_bounced_contacts()
    print(f"Total: {len(data)}")
