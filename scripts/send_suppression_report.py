#!/usr/bin/env python3
"""
Libertad Capital - Suppression + Campaign Report Email
Fetches suppression data and campaign stats from GHL, generates HTML report, sends via gog
"""

import os
import sys
import datetime
import argparse
from pathlib import Path
from collections import Counter

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.api.gohighlevel import GoHighLevelClient
from src.api.googlesheets import GoogleSheetsClient

load_dotenv(project_root / ".env")

RECIPIENT = os.environ.get("REPORT_RECIPIENT_EMAIL", "alex@altfunding.com,paolo.f@altfunding.com")
SENDER = "agsdev@allianceglobalsolutions.com"

# 2-color palette — navy + white only
COLOR_NAVY = "#1a1a2e"
COLOR_WHITE = "#ffffff"


# ============================================================================
# CAMPAIGN DATA
# ============================================================================

def fetch_campaign_stats():
    """Fetch campaign stats from all GHL accounts that have emails/schedule scope"""
    active_raw = os.environ.get("ACTIVE_GHL_ACCOUNTS", "1,2")
    active_accounts = [a.strip() for a in active_raw.split(",")]
    all_campaigns = []
    all_workflows = []

    for account_num in active_accounts:
        api_key = os.environ.get(f"GOHIGHLEVEL_API_KEY_{account_num}")
        location_id = os.environ.get(f"GHL_LOCATION_ID_{account_num}")
        source_name = os.environ.get(f"GHL_SOURCE_NAME_{account_num}", f"GHL_{account_num}")

        if not api_key or not location_id:
            continue

        try:
            campaigns = fetch_email_campaigns(api_key, location_id, source_name)
            all_campaigns.extend(campaigns)
        except Exception as e:
            print(f"Error fetching campaigns for {source_name}: {e}")

        try:
            workflows = fetch_workflow_stats(api_key, location_id, source_name)
            all_workflows.extend(workflows)
        except Exception as e:
            print(f"Error fetching workflows for {source_name}: {e}")

    return all_campaigns, all_workflows


def fetch_email_campaigns(api_key, location_id, source_name):
    """Fetch email campaigns and compute open/click rates"""
    import requests

    url = f"https://services.leadconnectorhq.com/emails/schedule"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    params = {
        "locationId": location_id,
        "limit": 50,
        "showStats": "true"
    }

    campaigns = []
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            return campaigns

        data = resp.json()
        for c in data.get("schedules", []):
            s = c.get("stats", {})
            sent = int(s.get("sent", 0) or 0)
            opens = int(s.get("opens", 0) or 0)
            clicks = int(s.get("clicks", 0) or 0)
            bounces = int(s.get("bounces", 0) or 0)
            unsubs = int(s.get("unsubscribes", 0) or 0)

            open_rate = round((opens / sent) * 100, 1) if sent > 0 else 0.0
            click_rate = round((clicks / sent) * 100, 1) if sent > 0 else 0.0
            bounce_rate = round((bounces / sent) * 100, 1) if sent > 0 else 0.0

            campaigns.append({
                "source": source_name,
                "name": c.get("name", "N/A"),
                "status": c.get("status", "N/A"),
                "type": c.get("campaignType", "N/A"),
                "sent": sent,
                "opens": opens,
                "clicks": clicks,
                "bounces": bounces,
                "unsubscribes": unsubs,
                "open_rate": open_rate,
                "click_rate": click_rate,
                "bounce_rate": bounce_rate,
            })
    except Exception as e:
        print(f"  Campaign fetch error: {e}")

    return campaigns


def fetch_workflow_stats(api_key, location_id, source_name):
    """Fetch drip workflows from the GHL Workflows API.

    Note: GHL /workflows/ endpoint does NOT return per-workflow stats (opens/clicks/sent).
    It returns only: id, name, status, version, createdAt, updatedAt, locationId.
    Stats must be derived via webhooks or the LC Email webhooks.
    We still list active workflows as they drive suppression events.
    """
    import requests

    url = "https://services.leadconnectorhq.com/workflows/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    params = {"locationId": location_id}

    workflows = []
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 401:
            print(f"  Workflows API: token lacks scope (add 'workflows/read' in GHL Private Integration)")
            return []
        if resp.status_code != 200:
            return []

        data = resp.json()
        for w in data.get("workflows", []) or []:
            # GHL workflow list endpoint has no stats — only name + status
            # Stats (opens/clicks/sent) require webhook aggregation or dashboard UI
            workflows.append({
                "source": source_name,
                "name": w.get("name", "N/A"),
                "status": w.get("status", "N/A"),
                "type": "drip",
                "sent": 0,
                "opens": 0,
                "clicks": 0,
                "bounces": 0,
                "unsubscribes": 0,
                "open_rate": 0.0,
                "click_rate": 0.0,
                "bounce_rate": 0.0,
            })
    except Exception as e:
        print(f"  Workflow fetch error: {e}")

    return workflows


