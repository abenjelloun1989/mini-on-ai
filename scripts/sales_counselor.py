#!/usr/bin/env python3
"""
sales_counselor.py
Sales counselor: reads Gumroad sales data + Reddit activity and delivers
a 4-section strategic report via Telegram.

Usage:
  python3 scripts/sales_counselor.py           # use cache if fresh
  python3 scripts/sales_counselor.py --refresh # force fresh fetch
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import anthropic
from lib.utils import read_json, write_json, log, log_token_usage, extract_json, timestamp, ROOT

CACHE_PATH = "data/counselor-cache.json"
CACHE_TTL_HOURS = 2
REDDIT_USER = "Upbeat-Rate3345"
REDDIT_USER_AGENT = "script:mini-on-ai-sales-counselor:v1.0 (by /u/minionai)"
GUMROAD_API = "https://api.gumroad.com/v2"
SONNET_MODEL = "claude-sonnet-4-6"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID", "")
SITE_URL = os.getenv("SITE_URL", "https://mini-on-ai.com")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gumroad_token() -> str:
    t = os.getenv("GUMROAD_API_TOKEN", "")
    if not t:
        raise RuntimeError("GUMROAD_API_TOKEN not set")
    return t


def _telegram_send(text: str) -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def _reddit_get(path: str, limit: int = 25) -> list:
    params = urllib.parse.urlencode({"limit": limit})
    url = f"https://api.reddit.com{path}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": REDDIT_USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    children = data.get("data", {}).get("children", [])
    return [c["data"] for c in children]


# ── Data fetching ─────────────────────────────────────────────────────────────

def fetch_gumroad_products() -> list:
    """GET /v2/products — returns id, name, price_cents, sales_count, short_url."""
    import requests
    resp = requests.get(
        f"{GUMROAD_API}/products",
        headers={"Authorization": f"Bearer {_gumroad_token()}"},
        timeout=15,
    )
    resp.raise_for_status()
    products = resp.json().get("products", [])
    result = []
    for p in products:
        if p.get("deleted") or not p.get("published"):
            continue
        result.append({
            "id": p.get("id", ""),
            "name": p.get("name", ""),
            "price_cents": p.get("price", 0),
            "sales_count": p.get("sales_count", 0),
            "sales_usd_cents": p.get("sales_usd_cents", 0),
            "short_url": p.get("short_url", ""),
            "url": p.get("url", ""),
        })
    return result


def fetch_gumroad_sales_30d() -> list:
    """Paginate /v2/sales until older than 30 days. Only paid=True."""
    import requests
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    sales = []
    page_key = None

    while True:
        params = {"page_key": page_key} if page_key else {}
        resp = requests.get(
            f"{GUMROAD_API}/sales",
            headers={"Authorization": f"Bearer {_gumroad_token()}"},
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("sales", [])
        if not batch:
            break

        for sale in batch:
            created_str = sale.get("created_at", "")
            try:
                created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            except Exception:
                continue
            if created < cutoff:
                return sales  # older than 30d, stop
            if sale.get("paid"):
                sales.append({
                    "product_name": sale.get("product_name", ""),
                    "product_id": sale.get("product_id", ""),
                    "created_at": created_str,
                    "price": sale.get("price", 0),
                    "referrer": sale.get("referrer", ""),
                    "country": sale.get("country", ""),
                })

        page_key = data.get("next_page_key")
        if not page_key:
            break
        time.sleep(0.3)

    return sales


def fetch_reddit_posts(limit: int = 25) -> list:
    """Fetch user's submitted posts."""
    try:
        items = _reddit_get(f"/user/{REDDIT_USER}/submitted.json", limit=limit)
        return [
            {
                "title": p.get("title", ""),
                "subreddit": p.get("subreddit", ""),
                "score": p.get("score", 0),
                "num_comments": p.get("num_comments", 0),
                "created_utc": p.get("created_utc", 0),
                "permalink": f"https://reddit.com{p.get('permalink', '')}",
            }
            for p in items
        ]
    except Exception as e:
        log("counselor", f"Reddit posts fetch failed: {e}")
        return []


def fetch_reddit_comments(limit: int = 25) -> list:
    """Fetch user's recent comments."""
    try:
        items = _reddit_get(f"/user/{REDDIT_USER}/comments.json", limit=limit)
        return [
            {
                "subreddit": c.get("subreddit", ""),
                "score": c.get("score", 0),
                "body": (c.get("body", "") or "")[:120],
                "link_title": c.get("link_title", ""),
                "created_utc": c.get("created_utc", 0),
            }
            for c in items
        ]
    except Exception as e:
        log("counselor", f"Reddit comments fetch failed: {e}")
        return []


