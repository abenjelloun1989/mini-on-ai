#!/usr/bin/env python3
"""
telegram_notify.py
Sends a pipeline run report to a Telegram chat.

Usage: python3 scripts/telegram_notify.py
       python3 scripts/telegram_notify.py --message "Custom message"
"""

import argparse
import os
import sys
import urllib.request
import urllib.parse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, log


def send_telegram(text: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        log("telegram", "TELEGRAM_BOT_TOKEN or TELEGRAM_OWNER_ID not set — skipping notification")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Telegram API error {resp.status}")

    log("telegram", "Message sent successfully")
    return True


def telegram_report(override_message: str = None) -> bool:
    if override_message:
        return send_telegram(override_message)

    pipeline_log = read_json("data/pipeline-log.json")
    runs = pipeline_log.get("runs", [])

    if not runs:
        log("telegram", "No pipeline runs found in log")
        return False

    latest = runs[-1]
    site_url = os.getenv("SITE_URL", "file://./site")

    if latest.get("status") == "success":
        product = latest.get("product") or {}
        text = "\n".join([
            "✅ <b>New product published</b>",
            "",
            f"📦 <b>{product.get('title', 'Unknown')}</b>",
            product.get("description", ""),
            "",
            f"🔗 {site_url}/products/{product.get('id', '')}.html",
            f"🕐 Completed in {latest.get('duration_seconds', '?')}s",
        ])
    else:
        text = "\n".join([
            "❌ <b>Pipeline failed</b>",
            "",
            f"Stage: <code>{latest.get('failed_stage', 'unknown')}</code>",
            f"Error: {latest.get('error', 'unknown error')}",
            f"🕐 {latest.get('started_at', '?')}",
        ])

    return send_telegram(text)


def send_approval_request(idea: dict) -> bool:
    """Send idea proposal with Go / No Go inline buttons. Returns True if sent."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log("telegram", "Credentials missing — cannot send approval request")
        return False

    tags = " · ".join(idea.get("tags") or [])
    text = (
        f"💡 <b>New product idea ready</b>\n\n"
        f"<b>{idea.get('title', '?')}</b>\n"
        f"{idea.get('description', '')}\n\n"
        f"Category: {idea.get('category', '?')}\n"
        f"Score: {idea.get('score', '?')}\n"
        + (f"Tags: {tags}\n" if tags else "") +
        f"\nShould I build this?"
    )
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "✅ Go", "callback_data": "approval:go"},
                {"text": "❌ No Go", "callback_data": "approval:nogo"},
            ]]
        },
    }).encode("utf-8")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Telegram API error {resp.status}")

    log("telegram", "Approval request sent")
    return True


def main():
    parser = argparse.ArgumentParser(description="Send Telegram pipeline report")
    parser.add_argument("--message", default=None, help="Custom message to send")
    args = parser.parse_args()
    telegram_report(args.message)


if __name__ == "__main__":
    main()
