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
        tokens = latest.get("tokens") or {}
        total_tokens = tokens.get("input_tokens", 0) + tokens.get("output_tokens", 0)
        cost_usd = tokens.get("estimated_cost_usd", 0.0)
        cost_str = f"${cost_usd:.4f}" if cost_usd >= 0.0001 else "&lt;$0.0001"
        token_line = f"🪙 {total_tokens:,} tokens ({tokens.get('input_tokens',0):,} in / {tokens.get('output_tokens',0):,} out) · {cost_str}"
        text = "\n".join([
            "✅ <b>New product published</b>",
            "",
            f"📦 <b>{product.get('title', 'Unknown')}</b>",
            product.get("description", ""),
            "",
            f"🔗 https://gumroad.com/products/new",
            f"🕐 Completed in {latest.get('duration_seconds', '?')}s",
            token_line,
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


def _send_with_buttons(text: str, buttons: list) -> bool:
    """Send a Telegram message with inline keyboard buttons."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log("telegram", "Credentials missing — skipping")
        return False

    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [buttons]},
    }).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Telegram API error {resp.status}")
    return True


def send_reddit_approval(post: dict, brief: dict) -> bool:
    """
    Send a Reddit candidate to Telegram for approval.
    Buildable posts get [Build it / Skip] buttons.
    Non-buildable posts show a copy-paste Claude Code prompt + [Skip] button.
    """
    score = brief.get("score", 0)
    category = brief.get("category", "?")
    buildable = brief.get("buildable", False)
    post_id = post.get("post_id", "")
    sub = post.get("subreddit", "?")
    author = post.get("author", "?")
    title = post.get("title", "")
    url = post.get("url", "")
    short_url = url.replace("https://reddit.com", "")

    if buildable:
        text = (
            f"🔍 <b>Reddit need detected</b>\n"
            f"r/{sub} · u/{author}\n\n"
            f"<i>\"{title[:120]}\"</i>\n"
            f"<a href=\"{url}\">{short_url[:60]}</a>\n\n"
            f"Proposed product:\n"
            f"📦 <b>{brief.get('title', '?')}</b> ({category})\n"
            f"{brief.get('description', '')}\n"
            f"Score: {score}/100"
        )
        buttons = [
            {"text": "✅ Build it", "callback_data": f"reddit:build:{post_id}"},
            {"text": "⏭ Skip", "callback_data": f"reddit:skip:{post_id}"},
        ]
    else:
        why = brief.get("why_not_buildable", "unsupported product type")
        build_prompt = brief.get("build_prompt", "")
        # Telegram max message = 4096 chars; truncate prompt if needed
        max_prompt = 3000
        prompt_display = build_prompt[:max_prompt] + ("…" if len(build_prompt) > max_prompt else "")
        text = (
            f"🔍 <b>Reddit need detected</b> (pipeline can't build this yet)\n"
            f"r/{sub} · u/{author}\n\n"
            f"<i>\"{title[:120]}\"</i>\n"
            f"<a href=\"{url}\">{short_url[:60]}</a>\n\n"
            f"Proposed: <b>{brief.get('title', '?')}</b> (category: {category})\n"
            f"Why not buildable: {why}\n\n"
            f"📋 <b>Paste into Claude Code to add capability:</b>\n"
            f"<pre>{prompt_display}</pre>"
        )
        buttons = [
            {"text": "⏭ Skip", "callback_data": f"reddit:skip:{post_id}"},
        ]

    try:
        _send_with_buttons(text, buttons)
        log("telegram", f"Reddit approval sent for post {post_id}")
        return True
    except Exception as e:
        log("telegram", f"Warning: could not send reddit approval: {e}")
        return False


def send_reddit_built(post: dict, meta: dict, product_url: str, reply_text: str) -> bool:
    """
    Send a notification after a Reddit-sourced product has been built.
    Includes the product link and a ready-to-paste Reddit reply.
    """
    sub = post.get("subreddit", "?")
    text = (
        f"✅ <b>Built for Reddit!</b>\n\n"
        f"📦 <b>{meta.get('title', '?')}</b>\n"
        f"{meta.get('description', '')}\n\n"
        f"🔗 {product_url}\n\n"
        f"📋 <b>Copy-paste reply for r/{sub}:</b>\n"
        f"────────────────────\n"
        f"{reply_text}\n"
        f"────────────────────"
    )
    try:
        send_telegram(text)
        log("telegram", "Reddit built notification sent")
        return True
    except Exception as e:
        log("telegram", f"Warning: could not send reddit built notification: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send Telegram pipeline report")
    parser.add_argument("--message", default=None, help="Custom message to send")
    args = parser.parse_args()
    telegram_report(args.message)


if __name__ == "__main__":
    main()
