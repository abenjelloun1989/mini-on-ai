# Next Steps

Last updated: 2026-03-13

## Immediate — Activate Gumroad publishing

1. Create a Gumroad account at gumroad.com
2. Go to Settings → Advanced → Access token → create one
3. Add to `.env`:
   ```
   GUMROAD_API_TOKEN=your_token_here
   PRODUCT_PRICE_CENTS=500
   ```
4. Publish existing products manually:
   ```bash
   python3 scripts/publish_product.py --id prompts-ats-optimized-resume-bullet-rewriter-by--20260312
   python3 scripts/publish_product.py --id prompts-shopify-product-description-packs-for-e--20260312
   python3 scripts/publish_product.py --id prompts-meeting-notes-to-action-items-fast-20260312
   ```
5. New products will publish automatically via the pipeline

## Immediate — Set up domain + email

1. **Buy** `mini-on-ai.com` at namecheap.com
2. **DNS at Namecheap** — add these records:
   ```
   A     @    185.199.108.153
   A     @    185.199.109.153
   A     @    185.199.110.153
   A     @    185.199.111.153
   CNAME www  abenjelloun1989.github.io
   ```
3. **GitHub Pages** → Settings → Pages → Custom domain → `mini-on-ai.com` → Save → Enable HTTPS
4. **Zoho Mail** (free) → zoho.com/mail → Add domain `mini-on-ai.com` → Add MX records → Create `hello@mini-on-ai.com`

## Next — Grow the catalog

The daemon is running. Approve ideas via Telegram until you have 8-10 products.
Good seeds:
  /run marketing
  /run freelancing
  /run writing
  /run coding
  /run productivity

## Then — M11 Phase B: Reddit distribution

- Install PRAW: `pip3 install praw`
- Create a Reddit app at reddit.com/prefs/apps
- Script posts to relevant subreddits per product category
- Add `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD` to `.env`

## Then — M14: Analytics

Know which products get the most clicks from the vitrine.
- Options: Cloudflare proxy (free), Plausible, or a tiny redirect counter
- Goal: feed download/click data back into idea ranking

## Then — M15: Email List

Convert visitors into an owned audience.
- Embed a free Beehiiv or Kit signup on product pages
- "Get notified when new packs drop"
