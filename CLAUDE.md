# mini-on-ai — Claude Operating Instructions

## What This Project Is

mini-on-ai is an AI-powered digital product factory running on a Mac mini.
It continuously generates, packages, and publishes small digital products to a public showcase website.

This is NOT a SaaS. There are no users, no auth, no payments.
The output is a catalog of downloadable digital products.

## Quick Context Recovery

Read these files in order to recover full project state:
1. `docs/current-state.md` — what exists and works right now
2. `docs/next-steps.md` — the immediate next actions
3. `docs/architecture.md` — stable design decisions
4. `data/product-catalog.json` — all published products
5. `data/idea-backlog.json` — candidate ideas

## Project Structure

```
mini-on-factory/
├── CLAUDE.md                    ← you are here
├── docs/
│   ├── architecture.md          ← design decisions
│   ├── roadmap.md               ← milestones
│   ├── current-state.md         ← ALWAYS READ THIS FIRST
│   └── next-steps.md            ← ALWAYS READ THIS SECOND
├── data/
│   ├── product-catalog.json     ← published products
│   ├── idea-backlog.json        ← idea candidates
│   └── pipeline-log.json        ← run history
├── skills/                      ← skill specifications
├── scripts/                     ← runnable pipeline scripts
├── products/                    ← one folder per product
│   └── {id}/
│       ├── meta.json
│       ├── assets/
│       └── package.zip
└── site/                        ← static showcase website
    ├── index.html
    ├── style.css
    └── products/{id}.html
```

## V1 Product Category

**Prompt Packs only.** Do not generate other product types in V1.

Each prompt pack contains:
- `prompts.md` — human-readable prompts (20–30 prompts per pack)
- `prompts.json` — machine-readable array
- `README.md` — title, use-case, how-to-use

## V1 Pipeline

```
run-pipeline.js
  → trend-scan.js       writes to data/idea-backlog.json
  → idea-rank.js        marks one idea as selected:true
  → generate-product.js writes to products/{id}/assets/
  → package-product.js  creates products/{id}/package.zip
  → update-site.js      updates site/ and data/product-catalog.json
  → telegram-notify.js  sends Telegram message
```

## Conventions

- Product IDs: `{category}-{kebab-title}-{YYYYMMDD}` e.g. `prompts-marketing-hooks-20260312`
- All scripts are Node.js, no build step required
- Environment variables: see `.env.example`
- Never commit `.env` file
- Never explain the factory on the public website — products only

## After Every Session

Update these two files before ending:
- `docs/current-state.md`
- `docs/next-steps.md`

## Environment Variables Required

```
ANTHROPIC_API_KEY=     # Claude API
TELEGRAM_BOT_TOKEN=    # Telegram bot
TELEGRAM_CHAT_ID=      # Your Telegram chat
SITE_URL=              # Public URL of showcase site
```
