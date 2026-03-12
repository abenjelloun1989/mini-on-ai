# Current State

Last updated: 2026-03-12

## Status: V2 — Continuous factory live on GitHub Pages

## What Works

### Pipeline (fully operational)
- `run_daemon.py` — continuous loop, restarts after each cycle automatically
- `run_pipeline.py` — full 7-stage pipeline with Telegram approval gate
- Stages: trend-scan → idea-rank → **approval** → generate → package → update-site → git push → telegram report
- Products auto-committed and pushed to GitHub after each run

### Approval Gate
- After idea ranking, pipeline sends a Telegram message with ✅ Go / ❌ No Go buttons
- Pipeline blocks until user approves or rejects
- Rejection marks idea as skipped, daemon loops to next idea

### Products Published (2)
- Meeting Notes to Action Items Fast — 25 prompts
- Shopify Product Description Packs for E-Commerce — 30 prompts (in progress)

### Site
- Live at https://abenjelloun1989.github.io/mini-on-ai
- Auto-deployed via GitHub Actions on every push to main
- Downloads working (package.zip served from site/products/{id}/)

### Telegram Bot
- Running as background process (pid 9077)
- Commands: /help /status /products /ideas /run /go /nogo
- Inline button support for approval gate

### Infrastructure
- Git repo: https://github.com/abenjelloun1989/mini-on-ai
- License: All Rights Reserved
- Python 3.9, anthropic + python-dotenv

## What Does NOT Exist Yet
- Publisher step (auto-publishing to Gumroad, Reddit, etc.)
- Real trend scraping (currently Claude generates ideas from thin air)
- Analytics / download tracking
- Multiple product categories (only prompt packs)
