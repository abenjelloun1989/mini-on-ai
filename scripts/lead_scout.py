#!/usr/bin/env python3
"""
lead_scout.py
Daily B2B lead-scout for ClauseGuard.

Finds N small law firms (1-10 lawyers) in English-speaking countries via
Claude (with WebSearch + WebFetch), drafts a personalized cold email per
lead, and sends a Telegram message with copy-paste-ready content.

Never auto-sends emails — user manually copies and sends from their own
mail client to keep anonymity and avoid spam-flagging.

Usage:
  python3 scripts/lead_scout.py             # find 10, draft, send to Telegram
  python3 scripts/lead_scout.py --max 5     # find 5
  python3 scripts/lead_scout.py --dry-run   # print to console, don't send
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, write_json, log, file_exists, ROOT
from lib.claude_cli import claude_call


STATE_FILE = "data/leads-state.json"


def load_state() -> dict:
    if not file_exists(STATE_FILE):
        return {"contacted": [], "skipped_domains": []}
    return read_json(STATE_FILE)


def save_state(state: dict) -> None:
    write_json(STATE_FILE, state)


def extract_json_block(text: str) -> str:
    """Pull the first JSON array from text (handles ```json fences and surrounding prose)."""
    # Strip code fences
    fence = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if fence:
        return fence.group(1)
    # Fallback: find first [...] block
    bracket = re.search(r"(\[\s*\{.*?\}\s*\])", text, re.DOTALL)
    if bracket:
        return bracket.group(1)
    raise ValueError("No JSON array found in Claude response")


def find_leads(n: int, state: dict) -> list:
    """Use Claude with WebSearch+WebFetch to find n new law-firm leads."""
    contacted = state.get("contacted", [])
    skipped = state.get("skipped_domains", [])

    system = (
        "You are a lead-research assistant. Find SMALL law firms (1-10 lawyers) "
        "in English-speaking countries (US, UK, Canada, Australia) doing business "
        "contracts, NDAs, or commercial law. Only return firms whose contact email "
        "is publicly visible on their official website. Return strict JSON only."
    )

    prompt = f"""Find {n} NEW small law firms (solo to ~10 lawyers) we have NOT contacted before.

Already-contacted emails to skip: {json.dumps(contacted)}
Already-known domains to skip: {json.dumps(skipped)}

Target countries: US, UK, Canada, Australia.
Mix cities. PREFER secondary markets (Austin, Denver, Portland, Manchester, Toronto, Melbourne, Calgary, Edinburgh, Adelaide) over Tier-1 (NYC, SF, London-City).

For each firm return JSON with these exact fields:
{{
  "name": "firm name",
  "lawyer": "primary lawyer name (or 'team' if no clear principal)",
  "city": "city",
  "country": "US | UK | CA | AU",
  "email": "verified-from-website@domain.com",
  "website": "https://firm-website.com",
  "size": "solo | boutique | mid",
  "practice_note": "1 sentence on why ClauseGuard fits their practice",
  "personalization_hook": "1 specific detail (a case, a service line, an article they wrote, a city niche) usable as opening hook"
}}

Use WebSearch to find candidates. Use WebFetch to verify each email is on the firm's public contact page. SKIP any firm whose email cannot be verified — never fabricate.

Return ONLY a JSON array of {n} objects. No prose, no commentary, no markdown fences other than ```json if needed."""

    log("lead-scout", f"Asking Claude to find {n} leads (with WebSearch+WebFetch)...")
    text, _ = claude_call(
        prompt,
        system=system,
        tools=["WebSearch", "WebFetch"],
        model="sonnet",
        timeout=900,
    )
    block = extract_json_block(text)
    leads = json.loads(block)
    if not isinstance(leads, list):
        raise ValueError("Claude returned non-list JSON")
    log("lead-scout", f"Got {len(leads)} candidate leads")
    return leads


CROSS_LINK_REGEX = re.compile(
    r"mini-on-ai\.com|ClauseGuard|InvoiceGuard|JobGuard", re.IGNORECASE
)
DEFAULT_SIGNATURE = (
    "\n\n— hello@mini-on-ai.com · mini-on-ai.com — small AI tools for "
    "freelancers & SMBs"
)


def draft_email(lead: dict) -> str:
    """Use Claude (Haiku) to draft a personalized cold email for one lead."""
    prompt = f"""Draft a cold email to {lead.get('lawyer', 'the lawyer')} at {lead.get('name', 'their firm')} ({lead.get('city', '')}, {lead.get('country', '')}).

Their hook: {lead.get('personalization_hook', '')}
Practice note: {lead.get('practice_note', '')}

Goal: introduce ClauseGuard — a Chrome extension that reviews contracts with AI in seconds.
ClauseGuard landing page: https://mini-on-ai.com/clauseguard.html

Constraints:
- Under 110 words
- Open with one specific detail about THEM (use the hook). Lead with a question or observation, not a pitch.
- End with a soft ask: invite them to check out the Chrome extension or ask a question — no phone call, no trial promise, no commitment language
- ClauseGuard is a Chrome extension — always name it as such, never imply it is a website or webapp
- No emojis, no marketing fluff, no "I hope this finds you well"
- No mention of free trials, phone calls, demos, or any offer the sender cannot guarantee
- Sender is "hello@mini-on-ai.com"
- MANDATORY: include a brief signature/P.S. that references mini-on-ai.com OR a related product (ClauseGuard / InvoiceGuard / JobGuard). Keep it natural, one short line.

Output format (no commentary, no markdown):
Subject: <subject line>

<body>

<signature line>"""

    text, _ = claude_call(prompt, model="haiku", timeout=120)
    text = text.strip()

    # Guard: ensure cross-link is present, append default signature if not
    if not CROSS_LINK_REGEX.search(text):
        text = text.rstrip() + DEFAULT_SIGNATURE

    return text


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def format_telegram(leads: list) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = [f"🎯 <b>{len(leads)} ClauseGuard B2B leads — {today}</b>", ""]
    for i, lead in enumerate(leads, 1):
        out.append(
            f"━━━ <b>Lead {i}: {html_escape(lead.get('name', '?'))}</b> "
            f"({html_escape(lead.get('city', '?'))}, {html_escape(lead.get('country', '?'))}) ━━━"
        )
        out.append(f"📧 <code>{html_escape(lead.get('email', '?'))}</code>")
        out.append(
            f"👤 {html_escape(lead.get('lawyer', '?'))} · "
            f"{html_escape(lead.get('size', '?'))}"
        )
        out.append(f"🔗 {html_escape(lead.get('website', '?'))}")
        out.append("")
        draft = lead.get("draft", "(missing draft)")
        out.append(f"<pre>{html_escape(draft)}</pre>")
        out.append("")
    out.append("📋 <b>Send instructions:</b>")
    out.append("1. Copy the email above")
    out.append("2. Paste into your mail client (from: hello@mini-on-ai.com)")
    out.append("3. Send ≤5/day to avoid spam-flagging")
    out.append("")
    out.append("Reply <code>SENT 1,3,5</code> to confirm which were actually sent. Unsent leads will be removed from dedupe and retried.")
    return "\n".join(out)


def chunk_message(msg: str, limit: int = 3800) -> list:
    """Telegram 4096-char limit; chunk by lead boundary."""
    if len(msg) <= limit:
        return [msg]
    parts = []
    buf = []
    size = 0
    for line in msg.splitlines(keepends=True):
        if size + len(line) > limit:
            parts.append("".join(buf))
            buf = [line]
            size = len(line)
        else:
            buf.append(line)
            size += len(line)
    if buf:
        parts.append("".join(buf))
    return parts


def main():
    parser = argparse.ArgumentParser(description="Daily ClauseGuard lead scout")
    parser.add_argument("--max", type=int, default=10, help="Number of leads (default 10)")
    parser.add_argument("--dry-run", action="store_true", help="Print to console, don't send Telegram or update state")
    args = parser.parse_args()

    state = load_state()
    log("lead-scout", f"Dedupe state: {len(state.get('contacted', []))} contacted, {len(state.get('skipped_domains', []))} skipped domains")

    try:
        leads = find_leads(args.max, state)
    except Exception as e:
        log("lead-scout", f"ERROR finding leads: {e}")
        if not args.dry_run:
            from telegram_notify import send_telegram
            send_telegram(f"⚠️ lead-scout failed: {e}")
        sys.exit(1)

    if len(leads) < 3:
        log("lead-scout", f"Only {len(leads)} leads — too few, aborting send")
        if not args.dry_run:
            from telegram_notify import send_telegram
            send_telegram(f"⚠️ lead-scout: only {len(leads)} leads found today, skipping send")
        sys.exit(1)

    # Draft email for each
    for i, lead in enumerate(leads, 1):
        try:
            log("lead-scout", f"Drafting email {i}/{len(leads)} for {lead.get('name', '?')}...")
            lead["draft"] = draft_email(lead)
        except Exception as e:
            lead["draft"] = f"(draft failed: {e})"

    msg = format_telegram(leads)

    if args.dry_run:
        print(msg)
        log("lead-scout", "Dry run — not sending Telegram, not updating state")
        return

    # Send (chunked if needed)
    from telegram_notify import send_telegram
    chunks = chunk_message(msg)
    for i, chunk in enumerate(chunks, 1):
        send_telegram(chunk)
        log("lead-scout", f"Sent Telegram chunk {i}/{len(chunks)}")

    # Update state — optimistically mark as contacted; user can untag via Telegram reply
    new_emails = [l["email"] for l in leads if l.get("email")]
    state.setdefault("contacted", []).extend(new_emails)
    new_domains = []
    for l in leads:
        site = l.get("website", "")
        m = re.match(r"https?://(?:www\.)?([^/]+)", site)
        if m:
            new_domains.append(m.group(1))
    state.setdefault("skipped_domains", []).extend(new_domains)
    # Dedupe state
    state["contacted"] = sorted(set(state["contacted"]))
    state["skipped_domains"] = sorted(set(state["skipped_domains"]))
    save_state(state)

    # Daily archive
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    write_json(f"data/leads-{today}.json", leads)
    log("lead-scout", f"Done. {len(leads)} leads sent + archived to data/leads-{today}.json")


if __name__ == "__main__":
    main()
