# Roadmap

## Completed ✅

### V1 — Foundation (2026-03-12)
Full pipeline: trend scan → rank → generate → package → site → Telegram

### V2 — Live Factory (2026-03-12)
- GitHub Pages deployment with auto-deploy via GitHub Actions
- Telegram approval gate (Go / No Go buttons)
- Continuous daemon replaces 9am cron
- Non-commercial license + README

### M12 — Real Trend Scanning (2026-03-12)
- pytrends (Google Trends) integration — rising queries last 7 days, US
- 15-seed audience rotation for diverse idea generation
- Duplicate title avoidance across backlog

---

## Upcoming

### M11 — Publisher Step
Auto-publish each product to distribution platforms without manual work.
The factory produces, the publisher distributes.

**Phase A — Paid marketplaces** (from original brainstorm)
- Gumroad: create listing via API, upload zip, set price
- Lemon Squeezy: alternative with better EU VAT handling
- Etsy: digital downloads marketplace, broader reach
- Automation template marketplaces (e.g. Zapier, Make marketplace)

**Phase B — Community distribution**
- Reddit auto-posting via PRAW (Python Reddit API Wrapper)
  Post to relevant subreddits (r/ChatGPT, r/AItools, r/freelance, etc.)
  Format: "Free prompt pack for X — no signup, direct download"

**Phase C — SEO**
- Add structured data (JSON-LD) to product pages
- Auto-submit sitemap to Google Search Console

### M13 — Product Category Expansion
Beyond prompt packs (from original brainstorm):
- **Automation templates** — ready-to-use workflow scripts/configs
- **Notion templates** — structured workspace setups
- **Datasets** — curated lists, reference data, swipe files
- **Checklists** — markdown / printable PDF
- **Mini-guides** — 1-page PDF on a specific topic
- **Small utilities or scripts** — lightweight tools

Each type needs its own generation logic and product page layout.
Pipeline category field already in place — extend `generate_product.py` per type.

### M14 — Analytics
Know what is being downloaded.
- GitHub Pages has no native download analytics
- Options: Cloudflare proxy (free), Plausible, or a tiny redirect counter script
- Goal: which products get most downloads — feed this back into idea ranking

### M15 — Email List
Convert downloaders into an audience you own.
- Embed a free Beehiiv or Kit signup on product pages
- "Get notified when new packs drop"
- No selling — just an owned distribution channel

---

## Full Vision

  [Mac mini — continuous]
          |
  Trend scan (real web data: Google Trends, Reddit)
          |
  Idea proposed to owner via Telegram (Go / No Go)
          | Go
  Generate + Package product
          |
  Publish to own site (GitHub Pages)
    + Publish to Gumroad (free listing)
    + Post to Reddit (targeted subreddit)
          |
  Telegram report with links to all published locations
