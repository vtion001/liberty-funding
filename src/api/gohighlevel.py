"""GoHighLevel API Client - Fixed endpoints"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
from config.settings import GoHighLevelConfig


class GoHighLevelClient:
    """Client for GoHighLevel API"""

    def __init__(self, api_key: str = None, location_id: str = None):
        self.api_key = api_key or GoHighLevelConfig.API_KEY
        self.location_id = location_id or GoHighLevelConfig.LOCATION_ID
        self.base_url = GoHighLevelConfig.BASE_URL
        self.timeout = GoHighLevelConfig.TIMEOUT
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def get_suppressed_contacts(self, limit: int = 100) -> List[Dict]:
        """
        Get contacts with suppression/bounce data from GoHighLevel
        """
        all_contacts = []
        
        # Try different endpoint approaches
        approaches = [
            # Approach 1: POST to search endpoint with locationId in body
            {
                "method": "POST",
                "url": f"{self.base_url}/v1/contacts/search",
                "params": {},
                "data": {"locationId": self.location_id, "limit": min(100, limit)} if self.location_id else {"limit": min(100, limit)}
            },
            # Approach 2: GET with locationId
            {
                "method": "GET",
                "url": f"{self.base_url}/v1/contacts",
                "params": {"locationId": self.location_id, "limit": min(100, limit)} if self.location_id else {"limit": min(100, limit)},
                "data": None
            },
            # Approach 3: Without location filter
            {
                "method": "GET",
                "url": f"{self.base_url}/v1/contacts",
                "params": {"limit": min(100, limit)},
                "data": None
            },
        ]

        for i, approach in enumerate(approaches):
            print(f"  Trying: {approach['method']} {approach['url']}")
            
            try:
                if approach["method"] == "POST":
                    response = self._session.post(
                        approach["url"], 
                        json=approach.get("data", {}),
                        timeout=self.timeout
                    )
                else:
                    response = self._session.get(
                        approach["url"], 
                        params=approach.get("params", {}),
                        timeout=self.timeout
                    )
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    contacts = (
                        data.get("contacts")
                        or data.get("data")
                        or data.get("results")
                        or []
                    )
                    
                    if contacts:
                        print(f"    Found {len(contacts)} contacts!")
                        for contact in contacts:
                            record = self._process_contact(contact)
                            if record:
                                all_contacts.append(record)
                        break
                        
                elif response.status_code == 401:
                    print(f"    ERROR: Unauthorized - check API key")
                    break
                elif response.status_code == 404:
                    print(f"    Not found - trying next approach")
                    continue
                else:
                    print(f"    Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"    Exception: {e}")
                continue

        if not all_contacts:
            print("  ⚠️  No suppression data found!")
            print("")
            print("  POSSIBLE ISSUES:")
            print("  1. API key doesn't have 'contacts.read' scope")
            print("     → Go to GoHighLevel > Settings > Integrations > API Keys")
            print("     → Create a new Agency API Key with contacts.read permission")
            print("  2. Location ID is incorrect")
            print("     → Verify the location ID in GoHighLevel > Locations")
            print("  3. API key is a Private Integration token (starts with 'pit-')")
            print("     → These have limited access - use an Agency API Key instead")

        return all_contacts[:limit]

    def _process_contact(self, contact: dict) -> Optional[Dict]:
        """Process raw contact data into suppression record"""
        email = contact.get("email")
        if not email:
            return None

        dnd = contact.get("dnd", False)
        tags = contact.get("tags", [])
        
        is_unsubscribed = contact.get("unsubscribed", False)
        is_hard_bounce = contact.get("invalid_email", False) or contact.get("hard_bounce", False)

        suppression_source = None
        reason = None
        rule_id = None
        suppression_tag = None

        if dnd:
            suppression_source = "DND Enabled"
            reason = "Do Not Disturb"
            rule_id = "R-SUP-DND-001"
            suppression_tag = "suppress_dnd"
        elif is_hard_bounce:
            suppression_source = "Hard Bounce"
            reason = "Invalid Email"
            rule_id = "R-SUP-H-002"
            suppression_tag = "suppress_invalid_email"
        elif is_unsubscribed:
            suppression_source = "Unsubscribe List"
            reason = "Unsubscribed"
            rule_id = "R-SUP-H-003"
            suppression_tag = "suppress_unsub"

        if not suppression_source and tags:
            for tag in tags:
                tag_lower = tag.lower() if isinstance(tag, str) else ""
                if "bounce" in tag_lower or "hard bounce" in tag_lower:
                    suppression_source = "Hard Bounce"
                    reason = "Invalid Email"
                    rule_id = "R-SUP-H-002"
                    suppression_tag = "suppress_invalid_email"
                    break
                elif "unsubscribe" in tag_lower:
                    suppression_source = "Unsubscribe List"
                    reason = "Unsubscribed"
                    rule_id = "R-SUP-H-003"
                    suppression_tag = "suppress_unsub"
                    break

        if not suppression_source:
            return None

        record = {
            "date_added": datetime.now().strftime("%m/%d/%Y"),
            "platform_source": "GHL: Alt Fund",
            "contact_id": contact.get("id", ""),
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

    def get_all_suppressed_contacts(self) -> List[Dict]:
        """Get all suppressed contacts"""
        return self.get_suppressed_contacts(limit=500)

    def test_connection(self) -> dict:
        """Test API connection"""
        print("Testing GoHighLevel API connection...")
        print(f"  API Key: {self.api_key[:10]}...")
        print(f"  Location ID: {self.location_id}")

        # Test base URL
        try:
            response = self._session.get(self.base_url, timeout=5)
            print(f"  Base URL: {response.text}")
        except Exception as e:
            print(f"  Base URL test failed: {e}")

        # Try contacts endpoint
        endpoint = f"{self.base_url}/v1/contacts"
        params = {"locationId": self.location_id, "limit": 1} if self.location_id else {"limit": 1}

        try:
            response = self._session.get(endpoint, params=params, timeout=self.timeout)
            print(f"  Contacts Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}

        except Exception as e:
            print(f"  Exception: {e}")
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    client = GoHighLevelClient()
    data = client.get_all_suppressed_contacts()
    print(f"Got {len(data)} suppressed contacts")
