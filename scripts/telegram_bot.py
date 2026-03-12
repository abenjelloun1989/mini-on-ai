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
  /go       — approve pending idea (or tap button in chat)
  /nogo     — reject pending idea (or tap button in chat)
  /holdon        — pause the pipeline daemon
  /resume        — resume the pipeline daemon
  /projectphases — show project roadmap and current phase
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

from lib.utils import read_json, write_json, timestamp, log, ROOT

DAEMON_STATE = ROOT / "data/daemon-state.json"

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


# --- Approval helpers ---

def handle_approval(decision: str) -> str:
    """Write approval decision to state file. Returns reply text."""
    try:
        state = read_json("data/approval-state.json")
    except Exception:
        state = {}

    if state.get("status") != "pending":
        return "ℹ️ No idea is currently waiting for approval."

    state["status"] = decision  # "approved" or "rejected"
    state["decided_at"] = timestamp()
    write_json("data/approval-state.json", state)

    idea_title = state.get("idea", {}).get("title", "idea")
    if decision == "approved":
        return f"✅ <b>Go!</b> Building: <i>{idea_title}</i>\nI'll notify you when it's published."
    else:
        return f"❌ <b>No Go.</b> Skipping: <i>{idea_title}</i>\n\nThe pipeline is now paused. Send /resume whenever you want the next idea."


# --- Command handlers ---

def set_daemon_paused(paused: bool) -> str:
    try:
        DAEMON_STATE.write_text(json.dumps({"paused": paused}))
        if paused:
            return "⏸ <b>Pipeline paused.</b>\nThe daemon will finish any current approval wait, then stop.\nSend /resume to start again."
        else:
            return "▶️ <b>Pipeline resumed.</b>\nThe daemon will start a new cycle shortly."
    except Exception as e:
        return f"❌ Error updating daemon state: {e}"


def cmd_projectphases() -> str:
    try:
        catalog = read_json("data/product-catalog.json")
        product_count = len(catalog.get("products", []))
    except Exception:
        product_count = 0

    return (
        "🗺 <b>Project Phases</b>\n\n"
        "✅ <b>V1 — Core Pipeline</b>\n"
        "   trend-scan → rank → generate → package → site\n\n"
        "✅ <b>V2 — Live Factory</b>\n"
        "   GitHub Pages • Telegram approval gate\n"
        "   Continuous daemon • License + README\n\n"
        f"📦 <b>Current:</b> {product_count} product{'s' if product_count != 1 else ''} published\n\n"
        "─────────────────────\n\n"
        "🔜 <b>M11 — Publisher</b>\n"
        "   Auto-post to Gumroad + Reddit after each product\n\n"
        "🔜 <b>M12 — Real Trend Scanning</b>\n"
        "   Replace AI-generated ideas with Google Trends\n"
        "   + Reddit scraping for real demand signals\n\n"
        "🔜 <b>M13 — More Product Types</b>\n"
        "   Checklists, templates, swipe files, mini-guides\n\n"
        "🔜 <b>M14 — Analytics</b>\n"
        "   Track downloads — feed best performers back\n"
        "   into idea scoring\n\n"
        "🔜 <b>M15 — Email List</b>\n"
        "   Capture audience you own (Beehiiv / Kit embed)"
    )


def cmd_help() -> str:
    return (
        "🏭 <b>mini-on-ai factory</b>\n\n"
        "/status — last run + product count\n"
        "/products — list published products\n"
        "/ideas — top ideas in backlog\n"
        "/run — trigger pipeline now\n"
        "/run [seed] — e.g. /run marketing\n"
        "/run all — run 4 seeds in sequence\n"
        "/go — approve pending idea\n"
        "/nogo — reject pending idea\n"
        "/holdon — pause the pipeline\n"
        "/resume — resume the pipeline\n"
        "/projectphases — roadmap and current phase\n"
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

        # Show pause and approval status
        approval_note = ""
        try:
            daemon_state = json.loads((ROOT / "data/daemon-state.json").read_text())
            if daemon_state.get("paused"):
                approval_note += "\n\n⏸ <b>Pipeline is paused.</b> Send /resume to restart."
        except Exception:
            pass
        try:
            approval = read_json("data/approval-state.json")
            if approval.get("status") == "pending":
                idea_title = approval.get("idea", {}).get("title", "?")
                approval_note += f"\n\n⏳ <b>Waiting for approval:</b> {idea_title}\nReply /go or /nogo"
        except Exception:
            pass

        return (
            f"📊 <b>Factory Status</b>\n\n"
            f"Products published: <b>{product_count}</b>\n"
            f"Total runs: {len(runs)}\n\n"
            f"Last run: {status_icon} {last['status']}\n"
            f"Product: {product_name}\n"
            f"Duration: {duration}s\n"
            f"At: {started} UTC"
            f"{approval_note}"
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
            if idea.get("status") == "produced":
                status = "✅ produced"
            elif idea.get("status") == "rejected":
                status = "❌ rejected"
            elif idea.get("selected"):
                status = "🎯 selected"
            else:
                status = f"score: {idea['score']}"
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

    if lower == "/projectphases":
        return cmd_projectphases()

    if lower == "/holdon":
        return set_daemon_paused(True)

    if lower == "/resume":
        return set_daemon_paused(False)

    if lower == "/go":
        return handle_approval("approved")

    if lower == "/nogo" or lower == "/no":
        return handle_approval("rejected")

    if lower == "/run all":
        send("🚀 Starting 4 pipeline runs (marketing, freelancing, writing, coding).\nYou'll get a Telegram message after each one.")
        for seed in SEEDS_ALL:
            run_pipeline_bg(seed)
            time.sleep(10)
        return None

    if lower.startswith("/run"):
        parts = text.split(None, 1)
        seed = parts[1].strip() if len(parts) > 1 else ""
        seed_note = f" with seed: <i>{seed}</i>" if seed else ""
        run_pipeline_bg(seed)
        return f"🚀 Pipeline started{seed_note}.\nI'll send an approval request when an idea is ready."

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

            # Handle inline button taps (callback queries)
            callback_query = update.get("callback_query")
            if callback_query:
                cq_id = callback_query.get("id")
                cq_chat_id = str(callback_query.get("from", {}).get("id", ""))
                cq_data = callback_query.get("data", "")
                log("bot", f"Callback query: data={cq_data} from={cq_chat_id}")

                if cq_chat_id == str(CHAT_ID) and cq_data.startswith("approval:"):
                    decision = "approved" if cq_data == "approval:go" else "rejected"
                    log("bot", f"Approval decision: {decision}")
                    reply = handle_approval(decision)
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    send(reply, cq_chat_id)
                else:
                    log("bot", f"Callback ignored: chat_id mismatch or unknown data")
                continue

            # Handle text commands
            message = update.get("message", {})
            text = message.get("text", "").strip()
            chat_id = str(message.get("chat", {}).get("id", ""))

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
