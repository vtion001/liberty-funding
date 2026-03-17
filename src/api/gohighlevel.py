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
        """Get contacts with suppression/bounce data from GoHighLevel"""
        
        # Show diagnostic info
        print(f"  API Key: {self.api_key[:20]}...")
        print(f"  Location ID: {self.location_id}")
        print(f"  Key type: {'Private Integration (pit-)' if self.api_key.startswith('pit-') else 'Agency/API Key'}")
        
        all_contacts = []
        
        # Try multiple approaches
        approaches = [
            # POST to search endpoint
            {
                "method": "POST",
                "url": f"{self.base_url}/v1/contacts/search",
                "data": {"locationId": self.location_id, "limit": min(50, limit)} if self.location_id else {"limit": min(50, limit)}
            },
            # GET with locationId
            {
                "method": "GET",
                "url": f"{self.base_url}/v1/contacts",
                "params": {"locationId": self.location_id, "limit": min(50, limit)} if self.location_id else {"limit": min(50, limit)}
            },
        ]

        for i, approach in enumerate(approaches):
            print(f"  Trying approach {i+1}: {approach['method']} {approach['url']}")
            
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
                
                # Check for different status codes
                if response.status_code == 200:
                    data = response.json()
                    contacts = data.get("contacts") or data.get("data") or []
                    
                    if contacts:
                        print(f"    ✅ Found {len(contacts)} contacts!")
                        for contact in contacts:
                            record = self._process_contact(contact)
                            if record:
                                all_contacts.append(record)
                        break
                        
                elif response.status_code == 401:
                    print(f"    ❌ Unauthorized - API key invalid or no permission")
                    break
                elif response.status_code == 403:
                    print(f"    ❌ Forbidden - API key doesn't have required scope")
                    break
                elif response.status_code == 404:
                    print(f"    ❌ Not found - endpoint may not exist for this key type")
                else:
                    print(f"    Response: {response.text[:100]}")
                    
            except Exception as e:
                print(f"    Exception: {e}")

        if not all_contacts:
            print("  ⚠️ No contacts returned!")
            print("")
            print("  DIAGNOSIS:")
            if self.api_key.startswith("pit-"):
                print("  → Using Private Integration token (pit-)")
                print("  → Private Integration tokens have LIMITED access")
                print("  → Need to use AGENCY API KEY instead")
                print("  → Go to GoHighLevel > Settings > Integrations > API Keys")
                print("  → Create NEW 'Agency API Key' (not Private Integration)")
            else:
                print("  → Check if Location ID is correct")
                print("  → Verify API key has 'contacts.read' permission")

        return all_contacts[:limit]

    def _process_contact(self, contact: dict) -> Optional[Dict]:
        """Process raw contact data into suppression record"""
        email = contact.get("email")
        if not email:
            return None

        dnd = contact.get("dnd", False)
        tags = contact.get("tags", [])

        suppression_source = None
        reason = None
        rule_id = None
        suppression_tag = None

        if dnd:
            suppression_source = "DND Enabled"
            reason = "Do Not Disturb"
            rule_id = "R-SUP-DND-001"
            suppression_tag = "suppress_dnd"

        # Check tags for bounce/unsubscribe
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
            # Return contact but mark as "Active" - not suppressed
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


if __name__ == "__main__":
    client = GoHighLevelClient()
    data = client.get_all_suppressed_contacts()
    print(f"Got {len(data)} suppressed contacts")
