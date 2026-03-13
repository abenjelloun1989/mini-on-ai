# Current State

Last updated: 2026-03-13

## Status: V2 — Continuous factory with Gumroad publishing + branded vitrine

## What Works

### Pipeline (fully operational — 8 stages)
- `run_daemon.py` — continuous loop, restarts after each cycle automatically
- `run_pipeline.py` — full pipeline with Telegram approval gate
- Stages: trend-scan → idea-rank → **approval** → generate → package → update-site → **publish-gumroad** → git push → telegram report
- Products auto-committed and pushed to GitHub after each run

### Approval Gate
- After idea ranking, pipeline sends a Telegram message with ✅ Go / ❌ No Go buttons
- Pipeline blocks until user approves or rejects
- Rejection marks idea as skipped, daemon loops to next idea

### Products Published (3)
- ATS-Optimized Resume Bullet Rewriter by Job Description — 25 prompts
- Shopify Product Description Packs for E-Commerce — 25 prompts
- Meeting Notes to Action Items Fast — 25 prompts

### Site (Vitrine v2 ✅)
- Live at https://abenjelloun1989.github.io/mini-on-ai
- CNAME set to mini-on-ai.com (ready once domain is purchased)
- Pure showcase — no downloads on site, CTAs link to Gumroad
- Hero section with unDraw illustration + bold headline
- "Coming soon" state on cards until Gumroad URL is set
- Contact email `hello@mini-on-ai.com` in footer (Zoho setup pending)
- Auto-deployed via GitHub Actions on every push to main

### Brand Identity ✅
- Logo: SVG wordmark with indigo geometric mark (`site/logo.svg`)
- Color: `#6366F1` indigo brand throughout
- Font: Inter / system font stack

### Gumroad Publisher (M11 ✅)
- `scripts/publish_product.py` — creates paid listings via Gumroad API v2
- Uploads package.zip, stores `gumroad_url` + `gumroad_product_id` in meta.json
- Pipeline runs it automatically after update-site (non-fatal if token missing)
- Requires: `GUMROAD_API_TOKEN` + `PRODUCT_PRICE_CENTS` in `.env`

### Trend Scanning (M12 ✅)
- Google Trends (pytrends) integrated — rising queries from last 7 days (US)
- 15-seed audience rotation for diverse idea generation
- Duplicate title avoidance across sessions

### Product Categories (M13 ✅)
- prompt-packs, checklist, swipe-file, mini-guide, n8n-template all supported
- trend_scan assigns category per idea; generate_product dispatches accordingly
- Site cards show colored category badges per category

### Telegram Bot
- Running via launchd (com.mini-on-ai.bot)
- Commands: /help /status /products /ideas /run /go /nogo /holdon /resume /projectphases
- Inline button support for approval gate

### Infrastructure
- Git repo: https://github.com/abenjelloun1989/mini-on-ai
- License: All Rights Reserved
- Python 3.9, anthropic + python-dotenv + requests

## What Does NOT Exist Yet
- Gumroad token not yet configured (add GUMROAD_API_TOKEN to .env)
- Domain mini-on-ai.com not yet purchased (manual step at Namecheap)
- Email hello@mini-on-ai.com not yet active (Zoho setup pending)
- Reddit auto-posting (M11 Phase B)
- Analytics / download tracking (M14)
- Email list capture (M15)