# ── Cross-reference ───────────────────────────────────────────────────────────

def _permalink_slug(url: str) -> str:
    """Extract the Gumroad permalink slug from a URL like .../l/kbwfrq → kbwfrq."""
    if not url:
        return ""
    parts = url.rstrip("/").split("/")
    return parts[-1] if parts else ""


def cross_reference(catalog: list, gumroad_products: list, sales_30d: list, reddit_posts: list) -> list:
    """Merge catalog, Gumroad, 30d sales, and Reddit posts per product."""
    # Build lookup: slug → gumroad product
    gum_by_slug = {_permalink_slug(p["short_url"]): p for p in gumroad_products if p.get("short_url")}
    # Also index by id
    gum_by_id = {p["id"]: p for p in gumroad_products}

    # Count 30d sales per product_id
    sales_count_30d: dict = {}
    sales_rev_30d: dict = {}
    for s in sales_30d:
        pid = s["product_id"]
        sales_count_30d[pid] = sales_count_30d.get(pid, 0) + 1
        sales_rev_30d[pid] = sales_rev_30d.get(pid, 0) + s.get("price", 0)

    merged = []
    matched_gum_slugs = set()

    for product in catalog:
        gum_url = product.get("gumroad_url", "")
        slug = _permalink_slug(gum_url)
        gum = gum_by_slug.get(slug) or {}
        if slug:
            matched_gum_slugs.add(slug)

        gum_id = gum.get("id", "")
        # Fuzzy title match against reddit posts
        keywords = [w.lower() for w in product.get("title", "").split() if len(w) > 3]
        matching_posts = [
            p for p in reddit_posts
            if any(kw in p["title"].lower() for kw in keywords)
        ]

        merged.append({
            "catalog_id": product.get("id", ""),
            "catalog_title": product.get("title", ""),
            "category": product.get("category", ""),
            "gumroad_id": gum_id,
            "price_cents": gum.get("price_cents") if gum else product.get("price"),
            "sales_count": gum.get("sales_count", 0),
            "sales_usd_cents": gum.get("sales_usd_cents", 0),
            "sales_30d_count": sales_count_30d.get(gum_id, 0),
            "sales_30d_revenue": sales_rev_30d.get(gum_id, 0),
            "vitrine_url": f"{SITE_URL}/products/{product.get('id', '')}.html",
            "reddit_posts": matching_posts,
            "has_gumroad": bool(gum_url),
        })

    # Add Gumroad-only products not in catalog
    for slug, gum in gum_by_slug.items():
        if slug not in matched_gum_slugs:
            gum_id = gum.get("id", "")
            merged.append({
                "catalog_id": "",
                "catalog_title": gum.get("name", ""),
                "category": "(Gumroad-only)",
                "gumroad_id": gum_id,
                "price_cents": gum.get("price_cents", 0),
                "sales_count": gum.get("sales_count", 0),
                "sales_usd_cents": gum.get("sales_usd_cents", 0),
                "sales_30d_count": sales_count_30d.get(gum_id, 0),
                "sales_30d_revenue": sales_rev_30d.get(gum_id, 0),
                "vitrine_url": "",
                "reddit_posts": [],
                "has_gumroad": True,
            })

    # Sort by sales_count desc
    merged.sort(key=lambda x: x["sales_count"], reverse=True)
    return merged


# ── Claude analysis ───────────────────────────────────────────────────────────

