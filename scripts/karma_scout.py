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


def generate_reddit_post(subreddit: str) -> str:
    """
    Generate a copy-paste Reddit post (title + body) to advertise the matching
    product on the given subreddit. Returns a formatted string or an error message.
    """
    sub = subreddit[2:] if subreddit.startswith("r/") else subreddit

    hint = SUBREDDIT_TO_PRODUCT.get(sub)
    if not hint:
        return f"No product mapped to r/{sub}. Check /post list for available subreddits."

    product_name, product_url = hint

    # Find the best matching product in the catalog
    catalog = read_json("data/product-catalog.json")
    product = None
    search_words = set(product_name.lower().split())
    best_score = 0
    for p in catalog.get("products", []):
        title_words = set(p.get("title", "").lower().split())
        score = len(search_words & title_words)
        if score > best_score:
            best_score = score
            product = p

    if not product:
        return f"Could not find product details for '{product_name}' in catalog."

    title = product.get("title", product_name)
    description = product.get("description", "")
    price = product.get("price", 0)
    gumroad_url = product.get("gumroad_url") or product_url
    is_free = product.get("is_free") or price == 0
    price_label = "free" if is_free else (f"${price // 100}" if price else "$5")

    prompt = f"""Write a short Reddit post promoting this product. Write in first person, like someone who personally hit this problem, solved it, and is sharing what worked — not a marketer.

Product: {title}
What it is: {description}
Price: {price_label}
Link: {gumroad_url}
Subreddit: r/{sub}

Style:
- First person throughout ("I", "my", "me") — you BUILT this product, so say "I built" not "I found" or "someone built"
- Short: title under 10 words, body under 120 words (3 short paragraphs max)
- First paragraph = the specific pain you felt, in plain language
- Second paragraph = what actually worked / what changed
- Last line = mention the product casually with the link, no hype
- Tone: direct, slightly tired of bad advice, genuinely useful

Hard rules:
- No em-dashes
- No bullet lists
- No "I'm excited", "hope this helps", "game-changer", "curated", "comprehensive"
- No "As someone who"
- The insight is the point, not the product
- IMPORTANT: the price is {price_label} — never say "free" or "no signup required" if it has a price

Respond ONLY with valid JSON: {{"title": "...", "body": "..."}}"""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        data = json.loads(raw)
        post_title = data.get("title", "")
        post_body = data.get("body", "")
        return (
            f"📣 r/{sub} — {product_name} ({price_label})\n\n"
            f"<b>Title</b> (tap to copy):\n<code>{post_title}</code>\n\n"
            f"<b>Body</b> (tap to copy):\n<code>{post_body}</code>"
        )
    except Exception as e:
        log("karma-scout", f"Warning: post generation failed: {e}")
        return f"Could not generate post: {e}"


def fix_reddit_post(subreddit: str, rule: str, title: str = "", body: str = "") -> str:
    """
    Revise or regenerate a Reddit post to comply with a specific rule.
    If title/body provided: revises that post.
    If not: regenerates from scratch with the rule as a constraint.
    """
    sub = subreddit[2:] if subreddit.startswith("r/") else subreddit

    hint = SUBREDDIT_TO_PRODUCT.get(sub)
    if not hint:
        return f"No product mapped to r/{sub}. Check /post list for available subreddits."

    product_name, product_url = hint

    # Find product in catalog
    catalog = read_json("data/product-catalog.json")
    product = None
    search_words = set(product_name.lower().split())
    best_score = 0
    for p in catalog.get("products", []):
        title_words = set(p.get("title", "").lower().split())
        score = len(search_words & title_words)
        if score > best_score:
            best_score = score
            product = p

    if not product:
        return f"Could not find product details for '{product_name}' in catalog."

    prod_title = product.get("title", product_name)
    description = product.get("description", "")
    price = product.get("price", 0)
    gumroad_url = product.get("gumroad_url") or product_url
    is_free = product.get("is_free") or price == 0
    price_label = "free" if is_free else (f"${price // 100}" if price else "$5")

    if title and body:
        task = f"""Revise this Reddit post so it complies with the rule below. Keep the core message intact — only change what's needed.

Original post:
TITLE: {title}
BODY: {body}

Rule violation to fix: {rule}

Keep it first-person throughout. Under 120 words. No em-dashes, no bullet lists."""
    else:
        task = f"""Write a Reddit post for r/{sub} that complies with this rule: {rule}

Write in first person, like someone who personally hit this problem and solved it.
Product: {prod_title}
What it is: {description}
Price: {price_label}
Link: {gumroad_url}

First paragraph = the specific pain you felt. Second = what worked. Last line = mention the product casually with the link.
Under 120 words. No em-dashes, no bullet lists, no "I'm excited", no "someone built"."""

    prompt = f"""{task}

Respond ONLY with valid JSON: {{"title": "...", "body": "...", "change_summary": "what was changed and why it now complies"}}"""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        data = json.loads(raw)
        post_title = data.get("title", "")
        post_body = data.get("body", "")
        summary = data.get("change_summary", "")
        return (
            f"🔧 r/{sub} — fixed for: {rule}\n\n"
            f"<b>Title</b> (tap to copy):\n<code>{post_title}</code>\n\n"
            f"<b>Body</b> (tap to copy):\n<code>{post_body}</code>\n\n"
            f"ℹ️ {summary}"
        )
    except Exception as e:
        log("karma-scout", f"Warning: post fix failed: {e}")
        return f"Could not fix post: {e}"


