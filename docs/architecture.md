# Architecture

## Core Principle

The repository IS the system. No external state. No database. No server.
If the Mac mini restarts, nothing is lost. Run the pipeline again.

## Design Decisions

### Why static site?
- Zero maintenance
- Zero cost
- Instant updates (edit HTML, done)
- No attack surface
- Can be hosted anywhere (GitHub Pages, Netlify, direct file serve)

### Why flat JSON files?
- Human-readable
- Git-trackable
- No schema migrations
- Claude can read and write them directly

### Why Node.js scripts?
- Available on every Mac by default
- Claude can generate and debug them easily
- No build step
- Easy to run manually or via cron

### Why Telegram for reporting?
- Free, reliable, instant
- Works without a dashboard
- Bot API is trivially simple
- One message = one pipeline run summary

### Why prompt packs for V1?
- Pure text output — Claude generates it natively
- No external dependencies to package
- Immediate perceived value
- Trivial to package (zip a markdown file)
- Proven demand (AI prompt marketplaces exist)

## Data Flow

```
Claude API
   ↓ generates ideas
idea-backlog.json
   ↓ one idea selected
Claude API
   ↓ generates product content
products/{id}/assets/
   ↓ zipped
products/{id}/package.zip
   ↓ added to
product-catalog.json + site/
   ↓ reported via
Telegram
```

## Showcase Website Rules

The public website ONLY shows:
- Product name
- Short description
- Download link or preview
- Category tag

The website NEVER mentions:
- AI generation
- Automation
- The factory
- Claude or Anthropic
- How products are made

## Scaling Path (post-V1)

V1 → cron schedule → multiple categories → auto-publishing to marketplaces

Each step is optional and additive. V1 remains valid indefinitely.

## File Authority

| Truth | File |
|-------|------|
| What products exist | `data/product-catalog.json` |
| What ideas are queued | `data/idea-backlog.json` |
| What the pipeline did | `data/pipeline-log.json` |
| What is built | `docs/current-state.md` |
| What to build next | `docs/next-steps.md` |