def build_claude_prompt(merged: list, reddit_posts_all: list, reddit_comments_all: list, sales_30d: list) -> str:
    lines = []

    lines.append("## Products (Gumroad + Catalog)")
    all_free = all((p.get("price_cents") or 0) == 0 for p in merged)
    if all_free:
        lines.append("NOTE: All products are currently $0 (free). Pricing suggestions should focus on identifying which products have enough downloads to justify introducing a paid tier.")
    for p in merged[:40]:  # cap at 40 to stay under token limit
        price = p.get("price_cents") or 0
        price_str = "free" if price == 0 else f"${price / 100:.0f}"
        rev_30d = (p.get("sales_30d_revenue") or 0) / 100
        lines.append(
            f"- {p['catalog_title']} | {price_str} | {p['sales_count']} total sales"
            f" | {p['sales_30d_count']} sales (30d) | ${rev_30d:.2f} revenue (30d)"
            f" | category: {p['category']}"
        )

    lines.append("\n## Recent Sales (last 30 days)")
    if sales_30d:
        for s in sales_30d[:20]:
            lines.append(f"- {s['product_name']} | {s['created_at'][:10]} | referrer: {s.get('referrer') or 'direct'}")
    else:
        lines.append("No paid sales in the last 30 days (all downloads are free).")

    lines.append("\n## Reddit Posts (submitted by u/Upbeat-Rate3345)")
    if reddit_posts_all:
        for p in reddit_posts_all[:25]:
            lines.append(f"- r/{p['subreddit']} | score={p['score']} | {p['num_comments']} comments | {p['title']}")
    else:
        lines.append("No Reddit posts found (account may be new or data unavailable).")

    lines.append("\n## Reddit Comments (recent)")
    if reddit_comments_all:
        for c in reddit_comments_all[:25]:
            lines.append(f"- r/{c['subreddit']} | score={c['score']} | {c['body'][:80]}")
    else:
        lines.append("No Reddit comments found.")

    lines.append("\n## Product-Post Cross-Reference")
    for p in merged:
        if p["reddit_posts"]:
            subs = ", ".join(f"r/{rp['subreddit']}" for rp in p["reddit_posts"])
            lines.append(f"- {p['catalog_title']}: related posts in {subs}")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are a sales counselor for a solo creator who sells digital products (prompt packs, n8n automation templates, Claude Code skills) on Gumroad and promotes them on Reddit.

Your job: analyze the product performance data and Reddit activity below, then return a structured JSON report with exactly 4 keys.

OUTPUT FORMAT — return only valid JSON, no markdown fences, no extra text:
{
  "whats_working": ["bullet 1", "bullet 2"],
  "what_to_fix": ["bullet 1", "bullet 2"],
  "next_reddit_posts": [
    {"subreddit": "SideProject", "angle": "...", "product": "...", "why": "..."}
  ],
  "pricing_suggestions": [
    {"product": "...", "current_price": "$0", "suggested_price": "$5", "reason": "..."}
  ]
}

