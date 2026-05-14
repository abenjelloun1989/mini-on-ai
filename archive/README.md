# Archive

Products and pages pulled from the public vitrine on 2026-05-14 to focus
mini-on-ai.com on its one proven category: **Claude Code skills & prompt packs**.

Nothing here is deleted — everything is restorable.

## What's archived

### Products (34)
Moved out of `data/product-catalog.json` because their categories never produced revenue:

| Category   | Count |
|------------|-------|
| mini-guide | 15    |
| n8n-template | 8   |
| swipe-file | 6     |
| checklist  | 5     |

- `product-catalog-archived.json` — the 34 removed catalog entries
- `products/{id}/` — the 34 product source folders (was `products/{id}/`)
- `site-products/{id}.html` — 34 rendered product pages + 1 pre-existing orphan page (was `site/products/{id}.html`)

### Pages (2)
- `pages/build.html` — the "Build Your Own" Stripe page. Removed from the vitrine (zero sales, diluted the pitch). **The `mini-on-ai-generate` Cloudflare Worker is still deployed** — only the site links were removed.
- `pages/services.html` — the freelance "AI automation expert" page. Removed (no revenue, conflicts with the anonymity constraint).

## Gumroad note

Gumroad listings for archived products were **left live** — they're independent of the site catalog and still findable on Gumroad directly.

## How to restore

### Restore one product
1. Move its entry from `product-catalog-archived.json` back into `data/product-catalog.json` (under `products`).
2. `mv archive/products/{id} products/{id}`
3. `python3 scripts/update_site.py --rebuild-all` (regenerates its page + sitemap)

### Restore Build Your Own / Services
1. `mv archive/pages/build.html site/build.html` (and/or `services.html`)
2. Re-add the nav links + tool cards in `scripts/update_site.py` (`_site_header()`, the `tools-section`, footer) and the static tool pages (`clauseguard.html`, `invoiceguard.html`, `ats.html`).
3. `python3 scripts/update_site.py --rebuild-all`

### Restore everything
Merge `product-catalog-archived.json` back into `data/product-catalog.json`, move all `archive/products/*` back to `products/`, restore the two pages, rebuild.
