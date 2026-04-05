#!/usr/bin/env python3
"""
marketing_agent.py — Autonomous marketing daemon for mini-on-ai.

Runs daily via launchd. Takes actions it can, asks via Telegram for the rest.

Actions (no approval needed):
  - Blog post: generate + publish + git push (3x/week max)
  - Generic tweets: post autonomously when no product tweet pending (every 5+ days)

Actions (Telegram button approval):
  - Product tweets: draft tweet, send with [✅ Post] [⏭ Skip], user taps

Instructions (Telegram copy-paste, ~2 min user effort):
  - Weekly directory submission: Claude-written blurb + form URL sent Monday

Weekly digest (Sundays):
  - Blog posts published, tweets sent, directories done, Gumroad stats

Usage: python3 scripts/marketing_agent.py [--force]
  --force: ignore cooldowns and run all tasks (useful for testing)
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, write_json, log, timestamp, ROOT

import anthropic

# ── Config ────────────────────────────────────────────────────────────────────

MARKETING_STATE = "data/marketing-state.json"
BLOG_POSTS_PER_WEEK = 3
BLOG_COOLDOWN_DAYS  = 2       # min days between blog posts
TWEET_COOLDOWN_DAYS = 5       # min days between generic tweets

SITE_URL = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")

# AI directories to submit to, in order
DIRECTORIES = [
    {"name": "There's An AI For That", "url": "https://theresanaiforthat.com/submit/"},
    {"name": "FuturePedia",            "url": "https://www.futurepedia.io/submit-tool"},
    {"name": "ToolPilot",              "url": "https://www.toolpilot.ai/pages/submit-ai-tool"},
    {"name": "AI Tools Directory",     "url": "https://aitoolsdirectory.com/submit"},
    {"name": "ProductHunt",            "url": "https://www.producthunt.com/posts/new"},
    {"name": "TopAI.tools",            "url": "https://topai.tools/submit"},
    {"name": "AI Valley",              "url": "https://aivalley.ai/submit-tool/"},
    {"name": "Insidr.ai",              "url": "https://www.insidr.ai/submit-tool/"},
    {"name": "AlternativeTo",          "url": "https://alternativeto.net/add-software/"},
    {"name": "Productivity Directory", "url": "https://productivity.directory/submit"},
]

# Generic autonomous tweets — no product promotion, just value
GENERIC_TWEETS = [
    "🧵 Free this week: Claude Code skill that auto-generates an architecture overview for any codebase.\n\nDrop it in, run /gen-architecture, get a full system map.\n\n{site_url}/products/skills-claude-code-skill-architecture-overview-free-20260326.html\n\n#ClaudeCode #AI",
    "Free n8n workflow: qualify leads and trigger email sequences automatically.\n\nReady to import — no coding.\n\n{site_url}/products/n8n-lead-qualifying-email-n8n-workflow-20260317.html\n\n#n8n #automation #nocode",
    "If you're switching from Zapier to n8n, this free guide maps the concepts 1-to-1.\n\nSaves hours of confusion.\n\n{site_url}/products/guide-n8n-starter-guide-for-zapier-users-20260317.html\n\n#n8n #zapier #automation",
    "You can describe your use case and get a custom AI prompt pack or checklist generated in 30 seconds.\n\nFree preview. $9 to download.\n\n{site_url}/build.html\n\n#AI #productivity #prompts",
    "Free: n8n workflow for PDF image & text extraction.\n\nUseful if you're parsing invoices, receipts, or scanned docs.\n\n{site_url}/products/n8n-pdf-image-text-extraction-n8n-workflow-20260318.html\n\n#n8n #automation #PDF",
]
_generic_tweet_index = 0  # rotates through the list


# ── State helpers ──────────────────────────────────────────────────────────────

def load_state() -> dict:
    try:
        return read_json(MARKETING_STATE)
    except Exception:
        return {
            "last_blog_post_date": None,
            "blog_posts_this_week": 0,
            "last_tweet_date": None,
            "tweeted_product_ids": [],
            "pending_tweet": None,
            "directories_submitted": [],
            "appsumo_submitted": False,
            "last_run": None,
        }


def save_state(state: dict) -> None:
    write_json(MARKETING_STATE, state)


# ── Telegram helpers ───────────────────────────────────────────────────────────

def _tg_api(method: str, data: dict) -> dict:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    url = f"https://api.telegram.org/bot{token}/{method}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def tg_send(text: str) -> None:
    chat_id = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID", "")
    _tg_api("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def tg_send_buttons(text: str, buttons: list) -> None:
    """Send a message with one row of inline keyboard buttons."""
    chat_id = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID", "")
    _tg_api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [buttons]},
    })


# ── Blog post task ─────────────────────────────────────────────────────────────

def _blog_due(state: dict, force: bool) -> bool:
    if force:
        return True
    if state.get("blog_posts_this_week", 0) >= BLOG_POSTS_PER_WEEK:
        return False
    last = state.get("last_blog_post_date")
    if not last:
        return True
    try:
        last_dt = date.fromisoformat(last)
        return (date.today() - last_dt).days >= BLOG_COOLDOWN_DAYS
    except ValueError:
        return True


def _week_start() -> str:
    """ISO date of this Monday."""
    today = date.today()
    return (today - timedelta(days=today.weekday())).isoformat()


def run_blog_post(state: dict) -> None:
    log("marketing", "Blog post due — generating…")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate_blog_post.py"), "--auto"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    if result.returncode != 0:
        err = result.stderr.strip()[:300]
        log("marketing", f"Blog generation failed: {err}")
        tg_send(f"⚠️ <b>Marketing agent</b> — blog post generation failed:\n<code>{err}</code>")
        return

    # Parse the published URL from stdout
    url = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""

    # Rebuild site and push
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/update_site.py"), "--rebuild-all"],
        capture_output=True, cwd=str(ROOT),
    )
    subprocess.run(
        ["git", "add", "-A"],
        capture_output=True, cwd=str(ROOT),
    )
    subprocess.run(
        ["git", "commit", "-m", "auto: publish blog post (marketing agent)"],
        capture_output=True, cwd=str(ROOT),
    )
    push = subprocess.run(
        ["git", "push"],
        capture_output=True, text=True, cwd=str(ROOT),
    )

    today_str = date.today().isoformat()
    this_week = _week_start()
    if state.get("_week_start") != this_week:
        state["_week_start"] = this_week
        state["blog_posts_this_week"] = 0

    state["last_blog_post_date"] = today_str
    state["blog_posts_this_week"] = state.get("blog_posts_this_week", 0) + 1
    save_state(state)

    push_ok = push.returncode == 0
    tg_send(
        f"📝 <b>Blog post published</b> (marketing agent)\n\n"
        f"{url or 'site rebuilt'}\n"
        f"{'✅ Pushed to Cloudflare' if push_ok else '⚠️ git push failed — check logs'}"
    )
    log("marketing", f"Blog post published: {url}")


# ── Tweet tasks ────────────────────────────────────────────────────────────────

def _unqueued_products(state: dict) -> list:
    """Products that have a Gumroad URL but haven't been tweeted yet."""
    tweeted = set(state.get("tweeted_product_ids", []))
    pending_id = (state.get("pending_tweet") or {}).get("product_id")
    try:
        catalog = read_json("data/product-catalog.json")
    except Exception:
        return []
    return [
        p for p in catalog.get("products", [])
        if p.get("gumroad_url")
        and p["id"] not in tweeted
        and p["id"] != pending_id
    ]


