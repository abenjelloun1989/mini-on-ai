#!/usr/bin/env python3
"""
update_site.py
Adds a product to the showcase website and updates the product catalog.

Usage: python3 scripts/update_site.py [--id product-id]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, write_json, write_file, ROOT, log


def escape_html(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_product_page(meta: dict) -> str:
    site_url = os.getenv("SITE_URL", "")
    tags_html = " ".join(f'<span class="tag">{escape_html(t)}</span>' for t in (meta.get("tags") or []))
    download_path = f"/{meta['package_path']}"

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
    <div class="product-tags">{tags_html}</div>
    <h1>{escape_html(meta['title'])}</h1>
    <p class="product-desc-large">{escape_html(meta['description'])}</p>

    <div class="product-stats">
      <span>{meta['prompt_count']} prompts included</span>
    </div>

    <a href="{download_path}" class="btn-download btn-large">
      Download Free
    </a>

    <section class="product-details">
      <h2>What's included</h2>
      <ul>
        <li>{meta['prompt_count']} ready-to-use prompts</li>
        <li>Works with any AI assistant (ChatGPT, Claude, Gemini, and others)</li>
        <li>Markdown and JSON formats included</li>
        <li>Organized by use case</li>
      </ul>
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
        <div class="product-tags">{tags_html}</div>
        <h2 class="product-title"><a href="products/{meta['id']}.html">{escape_html(meta['title'])}</a></h2>
        <p class="product-desc">{escape_html(meta['description'])}</p>
        <div class="product-meta">{meta['prompt_count']} prompts</div>
        <a href="{meta['package_path']}" class="btn-download">Download Free</a>
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
        "category": meta["category"],
        "tags": meta.get("tags", []),
        "prompt_count": meta["prompt_count"],
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
