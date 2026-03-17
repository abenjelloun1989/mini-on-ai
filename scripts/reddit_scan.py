#!/usr/bin/env python3
"""
reddit_scan.py
Scans target subreddits for posts expressing a specific need, then uses Claude Haiku
to assess each post and propose a tailored product brief.

Usage:
  python3 scripts/reddit_scan.py              # scan + assess, append to reddit-queue.json
  python3 scripts/reddit_scan.py --dry-run    # print candidates without saving/sending

Uses pullpush.io — a free, public Reddit archive API. No account or API key required.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import anthropic
from lib.utils import read_json, write_json, timestamp, log, ROOT

# Reddit public JSON API — no auth required, just a descriptive User-Agent
REDDIT_SEARCH_BASE = "https://www.reddit.com/r/{subreddit}/search.json"
REDDIT_USER_AGENT = "mini-on-ai-scanner/1.0 (contact: scanner@mini-on-ai.com)"

# ---------------------------------------------------------------------------
# Categories the existing pipeline can build today
# ---------------------------------------------------------------------------
BUILDABLE_CATEGORIES = {
    "prompt-packs", "checklist", "swipe-file", "mini-guide",
    "n8n-template", "claude-code-skill",
}

def _reddit_search(subreddit: str, keyword: str, size: int = 25) -> list:
    """Search Reddit for posts matching a keyword in a single subreddit (last week)."""
    params = urllib.parse.urlencode({
        "q": keyword,
        "restrict_sr": 1,
        "sort": "new",
        "t": "week",
        "limit": size,
    })
    url = REDDIT_SEARCH_BASE.format(subreddit=subreddit) + f"?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": REDDIT_USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        children = json.loads(resp.read().decode("utf-8")).get("data", {}).get("children", [])
    return [c["data"] for c in children if c.get("kind") == "t3"]


DEFAULT_SUBREDDITS = (
    "n8n,automation,nocode,zapier,MakeNoCode,"
    "freelance,Entrepreneur,smallbusiness,"
    "productivity,ADHD,selfimprovement,LifeProTips,"
    "writing,blogging,freelanceWriters,"
    "learnprogramming,webdev,SideProject"
)


def reddit_scan(subreddits: list, limit: int = 100, max_age_days: int = 14) -> list:
    """
    Scan subreddits for posts expressing a need via pullpush.io.
    Runs multiple keyword searches per subreddit, deduplicates, and returns matches.
    Only returns posts from the last max_age_days days.
    """
    after = int(time.time()) - max_age_days * 86400

    # Load already-seen post IDs
    queue = read_json("data/reddit-queue.json")
    seen_ids = {p["post_id"] for p in queue.get("posts", [])}

    # Short title keywords that signal a need (1-2 words work best with pullpush)
    SEARCH_KEYWORDS = [
        "anyone have",
        "looking for template",
        "looking for prompts",
        "need prompt",
        "does anyone have",
        "is there template",
        "struggling with",
        "how do I write",
        "how do I create",
        "can someone help",
        "recommend a tool",
        "any good prompts",
    ]

    seen_in_run = set()
    candidates = []

    for sub in subreddits:
        if len(candidates) >= limit:
            break
        for keyword in SEARCH_KEYWORDS:
            if len(candidates) >= limit:
                break
            try:
                posts = _reddit_search(sub, keyword, size=25)
            except Exception as e:
                log("reddit-scan", f"Warning: Reddit search failed r/{sub} '{keyword}': {e}")
                time.sleep(2)
                continue

            for post in posts:
                post_id = post.get("id", "")
                if not post_id or post_id in seen_ids or post_id in seen_in_run:
                    continue
                # Skip posts older than max_age_days
                if post.get("created_utc", 0) < after:
                    continue
                seen_in_run.add(post_id)

                title = post.get("title", "")
                body = (post.get("selftext") or "")
                if body in ("[removed]", "[deleted]", ""):
                    body = ""

                candidates.append({
                    "post_id": post_id,
                    "subreddit": post.get("subreddit", sub),
                    "title": title,
                    "body": body[:800].strip(),
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "author": post.get("author", "[deleted]"),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "created_utc": post.get("created_utc", 0),
                })

            time.sleep(0.5)  # polite delay between API calls

    log("reddit-scan", f"Found {len(candidates)} unique candidate posts (last {max_age_days}d) across {len(subreddits)} subreddits")
    return candidates


def assess_post(post: dict) -> Optional[dict]:
    """
    Use Claude Haiku to evaluate a post and propose a product brief.
    Returns a dict with score, title, category, description, tags,
    buildable flag, and (if not buildable) why_not_buildable.
    Returns None if the API call fails.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    text_excerpt = f"Title: {post['title']}\n\nBody: {post['body'][:400]}"

    prompt = f"""You are a product curator for a digital product shop (prompt packs, checklists, swipe files, mini guides, Claude Code skill packs, n8n workflow templates).

A Reddit user posted this in r/{post['subreddit']}:

{text_excerpt}

Evaluate whether this post expresses a clear need that could be solved with one of our product types.

Respond ONLY with valid JSON (no markdown, no prose):
{{
  "score": <0-100 integer — how well this need maps to a buildable digital product>,
  "title": "<proposed product title, 4-8 words>",
  "category": "<one of: prompt-packs | checklist | swipe-file | mini-guide | n8n-template | claude-code-skill | OTHER>",
  "description": "<one sentence describing what the product does and who it helps>",
  "tags": ["<tag1>", "<tag2>", "<tag3>"],
  "why_not_buildable": "<only if category is OTHER: explain what type of product is needed>"
}}

Score guide:
- 80-100: Clear, specific need perfectly matched by a product type
- 60-79: Good fit but somewhat vague or broad
- 40-59: Possible but weak signal
- 0-39: Not a good fit"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        brief = json.loads(raw)
        brief["buildable"] = brief.get("category") in BUILDABLE_CATEGORIES
        return brief
    except Exception as e:
        log("reddit-scan", f"Warning: assess_post failed for {post['post_id']}: {e}")
        return None


def _gen_build_prompt(post: dict, brief: dict) -> str:
    """Generate a copy-paste Claude Code prompt to add a new pipeline capability."""
    category = brief.get("category", "unknown")
    description = brief.get("description", "")
    why = brief.get("why_not_buildable", "")
    return (
        f"Add a new product category '{category}' to the mini-on-factory pipeline.\n\n"
        f"This was requested by a Reddit user in r/{post['subreddit']}:\n"
        f"Post: {post['url']}\n\n"
        f"The product needed: {description}\n"
        f"Why it's not currently buildable: {why}\n\n"
        f"Implement _gen_{category.replace('-', '_')}() in scripts/generate_product.py "
        f"following the same pattern as _gen_prompt_pack(). Add the category to "
        f"BUILDABLE_CATEGORIES in scripts/reddit_scan.py once done."
    )


def run_scan(subreddits: list, max_candidates: int = 10, dry_run: bool = False, max_age_days: int = 14) -> list:
    """
    Full scan + assess loop. Returns list of (post, brief) tuples for assessed candidates.
    If dry_run=True, prints results and does not save to queue.
    """
    import random
    posts = reddit_scan(subreddits, limit=100, max_age_days=max_age_days)
    random.shuffle(posts)  # spread candidates across subreddits, not just the first one

    results = []
    for post in posts:
        if len(results) >= max_candidates:
            break

        log("reddit-scan", f"Assessing: {post['title'][:60]}...")
        brief = assess_post(post)
        if not brief:
            continue
        if brief.get("score", 0) < 60:
            log("reddit-scan", f"  Score {brief.get('score', 0)} — skipping")
            continue

        if not brief["buildable"]:
            brief["build_prompt"] = _gen_build_prompt(post, brief)

        if dry_run:
            print(f"\n{'='*60}")
            print(f"r/{post['subreddit']} | Score: {brief['score']} | Buildable: {brief['buildable']}")
            print(f"Post: {post['title']}")
            print(f"URL:  {post['url']}")
            print(f"Proposed: {brief['title']} ({brief['category']})")
            print(f"  {brief['description']}")
            if not brief["buildable"]:
                print(f"  [NOT BUILDABLE] {brief.get('why_not_buildable', '')}")
        else:
            # Save to queue
            queue = read_json("data/reddit-queue.json")
            queue.setdefault("posts", []).append({
                "post_id": post["post_id"],
                "subreddit": post["subreddit"],
                "title": post["title"],
                "body": post["body"],
                "url": post["url"],
                "author": post["author"],
                "found_at": timestamp(),
                "status": "pending",
                "brief": brief,
                "product_id": None,
                "reply_text": None,
                "replied_at": None,
            })
            write_json("data/reddit-queue.json", queue)
            log("reddit-scan", f"  Saved to queue: {brief['title']} (score {brief['score']})")

        results.append((post, brief))
        time.sleep(0.5)  # small delay between Haiku calls

    log("reddit-scan", f"Scan complete — {len(results)} candidates {'printed' if dry_run else 'saved to queue'}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Scan Reddit for product opportunities")
    parser.add_argument("--dry-run", action="store_true", help="Print results without saving")
    parser.add_argument("--subreddits", default="", help="Comma-separated list (overrides .env)")
    parser.add_argument("--max", type=int, default=10, help="Max candidates to keep (default 10)")
    parser.add_argument("--max-age", type=int, default=14, help="Max post age in days (default 14)")
    args = parser.parse_args()

    subs_env = os.getenv("REDDIT_SUBREDDITS", DEFAULT_SUBREDDITS)
    subs_raw = args.subreddits if args.subreddits else subs_env
    subreddits = [s.strip() for s in subs_raw.split(",") if s.strip()]

    log("reddit-scan", f"Subreddits: {', '.join(subreddits)} | max age: {args.max_age}d")
    run_scan(subreddits, max_candidates=args.max, dry_run=args.dry_run, max_age_days=args.max_age)


if __name__ == "__main__":
    main()
