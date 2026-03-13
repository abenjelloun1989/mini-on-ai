#!/usr/bin/env python3
"""
publish_product.py
Handles Gumroad publishing for products.

Gumroad's v2 API supports READ and UPDATE of existing products, but NOT
creation of new listings via API (removed ~2023). New products must be
created manually through the Gumroad dashboard.

Workflow:
  NEW product  → sends Telegram message with all details + zip file attached
                  User creates on Gumroad, replies /seturl {id} {url}
  KNOWN product → update listing via API + re-upload zip

Usage:
  python3 scripts/publish_product.py              # auto-pick latest unpublished
  python3 scripts/publish_product.py --id {id}   # specific product
  python3 scripts/publish_product.py --seturl {id} {gumroad_url}  # save URL back

Env vars:
  GUMROAD_API_TOKEN   — from Gumroad Settings → Advanced → Access token
  PRODUCT_PRICE_CENTS — default listing price in cents (default: 500 = $5.00)
  TELEGRAM_BOT_TOKEN  — for sending publish-request notification
  TELEGRAM_OWNER_ID   — your Telegram chat ID
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import requests
from lib.utils import read_json, write_json, write_file, log, ROOT

GUMROAD_API = "https://api.gumroad.com/v2"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _token() -> str:
    t = os.getenv("GUMROAD_API_TOKEN", "")
    if not t:
        raise RuntimeError("GUMROAD_API_TOKEN not set in .env")
    return t


def _build_description(meta: dict) -> str:
    category = meta.get("category", "prompt-packs")
    item_count = meta.get("item_count") or meta.get("prompt_count", 0)

    includes_map = {
        "prompt-packs": [
            f"{item_count} ready-to-use prompts",
            "Works with ChatGPT, Claude, Gemini, and others",
            "Markdown and JSON formats included",
            "Organized by use case",
        ],
        "checklist": [
            f"{item_count} actionable checklist items",
            "Organized by phase",
            "Context explaining why each step matters",
            "Markdown and JSON formats included",
        ],
        "swipe-file": [
            f"{item_count} copy-ready examples",
            "Notes on when and how to use each one",
            "Markdown and JSON formats included",
        ],
        "mini-guide": [
            "Concise practitioner-focused guide",
            "Concrete tips, examples, and frameworks",
            "Quick-reference summary at the end",
            "Markdown format",
        ],
        "n8n-template": [
            "Ready-to-import n8n workflow (workflow.json)",
            "Step-by-step setup instructions",
            "Works with n8n self-hosted and n8n.cloud",
            "Customizable — adapt to your own tools",
        ],
    }

    items = includes_map.get(category, [f"{item_count} items included"])
    items_html = "\n".join(f"<li>{i}</li>" for i in items)
    return (
        f"<p>{meta['description']}</p>\n"
        f"<h3>What's included</h3>\n"
        f"<ul>\n{items_html}\n</ul>"
    )


def _telegram_send_text(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        log("publish", "Telegram not configured — skipping notification")
        return
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15):
            pass
    except Exception as e:
        log("publish", f"Telegram text error: {e}")


def _telegram_send_file(file_path: Path, caption: str) -> None:
    """Send a file (zip) via Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    try:
        with open(file_path, "rb") as f:
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendDocument",
                data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
                files={"document": (file_path.name, f, "application/zip")},
                timeout=60,
            )
        if resp.status_code != 200:
            log("publish", f"Telegram file send failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        log("publish", f"Telegram file send error: {e}")


def _resolve_product(product_id_arg: str = None) -> tuple:
    """Return (pid, meta) for the product to publish."""
    if product_id_arg:
        pid = product_id_arg
        meta_path = ROOT / f"products/{pid}/meta.json"
        with open(meta_path) as f:
            meta = json.load(f)
        return pid, meta

    products_dir = ROOT / "products"
    candidates = []
    for d in products_dir.iterdir():
        mp = d / "meta.json"
        if mp.exists():
            with open(mp) as f:
                m = json.load(f)
            if m.get("status") == "published" and not m.get("gumroad_url"):
                candidates.append((d.name, m))
    if not candidates:
        raise RuntimeError(
            "No unpublished products found (status=published and no gumroad_url)."
        )
    candidates.sort(key=lambda x: x[1].get("created_at", ""))
    return candidates[-1]


# ── Core publish logic ────────────────────────────────────────────────────────

def notify_manual_publish(pid: str, meta: dict) -> None:
    """
    Gumroad no longer supports creating products via API.
    Send a Telegram message with product details + zip so the user can
    create the listing manually and reply /seturl {id} {url}.
    """
    price_cents = meta.get("price") or int(os.getenv("PRODUCT_PRICE_CENTS", "500"))
    price_str = f"${price_cents / 100:.2f}"
    category = meta.get("category", "prompt-packs")
    item_count = meta.get("item_count") or meta.get("prompt_count", 0)

    msg = (
        f"📦 <b>New product ready — publish on Gumroad</b>\n\n"
        f"<b>{meta['title']}</b>\n"
        f"<i>{meta['description']}</i>\n\n"
        f"Category: {category}  |  Items: {item_count}  |  Price: {price_str}\n\n"
        f"<b>Steps:</b>\n"
        f"1. Go to <a href='https://app.gumroad.com/products/new'>gumroad.com/products/new</a>\n"
        f"2. Name: <code>{meta['title']}</code>\n"
        f"3. Price: <code>{price_str}</code>\n"
        f"4. Upload the zip attached to this message\n"
        f"5. Publish, then copy the product URL\n"
        f"6. Reply: <code>/seturl {pid} https://gumroad.com/l/xxxx</code>\n\n"
        f"Product ID: <code>{pid}</code>"
    )
    _telegram_send_text(msg)

    zip_path = ROOT / f"products/{pid}/package.zip"
    if zip_path.exists():
        _telegram_send_file(zip_path, f"📎 {meta['title']} — package.zip")
    else:
        log("publish", f"Warning: package.zip not found at {zip_path}")


def update_existing_listing(pid: str, meta: dict) -> None:
    """Update an existing Gumroad listing via API and re-upload the zip."""
    token = _token()
    gumroad_id = meta.get("gumroad_product_id")
    description = _build_description(meta)
    price_cents = meta.get("price") or int(os.getenv("PRODUCT_PRICE_CENTS", "500"))

    log("publish", f"Updating Gumroad product {gumroad_id}...")
    resp = requests.put(
        f"{GUMROAD_API}/products/{gumroad_id}",
        data={
            "access_token": token,
            "name": meta["title"],
            "description": description,
            "price": price_cents,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        log("publish", f"Warning: Gumroad update returned {resp.status_code}: {resp.text[:200]}")
        return

    result = resp.json()
    if not result.get("success"):
        log("publish", f"Warning: Gumroad update failed: {result.get('message', result)}")
        return

    log("publish", "Listing updated. Re-uploading zip...")
    zip_path = ROOT / f"products/{pid}/package.zip"
    if zip_path.exists():
        with open(zip_path, "rb") as zf:
            upload_resp = requests.post(
                f"{GUMROAD_API}/products/{gumroad_id}/files",
                data={"access_token": token},
                files={"file": (f"{pid}.zip", zf, "application/zip")},
                timeout=120,
            )
        if upload_resp.status_code == 200:
            log("publish", "Zip re-uploaded successfully")
        else:
            log("publish", f"Warning: zip upload returned {upload_resp.status_code}")


def publish_product(product_id_arg: str = None) -> dict:
    """
    Main entry point: either notify manual publish (new) or update existing.
    Returns the (possibly updated) meta dict.
    """
    pid, meta = _resolve_product(product_id_arg)
    log("publish", f"Product: {meta['title']} ({pid})")

    if meta.get("gumroad_product_id"):
        # Known product — update listing via API
        update_existing_listing(pid, meta)
        log("publish", "Done (existing listing updated)")
    else:
        # New product — must be created manually; send Telegram notification
        log("publish", "No Gumroad ID found — sending manual-publish notification via Telegram")
        notify_manual_publish(pid, meta)
        log("publish", "Telegram notification sent. Waiting for /seturl reply.")

    return meta


def set_gumroad_url(pid: str, gumroad_url: str) -> dict:
    """
    Called after user creates the Gumroad listing manually and sends /seturl.
    Saves URL to meta.json + catalog, returns updated meta.
    """
    meta_path = ROOT / f"products/{pid}/meta.json"
    if not meta_path.exists():
        raise RuntimeError(f"Product not found: {pid}")
    with open(meta_path) as f:
        meta = json.load(f)

    # Extract Gumroad product ID from URL if possible (e.g. gumroad.com/l/abcde)
    gumroad_id = None
    if "/l/" in gumroad_url:
        gumroad_id = gumroad_url.rstrip("/").split("/l/")[-1].split("?")[0]

    meta["gumroad_url"] = gumroad_url
    if gumroad_id:
        meta["gumroad_product_id"] = gumroad_id

    write_file(
        f"products/{pid}/meta.json",
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
    )
    log("publish", f"Saved gumroad_url={gumroad_url} for {pid}")

    # Update catalog
    catalog = read_json("data/product-catalog.json")
    for entry in catalog.get("products", []):
        if entry["id"] == pid:
            entry["gumroad_url"] = gumroad_url
            break
    write_json("data/product-catalog.json", catalog)
    log("publish", "Catalog updated")

    return meta


def main():
    parser = argparse.ArgumentParser(description="Publish product to Gumroad")
    parser.add_argument("--id", default=None, help="Product ID to publish")
    parser.add_argument(
        "--seturl",
        nargs=2,
        metavar=("PRODUCT_ID", "GUMROAD_URL"),
        help="Save a Gumroad URL back to a product (after manual creation)",
    )
    args = parser.parse_args()

    if args.seturl:
        pid, url = args.seturl
        set_gumroad_url(pid, url)
        print(f"✅ Saved: {pid} → {url}")
    else:
        publish_product(args.id)


if __name__ == "__main__":
    main()