Rules:
- whats_working: 2-4 bullets. Focus on what actually got traction (downloads, upvotes, comments). If nothing has traction yet, say that honestly.
- what_to_fix: 2-4 bullets. Be direct. Name specific products or posts that underperformed. Suggest concrete fixes.
- next_reddit_posts: 3-5 suggestions. Each must name a specific subreddit and a concrete angle — lead with the PROBLEM the reader faces, not with the product. Connect to a specific product only when the fit is natural. Post-friendly subreddits: SideProject, indiehackers, buildinpublic, nocode, SaaS, somethingimade, shamelessplug, ChatGPTCoding, ChatGPT, Entrepreneur.
- pricing_suggestions: 1-4 suggestions. If all products are free, identify which have enough downloads to justify a paid tier ($5-$9). If no pricing changes are needed, return 1 item explaining why.
- If Reddit activity is sparse, say so explicitly — do not speculate about patterns from minimal data.
- Each bullet must be under 120 characters. No em-dashes. Be direct and actionable."""


def call_claude_sonnet(prompt: str) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    response = client.messages.create(
        model=SONNET_MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    log_token_usage("counselor", response.usage, SONNET_MODEL)
    raw = response.content[0].text.strip()
    try:
        return extract_json(raw, array=False)
    except Exception:
        # Try raw parse
        try:
            return json.loads(raw)
        except Exception as e:
            raise ValueError(f"Could not parse Claude response as JSON: {e}\n\nRaw: {raw[:500]}")


# ── Rendering ─────────────────────────────────────────────────────────────────

def render_section(title: str, emoji: str, items) -> str:
    """Render one section as Telegram HTML."""
    header = f"{emoji} <b>{title}</b>\n\n"
    if isinstance(items, list) and items and isinstance(items[0], dict):
        # Structured items (next_reddit_posts, pricing_suggestions)
        parts = []
        for i, item in enumerate(items, 1):
            if "subreddit" in item:
                parts.append(
                    f"{i}. r/{item['subreddit']}\n"
                    f"   Angle: {item.get('angle', '')}\n"
                    f"   Product: {item.get('product', 'any')}\n"
                    f"   Why: {item.get('why', '')}"
                )
            elif "suggested_price" in item:
                parts.append(
                    f"{i}. {item.get('product', '')}\n"
                    f"   Now: {item.get('current_price', '?')} → Suggest: {item.get('suggested_price', '?')}\n"
                    f"   {item.get('reason', '')}"
                )
            else:
                parts.append(f"{i}. {str(item)}")
        body = "\n\n".join(parts)
    else:
        # Simple bullet list
        lines = [f"{i}. {item}" for i, item in enumerate(items, 1)]
        body = "\n".join(lines)

    full = header + body
    if len(full) > 3900:
        full = full[:3897] + "…"
    return full


def send_counsel_report(sections: dict, cache_age_minutes: int = None) -> None:
    """Send 4 Telegram messages, one per section."""
    prefix = ""
    if cache_age_minutes is not None:
        prefix = f"📊 <i>(cached {cache_age_minutes}m ago — /counsel refresh to update)</i>\n\n"

    messages = [
        (prefix + render_section("What's Working", "🏆", sections.get("whats_working", []))),
        render_section("What to Fix", "⚠️", sections.get("what_to_fix", [])),
        render_section("Next Reddit Posts", "📣", sections.get("next_reddit_posts", [])),
        render_section("Pricing Suggestions", "💰", sections.get("pricing_suggestions", [])),
    ]

    for msg in messages:
        _telegram_send(msg)
        time.sleep(0.5)


# ── Cache ─────────────────────────────────────────────────────────────────────

def load_cache() -> "dict | None":
    cache_path = ROOT / CACHE_PATH
    if not cache_path.exists():
        return None
    try:
        data = json.loads(cache_path.read_text())
        fetched_at_str = data.get("fetched_at", "")
        fetched_at = datetime.fromisoformat(fetched_at_str.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - fetched_at
        if age.total_seconds() < CACHE_TTL_HOURS * 3600:
            data["_age_minutes"] = int(age.total_seconds() / 60)
            return data
    except Exception:
        pass
    return None


def save_cache(sections: dict, summary: dict) -> None:
    write_json(CACHE_PATH, {
        "fetched_at": timestamp(),
        "sections": sections,
        "summary": summary,
    })


# ── Main ──────────────────────────────────────────────────────────────────────

def run_counselor(force_refresh: bool = False) -> None:
    stage = "init"
    try:
        # Check cache
        if not force_refresh:
            cached = load_cache()
            if cached:
                age_min = cached.get("_age_minutes", 0)
                log("counselor", f"Using cached report ({age_min}m old)")
                send_counsel_report(cached["sections"], cache_age_minutes=age_min)
                return

        # Fetch data
        stage = "gumroad-products"
        log("counselor", "Fetching Gumroad products…")
        gumroad_products = fetch_gumroad_products()
        log("counselor", f"Got {len(gumroad_products)} Gumroad products")

        stage = "gumroad-sales"
        log("counselor", "Fetching Gumroad 30d sales…")
        sales_30d = fetch_gumroad_sales_30d()
        log("counselor", f"Got {len(sales_30d)} paid sales in last 30 days")

        stage = "reddit-posts"
        log("counselor", "Fetching Reddit posts…")
        reddit_posts = fetch_reddit_posts()
        log("counselor", f"Got {len(reddit_posts)} Reddit posts")

        stage = "reddit-comments"
        log("counselor", "Fetching Reddit comments…")
        reddit_comments = fetch_reddit_comments()
        log("counselor", f"Got {len(reddit_comments)} Reddit comments")

        stage = "catalog"
        catalog_data = read_json("data/product-catalog.json")
        catalog = catalog_data.get("products", [])

        stage = "cross-reference"
        merged = cross_reference(catalog, gumroad_products, sales_30d, reddit_posts)
        log("counselor", f"Cross-referenced {len(merged)} products")

        stage = "claude-analysis"
        log("counselor", "Sending to Claude Sonnet for analysis…")
        prompt = build_claude_prompt(merged, reddit_posts, reddit_comments, sales_30d)
        sections = call_claude_sonnet(prompt)

        stage = "send"
        send_counsel_report(sections)

        stage = "cache"
        save_cache(sections, {
            "products_count": len(merged),
            "gumroad_products_count": len(gumroad_products),
            "sales_30d_count": len(sales_30d),
            "reddit_posts_count": len(reddit_posts),
            "reddit_comments_count": len(reddit_comments),
        })
        log("counselor", "Done.")

    except Exception as e:
        log("counselor", f"Error at stage {stage}: {e}")
        try:
            _telegram_send(f"❌ <b>Sales counselor failed</b> at stage <code>{stage}</code>:\n{e}")
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Sales counselor — Gumroad + Reddit analysis")
    parser.add_argument("--refresh", action="store_true", help="Force fresh data fetch")
    args = parser.parse_args()
    run_counselor(force_refresh=args.refresh)


if __name__ == "__main__":
    main()
