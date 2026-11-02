# mini-on-ai — Claude Operating Instructions

## What This Project Is

mini-on-ai is an AI-powered digital product factory running on a Mac mini.
It continuously generates, packages, and publishes small digital products to a public showcase website at `mini-on-ai.com`.

Products are sold via Gumroad ($9–$49). The vitrine is focused on Claude Code skills & prompt packs (see `archive/README.md`). The "Build Your Own" page was pulled from the site but its Worker (`mini-on-ai-generate`) stays deployed.

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
    ├── _headers                 ← NOT in force on GitHub Pages (see Site Hosting)
    ├── _redirects               ← NOT in force on GitHub Pages (see Site Hosting)
    ├── blog/
    └── products/{id}.html
```

## Product Categories

The public vitrine was focused on 2026-05-14 down to the two AI categories
that match the only proven funnel. See `archive/README.md`.

**Active (on the site):**
- `claude-code-skill` — Claude Code skill configuration pack
- `prompt-packs` — 20–30 ready-to-use prompts

**Archived (in `archive/`, restorable, not deleted):**
- `checklist`, `swipe-file`, `mini-guide`, `n8n-template`

`Build Your Own` (`build.html`) and `Services` (`services.html`) were also
pulled from the vitrine — files in `archive/pages/`, the
`mini-on-ai-generate` Worker stays deployed.

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
This regenerates all product pages, index, and blog index. Then a push to `main` that touches `site/**` deploys to GitHub Pages.

## Site Hosting

`mini-on-ai.com` is served by **GitHub Pages**, not Cloudflare Pages. Verified 2026-11-02:

- **Deploy:** `.github/workflows/deploy.yml` publishes `site/` on pushes to `main` that touch `site/**`. Custom domain comes from `site/CNAME`.
- **DNS:** Namecheap BasicDNS (`dns1/dns2.registrar-servers.com`). Apex A records point to GitHub's `185.199.108-111.153`; `www` is a CNAME to `abenjelloun1989.github.io`, which redirects to the apex. The domain is not a Cloudflare zone, so Cloudflare rules (transform rules, Workers routes) cannot apply to it.
- **`site/_headers` and `site/_redirects` do nothing.** They are Cloudflare Pages files; GitHub Pages serves them as plain downloads. No CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` or HSTS reaches browsers, and the archived URLs in `_redirects` return 404 rather than 301. The CSPs in `_headers` have never been enforced, so do not treat them as protection or as tested.
- **`_headers` cannot go live as written.** It would break the site: see the warning below.
- **Page-level protection available today:** `<meta http-equiv="Content-Security-Policy">` and `<meta name="referrer">` work. `frame-ancestors`, `X-Frame-Options`, `X-Content-Type-Options` and HSTS cannot be set from a page.

Before moving to Cloudflare Pages or enforcing any CSP, fix `_headers`. Cloudflare Pages merges every matching rule and comma-joins repeated headers, so `/*` and `/f1` send two CSPs and browsers enforce both. Without `! Content-Security-Policy` in the specific rule, the strict `/*` policy blocks inline scripts on `/f1`. Inline `on*` handlers on `f1.html` and `f1/dashboard.html`, and the inline scripts on the 45 pages that have them, also need `'unsafe-inline'` or a refactor, and `connect-src` needs `https://cloudflareinsights.com` for the analytics beacon.

Changing DNS or nameservers requires the user's explicit approval.

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
- **Deployment:** GitHub Pages via GitHub Actions (push to `main` touching `site/**` → auto-deploy; see Site Hosting). Workers managed via Cloudflare dashboard, not wrangler CLI.
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
