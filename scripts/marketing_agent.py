#!/usr/bin/env python3
"""
marketing_agent.py — Autonomous marketing daemon for mini-on-ai.

Runs daily via launchd. Takes actions it can, asks via Telegram for the rest.

Autonomous (no approval needed):
  - Blog post: generate + publish + git push (3x/week max)
  - Dev.to cross-post: auto-publish each blog post to Dev.to after generation
  - Email blast: weekly auto-send to Brevo list when new products exist
  - Generic tweets: copy-paste text via Telegram (no Twitter API)

Telegram copy-paste (~30 sec):
  - Product tweets: draft sent as copy-paste, user posts manually
  - Reddit reply: best matching thread + generated reply copy

One-time:
  - ProductHunt launch instructions (like AppSumo)

Weekly digest (Sundays):
  - Stats + 🎯 best action recommendation

Usage: python3 scripts/marketing_agent.py [--force]
  --force: ignore cooldowns and run all tasks (useful for testing)
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, write_json, log, timestamp, ROOT

import anthropic

# ── Config ────────────────────────────────────────────────────────────────────

MARKETING_STATE     = "data/marketing-state.json"
BLOG_POSTS_PER_WEEK = 3
BLOG_COOLDOWN_DAYS  = 2       # min days between blog posts
TWEET_COOLDOWN_DAYS = 5       # min days between tweet copies
EMAIL_COOLDOWN_DAYS = 7       # min days between email blasts
REDDIT_COOLDOWN_DAYS = 1      # min days between reddit reply copies
REDDIT_MIN_SCORE    = 60      # min score to send a reply copy
REDDIT_MAX_AGE_DAYS = 14      # ignore posts older than this

SITE_URL = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")

# Generic autonomous tweet texts
GENERIC_TWEETS = [
    "🧵 Free this week: Claude Code skill that auto-generates an architecture overview for any codebase.\n\nDrop it in, run /gen-architecture, get a full system map.\n\n{site_url}/products/skills-claude-code-skill-architecture-overview-free-20260326.html\n\n#ClaudeCode #AI",
    "Free n8n workflow: qualify leads and trigger email sequences automatically.\n\nReady to import — no coding.\n\n{site_url}/products/n8n-lead-qualifying-email-n8n-workflow-20260317.html\n\n#n8n #automation #nocode",
    "If you're switching from Zapier to n8n, this free guide maps the concepts 1-to-1.\n\nSaves hours of confusion.\n\n{site_url}/products/guide-n8n-starter-guide-for-zapier-users-20260317.html\n\n#n8n #zapier #automation",
    "You can describe your use case and get a custom AI prompt pack or checklist generated in 30 seconds.\n\nFree preview. $9 to download.\n\n{site_url}/build.html\n\n#AI #productivity #prompts",
    "Free: n8n workflow for PDF image & text extraction.\n\nUseful if you're parsing invoices, receipts, or scanned docs.\n\n{site_url}/products/n8n-pdf-image-text-extraction-n8n-workflow-20260318.html\n\n#n8n #automation #PDF",
]


# ── State helpers ──────────────────────────────────────────────────────────────

def load_state() -> dict:
    try:
        return read_json(MARKETING_STATE)
    except Exception:
        return {}


def _state_defaults(state: dict) -> dict:
    """Ensure all state keys exist with defaults."""
    defaults = {
        "last_blog_post_date": None,
        "blog_posts_this_week": 0,
        "last_tweet_date": None,
        "tweeted_product_ids": [],
        "pending_tweet": None,
        # kept for history, no longer written:
        "directories_submitted": [],
        "pending_directory": None,
        "appsumo_submitted": False,
        "last_run": None,
        # new fields:
        "devto_published_post_ids": [],
        "last_email_blast_date": None,
        "last_reddit_reply_date": None,
        "reddit_replied_post_ids": [],
        "producthunt_submitted": False,
        "generic_tweet_index": 0,
    }
    for k, v in defaults.items():
        state.setdefault(k, v)
    return state


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

    url = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""

    subprocess.run(
        [sys.executable, str(ROOT / "scripts/update_site.py"), "--rebuild-all"],
        capture_output=True, cwd=str(ROOT),
    )
    subprocess.run(["git", "add", "-A"], capture_output=True, cwd=str(ROOT))
    subprocess.run(
        ["git", "commit", "-m", "auto: publish blog post (marketing agent)"],
        capture_output=True, cwd=str(ROOT),
    )
    push = subprocess.run(
        ["git", "push"], capture_output=True, text=True, cwd=str(ROOT),
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
        f"📝 <b>Blog post published</b>\n\n"
        f"{url or 'site rebuilt'}\n"
        f"{'✅ Pushed to Cloudflare' if push_ok else '⚠️ git push failed'}"
    )
    log("marketing", f"Blog post published: {url}")

    # Immediately cross-post to Dev.to
    if push_ok:
        try:
            posts = read_json("data/blog-posts.json").get("posts", [])
            if posts:
                run_devto_cross_post(state, posts[-1])
        except Exception as e:
            log("marketing", f"Dev.to cross-post failed after blog: {e}")


# ── Dev.to cross-post ──────────────────────────────────────────────────────────

def _devto_tags(topic: str) -> list:
    """Map a blog topic string to up to 4 Dev.to tags."""
    t = topic.lower()
    if "n8n" in t:
        return ["n8n", "automation", "nocode", "productivity"]
    if "claude" in t or "claude-code" in t:
        return ["ai", "claudeai", "developer", "productivity"]
    if "automation" in t:
        return ["automation", "python", "productivity", "devops"]
    if "freelanc" in t:
        return ["career", "freelancing", "productivity", "ai"]
    if "prompt" in t:
        return ["ai", "productivity", "chatgpt", "developer"]
    return ["ai", "productivity"]


def devto_publish(post: dict) -> str:
    """
    Publish a blog post to Dev.to. Returns published article URL.
    Raises RuntimeError on failure. Logs and skips on 422 (duplicate).
    """
    api_key = os.getenv("DEV_TO_API_KEY", "")
    if not api_key:
        log("marketing", "DEV_TO_API_KEY not set — skipping Dev.to cross-post")
        return ""

    slug = post.get("slug", "")
    canonical_url = f"{SITE_URL}/blog/{slug}.html" if slug else SITE_URL

    body_md = post.get("body_markdown", "")
    if not body_md:
        # Try loading the actual HTML file and extracting content
        log("marketing", f"No body_markdown in post dict for {post.get('id')} — skipping Dev.to")
        return ""

    footer = f"\n\n---\n*Originally published at [{SITE_URL}]({SITE_URL})*"

    payload = json.dumps({
        "article": {
            "title": post.get("title", ""),
            "body_markdown": body_md + footer,
            "published": True,
            "description": post.get("excerpt", "")[:155],
            "canonical_url": canonical_url,
            "tags": _devto_tags(post.get("topic", "")),
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://dev.to/api/articles",
        data=payload,
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            return data.get("url", "https://dev.to")
    except urllib.error.HTTPError as e:
        if e.code == 422:
            log("marketing", f"Dev.to: duplicate article skipped ({post.get('title', '')})")
            return ""
        raise RuntimeError(f"Dev.to API error {e.code}: {e.read().decode()[:200]}") from None


def _devto_due(state: dict, post_id: str) -> bool:
    return post_id not in state.get("devto_published_post_ids", [])


def run_devto_cross_post(state: dict, post: dict) -> None:
    post_id = post.get("id", "")
    if not _devto_due(state, post_id):
        log("marketing", f"Dev.to: already published {post_id}")
        return

    log("marketing", f"Cross-posting to Dev.to: {post.get('title', '')}")
    try:
        url = devto_publish(post)
    except Exception as e:
        log("marketing", f"Dev.to cross-post error: {e}")
        tg_send(f"⚠️ Dev.to cross-post failed:\n<code>{e}</code>")
        return

    published = state.get("devto_published_post_ids", [])
    published.append(post_id)
    state["devto_published_post_ids"] = published
    save_state(state)

    if url:
        tg_send(f"✅ <b>Cross-posted to Dev.to</b>\n{url}")
        log("marketing", f"Dev.to published: {url}")


# ── Email blast task ───────────────────────────────────────────────────────────

def _new_products_since(days: int) -> list:
    """Return products created in the last N days, by parsing YYYYMMDD from product ID."""
    try:
        catalog = read_json("data/product-catalog.json")
    except Exception:
        return []
    cutoff = date.today() - timedelta(days=days)
    results = []
    for p in catalog.get("products", []):
        pid = p.get("id", "")
        # ID format: category-title-YYYYMMDD
        try:
            date_str = pid[-8:]  # last 8 chars = YYYYMMDD
            product_date = date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
            if product_date >= cutoff:
                results.append(p)
        except (ValueError, IndexError):
            continue
    return results


def _email_blast_due(state: dict, force: bool) -> bool:
    if force:
        return len(_new_products_since(EMAIL_COOLDOWN_DAYS)) >= 1
    last = state.get("last_email_blast_date")
    if last:
        try:
            last_dt = date.fromisoformat(last)
            if (date.today() - last_dt).days < EMAIL_COOLDOWN_DAYS:
                return False
        except ValueError:
            pass
    return len(_new_products_since(EMAIL_COOLDOWN_DAYS)) >= 2


def run_email_blast(state: dict) -> None:
    new_products = _new_products_since(EMAIL_COOLDOWN_DAYS)
    if not new_products:
        log("marketing", "Email blast: no new products this week, skipping")
        return

    log("marketing", f"Generating email blast for {len(new_products)} new products")

    # Build product list for the prompt
    product_lines = []
    for p in new_products[:5]:
        title = p.get("title", "")
        price = p.get("price", 0)
        price_str = "Free" if price == 0 else f"${price // 100}"
        url = p.get("gumroad_url") or f"{SITE_URL}/products/{p.get('id')}.html"
        product_lines.append(f"- {title} ({price_str}): {url}")
    product_list = "\n".join(product_lines)
    first_title = new_products[0].get("title", "new AI tools")

    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": (
                    "Write a short email to subscribers of mini-on-ai.com about new products.\n\n"
                    f"New products this week:\n{product_list}\n\n"
                    "Instructions:\n"
                    "- Under 200 words\n"
                    "- Plain, genuine tone — no marketing superlatives, no 'exciting news'\n"
                    "- Start with what's new, briefly\n"
                    "- End with one line mentioning Build Your Own at https://mini-on-ai.com/build\n"
                    "- Do not add a subject line — just the email body\n"
                    "- Use product URLs as-is (don't shorten or modify them)"
                ),
            }],
        )
        body = resp.content[0].text.strip()
    except Exception as e:
        log("marketing", f"Claude failed for email blast body: {e}")
        lines = [f"New this week on mini-on-ai:\n"]
        for p in new_products[:5]:
            lines.append(f"→ {p.get('title', '')}: {p.get('gumroad_url') or SITE_URL}")
        lines.append(f"\nBuild your own custom prompt pack or checklist in 30 seconds: {SITE_URL}/build")
        body = "\n".join(lines)

    subject = f"New this week on mini-on-ai: {first_title[:50]}"

    # Send via email_blast.py subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/email_blast.py"),
         "--subject", subject, "--body", body],
        capture_output=True, text=True, cwd=str(ROOT),
    )

    state["last_email_blast_date"] = date.today().isoformat()
    save_state(state)

    if result.returncode == 0:
        # Get contact count for notification
        count_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/email_blast.py"), "--count"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        n = count_result.stdout.strip() or "?"
        tg_send(f"📧 <b>Email blast sent</b> to {n} subscribers\n<i>{subject}</i>")
        log("marketing", f"Email blast sent: {subject}")
    else:
        err = result.stderr.strip()[:200] or result.stdout.strip()[:200]
        tg_send(f"⚠️ Email blast failed:\n<code>{err}</code>")
        log("marketing", f"Email blast failed: {err}")


# ── Reddit reply copy task ─────────────────────────────────────────────────────

def _reddit_reply_due(state: dict, force: bool) -> bool:
    if force:
        return True
    last = state.get("last_reddit_reply_date")
    if not last:
        return True
    try:
        last_dt = date.fromisoformat(last)
        return (date.today() - last_dt).days >= REDDIT_COOLDOWN_DAYS
    except ValueError:
        return True


def _parse_found_at(found_at: str) -> date:
    """Parse found_at ISO string to a date."""
    try:
        dt = datetime.fromisoformat(found_at.replace("Z", "+00:00"))
        return dt.date()
    except (ValueError, AttributeError):
        return date(2000, 1, 1)


def run_reddit_reply_copy(state: dict) -> None:
    # Refresh the queue with a fresh scan
    log("marketing", "Running Reddit scan to refresh queue…")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/reddit_scan.py")],
        capture_output=True, cwd=str(ROOT), timeout=120,
    )

    try:
        queue_data = read_json("data/reddit-queue.json")
    except Exception:
        log("marketing", "Reddit queue not found — skipping")
        return

    replied_ids = set(state.get("reddit_replied_post_ids", []))
    cutoff = date.today() - timedelta(days=REDDIT_MAX_AGE_DAYS)

    candidates = [
        p for p in queue_data.get("posts", [])
        if p.get("status") not in ("reply_sent",)
        and p.get("post_id") not in replied_ids
        and p.get("brief", {}).get("score", 0) >= REDDIT_MIN_SCORE
        and _parse_found_at(p.get("found_at", "")) >= cutoff
    ]

    if not candidates:
        log("marketing", "Reddit: no suitable candidates found — skipping")
        return

    # Pick highest score
    post = sorted(candidates, key=lambda x: x.get("brief", {}).get("score", 0), reverse=True)[0]
    brief = post.get("brief", {})
    score = brief.get("score", 0)

    log("marketing", f"Generating Reddit reply for: r/{post['subreddit']} — {post['title'][:60]}")

    # Find best matching product for this post
    try:
        catalog = read_json("data/product-catalog.json")
        cat = brief.get("category", "")
        matching = [p for p in catalog.get("products", []) if p.get("category") == cat and p.get("gumroad_url")]
        product_mention = matching[0] if matching else None
    except Exception:
        product_mention = None

    product_line = ""
    if product_mention and score >= 70:
        product_url = product_mention.get("gumroad_url", f"{SITE_URL}/products/{product_mention['id']}.html")
        product_line = f"\nIf score >= 70, add ONE final line: \"Happen to have built something for this: {product_url}\""

    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": (
                    f"Write a genuine, helpful Reddit reply (3-5 sentences).\n\n"
                    f"Subreddit: r/{post['subreddit']}\n"
                    f"Post title: {post['title']}\n"
                    f"Post body: {(post.get('body') or '')[:500]}\n\n"
                    f"Rules:\n"
                    f"- Answer the question or address the pain point directly first\n"
                    f"- Never start with 'I'\n"
                    f"- Sound human and helpful, not promotional\n"
                    f"- Do not use markdown headers\n"
                    f"{product_line}"
                ),
            }],
        )
        reply_text = resp.content[0].text.strip()
    except Exception as e:
        log("marketing", f"Claude failed for Reddit reply: {e}")
        return

    # Send to Telegram as copy-paste
    tg_send(
        f"💬 <b>Reddit reply copy</b> — r/{post['subreddit']}\n\n"
        f"<i>{post['title'][:80]}</i>\n"
        f"{post['url']}\n\n"
        f"<code>{reply_text}</code>\n\n"
        f"Post manually if relevant (~30 sec)."
    )

    # Update state
    state["last_reddit_reply_date"] = date.today().isoformat()
    replied_ids_list = state.get("reddit_replied_post_ids", [])
    replied_ids_list.append(post["post_id"])
    state["reddit_replied_post_ids"] = replied_ids_list
    save_state(state)

    # Mark post in queue as reply_sent
    try:
        for p in queue_data.get("posts", []):
            if p.get("post_id") == post["post_id"]:
                p["status"] = "reply_sent"
                p["reply_text"] = reply_text
                p["replied_at"] = timestamp()
                break
        write_json("data/reddit-queue.json", queue_data)
    except Exception as e:
        log("marketing", f"Could not update reddit-queue.json: {e}")

    log("marketing", f"Reddit reply copy sent: r/{post['subreddit']} — {post['post_id']}")


# ── Tweet tasks ────────────────────────────────────────────────────────────────

def _unqueued_products(state: dict) -> list:
    tweeted = set(state.get("tweeted_product_ids", []))
    try:
        catalog = read_json("data/product-catalog.json")
    except Exception:
        return []
    return [
        p for p in catalog.get("products", [])
        if p.get("gumroad_url")
        and p["id"] not in tweeted
    ]


def _tweet_due(state: dict, force: bool) -> bool:
    if force:
        return True
    last = state.get("last_tweet_date")
    if not last:
        return True
    try:
        last_dt = date.fromisoformat(last)
        return (date.today() - last_dt).days >= TWEET_COOLDOWN_DAYS
    except ValueError:
        return True


def run_product_tweet(state: dict, product: dict) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from twitter_post import draft_for_product  # noqa: E402

    tweet_text = draft_for_product(product)
    pid = product["id"]

    tweeted = state.get("tweeted_product_ids", [])
    if pid not in tweeted:
        tweeted.append(pid)
    state["tweeted_product_ids"] = tweeted
    state["pending_tweet"] = None
    state["last_tweet_date"] = date.today().isoformat()
    save_state(state)

    tg_send(
        f"🐦 <b>Tweet copy</b> — <i>{product.get('title', '')}</i>\n\n"
        f"<code>{tweet_text}</code>\n\n"
        f"({len(tweet_text)}/280 chars) — post manually if you want."
    )
    log("marketing", f"Tweet copy sent for: {pid}")


def run_generic_tweet(state: dict) -> None:
    idx = state.get("generic_tweet_index", 0) % len(GENERIC_TWEETS)
    text = GENERIC_TWEETS[idx].format(site_url=SITE_URL)

    state["generic_tweet_index"] = idx + 1
    state["last_tweet_date"] = date.today().isoformat()
    save_state(state)

    tg_send(f"🐦 <b>Tweet copy</b>\n\n<code>{text}</code>\n\nPost manually if you want.")
    log("marketing", f"Generic tweet copy sent (idx {idx})")


# ── ProductHunt one-time task ──────────────────────────────────────────────────

def _producthunt_due(state: dict) -> bool:
    return not state.get("producthunt_submitted", False)


def run_producthunt(state: dict) -> None:
    try:
        copy = (ROOT / "data/outreach/producthunt-copy.md").read_text()
    except Exception:
        copy = "See data/outreach/producthunt-copy.md for launch copy."

    # Truncate if too long for Telegram (4096 char limit)
    if len(copy) > 3800:
        copy = copy[:3800] + "\n\n[…see data/outreach/producthunt-copy.md for full copy]"

    tg_send(
        f"🚀 <b>ProductHunt launch copy (one-time)</b>\n\n"
        f"Post on a <b>Tuesday or Wednesday at 12:01am PST</b> for best results.\n\n"
        f"<pre>{copy}</pre>"
    )
    state["producthunt_submitted"] = True
    save_state(state)
    log("marketing", "ProductHunt instructions sent")


# ── Weekly report (Sundays) ────────────────────────────────────────────────────

def _recommend_best_action(state: dict, gumroad_text: str) -> str:
    """Deterministic best-action recommendation based on current state."""
    if not state.get("producthunt_submitted", False):
        return "🚀 Launch on ProductHunt — copy is ready in your Telegram history"

    # Parse free download count from gumroad stats output
    free_downloads = 0
    for line in gumroad_text.splitlines():
        if "free" in line.lower() and any(c.isdigit() for c in line):
            try:
                free_downloads = int("".join(c for c in line if c.isdigit()))
                break
            except ValueError:
                pass

    if free_downloads == 0:
        try:
            queue_data = read_json("data/reddit-queue.json")
            pending = [p for p in queue_data.get("posts", []) if p.get("status") == "pending"]
            return f"💬 Post a Reddit reply — {len(pending)} matching threads in the queue"
        except Exception:
            return "💬 Post a Reddit reply — check the queue"

    devto_count = len(state.get("devto_published_post_ids", []))
    if devto_count == 0:
        return "📝 Add DEV_TO_API_KEY to .env — Dev.to cross-posting will reach 900K developers automatically"

    return "💬 Post the Reddit reply copy — highest-intent traffic for dev tools"


def run_weekly_report(state: dict) -> None:
    log("marketing", "Sending weekly report")
    blog_count = state.get("blog_posts_this_week", 0)
    tweeted = len(state.get("tweeted_product_ids", []))
    devto_count = len(state.get("devto_published_post_ids", []))
    email_last = state.get("last_email_blast_date") or "never"
    reddit_count = len(state.get("reddit_replied_post_ids", []))

    stats_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/gumroad_stats.py"), "--days", "7"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    gumroad_block = stats_result.stdout.strip() if stats_result.returncode == 0 else "❌ Could not fetch Gumroad stats"

    recommendation = _recommend_best_action(state, gumroad_block)

    msg = (
        f"📊 <b>Weekly marketing report</b>\n\n"
        f"📝 Blog posts this week: {blog_count}/{BLOG_POSTS_PER_WEEK}\n"
        f"🔷 Dev.to cross-posts (total): {devto_count}\n"
        f"📧 Last email blast: {email_last}\n"
        f"💬 Reddit replies sent (total): {reddit_count}\n"
        f"🐦 Products tweeted (total): {tweeted}\n\n"
        f"{gumroad_block}\n\n"
        f"🎯 <b>Best action this week:</b> {recommendation}"
    )
    tg_send(msg)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Autonomous marketing agent")
    parser.add_argument("--force", action="store_true", help="Ignore cooldowns (for testing)")
    args = parser.parse_args()

    log("marketing", f"Starting marketing agent (force={args.force})")
    state = load_state()
    state = _state_defaults(state)
    state["last_run"] = timestamp()
    save_state(state)

    actions_taken = []

    # 1. Blog post (+ Dev.to cross-post happens inside run_blog_post)
    if _blog_due(state, args.force):
        run_blog_post(state)
        state = load_state()
        state = _state_defaults(state)
        actions_taken.append("blog")
    else:
        log("marketing", "Blog post not due — skipping")

    # 2. Reddit reply copy (daily)
    if _reddit_reply_due(state, args.force):
        run_reddit_reply_copy(state)
        state = load_state()
        state = _state_defaults(state)
        actions_taken.append("reddit_reply")
    else:
        log("marketing", "Reddit reply not due — skipping")

    # 3. Tweet copy (every 5 days)
    if _tweet_due(state, args.force):
        unqueued = _unqueued_products(state)
        if unqueued:
            run_product_tweet(state, unqueued[0])
            state = load_state()
            actions_taken.append("product_tweet")
        else:
            run_generic_tweet(state)
            state = load_state()
            actions_taken.append("generic_tweet")
    else:
        log("marketing", "Tweet not due — skipping")

    # 4. Email blast (weekly, if new products exist)
    if _email_blast_due(state, args.force):
        run_email_blast(state)
        state = load_state()
        state = _state_defaults(state)
        actions_taken.append("email_blast")
    else:
        log("marketing", "Email blast not due — skipping")

    # 5. ProductHunt one-time
    if _producthunt_due(state):
        run_producthunt(state)
        state = load_state()
        state = _state_defaults(state)
        actions_taken.append("producthunt")

    # 6. Weekly digest (Sundays = weekday 6)
    if args.force or date.today().weekday() == 6:
        run_weekly_report(state)
        actions_taken.append("report")

    if not actions_taken:
        log("marketing", "No actions due today")
    else:
        log("marketing", f"Done — actions: {', '.join(actions_taken)}")


if __name__ == "__main__":
    main()
