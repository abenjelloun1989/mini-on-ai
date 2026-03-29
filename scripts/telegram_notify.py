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


def send_gumroad_description(meta: dict) -> bool:
    """Send the Gumroad copy-paste description for a newly published product."""
    desc = meta.get("gumroad_description")
    if not desc:
        return False
    title = meta.get("title", "New product")
    text = (
        f"📋 <b>Gumroad description — {title}</b>\n\n"
        f"<code>{desc}</code>"
    )
    try:
        send_telegram(text)
        log("telegram", f"Gumroad description sent for {meta.get('id', '?')}")
        return True
    except Exception as e:
        log("telegram", f"Warning: could not send Gumroad description: {e}")
        return False


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

    result = send_telegram(text)

    # Send Gumroad description as a follow-up message if available
    if latest.get("status") == "success":
        product = latest.get("product") or {}
        if product.get("gumroad_description"):
            send_gumroad_description(product)

    return result


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


def send_tweet_draft(product_id: str, tweet_text: str) -> bool:
    """Send a tweet draft to Telegram with Post / Regenerate buttons."""
    char_count = len(tweet_text)
    text = (
        f"🐦 <b>Tweet draft</b> ({char_count}/280 chars)\n\n"
        f"<code>{tweet_text}</code>\n\n"
        f"<i>Tap the text above to copy, then paste into X.</i>"
    )
    # Telegram callback_data max = 64 bytes; truncate product_id to fit
    pid_short = product_id[:50]
    buttons = [
        {"text": "✅ Done",        "callback_data": f"tweet:done:{pid_short}"},
        {"text": "🔄 Regenerate",  "callback_data": f"tweet:regen:{pid_short}"},
    ]
    try:
        _send_with_buttons(text, buttons)
        log("twitter", f"Tweet draft sent for product {product_id}")
        return True
    except Exception as e:
        log("twitter", f"Warning: could not send tweet draft: {e}")
        return False


def send_karma_draft(post: dict, comment: str, score: int, product_hint=None) -> bool:
    """
    Send a karma scout result to Telegram.
    Includes the post title, link, and a copy-paste comment draft with a Skip button.
    product_hint: optional (name, url) tuple shown as a footer line.
    """
    post_id = post.get("post_id", "")
    sub = post.get("subreddit", "?")
    title = post.get("title", "")
    url = post.get("url", "")
    short_url = url.replace("https://reddit.com", "reddit.com")

    text = (
        f"🎯 <b>r/{sub}</b>  |  Score {score}\n\n"
        f"<i>\"{title[:120]}\"</i>\n"
        f"<a href=\"{url}\">{short_url[:70]}</a>\n\n"
        f"💬 <b>Draft comment</b> (tap to copy):\n"
        f"<code>{comment}</code>"
    )
    if product_hint:
        name, hint_url = product_hint
        text += f"\n\n💡 <b>Your product:</b> <a href=\"{hint_url}\">{name}</a>"
    buttons = [
        {"text": "⏭ Skip", "callback_data": f"karma:skip:{post_id}"},
    ]
    try:
        _send_with_buttons(text, buttons)
        log("telegram", f"Karma draft sent for post {post_id}")
        return True
    except Exception as e:
        log("telegram", f"Warning: could not send karma draft: {e}")
        return False


def send_comparison_table(proposals: list) -> bool:
    """Send a quick comparison table for all proposals before the first detailed one."""
    if not proposals:
        return False

    transport_icons = {"train": "🚄", "vol": "✈️", "flight": "✈️", "voiture": "🚗", "bus": "🚌"}

    # Find cheapest and best weather for badges
    prices = [p.get("total_estimate_eur", 9999) for p in proposals]
    min_price = min(prices)

    # Parse temperatures for "best weather" badge
    def extract_temp(weather_note: str) -> int:
        import re
        m = re.search(r"(\d+)", weather_note or "")
        return int(m.group(1)) if m else 0

    temps = [extract_temp(p.get("weather_note", "")) for p in proposals]
    max_temp = max(temps) if temps else 0

    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    lines = ["📊 <b>Comparaison rapide:</b>\n"]

    for i, p in enumerate(proposals):
        num = number_emojis[i] if i < len(number_emojis) else f"{i+1}."
        dest = _he(p.get("destination", "?").split(",")[0])
        transport = p.get("transport", {})
        t_icon = transport_icons.get(transport.get("type", "").lower(), "🚌")
        t_dur = _he(transport.get("duration", "?"))
        weather = _he(p.get("weather_note", "—"))
        price = p.get("total_estimate_eur", "?")

        badges = []
        if price == min_price:
            badges.append("← Meilleur prix")
        if temps[i] == max_temp and max_temp > 0 and price != min_price:
            badges.append("← Meilleur temps")

        badge_str = f"  <i>{' / '.join(badges)}</i>" if badges else ""
        lines.append(f"{num}  {dest}   {t_icon} {t_dur}   🌡 {weather}   💰 ~{price}€{badge_str}")

    lines.append("\nTapez <b>1</b>, <b>2</b> ou <b>3</b> pour sauter directement à une option.")
    lines.append("Ou utilisez ➡️ pour parcourir dans l'ordre.")

    text = "\n".join(lines)
    try:
        send_telegram(text)
        log("telegram", "Comparison table sent")
        return True
    except Exception as e:
        log("telegram", f"Warning: could not send comparison table: {e}")
        return False


