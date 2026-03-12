#!/usr/bin/env python3
"""
update_site.py
Adds a product to the showcase website and updates the product catalog.

Usage: python3 scripts/update_site.py [--id product-id]
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, write_json, write_file, ROOT, log


CATEGORY_LABELS = {
    "prompt-packs":  ("Prompt Pack",  "{n} prompts"),
    "checklist":     ("Checklist",    "{n} items"),
    "swipe-file":    ("Swipe File",   "{n} examples"),
    "mini-guide":    ("Mini Guide",   "focused guide"),
    "n8n-template":  ("n8n Template", "{n}-node workflow"),
}

CATEGORY_INCLUDES = {
    "prompt-packs": [
        "{n} ready-to-use prompts",
        "Works with ChatGPT, Claude, Gemini, and others",
        "Markdown and JSON formats",
        "Organized by use case",
    ],
    "checklist": [
        "{n} actionable checklist items",
        "Organized by phase",
        "Context explaining why each step matters",
        "Markdown and JSON formats",
    ],
    "swipe-file": [
        "{n} copy-ready examples",
        "Notes on when and how to use each one",
        "Markdown and JSON formats",
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


def _item_count(meta: dict) -> int:
    return meta.get("item_count") or meta.get("prompt_count", 0)


def _category_badge(meta: dict) -> str:
    cat = meta.get("category", "prompt-packs")
    label = CATEGORY_LABELS.get(cat, ("Resource", ""))[0]
    return f'<span class="category-badge category-{cat}">{escape_html(label)}</span>'


def _count_label(meta: dict) -> str:
    cat = meta.get("category", "prompt-packs")
    n = _item_count(meta)
    template = CATEGORY_LABELS.get(cat, ("", "{n} items"))[1]
    return template.replace("{n}", str(n))


def _includes_html(meta: dict) -> str:
    cat = meta.get("category", "prompt-packs")
    n = _item_count(meta)
    items = CATEGORY_INCLUDES.get(cat, ["{n} items included"])
    lines = "\n".join(f"        <li>{escape_html(i.replace('{n}', str(n)))}</li>" for i in items)
    return f"      <ul>\n{lines}\n      </ul>"


def escape_html(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_product_page(meta: dict) -> str:
    tags_html = " ".join(f'<span class="tag">{escape_html(t)}</span>' for t in (meta.get("tags") or []))
    download_path = "package.zip"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape_html(meta['title'])}</title>
  <link rel="stylesheet" href="../style.css">
  <meta name="description" content="{escape_html(meta['description'])}">
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <a href="../index.html" class="site-logo">← Back to catalog</a>
    </div>
  </header>

  <main class="product-detail">
    <div class="product-tags">{_category_badge(meta)}{tags_html}</div>
    <h1>{escape_html(meta['title'])}</h1>
    <p class="product-desc-large">{escape_html(meta['description'])}</p>

    <div class="product-stats">
      <span>{escape_html(_count_label(meta))}</span>
    </div>

    <a href="{download_path}" class="btn-download btn-large">
      Download Free
    </a>

    <section class="product-details">
      <h2>What's included</h2>
{_includes_html(meta)}
    </section>
  </main>

  <footer class="site-footer">
    <p>&copy; {datetime.now().year} mini-on-ai</p>
  </footer>
</body>
</html>
"""


def build_product_card(meta: dict) -> str:
    tags_html = " ".join(f'<span class="tag">{escape_html(t)}</span>' for t in (meta.get("tags") or []))
    return f"""      <article class="product-card">
        <div class="product-tags">{_category_badge(meta)}{tags_html}</div>
        <h2 class="product-title"><a href="products/{meta['id']}.html">{escape_html(meta['title'])}</a></h2>
        <p class="product-desc">{escape_html(meta['description'])}</p>
        <div class="product-meta">{escape_html(_count_label(meta))}</div>
        <a href="products/{meta['id']}/package.zip" class="btn-download">Download Free</a>
      </article>"""


