# Next Steps

Last updated: 2026-03-12

## Now — Grow the catalog

The daemon is running. Just approve ideas via Telegram until you have 8-10 products.
Good seeds to feed the pipeline:
  /run marketing
  /run freelancing
  /run writing
  /run coding
  /run productivity

Target: 8-10 products before tackling distribution.

## Next — M11: Publisher Step

Build a `publish_product.py` script that runs after `update_site.py` in the pipeline.

**Step 1: Gumroad**
- Register for a free Gumroad account + get API key
- Script calls Gumroad API to create a free product listing
- Uploads the zip, sets name/description from meta.json
- Stores the Gumroad URL back in meta.json

**Step 2: Reddit**
- Install PRAW: pip install praw
- Create a Reddit app (script type) at reddit.com/prefs/apps
- Script posts to 1-2 relevant subreddits per product
- Uses a natural title + link to GitHub Pages download

**Step 3: Wire into pipeline**
- Add `publish_product` as stage 6 in run_pipeline.py
- Telegram report includes all published URLs

## Then — M12: Real Trend Scanning

Replace fake idea generation with real data:
- pip install pytrends
- Scrape Google Trends for rising topics in "AI tools", "productivity", "freelance"
- Feed trending keywords as seed to Claude instead of generating blind
