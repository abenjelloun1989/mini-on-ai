#!/usr/bin/env python3
"""
reddit_pipeline.py
Demand-driven pipeline: scan Reddit → assess needs → Telegram approval batch →
on approval: generate product → package → publish → send reply copy.

Usage:
  python3 scripts/reddit_pipeline.py              # full scan + Telegram batch
  python3 scripts/reddit_pipeline.py --dry-run    # scan only, print to console
  python3 scripts/reddit_pipeline.py --build <post_id>  # build product for a queued post
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, write_json, timestamp, log, ROOT, get_run_token_summary
from reddit_scan import run_scan, BUILDABLE_CATEGORIES
from generate_product import generate_product
from package_product import package_product
from update_site import update_site
from telegram_notify import send_reddit_approval, send_reddit_built


def _get_subreddits(override: str = "") -> list:
    from reddit_scan import DEFAULT_SUBREDDITS
    raw = override or os.getenv("REDDIT_SUBREDDITS", DEFAULT_SUBREDDITS)
    return [s.strip() for s in raw.split(",") if s.strip()]


def _update_queue_post(post_id: str, **updates):
    """Update a post in reddit-queue.json by post_id."""
    queue = read_json("data/reddit-queue.json")
    for p in queue.get("posts", []):
        if p["post_id"] == post_id:
            p.update(updates)
            break
    write_json("data/reddit-queue.json", queue)


def _get_queue_post(post_id: str) -> dict:
    queue = read_json("data/reddit-queue.json")
    for p in queue.get("posts", []):
        if p["post_id"] == post_id:
            return p
    raise ValueError(f"Post {post_id} not found in reddit-queue.json")


def build_for_post(post_id: str):
    """
    Build a product for a queued Reddit post.
    Called after the user approves via Telegram.
    """
    post_entry = _get_queue_post(post_id)
    brief = post_entry.get("brief", {})

    log("reddit-pipeline", f"Building product for post: {post_entry['title'][:60]}")

    # Inject into idea-backlog so generate_product can pick it up
    backlog = read_json("data/idea-backlog.json")
    idea = {
        "id": f"idea-reddit-{post_id}",
        "title": brief.get("title", post_entry["title"]),
        "description": brief.get("description", ""),
        "category": brief.get("category", "prompt-packs"),
        "tags": brief.get("tags", []),
        "score": brief.get("score", 75),
        "rationale": f"Sourced from Reddit r/{post_entry['subreddit']}: {post_entry['url']}",
        "selected": True,
        "status": None,
        "product_id": None,
        "generated_at": timestamp(),
        "source": "reddit-scan",
        "reddit_post_id": post_id,
        "reddit_url": post_entry["url"],
    }
    backlog.setdefault("ideas", []).append(idea)
    write_json("data/idea-backlog.json", backlog)

    start_time = time.time()
    run_id = f"run-reddit-{int(time.time())}"
    os.environ["PIPELINE_RUN_ID"] = run_id

    _update_queue_post(post_id, status="building")

    try:
        log("reddit-pipeline", "Stage: generate-product")
        meta = generate_product()

        log("reddit-pipeline", "Stage: package-product")
        meta = package_product()

        log("reddit-pipeline", "Stage: update-site")
        meta = update_site()
    except Exception as e:
        log("reddit-pipeline", f"Build failed: {e}")
        _update_queue_post(post_id, status="build-failed", error=str(e))
        raise

    # Try Gumroad publish (non-fatal)
    gumroad_url = None
    try:
        from publish_product import publish_product
        meta = publish_product()
        gumroad_url = meta.get("gumroad_url")
    except Exception as e:
        log("reddit-pipeline", f"Warning: Gumroad publish failed (non-fatal): {e}")

    site_url = os.getenv("SITE_URL", "https://mini-on-ai.com")
    product_url = gumroad_url or f"{site_url}/products/{meta['id']}.html"

    # Compose copy-paste Reddit reply
    reply_text = _compose_reply(post_entry, meta, product_url)

    _update_queue_post(
        post_id,
        status="built",
        product_id=meta["id"],
        reply_text=reply_text,
    )

    # Git commit
    try:
        subprocess.run(
            ["git", "add", "site/", "data/", f"products/{meta['id']}/"],
            cwd=str(ROOT), check=True, capture_output=True
        )
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(ROOT), capture_output=True
        )
        if diff.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"product (reddit): {meta['title']}"],
                cwd=str(ROOT), check=True, capture_output=True
            )
        subprocess.run(["git", "push"], cwd=str(ROOT), capture_output=True)
        log("reddit-pipeline", "Git commit + push done")
    except Exception as e:
        log("reddit-pipeline", f"Warning: git error: {e}")

    # Telegram: send built notification with copy-paste reply
    duration = round(time.time() - start_time)
    log("reddit-pipeline", f"Build complete in {duration}s — sending Telegram notification")
    try:
        send_reddit_built(post_entry, meta, product_url, reply_text)
    except Exception as e:
        log("reddit-pipeline", f"Warning: Telegram notification failed: {e}")

    log("reddit-pipeline", f"Done! Product: {meta['title']}")
    log("reddit-pipeline", f"URL: {product_url}")
    return meta


def _compose_reply(post_entry: dict, meta: dict, product_url: str) -> str:
    """Compose a natural, copy-paste Reddit reply."""
    sub = post_entry.get("subreddit", "")
    title = meta.get("title", "")
    description = meta.get("description", "")
    category = meta.get("category", "")

    type_label = {
        "prompt-packs": "prompt pack",
        "checklist": "checklist",
        "swipe-file": "swipe file",
        "mini-guide": "mini guide",
        "n8n-template": "n8n workflow template",
        "claude-code-skill": "Claude Code skill pack",
    }.get(category, "resource")

    return (
        f"Hey! I actually built a {type_label} for exactly this — {title}.\n\n"
        f"{description}\n\n"
        f"It's free (pay what you want): {product_url}\n\n"
        f"Hope it helps!"
    )


def reddit_pipeline(dry_run: bool = False, subreddit: str = ""):
    """Main entry: scan subreddits, assess, send Telegram batch."""
    subreddits = _get_subreddits(override=subreddit)
    log("reddit-pipeline", f"Starting Reddit demand scan on: {', '.join(subreddits)}")

    candidates = run_scan(subreddits, max_candidates=10, dry_run=dry_run)

    if dry_run:
        log("reddit-pipeline", f"Dry run complete — {len(candidates)} candidates found")
        return

    if not candidates:
        log("reddit-pipeline", "No viable candidates found — nothing to send")
        return

    log("reddit-pipeline", f"Sending {len(candidates)} candidates to Telegram...")
    sent = 0
    for post, brief in candidates:
        try:
            send_reddit_approval(post, brief)
            sent += 1
            time.sleep(0.3)  # avoid Telegram rate limit (30 msg/sec)
        except Exception as e:
            log("reddit-pipeline", f"Warning: could not send Telegram for {post['post_id']}: {e}")

    log("reddit-pipeline", f"Sent {sent}/{len(candidates)} approval requests to Telegram")
    log("reddit-pipeline", "Approve items in Telegram then run: python3 scripts/reddit_pipeline.py --build <post_id>")


def main():
    parser = argparse.ArgumentParser(description="Reddit demand-driven pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, print to console")
    parser.add_argument("--build", metavar="POST_ID", help="Build product for this queued post ID")
    args = parser.parse_args()

    if args.build:
        build_for_post(args.build)
    else:
        reddit_pipeline(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
