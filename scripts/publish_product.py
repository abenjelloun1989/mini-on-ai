#!/usr/bin/env python3
"""
publish_product.py
Publishes a product to Gumroad after it has been packaged and added to the site.

Requires env vars:
  GUMROAD_API_TOKEN     — from Gumroad Settings → Advanced → Access token
  PRODUCT_PRICE_CENTS   — default price in cents, e.g. 500 = $5.00 (default: 500)

Usage:
  python3 scripts/publish_product.py
  python3 scripts/publish_product.py --id product-id
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import requests
from lib.utils import read_json, write_json, write_file, log, ROOT

GUMROAD_API = "https://api.gumroad.com/v2"


def _get_token() -> str:
    token = os.getenv("GUMROAD_API_TOKEN", "")
    if not token:
        raise RuntimeError("GUMROAD_API_TOKEN not set. Add it to .env")
    return token


def _build_description(meta: dict) -> str:
    """Build an HTML product description for Gumroad from meta fields."""
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


def publish_product(product_id_arg: str = None) -> dict:
    """Publish or update a product on Gumroad. Returns updated meta."""
    token = _get_token()
    default_price = int(os.getenv("PRODUCT_PRICE_CENTS", "500"))

    # Resolve which product to publish
    if product_id_arg:
        pid = product_id_arg
        meta_path = ROOT / f"products/{pid}/meta.json"
        with open(meta_path) as f:
            meta = json.load(f)
    else:
        products_dir = ROOT / "products"
        candidates = []
        for d in products_dir.iterdir():
            mp = d / "meta.json"
            if mp.exists():
                with open(mp) as f:
                    m = json.load(f)
                if m.get("status") == "published" and not m.get("gumroad_product_id"):
                    candidates.append((d.name, m))
        if not candidates:
            raise RuntimeError(
                "No publishable products found (status=published, no gumroad_product_id)."
            )
        candidates.sort(key=lambda x: x[1].get("created_at", ""))
        pid, meta = candidates[-1]

    log("publish", f"Publishing: {meta['title']} ({pid})")

    description = _build_description(meta)
    price_cents = meta.get("price") or default_price

    headers = {"Authorization": f"Bearer {token}"}

    # ── Create or update listing ─────────────────────────────────────────────
    existing_id = meta.get("gumroad_product_id")
    if existing_id:
        log("publish", f"Updating existing Gumroad product: {existing_id}")
        resp = requests.put(
            f"{GUMROAD_API}/products/{existing_id}",
            headers=headers,
            data={
                "name": meta["title"],
                "description": description,
                "price": price_cents,
            },
            timeout=30,
        )
    else:
        log("publish", "Creating new Gumroad listing...")
        resp = requests.post(
            f"{GUMROAD_API}/products",
            headers=headers,
            data={
                "name": meta["title"],
                "description": description,
                "price": price_cents,
            },
            timeout=30,
        )

    resp.raise_for_status()
    result = resp.json()

    if not result.get("success"):
        raise RuntimeError(f"Gumroad API error: {result.get('message', result)}")

    product_data = result["product"]
    gumroad_id = product_data["id"]
    gumroad_url = product_data.get("short_url") or product_data.get("url", "")

    log("publish", f"Gumroad listing ready: {gumroad_url}")

    # ── Upload zip file ───────────────────────────────────────────────────────
    zip_path = ROOT / f"products/{pid}/package.zip"
    if zip_path.exists():
        log("publish", "Uploading package.zip...")
        with open(zip_path, "rb") as zf:
            upload_resp = requests.post(
                f"{GUMROAD_API}/products/{gumroad_id}/files",
                headers=headers,
                files={"file": (f"{pid}.zip", zf, "application/zip")},
                timeout=120,
            )
        if upload_resp.status_code == 200:
            log("publish", "File uploaded successfully")
        else:
            log("publish", f"Warning: file upload returned {upload_resp.status_code}: {upload_resp.text[:200]}")
    else:
        log("publish", f"Warning: package.zip not found at {zip_path}")

    # ── Save back to meta.json ────────────────────────────────────────────────
    meta["gumroad_product_id"] = gumroad_id
    meta["gumroad_url"] = gumroad_url
    meta["price"] = price_cents
    write_file(
        f"products/{pid}/meta.json",
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
    )

    # ── Update catalog entry ──────────────────────────────────────────────────
    catalog = read_json("data/product-catalog.json")
    for entry in catalog["products"]:
        if entry["id"] == pid:
            entry["gumroad_url"] = gumroad_url
            entry["price"] = price_cents
            break
    write_json("data/product-catalog.json", catalog)

    log("publish", f"Done. Gumroad URL: {gumroad_url}")
    return meta


def main():
    parser = argparse.ArgumentParser(description="Publish product to Gumroad")
    parser.add_argument("--id", default=None, help="Product ID to publish")
    args = parser.parse_args()
    publish_product(args.id)


if __name__ == "__main__":
    main()
