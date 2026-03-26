# Skill: sales-counsel

## Purpose
Act as a sales counselor for the mini-on-ai factory. Fetch real data, analyze performance, and guide the user step by step through concrete actions.

## Trigger
User says anything like: "run the counsel", "counsel me", "what should I do to sell", "sales review", "how are sales going"

## What to execute (in order)

### 1. Fetch Gumroad products
Call `GET https://api.gumroad.com/v2/products` with `Authorization: Bearer {GUMROAD_API_TOKEN}`.
Extract per product: `name`, `price` (cents), `sales_count`, `sales_usd_cents`, `short_url`, `published`.
Filter out deleted or unpublished.

### 2. Fetch Gumroad 30-day sales
Paginate `GET https://api.gumroad.com/v2/sales` until `created_at` is older than 30 days.
Extract: `product_name`, `created_at`, `price`, `paid`, `referrer`.
Count only `paid=true` entries.

### 3. Fetch Reddit activity
Search `https://api.reddit.com/search.json?q=author:Upbeat-Rate3345&sort=new&limit=25&type=link`
and `https://api.reddit.com/search.json?q=author:Upbeat-Rate3345&sort=new&limit=25&type=comment`
using `requests` (not urllib — LibreSSL blocks it).
Extract: subreddit, title/body, score, num_comments.

### 4. Cross-reference with catalog
Read `data/product-catalog.json`. Match catalog products to Gumroad products via the permalink slug in `gumroad_url`.

### 5. Analyze and report
Present findings in 4 sections, be direct and specific:

**🏆 What's working** — actual traction only (downloads, upvotes, comments). If nothing, say so.

**⚠️ What to fix** — name specific products or posts. Be direct. No vague advice.

**📣 Next 3 Reddit posts** — specific subreddit + angle (the problem, not the product) + which product fits. Reference `SUBREDDIT_RULES` in `karma_scout.py` for subreddit-specific constraints.

**💰 Pricing** — only suggest changes for products that exist on Gumroad (cross-check `sales_count` and `short_url`). If price is already correct, say so. Focus on "which $0 products have enough downloads to justify $5".

### 6. Ask what to act on
After the report, ask: "What do you want to act on first?" Then for each action:

- **Price change** → call `PUT https://api.gumroad.com/v2/products/{id}` with `price={cents}`, then run `/syncprices` via the bot. If the API call fails, give the exact Gumroad dashboard URL.
- **Reddit post** → generate the post copy immediately using the angle. Apply subreddit rules from `SUBREDDIT_RULES` in `karma_scout.py`. User copies and pastes.
- **Anything else** → give exact steps, not vague advice.

## Rules
- Never suggest a price change for a product not found in the live Gumroad API response
- Never say "free" or "no signup" for a paid product
- No em-dashes in generated copy
- If Reddit data is sparse, say so explicitly — don't speculate
- Keep each bullet under 120 characters
- Be direct. The user is demotivated. Short, actionable, honest.

## Environment
- `GUMROAD_API_TOKEN` — in `.env`
- `ANTHROPIC_API_KEY` — in `.env`
- Reddit: use `requests` with `User-Agent: script:mini-on-ai:v1.0 (by /u/minionai)`
- Catalog: `data/product-catalog.json`
- Subreddit rules: `scripts/karma_scout.py` → `SUBREDDIT_RULES` dict