def rebuild_index(catalog: dict) -> str:
    count = len(catalog["products"])
    cards = "\n".join(build_product_card(p) for p in catalog["products"])
    year = datetime.now().year

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>mini-on-ai — Free Digital Resources</title>
  <link rel="stylesheet" href="style.css">
  <meta name="description" content="Free digital resources, prompt packs, and tools.">
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <a href="index.html" class="site-logo">mini-on-ai</a>
      <span class="product-count">{count} free resource{'s' if count != 1 else ''}</span>
    </div>
  </header>

  <main class="catalog">
    <div class="catalog-header">
      <h1>Free Digital Resources</h1>
      <p>Download and use immediately. No signup required.</p>
    </div>

    <div class="product-grid">
{cards}
    </div>
  </main>

  <footer class="site-footer">
    <p>&copy; {year} mini-on-ai</p>
  </footer>
</body>
</html>
"""


def update_site(product_id_arg: str = None) -> dict:
    if product_id_arg:
        pid = product_id_arg
        meta_path = ROOT / f"products/{pid}/meta.json"
        with open(meta_path) as f:
            meta = json.load(f)
    else:
        products_dir = ROOT / "products"
        if not products_dir.exists():
            raise RuntimeError("No products directory found")

        candidates = []
        for d in products_dir.iterdir():
            meta_path = d / "meta.json"
            if meta_path.exists():
                with open(meta_path) as f:
                    m = json.load(f)
                if m.get("status") == "packaged":
                    candidates.append((d.name, m))

        if not candidates:
            raise RuntimeError("No packaged products found. Run package_product first.")

        candidates.sort(key=lambda x: x[1].get("created_at", ""))
        pid, meta = candidates[-1]

    log("update-site", f"Adding to site: {meta['title']} ({pid})")

    # Copy zip into site so GitHub Pages can serve it
    zip_src = ROOT / meta["package_path"]
    zip_dst_dir = ROOT / "site" / "products" / pid
    zip_dst_dir.mkdir(parents=True, exist_ok=True)
    zip_dst = zip_dst_dir / "package.zip"
    if zip_src.exists():
        shutil.copy2(zip_src, zip_dst)
        log("update-site", f"Copied package.zip → site/products/{pid}/package.zip")
    else:
        log("update-site", f"Warning: zip not found at {zip_src}")

    # Write product page
    product_page = build_product_page(meta)
    write_file(f"site/products/{pid}.html", product_page)
    log("update-site", f"Created site/products/{pid}.html")

    # Update catalog
    catalog = read_json("data/product-catalog.json")
    catalog_entry = {
        "id": meta["id"],
        "title": meta["title"],
        "description": meta["description"],
        "category": meta.get("category", "prompt-packs"),
        "tags": meta.get("tags", []),
        "item_count": _item_count(meta),
        "prompt_count": meta.get("prompt_count") or meta.get("item_count", 0),
        "created_at": meta["created_at"],
        "package_path": meta["package_path"],
        "site_path": f"site/products/{pid}.html",
    }

    existing_idx = next((i for i, p in enumerate(catalog["products"]) if p["id"] == pid), None)
    if existing_idx is not None:
        catalog["products"][existing_idx] = catalog_entry
    else:
        catalog["products"].insert(0, catalog_entry)  # newest first

    write_json("data/product-catalog.json", catalog)

    # Rebuild index
    index_html = rebuild_index(catalog)
    write_file("site/index.html", index_html)
    log("update-site", "Rebuilt site/index.html")

    # Update meta status
    meta["status"] = "published"
    meta["site_path"] = f"site/products/{pid}.html"
    write_file(f"products/{pid}/meta.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    log("update-site", "Done. Open site/index.html to preview.")
    return meta


def main():
    parser = argparse.ArgumentParser(description="Add product to showcase site")
    parser.add_argument("--id", default=None, help="Product ID")
    args = parser.parse_args()
    update_site(args.id)


if __name__ == "__main__":
    main()
