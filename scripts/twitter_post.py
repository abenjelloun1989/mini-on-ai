#!/usr/bin/env python3
"""
twitter_post.py
Post a tweet on your behalf using the Twitter API v2.

Usage:
  python3 scripts/twitter_post.py                        # auto-draft from latest product
  python3 scripts/twitter_post.py --message "My tweet"   # custom message
  python3 scripts/twitter_post.py --draft                # print tweet, don't post

Requirements in .env:
  TWITTER_API_KEY
  TWITTER_API_SECRET
  TWITTER_ACCESS_TOKEN
  TWITTER_ACCESS_TOKEN_SECRET
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import base64
import secrets
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, log


# ── OAuth 1.0a ────────────────────────────────────────────────────────────────

def _percent_encode(s: str) -> str:
    return urllib.parse.quote(str(s), safe="")


def _build_oauth_header(method: str, url: str, params: dict) -> str:
    api_key       = os.getenv("TWITTER_API_KEY", "")
    api_secret    = os.getenv("TWITTER_API_SECRET", "")
    access_token  = os.getenv("TWITTER_ACCESS_TOKEN", "")
    access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

    if not all([api_key, api_secret, access_token, access_secret]):
        raise RuntimeError(
            "Twitter credentials missing. Set TWITTER_API_KEY, TWITTER_API_SECRET, "
            "TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET in your .env file."
        )

    nonce     = secrets.token_hex(16)
    timestamp = str(int(time.time()))

    oauth_params = {
        "oauth_consumer_key":     api_key,
        "oauth_nonce":            nonce,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp":        timestamp,
        "oauth_token":            access_token,
        "oauth_version":          "1.0",
    }

    # Signature base string
    all_params = {**params, **oauth_params}
    sorted_params = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in sorted(all_params.items())
    )
    base_string = "&".join([
        method.upper(),
        _percent_encode(url),
        _percent_encode(sorted_params),
    ])

    signing_key = f"{_percent_encode(api_secret)}&{_percent_encode(access_secret)}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()

    oauth_params["oauth_signature"] = signature
    header_value = "OAuth " + ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )
    return header_value


# ── Tweet posting ─────────────────────────────────────────────────────────────

def post_tweet(text: str) -> dict:
    """Post a tweet and return the API response."""
    url = "https://api.twitter.com/2/tweets"
    body = json.dumps({"text": text}).encode("utf-8")
    auth_header = _build_oauth_header("POST", url, {})

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization":  auth_header,
            "Content-Type":   "application/json",
            "Accept":         "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        response = json.loads(resp.read().decode("utf-8"))
    return response


# ── Draft helpers ─────────────────────────────────────────────────────────────

_TAG_MAP = {
    # Claude / AI dev community
    "claude":           "#ClaudeCode",
    "claude-code":      "#ClaudeCode",
    "ai":               "#AI",
    "llm":              "#LLM",
    "chatgpt":          "#ChatGPT",
    # Automation community
    "n8n":              "#n8n",
    "automation":       "#automation",
    "nocode":           "#nocode",
    "zapier":           "#zapier",
    "make":             "#make",
    # Developer community
    "coding":           "#coding",
    "developer":        "#developer",
    "engineering":      "#softwareengineering",
    "documentation":    "#devdocs",
    # Productivity / business
    "productivity":     "#productivity",
    "freelance":        "#freelance",
    "marketing":        "#marketing",
    "writing":          "#writing",
    "solopreneur":      "#solopreneur",
    "entrepreneur":     "#entrepreneur",
}

# Fallback hashtags per product category
_CATEGORY_HASHTAGS = {
    "claude-code-skill": ["#ClaudeCode", "#AI", "#developer"],
    "n8n-template":      ["#n8n", "#automation", "#nocode"],
    "prompt-packs":      ["#AI", "#productivity", "#prompts"],
    "mini-guide":        ["#AI", "#productivity"],
    "checklist":         ["#productivity", "#tools"],
    "swipe-file":        ["#copywriting", "#marketing"],
}


def draft_for_product(meta: dict) -> str:
    """Generate a deterministic tweet draft for a given product meta dict."""
    site_url = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")
    title    = meta.get("title", "New product")
    desc     = meta.get("description", "")
    price_cents = meta.get("price_usd") or meta.get("price") or 0
    pid         = meta.get("id", "")
    tags        = meta.get("tags") or []

    product_url = f"{site_url}/products/{pid}.html" if pid else site_url

    cat = meta.get("category", "")
    hashtags = list(dict.fromkeys(
        _TAG_MAP[t] for t in tags if t in _TAG_MAP
    ))[:3]
    if not hashtags:
        hashtags = _CATEGORY_HASHTAGS.get(cat, ["#AI", "#productivity"])
    hashtag_str = " ".join(hashtags)

    # price stored in cents (500 = $5)
    if meta.get("is_free") or price_cents == 0:
        price_str = "free"
    else:
        price_str = f"${price_cents // 100}"

    tweet = (
        f"Just published: {title} ({price_str})\n\n"
        f"{desc[:120].rstrip()}{'…' if len(desc) > 120 else ''}\n\n"
        f"{product_url}\n\n"
        f"{hashtag_str}"
    )
    if len(tweet) > 280:
        available = 280 - len(tweet) + len(desc[:120])
        tweet = (
            f"Just published: {title} ({price_str})\n\n"
            f"{desc[:max(0, available - 1)].rstrip()}…\n\n"
            f"{product_url}\n\n"
            f"{hashtag_str}"
        )
    return tweet


def _draft_from_latest_product() -> str:
    site_url = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")

    try:
        catalog = read_json("data/product-catalog.json")
        products = catalog.get("products", [])
    except Exception:
        products = []

    if not products:
        return (
            "I've been building Claude Code skills and AI workflow packs — "
            f"check them out at {site_url} 🧰 #ClaudeCode #AI #automation"
        )

    return draft_for_product(products[-1])


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Post a tweet on your behalf")
    parser.add_argument("--message", default=None, help="Custom tweet text")
    parser.add_argument("--draft",   action="store_true", help="Print tweet without posting")
    args = parser.parse_args()

    text = args.message or _draft_from_latest_product()

    print("\n── Tweet preview (" + str(len(text)) + " chars) ──────────────────")
    print(text)
    print("─────────────────────────────────────────────\n")

    if len(text) > 280:
        print(f"ERROR: Tweet is {len(text)} chars — max is 280. Shorten it with --message.", file=sys.stderr)
        sys.exit(1)

    if args.draft:
        log("twitter", "Draft mode — not posting.")
        return

    log("twitter", "Posting tweet…")
    try:
        resp = post_tweet(text)
        tweet_id = resp.get("data", {}).get("id", "?")
        log("twitter", f"Posted! Tweet ID: {tweet_id}")
        log("twitter", f"https://twitter.com/i/web/status/{tweet_id}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
