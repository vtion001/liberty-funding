"""GoHighLevel API Client - Uses LeadConnector API (services.leadconnectorhq.com)"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import time
from config.settings import GoHighLevelConfig


class GoHighLevelClient:
    """Client for GoHighLevel API via LeadConnector"""

    SUPPRESSION_TAG_MAP = {
        "suppress_bounce_hard": {
            "suppression_source": "Hard Bounce",
            "reason": "Invalid Email",
            "rule_id": "R-SUP-H-001",
            "suppression_tag": "suppress_bounce_hard",
        },
        "suppress_invalid_email": {
            "suppression_source": "Hard Bounce",
            "reason": "Invalid Email",
            "rule_id": "R-SUP-H-002",
            "suppression_tag": "suppress_invalid_email",
        },
        "suppress_unsub": {
            "suppression_source": "Unsubscribe List",
            "reason": "Unsubscribed",
            "rule_id": "R-SUP-H-003",
            "suppression_tag": "suppress_unsub",
        },
        "suppress_not_interested": {
            "suppression_source": "Manual Reply",
            "reason": "Not Interested",
            "rule_id": "R-SUP-H-004",
            "suppression_tag": "suppress_not_interested",
        },
        "suppress_complain": {
            "suppression_source": "Complaint",
            "reason": "Recorded Complaint",
            "rule_id": "R-SUP-H-005",
            "suppression_tag": "suppress_complain",
        },
        "suppress_complaint": {
            "suppression_source": "Complaint",
            "reason": "Recorded Complaint",
            "rule_id": "R-SUP-H-005",
            "suppression_tag": "suppress_complain",
        },
    }

    def __init__(self, api_key: str = None, location_id: str = None, source_name: str = None):
        self.api_key = api_key or GoHighLevelConfig.API_KEY
        self.location_id = location_id or GoHighLevelConfig.LOCATION_ID
        self.source_name = source_name or "GHL"
        self.base_url = "https://services.leadconnectorhq.com"
        self.api_version = "2021-07-28"
        self.timeout = 15
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Version": self.api_version,
                "Content-Type": "application/json",
            }
        )

    def get_all_contacts(self, limit: int = 500) -> List[Dict]:
        """Get all contacts from GoHighLevel location"""
        contacts = []
        seen_ids = set()
        page_token = None

        while len(contacts) < limit:
            body = {
                "locationId": self.location_id,
                "pageLimit": min(100, limit - len(contacts)),
            }
            if page_token:
                body["searchAfter"] = page_token

            for attempt in range(3):
                try:
                    response = self._session.post(
                        f"{self.base_url}/contacts/search",
                        json=body,
                        timeout=self.timeout,
                    )
                except requests.RequestException:
                    wait = 2 * (2**attempt)
                    print(f"  Connection failed, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                if response is None:
                    continue

                if response.status_code == 429 or response.status_code == 503:
                    wait = 5 * (2**attempt)
                    print(f"  Rate limited ({response.status_code}), retrying in {wait}s...")
                    time.sleep(wait)
                    response = None
                    continue

                if response.status_code == 401:
                    print(f"  401 Unauthorized - check API key and scopes")
                    return contacts
                elif response.status_code != 200:
                    print(f"  Error {response.status_code}: {response.text[:200]}")
                    return contacts
                break

            if response is None or response.status_code != 200:
                break

            try:
                data = response.json()
            except Exception:
                wait = 5
                print(f"  Invalid JSON, retrying in {wait}s...")
                time.sleep(wait)
                continue

            raw_contacts = data.get("contacts", [])
            if not raw_contacts:
                break

            for contact in raw_contacts:
                cid = contact.get("id")
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)
                contacts.append(contact)

            if len(raw_contacts) < body["pageLimit"]:
                break

            page_token = raw_contacts[-1].get("searchAfter")
            if not page_token:
                break

        return contacts[:limit]

    def get_suppressed_contacts(self, limit: int = 500) -> List[Dict]:
        """Get contacts with suppression markers (DND, invalid email, or suppress tags)"""
        all_contacts = self.get_all_contacts(limit=limit)
        suppressed = []

        for contact in all_contacts:
            record = self._process_contact(contact)
            if record:
                suppressed.append(record)

        return suppressed

    def _process_contact(self, contact: dict) -> Optional[Dict]:
        """Process raw contact data into suppression record"""
        email = contact.get("email")
        if not email:
            return None

        dnd = contact.get("dnd", False)
        valid_email = contact.get("validEmail")
        tags = contact.get("tags", [])

        suppression_source = None
        reason = None
        rule_id = None
        suppression_tag = None

        # Check DND flag
        if dnd:
            suppression_source = "DND Enabled"
            reason = "Policy Block"
            rule_id = "R-SUP-H-001"
            suppression_tag = "dnd_block"

        # Check invalid email
        elif valid_email is False:
            suppression_source = "Hard Bounce"
            reason = "Invalid Email"
            rule_id = "R-SUP-H-002"
            suppression_tag = "suppress_invalid_email"

        # Check suppress tags
        if not suppression_source and tags:
            for tag in tags:
                tag_lower = tag.lower() if isinstance(tag, str) else ""
                for suppress_key, suppress_info in self.SUPPRESSION_TAG_MAP.items():
                    if suppress_key in tag_lower:
                        suppression_source = suppress_info["suppression_source"]
                        reason = suppress_info["reason"]
                        rule_id = suppress_info["rule_id"]
                        suppression_tag = suppress_info["suppression_tag"]
                        break
                if suppression_source:
                    break

        if not suppression_source:
            return None

        record = {
            "date_added": datetime.now().strftime("%m/%d/%Y"),
            "platform_source": self.source_name,  # e.g. "Libertad_Capital" or "Alternative_Funding"
            "contact_id": contact.get("id", ""),
            "email": email,
            "suppression_source": suppression_source,
            "reason": reason,
            "rule_id": rule_id,
            "suppression_tag": suppression_tag,
            "permanent_required": "Yes",
            "dnd_required": "Yes" if dnd else "No",
            "workflow_removal_required": "Yes",
        }

        return record

    def get_all_suppressed_contacts(self) -> List[Dict]:
        """Get all suppressed contacts"""
        return self.get_suppressed_contacts(limit=500)


if __name__ == "__main__":
    client = GoHighLevelClient()
    print("=== Testing GHL API ===")
    data = client.get_suppressed_contacts()
    print(f"Got {len(data)} suppressed contacts")
    for r in data[:10]:
        print(f"  {r['email']} - {r['suppression_source']} ({r['reason']})")
