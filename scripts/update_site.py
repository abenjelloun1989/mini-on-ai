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

CONTACT_EMAIL = "hello@mini-on-ai.com"

CATEGORY_LABELS = {
    "prompt-packs":      ("Prompt Pack",        "{n} prompts"),
    "checklist":         ("Checklist",           "{n} items"),
    "swipe-file":        ("Swipe File",          "{n} examples"),
    "mini-guide":        ("Mini Guide",          "focused guide"),
    "n8n-template":      ("n8n Template",        "{n}-node workflow"),
    "claude-code-skill": ("CC Skills Pack",        "{n} skills"),
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
    "claude-code-skill": [
        "5 ready-to-use SKILL.md files (drop into `skills/`, no setup required)",
        "Each skill covers a distinct sub-task in the workflow domain",
        "Installation guide with quick-reference table of all triggers",
        "Works immediately with Claude Code — just run `claude`",
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


def _thumbnail_html_detail(meta: dict) -> str:
    thumb = meta.get("thumbnail")
    cat = meta.get("category", "prompt-packs")
    if thumb:
        src = f"../{escape_html(thumb)}"
    else:
        # Use category-specific placeholder on detail pages too
        cat_key = cat if cat in ("prompt-packs", "checklist", "swipe-file", "mini-guide", "n8n-template") else "prompt-packs"
        src = f"../images/placeholder-{cat_key}.svg"
    return f'  <img src="{src}" alt="" class="product-thumbnail-detail" aria-hidden="true" style="width:100%;border-radius:14px;margin-bottom:32px;aspect-ratio:16/9;object-fit:cover;">\n'


def _gumroad_cta_page(meta: dict) -> str:
    """Gumroad CTA button for the product detail page."""
    url = meta.get("gumroad_url")
    if url:
        return f'    <a href="{escape_html(url)}" class="btn-cta btn-large" target="_blank" rel="noopener">Get it on Gumroad →</a>'
    return '    <span class="btn-cta btn-large btn-coming-soon">Coming soon</span>'


def _gumroad_cta_card(meta: dict) -> str:
    """Gumroad CTA button for catalog cards."""
    url = meta.get("gumroad_url")
    if url:
        return f'<a href="{escape_html(url)}" class="btn-cta" target="_blank" rel="noopener">Get it on Gumroad →</a>'
    return '<span class="btn-cta btn-coming-soon">Coming soon</span>'


def _rich_description_html(meta: dict) -> str:
    """Render the plain-text Gumroad description as HTML, or fall back to static includes."""
    rich = meta.get("gumroad_description")
    if rich:
        return f'      <div class="product-plaintext">{escape_html(rich)}</div>'
    # Fallback: static "What's included" list
    return f"      <h2>What's included</h2>\n{_includes_html(meta)}"


def _gumroad_copy_block(meta: dict) -> str:
    """Collapsible block with the raw Gumroad description HTML for easy copy-paste."""
    desc = meta.get("gumroad_description")
    if not desc:
        return ""
    escaped = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return f"""    <details class="gumroad-copy-block">
      <summary>📋 Copy description for Gumroad</summary>
      <textarea readonly onclick="this.select()">{escaped}</textarea>
    </details>
"""


def build_product_page(meta: dict) -> str:
    tags_html = " ".join(f'<span class="tag">{escape_html(t)}</span>' for t in (meta.get("tags") or []))
    thumbnail_html = _thumbnail_html_detail(meta)
    cta_html = _gumroad_cta_page(meta)
    year = datetime.now().year

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape_html(meta['title'])}</title>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="icon" type="image/x-icon" href="../favicon.ico">
  <link rel="stylesheet" href="../style.css">
  <meta name="description" content="{escape_html(meta['description'])}">
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <a href="../index.html" class="site-logo" aria-label="mini-on-ai home">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 40" width="200" height="40" fill="none" aria-hidden="true">
          <rect x="0"  y="1.5" width="17" height="17" rx="4" fill="#6366F1"/>
          <rect x="20" y="1.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.35"/>
          <rect x="0"  y="21.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.6"/>
          <rect x="20" y="21.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.18"/>
          <text x="50" y="29" font-family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="22" font-weight="700" letter-spacing="-0.5" fill="currentColor">mini-on-ai</text>
        </svg>
      </a>
      <button class="dark-mode-toggle" id="darkModeToggle" title="Toggle dark mode" aria-label="Toggle dark mode">Light</button>
    </div>
  </header>

  <main class="product-detail">
{thumbnail_html}    <div class="product-tags">{_category_badge(meta)}{tags_html}</div>
    <h1>{escape_html(meta['title'])}</h1>
    <p class="product-desc-large">{escape_html(meta['description'])}</p>

    <div class="product-stats">
      <span>{escape_html(_count_label(meta))}</span>
    </div>

{cta_html}

    <section class="product-details">
{_rich_description_html(meta)}
    </section>

{_gumroad_copy_block(meta)}
  </main>

  <footer class="site-footer">
    <p>&copy; {year} mini-on-ai &nbsp;·&nbsp; <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
  </footer>

  <script>
    (function() {{
      const toggle = document.getElementById('darkModeToggle');

      function initDarkMode() {{
        const saved = localStorage.getItem('darkMode');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = saved !== null ? saved === 'true' : prefersDark;

        if (isDark) {{
          document.documentElement.classList.add('dark-mode');
          document.documentElement.classList.remove('light-mode-manual');
          toggle.textContent = 'Dark';
        }} else {{
          document.documentElement.classList.remove('dark-mode');
          document.documentElement.classList.add('light-mode-manual');
          toggle.textContent = 'Light';
        }}
      }}

      function toggleDarkMode() {{
        const isDark = !document.documentElement.classList.contains('dark-mode');
        if (isDark) {{
          document.documentElement.classList.add('dark-mode');
          document.documentElement.classList.remove('light-mode-manual');
        }} else {{
          document.documentElement.classList.remove('dark-mode');
          document.documentElement.classList.add('light-mode-manual');
        }}
        localStorage.setItem('darkMode', isDark ? 'true' : 'false');
        toggle.textContent = isDark ? 'Dark' : 'Light';
      }}

      if (toggle) {{
        toggle.addEventListener('click', toggleDarkMode);
      }}

      initDarkMode();
    }})();
  </script>
</body>
</html>
"""


CATEGORY_PLACEHOLDER_IMG = {
    "prompt-packs":      "images/placeholder-prompt-packs.svg",
    "checklist":         "images/placeholder-checklist.svg",
    "swipe-file":        "images/placeholder-swipe-file.svg",
    "mini-guide":        "images/placeholder-mini-guide.svg",
    "n8n-template":      "images/placeholder-n8n-template.svg",
    "claude-code-skill": "images/placeholder-claude-code-skill.svg",
}


def build_product_card(meta: dict) -> str:
    tags_html = " ".join(f'<span class="tag">{escape_html(t)}</span>' for t in (meta.get("tags") or []))
    thumb = meta.get("thumbnail")
    cat = meta.get("category", "prompt-packs")
    tags_attr = ",".join(meta.get("tags") or [])
    if thumb:
        thumbnail_html = f'\n        <img src="{escape_html(thumb)}" alt="{escape_html(meta["title"])}" class="product-thumbnail">'
    else:
        placeholder_src = CATEGORY_PLACEHOLDER_IMG.get(cat, "images/placeholder-prompt-packs.svg")
        thumbnail_html = f'\n        <img src="{placeholder_src}" alt="" class="product-thumbnail" aria-hidden="true">'
    cta_html = _gumroad_cta_card(meta)
    return f"""      <article class="product-card" data-category="{escape_html(cat)}" data-tags="{escape_html(tags_attr)}">{thumbnail_html}
        <div class="product-card-body">
          <div class="product-tags">{_category_badge(meta)}{tags_html}</div>
          <h2 class="product-title"><a href="products/{meta['id']}.html">{escape_html(meta['title'])}</a></h2>
          <p class="product-desc">{escape_html(meta['description'])}</p>
          <div class="product-meta">{escape_html(_count_label(meta))}</div>
          {cta_html}
        </div>
      </article>"""


def _build_filter_bar(products: list) -> str:
    """Build a filter bar HTML with category pills and counts."""
    from collections import Counter
    cat_counts = Counter(p.get("category", "prompt-packs") for p in products)
    total = len(products)

    cat_order = ["prompt-packs", "checklist", "swipe-file", "mini-guide", "n8n-template", "claude-code-skill"]
    cat_labels = {
        "prompt-packs":      "Prompt Packs",
        "checklist":         "Checklists",
        "swipe-file":        "Swipe Files",
        "mini-guide":        "Mini Guides",
        "n8n-template":      "n8n Templates",
        "claude-code-skill": "CC Skills",
    }

    btns = [f'    <button class="filter-btn active" data-filter="all">All <span class="filter-count">{total}</span></button>']
    for cat in cat_order:
        n = cat_counts.get(cat, 0)
        if n > 0:
            label = cat_labels.get(cat, cat)
            btns.append(f'    <button class="filter-btn" data-filter="cat:{cat}">{label} <span class="filter-count">{n}</span></button>')

    return "  <div class=\"filter-bar\">\n" + "\n".join(btns) + "\n  </div>"


def _filter_js() -> str:
    """Return the catalog filter JavaScript."""
    return """  <script>
    (function() {
      var filterBtns = document.querySelectorAll('.filter-btn');
      var cards = document.querySelectorAll('.product-card');
      var emptyMsg = document.getElementById('catalogEmpty');
      var countEl = document.getElementById('catalogCount');
      var totalCount = cards.length;

      function applyFilter(filter) {
        var visible = 0;
        cards.forEach(function(card) {
          var show = false;
          if (filter === 'all') {
            show = true;
          } else if (filter.indexOf('cat:') === 0) {
            show = card.dataset.category === filter.slice(4);
          }
          if (show) {
            card.classList.remove('filter-hidden');
            visible++;
          } else {
            card.classList.add('filter-hidden');
          }
        });
        if (emptyMsg) emptyMsg.classList.toggle('visible', visible === 0);
        if (countEl) countEl.textContent = visible === totalCount
          ? totalCount + ' product' + (totalCount !== 1 ? 's' : '') + ' available'
          : visible + ' of ' + totalCount + ' products';
      }

      filterBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
          filterBtns.forEach(function(b) { b.classList.remove('active'); });
          btn.classList.add('active');
          applyFilter(btn.dataset.filter);
        });
      });
    })();
  </script>"""


def rebuild_index(catalog: dict) -> str:
    products = catalog["products"]
    count = len(products)
    cards = "\n".join(build_product_card(p) for p in products)
    filter_bar = _build_filter_bar(products)
    year = datetime.now().year

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>mini-on-ai — AI-Powered Digital Products</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="stylesheet" href="style.css">
  <meta name="description" content="Prompt packs, checklists, swipe files, mini guides, n8n automation templates, and Claude Code skills. Discover AI-powered digital products.">
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <a href="index.html" class="site-logo" aria-label="mini-on-ai home">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 40" width="200" height="40" fill="none" aria-hidden="true">
          <rect x="0"  y="1.5" width="17" height="17" rx="4" fill="#6366F1"/>
          <rect x="20" y="1.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.35"/>
          <rect x="0"  y="21.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.6"/>
          <rect x="20" y="21.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.18"/>
          <text x="50" y="29" font-family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="22" font-weight="700" letter-spacing="-0.5" fill="currentColor">mini-on-ai</text>
        </svg>
      </a>
      <div style="display: flex; gap: 16px; align-items: center;">
        <span class="product-count">{count} product{'s' if count != 1 else ''}</span>
        <button class="dark-mode-toggle" id="darkModeToggle" title="Toggle dark mode" aria-label="Toggle dark mode">Light</button>
      </div>
    </div>
  </header>

  <section class="hero">
    <div class="hero-text">
      <h1>AI-powered digital products</h1>
      <p>Prompt packs, checklists, swipe files, mini guides, n8n automation templates, and Claude Code skills — crafted with AI, ready to use.</p>
    </div>
    <img src="images/hero.svg" class="hero-illustration" alt="">
  </section>

  <main class="catalog">
    <div class="catalog-header">
      <p class="catalog-subtitle" id="catalogCount">{count} product{'s' if count != 1 else ''} available</p>
{filter_bar}
    </div>

    <div class="product-grid">
{cards}
      <div class="catalog-empty" id="catalogEmpty">
        <p>No products in this category yet.</p>
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <p>&copy; {year} mini-on-ai &nbsp;·&nbsp; <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
  </footer>

  <script>
    (function() {{
      const toggle = document.getElementById('darkModeToggle');

      function initDarkMode() {{
        const saved = localStorage.getItem('darkMode');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = saved !== null ? saved === 'true' : prefersDark;

        if (isDark) {{
          document.documentElement.classList.add('dark-mode');
          document.documentElement.classList.remove('light-mode-manual');
          toggle.textContent = 'Dark';
        }} else {{
          document.documentElement.classList.remove('dark-mode');
          document.documentElement.classList.add('light-mode-manual');
          toggle.textContent = 'Light';
        }}
      }}

      function toggleDarkMode() {{
        const isDark = !document.documentElement.classList.contains('dark-mode');
        if (isDark) {{
          document.documentElement.classList.add('dark-mode');
          document.documentElement.classList.remove('light-mode-manual');
        }} else {{
          document.documentElement.classList.remove('dark-mode');
          document.documentElement.classList.add('light-mode-manual');
        }}
        localStorage.setItem('darkMode', isDark ? 'true' : 'false');
        toggle.textContent = isDark ? 'Dark' : 'Light';
      }}

      if (toggle) {{
        toggle.addEventListener('click', toggleDarkMode);
      }}

      initDarkMode();
    }})();
  </script>
{_filter_js()}
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
        "category": meta.get("category", "prompt-packs"),
        "tags": meta.get("tags", []),
        "item_count": _item_count(meta),
        "prompt_count": meta.get("prompt_count") or meta.get("item_count", 0),
        "created_at": meta["created_at"],
        "package_path": meta["package_path"],
        "site_path": f"site/products/{pid}.html",
        "thumbnail": meta.get("thumbnail"),
        "gumroad_url": meta.get("gumroad_url"),
        "price": meta.get("price"),
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


def rebuild_all() -> None:
    """Rebuild every published product page and the index from current meta.json files."""
    products_dir = ROOT / "products"
    catalog = {"products": []}
    metas = []
    for d in sorted(products_dir.iterdir()):
        meta_path = d / "meta.json"
        if meta_path.exists():
            with open(meta_path) as f:
                m = json.load(f)
            if m.get("status") in ("published", "packaged"):
                metas.append((m.get("created_at", ""), m))

    metas.sort(key=lambda x: x[0], reverse=True)  # newest first

    for _, meta in metas:
        pid = meta["id"]
        product_page = build_product_page(meta)
        write_file(f"site/products/{pid}.html", product_page)
        log("update-site", f"Rebuilt site/products/{pid}.html")

        n = _item_count(meta)
        catalog["products"].append({
            "id": meta["id"],
            "title": meta["title"],
            "description": meta["description"],
            "category": meta.get("category", "prompt-packs"),
            "tags": meta.get("tags", []),
            "item_count": n,
            "prompt_count": meta.get("prompt_count", n),
            "status": meta.get("status"),
            "created_at": meta.get("created_at"),
            "site_path": f"site/products/{pid}.html",
            "gumroad_url": meta.get("gumroad_url"),
            "thumbnail": meta.get("thumbnail"),
        })

    write_json("data/product-catalog.json", catalog)
    index_html = rebuild_index(catalog)
    write_file("site/index.html", index_html)
    log("update-site", f"Rebuilt index with {len(catalog['products'])} products.")


def main():
    parser = argparse.ArgumentParser(description="Add product to showcase site")
    parser.add_argument("--id", default=None, help="Product ID")
    parser.add_argument("--rebuild-all", action="store_true", help="Rebuild every published product page and index")
    args = parser.parse_args()
    if args.rebuild_all:
        rebuild_all()
    else:
        update_site(args.id)


if __name__ == "__main__":
    main()