# ============================================================================
# SUPPRESSION DATA
# ============================================================================

def fetch_all_suppressed():
    """Fetch suppressed contacts from all configured GHL accounts"""
    active_raw = os.environ.get("ACTIVE_GHL_ACCOUNTS", "1,2")
    active_accounts = [a.strip() for a in active_raw.split(",")]
    all_data = []

    for account_num in active_accounts:
        api_key = os.environ.get(f"GOHIGHLEVEL_API_KEY_{account_num}")
        location_id = os.environ.get(f"GHL_LOCATION_ID_{account_num}")
        source_name = os.environ.get(f"GHL_SOURCE_NAME_{account_num}", f"GHL_{account_num}")

        if not api_key or not location_id:
            continue

        try:
            client = GoHighLevelClient(
                api_key=api_key,
                location_id=location_id,
                source_name=source_name
            )
            data = client.get_all_suppressed_contacts()
            all_data.extend(data)
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")

    return all_data


def get_sheet_summary():
    """Get current suppression counts from Google Sheets"""
    try:
        sheets = GoogleSheetsClient()
        emails = sheets.get_email_index()
        return len(emails)
    except Exception as e:
        print(f"Error fetching sheet: {e}")
        return 0


# ============================================================================
# HTML REPORT BUILDER
# ============================================================================

