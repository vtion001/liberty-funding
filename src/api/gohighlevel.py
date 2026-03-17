"""GoHighLevel API Client"""

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

        Args:
            limit: Maximum number of contacts to fetch

        Returns:
            List of suppressed contact records
        """
        all_contacts = []
        page = 1

        while len(all_contacts) < limit:
            endpoint = f"{self.base_url}/v1/contacts"
            params = {"limit": 100, "page": page}

            if self.location_id:
                params["location_id"] = self.location_id

            try:
                response = self._session.get(
                    endpoint, params=params, timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()

                contacts = data.get("contacts", [])
                if not contacts:
                    break

                for contact in contacts:
                    record = self._process_contact(contact)
                    if record:
                        all_contacts.append(record)

                if len(contacts) < 100:
                    break
                page += 1

            except requests.exceptions.RequestException as e:
                print(f"Error fetching contacts: {e}")
                break

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
            elif "complaint" in tag_lower:
                suppression_source = "Complaint"
                reason = "Recorded Complaint"
                rule_id = "R-SUP-H-005"
                suppression_tag = "suppress_complain"
                break
            elif "not interested" in tag_lower:
                suppression_source = "Manual Reply"
                reason = "Not Interested"
                rule_id = "R-SUP-H-004"
                suppression_tag = "suppress_not_interested"
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


if __name__ == "__main__":
    client = GoHighLevelClient()
    data = client.get_all_suppressed_contacts()
    print(f"Got {len(data)} suppressed contacts")
