#!/usr/bin/env python3
"""
telegram_bot.py
Persistent Telegram bot that listens for commands and controls the factory.

Run as a background service (see docs/launchd-setup.md).

Commands:
  /run      — generate a new product (e.g. /run marketing)
  /reddit   — scan Reddit, propose up to 10 products
  /go       — approve pending idea → build it
  /skip     — skip pending idea
  /pause    — pause the factory daemon
  /resume   — resume the factory daemon
  /status   — last run, product count, API costs
  /products — all published products with links
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

from lib.utils import read_json, write_json, timestamp, log, ROOT, get_run_token_summary

DAEMON_STATE = ROOT / "data/daemon-state.json"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID", "")

SEEDS_ALL = ["marketing", "freelancing", "writing", "coding"]

# ── Holiday planner ────────────────────────────────────────────────────────────

HOLIDAY_QUESTIONS = [
    ("dates",         "✈️ <b>Quand voulez-vous partir?</b>\n\nDates précises ou période approximative? Vous êtes flexible?"),
    ("budget",        "💰 <b>Quel est votre budget total?</b>\n\nTransport + hébergement, pour les 3 (2 adultes + enfant)."),
    ("destination",   "🌍 <b>Avez-vous une destination en tête?</b>\n\nQuelque chose de précis, ou ouvert aux suggestions? Des pays à éviter?"),
    ("trip_type",     "🏖️ <b>Quel type de voyage?</b>\n\nBord de mer, ville, nature, montagne, repos, culture — ou un mix?"),
    ("journey_time",  "⏱️ <b>Combien de temps max pour le trajet?</b>\n\nEx: 3h en train, 2h de vol, pas plus de 5h porte-à-porte. On évite la voiture sauf si moins d'1h."),
    ("accommodation", "🏨 <b>Hôtel ou Airbnb?</b>\n\nDes exigences particulières? (piscine, vue mer, accès poussette, lit bébé, ascenseur...)"),
    ("nights",        "🌙 <b>Combien de nuits environ?</b>"),
    ("extras",        "✅ <b>Autre chose à savoir?</b>\n\nContraintes, envies particulières, choses à absolument éviter.\n\nTapez <b>go</b> quand vous êtes prêt pour que je lance la recherche."),
]

KNOWN_CATEGORIES = {
    "prompt-packs":       ("Prompt Pack",        "20–30 ready-to-use prompts"),
    "checklist":          ("Checklist",           "structured decision/action list"),
    "swipe-file":         ("Swipe File",          "copy-ready examples and templates"),
    "mini-guide":         ("Mini Guide",          "concise practitioner guide"),
    "n8n-template":       ("n8n Template",        "ready-to-import automation workflow"),
    "claude-code-skill":  ("Claude Code Skill",   "full configuration guide for a Claude Code skill"),
}


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
        msg = str(e)
        log("bot", f"getUpdates error: {msg}")
        if "409" in msg:
            time.sleep(30)  # back off long enough for old instance to fully die
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


def cmd_seturl(args: str) -> str:
    """Handle /seturl {product_id} {gumroad_url}"""
    import subprocess
    parts = args.strip().split(None, 1)
    if len(parts) < 2:
        return (
            "Usage: <code>/seturl {product_id} {gumroad_url}</code>\n\n"
            "Example:\n"
            "<code>/seturl prompts-my-product-20260312 https://minionai.gumroad.com/l/abcde</code>"
        )
    pid, url = parts[0], parts[1]

    try:
        # Save URL to meta + catalog
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/publish_product.py"), "--seturl", pid, url],
            capture_output=True, text=True, cwd=str(ROOT), timeout=30,
        )
        if result.returncode != 0:
            return f"❌ Error saving URL:\n<code>{result.stderr[:300]}</code>"

        # Rebuild all site pages so the Gumroad button appears everywhere
        rebuild = subprocess.run(
            [sys.executable, str(ROOT / "scripts/update_site.py"), "--rebuild-all"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=60,
        )
        if rebuild.returncode != 0:
            return f"⚠️ URL saved but site rebuild failed:\n<code>{rebuild.stderr[:300]}</code>"

        # Push to GitHub
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(ROOT), capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"publish: link Gumroad URL for {pid}"],
            cwd=str(ROOT), capture_output=True,
        )
        subprocess.run(
            ["git", "push"],
            cwd=str(ROOT), capture_output=True, timeout=60,
        )

        site_url = os.getenv("SITE_URL", "")
        return (
            f"✅ <b>Gumroad URL saved!</b>\n\n"
            f"Product: <code>{pid}</code>\n"
            f"Gumroad: {url}\n\n"
            f"Site rebuilt and pushed to GitHub.\n"
            f"Product page: {site_url}/products/{pid}.html"
        )
    except Exception as e:
        return f"❌ Unexpected error: {e}"


def cmd_setfree(pid: str) -> str:
    """Handle /setfree {product_id} — mark a product as free and rebuild site."""
    import json as _json
    pid = pid.strip()
    if not pid:
        return (
            "Usage: <code>/setfree {product_id}</code>\n\n"
            "Example:\n"
            "<code>/setfree skills-claude-code-skills-pack-codebase-onboard-20260315</code>\n\n"
            "Use /products to see product IDs."
        )
    try:
        # Update product-catalog.json
        catalog_path = ROOT / "data/product-catalog.json"
        with open(catalog_path) as f:
            catalog = _json.load(f)
        found = False
        for p in catalog["products"]:
            if p["id"] == pid:
                p["is_free"] = True
                found = True
                break
        if not found:
            return f"❌ Product not found: <code>{pid}</code>"
        with open(catalog_path, "w") as f:
            _json.dump(catalog, f, indent=2, ensure_ascii=False)

        # Update meta.json too so rebuild_all picks it up
        meta_path = ROOT / f"products/{pid}/meta.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = _json.load(f)
            meta["is_free"] = True
            with open(meta_path, "w") as f:
                _json.dump(meta, f, indent=2, ensure_ascii=False)

        # Rebuild site
        rebuild = subprocess.run(
            [sys.executable, str(ROOT / "scripts/update_site.py"), "--rebuild-all"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=60,
        )
        if rebuild.returncode != 0:
            return f"⚠️ Marked free but site rebuild failed:\n<code>{rebuild.stderr[:300]}</code>"

        # Push to GitHub
        subprocess.run(["git", "add", "-A"], cwd=str(ROOT), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"site: mark {pid} as free"],
            cwd=str(ROOT), capture_output=True,
        )
        subprocess.run(["git", "push"], cwd=str(ROOT), capture_output=True, timeout=60)

        return (
            f"✅ <b>Marked as free!</b>\n\n"
            f"Product: <code>{pid}</code>\n"
            f"Free badge now shows on the site."
        )
    except Exception as e:
        return f"❌ Unexpected error: {e}"



def cmd_categories() -> str:
    lines = ["🗂 <b>Product Categories</b>\n"]
    for key, (label, desc) in KNOWN_CATEGORIES.items():
        lines.append(f"  <b>{key}</b> — {label}\n  <i>{desc}</i>")
    lines.append("\n<b>Usage:</b>")
    lines.append("  <code>/run prompt-packs</code> — generate only prompt packs")
    lines.append("  <code>/run freelancing checklist</code> — seed + category focus")
    lines.append("  <code>/run checklist</code> — pick best checklist idea from backlog")
    return "\n".join(lines)


def cmd_karma() -> str:
    """Handle /karma — scout Reddit for 5 posts worth commenting on."""
    subprocess.Popen(
        [sys.executable, str(ROOT / "scripts/karma_scout.py"), "--max", "5"],
        cwd=str(ROOT),
        stdout=open(ROOT / "logs/pipeline.log", "a"),
        stderr=open(ROOT / "logs/pipeline-error.log", "a"),
    )
    return "🎯 Scouting Reddit for posts to comment on… 5 drafts coming shortly."


def cmd_help() -> str:
    return (
        "🏭 <b>mini-on-ai factory</b>\n\n"
        "/run — Generate a new product  (e.g. /run marketing)\n"
        "/reddit — Scan Reddit, propose up to 10 products  (e.g. /reddit n8n)\n"
        "/holidays — Plan a family trip (interactive questionnaire)\n"
        "/holidays cancel — Cancel current planning session\n"
        "/karma — Scout 5 posts to comment on for Reddit karma\n"
        "/karma {url} — Draft a comment for a specific Reddit post URL\n"
        "/draft r/Sub | Title | Body — Draft a comment from pasted post text\n"
        "/go — Approve pending idea → build it\n"
        "/skip — Skip pending idea\n"
        "/pause — Pause the factory\n"
        "/resume — Resume the factory\n"
        "/status — Last run, products count, API costs\n"
        "/products — All published products with links"
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

        msg = (
            f"📊 <b>Factory Status</b>\n\n"
            f"Products published: <b>{product_count}</b>\n"
            f"Total runs: {len(runs)}\n\n"
            f"Last run: {status_icon} {last['status']}\n"
            f"Product: {product_name}\n"
            f"Duration: {duration}s\n"
            f"At: {started} UTC"
        )

        # Add token usage if available
        if last and last.get("tokens"):
            tokens = last["tokens"]
            cost = tokens.get("estimated_cost_usd", 0)
            inp = tokens.get("input_tokens", 0)
            out = tokens.get("output_tokens", 0)
            msg += f"\n\n💰 Cost: ${cost:.4f}\n📊 Tokens: {inp:,} in / {out:,} out"

        msg += approval_note
        return msg
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
        shown = 0
        for i, p in enumerate(products, 1):
            gumroad = p.get("gumroad_url")
            gumroad_line = f"\n   🛒 {gumroad}" if gumroad else "\n   🛒 <i>Gumroad pending</i>"
            entry = (
                f"{i}. <b>{p['title']}</b>\n"
                f"   🔗 {site_url}/products/{p['id']}.html"
                f"{gumroad_line}"
            )
            lines.append(entry)
            shown += 1
            # Keep under Telegram's 4096-char limit
            if len("\n\n".join(lines)) > 3500:
                lines.append(f"<i>…and {len(products) - shown} more. See {site_url}</i>")
                break
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


def _skip_reddit_post(post_id: str) -> None:
    """Mark a Reddit queue post as skipped."""
    queue = read_json("data/reddit-queue.json")
    for p in queue.get("posts", []):
        if p["post_id"] == post_id:
            p["status"] = "skipped"
            break
    write_json("data/reddit-queue.json", queue)


def _skip_karma_post(post_id: str) -> None:
    """Mark a karma queue post as skipped."""
    queue = read_json("data/karma-queue.json")
    for p in queue.get("posts", []):
        if p["post_id"] == post_id:
            p["status"] = "skipped"
            break
    write_json("data/karma-queue.json", queue)


def run_pipeline_bg(seed: str = "", category: str = "") -> None:
    """Run pipeline in background subprocess."""
    cmd = [sys.executable, str(ROOT / "scripts/run_pipeline.py")]
    if seed:
        cmd += ["--seed", seed]
    if category:
        cmd += ["--category", category]

    log("bot", f"Spawning pipeline subprocess (seed={seed or 'none'}, category={category or 'any'})")
    subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        stdout=open(ROOT / "logs/pipeline.log", "a"),
        stderr=open(ROOT / "logs/pipeline-error.log", "a"),
    )


def _holiday_state() -> dict:
    try:
        return read_json("data/holiday-state.json")
    except Exception:
        return {"status": "idle", "step": 0, "constraints": {}, "proposals": []}


def _save_holiday_state(state: dict) -> None:
    write_json("data/holiday-state.json", state)


def cmd_holidays(text: str) -> str:
    lower = text.lower().strip()

    if "cancel" in lower or "annule" in lower:
        state = _holiday_state()
        state["status"] = "idle"
        state["step"] = 0
        state["constraints"] = {}
        _save_holiday_state(state)
        return "✅ Planification annulée. Tapez /holidays pour recommencer."

    state = _holiday_state()
    current_status = state.get("status", "idle")

    if current_status == "gathering":
        step = state.get("step", 0)
        _, question = HOLIDAY_QUESTIONS[step]
        return (
            f"Une planification est déjà en cours (question {step + 1}/{len(HOLIDAY_QUESTIONS)}).\n\n"
            f"Question actuelle:\n{question}\n\n"
            f"Tapez /holidays cancel pour recommencer."
        )

    if current_status == "researching":
        return "🔍 Recherche en cours… Les propositions arrivent bientôt!"

    # Start fresh session
    state = {
        "status": "gathering",
        "step": 0,
        "constraints": {},
        "proposals": [],
        "started_at": timestamp(),
    }
    _save_holiday_state(state)

    _, first_question = HOLIDAY_QUESTIONS[0]
    return (
        f"🏝️ <b>Planification de voyage</b>\n\n"
        f"Je vais vous poser {len(HOLIDAY_QUESTIONS)} questions pour trouver le voyage parfait.\n\n"
        f"Question 1/{len(HOLIDAY_QUESTIONS)}:\n\n{first_question}"
    )


def handle_holiday_answer(text: str) -> str:
    """Process a free-text answer during the holiday gathering phase."""
    state = _holiday_state()
    step = state.get("step", 0)
    constraints = state.get("constraints", {})

    key, _ = HOLIDAY_QUESTIONS[step]

    # Check if user wants to launch research early
    if text.lower().strip() in ("go", "go!", "recherche", "lance", "ok go", "let's go"):
        if not constraints:
            return "Répondez d'abord à quelques questions pour que je puisse chercher! 😊"
        return _launch_holiday_research(state)

    # Store the answer as-is for this constraint
    constraints[key] = text.strip()
    state["constraints"] = constraints

    next_step = step + 1

    if next_step >= len(HOLIDAY_QUESTIONS):
        # All questions answered — launch research
        state["step"] = next_step
        _save_holiday_state(state)
        return _launch_holiday_research(state)

    # Advance to next question
    state["step"] = next_step
    _save_holiday_state(state)

    _, next_question = HOLIDAY_QUESTIONS[next_step]
    return f"Question {next_step + 1}/{len(HOLIDAY_QUESTIONS)}:\n\n{next_question}"


def _launch_holiday_research(state: dict) -> str:
    """Transition to researching state and spawn research subprocess."""
    state["status"] = "researching"
    _save_holiday_state(state)

    subprocess.Popen(
        [sys.executable, str(ROOT / "scripts/holiday_planner.py")],
        cwd=str(ROOT),
        stdout=open(ROOT / "logs/pipeline.log", "a"),
        stderr=open(ROOT / "logs/pipeline-error.log", "a"),
    )

    constraints = state.get("constraints", {})
    summary_lines = []
    labels = {
        "dates": "Dates", "budget": "Budget", "destination": "Destination",
        "trip_type": "Type", "journey_time": "Durée max trajet",
        "accommodation": "Hébergement", "nights": "Nuits", "extras": "Extras",
    }
    for k, label in labels.items():
        if constraints.get(k):
            summary_lines.append(f"• {label}: {constraints[k]}")

    summary = "\n".join(summary_lines)
    return (
        f"🔍 <b>Recherche lancée!</b>\n\n"
        f"Je cherche 3 voyages basés sur:\n{summary}\n\n"
        f"Les propositions arrivent dans 1-2 minutes…"
    )


def handle_command(text: str) -> str:
    text = text.strip()
    lower = text.lower()

    # Free-text intercept: route to holiday planner if session is active
    if not text.startswith("/"):
        holiday_st = _holiday_state()
        if holiday_st.get("status") == "gathering":
            return handle_holiday_answer(text)
        return None  # Ignore non-commands outside sessions

    if lower == "/help" or lower.startswith("/start"):
        return cmd_help()

    if lower == "/status":
        return cmd_status()

    if lower == "/products":
        return cmd_products()

    if lower == "/ideas":
        return cmd_ideas()

    if lower == "/pause" or lower == "/holdon":
        return set_daemon_paused(True)

    if lower == "/resume":
        return set_daemon_paused(False)

    if lower == "/go":
        return handle_approval("approved")

    if lower == "/skip" or lower == "/nogo" or lower == "/no":
        return handle_approval("rejected")

    if lower == "/holidays" or lower.startswith("/holidays "):
        return cmd_holidays(text)

    if lower == "/karma":
        return cmd_karma()

    if lower.startswith("/karma "):
        url_arg = text[len("/karma "):].strip()
        if url_arg.startswith("http"):
            from karma_scout import comment_for_url
            return comment_for_url(url_arg)
        return "Usage: /karma https://reddit.com/r/..."

    if lower.startswith("/draft "):
        from karma_scout import draft_from_text
        raw = text[len("/draft "):].strip()
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 2:
            return "Usage: /draft r/SubName | Post title | Optional body"
        subreddit = parts[0].lstrip("r/")
        title = parts[1]
        body = parts[2] if len(parts) > 2 else ""
        return draft_from_text(subreddit, title, body)

    if lower == "/reddit" or lower.startswith("/reddit "):
        sub_arg = text[len("/reddit"):].strip()
        cmd = [sys.executable, str(ROOT / "scripts/run_pipeline.py"), "--reddit-mode"]
        if sub_arg:
            cmd += ["--reddit-subreddit", sub_arg]
        subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=open(ROOT / "logs/pipeline.log", "a"),
            stderr=open(ROOT / "logs/pipeline-error.log", "a"),
        )
        note = f" (r/{sub_arg})" if sub_arg else ""
        return f"🔍 Scanning Reddit{note} for needs… candidates will arrive shortly."

    if lower.startswith("/seturl"):
        args = text[len("/seturl"):].strip()
        return cmd_seturl(args)

    if lower.startswith("/setfree"):
        args = text[len("/setfree"):].strip()
        return cmd_setfree(args)

    if lower == "/categories":
        return cmd_categories()

    if lower == "/run all":
        send("🚀 Starting 4 pipeline runs (marketing, freelancing, writing, coding).\nYou'll get a Telegram message after each one.")
        for seed in SEEDS_ALL:
            run_pipeline_bg(seed)
            time.sleep(10)
        return None

    if lower.startswith("/run"):
        parts = text.split(None, 3)
        args = parts[1:]  # everything after /run

        seed = ""
        category = ""

        if len(args) == 1:
            # /run X — could be a seed or a category
            if args[0].lower() in KNOWN_CATEGORIES:
                category = args[0].lower()
            else:
                seed = args[0]
        elif len(args) >= 2:
            # /run X Y — first is seed, second is category
            seed = args[0]
            if args[1].lower() in KNOWN_CATEGORIES:
                category = args[1].lower()
            else:
                seed = " ".join(args)  # treat whole thing as seed

        note_parts = []
        if seed:
            note_parts.append(f"seed: <i>{seed}</i>")
        if category:
            note_parts.append(f"category: <b>{KNOWN_CATEGORIES[category][0]}</b>")
        note = " · ".join(note_parts)
        note_str = f" ({note})" if note else ""

        run_pipeline_bg(seed=seed, category=category)
        return f"🚀 Pipeline started{note_str}.\nI'll send an approval request when an idea is ready."

    return f"Unknown command: <code>{text}</code>\n\nType /help for available commands."


LOCKFILE = Path(ROOT) / "logs" / "bot.lock"


def _acquire_lock() -> bool:
    """Write PID to lock file. Return False if another instance is already running."""
    import fcntl
    global _lock_fh
    _lock_fh = open(LOCKFILE, "w")
    try:
        fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fh.write(str(os.getpid()))
        _lock_fh.flush()
        return True
    except BlockingIOError:
        return False


_lock_fh = None


def main():
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN not set. Exiting.")
        sys.exit(1)

    # Prevent multiple instances from fighting over Telegram's getUpdates
    retries = 0
    while not _acquire_lock():
        retries += 1
        log("bot", f"Another instance is running, waiting... ({retries})")
        time.sleep(10)
        if retries > 12:  # give up after 2 minutes
            log("bot", "Could not acquire lock after 2 minutes. Exiting.")
            sys.exit(1)

    log("bot", f"Starting Telegram bot (chat_id: {CHAT_ID})")
    try:
        send("🤖 <b>mini-on-ai bot online</b>\n\nType /help to see commands.")
    except Exception as e:
        log("bot", f"Startup notification failed (non-fatal): {e}")

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

                if cq_chat_id != str(CHAT_ID):
                    log("bot", f"Callback ignored: chat_id mismatch")
                elif cq_data.startswith("approval:"):
                    decision = "approved" if cq_data == "approval:go" else "rejected"
                    log("bot", f"Approval decision: {decision}")
                    reply = handle_approval(decision)
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    send(reply, cq_chat_id)
                elif cq_data.startswith("reddit:build:"):
                    post_id = cq_data.split(":", 2)[2]
                    log("bot", f"Reddit build requested: {post_id}")
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    send("⏳ Building product for Reddit post…", cq_chat_id)
                    subprocess.Popen(
                        [sys.executable, str(ROOT / "scripts/run_pipeline.py"), "--reddit-build", post_id],
                        cwd=str(ROOT),
                        stdout=open(ROOT / "logs/pipeline.log", "a"),
                        stderr=open(ROOT / "logs/pipeline-error.log", "a"),
                    )
                elif cq_data.startswith("reddit:skip:"):
                    post_id = cq_data.split(":", 2)[2]
                    log("bot", f"Reddit skip: {post_id}")
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    _skip_reddit_post(post_id)
                    send("⏭ Skipped.", cq_chat_id)
                elif cq_data.startswith("karma:skip:"):
                    post_id = cq_data.split(":", 2)[2]
                    log("bot", f"Karma skip: {post_id}")
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    _skip_karma_post(post_id)
                    send("⏭ Skipped.", cq_chat_id)
                else:
                    log("bot", f"Callback ignored: unknown data={cq_data}")
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