def build_html_report(contacts, sheet_total, campaigns, workflows):
    """Build 2-color HTML email report (no emojis)"""

    total_suppressed = len(contacts)
    by_source = Counter(c.get("platform_source", "Unknown") for c in contacts)
    by_reason = Counter(c.get("reason", "Unknown") for c in contacts)

    now = datetime.datetime.now()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M %p")

    # Suppression severity
    if total_suppressed > 20:
        sev = "HIGH - " + str(total_suppressed) + " contacts"
    elif total_suppressed > 10:
        sev = "MODERATE - " + str(total_suppressed) + " contacts"
    elif total_suppressed > 0:
        sev = "LOW - " + str(total_suppressed) + " contacts"
    else:
        sev = "CLEAN - No suppression issues"

    # Campaign summary (email broadcasts + drip workflows)
    total_sent = sum(c.get("sent", 0) for c in campaigns) + sum(w.get("sent", 0) for w in workflows)
    total_opens = sum(c.get("opens", 0) for c in campaigns) + sum(w.get("opens", 0) for w in workflows)
    total_clicks = sum(c.get("clicks", 0) for c in campaigns) + sum(w.get("clicks", 0) for w in workflows)
    total_bounces = sum(c.get("bounces", 0) for c in campaigns) + sum(w.get("bounces", 0) for w in workflows)
    avg_open_rate = round(total_opens / total_sent * 100, 1) if total_sent > 0 else 0.0
    avg_click_rate = round(total_clicks / total_sent * 100, 1) if total_sent > 0 else 0.0
    avg_bounce_rate = round(total_bounces / total_sent * 100, 1) if total_sent > 0 else 0.0

    # Recommendations
    recommendations = []
    invalid_count = by_reason.get("Invalid Email", 0)
    unsub_count = by_reason.get("Unsubscribed", 0)

    if invalid_count > 5:
        recommendations.append(
            "HIGH INVALID EMAIL RATE: " + str(invalid_count) + " contacts flagged as invalid/bounce. "
            "Audit your email list acquisition - fake or mistyped emails hurt deliverability."
        )
    elif invalid_count > 0:
        recommendations.append(
            "INVALID EMAILS DETECTED: " + str(invalid_count) + " contacts with invalid/bounce emails. "
            "Keep permanently suppressed to protect sender reputation."
        )

    if unsub_count > 3:
        recommendations.append(
            "HIGH UNSUBSCRIBE ACTIVITY: " + str(unsub_count) + " contacts have unsubscribed. "
            "Review email content frequency and relevance."
        )

    if total_sent > 0 and avg_open_rate < 20:
        recommendations.append(
            "LOW OPEN RATE: Average open rate is " + str(avg_open_rate) + "%. "
            "Consider improving subject lines and sender reputation."
        )

    if total_sent > 0 and avg_click_rate < 2:
        recommendations.append(
            "LOW CLICK RATE: Average CTR is " + str(avg_click_rate) + "%. "
            "Review call-to-action placement and email content relevance."
        )

    if total_sent == 0:
        recommendations.append(
            "NO CAMPAIGN DATA: No sent campaigns detected. "
            "Ensure your GHL account has active campaigns with tracking enabled."
        )

    if total_suppressed == 0:
        recommendations.append(
            "CLEAN LIST: No suppression issues detected. Your contact list is in good standing."
        )

    recommendations.append(
        "RUN DAILY: Liberty runs daily to catch new suppressions early. "
        "Use DRY_RUN=true to preview before changes go live."
    )

    # ---- Build table rows ----

    # Campaign rows
    campaign_rows = ""
    for c in campaigns:
        sent_k = f"{c['sent']:,}" if c['sent'] > 0 else "0"
        campaign_rows += f"""
        <tr>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};font-size:13px;">{c['source']}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};font-size:13px;">{c['name'][:45]}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};text-align:center;font-size:13px;">{sent_k}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};text-align:center;font-size:13px;">{c['open_rate']}%</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};text-align:center;font-size:13px;">{c['click_rate']}%</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};text-align:center;font-size:13px;">{c['bounce_rate']}%</td>
        </tr>"""

    if not campaigns:
        campaign_rows = f"""
        <tr>
            <td colspan="6" style="padding:16px;text-align:center;color:#888;font-size:13px;">
                No campaign data available. Ensure emails/schedule scope is enabled for your GHL account.
            </td>
        </tr>"""
    elif total_sent == 0:
        campaign_rows += f"""
        <tr>
            <td colspan="6" style="padding:12px;text-align:center;color:#888;font-size:12px;font-style:italic;">
                Campaign(s) found but no sends recorded yet.
            </td>
        </tr>"""

    # Workflow rows — GHL /workflows/ API has no per-workflow stats (opens/clicks/sent)
    # We list active workflows by name + status as they drive suppression events
    workflow_rows = ""
    for w in workflows:
        status_color = "#22c55e" if w['status'] == "published" else "#f59e0b"
        workflow_rows += f"""
        <tr>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};font-size:13px;">{w['source']}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};font-size:13px;">{w['name'][:45]}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{status_color};text-align:center;font-size:11px;font-weight:600;text-transform:uppercase;">{w['status']}</td>
            <td colspan="3" style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:#888;text-align:center;font-size:11px;">Stats via GHL dashboard or webhooks</td>
        </tr>"""

    if not workflows:
        workflow_rows = f"""
        <tr>
            <td colspan="5" style="padding:16px;text-align:center;color:#888;font-size:13px;">
                No workflows found for this account. Active workflows appear here once the 'workflows/read' scope is added.
            </td>
        </tr>"""

    # Suppression source rows
    source_rows = ""
    for src, count in sorted(by_source.items()):
        pct = round(count / total_suppressed * 100) if total_suppressed > 0 else 0
        source_rows += f"""
        <tr>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};font-weight:600;font-size:13px;">{src}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};text-align:center;font-size:13px;">{count}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};text-align:center;font-size:13px;">{pct}%</td>
        </tr>"""

    # Suppression reason rows
    reason_rows = ""
    for reason, count in by_reason.most_common():
        pct = round(count / total_suppressed * 100) if total_suppressed > 0 else 0
        reason_rows += f"""
        <tr>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};font-size:13px;">{reason}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};text-align:center;font-size:13px;">{count}</td>
            <td style="padding:9px 10px;border-bottom:1px solid {COLOR_NAVY};color:{COLOR_NAVY};text-align:center;font-size:13px;">{pct}%</td>
        </tr>"""

    # Recommendations
    rec_items = "".join(
        f'<li style="margin-bottom:8px;color:{COLOR_NAVY};">{r}</li>'
        for r in recommendations
    )

    # Suppression detail rows
    detail_rows = ""
    for c in contacts[:20]:
        detail_rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #ccc;color:{COLOR_NAVY};font-size:12px;">{c.get('email','')}</td>
            <td style="padding:8px;border-bottom:1px solid #ccc;color:{COLOR_NAVY};font-size:12px;">{c.get('platform_source','')}</td>
            <td style="padding:8px;border-bottom:1px solid #ccc;color:{COLOR_NAVY};font-size:12px;">{c.get('suppression_source','')}</td>
            <td style="padding:8px;border-bottom:1px solid #ccc;color:{COLOR_NAVY};font-size:12px;">{c.get('reason','')}</td>
        </tr>"""

    more_note = (
        f"<p style=\"color:#888;font-size:12px;margin-top:8px;\">+ {total_suppressed - 20} more contacts in Google Sheet</p>"
        if total_suppressed > 20 else ""
    )

    avg_note = (
        f"<p style=\"color:{COLOR_NAVY};font-size:12px;margin:8px 0 0;\">Averages: {avg_open_rate}% open | {avg_click_rate}% click | {avg_bounce_rate}% bounce</p>"
        if total_sent > 0 else ""
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body{{font-family:Calibri,Arial,sans-serif;background:#f5f5f5;margin:0;padding:20px;color:{COLOR_NAVY}}}
  .wrap{{max-width:700px;margin:0 auto;background:{COLOR_WHITE};border-radius:8px;overflow:hidden;border:2px solid {COLOR_NAVY}}}
  .header{{background:{COLOR_NAVY};padding:24px 32px}}
  .header h1{{margin:0 0 6px;font-size:20px;font-weight:700;color:{COLOR_WHITE};letter-spacing:-0.3px}}
  .header p{{margin:0;color:#9ca3af;font-size:13px}}
  .sev{{display:inline-block;margin-top:10px;font-size:13px;font-weight:700;color:{COLOR_WHITE};border:1px solid {COLOR_WHITE};padding:3px 12px;border-radius:3px;letter-spacing:0.5px}}
  .body{{padding:24px 32px}}
  .stats{{display:table;width:100%;border-collapse:collapse;margin-bottom:28px}}
  .stat-row{{display:table-row}}
  .stat{{display:table-cell;padding:16px 0;text-align:center;border:1px solid {COLOR_NAVY};vertical-align:middle}}
  .stat:first-child{{background:{COLOR_NAVY};color:{COLOR_WHITE};border-right:none}}
  .stat:not(:first-child){{border-left:none}}
  .stat-n{{font-size:28px;font-weight:800;line-height:1}}
  .stat-l{{font-size:10px;margin-top:6px;text-transform:uppercase;letter-spacing:0.5px}}
  .sec{{margin-bottom:24px}}
  .sec-title{{font-size:13px;font-weight:700;color:{COLOR_NAVY};margin:0 0 12px;padding-bottom:6px;border-bottom:2px solid {COLOR_NAVY};text-transform:uppercase;letter-spacing:0.5px}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  th{{text-align:left;padding:9px 10px;background:{COLOR_NAVY};color:{COLOR_WHITE};font-size:10px;text-transform:uppercase;letter-spacing:0.5px}}
  td{{padding:9px 10px;color:{COLOR_NAVY}}}
  ul{{margin:0;padding-left:20px}}
  li{{color:{COLOR_NAVY};font-size:13px;line-height:1.6}}
  .note{{background:#f5f5f5;border-left:4px solid {COLOR_NAVY};padding:12px 16px;font-size:13px;color:{COLOR_NAVY};margin-bottom:20px;line-height:1.6}}
  .footer{{padding:16px 32px;background:#f5f5f5;border-top:1px solid #ddd;text-align:center;color:#888;font-size:11px}}
  .footer-brand{{font-weight:700;color:{COLOR_NAVY};margin-bottom:4px}}
</style>
</head>
<body>
<div class=wrap>

  <div class=header>
    <h1>Libertad Capital - Daily Report</h1>
    <p>Suppression &amp; Campaign Analytics &mdash; {date_str} at {time_str}</p>
    <span class=sev>{sev}</span>
  </div>

  <div class=body>

    <div class=sec>
      <h2 class=sec-title>Campaign Performance</h2>
      <table>
        <thead>
          <tr>
            <th>Source</th>
            <th>Campaign</th>
            <th style=text-align:center>Sent</th>
            <th style=text-align:center>Open %</th>
            <th style=text-align:center>Click %</th>
            <th style=text-align:center>Bounce %</th>
          </tr>
        </thead>
        <tbody>{campaign_rows}</tbody>
      </table>
      {avg_note}
    </div>

    <div class=sec>
      <h2 class=sec-title>Drip Workflows</h2>
      <p style="color:#888;font-size:11px;margin:0 0 12px;">GHL REST API does not expose per-workflow stats. Open/click rates require GHL dashboard or webhook aggregation.</p>
      <table>
        <thead>
          <tr>
            <th>Source</th>
            <th>Workflow</th>
            <th style=text-align:center>Status</th>
            <th style=text-align:center colspan=3>Engagement</th>
          </tr>
        </thead>
        <tbody>{workflow_rows}</tbody>
      </table>
    </div>

    <div class=stats>
      <div class=stat-row>
        <div class=stat>
          <div class=stat-n>{total_suppressed}</div>
          <div class=stat-l>Total Suppressed</div>
        </div>
        <div class=stat>
          <div class=stat-n>{sheet_total}</div>
          <div class=stat-l>Total in Sheet</div>
        </div>
        <div class=stat>
          <div class=stat-n>{len(by_source)}</div>
          <div class=stat-l>Sources</div>
        </div>
        <div class=stat>
          <div class=stat-n>{len(campaigns)}</div>
          <div class=stat-l>Campaigns</div>
        </div>
      </div>
    </div>

    <div class=sec>
      <h2 class=sec-title>Suppression by Source</h2>
      <table>
        <thead><tr><th>Source Account</th><th style=text-align:center>Count</th><th style=text-align:center>% of Total</th></tr></thead>
        <tbody>{source_rows if source_rows else '<tr><td colspan=3 style="text-align:center;color:#888">No suppression data</td></tr>'}</tbody>
      </table>
    </div>

    <div class=sec>
      <h2 class=sec-title>Suppression by Reason</h2>
      <table>
        <thead><tr><th>Reason</th><th style=text-align:center>Count</th><th style=text-align:center>% of Total</th></tr></thead>
        <tbody>{reason_rows if reason_rows else '<tr><td colspan=3 style="text-align:center;color:#888">No suppression data</td></tr>'}</tbody>
      </table>
    </div>

    <div class=sec>
      <h2 class=sec-title>Recommendations</h2>
      <ul>{rec_items}</ul>
    </div>

    <div class=sec>
      <h2 class=sec-title>Contact Details (First 20)</h2>
      <table>
        <thead><tr><th>Email</th><th>Source</th><th>Type</th><th>Reason</th></tr></thead>
        <tbody>{detail_rows if detail_rows else '<tr><td colspan=4 style="text-align:center;color:#888">No contacts</td></tr>'}</tbody>
      </table>
      {more_note}
    </div>

  </div>

  <div class=footer>
    <div class=footer-brand>Liberty Suppression Agent</div>
    <div>Generated: {date_str} {time_str} | Synced to: Suppression Register</div>
    <div>Libertad Capital &middot; Alternative Funding &middot; AGS Dev</div>
  </div>

</div>
</body>
</html>"""

    return html


