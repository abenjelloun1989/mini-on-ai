# mini-on-ai — Claude Operating Instructions

## What This Project Is

mini-on-ai is an AI-powered digital product factory running on a Mac mini.
It continuously generates, packages, and publishes small digital products to a public showcase website at `mini-on-ai.com`.

Products are sold via Gumroad ($9–$49). Visitors can also generate a custom product on-demand via the "Build Your Own" page (Stripe, $9).

## Quick Context Recovery

The memory system is the authoritative state source — read these in order:
1. `~/.claude/projects/-Users-minion-Dev-mini-on-factory/memory/factory_state.md` — products, commands, infrastructure
2. `~/.claude/projects/-Users-minion-Dev-mini-on-factory/memory/distribution_state.md` — channel status
3. `~/.claude/projects/-Users-minion-Dev-mini-on-factory/memory/scripts_manifest.md` — all scripts

Do NOT rely on `docs/current-state.md` — it is stale.

## Project Structure

```
mini-on-factory/
├── CLAUDE.md                    ← you are here
├── data/
│   ├── product-catalog.json     ← all published products
│   ├── idea-backlog.json        ← idea candidates
│   ├── blog-posts.json          ← published blog posts
│   └── pipeline-log.json        ← run history
├── scripts/                     ← all Python pipeline scripts
│   └── lib/                     ← shared utils, claude_cli wrapper
├── worker/
│   ├── generate.js              ← CF Worker: Build Your Own (generate/checkout/download)
│   └── subscribe.js             ← CF Worker: Brevo email subscribe proxy
├── clauseguard/                 ← Chrome extension: AI contract analyzer (v1.3.1)
│   ├── popup/                   ← Extension UI (HTML/CSS/JS)
│   ├── store-assets/            ← CWS listing copy, screenshots
│   └── worker/                  ← Cloudflare Worker backend
├── invoiceguard/                ← Chrome extension: Gmail invoice tracker (v1.1.1)
│   ├── popup/
│   ├── store-assets/
│   └── worker/                  ← Cloudflare Worker backend
├── jobguard/                    ← Chrome extension: AI job posting analyzer (v1.0.1)
│   ├── popup/
│   ├── store-assets/
│   └── worker/                  ← Cloudflare Worker backend
├── _shared/                     ← Shared JS/CSS synced to all 3 extensions
├── skills/                      ← skill specifications
├── products/                    ← one folder per product
│   └── {id}/
│       ├── meta.json
│       ├── assets/
│       └── package.zip
└── site/                        ← static showcase website
    ├── index.html               ← rebuilt by update_site.py
    ├── style.css                ← Dark Premium design system
    ├── build.html               ← Build Your Own page
    ├── _headers                 ← Cloudflare Pages security headers (CSP etc.)
    ├── blog/
    └── products/{id}.html
```

## Product Categories (all active)

- `prompt-packs` — 20–30 ready-to-use prompts
- `checklist` — structured action/decision list
- `swipe-file` — copy-ready examples
- `mini-guide` — concise practitioner guide
- `n8n-template` — ready-to-import automation workflow
- `claude-code-skill` — Claude Code skill configuration pack

## Pipeline

All scripts are Python 3. Orchestrated by `scripts/run_pipeline.py`.

```
run_pipeline.py
  → trend_scan.py       writes to data/idea-backlog.json
  → idea_rank.py        marks one idea as selected:true
  → generate_product.py writes to products/{id}/assets/
  → package_product.py  creates products/{id}/package.zip
  → update_site.py      updates site/ and data/product-catalog.json
  → telegram_notify.py  sends Telegram message
```

Triggered via `/run [seed]` in Telegram or the background daemon.

## Site Rebuilding

After any change to product data or templates:
```bash
python3 scripts/update_site.py --rebuild-all
```
This regenerates all product pages, index, and blog index. Then `git push` deploys to Cloudflare Pages.

## Cloudflare Workers

Two workers deployed (not in this repo, managed in Cloudflare dashboard):
- `worker/generate.js` — Build Your Own: generate (Anthropic Haiku) → Stripe checkout → ZIP download. Deployed as `mini-on-ai-generate`.
- `worker/subscribe.js` — Brevo subscribe proxy. Deployed as `mini-on-ai-subscribe`.

