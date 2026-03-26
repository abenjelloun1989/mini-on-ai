#!/usr/bin/env python3
"""
counsel_go.py
Executes actions from the latest /counsel report automatically:
  1. Applies price changes on Gumroad + rebuilds vitrine
  2. Generates Reddit post drafts with the exact counselor angles
  3. Sends a manual checklist for things that can't be automated

Usage:
  python3 scripts/counsel_go.py
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

import anthropic
import requests
from lib.utils import read_json, write_json, log, ROOT

GUMROAD_API = "https://api.gumroad.com/v2"
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID", "")
SITE_URL = os.getenv("SITE_URL", "https://mini-on-ai.com")


def _send(text: str) -> None:
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30):
        pass


def _gumroad_token() -> str:
    t = os.getenv("GUMROAD_API_TOKEN", "")
    if not t:
        raise RuntimeError("GUMROAD_API_TOKEN not set")
    return t


# ── Price updates ─────────────────────────────────────────────────────────────

_gumroad_products_cache = None

def _get_gumroad_products() -> list:
    """Fetch all Gumroad products (cached for this run)."""
    global _gumroad_products_cache
    if _gumroad_products_cache is not None:
        return _gumroad_products_cache
    resp = requests.get(
        f"{GUMROAD_API}/products",
        headers={"Authorization": f"Bearer {_gumroad_token()}"},
        timeout=15,
    )
    resp.raise_for_status()
    _gumroad_products_cache = resp.json().get("products", [])
    return _gumroad_products_cache


def _find_gumroad_id(product_name: str, catalog: list) -> "str | None":
    """Find the real Gumroad API product ID by fuzzy-matching name against catalog,
    then looking up the slug in the live Gumroad products list."""
    name_lower = product_name.lower()
    keywords = [w for w in name_lower.split() if len(w) > 3]

    # Find best catalog match
    best_slug = None
    best_score = 0
    for entry in catalog:
        title_lower = entry.get("title", "").lower()
        gurl = entry.get("gumroad_url", "")
        if not gurl or "/l/" not in gurl:
            continue
        score = sum(1 for kw in keywords if kw in title_lower)
        if score > best_score:
            best_score = score
            best_slug = gurl.rstrip("/").split("/l/")[-1].split("?")[0]

    if best_score < 2 or not best_slug:
        return None

    # Look up real API id from Gumroad products (slug → id)
    gumroad_products = _get_gumroad_products()
    for gp in gumroad_products:
        short_url = gp.get("short_url", "")
        slug = short_url.rstrip("/").split("/")[-1]
        if slug == best_slug:
            return gp.get("id")

    # Fallback: slug might be the id directly for some products
    return best_slug


def apply_price_changes(suggestions: list, catalog: list) -> list:
    """Apply price changes to Gumroad for suggestions where price differs. Returns results."""
    results = []
    for s in suggestions:
        current = s.get("current_price", "")
        suggested = s.get("suggested_price", "")
        if current == suggested:
            results.append({"product": s["product"], "status": "skipped", "reason": "price unchanged"})
            continue

        # Parse suggested price in cents
        try:
            price_cents = int(float(suggested.replace("$", "")) * 100)
        except Exception:
            results.append({"product": s["product"], "status": "skipped", "reason": f"could not parse price: {suggested}"})
            continue

        gumroad_id = _find_gumroad_id(s["product"], catalog)
        if not gumroad_id:
            results.append({
                "product": s["product"], "status": "manual",
                "manual_step": f"Go to gumroad.com/products → find \"{s['product'][:40]}\" → set price to {suggested}",
            })
            continue

        try:
            resp = requests.put(
                f"{GUMROAD_API}/products/{gumroad_id}",
                headers={"Authorization": f"Bearer {_gumroad_token()}"},
                data={"price": price_cents},
                timeout=15,
            )
            if resp.status_code == 200:
                results.append({"product": s["product"], "status": "updated", "price": suggested, "gumroad_id": gumroad_id})
            else:
                results.append({
                    "product": s["product"], "status": "manual",
                    "manual_step": f"API returned {resp.status_code}. Go to gumroad.com/products → find \"{s['product'][:40]}\" → set price to {suggested} manually",
                })
        except Exception as e:
            results.append({
                "product": s["product"], "status": "manual",
                "manual_step": f"API error ({str(e)[:40]}). Go to gumroad.com/products → find \"{s['product'][:40]}\" → set price to {suggested} manually",
            })

    return results


# ── Reddit post generation ────────────────────────────────────────────────────

def generate_post_from_angle(subreddit: str, angle: str, product_name: str) -> "dict | None":
    """Generate a Reddit post using the counselor's specific angle."""
    # Find product in catalog for URL and price
    catalog_data = read_json("data/product-catalog.json")
    catalog = catalog_data.get("products", [])
    keywords = [w for w in product_name.lower().split() if len(w) > 3]
    product = None
    best_score = 0
    for entry in catalog:
        score = sum(1 for kw in keywords if kw in entry.get("title", "").lower())
        if score > best_score:
            best_score = score
            product = entry

    if not product or best_score < 2:
        product_url = SITE_URL
        price_label = ""
    else:
        product_url = f"{SITE_URL}/products/{product['id']}.html"
        price = product.get("price")
        is_free = product.get("is_free") or price == 0
        price_label = "free" if is_free else (f"${price // 100}" if price else "$5")

    subreddit_rules = {
        "ClaudeAI": "Rule 7: Lead with a concrete technique or workflow the reader can apply. Do NOT open with 'I built' or 'I made'. Open with the technique or lesson. The product is a resource at the end.",
        "cursor": "Lead with a workflow or technique. Product is a resource, not the focus.",
        "ChatGPTCoding": "Lead with a specific coding problem. Be technical and concrete. Product mention is secondary.",
        "SideProject": "Share the story — the problem, struggle, and what you learned. Product link at the end.",
        "indiehackers": "Share numbers, process, or lessons learned. Be transparent. Product is secondary.",
        "buildinpublic": "Share what you built and what you learned. Be honest about struggles. No hype.",
    }
    sub_rule = subreddit_rules.get(subreddit, "")
    sub_rule_block = f"\nSubreddit-specific rule:\n{sub_rule}\n" if sub_rule else ""

    prompt = f"""Write a Reddit post for r/{subreddit}.

Angle (use this as the core of your title and first paragraph):
{angle}
{sub_rule_block}

Product to mention (casually, near the end):
{product_name}
Link: {product_url}
Price: {price_label if price_label else "free"}

Style rules:
- First person ("I", "my", "me") throughout — you BUILT this, say "I built" not "I found"
- Title: under 12 words, leads directly with the angle above — no hype, no colons
- Body: 3 short paragraphs, under 120 words total
- First paragraph: the specific pain described in the angle, in plain language
- Second paragraph: what actually changed or what you built
- Third paragraph: casual mention of the product with the direct link, then one sentence: "I've been building more tools at {SITE_URL} if you're into this kind of thing."
- Tone: direct, slightly tired of bad advice, genuinely useful
- No em-dashes, no bullet lists, no "I'm excited", no "game-changer", no "hope this helps"
- Never say "free" or "no signup required" if it has a price

Return ONLY valid JSON: {{"title": "...", "body": "..."}}"""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
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
    # Strip em-dashes post-generation as safety net
    data["title"] = data.get("title", "").replace("\u2014", ",").replace("\u2013", "-")
    data["body"] = data.get("body", "").replace("\u2014", ",").replace("\u2013", "-")
    return data


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    # Load latest counselor report
    cache_path = ROOT / "data/counselor-cache.json"
    if not cache_path.exists():
        _send("❌ No counselor report found. Run /counsel first.")
        return

    cache = json.loads(cache_path.read_text())
    sections = cache.get("sections", {})
    fetched_at = cache.get("fetched_at", "")[:10]

    pricing = sections.get("pricing_suggestions", [])
    post_suggestions = sections.get("next_reddit_posts", [])
    what_to_fix = sections.get("what_to_fix", [])

    _send(f"⚙️ <b>Running counsel actions</b> (from report {fetched_at})…\n\nApplying prices, generating posts.")

    # ── 1. Price changes ──────────────────────────────────────────────────────
    catalog_data = read_json("data/product-catalog.json")
    catalog = catalog_data.get("products", [])

    # Cross-check pricing suggestions against live Gumroad data
    # Skip suggestions where the product doesn't exist on Gumroad or price is already correct
    try:
        live_products = _get_gumroad_products()
        live_by_slug = {}
        for gp in live_products:
            slug = gp.get("short_url", "").rstrip("/").split("/")[-1]
            live_by_slug[slug] = gp
    except Exception:
        live_products = []
        live_by_slug = {}

    validated_prices = []
    skipped_prices = []
    for s in pricing:
        if s.get("current_price") == s.get("suggested_price"):
            skipped_prices.append((s["product"], "price already correct"))
            continue
        gumroad_id = _find_gumroad_id(s["product"], catalog)
        if not gumroad_id:
            skipped_prices.append((s["product"], "not found on Gumroad — may not be published yet"))
            continue
        # Check live price
        live_price_cents = None
        for gp in live_products:
            if gp.get("id") == gumroad_id:
                live_price_cents = gp.get("price", 0)
                break
        suggested_cents = int(float(s.get("suggested_price", "$0").replace("$", "")) * 100)
        if live_price_cents is not None and live_price_cents == suggested_cents:
            skipped_prices.append((s["product"], f"already at {s['suggested_price']} on Gumroad"))
            continue
        validated_prices.append(s)

    actionable_prices = validated_prices
    price_results = []
    if actionable_prices:
        log("counsel-go", f"Applying {len(actionable_prices)} price changes…")
        price_results = apply_price_changes(actionable_prices, catalog)

        # Sync prices + rebuild vitrine
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/publish_product.py"), "--sync-prices"],
            cwd=str(ROOT), capture_output=True,
        )
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/update_site.py"), "--rebuild-all"],
            cwd=str(ROOT), capture_output=True,
        )

        price_lines = []
        manual_price = []
        for r in price_results:
            name = r["product"][:50].replace("&", "&amp;").replace("<", "&lt;")
            if r["status"] == "updated":
                price_lines.append(f"✅ {name} → {r['price']}")
            elif r["status"] == "skipped":
                price_lines.append(f"⏭ {name} — already correct")
            else:
                step = r.get("manual_step", f"Update price for {name} manually on gumroad.com")
                manual_price.append(step.replace("&", "&amp;").replace("<", "&lt;"))

        lines = price_lines if price_lines else ["No automatic updates applied."]
        msg = "💰 <b>Price updates</b>\n\n" + "\n".join(lines)
        if skipped_prices:
            skipped_lines = "\n".join(
                f"⏭ {name[:45].replace('&','&amp;').replace('<','&lt;')} — {reason}"
                for name, reason in skipped_prices
            )
            msg += f"\n\n<i>Skipped:</i>\n{skipped_lines}"
        if manual_price:
            msg += "\n\n📋 <b>Do manually:</b>\n" + "\n".join(f"• {s}" for s in manual_price)
        _send(msg)
        time.sleep(0.5)
    else:
        msg = "💰 <b>Price updates</b>\n\nNo changes needed."
        if skipped_prices:
            skipped_lines = "\n".join(
                f"⏭ {name[:45].replace('&','&amp;').replace('<','&lt;')} — {reason}"
                for name, reason in skipped_prices
            )
            msg += f"\n\n<i>Skipped:</i>\n{skipped_lines}"
        _send(msg)
        time.sleep(0.5)

    # ── 2. Reddit post drafts ─────────────────────────────────────────────────
    log("counsel-go", f"Generating {len(post_suggestions)} Reddit post drafts…")
    post_lines = []
    for i, suggestion in enumerate(post_suggestions, 1):
        sub = suggestion.get("subreddit", "")
        angle = suggestion.get("angle", "")
        product = suggestion.get("product", "")
        why = suggestion.get("why", "")
        try:
            post = generate_post_from_angle(sub, angle, product)
            title = post.get("title", "")
            body = post.get("body", "")
            _send(
                f"📣 <b>Post {i}/{len(post_suggestions)} — r/{sub}</b>\n"
                f"<i>Why: {why}</i>\n\n"
                f"<b>Title:</b>\n<code>{title}</code>\n\n"
                f"<b>Body:</b>\n<code>{body}</code>"
            )
            post_lines.append(("ok", sub, None))
        except Exception as e:
            angle_short = angle[:80].replace("&", "&amp;").replace("<", "&lt;")
            _send(
                f"❌ <b>Post {i}/{len(post_suggestions)} — r/{sub} failed</b>\n\n"
                f"Generate it manually with:\n<code>/post {sub}</code>\n\n"
                f"Or write a post with this angle:\n<i>{angle_short}</i>"
            )
            post_lines.append(("fail", sub, angle))
        time.sleep(1)

    # ── 3. Manual checklist ───────────────────────────────────────────────────
    manual_items = []

    # Posts that were successfully generated — user needs to actually post them
    ok_posts = [sub for status, sub, _ in post_lines if status == "ok"]
    if ok_posts:
        subs_str = ", ".join(f"r/{s}" for s in ok_posts)
        manual_items.append(f"Post the {len(ok_posts)} drafts above on Reddit — one per day: {subs_str}")

    # Posts that failed generation — tell user to use /post manually
    failed_posts = [(sub, angle) for status, sub, angle in post_lines if status == "fail"]
    for sub, angle in failed_posts:
        manual_items.append(f"Generate post for r/{sub} manually: /post {sub}")

    # Prices that couldn't be automated
    for r in price_results:
        if r.get("status") == "manual" and r.get("manual_step"):
            manual_items.append(r["manual_step"])

    # From what_to_fix — structural advice
    for item in what_to_fix:
        if "free" in item.lower() and "paid" in item.lower():
            manual_items.append("Split a product into free preview + paid tier: keep 2 skills free, gate rest behind $5 on Gumroad")
        elif "rewrite" in item.lower() or "title" in item.lower():
            manual_items.append("Rewrite weak post titles to lead with the specific pain: use /fix {sub} | title too vague")

    # Deduplicate
    seen = set()
    deduped = []
    for item in manual_items:
        if item not in seen:
            seen.add(item)
            deduped.append(item)

    if deduped:
        checklist = "\n".join(f"{i}. {item}" for i, item in enumerate(deduped, 1))
        _send(f"📋 <b>Your manual checklist</b>\n\n{checklist}")
    else:
        _send("✅ <b>All actions completed automatically.</b>")

    log("counsel-go", "Done.")


if __name__ == "__main__":
    run()
