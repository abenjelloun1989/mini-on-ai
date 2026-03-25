#!/usr/bin/env python3
"""
karma_scout.py
Scans target subreddits for posts worth commenting on, then drafts a
human-sounding comment for each one. Sends results to Telegram as
copy-paste ready messages.

Usage:
  python3 scripts/karma_scout.py              # scan + send to Telegram
  python3 scripts/karma_scout.py --dry-run    # print to console only
  python3 scripts/karma_scout.py --max 10     # get 10 posts (default 5)
"""

import argparse
import json
import os
import sys
import time
import random
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import anthropic
from lib.utils import read_json, write_json, timestamp, log, ROOT

REDDIT_USER_AGENT = "script:mini-on-ai-karma-scout:v1.0 (by /u/minionai)"


def _reddit_new(subreddit: str, limit: int = 25) -> list:
    """Fetch newest posts from a subreddit via api.reddit.com (no auth required)."""
    params = urllib.parse.urlencode({"limit": limit})
    url = f"https://api.reddit.com/r/{subreddit}/new?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": REDDIT_USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        children = json.loads(resp.read().decode("utf-8")).get("data", {}).get("children", [])
    return [c["data"] for c in children if c.get("kind") == "t3"]

KARMA_SUBREDDITS = [
    # Claude Code skills packs ($5 each)
    "ClaudeAI",
    "cursor",
    "ExperiencedDevs",
    "learnprogramming",
    # ATS Resume Rewriter
    "resumes",
    "jobs",
    "cscareerquestions",
    # n8n templates
    "n8n",
    "nocode",
    "zapier",
    # Freelance products
    "freelance",
    "consulting",
    # General AI / productivity
    "ChatGPT",
    "productivity",
    "Entrepreneur",
]

_SITE = "https://mini-on-ai.com"

SUBREDDIT_TO_PRODUCT = {
    "ClaudeAI":         ("Claude Code Skills Packs", _SITE),
    "cursor":           ("Claude Code Skills Packs", _SITE),
    "ExperiencedDevs":  ("Claude Code Skills Packs", _SITE),
    "learnprogramming": ("Claude Code Skills Packs", _SITE),
    "resumes":          ("ATS Resume Bullet Rewriter", f"{_SITE}/products/prompts-ats-optimized-resume-bullet-rewriter-by--2.html"),
    "jobs":             ("ATS Resume Bullet Rewriter", f"{_SITE}/products/prompts-ats-optimized-resume-bullet-rewriter-by--2.html"),
    "cscareerquestions":("ATS Resume Bullet Rewriter", f"{_SITE}/products/prompts-ats-optimized-resume-bullet-rewriter-by--2.html"),
    "n8n":              ("n8n Workflow Templates", _SITE),
    "nocode":           ("n8n Workflow Templates", _SITE),
    "zapier":           ("n8n Workflow Templates", _SITE),
    "freelance":        ("Freelance Proposal & Pricing Swipe Files", _SITE),
    "consulting":       ("Freelance Proposal & Pricing Swipe Files", _SITE),
}


def _assess_and_draft(post: dict) -> Optional[dict]:
    """
    Use Claude Haiku to score the post for commentability and draft a comment.
    Returns dict with score and comment, or None on failure.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    title = post["title"]
    body = post["body"][:400] if post["body"] else ""
    sub = post["subreddit"]

    text_excerpt = f"Title: {title}"
    if body:
        text_excerpt += f"\n\nBody: {body}"

    prompt = f"""You are helping someone build Reddit karma by writing genuinely helpful comments on posts in r/{sub}.

Post:
{text_excerpt}

Your job:
1. Score this post 0-100 for "commentability": how likely would a short, helpful comment get upvotes here?
   - 80-100: Clear question or struggle we can directly answer with practical advice
   - 60-79: Good discussion where a helpful tip would be well received
   - 40-59: Vague or already well-answered
   - 0-39: Showcase post, meme, news, or no room to add value

2. If score >= 65, write a comment draft. Rules:
   - 2 to 4 sentences max
   - Sounds like a real person sharing experience, not an AI assistant
   - Genuinely helpful — concrete, specific, actionable
   - No em-dashes, no "As someone who...", no "Great question!", no bullet lists
   - No links, no product mentions, no self-promotion
   - Natural conversational tone

Respond ONLY with valid JSON (no markdown):
{{
  "score": <0-100 integer>,
  "comment": "<draft comment, or empty string if score < 65>"
}}"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        return json.loads(raw)
    except Exception as e:
        log("karma-scout", f"Warning: assess failed for {post['post_id']}: {e}")
        return None


