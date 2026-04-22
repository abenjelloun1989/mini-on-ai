#!/usr/bin/env python3
"""
email_blast.py — Send an email campaign to the Brevo list.

Usage:
  python3 scripts/email_blast.py --count
  python3 scripts/email_blast.py --subject "Subject" --body "Plain text body"
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import log

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
BREVO_LIST_ID = int(os.getenv("BREVO_LIST_ID", "2"))
SITE_URL      = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")
SENDER_NAME   = os.getenv("BREVO_SENDER_NAME", "mini-on-ai")
SENDER_EMAIL  = os.getenv("BREVO_SENDER_EMAIL", "kirozdormu@gmail.com")


def _brevo(method: str, path: str, body: dict = None) -> dict:
    """Make a Brevo REST API call. Returns parsed JSON response."""
    url  = f"https://api.brevo.com/v3{path}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, method=method)
    req.add_header("api-key", BREVO_API_KEY)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:  # nosec B310 -- URL constructed from hardcoded https:// base
            content = resp.read()
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise RuntimeError(f"Brevo {method} {path} → {e.code}: {err}") from None


def get_contact_count() -> int:
    """Return total active contacts in the list."""
    try:
        resp = _brevo("GET", f"/contacts/lists/{BREVO_LIST_ID}")
        return resp.get("totalSubscribers", 0)
    except Exception:
        return 0


def _text_to_html(text: str) -> str:
    """Convert plain text email body to a clean HTML email."""
    lines = text.strip().split("\n")
    html_lines = []
    in_ul = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            html_lines.append("")
            continue
        if stripped.startswith("→ ") or stripped.startswith("- "):
            if not in_ul:
                html_lines.append("<ul style='margin:8px 0;padding-left:20px;'>")
                in_ul = True
            item = stripped[2:].strip()
            html_lines.append(f"  <li style='margin-bottom:6px;'>{item}</li>")
        else:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            html_lines.append(f"<p style='margin:0 0 14px;'>{stripped}</p>")

    if in_ul:
        html_lines.append("</ul>")

    body_inner = "\n".join(html_lines)

    # Auto-link URLs
    body_inner = re.sub(
        r'(https?://[^\s<"]+)',
        r'<a href="\1" style="color:#6366F1;">\1</a>',
        body_inner
    )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:40px 16px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;padding:40px;max-width:600px;">
        <tr><td>
          <!-- Logo -->
          <p style="margin:0 0 32px;font-size:18px;font-weight:800;color:#6366F1;letter-spacing:-0.5px;">mini-on-ai</p>
          <!-- Body -->
          <div style="font-size:15px;line-height:1.7;color:#1f2937;">
{body_inner}
          </div>
          <!-- Footer -->
          <hr style="border:none;border-top:1px solid #e5e7eb;margin:32px 0;">
          <p style="margin:0;font-size:12px;color:#9ca3af;">
            You're receiving this because you downloaded a free product from
            <a href="{SITE_URL}" style="color:#6366F1;">mini-on-ai.com</a>.
            <br>To unsubscribe, reply with "unsubscribe".
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def create_and_send(subject: str, body: str) -> dict:
    """Create a campaign and send it immediately. Returns {campaign_id, recipients}."""
    html = _text_to_html(body)
    count = get_contact_count()
    name  = f"blast-{datetime.now().strftime('%Y%m%d-%H%M')}"

    campaign = _brevo("POST", "/emailCampaigns", {
        "name":       name,
        "subject":    subject,
        "type":       "classic",
        "sender":     {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "replyTo":    SENDER_EMAIL,
        "htmlContent": html,
        "recipients": {"listIds": [BREVO_LIST_ID]},
    })

    campaign_id = campaign.get("id")
    if not campaign_id:
        raise RuntimeError(f"Campaign creation failed: {campaign}")

    log("email-blast", f"Campaign created: id={campaign_id}")
    _brevo("POST", f"/emailCampaigns/{campaign_id}/sendNow")
    log("email-blast", f"Campaign sent to ~{count} subscribers")

    return {"campaign_id": campaign_id, "recipients": count}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count",    action="store_true", help="Show contact count and exit")
    parser.add_argument("--dry-run",  action="store_true", help="Preview without sending")
    parser.add_argument("--subject",  type=str, default="")
    parser.add_argument("--body",     type=str, default="")
    args = parser.parse_args()

    if args.count:
        n = get_contact_count()
        print(n)
        return

    if not args.subject or not args.body:
        print("Usage: email_blast.py --subject 'Subject' --body 'Body text'", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        n = get_contact_count()
        log("email-blast", f"[DRY RUN] Would send to {n} subscribers")
        log("email-blast", f"[DRY RUN] Subject: {args.subject}")
        log("email-blast", f"[DRY RUN] Body: {args.body[:100]}...")
        print(json.dumps({"dry_run": True, "recipients": n}))
        return

    result = create_and_send(args.subject, args.body)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
