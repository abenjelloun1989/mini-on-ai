# Roadmap

## Completed ✅

### V1 — Foundation (2026-03-12)
Full pipeline: trend scan → rank → generate → package → site → Telegram

### V2 — Live Factory (2026-03-12)
- GitHub Pages deployment with auto-deploy via GitHub Actions
- Telegram approval gate (Go / No Go buttons)
- Continuous daemon replaces 9am cron
- Non-commercial license + README

---

## Upcoming

### M11 — Publisher Step
Auto-publish each product to distribution platforms without manual work.
The factory produces, the publisher distributes.

**Phase A — Free download platforms**
- Gumroad (free tier): create product via API, upload zip, set price $0
- Ko-fi / Payhip: alternatives if Gumroad API is restrictive

**Phase B — Community distribution**
- Reddit auto-posting via PRAW (Python Reddit API Wrapper)
  Post to relevant subreddits (r/ChatGPT, r/AItools, r/freelance, etc.)
  Format: "Free prompt pack for X — no signup, direct download"

**Phase C — SEO**
- Add structured data (JSON-LD) to product pages
- Auto-submit sitemap to Google Search Console

### M12 — Real Trend Scanning
Replace Claude generating ideas from thin air with actual trend data.

Options in order of effort:
1. pytrends — Google Trends Python library, free, no API key
2. Reddit scraping — r/ChatGPT, r/artificial, r/freelance rising topics
3. Playwright scraping — Exploding Topics, Product Hunt, trending searches
4. Twitter/X — trending hashtags (requires paid API access)

Feed real trending topics to Claude as context — much higher quality ideas.

### M13 — Product Category Expansion
Beyond prompt packs:
- Checklists (markdown / PDF)
- Templates (Notion, Google Docs, email)
- Swipe files (copywriting hooks, subject lines)
- Mini-guides (1-page PDF on a specific topic)

Pipeline already supports categories — needs new generation logic per type.

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