def comment_for_url(url: str) -> str:
    """
    Fetch a Reddit post by URL and draft a comment for it.
    Returns the comment string, or an error message.
    """
    import re
    m = re.search(r"/comments/([a-z0-9]+)", url)
    if not m:
        return "Could not parse post ID from URL."

    post_id = m.group(1)
    # Try to infer subreddit from URL
    sub_m = re.search(r"/r/([^/]+)/", url)
    subreddit = sub_m.group(1) if sub_m else "reddit"

    json_url = f"https://api.reddit.com/comments/{post_id}.json?limit=1"
    req = urllib.request.Request(json_url, headers={"User-Agent": REDDIT_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        post_data = data[0]["data"]["children"][0]["data"]
        subreddit = post_data.get("subreddit", subreddit)
        title = post_data.get("title", "")
        body = (post_data.get("selftext") or "")[:600]
        if body in ("[removed]", "[deleted]"):
            body = ""
    except Exception:
        return (
            "Reddit API is temporarily blocked from this IP.\n\n"
            "Use /draft instead — paste the post title and body directly:\n\n"
            "/draft r/SubName | Post title here | Optional post body here"
        )

    post = {
        "post_id": post_id,
        "subreddit": subreddit,
        "title": title,
        "body": body,
        "url": url,
        "score": 0,
        "created_utc": 0,
    }

    result = _assess_and_draft(post)
    if not result:
        return "Could not generate comment (API error)."

    comment = result.get("comment", "").strip()
    if not comment:
        return f"Score {result.get('score', 0)}/100 — not a great post to comment on."

    return (
        f"r/{subreddit} | Score {result.get('score', 0)}/100\n"
        f"Post: {title[:80]}\n\n"
        f"Comment draft:\n\n"
        f"{comment}"
    )


def draft_from_text(subreddit: str, title: str, body: str = "") -> str:
    """
    Draft a comment from raw text — no Reddit API needed.
    """
    post = {
        "post_id": "manual",
        "subreddit": subreddit,
        "title": title,
        "body": body[:600],
        "url": "",
        "score": 0,
        "created_utc": 0,
    }

    result = _assess_and_draft(post)
    if not result:
        return "Could not generate comment (API error)."

    comment = result.get("comment", "").strip()
    if not comment:
        return f"Score {result.get('score', 0)}/100 — not a great post to comment on."

    return (
        f"r/{subreddit} | Score {result.get('score', 0)}/100\n\n"
        f"{comment}"
    )


def karma_scout(max_results: int = 5, dry_run: bool = False) -> list:
    """
    Scan subreddits, assess posts, draft comments, send to Telegram.
    Returns list of (post, assessment) tuples for results sent.
    """
    # Load already-seen post IDs from karma queue
    queue = read_json("data/karma-queue.json")
    seen_ids = {p["post_id"] for p in queue.get("posts", [])}

    candidates = []
    seen_in_run = set()

    for sub in KARMA_SUBREDDITS:
        if len(candidates) >= max_results * 6:
            break
        try:
            posts = _reddit_new(sub, limit=25)
        except Exception as e:
            log("karma-scout", f"Warning: Reddit fetch failed r/{sub}: {e}")
            time.sleep(2)
            continue

        for post in posts:
            post_id = post.get("id", "")
            if not post_id or post_id in seen_ids or post_id in seen_in_run:
                continue
            # Skip removed/deleted posts
            body = (post.get("selftext") or "")
            if body in ("[removed]", "[deleted]"):
                body = ""
            seen_in_run.add(post_id)
            candidates.append({
                "post_id": post_id,
                "subreddit": post.get("subreddit", sub),
                "title": post.get("title", ""),
                "body": body[:600].strip(),
                "url": f"https://reddit.com{post.get('permalink', '')}",
                "score": post.get("score", 0),
                "created_utc": post.get("created_utc", 0),
            })

        time.sleep(0.5)

    random.shuffle(candidates)
    log("karma-scout", f"Collected {len(candidates)} unique candidates across {len(KARMA_SUBREDDITS)} subreddits")

    results = []
    for post in candidates:
        if len(results) >= max_results:
            break

        log("karma-scout", f"Assessing: {post['title'][:60]}…")
        assessment = _assess_and_draft(post)
        if not assessment:
            continue

        score = assessment.get("score", 0)
        comment = assessment.get("comment", "").strip()

        if score < 65 or not comment:
            log("karma-scout", f"  Score {score} — skipping")
            continue

        log("karma-scout", f"  Score {score} — good candidate")

        if dry_run:
            print(f"\n{'='*60}")
            print(f"r/{post['subreddit']}  |  Score: {score}")
            print(f"Post: {post['title']}")
            print(f"URL:  {post['url']}")
            print(f"\nDraft comment:\n{comment}")
        else:
            # Save to karma queue
            queue.setdefault("posts", []).append({
                "post_id": post["post_id"],
                "subreddit": post["subreddit"],
                "title": post["title"],
                "url": post["url"],
                "found_at": timestamp(),
                "comment_draft": comment,
                "score": score,
                "status": "pending",
            })
            write_json("data/karma-queue.json", queue)

            # Send to Telegram
            try:
                from telegram_notify import send_karma_draft
                hint = SUBREDDIT_TO_PRODUCT.get(post["subreddit"])
                send_karma_draft(post, comment, score, product_hint=hint)
                time.sleep(0.4)  # avoid Telegram rate limit
            except Exception as e:
                log("karma-scout", f"Warning: Telegram send failed: {e}")

        results.append((post, assessment))
        time.sleep(0.5)

    log("karma-scout", f"Done — {len(results)} comments {'printed' if dry_run else 'sent to Telegram'}")

    if not results and not dry_run:
        try:
            from telegram_notify import send_telegram
            send_telegram(
                "⚠️ <b>/karma</b> — Reddit API is temporarily blocked (rate limit).\n\n"
                "Use /draft instead:\n"
                "<code>/draft r/ClaudeAI | Post title here | Optional body</code>"
            )
        except Exception:
            pass

    return results


def main():
    parser = argparse.ArgumentParser(description="Scout Reddit posts to comment on for karma")
    parser.add_argument("--dry-run", action="store_true", help="Print results without saving/sending")
    parser.add_argument("--max", type=int, default=5, help="Max comments to generate (default 5)")
    args = parser.parse_args()

    karma_scout(max_results=args.max, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