Both use `ALLOWED_ORIGIN = "https://mini-on-ai.com"` CORS. Secrets in CF environment.

## Chrome Extensions

Three Chrome extensions, separate from the pipeline-generated product catalog:

| Extension | Version | Status | CWS URL |
|---|---|---|---|
| **ClauseGuard** — AI contract analyzer | v1.3.3 | Live | [CWS link](https://chromewebstore.google.com/detail/clauseguard-ai-contract-n/nknbofmcikmpifeopelgngnhdcajffdl) |
| **InvoiceGuard** — Gmail invoice tracker | v1.1.1 | Live | [CWS link](https://chrome.google.com/webstore/detail/lppombokbcoafaahfhnjmckhnkbmhalp) |
| **JobGuard** — AI job posting analyzer | v1.0.1 | Pending CWS review | — |

Workers:
- ClauseGuard: `clauseguard-api.kirozdormu.workers.dev`
- InvoiceGuard: `invoiceguard-api.kirozdormu.workers.dev`
- JobGuard: `jobguard-api.kirozdormu.workers.dev`

All three have dedicated landing pages (`clauseguard.html`, `invoiceguard.html`, `jobguard.html`) and appear in the Tools & Services section on the homepage. Shared code lives in `_shared/` (synced via `scripts/sync_shared.py`).

## Extension Assets & ZIPs

When generating a submission ZIP or any store asset (screenshots, marquee tiles, promo images) for a Chrome extension, always save it to the extension's `store-assets/` folder:
- `clauseguard/store-assets/clauseguard-X.X.X.zip`
- `invoiceguard/store-assets/invoiceguard-X.X.X.zip`
- `jobguard/store-assets/jobguard-X.X.X.zip`

Never drop ZIPs or assets in the repo root.

## Conventions

- Product IDs: `{prefix}-{kebab-title}-{YYYYMMDD}` e.g. `prompts-marketing-hooks-20260312`
- All pipeline scripts are Python 3, no build step required
- Environment variables: see `.env.example`
- Never commit `.env` file
- Never explain the factory on the public website — products only
- After any edit: commit + push immediately (user preference)

## Pricing/Value Updates

When updating prices or key values across a site:
1. Run `grep -rn "OLD_VALUE" .` across the whole repo first — including HTML meta tags, OG tags, JSON-LD, markdown docs, and comments
2. List every hit before touching anything
3. Update all of them
4. Run `grep -rn "OLD_VALUE" .` again to confirm zero remaining matches
Never report a value change as done until the final grep returns no results.

## Environment & Tooling

- **Claude Code install:** Homebrew (`brew install claude-code`). Check current version with `brew list --versions claude-code` before suggesting upgrades — don't assume it's outdated.
- **Remote/phone access:** Telegram bot only. `/remote-control` is VSCode-only and does not work in this setup.
- **Deployment:** Cloudflare Pages (git push → auto-deploy). Workers managed via Cloudflare dashboard, not wrangler CLI.
- **Python:** Python 3, no virtualenv — scripts run directly with `python3`.
- **Node:** Not used for the pipeline. Only present for PDF.js lib bundled in Chrome extensions.

## Active Workflow Skills

Read these at the start of the relevant task:

- `skills/pattern-detect.md` — at the start of any new planning session: scan git log for repeated patterns, propose up to 2 new skills
- `skills/sales-counsel.md` — when user asks about sales/distribution: fetch live data and give concrete next actions
- `skills/chrome-extension-playbook.md` — when starting any new Chrome extension: full playbook for stack, security, monetization, UX, landing page, CWS listing, and distribution

## Environment Variables Required

```
ANTHROPIC_API_KEY=         # Claude API
TELEGRAM_BOT_TOKEN=        # Telegram bot
TELEGRAM_CHAT_ID=          # Your Telegram chat
SITE_URL=                  # https://mini-on-ai.com
BREVO_SUBSCRIBE_URL=       # CF Worker URL for email subscribe
GUMROAD_API_TOKEN=         # Gumroad API
```
