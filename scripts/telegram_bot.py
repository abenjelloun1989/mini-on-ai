#!/usr/bin/env python3
"""
telegram_bot.py
Persistent Telegram bot that listens for commands and controls the factory.

Run as a background service (see docs/launchd-setup.md).

Commands:
  /help     — show available commands
  /status   — last pipeline run + product count
  /products — list all published products
  /ideas    — show top scored ideas in backlog
  /run      — trigger pipeline (optional: /run marketing)
  /run all  — run pipeline 4x with preset seeds
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, log, ROOT

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID", "")

SEEDS_ALL = ["marketing", "freelancing", "writing", "coding"]


def api(method: str, data: dict = None) -> dict:
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    payload = json.dumps(data or {}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def send(text: str, chat_id: str = None) -> None:
    api("sendMessage", {
        "chat_id": chat_id or CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    })


def get_updates(offset: int) -> list:
    try:
        result = api("getUpdates", {"offset": offset, "timeout": 20, "limit": 10})
        return result.get("result", [])
    except Exception as e:
        log("bot", f"getUpdates error: {e}")
        return []


# --- Command handlers ---

def cmd_help() -> str:
    return (
        "🏭 <b>mini-on-ai factory</b>\n\n"
        "/status — last run + product count\n"
        "/products — list published products\n"
        "/ideas — top ideas in backlog\n"
        "/run — trigger pipeline now\n"
        "/run [seed] — e.g. /run marketing\n"
        "/run all — run 4 seeds in sequence\n"
        "/help — show this message"
    )


def cmd_status() -> str:
    try:
        catalog = read_json("data/product-catalog.json")
        pipeline_log = read_json("data/pipeline-log.json")
        runs = pipeline_log.get("runs", [])

        product_count = len(catalog.get("products", []))

        if not runs:
            return f"📊 <b>Status</b>\n\nProducts: {product_count}\nNo pipeline runs yet."

        last = runs[-1]
        status_icon = "✅" if last["status"] == "success" else "❌"
        product_name = last.get("product", {}).get("title", "—") if last.get("product") else "—"
        duration = last.get("duration_seconds", "?")
        started = last.get("started_at", "?")[:16].replace("T", " ")

        return (
            f"📊 <b>Factory Status</b>\n\n"
            f"Products published: <b>{product_count}</b>\n"
            f"Total runs: {len(runs)}\n\n"
            f"Last run: {status_icon} {last['status']}\n"
            f"Product: {product_name}\n"
            f"Duration: {duration}s\n"
            f"At: {started} UTC"
        )
    except Exception as e:
        return f"❌ Error reading status: {e}"


def cmd_products() -> str:
    try:
        catalog = read_json("data/product-catalog.json")
        products = catalog.get("products", [])
        if not products:
            return "📦 No products published yet."

        site_url = os.getenv("SITE_URL", "http://localhost:8080")
        lines = [f"📦 <b>Products ({len(products)})</b>\n"]
        for i, p in enumerate(products, 1):
            tags = " · ".join(p.get("tags", []))
            lines.append(
                f"{i}. <b>{p['title']}</b>\n"
                f"   {p['description']}\n"
                f"   🔗 {site_url}/products/{p['id']}.html"
            )
        return "\n\n".join(lines)
    except Exception as e:
        return f"❌ Error reading products: {e}"


def cmd_ideas() -> str:
    try:
        backlog = read_json("data/idea-backlog.json")
        ideas = backlog.get("ideas", [])
        if not ideas:
            return "💡 Idea backlog is empty. Run /run to scan for ideas."

        scored = [i for i in ideas if i.get("score") is not None]
        unscored = [i for i in ideas if i.get("score") is None]
        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[:5]

        lines = [f"💡 <b>Idea Backlog</b> ({len(ideas)} total, {len(unscored)} unscored)\n"]
        for i, idea in enumerate(top, 1):
            status = "✅ produced" if idea.get("status") == "produced" else ("🎯 selected" if idea.get("selected") else f"score: {idea['score']}")
            lines.append(f"{i}. <b>{idea['title']}</b>\n   {status}")

        if not top:
            lines.append("No scored ideas yet.")
        return "\n\n".join(lines)
    except Exception as e:
        return f"❌ Error reading backlog: {e}"


def run_pipeline_bg(seed: str = "") -> None:
    """Run pipeline in background subprocess."""
    cmd = [sys.executable, str(ROOT / "scripts/run_pipeline.py")]
    if seed:
        cmd += ["--seed", seed]

    log("bot", f"Spawning pipeline subprocess (seed={seed or 'none'})")
    subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        stdout=open(ROOT / "logs/pipeline.log", "a"),
        stderr=open(ROOT / "logs/pipeline-error.log", "a"),
    )


def handle_command(text: str) -> str:
    text = text.strip()
    lower = text.lower()

    if lower == "/help" or lower.startswith("/start"):
        return cmd_help()

    if lower == "/status":
        return cmd_status()

    if lower == "/products":
        return cmd_products()

    if lower == "/ideas":
        return cmd_ideas()

    if lower == "/run all":
        send("🚀 Starting 4 pipeline runs (marketing, freelancing, writing, coding).\nYou'll get a Telegram message after each one.")
        for seed in SEEDS_ALL:
            run_pipeline_bg(seed)
            time.sleep(10)  # slight delay between spawns
        return None  # already sent message above

    if lower.startswith("/run"):
        parts = text.split(None, 1)
        seed = parts[1].strip() if len(parts) > 1 else ""
        seed_note = f" with seed: <i>{seed}</i>" if seed else ""
        run_pipeline_bg(seed)
        return f"🚀 Pipeline started{seed_note}.\nI'll notify you when it's done (~2 min)."

    return f"Unknown command: <code>{text}</code>\n\nType /help for available commands."


def main():
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN not set. Exiting.")
        sys.exit(1)

    log("bot", f"Starting Telegram bot (chat_id: {CHAT_ID})")
    send("🤖 <b>mini-on-ai bot online</b>\n\nType /help to see commands.")

    offset = 0
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message", {})
            text = message.get("text", "").strip()
            chat_id = str(message.get("chat", {}).get("id", ""))

            # Only respond to the owner
            if chat_id != str(CHAT_ID):
                log("bot", f"Ignoring message from unknown chat_id: {chat_id}")
                continue

            if not text:
                continue

            log("bot", f"Command: {text}")
            try:
                reply = handle_command(text)
                if reply:
                    send(reply, chat_id)
            except Exception as e:
                log("bot", f"Error handling command: {e}")
                send(f"❌ Error: {e}", chat_id)

        time.sleep(1)


if __name__ == "__main__":
    main()