def _tweet_due(state: dict, force: bool) -> bool:
    if force:
        return True
    if state.get("pending_tweet"):
        return False  # already waiting for approval
    last = state.get("last_tweet_date")
    if not last:
        return True
    try:
        last_dt = date.fromisoformat(last)
        return (date.today() - last_dt).days >= TWEET_COOLDOWN_DAYS
    except ValueError:
        return True


def run_product_tweet(state: dict, product: dict) -> None:
    """Draft a product tweet and send as copy-paste text via Telegram."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from twitter_post import draft_for_product  # noqa: E402

    tweet_text = draft_for_product(product)
    pid = product["id"]

    # Mark as done immediately — no API posting, just copy-paste
    tweeted = state.get("tweeted_product_ids", [])
    if pid not in tweeted:
        tweeted.append(pid)
    state["tweeted_product_ids"] = tweeted
    state["pending_tweet"] = None
    state["last_tweet_date"] = date.today().isoformat()
    save_state(state)

    msg = (
        f"🐦 <b>Tweet copy</b> — <i>{product.get('title', '')}</i>\n\n"
        f"<code>{tweet_text}</code>\n\n"
        f"({len(tweet_text)}/280 chars) — post manually if you want."
    )
    tg_send(msg)
    log("marketing", f"Tweet copy sent for: {pid}")


def run_generic_tweet(state: dict) -> None:
    """Send a generic tweet as copy-paste text via Telegram."""
    idx = state.get("generic_tweet_index", 0) % len(GENERIC_TWEETS)
    text = GENERIC_TWEETS[idx].format(site_url=SITE_URL)

    state["generic_tweet_index"] = idx + 1
    state["last_tweet_date"] = date.today().isoformat()
    save_state(state)

    tg_send(f"🐦 <b>Tweet copy</b>\n\n<code>{text}</code>\n\nPost manually if you want.")
    log("marketing", f"Generic tweet copy sent (idx {idx})")


# ── Directory submission task ──────────────────────────────────────────────────

def _directory_due(state: dict, force: bool) -> bool:
    """Run on Mondays (or force)."""
    if force:
        submitted = state.get("directories_submitted", [])
        return len(submitted) < len(DIRECTORIES)
    if date.today().weekday() != 0:  # Monday = 0
        return False
    submitted = state.get("directories_submitted", [])
    return len(submitted) < len(DIRECTORIES)


def run_directory_submission(state: dict) -> None:
    submitted = state.get("directories_submitted", [])
    remaining = [d for d in DIRECTORIES if d["name"] not in submitted]
    if not remaining:
        log("marketing", "All directories already submitted")
        return

    directory = remaining[0]
    log("marketing", f"Generating directory submission for: {directory['name']}")

    # Use Claude to generate submission copy
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": (
                    f"Write a submission for mini-on-ai.com to be listed on {directory['name']}.\n\n"
                    "mini-on-ai is an AI product factory: a Python pipeline on a Mac mini that "
                    "auto-generates Claude Code skill packs, n8n workflow templates, prompt packs, "
                    "checklists, and mini-guides. 57 products live. Visitors can also build a "
                    "custom AI product (prompt pack or checklist) in 30 seconds at mini-on-ai.com/build for $9.\n\n"
                    "Write:\n"
                    "- Name: (product/tool name)\n"
                    "- Tagline: (one sentence, max 60 chars)\n"
                    "- Description: (150-200 words, benefit-focused, no hype)\n"
                    "- Category: (pick the most relevant: Productivity / Developer Tools / AI / Automation)\n"
                    "- URL: https://mini-on-ai.com\n"
                    "- Tags: (5-8 comma-separated keywords)\n\n"
                    "Be specific and honest. No buzzwords."
                ),
            }],
        )
        copy = resp.content[0].text.strip()
    except Exception as e:
        copy = (
            "Name: mini-on-ai\n"
            "Tagline: AI-generated Claude skills & workflows — 57 products, new ones weekly.\n"
            "Description: mini-on-ai is a showcase of AI-generated digital products built by a Python "
            "pipeline running on a Mac mini. Products include Claude Code skill packs (drop-in skills "
            "for code review, architecture, testing), n8n workflow templates (ready-to-import automations), "
            "prompt packs (20-30 ready-to-use prompts), checklists, and mini-guides. 15 products are free. "
            "Paid products range from $5-$49. The Build Your Own feature generates a custom prompt pack or "
            "checklist for any use case in 30 seconds — free preview, $9 to download.\n"
            "Category: Developer Tools / AI / Productivity\n"
            "URL: https://mini-on-ai.com\n"
            "Tags: Claude, AI, automation, n8n, prompts, Claude Code, workflows, productivity"
        )
        log("marketing", f"Claude failed for directory copy, using fallback: {e}")

    # Store pending directory so the bot knows which one to mark done
    state["pending_directory"] = directory["name"]
    save_state(state)

    msg = (
        f"📋 <b>Directory submission — {directory['name']}</b>\n\n"
        f"Open the form: {directory['url']}\n\n"
        f"Copy-paste this:\n\n"
        f"<code>{copy}</code>\n\n"
        f"Takes ~2 min. Reply <b>/marketing-done-dir</b> when submitted."
    )
    tg_send(msg)
    log("marketing", f"Directory instructions sent: {directory['name']}")


# ── AppSumo one-time task ──────────────────────────────────────────────────────

def run_appsumo(state: dict) -> None:
    msg = (
        "🚀 <b>AppSumo submission (one-time)</b>\n\n"
        "Go to: https://partners.appsumo.com/apply\n\n"
        "Fill in:\n"
        "• <b>Product name:</b> mini-on-ai — Build Your Own AI Product\n"
        "• <b>Website:</b> https://mini-on-ai.com/build.html\n"
        "• <b>What it does:</b> Describe a use case, get a custom AI prompt pack or checklist "
        "generated in 30 seconds. Free preview, $9 to download. Built on Claude API + Cloudflare Workers.\n"
        "• <b>Category:</b> AI Tools / Productivity\n"
        "• <b>Deal type:</b> Pay-once lifetime access OR credit bundle\n\n"
        "Reply <b>/marketing-done-appsumo</b> when submitted."
    )
    tg_send(msg)
    log("marketing", "AppSumo instructions sent")


# ── Weekly report (Sundays) ────────────────────────────────────────────────────

def run_weekly_report(state: dict) -> None:
    log("marketing", "Sending weekly report")
    blog_count = state.get("blog_posts_this_week", 0)
    tweeted = len(state.get("tweeted_product_ids", []))
    dirs_done = len(state.get("directories_submitted", []))
    dirs_total = len(DIRECTORIES)

    # Gumroad stats
    stats_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/gumroad_stats.py"), "--days", "7"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    gumroad_block = stats_result.stdout.strip() if stats_result.returncode == 0 else "❌ Could not fetch Gumroad stats"

    msg = (
        f"📊 <b>Weekly marketing report</b>\n\n"
        f"Blog posts this week: {blog_count}/{BLOG_POSTS_PER_WEEK}\n"
        f"Products tweeted (total): {tweeted}\n"
        f"Directories submitted: {dirs_done}/{dirs_total}\n\n"
        f"{gumroad_block}"
    )
    tg_send(msg)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Autonomous marketing agent")
    parser.add_argument("--force", action="store_true", help="Ignore cooldowns (for testing)")
    args = parser.parse_args()

    log("marketing", f"Starting marketing agent (force={args.force})")
    state = load_state()
    state["last_run"] = timestamp()
    save_state(state)

    today = date.today()
    actions_taken = []

    # 1. Blog post
    if _blog_due(state, args.force):
        run_blog_post(state)
        state = load_state()  # reload after potential write
        actions_taken.append("blog")
    else:
        log("marketing", "Blog post not due — skipping")

    # 2. Product tweet approval request
    if _tweet_due(state, args.force):
        unqueued = _unqueued_products(state)
        if unqueued:
            run_product_tweet(state, unqueued[0])
            state = load_state()
            actions_taken.append("product_tweet")
        elif not state.get("pending_tweet"):
            # No new products — try a generic tweet
            run_generic_tweet(state)
            state = load_state()
            actions_taken.append("generic_tweet")
    else:
        log("marketing", "Tweet not due — skipping")

    # 3. Directory submission (Mondays)
    if _directory_due(state, args.force):
        run_directory_submission(state)
        actions_taken.append("directory")
    else:
        log("marketing", "Directory submission not due — skipping")

    # 4. AppSumo (one-time)
    if not state.get("appsumo_submitted", False) and (args.force or today.weekday() == 0):
        run_appsumo(state)
        actions_taken.append("appsumo")

    # 5. Weekly digest (Sundays = weekday 6)
    if args.force or today.weekday() == 6:
        run_weekly_report(state)
        actions_taken.append("report")

    if not actions_taken:
        log("marketing", "No actions due today")
    else:
        log("marketing", f"Done — actions: {', '.join(actions_taken)}")


if __name__ == "__main__":
    main()