def send_holiday_question(question: str, step: int, total: int) -> bool:
    """Send a holiday planning question with step indicator."""
    text = f"🏝️ <b>Planification voyage</b> ({step}/{total})\n\n{question}"
    try:
        send_telegram(text)
        return True
    except Exception as e:
        log("telegram", f"Warning: could not send holiday question: {e}")
        return False


def _he(text: str) -> str:
    """Escape HTML special characters for Telegram HTML parse mode."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send_holiday_proposal(proposal: dict, index: int, total: int) -> bool:
    """Send one trip proposal with navigation buttons."""
    emoji = proposal.get("emoji", "🌍")
    title = _he(proposal.get("title", "Proposition"))
    destination = _he(proposal.get("destination", ""))
    why = _he(proposal.get("why", ""))
    weather = _he(proposal.get("weather_note", ""))
    stroller = _he(proposal.get("stroller_note", ""))
    journey_time = _he(proposal.get("journey_time_note", ""))
    nights = proposal.get("nights", "?")
    total_eur = proposal.get("total_estimate_eur", "?")

    transport = proposal.get("transport", {})
    t_desc = _he(transport.get("description", ""))
    t_price = transport.get("total_transport_eur", "?")
    t_duration = _he(transport.get("duration", ""))
    t_notes = _he(transport.get("notes", ""))

    accom = proposal.get("accommodation", {})
    a_desc = _he(accom.get("description", ""))
    a_price_night = accom.get("price_per_night_eur", "?")
    a_total = accom.get("total_accommodation_eur", "?")
    a_notes = _he(accom.get("notes", ""))

    booking_links = proposal.get("booking_links", [])

    lines = [
        f"{emoji} <b>Option {index}/{total} — {title}</b>",
        f"📍 {destination} · {nights} nuits",
        "",
        "<b>Pourquoi cette option?</b>",
        why,
        "",
    ]

    if journey_time:
        lines.append(f"🕐 <i>{journey_time}</i>")
    if weather:
        lines.append(f"☀️ <i>{weather}</i>")
    if stroller:
        lines.append(f"🦽 <i>{stroller}</i>")
    if journey_time or weather or stroller:
        lines.append("")

    lines.append(f"<b>Transport:</b> {t_desc}")
    if t_duration:
        lines.append(f"⏱ {t_duration}")
    lines.append(f"💶 ~{t_price}€ (transport total)")
    if t_notes:
        lines.append(f"<i>{t_notes}</i>")

    lines += [
        "",
        f"<b>Hébergement:</b> {a_desc}",
        f"💶 ~{a_price_night}€/nuit · ~{a_total}€ total",
    ]
    if a_notes:
        lines.append(f"<i>{a_notes}</i>")

    lines += [
        "",
        f"💰 <b>Estimation totale: ~{total_eur}€</b>",
        "<i>Prix estimés — cliquez les liens pour les prix en temps réel</i>",
        "",
        "<b>Réserver:</b>",
    ]
    for link in booking_links:
        label = _he(link.get("label", "Réserver"))
        url = link.get("url", "#")
        lines.append(f'<a href="{url}">{label}</a>')

    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:3990] + "\n..."

    # Navigation buttons
    buttons = []
    if index < total:
        buttons.append({"text": f"➡️ Option suivante ({index + 1}/{total})", "callback_data": f"holiday:next:{index}"})
    buttons.append({"text": "🔁 Relancer (mêmes critères)", "callback_data": "holiday:relaunch"})
    buttons.append({"text": "✏️ Modifier critères", "callback_data": "holiday:modify"})

    try:
        _send_with_buttons(text, buttons)
        log("telegram", f"Holiday proposal {index}/{total} sent")
        return True
    except Exception as e:
        log("telegram", f"Warning: could not send holiday proposal {index}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send Telegram pipeline report")
    parser.add_argument("--message", default=None, help="Custom message to send")
    args = parser.parse_args()
    telegram_report(args.message)


if __name__ == "__main__":
    main()
