# How I Built an AI Product Factory on a Mac mini

*A candid build-in-public guide — architecture, code, mistakes, and lessons.*

---

## The Idea

I wanted passive income from digital products without spending 80% of my time on content creation. Most "passive income" advice ignores the brutal truth: creating products is slow, distribution is hard, and most solo creators burn out before seeing results.

So I asked a different question: **what if a machine made the products?**

The result is mini-on-ai — a pipeline running on a Mac mini that scans for demand, generates digital products using Claude, packages them, publishes them to a showcase website, and notifies me on Telegram. Fully automated from idea to published product.

This guide is the full honest breakdown: what I built, how it works, what failed, and how you can replicate it.

---

## What It Produces

The factory currently generates six types of digital products:

- **Prompt packs** — 20–30 curated prompts for a specific use case
- **Checklists** — step-by-step decision frameworks
- **Swipe files** — curated examples and templates
- **Mini guides** — focused how-to documents
- **n8n workflow templates** — importable automation workflows
- **Claude Code skills** — `.md` skill files for Claude's Projects feature

All priced at $19 on Gumroad. Products are fully AI-generated but reviewed by me before publishing (there's a Telegram approval gate before anything goes live).

---

## The Stack

Everything runs on a single Mac mini (M1, 8GB RAM). No cloud servers, no containers, no build pipeline.

| Component | Tool | Cost |
|---|---|---|
| Product generation | Claude API (Sonnet + Haiku) | ~$0.05–0.20/product |
| Showcase website | Static HTML, hosted on Cloudflare Pages | Free |
| Sales platform | Gumroad | 10% fee on sales |
| Notifications | Telegram Bot API | Free |
| Version control | GitHub | Free |
| Language | Python 3.9 | Free |
| Email capture | Brevo (free tier) + Cloudflare Worker | Free |

Total fixed cost: $0/month (variable: Claude API per run).

---

## Pipeline Architecture

The pipeline runs as a single Python script (`run_pipeline.py`) that calls six stages in sequence:

```
trend-scan → idea-rank → [approval gate] → generate → package → publish
```

### Stage 1: Trend Scan (`trend_scan.py`)

Scans Reddit (via PullPush.io, no auth required) and curated subreddits for pain points. Looks for posts with phrases like "I wish there was a tool that..." or "anyone have a template for...". Scores each hit by upvotes, recency, and keyword relevance. Writes candidates to `data/idea-backlog.json`.

Subreddits monitored: `r/n8n`, `r/automation`, `r/freelance`, `r/learnprogramming`, `r/SideProject`, `r/productivity`, and 12 others.

### Stage 2: Idea Rank (`idea_rank.py`)

Reads the backlog and uses Claude Haiku to score each idea on:
- **Demand signal** (how many people asked for this?)
- **Producibility** (can this be a prompt pack / checklist / guide?)
- **Differentiation** (is there already something obvious like this?)

Marks the highest-scoring un-produced idea as `selected: true`.

### Stage 3: Approval Gate

Before generating, the pipeline sends me a Telegram message: idea title, description, and category. Two buttons: ✅ Go / ❌ No Go. The pipeline blocks (polls `data/approval-state.json` every 10 seconds) for up to 48 hours.

This is the one manual step I kept intentionally. Quality control matters. In ~119 pipeline runs, I rejected 63 ideas.

### Stage 4: Generate Product (`generate_product.py`)

The actual generation. One or more Claude API calls (Sonnet for quality, Haiku for cheap stuff) produce the product content. Examples:

**Prompt pack**: single API call, returns a JSON array of 20 prompts with title + body + use-case for each.

**Claude Code skills pack**: 6 API calls — one to define 5 skill structures, then one per skill to write the full `SKILL.md` file. Each skill is ~300–500 words.

**n8n template**: one call that returns a complete n8n-importable JSON workflow with node descriptions and setup instructions.

Output goes to `products/{id}/assets/`.

The same call also generates a Gumroad sales description using a separate prompt that produces persuasive copy with section headers and bullet points.

### Stage 5: Package (`package_product.py`)

Zips the assets folder to `products/{id}/package.zip`. Writes `meta.json` with title, description, category, price, item count, and created_at.

### Stage 6: Update Site (`update_site.py`)

Generates:
1. A product detail page at `site/products/{id}.html`
2. Updates the catalog JSON (`data/product-catalog.json`)
3. Rebuilds `site/index.html` from scratch
4. Regenerates `sitemap.xml`
5. Commits and pushes to GitHub → Cloudflare Pages picks up the change automatically

The site is entirely static HTML. No React, no Next.js, no build step. Raw HTML templates in Python f-strings. Fast, simple, deployable anywhere.

### Telegram Notification

After a successful run, a Telegram message includes:
- Product title + category
- Gumroad copy (formatted for easy copy-paste)
- Tweet draft with community hashtags
- Buttons to draft/regenerate the tweet

---

## The Telegram Bot

The bot is the control panel. Key commands:

| Command | What it does |
|---|---|
| `/run` | Start a pipeline run (optional `--seed keyword`) |
| `/status` | Show pipeline state + API cost today |
| `/tweet list` | List products needing a tweet |
| `/tweet N` | Get tweet draft for product N |
| `/missing list` | Products not yet on Gumroad |
| `/missing N` | Full Gumroad listing instructions for product N |
| `/gumroad N` | Get copy-paste Gumroad description |
| `/blog` | Generate + publish an SEO blog post |

The bot runs as a `launchd` daemon, auto-starts on boot, restarts on crash.

---

## What Worked

**The approval gate.** Keeping one human review step means I'm not publishing garbage. The factory generates ideas I'd never think of, but I still choose what goes live.

**Telegram as the interface.** Every notification, every decision, every status check goes through Telegram. No dashboard to build, no web UI, no login. Your phone is the control panel.

**Static site.** Zero infrastructure to manage. Cloudflare Pages deploys on every `git push`. The site is fast (no JS frameworks), costs nothing, and can handle any traffic spike.

**Haiku for cheap tasks.** Using Claude Haiku for idea ranking and tweet drafting instead of Sonnet cuts cost by ~90% for those stages with no quality difference.

---

## What Failed or Sucked

**Reddit distribution.** The original plan was automated Reddit posts. I got banned from the main subreddit within a week. Manual posting is the only safe approach, and it's slow.

**Twitter API.** The free tier of the Twitter API only allows reading, not posting. You need a paid plan ($100/month) to post programmatically. I kept the tweet drafting feature (Telegram shows me the draft, I paste manually) but removed the auto-post.

**63 rejected ideas out of 119 runs.** The trend scanner generates a lot of mediocre ideas. Tightening the scoring prompt helped, but there's still a lot of noise.

**Thumbnail generation.** Tried to auto-generate product card images. The results looked generic and bad. Switched to category-specific SVG placeholders — cleaner and more consistent.

---

## The Code Structure

```
mini-on-factory/
├── scripts/
│   ├── run_pipeline.py       ← orchestrator
│   ├── trend_scan.py         ← idea discovery
│   ├── idea_rank.py          ← scoring
│   ├── generate_product.py   ← Claude API calls
│   ├── package_product.py    ← zip assets
│   ├── update_site.py        ← HTML generation
│   ├── publish_product.py    ← Gumroad API
│   ├── telegram_notify.py    ← send messages
│   ├── telegram_bot.py       ← command handler
│   └── lib/utils.py          ← shared helpers
├── data/
│   ├── product-catalog.json
│   ├── idea-backlog.json
│   └── pipeline-log.json
├── products/{id}/            ← one folder per product
└── site/                     ← static website
```

Everything is plain Python. No frameworks, no ORMs, no complex dependencies. `anthropic`, `python-dotenv`, `requests` — that's basically the entire requirements.

---

## How to Replicate This

You need:

1. **A Mac mini** (or any always-on machine — a $5 VPS works too)
2. **Anthropic API key** — Claude Sonnet for generation (~$3/MTok input), Haiku for cheap tasks
3. **Telegram bot token** — create via @BotFather, free
4. **Gumroad account** — free, 10% fee on sales
5. **GitHub account + Cloudflare Pages** — free static hosting

Estimated setup time: 4–6 hours for someone comfortable with Python.

Estimated cost to run: ~$2–5/month in Claude API usage if you run the pipeline daily.

---

## Current Status

56 products live. $0 in sales (at time of writing — this guide is my first real distribution push).

The factory works. The pipeline is reliable. The bottleneck is the same one every indie maker faces: getting the first person to find your stuff.

If you replicate this and get further than me, I want to hear about it.

→ mini-on-ai.com

---

*Questions? Reach me at hello@mini-on-ai.com*
