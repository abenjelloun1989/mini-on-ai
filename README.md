# mini-on-ai

![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-red)

An AI-powered digital product factory running on a Mac mini. It scans Reddit for unmet needs, generates a matching product (prompt pack, checklist, swipe file, etc.), publishes it to Gumroad, and sends a reply to the original thread — fully automated with a Telegram approval gate.

**Live site:** [mini-on-ai.com](https://mini-on-ai.com)

---

## How it works

### Demand-driven mode (Reddit)
1. Scans target subreddits for posts expressing a specific need
2. Claude Haiku scores each post (0–100) and proposes a product brief
3. Up to 10 candidates arrive in Telegram as a non-blocking batch
4. Tap **Build it** → factory generates, packages, and publishes to Gumroad
5. A copy-paste Reddit reply is delivered to Telegram

### Idea-driven mode (trend scan)
1. Claude generates 10 product ideas from trending topics
2. Ideas are ranked and the best one surfaces as a Telegram approval request
3. Tap **Go** → same generate → package → publish pipeline runs
4. Telegram report with product link, duration, and API cost

---

## Product categories

| Category | Description |
|---|---|
| `prompt-packs` | 20–30 ready-to-use prompts |
| `checklist` | Structured decision / action list |
| `swipe-file` | Copy-ready examples and templates |
| `mini-guide` | Concise practitioner guide |
| `n8n-template` | Ready-to-import automation workflow |
| `claude-code-skill` | Full configuration guide for a Claude Code skill |

---

## Telegram commands

| Command | Description |
|---|---|
| `/run` | Generate a new product (e.g. `/run marketing`) |
| `/reddit` | Scan Reddit, propose up to 10 products |
| `/go` | Approve pending idea → build it |
| `/skip` | Skip pending idea |
| `/pause` | Pause the factory daemon |
| `/resume` | Resume the factory daemon |
| `/status` | Last run, product count, API costs |
| `/products` | All published products with links |

---

## Setup

```bash
git clone https://github.com/abenjelloun1989/mini-on-ai
cd mini-on-ai
pip3 install anthropic python-dotenv

cp .env.example .env
# Fill in ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_OWNER_ID, GUMROAD_API_TOKEN
```

Run manually:
```bash
python3 scripts/run_pipeline.py --seed "marketing"
python3 scripts/run_pipeline.py --reddit-mode
python3 scripts/run_pipeline.py --reddit-build <post_id>
```

Start the Telegram bot:
```bash
python3 scripts/telegram_bot.py
```

---

## Project structure

```
mini-on-factory/
├── scripts/
│   ├── run_pipeline.py       — full pipeline orchestrator
│   ├── telegram_bot.py       — Telegram command interface
│   ├── reddit_scan.py        — pullpush.io scanner + Claude Haiku assessor
│   ├── reddit_pipeline.py    — demand-driven pipeline (Reddit → build)
│   ├── trend_scan.py         — idea generation from trending topics
│   ├── idea_rank.py          — score and select best idea
│   ├── generate_product.py   — generate product content via Claude
│   ├── package_product.py    — zip product assets
│   ├── update_site.py        — add product to showcase site
│   ├── publish_product.py    — publish to Gumroad
│   └── telegram_notify.py    — send notifications + approval requests
├── data/
│   ├── product-catalog.json  — published products
│   ├── idea-backlog.json     — idea candidates
│   ├── reddit-queue.json     — Reddit posts found + build status
│   └── pipeline-log.json     — run history
├── products/                 — one folder per product (assets + zip)
└── site/                     — static showcase website (GitHub Pages)
```

---

## Stack

- Python 3 + Anthropic Claude API (Sonnet for generation, Haiku for assessment)
- [pullpush.io](https://pullpush.io) — free Reddit archive API, no auth required
- Gumroad API for publishing
- Static HTML site deployed to GitHub Pages
- Telegram bot for control and approval

---

## License

All rights reserved. See [LICENSE](LICENSE) for details.
