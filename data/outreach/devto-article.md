# I built a Python pipeline that auto-generates digital products using Claude API — here's the architecture

*Tags: #showdev #buildinpublic #python #claudeai*

---

I built a machine that makes digital products. It runs 24/7 on a $600 Mac mini in my home office. Here's the honest story: 119 pipeline runs, 57 products shipped, **$0 in revenue so far** — and why I'm publishing this anyway.

## The concept

The idea is embarrassingly simple: scan the internet for pain points → rank which ones make viable products → auto-generate the product with Claude → publish it to a static site and Gumroad → repeat weekly.

No human writes the content. No human formats the pages. I only touch two things: approving or rejecting ideas (via Telegram inline buttons on my phone) and occasionally debugging Python.

## The pipeline

```
trend_scan.py
  → scrapes Reddit for questions and complaints
  → synthesizes pain points into product ideas

idea_rank.py
  → scores each idea: audience size, search volume, competition, monetization fit
  → marks the top-ranked idea as selected

[Telegram approval gate — me, on my phone]

generate_product.py
  → Claude writes all content (20-30 prompts, or a full guide, or a checklist)
  → structured output, no hallucination guard needed at this scale

package_product.py
  → zips the content into a downloadable package

update_site.py
  → rebuilds every product page, the homepage, and sitemap
  → pushes to Cloudflare Pages via git

telegram_notify.py
  → sends me a summary with Gumroad copy ready to paste
```

The whole run takes ~5 minutes. I get a Telegram message, paste the copy into Gumroad, done.

## The stack

- **Python 3** — all scripts, no build step
- **Claude API (Haiku + Sonnet 3.5)** — content generation; Haiku for bulk, Sonnet for flagship guides
- **Gumroad** — product listings and payments ($5–$49)
- **Cloudflare Pages** — static site hosting (free tier)
- **Cloudflare Workers** — two workers: one for the "Build Your Own" Stripe flow, one for email subscribe
- **Stripe** — $9 on-demand custom product generation
- **Brevo** — email list (17 subscribers so far)
- **Telegram Bot API** — zero-UI control panel: `/run`, `/approve`, `/blast`, `/tweet`

## What I got right

**The approval gate.** Every product idea goes through a Telegram message with Go/No buttons. 63 ideas rejected out of 119 runs. This kept quality up — the factory is opinionated, not just a fire hose.

**Static site.** The entire store is generated HTML. Cloudflare Pages serves it from CDN. No database, no server. The whole site rebuilds in ~30 seconds.

**Free tier as lead magnet.** 15 products are free. Claude Code skill packs, n8n workflow templates. These drive discovery — someone finds the free Architecture Overview Generator, clicks through, discovers the $49 guide.

## What failed

**Reddit.** Got banned from r/ClaudeAI after one post. I was trying to share a free skill pack. Lesson: subreddits don't want automated products even when they're free. I now focus on organic karma building in r/Python and r/SideProject, slowly.

**Twitter API.** The automated tweet workflow requires Twitter API v2 with elevated access — $100/month. Not worth it at zero revenue. Tweets are now drafted and posted manually.

**Thumbnail generation.** Claude kept generating image descriptions instead of actual image files. I gave up and now use text-only product cards. The dark premium design actually makes them look intentional.

**Distribution is hard.** 57 products live. 0 paid sales. The factory works. The pipeline works. The bottleneck is entirely distribution — getting the right people to the site.

## The $49 guide

I wrote a full breakdown of everything above — architecture, all the prompts, the Cloudflare Worker code, lessons learned — as a product on the site itself. It's the most meta thing I've ever built: the factory's own documentation as its first flagship product.

→ **[How I Built an AI Product Factory on a Mac mini](https://mini-on-ai.com/products/guide-how-i-built-an-ai-product-factory-20260330.html)** — $49

## Free stuff

If you just want to see the output:
- **[n8n Starter Guide for Zapier Users](https://minionai.gumroad.com/l/appuyt)** — free
- **[Claude Code Skill: Architecture Overview Generator](https://minionai.gumroad.com/l/vmkqra)** — free
- **[n8n Social Media Auth & Posting Workflow](https://minionai.gumroad.com/l/kbwfrq)** — free

Or try the [Build Your Own](https://mini-on-ai.com/build.html) — describe your use case, get a custom prompt pack or checklist in 30 seconds, preview free, download for $9.

---

Happy to answer questions about the pipeline, the Claude prompting patterns, or the Cloudflare Worker setup. What I actually need help with: **distribution**. If you've shipped digital products without an existing audience, I'd genuinely love to know what worked.
