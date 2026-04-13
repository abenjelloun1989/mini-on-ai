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
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

CF_TOKEN = os.getenv("CF_ANALYTICS_TOKEN", "97d7df5dc9454ccab192e901157799b6")
# Brevo subscribe endpoint — set this to a proxy URL (e.g. Cloudflare Worker) that holds
# the API key server-side. Never embed the Brevo API key directly in static HTML.
BREVO_SUBSCRIBE_URL = os.getenv("BREVO_SUBSCRIBE_URL", "")

def _cf_analytics() -> str:
    if not CF_TOKEN:
        return ""
    return f"<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{\"token\": \"{CF_TOKEN}\"}}'></script><!-- End Cloudflare Web Analytics -->"

def _brevo_form_js() -> str:
    """Wire email forms to a server-side proxy endpoint.
    The proxy (e.g. a Cloudflare Worker) holds the Brevo API key — never embed it in HTML."""
    if not BREVO_SUBSCRIBE_URL:
        return ""
    return f"""<script>
function wireBrevoForm(sel) {{
  var form = document.querySelector(sel);
  if (!form) return;
  form.addEventListener('submit', function(e) {{
    e.preventDefault();
    var email = form.querySelector('input[type=email]').value;
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = '...';
    fetch('{BREVO_SUBSCRIBE_URL}', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{email: email}})
    }}).then(function(r) {{
      if (r.ok) {{
        form.innerHTML = '<p style="color:var(--brand);font-weight:600;margin:0">✅ You\\'re on the list!</p>';
      }} else {{
        btn.disabled = false; btn.textContent = 'Try again';
      }}
    }}).catch(function() {{ btn.disabled = false; btn.textContent = 'Try again'; }});
  }});
}}
document.addEventListener('DOMContentLoaded', function() {{
  wireBrevoForm('.email-capture-form');
  wireBrevoForm('.newsletter-form');
}});
</script>"""

from lib.utils import read_json, write_json, write_file, ROOT, log

CONTACT_EMAIL = "hello@mini-on-ai.com"
SITE_URL = os.getenv("SITE_URL", "https://mini-on-ai.com").rstrip("/")


def _og_tags_product(meta: dict) -> str:
    title = escape_html(meta.get("title", ""))
    desc  = escape_html(meta.get("description", ""))
    pid   = meta.get("id", "")
    url   = f"{SITE_URL}/products/{pid}.html"
    img   = f"{SITE_URL}/images/og-default.svg"
    return (
        f'  <meta property="og:type" content="product">\n'
        f'  <meta property="og:title" content="{title}">\n'
        f'  <meta property="og:description" content="{desc}">\n'
        f'  <meta property="og:url" content="{url}">\n'
        f'  <meta property="og:image" content="{img}">\n'
        f'  <meta name="twitter:card" content="summary_large_image">\n'
        f'  <meta name="twitter:title" content="{title}">\n'
        f'  <meta name="twitter:description" content="{desc}">\n'
        f'  <link rel="canonical" href="{url}">'
    )


def _og_tags_index() -> str:
    title = "mini-on-ai — Claude Code Skills & AI Workflows for Engineering Teams"
    desc  = "Claude Code skills and n8n automation workflows crafted by a seasoned software engineer. Deploy in minutes, save hours every week."
    img   = f"{SITE_URL}/images/og-default.svg"
    return (
        f'  <meta property="og:type" content="website">\n'
        f'  <meta property="og:title" content="{title}">\n'
        f'  <meta property="og:description" content="{desc}">\n'
        f'  <meta property="og:url" content="{SITE_URL}/">\n'
        f'  <meta property="og:image" content="{img}">\n'
        f'  <meta name="twitter:card" content="summary_large_image">\n'
        f'  <meta name="twitter:title" content="{title}">\n'
        f'  <meta name="twitter:description" content="{desc}">\n'
        f'  <link rel="canonical" href="{SITE_URL}/">'
    )


