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
  /tweet    — draft a tweet for the latest un-tweeted product
  /tweet list — show all products not yet tweeted
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

from lib.utils import read_json, write_json, timestamp, log, ROOT, get_run_token_summary, get_lifetime_token_summary

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


def _missing_products() -> list:
    catalog = read_json("data/product-catalog.json")
    products = catalog.get("products", [])
    return [p for p in products if not p.get("gumroad_url") and not p.get("is_free")]


def cmd_missing(args: str = "") -> str:
    """
    /missing list  — numbered list of products without Gumroad URL
    /missing 3     — full Gumroad listing instructions for product #3
    """
    missing = _missing_products()

    if not missing:
        return "✅ All paid products have a Gumroad URL!"

    # /missing list (or bare /missing)
    if not args or args == "list":
        lines = [f"⚠️ <b>{len(missing)} paid products need a Gumroad listing:</b>\n"]
        for i, p in enumerate(missing, 1):
            title = p.get("title", "?")[:55]
            price = p.get("price") or 0
            price_str = f"${price // 100}" if price else "?"
            lines.append(f"{i}. ({price_str}) {title}")
        lines.append("\nUse <code>/missing 3</code> to get full Gumroad instructions for product #3.")
        return "\n".join(lines)

    # /missing {number}
    if not args.isdigit():
        return "Usage: <code>/missing list</code> or <code>/missing 3</code>"

    idx = int(args) - 1
    if idx < 0 or idx >= len(missing):
        return f"❌ Number {args} out of range. Use /missing list to see options."

    p = missing[idx]
    pid = p.get("id", "")

    # Load full meta from products/{id}/meta.json for gumroad_description + package_path
    import json as _json
    meta_path = ROOT / f"products/{pid}/meta.json"
    meta = _json.loads(meta_path.read_text()) if meta_path.exists() else p

    title       = meta.get("title", "?")
    price_cents = meta.get("price") or 0
    price_str   = f"${price_cents // 100}" if price_cents else "free"
    package     = meta.get("package_path", f"products/{pid}/package.zip")
    site_url    = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")
    product_url = f"{site_url}/products/{pid}.html"
    gumroad_desc = meta.get("gumroad_description", "")

    desc_block = f"\n\n<code>{gumroad_desc}</code>" if gumroad_desc else " <i>(not available)</i>"

    return (
        f"📦 <b>Gumroad listing instructions</b>\n\n"
        f"<b>Title:</b>\n<code>{title}</code>\n\n"
        f"<b>Price:</b> {price_str}\n\n"
        f"<b>Summary URL</b> (custom permalink field):\n<code>{product_url}</code>\n\n"
        f"<b>File to attach:</b>\n<code>{package}</code>\n\n"
        f"<b>Description (tap to copy):</b>{desc_block}\n\n"
        f"Once published, send:\n<code>/seturl {pid} GUMROAD_URL</code>"
    )


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


def cmd_tokens() -> str:
    """Show lifetime token usage and cost breakdown by model and stage."""
    log_file = ROOT / "data/token-usage.json"
    if not log_file.exists():
        return "📊 No token usage data yet."
    try:
        entries = read_json("data/token-usage.json")
    except Exception:
        return "📊 Could not read token-usage.json."

    from collections import defaultdict
    _COST = {
        "claude-sonnet-4-6":         (3.00, 15.00),
        "claude-haiku-4-5-20251001": (0.80,  4.00),
        "claude-haiku-4-5":          (0.80,  4.00),
        "claude-opus-4-6":           (15.0, 75.00),
    }
    by_model = defaultdict(lambda: {"in": 0, "out": 0})
    by_stage = defaultdict(lambda: {"in": 0, "out": 0})
    total_cost = 0.0

    for e in entries:
        m = e.get("model", "unknown")
        s = e.get("stage", "unknown")
        i = e.get("input_tokens", 0)
        o = e.get("output_tokens", 0)
        by_model[m]["in"] += i
        by_model[m]["out"] += o
        by_stage[s]["in"] += i
        by_stage[s]["out"] += o
        r = _COST.get(m, (3.00, 15.00))
        total_cost += (i * r[0] + o * r[1]) / 1_000_000

    lines = [f"📊 <b>Token Usage — ${total_cost:.3f} total</b>\n"]

    lines.append("<b>By model:</b>")
    for m, v in sorted(by_model.items()):
        r = _COST.get(m, (3.00, 15.00))
        cost = (v["in"] * r[0] + v["out"] * r[1]) / 1_000_000
        short = m.replace("claude-", "").replace("-20251001", "")
        lines.append(f"  {short}: ${cost:.3f}  ({v['in']//1000}k in / {v['out']//1000}k out)")

    lines.append("\n<b>By stage:</b>")
    stage_costs = []
    for s, v in by_stage.items():
        # estimate cost using average rate
        c = (v["in"] * 3.0 + v["out"] * 15.0) / 1_000_000  # conservative
        stage_costs.append((c, s, v))
    for c, s, v in sorted(stage_costs, reverse=True):
        lines.append(f"  {s}: {v['in']//1000}k in / {v['out']//1000}k out")

    lines.append(f"\n<i>{len(entries)} API calls logged</i>")
    return "\n".join(lines)