def _reddit_new(subreddit: str, limit: int = 25) -> list:
    """Fetch newest posts from a subreddit via api.reddit.com (no auth required)."""
    params = urllib.parse.urlencode({"limit": limit})
    url = f"https://api.reddit.com/r/{subreddit}/new?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": REDDIT_USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        children = json.loads(resp.read().decode("utf-8")).get("data", {}).get("children", [])
    return [c["data"] for c in children if c.get("kind") == "t3"]

KARMA_SUBREDDITS = [
    # Audience = your buyers, comment mentions tolerated
    "ClaudeAI",
    "cursor",
    "ChatGPTCoding",
    # n8n bans Gumroad links but "DM me for the template" works in comments
    "n8n",
    # These have weekly promo threads — karma needed to participate
    "Entrepreneur",
    "passive_income",
]

_SITE = "https://mini-on-ai.com"
_ATS_URL = f"{_SITE}/products/prompts-ats-optimized-resume-bullet-rewriter-by--2.html"

# VERIFIED post-friendly subreddits (rules checked 2026-03-26):
#
# ✅ SideProject    — 503K members, paid products explicitly OK, "I built" framing
# ✅ indiehackers   — 115K members, paid products OK, milestone/founder posts
# ✅ buildinpublic  — 27K members, transparent founder updates, paid products OK
# ✅ nocode         — paid products OK, value-first post + disclose affiliation
# ✅ SaaS           — weekly feedback thread, tolerant of product posts
# ✅ somethingimade — 2M+ members, paid products allowed
# ✅ shamelessplug  — 52K members, explicitly for self-promo (low engagement but zero friction)
#
# ❌ KARMA-ONLY — see KARMA_SUBREDDITS above
SUBREDDIT_TO_PRODUCT = {
    # Claude Code Skills — developer/founder audience
    "SideProject":   ("Claude Code Skills Packs", _SITE),
    "indiehackers":  ("Claude Code Skills Packs", _SITE),
    "buildinpublic": ("Claude Code Skills Packs", _SITE),
    "ChatGPTCoding": ("Claude Code Skills Packs", _SITE),
    # ATS Resume Rewriter — maker/general audience
    "somethingimade": ("ATS Resume Bullet Rewriter", _ATS_URL),
    "shamelessplug":  ("ATS Resume Bullet Rewriter", _ATS_URL),
    # n8n / automation — nocode is the only verified-safe automation sub
    "nocode":        ("n8n Workflow Templates", _SITE),
    "SaaS":          ("n8n Workflow Templates", _SITE),
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


def karma_scout(max_results: int = 5, dry_run: bool = False, subreddit: str = "") -> list:
    """
    Scan subreddits, assess posts, draft comments, send to Telegram.
    subreddit: if set, scan only that one subreddit (lower score threshold: 55).
    Returns list of (post, assessment) tuples for results sent.
    """
    # Load already-seen post IDs from karma queue
    queue = read_json("data/karma-queue.json")
    seen_ids = {p["post_id"] for p in queue.get("posts", [])}

    # Targeted mode: single subreddit, fetch more posts, lower threshold
    if subreddit:
        subs_to_scan = [subreddit[2:] if subreddit.startswith("r/") else subreddit]
        fetch_limit = 50
        score_threshold = 55
    else:
        subs_to_scan = KARMA_SUBREDDITS
        fetch_limit = 25
        score_threshold = 65

    candidates = []
    seen_in_run = set()

    for sub in subs_to_scan:
        if len(candidates) >= max_results * 6:
            break
        try:
            posts = _reddit_new(sub, limit=fetch_limit)
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
    scope = f"r/{subs_to_scan[0]}" if subreddit else f"{len(subs_to_scan)} subreddits"
    log("karma-scout", f"Collected {len(candidates)} unique candidates from {scope}")

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

        if score < score_threshold or not comment:
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
    parser.add_argument("--subreddit", default="", help="Target a single subreddit (e.g. resumes)")
    args = parser.parse_args()

    karma_scout(max_results=args.max, dry_run=args.dry_run, subreddit=args.subreddit)


if __name__ == "__main__":
    main()