def _json_ld_product(meta: dict) -> str:
    import json as _json
    pid   = meta.get("id", "")
    url   = f"{SITE_URL}/products/{pid}.html"
    price = meta.get("price")
    gurl  = meta.get("gumroad_url") or url
    data: dict = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": meta.get("title", ""),
        "description": meta.get("description", ""),
        "url": url,
        "brand": {"@type": "Brand", "name": "mini-on-ai"},
    }
    # Always emit offers when product has a Gumroad URL or an explicit price.
    # Free (PWYW) products use price "0". This satisfies Google's Product schema requirement.
    if gurl or price is not None:
        offer_price = "0" if (meta.get("is_free") or price is None) else str(price // 100)
        data["offers"] = {
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": offer_price,
            "availability": "https://schema.org/InStock",
            "url": gurl or url,
        }
    return f'  <script type="application/ld+json">\n  {_json.dumps(data, ensure_ascii=False)}\n  </script>'


def write_sitemap(catalog: dict) -> None:
    """Generate site/sitemap.xml from products + blog posts."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{SITE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{SITE_URL}/blog/index.html</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>',
    ]
    for p in catalog.get("products", []):
        pid     = p.get("id", "")
        lastmod = (p.get("created_at") or "")[:10]
        loc     = f"{SITE_URL}/products/{pid}.html"
        lines.append(
            f'  <url><loc>{loc}</loc>'
            + (f'<lastmod>{lastmod}</lastmod>' if lastmod else "")
            + '<priority>0.8</priority></url>'
        )
    # Include blog posts
    try:
        blog_data = read_json("data/blog-posts.json")
        for post in blog_data.get("posts", []):
            slug    = post.get("slug", "")
            lastmod = (post.get("created_at") or "")[:10]
            loc     = f"{SITE_URL}/blog/{slug}.html"
            lines.append(
                f'  <url><loc>{loc}</loc>'
                + (f'<lastmod>{lastmod}</lastmod>' if lastmod else "")
                + '<priority>0.6</priority></url>'
            )
    except Exception:
        pass
    lines.append("</urlset>")
    total = len(catalog.get("products", [])) + 1
    write_file("site/sitemap.xml", "\n".join(lines) + "\n")
    log("update-site", f"Wrote site/sitemap.xml ({total} URLs)")
    write_file("site/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    log("update-site", "Wrote site/robots.txt")

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
        "{n} ready-to-use SKILL.md file(s) (drop into `skills/`, no setup required)",
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
    cat = meta.get("category", "prompt-packs")
    cat_key = cat if cat in ("prompt-packs", "checklist", "swipe-file", "mini-guide", "n8n-template") else "prompt-packs"
    src = f"../images/placeholder-{cat_key}.svg"
    return f'  <img src="{src}" alt="" class="product-thumbnail-detail" aria-hidden="true" style="width:100%;border-radius:14px;margin-bottom:32px;aspect-ratio:16/9;object-fit:cover;">\n'


def _utm_url(base_url: str, medium: str, campaign: str) -> str:
    """Append UTM parameters to a Gumroad URL for attribution tracking."""
    sep = "&" if "?" in base_url else "?"
    return f"{base_url}{sep}utm_source=site&utm_medium={medium}&utm_campaign={campaign}"


def _gumroad_cta_page(meta: dict) -> str:
    """Gumroad CTA button for the product detail page."""
    url = meta.get("gumroad_url")
    if not url:
        return '    <span class="btn-cta btn-large btn-coming-soon">Coming soon</span>'
    price = meta.get("price")
    is_free = meta.get("is_free")
    if is_free or price == 0:
        label = "Get it free →"
    elif price:
        label = f"Get it — ${price // 100} →"
    else:
        label = "Get it on Gumroad →"
    tracked_url = _utm_url(url, "product_page", meta.get("id", "unknown"))
    return f'    <a href="{escape_html(tracked_url)}" class="btn-cta btn-large" target="_blank" rel="noopener">{label}</a>'


def _gumroad_cta_card(meta: dict) -> str:
    """Gumroad CTA button for catalog cards."""
    url = meta.get("gumroad_url")
    if not url:
        return '<span class="btn-cta btn-coming-soon">Coming soon</span>'
    price = meta.get("price")
    is_free = meta.get("is_free")
    if is_free or price == 0:
        label = "Get it free →"
    elif price:
        label = f"Get it — ${price // 100} →"
    else:
        label = "Get it on Gumroad →"
    tracked_url = _utm_url(url, "product_card", meta.get("id", "unknown"))
    return f'<a href="{escape_html(tracked_url)}" class="btn-cta" target="_blank" rel="noopener">{label}</a>'


def _render_gumroad_description(text: str) -> str:
    """Convert plain gumroad description to readable HTML for the product page."""
    from urllib.parse import urlparse
    lines = text.splitlines()
    html_parts = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            html_parts.append("")
            i += 1
            continue

        # Section header (ends with ":" and not a bullet)
        if stripped.endswith(":") and not stripped.startswith("—"):
            html_parts.append(f'<h3 class="desc-section-header">{escape_html(stripped)}</h3>')
            i += 1
            # Collect following bullet lines into a <ul>
            bullets = []
            while i < len(lines) and lines[i].strip().startswith("—"):
                bullets.append(lines[i].strip()[1:].strip())
                i += 1
            if bullets:
                items = "\n".join(f"<li>{escape_html(b)}</li>" for b in bullets)
                html_parts.append(f"<ul>\n{items}\n</ul>")
            continue

        # Standalone bullet
        if stripped.startswith("—"):
            bullets = []
            while i < len(lines) and lines[i].strip().startswith("—"):
                bullets.append(lines[i].strip()[1:].strip())
                i += 1
            items = "\n".join(f"<li>{escape_html(b)}</li>" for b in bullets)
            html_parts.append(f"<ul>\n{items}\n</ul>")
            continue

        # Footer link line
        if "mini-on-ai.com" in stripped:
            linked = escape_html(stripped).replace(
                "mini-on-ai.com",
                '<a href="https://mini-on-ai.com">mini-on-ai.com</a>'
            )
            html_parts.append(f'<p class="desc-footer">{linked}</p>')
            i += 1
            continue

        # Regular paragraph
        html_parts.append(f"<p>{escape_html(stripped)}</p>")
        i += 1

    return "\n".join(p for p in html_parts if p != "")


def _rich_description_html(meta: dict) -> str:
    """Render the plain-text Gumroad description as HTML, or fall back to static includes."""
    rich = meta.get("gumroad_description")
    if rich:
        rendered = _render_gumroad_description(rich)
        return f'      <div class="product-description-body">\n{rendered}\n      </div>'
    # Fallback: static "What's included" list
    return f"      <h2>What's included</h2>\n{_includes_html(meta)}"


def _gumroad_copy_block(meta: dict) -> str:
    return ""  # Moved to Telegram notification


def build_product_page(meta: dict) -> str:
    cat = meta.get("category", "prompt-packs")
    cat_color = CATEGORY_COLORS.get(cat, "#6366F1")
    cat_label = cat.replace("-", " ")
    tags = meta.get("tags") or []
    tags_html = " ".join(f'<span class="tag" data-tag="{escape_html(t)}">{escape_html(t)}</span>' for t in tags)
    year = datetime.now().year
    og_tags = _og_tags_product(meta)
    json_ld = _json_ld_product(meta)

    price = meta.get("price")
    price_badge = f'<span class="product-detail-price">${price // 100}</span>' if price else ""

    gumroad_url = meta.get("gumroad_url", "")
    if gumroad_url:
        tracked_gumroad = _utm_url(gumroad_url, "product_page", meta.get("id", "unknown"))
        cta_html = f'<a href="{escape_html(tracked_gumroad)}" class="product-detail-cta" target="_blank" rel="noopener">Get it now →</a>'
    else:
        cta_html = '<span class="product-detail-cta" style="opacity:0.5;cursor:default">Coming soon</span>'

    count_label = escape_html(_count_label(meta))
    header = _site_header(back_href="../index.html", back_label="← Products", prefix="../")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape_html(meta['title'])} — mini-on-ai</title>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="icon" type="image/x-icon" href="../favicon.ico">
  <link rel="stylesheet" href="../style.css">
  <meta name="description" content="{escape_html(meta['description'])}">
{og_tags}
{json_ld}
</head>
<body>
{header}

  <main class="product-detail-page">
    <p class="product-breadcrumb"><a href="../index.html">mini-on-ai</a> / <a href="../index.html">Products</a></p>
    <span class="product-detail-cat" style="color:{cat_color}">{escape_html(cat_label)}</span>
    <h1 class="product-detail-title">{escape_html(meta['title'])}</h1>
    {price_badge}
    <div class="product-detail-tags">{tags_html}</div>
    <p class="product-detail-desc">{escape_html(meta['description'])}</p>
    <p style="font-size:13px;color:var(--text-muted);margin-bottom:24px">{count_label}</p>
    {cta_html}

    <div class="product-gumroad-desc">
{_rich_description_html(meta)}
    </div>
  </main>

  <footer class="site-footer">
    <p>&copy; {year} mini-on-ai &nbsp;·&nbsp; <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
  </footer>

{_dark_mode_js()}
{_brevo_form_js()}
{_cf_analytics()}
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


def _product_persona(meta: dict) -> str:
    """Derive audience persona from category and tags."""
    cat = meta.get("category", "prompt-packs")
    tags = meta.get("tags") or []
    if cat == "claude-code-skill":
        return "engineering"
    if cat == "n8n-template":
        return "automation"
    if cat == "mini-guide":
        return "automation" if "n8n" in tags else "non-tech"
    return "non-tech"


CATEGORY_COLORS = {
    "prompt-packs":      "#6366F1",
    "checklist":         "#10B981",
    "mini-guide":        "#8B5CF6",
    "swipe-file":        "#F59E0B",
    "n8n-template":      "#EF4444",
    "claude-code-skill": "#06B6D4",
}

SVG_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 40" width="200" height="40" fill="none" aria-hidden="true">
          <rect x="0"  y="1.5" width="17" height="17" rx="4" fill="#6366F1"/>
          <rect x="20" y="1.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.35"/>
          <rect x="0"  y="21.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.6"/>
          <rect x="20" y="21.5" width="17" height="17" rx="4" fill="#6366F1" opacity="0.18"/>
          <text x="50" y="29" font-family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="22" font-weight="700" letter-spacing="-0.5" fill="currentColor">mini-on-ai</text>
        </svg>"""


def _dark_mode_js() -> str:
    """Dark-default theme toggle JS. Adds/removes light-mode class on body."""
    return """  <script>
    (function() {
      var toggle = document.getElementById('darkModeToggle');
      var stored = localStorage.getItem('theme');
      if (stored !== 'light' && stored !== 'dark') { stored = null; }
      if (stored === 'light') {
        document.body.classList.add('light-mode');
        if (toggle) toggle.textContent = '☀ Light';
      } else {
        if (toggle) toggle.textContent = '☾ Dark';
      }
      if (toggle) {
        toggle.addEventListener('click', function() {
          var isLight = document.body.classList.toggle('light-mode');
          localStorage.setItem('theme', isLight ? 'light' : 'dark');
          toggle.textContent = isLight ? '☀ Light' : '☾ Dark';
        });
      }
    })();
  </script>"""


def _site_header(back_href: str = None, back_label: str = "← Products", prefix: str = "") -> str:
    """Frosted glass header. prefix is '' for index, '../' for product pages, '../' for blog posts."""
    nav_items = ""
    if back_href:
        nav_items += f'        <a href="{back_href}" class="nav-link">{back_label}</a>\n'
    else:
        nav_items += f'        <a href="{prefix}index.html" class="nav-link">Products</a>\n'
        nav_items += f'        <a href="{prefix}blog/index.html" class="nav-link">Blog</a>\n'
        nav_items += f'        <a href="{prefix}services.html" class="nav-link">Services</a>\n'
        nav_items += f'        <a href="{prefix}build.html" class="nav-link-cta">✦ Build your own</a>\n'
    nav_items += '        <button class="dark-mode-toggle" id="darkModeToggle" aria-label="Toggle theme">☾ Dark</button>'
    return f"""  <header class="site-header">
    <div class="site-header-inner">
      <a href="{prefix}index.html" class="site-logo" aria-label="mini-on-ai home">
        {SVG_LOGO}
      </a>
      <nav style="display:flex;gap:16px;align-items:center;">
{nav_items}
      </nav>
    </div>
  </header>"""


def build_product_card(meta: dict) -> str:
    tags = meta.get("tags") or []
    cat = meta.get("category", "prompt-packs")
    tags_attr = ",".join(tags)
    persona = _product_persona(meta)
    cat_color = CATEGORY_COLORS.get(cat, "#6366F1")

    # Badges
    free_attr = ' data-free="true"' if meta.get("is_free") else ""
    badges = ""
    if meta.get("is_free"):
        badges += '<span class="badge-free">Free</span>'
    created = meta.get("created_at", "")
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if (datetime.now(timezone.utc) - dt) < timedelta(days=14):
                badges += '<span class="badge-new">New</span>'
        except Exception:
            pass

    # Price
    price = meta.get("price")
    price_html = f'<span class="card-price">${price // 100}</span>' if price else ""

    # Tags row
    tags_html = " ".join(f'<span class="tag" data-tag="{escape_html(t)}">{escape_html(t)}</span>' for t in tags[:4])

    # CTA
    gumroad_url = meta.get("gumroad_url", "")
    if gumroad_url:
        tracked_gumroad = _utm_url(gumroad_url, "product_card", meta.get("id", "unknown"))
        cta = f'<a href="{escape_html(tracked_gumroad)}" class="card-cta" target="_blank" rel="noopener">Get it →</a>'
    else:
        cta = '<span class="card-cta" style="opacity:0.4;cursor:default">Coming soon</span>'

    cat_label = cat.replace("-", " ")

    return f"""      <article class="product-card" data-category="{escape_html(cat)}" data-persona="{persona}" data-tags="{escape_html(tags_attr)}"{free_attr} style="--cat-color:{cat_color}">
        <div class="card-inner">
          <div class="card-top">
            <span class="card-category">{escape_html(cat_label)}</span>
            {price_html}
          </div>
          <h2 class="card-title"><a href="products/{meta['id']}.html">{escape_html(meta['title'])}</a></h2>
          <p class="card-desc">{escape_html(meta['description'])}</p>
          <div class="card-bottom">
            <div class="card-tags">{badges}{tags_html}</div>
            {cta}
          </div>
        </div>
      </article>"""


def _build_filter_bar(products: list) -> str:
    """Build a filter bar HTML with persona pills and counts."""
    total = len(products)
    persona_counts = {"engineering": 0, "automation": 0, "non-tech": 0}
    for p in products:
        persona = _product_persona(p)
        if persona in persona_counts:
            persona_counts[persona] += 1
    free_count = sum(1 for p in products if p.get("is_free"))

    btns = [f'    <button class="filter-btn active" data-filter="all">All <span class="filter-count">{total}</span></button>']
    if persona_counts["engineering"]:
        btns.append(f'    <button class="filter-btn" data-filter="persona:engineering">For Engineering Teams <span class="filter-count">{persona_counts["engineering"]}</span></button>')
    if persona_counts["automation"]:
        btns.append(f'    <button class="filter-btn" data-filter="persona:automation">For Automation Builders <span class="filter-count">{persona_counts["automation"]}</span></button>')
    if persona_counts["non-tech"]:
        btns.append(f'    <button class="filter-btn" data-filter="persona:non-tech">For Non-Tech Pros <span class="filter-count">{persona_counts["non-tech"]}</span></button>')
    if free_count:
        btns.append(f'    <button class="filter-btn" data-filter="free">Free <span class="filter-count">{free_count}</span></button>')

    return "  <div class=\"filter-bar\">\n" + "\n".join(btns) + "\n  </div>"


def _filter_js() -> str:
    """Return the catalog filter + search JavaScript."""
    return """  <script>
    (function() {
      var filterBtns = document.querySelectorAll('.filter-btn');
      var cards = document.querySelectorAll('.product-card');
      var emptyMsg = document.getElementById('catalogEmpty');
      var countEl = document.getElementById('catalogCount');
      var searchInput = document.getElementById('productSearch');
      var searchClear = document.getElementById('searchClear');
      var totalCount = Array.from(cards).filter(function(c) { return c.dataset.visible !== 'false'; }).length;

      var activeFilter = 'all';
      var searchQuery = '';

      function cardMatchesFilter(card) {
        if (activeFilter === 'all') return true;
        if (activeFilter === 'free') return card.dataset.free === 'true';
        if (activeFilter.indexOf('persona:') === 0) return card.dataset.persona === activeFilter.slice(8);
        return true;
      }

      function cardMatchesSearch(card) {
        if (!searchQuery) return true;
        var q = searchQuery.toLowerCase();
        var title = (card.querySelector('.product-title') || {}).textContent || '';
        var desc = (card.querySelector('.product-desc') || {}).textContent || '';
        var tags = card.dataset.tags || '';
        return title.toLowerCase().indexOf(q) >= 0
          || desc.toLowerCase().indexOf(q) >= 0
          || tags.toLowerCase().indexOf(q) >= 0;
      }

      function applyFilters() {
        var visible = 0;
        cards.forEach(function(card) {
          var show = cardMatchesFilter(card) && cardMatchesSearch(card);
          card.classList.toggle('filter-hidden', !show);
          if (show) visible++;
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
          activeFilter = btn.dataset.filter;
          applyFilters();
        });
      });

      if (searchInput) {
        searchInput.addEventListener('input', function() {
          searchQuery = searchInput.value.trim();
          if (searchClear) searchClear.style.display = searchQuery ? 'block' : 'none';
          applyFilters();
        });
      }

      if (searchClear) {
        searchClear.addEventListener('click', function() {
          searchInput.value = '';
          searchQuery = '';
          searchClear.style.display = 'none';
          searchInput.focus();
          applyFilters();
        });
      }

      document.querySelectorAll('.tag[data-tag]').forEach(function(tag) {
        tag.addEventListener('click', function() {
          if (searchInput) {
            searchInput.value = tag.dataset.tag;
            searchQuery = tag.dataset.tag;
            if (searchClear) searchClear.style.display = 'block';
            applyFilters();
            searchInput.focus();
          }
        });
      });
    })();
  </script>"""


def rebuild_index(catalog: dict) -> str:
    # Live products first, coming-soon last
    _live = [p for p in catalog["products"] if p.get("gumroad_url")]
    _soon = [p for p in catalog["products"] if not p.get("gumroad_url")]
    products = _live + _soon
    count = len(products)
    cards = "\n".join(build_product_card(p) for p in products)
    filter_bar = _build_filter_bar(products)
    year = datetime.now().year
    og_tags = _og_tags_index()
    header = _site_header()

    # Featured flagship: highest-priced product with a Gumroad URL
    _flagship = max((p for p in _live if p.get("price")), key=lambda p: p["price"], default=None)
    if _flagship:
        _fp_title = escape_html(_flagship["title"])
        _fp_desc = escape_html(_flagship.get("description", ""))
        _fp_price = _flagship["price"] // 100
        _fp_url = escape_html(f'products/{_flagship["id"]}.html')
        featured_section = f"""
  <section class="featured-product">
    <div class="featured-inner">
      <span class="featured-label">Featured</span>
      <h2 class="featured-title">{_fp_title}</h2>
      <p class="featured-desc">{_fp_desc}</p>
      <a href="{_fp_url}" class="btn-cta btn-featured">Read more — ${_fp_price} →</a>
    </div>
  </section>
"""
    else:
        featured_section = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>mini-on-ai — AI Tools, Prompt Packs &amp; Automation Workflows</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="stylesheet" href="style.css">
  <meta name="description" content="Prompt packs, Claude Code skills, n8n templates, and AI-powered tools for freelancers and professionals. Deploy in minutes, save hours every week.">
  <meta name="google-site-verification" content="_bUSLc4yVdu115P3SlUFsKIZ15YTewr70wL6yFRxHGs">
{og_tags}
</head>
<body>
{header}

  <div class="launch-bar">
    April 2026 launch — {count} products live. <a href="build.html">Try a free preview →</a>
  </div>

  <section class="hero">
    <div class="hero-inner">
      <h1 class="hero-headline">AI tools &amp; workflows —<br>built for professionals who ship</h1>
      <p class="hero-sub">Prompt packs, Claude Code skills, n8n templates, and AI-powered tools. Drop one in, save hours this week.</p>
      <div class="hero-cta-group">
        <a href="build.html" class="hero-cta-primary">✦ Build your own — free</a>
        <a href="#catalog" class="hero-cta-secondary">Browse {count} products</a>
      </div>
      <div class="hero-stats">
        <div class="hero-stat">
          <div class="hero-stat-num">{count}</div>
          <div class="hero-stat-label">Products</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-num">5 min</div>
          <div class="hero-stat-label">To deploy</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-num">Weekly</div>
          <div class="hero-stat-label">New drops</div>
        </div>
      </div>
    </div>
  </section>

  <section class="tools-strip">
    <div class="tools-strip-inner">
      <a href="build.html" class="tool-card">
        <span class="tool-card-icon">✦</span>
        <div class="tool-card-body">
          <strong class="tool-card-title">Build Your Own</strong>
          <p class="tool-card-desc">Describe a use case, get a custom AI product in 30 seconds.</p>
        </div>
        <span class="tool-card-cta">Try free →</span>
      </a>
      <a href="ats.html" class="tool-card">
        <span class="tool-card-icon">◈</span>
        <div class="tool-card-body">
          <strong class="tool-card-title">ATS Resume Checker</strong>
          <p class="tool-card-desc">Instant ATS score, keyword gaps, and optimization tips — free.</p>
        </div>
        <span class="tool-card-cta">Check score →</span>
      </a>
      <a href="clauseguard.html" class="tool-card">
        <span class="tool-card-icon">🛡</span>
        <div class="tool-card-body">
          <strong class="tool-card-title">ClauseGuard</strong>
          <p class="tool-card-desc">Analyze contracts for red flags in seconds. Free Chrome extension.</p>
        </div>
        <span class="tool-card-cta">Add to Chrome →</span>
      </a>
    </div>
  </section>

{featured_section}
  <main class="catalog" id="catalog">
    <div class="catalog-header">
      <p class="catalog-subtitle" id="catalogCount">{count} product{'s' if count != 1 else ''} available</p>
      <div class="search-wrap">
        <input type="search" id="productSearch" class="search-input" placeholder="Search products…" autocomplete="off">
        <button class="search-clear" id="searchClear" aria-label="Clear search">×</button>
      </div>
{filter_bar}
    </div>

    <div class="product-grid">
{cards}
      <div class="catalog-empty" id="catalogEmpty">
        <p>No products match your search.</p>
      </div>
    </div>
  </main>

  <div class="build-banner">
    <div class="build-banner-text">
      <h2>Didn't find what you need?</h2>
      <p>Describe your use case and get a custom product generated in 30 seconds.</p>
    </div>
    <a href="build.html" class="build-banner-cta">✦ Build your own →</a>
  </div>

  <section class="newsletter-cta">
    <div class="newsletter-cta-inner">
      <p class="newsletter-label">Newsletter</p>
      <h2 class="newsletter-headline">One AI Workflow a Week</h2>
      <p class="newsletter-desc">One practical AI workflow every Friday — no coding required.</p>
      <form class="newsletter-form" action="#" method="get">
        <input type="email" name="email" placeholder="your@email.com" required>
        <button type="submit">Subscribe free</button>
      </form>
    </div>
  </section>

  <footer class="site-footer">
    <p>&copy; {year} mini-on-ai &nbsp;·&nbsp; <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
    <p class="site-footer-tools"><a href="build.html">Build Your Own</a> &nbsp;·&nbsp; <a href="ats.html">ATS Resume Checker</a> &nbsp;·&nbsp; <a href="clauseguard.html">ClauseGuard</a></p>
  </footer>

{_dark_mode_js()}
{_filter_js()}
{_brevo_form_js()}
{_cf_analytics()}
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOG
# ─────────────────────────────────────────────────────────────────────────────

def _markdown_to_html(md: str) -> str:
    """Convert a limited subset of Markdown to HTML for blog posts."""
    import re as _re
    lines = md.split("\n")
    html_lines = []
    in_ul = False

    for line in lines:
        # H2 / H3
        if line.startswith("### "):
            if in_ul: html_lines.append("</ul>"); in_ul = False
            html_lines.append(f"<h3>{escape_html(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            if in_ul: html_lines.append("</ul>"); in_ul = False
            html_lines.append(f"<h2>{escape_html(line[3:])}</h2>")
            continue
        # Bullet list
        if line.startswith("- ") or line.startswith("* "):
            if not in_ul: html_lines.append("<ul>"); in_ul = True
            html_lines.append(f"<li>{escape_html(line[2:])}</li>")
            continue
        # End list on blank line
        if not line.strip():
            if in_ul: html_lines.append("</ul>"); in_ul = False
            html_lines.append("")
            continue
        # Regular paragraph
        if in_ul: html_lines.append("</ul>"); in_ul = False
        html_lines.append(line)

    if in_ul:
        html_lines.append("</ul>")

    body = "\n".join(html_lines)

    # Inline: **bold**
    body = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    # Inline: *italic*
    body = _re.sub(r"\*(.+?)\*", r"<em>\1</em>", body)
    # Inline: [text](url)
    body = _re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', body)
    # Inline: `code`
    body = _re.sub(r"`([^`]+)`", r"<code>\1</code>", body)

    # Wrap orphan text lines in <p> (lines that don't start with < and aren't empty)
    result = []
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("<"):
            result.append(f"<p>{stripped}</p>")
        else:
            result.append(line)

    return "\n".join(result)


def build_blog_post_page(post: dict) -> str:
    title   = escape_html(post.get("title", ""))
    excerpt = escape_html(post.get("excerpt", ""))
    slug    = post.get("slug", "")
    url     = f"{SITE_URL}/blog/{slug}.html"
    date    = (post.get("created_at") or "")[:10]
    body_html = _markdown_to_html(post.get("body_markdown", ""))
    year    = datetime.now().year
    header  = _site_header(back_href="index.html", back_label="← All posts", prefix="../")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — mini-on-ai</title>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="icon" type="image/x-icon" href="../favicon.ico">
  <link rel="stylesheet" href="../style.css">
  <meta name="description" content="{excerpt}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{excerpt}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE_URL}/images/og-default.svg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{url}">
</head>
<body>
{header}

  <main class="blog-post-page">
    <article class="blog-post">
      <header class="blog-post-header">
        <p class="blog-post-date">{date}</p>
        <h1>{title}</h1>
        <p class="blog-post-excerpt">{excerpt}</p>
      </header>
      <div class="blog-post-content">
{body_html}
      </div>
    </article>
  </main>

  <footer class="site-footer">
    <p>&copy; {year} mini-on-ai &nbsp;·&nbsp; <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
  </footer>

{_dark_mode_js()}
{_cf_analytics()}
</body>
</html>"""


def rebuild_blog_index(posts: list) -> str:
    """Build site/blog/index.html listing all blog posts."""
    year = datetime.now().year
    header = _site_header(back_href="../index.html", back_label="← Products", prefix="../")
    cards = ""
    for post in sorted(posts, key=lambda p: p.get("created_at", ""), reverse=True):
        title   = escape_html(post.get("title", ""))
        excerpt = escape_html(post.get("excerpt", ""))
        slug    = post.get("slug", "")
        date    = (post.get("created_at") or "")[:10]
        cards += f"""    <a href="{slug}.html" class="blog-card">
      <p class="blog-card-date">{date}</p>
      <h2 class="blog-card-title">{title}</h2>
      <p class="blog-card-excerpt">{excerpt}</p>
    </a>
"""
    if not cards:
        cards = '    <p class="catalog-empty-msg">No posts yet.</p>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog — mini-on-ai</title>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="icon" type="image/x-icon" href="../favicon.ico">
  <link rel="stylesheet" href="../style.css">
  <meta name="description" content="Practical guides on Claude Code, n8n automation, and AI workflows for developers and makers.">
  <meta property="og:title" content="Blog — mini-on-ai">
  <meta property="og:url" content="{SITE_URL}/blog/index.html">
  <link rel="canonical" href="{SITE_URL}/blog/index.html">
</head>
<body>
{header}

  <main class="blog-listing-page">
    <div class="blog-listing-header">
      <h1>Blog</h1>
      <p>Practical guides on Claude Code, n8n, and AI automation.</p>
    </div>
    <div class="blog-grid">
{cards}    </div>
  </main>

  <footer class="site-footer">
    <p>&copy; {year} mini-on-ai &nbsp;·&nbsp; <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
  </footer>

{_dark_mode_js()}
{_cf_analytics()}
</body>
</html>"""


def update_blog(post: dict) -> str:
    """Save a blog post page, update blog-posts.json, rebuild index. Returns post URL."""
    import json as _json

    Path(ROOT / "site/blog").mkdir(parents=True, exist_ok=True)

    slug = post["slug"]
    page_html = build_blog_post_page(post)
    write_file(f"site/blog/{slug}.html", page_html)
    log("update-site", f"Created site/blog/{slug}.html")

    # Update blog-posts.json
    blog_data_path = ROOT / "data/blog-posts.json"
    if blog_data_path.exists():
        with open(blog_data_path) as f:
            blog_data = _json.load(f)
    else:
        blog_data = {"posts": []}

    existing_idx = next((i for i, p in enumerate(blog_data["posts"]) if p["id"] == post["id"]), None)
    entry = {
        "id":         post["id"],
        "title":      post["title"],
        "slug":       slug,
        "excerpt":    post["excerpt"],
        "topic":      post.get("topic", ""),
        "created_at": post["created_at"],
    }
    if existing_idx is not None:
        blog_data["posts"][existing_idx] = entry
    else:
        blog_data["posts"].insert(0, entry)

    with open(blog_data_path, "w") as f:
        _json.dump(blog_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Rebuild blog index
    index_html = rebuild_blog_index(blog_data["posts"])
    write_file("site/blog/index.html", index_html)
    log("update-site", f"Rebuilt site/blog/index.html ({len(blog_data['posts'])} posts)")

    # Extend sitemap
    catalog = read_json("data/product-catalog.json")
    write_sitemap(catalog)

    url = f"{SITE_URL}/blog/{slug}.html"
    return url


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
        "is_free": meta.get("is_free"),
    }

    existing_idx = next((i for i, p in enumerate(catalog["products"]) if p["id"] == pid), None)
    if existing_idx is not None:
        catalog["products"][existing_idx] = catalog_entry
    else:
        catalog["products"].insert(0, catalog_entry)  # newest first

    write_json("data/product-catalog.json", catalog)

    # Rebuild index + sitemap
    index_html = rebuild_index(catalog)
    write_file("site/index.html", index_html)
    write_sitemap(catalog)
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
            "price": meta.get("price"),
            "is_free": meta.get("is_free"),
        })

    write_json("data/product-catalog.json", catalog)
    index_html = rebuild_index(catalog)
    write_file("site/index.html", index_html)
    write_sitemap(catalog)
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