def cmd_help(group: str = "") -> str:
    group = group.strip().lower()

    if group == "factory":
        return (
            "🏭 <b>Factory — full detail</b>\n\n"
            "<b>/run [seed] [category]</b>\n"
            "  Generate a new product.\n"
            "  <code>/run</code> — pick best idea from backlog\n"
            "  <code>/run marketing</code> — seed the idea search\n"
            "  <code>/run checklist</code> — force a specific category\n"
            "  <code>/run freelancing checklist</code> — seed + category\n"
            "  <code>/run all</code> — 4 runs (marketing, freelancing, writing, coding)\n"
            "  Categories: prompt-packs · checklist · swipe-file · mini-guide · n8n-template\n\n"
            "<b>/go · /skip</b> — approve or reject the pending idea\n"
            "<b>/pause · /resume</b> — start/stop the daemon\n"
            "<b>/status</b> — last run, product count, API costs\n"
            "<b>/stats [days]</b> — Gumroad revenue, sales, top products, referrers\n"
            "<b>/products</b> — all published products with links\n"
            "<b>/ideas</b> — top 5 scored ideas in the backlog"
        )

    if group == "posts":
        return (
            "📣 <b>Reddit Posts — full detail</b>\n\n"
            "<b>/post list</b> — subreddits grouped by product\n\n"
            "<b>/post {sub}</b> — generate a post with product link\n"
            "  Verified post-friendly: SideProject · indiehackers · buildinpublic\n"
            "  Also: nocode · SaaS · somethingimade · shamelessplug · ChatGPTCoding\n\n"
            "<b>/fix {sub} | {rule}</b>\n"
            "  Regenerate from scratch, avoiding a specific rule violation\n"
            "  <code>/fix SideProject | no self-promotion</code>\n\n"
            "<b>/fix {sub} | {rule} | {title} | {body}</b>\n"
            "  Revise a specific post you already wrote\n"
            "  <code>/fix indiehackers | too salesy | My title | My body text</code>"
        )

    if group == "karma":
        return (
            "💬 <b>Reddit Karma — full detail</b>\n\n"
            "<b>/karma</b> — scout 5 posts to comment on (all target subreddits)\n\n"
            "<b>/karma {sub}</b> — scan one subreddit, lower threshold\n"
            "  <code>/karma resumes</code> — good for karma, no product links allowed there\n\n"
            "<b>/karma {url}</b> — draft comment for a specific post URL\n"
            "  <code>/karma https://reddit.com/r/ClaudeAI/...</code>\n\n"
            "<b>/draft r/Sub | Title | Body</b> — draft comment from pasted post text\n"
            "  <code>/draft r/resumes | Help with ATS | I'm applying for...</code>"
        )

    if group == "twitter":
        return (
            "🐦 <b>Twitter — full detail</b>\n\n"
            "<b>/tweet</b> — Draft a tweet for the latest un-tweeted product\n\n"
            "<b>/tweet list</b> — Show all products not yet tweeted (numbered)\n\n"
            "<b>/tweet 3</b> — Draft tweet for product #3 from the list\n\n"
            "Draft is sent as tap-to-copy text — paste it into X manually.\n"
            "  🔄 <b>Regenerate</b> — Claude writes a fresh angle (different hook)\n\n"
            "Tweets always link to mini-on-ai.com, never Gumroad.\n"
            "Hashtags are community-targeted by product category."
        )

    if group == "products":
        return (
            "📦 <b>Products — full detail</b>\n\n"
            "<b>/missing list</b> — Paid products without a Gumroad URL\n"
            "<b>/missing 3</b> — Full Gumroad instructions for product #3 (title, price, description, file)\n\n"
            "<b>/seturl {id} {url}</b>\n"
            "  Link a product to its Gumroad listing (fetches real price automatically)\n"
            "  <code>/seturl prompts-my-pack-20260312 https://minionai.gumroad.com/l/abc</code>\n\n"
            "<b>/setfree {id}</b> — mark product as free on the vitrine\n\n"
            "<b>/list</b> — all subreddits and products at a glance\n\n"
            "Use /products to see product IDs."
        )

    # Default — grouped overview
    return (
        "🏭 <b>Factory</b>\n"
        "  /run [seed] [category] — Generate a product\n"
        "  /go · /skip — Approve or reject pending idea\n"
        "  /pause · /resume — Start/stop the daemon\n"
        "  /status · /products · /ideas — Info\n"
        "  /stats [days] — Gumroad sales, revenue & referrers\n"
        "  /tokens — API cost breakdown by model + stage\n\n"
        "📣 <b>Reddit Posts</b>\n"
        "  /post list — Subreddits per product\n"
        "  /post {sub} — Draft a post  (e.g. /post SideProject)\n"
        "  /fix {sub} | {rule} — Revise a rejected post\n\n"
        "💬 <b>Reddit Karma</b>\n"
        "  /karma — Scout 5 posts to comment on\n"
        "  /karma {sub} — Scan one subreddit  (e.g. /karma resumes)\n"
        "  /karma {url} — Draft comment for a post URL\n"
        "  /draft r/Sub | Title | Body — Draft from pasted text\n\n"
        "📦 <b>Products</b>\n"
        "  /seturl {id} {url} — Link product to Gumroad\n"
        "  /setfree {id} — Mark product as free\n"
        "  /syncprices — Pull latest prices from Gumroad + rebuild vitrine\n"
        "  /missing — Products without a Gumroad URL\n"
        "  /list — All subreddits and products at a glance\n\n"
        "🐦 <b>Twitter</b>\n"
        "  /tweet — Draft tweet for latest un-tweeted product\n"
        "  /tweet list — Products not yet tweeted (numbered)\n"
        "  /tweet 3 — Draft tweet for product #3 from the list\n\n"
        "📧 <b>Email</b>\n"
        "  /blast — Draft + send an email to your subscriber list\n\n"
        "✍️ <b>Blog</b>\n"
        "  /blog — Auto-generate + publish an SEO blog post\n"
        "  /blog \"topic\" — Blog post on a specific keyword\n\n"
        "Type /help {group} for more detail:\n"
        "<code>factory · posts · karma · products · twitter</code>"
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


def cmd_stats(days: int = 30) -> str:
    """Fetch live sales data from Gumroad and return a formatted summary."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gumroad_stats.py"), "--days", str(days)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    output = result.stdout.strip()
    if result.returncode != 0 or not output:
        err = result.stderr.strip() or "No output from gumroad_stats.py"
        return f"❌ Stats error: {err[:300]}"
    return output


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

    # Check for previous constraints to offer reuse
    previous_constraints = state.get("constraints", {})
    if previous_constraints and current_status in ("done", "idle"):
        labels = {
            "dates": "Dates", "budget": "Budget", "destination": "Destination",
            "trip_type": "Type", "journey_time": "Durée max trajet",
            "accommodation": "Hébergement", "nights": "Nuits", "extras": "Extras",
        }
        summary = "\n".join(
            f"• {labels.get(k, k)}: {v}"
            for k, v in previous_constraints.items() if v
        )
        return (
            f"🏝️ <b>Voyage précédent retrouvé</b>\n\n"
            f"{summary}\n\n"
            f"Que voulez-vous faire?\n"
            f"• Tapez <b>go</b> pour relancer avec ces critères\n"
            f"• Tapez <b>modifier</b> pour les ajuster question par question\n"
            f"• Tapez <b>nouveau</b> pour repartir de zéro"
        )

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
        warning = _school_holiday_warning(state)
        if warning:
            return warning
        return _launch_holiday_research(state)

    # "ok" or "skip" keeps the existing value
    if text.lower().strip() in ("ok", "skip", "pareil", "idem", "même", "garder"):
        if constraints.get(key):
            # Keep existing, advance to next step
            pass
        else:
            constraints[key] = ""
    else:
        constraints[key] = text.strip()

    state["constraints"] = constraints
    next_step = step + 1

    if next_step >= len(HOLIDAY_QUESTIONS):
        state["step"] = next_step
        _save_holiday_state(state)
        warning = _school_holiday_warning(state)
        if warning:
            return warning
        return _launch_holiday_research(state)

    state["step"] = next_step
    _save_holiday_state(state)

    next_key, next_question = HOLIDAY_QUESTIONS[next_step]
    existing = constraints.get(next_key, "")
    hint = f"\n\n<i>Valeur actuelle: {existing}</i>\nTapez une nouvelle valeur ou <b>ok</b> pour garder." if existing else ""
    return f"Question {next_step + 1}/{len(HOLIDAY_QUESTIONS)}:\n\n{next_question}{hint}"


def _school_holiday_warning(state: dict) -> str:
    """Check for school holiday overlap and return warning message, or None if clear."""
    from holiday_planner import check_school_holidays
    dates_str = state.get("constraints", {}).get("dates", "")
    if not dates_str:
        return None
    matches = check_school_holidays(dates_str)
    if not matches:
        return None
    details = "\n".join(f"  • {label} ({zones})" for label, zones in matches)
    state["status"] = "school_holiday_warning"
    _save_holiday_state(state)
    return (
        f"⚠️ <b>Attention — Vacances scolaires détectées!</b>\n\n"
        f"Vos dates semblent coïncider avec:\n{details}\n\n"
        f"Les prix peuvent être <b>+30-40% plus élevés</b> pendant ces périodes.\n\n"
        f"• Tapez <b>continuer</b> pour chercher quand même\n"
        f"• Tapez <b>modifier</b> pour changer les dates"
    )


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


# ── Email blast helpers ───────────────────────────────────────────────────────

BLAST_STATE = ROOT / "data/blast-state.json"


def _save_blast_state(draft: dict) -> None:
    BLAST_STATE.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n")


def _load_blast_state() -> dict:
    if not BLAST_STATE.exists():
        return {}
    try:
        return json.loads(BLAST_STATE.read_text())
    except Exception:
        return {}


def _generate_blast_draft() -> dict:
    """Use Claude Haiku to draft a short email based on latest products + blog posts."""
    import anthropic as _anthropic
    client = _anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    catalog = read_json("data/product-catalog.json")
    products = [p for p in catalog.get("products", []) if p.get("gumroad_url")][:3]

    blog_data_path = ROOT / "data/blog-posts.json"
    blog_posts = []
    if blog_data_path.exists():
        try:
            blog_posts = json.loads(blog_data_path.read_text()).get("posts", [])[:2]
        except Exception:
            pass

    site_url = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")

    product_lines = "\n".join(
        f'- {p["title"]} ({site_url}/products/{p["id"]}.html)'
        for p in products
    )
    blog_lines = "\n".join(
        f'- {p["title"]} ({site_url}/blog/{p["slug"]}.html)'
        for p in blog_posts
    )

    prompt = f"""Write a short, personal email to send to a small list (~20 people) who downloaded free digital products from mini-on-ai.com.

Recent products:
{product_lines}

Recent blog posts:
{blog_lines}

Requirements:
- Subject line: punchy, not clickbait, max 60 chars
- Body: 3-4 sentences, personal tone, no "Dear subscriber" openers, no exclamation marks spam
- Reference one product or blog post naturally
- End with a soft CTA linking to {site_url}
- Plain text only (no markdown, no bullet points)

Return ONLY valid JSON:
{{"subject": "...", "body": "..."}}"""

    msg = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    import re as _re
    raw = _re.sub(r"^```[a-z]*\n?", "", raw)
    raw = _re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


def cmd_blast(args: str = "") -> None:
    """Handle /blast — generate draft + send with inline keyboard."""
    send("✍️ Drafting email…")
    try:
        draft = _generate_blast_draft()
    except Exception as e:
        send(f"❌ Draft failed: {e}")
        return

    _save_blast_state(draft)

    count = 0
    try:
        import subprocess as _sp
        r = _sp.run(
            [sys.executable, str(ROOT / "scripts/email_blast.py"), "--count"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=15
        )
        count = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
    except Exception:
        pass

    subject = draft.get("subject", "")
    body    = draft.get("body", "")
    text = (
        f"📧 <b>Draft email</b> → {count} subscriber{'s' if count != 1 else ''}\n\n"
        f"<b>Subject:</b> {subject}\n\n"
        f"{body}"
    )
    api("sendMessage", {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[
            {"text": "✅ Send", "callback_data": "blast:send"},
            {"text": "🔄 Regenerate", "callback_data": "blast:regen"},
        ]]},
    })


def _handle_blast_callback(data: str) -> str:
    if data == "blast:regen":
        cmd_blast()
        return ""

    if data == "blast:send":
        draft = _load_blast_state()
        if not draft:
            return "❌ No draft found. Run /blast again."
        subject = draft.get("subject", "")
        body    = draft.get("body", "")
        try:
            import subprocess as _sp
            r = _sp.run(
                [sys.executable, str(ROOT / "scripts/email_blast.py"),
                 "--subject", subject, "--body", body],
                capture_output=True, text=True, cwd=str(ROOT), timeout=60
            )
            if r.returncode == 0:
                result = json.loads(r.stdout.strip())
                n = result.get("recipients", "?")
                return f"✅ <b>Email sent</b> to {n} subscriber{'s' if n != 1 else ''}!"
            else:
                return f"❌ Send failed:\n<code>{r.stderr[-300:]}</code>"
        except Exception as e:
            return f"❌ Send error: {e}"

    return ""


# ── Twitter helpers ───────────────────────────────────────────────────────────

TWEET_LOG   = ROOT / "data/tweet-log.json"
TWEET_STATE = ROOT / "data/tweet-state.json"


def _tweeted_ids() -> set:
    """Return set of product IDs already tweeted."""
    if not TWEET_LOG.exists():
        return set()
    try:
        entries = json.loads(TWEET_LOG.read_text())
        return {e["product_id"] for e in entries if "product_id" in e}
    except Exception:
        return set()


def _save_tweet_state(product_id: str, tweet_text: str) -> None:
    TWEET_STATE.parent.mkdir(parents=True, exist_ok=True)
    TWEET_STATE.write_text(json.dumps({
        "product_id": tweet_text and product_id,
        "tweet_text": tweet_text,
        "generated_at": timestamp(),
    }, ensure_ascii=False) + "\n")


def _load_tweet_state() -> dict:
    if not TWEET_STATE.exists():
        return {}
    try:
        return json.loads(TWEET_STATE.read_text())
    except Exception:
        return {}


def _log_tweet(product_id: str, tweet_id: str, tweet_text: str) -> None:
    entries = []
    if TWEET_LOG.exists():
        try:
            entries = json.loads(TWEET_LOG.read_text())
        except Exception:
            entries = []
    entries.append({
        "product_id": product_id,
        "tweet_id":   tweet_id,
        "tweet_text": tweet_text,
        "tweeted_at": timestamp(),
    })
    TWEET_LOG.parent.mkdir(parents=True, exist_ok=True)
    TWEET_LOG.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n")


def _handle_tweet_regen(product_id: str, cq_id: str, chat_id: str) -> None:
    try:
        api("answerCallbackQuery", {"callback_query_id": cq_id})
    except Exception:
        pass

    catalog = read_json("data/product-catalog.json")
    products = catalog.get("products", [])
    meta = next((p for p in products if p.get("id") == product_id), None)
    if not meta:
        send(f"❌ Product not found: {product_id}", chat_id)
        return

    send("🔄 Regenerating tweet…", chat_id)
    try:
        import anthropic as _anthropic
        client = _anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        site_url = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")
        pid = meta.get("id", "")
        product_url = f"{site_url}/products/{pid}.html" if pid else site_url
        cat = meta.get("category", "")
        cat_hashtags = {
            "claude-code-skill": "#ClaudeCode #AI #developer",
            "n8n-template":      "#n8n #automation #nocode",
            "prompt-packs":      "#AI #productivity #prompts",
            "mini-guide":        "#AI #productivity",
            "checklist":         "#productivity #tools",
            "swipe-file":        "#copywriting #marketing",
        }.get(cat, "#AI #productivity")
        prompt = (
            f"Write a single tweet (max 270 chars) to promote this digital product.\n"
            f"Title: {meta.get('title', '')}\n"
            f"Description: {meta.get('description', '')}\n"
            f"URL: {product_url}\n\n"
            f"Rules:\n"
            f"- Use a fresh hook: a question, a benefit, or a concrete use-case.\n"
            f"- Do NOT start with 'Just published'.\n"
            f"- Always end with the URL above (vitrine site, not Gumroad).\n"
            f"- Add 2-3 hashtags from this set: {cat_hashtags}\n"
            f"- Return only the tweet text, no quotes, no explanation."
        )
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        new_text = msg.content[0].text.strip().strip('"').strip("'")
        if len(new_text) > 280:
            new_text = new_text[:277] + "…"
        _save_tweet_state(product_id, new_text)
        from telegram_notify import send_tweet_draft
        send_tweet_draft(product_id, new_text)
    except Exception as e:
        send(f"❌ Regeneration failed: {e}", chat_id)


def cmd_gumroad_desc(args: str) -> str:
    """Handle /gumroad [number | product_id] — send Gumroad description for a product."""
    catalog = read_json("data/product-catalog.json")
    products = catalog.get("products", [])

    if not args:
        # Show numbered list for picking
        lines = ["📋 <b>Pick a product to get its Gumroad description:</b>\n"]
        for i, p in enumerate(products, 1):
            lines.append(f"{i}. {p.get('title', '?')[:60]}")
        lines.append("\nUse <code>/gumroad 3</code> to get description for product #3.")
        return "\n".join(lines)

    # Resolve by number or id
    if args.isdigit():
        idx = int(args) - 1
        if idx < 0 or idx >= len(products):
            return f"❌ Number {args} out of range."
        meta_catalog = products[idx]
    else:
        meta_catalog = next((p for p in products if p.get("id") == args), None)
        if not meta_catalog:
            return f"❌ Product not found: <code>{args}</code>"

    pid = meta_catalog.get("id", "")
    meta_path = ROOT / f"products/{pid}/meta.json"
    if meta_path.exists():
        try:
            import json as _json
            meta = _json.loads(meta_path.read_text())
        except Exception:
            meta = meta_catalog
    else:
        meta = meta_catalog

    desc = meta.get("gumroad_description")
    if not desc:
        return f"❌ No Gumroad description found for <b>{meta_catalog.get('title', pid)}</b>."

    from telegram_notify import send_gumroad_description
    send_gumroad_description(meta)
    return None  # already sent


def _tweet_priority(p: dict) -> int:
    """Score a product for tweet priority — higher = tweet sooner."""
    score = 0
    # Purchasable (has Gumroad link)
    if p.get("gumroad_url"):
        score += 30
    # Price value
    price = p.get("price") or 0
    if price >= 1900:
        score += 20
    elif price >= 500:
        score += 10
    elif p.get("is_free"):
        score += 5
    # Category — Twitter audience fit
    cat = p.get("category", "")
    score += {"claude-code-skill": 15, "n8n-template": 10,
              "prompt-packs": 5, "mini-guide": 5, "swipe-file": 3, "checklist": 3}.get(cat, 0)
    return score


def cmd_tweet(args: str) -> str:
    """Handle /tweet [list | number]"""
    catalog = read_json("data/product-catalog.json")
    products = catalog.get("products", [])
    tweeted = _tweeted_ids()
    untweeted = sorted(
        [p for p in products if p.get("id") not in tweeted],
        key=_tweet_priority, reverse=True
    )

    if args == "list":
        if not untweeted:
            return "✅ All products have been tweeted!"
        lines = [f"📋 <b>Products not yet tweeted ({len(untweeted)}):</b>\n"]
        for i, p in enumerate(untweeted, 1):
            title = p.get("title", "?")
            price = p.get("price") or 0
            price_str = "free" if p.get("is_free") or price == 0 else f"${price // 100}"
            gum = "🛒" if p.get("gumroad_url") else "⚠️"
            lines.append(f"{i}. {gum} {title} ({price_str})")
        lines.append(f"\nUse <code>/tweet 1</code> to draft tweet for the top product.")
        return "\n".join(lines)

    # Resolve product by number or full id
    if args:
        if args.isdigit():
            idx = int(args) - 1
            if idx < 0 or idx >= len(untweeted):
                return f"❌ Number {args} out of range. Use /tweet list to see options."
            meta = untweeted[idx]
        else:
            meta = next((p for p in products if p.get("id") == args), None)
            if not meta:
                return f"❌ Product not found: <code>{args}</code>\nUse /tweet list to see options."
    else:
        if not untweeted:
            return "✅ All products have been tweeted!"
        meta = untweeted[0]  # highest priority first

    from twitter_post import draft_for_product
    from telegram_notify import send_tweet_draft
    tweet_text = draft_for_product(meta)
    _save_tweet_state(meta["id"], tweet_text)
    send_tweet_draft(meta["id"], tweet_text)
    return None  # response already sent via send_tweet_draft


def handle_command(text: str) -> str:
    text = text.strip()
    lower = text.lower()

    # Free-text intercept for holiday planner
    if not text.startswith("/"):
        holiday_st = _holiday_state()
        status = holiday_st.get("status", "idle")
        cmd = text.lower().strip()

        if status == "gathering":
            return handle_holiday_answer(text)

        # School holiday warning — waiting for user response
        if status == "school_holiday_warning":
            if cmd in ("modifier", "changer", "modifier dates"):
                holiday_st["status"] = "gathering"
                holiday_st["step"] = 0
                holiday_st["proposals"] = []
                _save_holiday_state(holiday_st)
                key, question = HOLIDAY_QUESTIONS[0]
                existing = holiday_st["constraints"].get(key, "")
                hint = f"\n\n<i>Valeur actuelle: {existing}</i>\nTapez une nouvelle valeur ou <b>ok</b> pour garder." if existing else ""
                return f"✏️ <b>Modification des critères</b>\n\nQuestion 1/{len(HOLIDAY_QUESTIONS)}:\n\n{question}{hint}"
            # Any other response (continuer, oui, ok, etc.) → proceed
            return _launch_holiday_research(holiday_st)

        # Jump to specific proposal by number (when status is done)
        if status == "done" and cmd in ("1", "2", "3"):
            proposals = holiday_st.get("proposals", [])
            idx = int(cmd) - 1
            if 0 <= idx < len(proposals):
                from telegram_notify import send_holiday_proposal
                holiday_st["current_proposal_index"] = idx
                _save_holiday_state(holiday_st)
                send_holiday_proposal(proposals[idx], idx + 1, len(proposals))
                return None  # already sent via send_holiday_proposal
            return f"Option {cmd} non disponible — il n'y a que {len(proposals)} proposition(s)."

        # Handle reuse/modify/new responses after /holidays summary
        if holiday_st.get("constraints") and status in ("done", "idle"):
            if cmd in ("go", "relancer", "oui", "yes"):
                warning = _school_holiday_warning(holiday_st)
                if warning:
                    return warning
                return _launch_holiday_research(holiday_st)
            if cmd in ("modifier", "modify", "changer"):
                holiday_st["status"] = "gathering"
                holiday_st["step"] = 0
                holiday_st["proposals"] = []
                _save_holiday_state(holiday_st)
                key, question = HOLIDAY_QUESTIONS[0]
                existing = holiday_st["constraints"].get(key, "")
                hint = f"\n\n<i>Valeur actuelle: {existing}</i>\nTapez une nouvelle valeur ou <b>ok</b> pour garder." if existing else ""
                return f"✏️ <b>Modification des critères</b>\n\nQuestion 1/{len(HOLIDAY_QUESTIONS)}:\n\n{question}{hint}"
            if cmd in ("nouveau", "new", "recommencer", "reset"):
                _save_holiday_state({"status": "gathering", "step": 0, "constraints": {}, "proposals": [], "started_at": timestamp()})
                _, first_question = HOLIDAY_QUESTIONS[0]
                return f"🏝️ <b>Nouveau voyage</b>\n\nQuestion 1/{len(HOLIDAY_QUESTIONS)}:\n\n{first_question}"
        return None  # Ignore non-commands outside sessions

    # ── HELP ──────────────────────────────────────────────────────────────────
    if lower == "/help" or lower.startswith("/start"):
        group = text[len("/help"):].strip() if lower.startswith("/help") else ""
        return cmd_help(group)

    # ── FACTORY ───────────────────────────────────────────────────────────────
    if lower == "/tokens":
        return cmd_tokens()

    if lower == "/status":
        return cmd_status()

    if lower == "/stats" or lower.startswith("/stats "):
        days = 30
        try:
            days = int(text.strip().split()[1])
        except (IndexError, ValueError):
            pass
        return cmd_stats(days)

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

    # ── REDDIT POSTS ──────────────────────────────────────────────────────────

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

    if lower == "/post list":
        from karma_scout import SUBREDDIT_TO_PRODUCT
        by_product: dict = {}
        for sub, (name, url) in SUBREDDIT_TO_PRODUCT.items():
            by_product.setdefault(name, []).append(sub)
        lines = ["<b>Subreddits you can post on:</b>\n"]
        for product, subs in by_product.items():
            lines.append(f"<b>{product}</b>")
            for s in subs:
                lines.append(f"  → r/{s}   <code>/post {s}</code>")
            lines.append("")
        return "\n".join(lines).strip()

    if lower.startswith("/post "):
        sub_arg = text[len("/post "):].strip()
        from karma_scout import generate_reddit_post
        return generate_reddit_post(sub_arg)

    if lower.startswith("/fix "):
        from karma_scout import fix_reddit_post
        parts = [p.strip() for p in text[len("/fix "):].split("|")]
        if len(parts) < 2:
            return "Usage:\n/fix {subreddit} | {rule}\n/fix {subreddit} | {rule} | {title} | {body}"
        sub = parts[0]
        rule = parts[1]
        title = parts[2] if len(parts) > 2 else ""
        body = parts[3] if len(parts) > 3 else ""
        return fix_reddit_post(sub, rule, title, body)

    # ── REDDIT KARMA ──────────────────────────────────────────────────────────

    if lower in ("/karma list", "/karma list"):
        from karma_scout import SUBREDDIT_TO_PRODUCT
        by_product: dict = {}
        for sub, (name, url) in SUBREDDIT_TO_PRODUCT.items():
            by_product.setdefault(name, []).append(sub)
        lines = ["<b>Subreddits to build karma on:</b>\n"]
        for product, subs in by_product.items():
            lines.append(f"<b>{product}</b>")
            for s in subs:
                lines.append(f"  → r/{s}   <code>/karma {s}</code>")
            lines.append("")
        return "\n".join(lines).strip()

    if lower == "/karma":
        return cmd_karma()

    if lower.startswith("/karma "):
        url_arg = text[len("/karma "):].strip()
        if url_arg.startswith("http"):
            from karma_scout import comment_for_url
            return comment_for_url(url_arg)
        # Subreddit targeting: /karma resumes  or  /karma r/resumes
        sub = url_arg[2:] if url_arg.startswith("r/") else url_arg
        subprocess.Popen(
            [sys.executable, str(ROOT / "scripts/karma_scout.py"), "--max", "5", "--subreddit", sub],
            cwd=str(ROOT),
            stdout=open(ROOT / "logs/pipeline.log", "a"),
            stderr=open(ROOT / "logs/pipeline-error.log", "a"),
        )
        return f"🎯 Scanning r/{sub} for karma opportunities (threshold: 55)…"

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

    # ── PRODUCTS ──────────────────────────────────────────────────────────────

    if lower == "/list":
        from karma_scout import SUBREDDIT_TO_PRODUCT
        by_product: dict = {}
        for sub, (name, url) in SUBREDDIT_TO_PRODUCT.items():
            by_product.setdefault(name, []).append(sub)
        lines = ["<b>📋 Products &amp; Subreddits</b>\n"]
        for product, subs in by_product.items():
            post_cmds = "  ".join(f"<code>/post {s}</code>" for s in subs)
            karma_cmds = "  ".join(f"<code>/karma {s}</code>" for s in subs)
            lines.append(f"<b>{product}</b>")
            lines.append(f"  📣 Post: {post_cmds}")
            lines.append(f"  💬 Karma: {karma_cmds}")
            lines.append("")
        return "\n".join(lines).strip()

    if lower == "/missing" or lower.startswith("/missing "):
        return cmd_missing(text[len("/missing"):].strip())

    if lower.startswith("/seturl"):
        args = text[len("/seturl"):].strip()
        return cmd_seturl(args)

    if lower.startswith("/setfree"):
        args = text[len("/setfree"):].strip()
        return cmd_setfree(args)

    if lower == "/syncprices":
        def _sync():
            import subprocess as sp
            r1 = sp.run(
                [sys.executable, str(ROOT / "scripts/publish_product.py"), "--sync-prices"],
                capture_output=True, text=True, cwd=str(ROOT),
            )
            r2 = sp.run(
                [sys.executable, str(ROOT / "scripts/update_site.py"), "--rebuild-all"],
                capture_output=True, text=True, cwd=str(ROOT),
            )
            lines = [l for l in (r1.stdout + r1.stderr).splitlines() if l.strip()]
            updated = sum(1 for l in lines if "Updated" in l or "✅" in l)
            errors = sum(1 for l in lines if "⚠️" in l or "Error" in l)
            send(f"✅ Prices synced — {updated} updated, {errors} warnings.\nVitrine rebuilt.")
        import threading
        send("🔄 Syncing prices from Gumroad…")
        threading.Thread(target=_sync, daemon=True).start()
        return None

    if lower == "/gumroad" or lower.startswith("/gumroad "):
        args = text[len("/gumroad"):].strip()
        return cmd_gumroad_desc(args)

    if lower == "/tweet" or lower.startswith("/tweet "):
        args = text[len("/tweet"):].strip()
        return cmd_tweet(args)

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

    if lower == "/blast" or lower.startswith("/blast "):
        cmd_blast()
        return None

    if lower == "/blog" or lower.startswith("/blog "):
        topic = text[len("/blog"):].strip().strip('"').strip("'")
        flag = ["--auto"] if not topic else ["--topic", topic]
        note = f" on <i>{topic}</i>" if topic else " (auto-topic)"
        send(f"✍️ Generating blog post{note}…")
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/generate_blog_post.py")] + flag,
                cwd=str(ROOT), capture_output=True, text=True, timeout=120
            )
            url = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
            if result.returncode == 0 and url.startswith("http"):
                # git commit + push
                subprocess.run(
                    ["git", "add", "site/blog/", "data/blog-posts.json", "site/sitemap.xml"],
                    cwd=str(ROOT), capture_output=True
                )
                subprocess.run(
                    ["git", "commit", "-m", f"blog: {topic or 'auto-topic'}"],
                    cwd=str(ROOT), capture_output=True
                )
                subprocess.run(["git", "push"], cwd=str(ROOT), capture_output=True)
                return f"📝 <b>Blog post published!</b>\n\n{url}\n\nLive in ~1 min after Cloudflare deploys."
            else:
                err = (result.stderr or "")[-300:]
                return f"❌ Blog post failed:\n<code>{err}</code>"
        except Exception as e:
            return f"❌ Blog error: {e}"

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
                elif cq_data.startswith("holiday:next:"):
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    shown_index = int(cq_data.split(":", 2)[2])  # index already shown (0-based)
                    state = _holiday_state()
                    proposals = state.get("proposals", [])
                    next_index = shown_index + 1  # next to show (0-based)
                    if next_index < len(proposals):
                        from telegram_notify import send_holiday_proposal
                        state["current_proposal_index"] = next_index
                        _save_holiday_state(state)
                        send_holiday_proposal(proposals[next_index], next_index + 1, len(proposals))
                    else:
                        send("✅ Vous avez vu toutes les options! Tapez /holidays pour relancer.", cq_chat_id)
                elif cq_data == "holiday:relaunch":
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    state = _holiday_state()
                    constraints = state.get("constraints", {})
                    if not constraints:
                        send("Aucun critère sauvegardé. Tapez /holidays pour commencer.", cq_chat_id)
                    else:
                        reply = _launch_holiday_research(state)
                        send(reply, cq_chat_id)
                elif cq_data == "holiday:modify":
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    state = _holiday_state()
                    constraints = state.get("constraints", {})
                    if not constraints:
                        send("Aucun critère sauvegardé. Tapez /holidays pour commencer.", cq_chat_id)
                    else:
                        # Restart gathering with pre-filled constraints
                        state["status"] = "gathering"
                        state["step"] = 0
                        state["proposals"] = []
                        _save_holiday_state(state)
                        key, question = HOLIDAY_QUESTIONS[0]
                        existing = constraints.get(key, "")
                        hint = f"\n\n<i>Valeur actuelle: {existing}</i>\nTapez une nouvelle valeur ou <b>ok</b> pour garder." if existing else ""
                        send(f"✏️ <b>Modification des critères</b>\n\nQuestion 1/{len(HOLIDAY_QUESTIONS)}:\n\n{question}{hint}", cq_chat_id)
                elif cq_data in ("blast:send", "blast:regen"):
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    reply = _handle_blast_callback(cq_data)
                    if reply:
                        send(reply, cq_chat_id)
                elif cq_data.startswith("tweet:done:"):
                    pid_short = cq_data.split(":", 2)[2]
                    catalog = read_json("data/product-catalog.json")
                    product_id = next((p["id"] for p in catalog.get("products", []) if p["id"].startswith(pid_short)), pid_short)
                    log("bot", f"Tweet done: {product_id}")
                    try:
                        api("answerCallbackQuery", {"callback_query_id": cq_id})
                    except Exception:
                        pass
                    _log_tweet(product_id, "", "")
                    send("✅ Marked as tweeted. Send /tweet for the next product.", cq_chat_id)
                elif cq_data.startswith("tweet:regen:"):
                    pid_short = cq_data.split(":", 2)[2]
                    catalog = read_json("data/product-catalog.json")
                    product_id = next((p["id"] for p in catalog.get("products", []) if p["id"].startswith(pid_short)), pid_short)
                    log("bot", f"Tweet regen requested: {product_id}")
                    _handle_tweet_regen(product_id, cq_id, cq_chat_id)
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