def send_email(html_body, subject):
    """Send email via gog with HTML body string"""
    import subprocess

    cmd = [
        "gog", "gmail", "send",
        "--account", "v.rodriguez@allianceglobalsolutions.com",
        "--from", SENDER,
        "--to", RECIPIENT,
        "--subject", subject,
        "--body-html", html_body
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Email sent to {RECIPIENT}")
        return True
    else:
        print(f"Error: {result.stderr}")
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Send suppression + campaign report email")
    parser.add_argument("--dry", action="store_true", help="Generate report without sending")
    parser.add_argument("--recipient", default=RECIPIENT, help="Override recipient email")
    args = parser.parse_args()

    print("Liberty Daily Report")
    print("=" * 40)

    print("Fetching suppression data...")
    contacts = fetch_all_suppressed()
    print(f"  {len(contacts)} suppressed contacts")

    print("Fetching sheet summary...")
    sheet_total = get_sheet_summary()
    print(f"  {sheet_total} emails in sheet")

    print("Fetching campaign stats...")
    campaigns, workflows = fetch_campaign_stats()
    print(f"  {len(campaigns)} email campaigns with stats")
    for c in campaigns:
        print(f"    - {c['source']}: {c['name'][:40]} | sent:{c['sent']} open:{c['open_rate']}% click:{c['click_rate']}%")
    print(f"  {len(workflows)} drip workflows with stats")
    for w in workflows:
        print(f"    - {w['source']}: {w['name'][:40]} | sent:{w['sent']} open:{w['open_rate']}% click:{w['click_rate']}%")

    print("Building HTML report...")
    html = build_html_report(contacts, sheet_total, campaigns, workflows)

    report_file = project_root / "data" / "suppression_report.html"
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, "w") as f:
        f.write(html)
    print(f"  Saved: {report_file}")

    if args.dry:
        print("\n[DRY RUN] Email not sent.")
        return

    subject = f"Daily Report - {len(contacts)} suppressed | {len(campaigns)} campaigns | {len(workflows)} workflows | {datetime.datetime.now().strftime('%B %d, %Y')}"
    print(f"\nSending to {args.recipient}...")
    send_email(html, subject)
    print("\nDone!")


if __name__ == "__main__":
    main()
