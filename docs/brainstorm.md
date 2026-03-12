# mini-on-ai — Original Brainstorm

*Captured 2026-03-12. This is the source-of-truth for product vision and scope.*

---

## Project Name

**mini-on-ai**
- Mac mini running continuously
- AI-driven automation
- Always-on experimentation environment

---

## Core Idea

The Mac mini runs a continuous pipeline that produces small digital products.

```
discover → build → publish → showcase → repeat
```

Focus: output and experimentation, not a complex autonomous system from day one.

---

## Pipeline

```
Trend Scanner → Idea Selection → Product Generator → Publisher → Website Update
```

Each step stays lightweight.

---

## Trend Scanner

Purpose: detect demand signals.

Sources to scan periodically:
- Reddit discussions
- Indie Hackers
- Product Hunt
- Marketplaces (Gumroad, Etsy)
- Automation communities

Output: list of potential product ideas grounded in real demand.

---

## Idea Selection

Filter ideas using simple criteria:
- Easy to produce
- Evergreen demand
- Compatible with digital products
- Suitable for marketplaces

Only the best ideas move to production.
At the start: semi-automatic with manual validation (Telegram approval gate).

---

## Product Generator

Creates small digital assets such as:
- **Automation templates**
- **AI prompt workflows**
- **Datasets**
- **Notion templates**
- **Small utilities or scripts**

Each generated product includes:
- The asset itself
- Documentation
- Screenshots
- Product description

Ready to publish.

---

## Publisher

Products are published on marketplaces:
- Gumroad
- Lemon Squeezy
- Etsy
- Automation template marketplaces

Publishing process includes:
- Title generation
- Description writing
- Thumbnail generation
- Product listing creation

Products generate revenue without direct sales effort.

---

## Project Showcase Website

Acts only as a product showcase ("vitrine").

**Important rule: the website does NOT explain the factory or automation system. It simply presents the products.**

Structure:
- Homepage: list of products
- Each product page: name, short description, screenshots, link to marketplace listing

Clean catalog, nothing more.

---

## Automated Website Updates

Whenever a new product is created:
```
product generated
→ create product page
→ generate description
→ add to project list
→ deploy website update
```

---

## Local Stack

- Python
- Cron / daemon scheduler
- Claude Code
- SQLite database (future)
- Scraping: Playwright or simple HTTP requests
- Communication: Telegram bot
- Website: static site (simple static framework)

---

## Telegram Control Interface

Lightweight control dashboard.

Commands: `/status` `/products` `/ideas` `/publish`

Example response:
```
mini-on-ai status
Products published: 12
Products generated today: 1
Revenue today: €19
```

---

## V1 Strategy

Focus on:
1. Trend scanning
2. Product generation
3. Publishing
4. Website showcase

Advanced features (token optimization, autonomous ranking) added later.
**Goal: start producing real products quickly.**

---

## Long-Term Vision

The Mac mini becomes a small autonomous studio generating many small digital products.

The mini-on-ai website grows into a catalog of projects and experiments.
Marketplaces handle the transactions.
Revenue comes from the accumulation of many small products.
