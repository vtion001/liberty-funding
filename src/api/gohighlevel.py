"""GoHighLevel API Client - Uses LeadConnector API (services.leadconnectorhq.com)"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import time
from config.settings import GoHighLevelConfig


class GoHighLevelClient:
    """Client for GoHighLevel API via LeadConnector"""

    def __init__(self, api_key: str = None, location_id: str = None):
        self.api_key = api_key or GoHighLevelConfig.API_KEY
        self.location_id = location_id or GoHighLevelConfig.LOCATION_ID
        self.base_url = GoHighLevelConfig.BASE_URL
        self.api_version = GoHighLevelConfig.API_VERSION
        self.timeout = GoHighLevelConfig.TIMEOUT
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Version": self.api_version,
                "Content-Type": "application/json",
            }
        )

    def get_suppressed_contacts(self, limit: int = 500) -> List[Dict]:
        """Get contacts with suppression/bounce data from GoHighLevel"""

        suppressed = []
        seen_ids = set()
        page_token = None

        while len(suppressed) < limit:
            batch_size = min(100, limit - len(suppressed))
            body = {
                "locationId": self.location_id,
                "pageLimit": batch_size,
            }
            if page_token:
                body["searchAfter"] = page_token

            response = None
            for attempt in range(3):
                try:
                    response = self._session.post(
                        f"{self.base_url}/contacts/search",
                        json=body,
                        timeout=self.timeout,
                    )
                except requests.RequestException:
                    pass

                if response is None:
                    wait = 2 * (2**attempt)
                    print(f"  Connection failed, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                if response.status_code == 429 or response.status_code == 503:
                    wait = 5 * (2**attempt)
                    print(
                        f"  Rate limited ({response.status_code}), retrying in {wait}s..."
                    )
                    time.sleep(wait)
                    response = None
                    continue

                if response.status_code == 401:
                    print(f"  401 Unauthorized - check API key and scopes")
                    return suppressed
                elif response.status_code == 422:
                    print(f"  422: {response.text[:200]}")
                    return suppressed
                elif response.status_code != 200:
                    print(f"  Error {response.status_code}: {response.text[:200]}")
                    return suppressed

                break

            if response is None or response.status_code != 200:
                return suppressed

            try:
                data = response.json()
            except Exception:
                wait = 5
                print(f"  Invalid JSON, retrying in {wait}s...")
                time.sleep(wait)
                response = None
                continue

            contacts = data.get("contacts", [])

            if not contacts:
                break

            for contact in contacts:
                contact_id = contact.get("id")
                if contact_id in seen_ids:
                    continue
                seen_ids.add(contact_id)

                record = self._process_contact(contact)
                if record:
                    suppressed.append(record)

            if len(contacts) < batch_size:
                break

            page_token = contacts[-1].get("searchAfter")
            if not page_token:
                break

        return suppressed[:limit]

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

        if dnd:
            suppression_source = "DND Enabled"
            reason = "Policy Block"
            rule_id = "R-SUP-H-001"
            suppression_tag = "suppress_bounce_hard"
        elif valid_email is False:
            suppression_source = "Hard Bounce"
            reason = "Invalid Email"
            rule_id = "R-SUP-H-002"
            suppression_tag = "suppress_invalid_email"

        if not suppression_source and tags:
            for tag in tags:
                tag_lower = tag.lower() if isinstance(tag, str) else ""
                if tag_lower == "suppress_bounce_hard":
                    suppression_source = "Hard Bounce"
                    reason = "Invalid Email"
                    rule_id = "R-SUP-H-001"
                    suppression_tag = "suppress_bounce_hard"
                    break
                elif tag_lower == "suppress_invalid_email":
                    suppression_source = "Hard Bounce"
                    reason = "Invalid Email"
                    rule_id = "R-SUP-H-002"
                    suppression_tag = "suppress_invalid_email"
                    break
                elif tag_lower == "suppress_unsub":
                    suppression_source = "Unsubscribe List"
                    reason = "Unsubscribed"
                    rule_id = "R-SUP-H-003"
                    suppression_tag = "suppress_unsub"
                    break
                elif tag_lower == "suppress_not_interested":
                    suppression_source = "Manual Reply"
                    reason = "Not Interested"
                    rule_id = "R-SUP-H-004"
                    suppression_tag = "suppress_not_interested"
                    break
                elif (
                    tag_lower == "suppress_complain"
                    or tag_lower == "suppress_complaint"
                ):
                    suppression_source = "Complaint"
                    reason = "Recorded Complaint"
                    rule_id = "R-SUP-H-005"
                    suppression_tag = "suppress_complain"
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
    print("=== Testing GHL API ===")
    data = client.get_all_suppressed_contacts()
    print(f"Got {len(data)} suppressed contacts")
    for r in data[:5]:
        print(f"  {r['email']} - {r['suppression_source']}")
