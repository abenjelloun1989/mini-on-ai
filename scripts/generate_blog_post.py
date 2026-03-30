#!/usr/bin/env python3
"""
generate_blog_post.py — Generate and publish an SEO blog post.

Usage:
  python3 scripts/generate_blog_post.py --topic "claude code prompts for api testing"
  python3 scripts/generate_blog_post.py --auto        # picks topic from catalog tags
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import anthropic
from lib.utils import read_json, log, log_token_usage, ROOT

MODEL = "claude-haiku-4-5"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

BLOG_POSTS_PATH = "data/blog-posts.json"
SITE_URL = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")


def _slug(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:55]


def _ensure_blog_posts_file() -> dict:
    path = ROOT / BLOG_POSTS_PATH
    if not path.exists():
        data = {"posts": []}
        path.write_text(json.dumps(data, indent=2) + "\n")
        return data
    with open(path) as f:
        return json.load(f)


def _pick_topic_auto(catalog: dict) -> str:
    """Pick the most popular unwritten tag from the product catalog."""
    blog_data = _ensure_blog_posts_file()
    used_topics = {p.get("topic", "").lower() for p in blog_data.get("posts", [])}

    tag_counts: dict = {}
    for p in catalog.get("products", []):
        for t in (p.get("tags") or []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    # Sort by frequency descending, skip already-used topics and short tags
    for tag, _ in sorted(tag_counts.items(), key=lambda x: -x[1]):
        if len(tag) > 4 and tag.lower() not in used_topics:
            return tag

    return "claude code automation prompts"


def _relevant_products(topic: str, catalog: dict, n: int = 3) -> list:
    """Return up to n products most relevant to the topic (Gumroad-linked only)."""
    topic_words = set(re.sub(r"[^a-z0-9 ]", " ", topic.lower()).split())
    scored = []
    for p in catalog.get("products", []):
        if not p.get("gumroad_url"):
            continue
        text = (p.get("title", "") + " " + " ".join(p.get("tags") or [])).lower()
        score = sum(1 for w in topic_words if w in text)
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:n]]


def generate_blog_post(topic: str, catalog: dict) -> dict:
    """Call Claude Haiku to produce a blog post, return post metadata dict."""
    relevant = _relevant_products(topic, catalog)

    product_refs = ""
    if relevant:
        product_refs = "\n\nNaturally link to 2-3 of these products (use exact URLs, embed them in the prose — do NOT add a separate 'Products' section):\n"
        for p in relevant:
            product_refs += f'- [{p["title"]}]({SITE_URL}/products/{p["id"]}.html)\n'

    prompt = f"""Write an SEO-optimized blog post targeting the keyword phrase: "{topic}"

Requirements:
- 700–900 words total
- Structure: short intro (1-2 sentences), 3-4 ## sections with actionable content, brief conclusion
- Tone: practical and direct — written for developers, freelancers, and automation builders
- Include the target keyword naturally in the first paragraph, one H2, and conclusion
- No keyword stuffing, no fluff sentences, no "In conclusion, ..." openers{product_refs}

Return ONLY valid JSON — no markdown fences, no explanation — using this exact schema:
{{
  "title": "...",
  "excerpt": "One sentence, 100–130 chars, summarising the post value",
  "body_markdown": "full markdown body of the post"
}}"""

    msg = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    log_token_usage("generate-blog-post", msg.usage, MODEL)

    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    data = json.loads(raw)
    date_str = datetime.now().strftime("%Y%m%d")
    slug = _slug(data.get("title", topic))
    post_id = f"blog-{slug}-{date_str}"

    return {
        "id":            post_id,
        "title":         data["title"],
        "slug":          f"{slug}-{date_str}",
        "excerpt":       data["excerpt"],
        "body_markdown": data["body_markdown"],
        "topic":         topic,
        "created_at":    datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate an SEO blog post")
    parser.add_argument("--topic", type=str, default="", help="Keyword/topic to target")
    parser.add_argument("--auto",  action="store_true", help="Auto-pick topic from catalog tags")
    args = parser.parse_args()

    catalog = read_json("data/product-catalog.json")

    if args.auto or not args.topic:
        topic = _pick_topic_auto(catalog)
        log("generate-blog", f"Auto-selected topic: {topic}")
    else:
        topic = args.topic

    log("generate-blog", f"Generating post on: {topic}")
    post = generate_blog_post(topic, catalog)
    log("generate-blog", f"Generated: {post['title']}")

    from update_site import update_blog
    url = update_blog(post)
    log("generate-blog", f"Published: {url}")
    print(url)


if __name__ == "__main__":
    main()
