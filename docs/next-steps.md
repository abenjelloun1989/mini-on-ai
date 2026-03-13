# Next Steps

Last updated: 2026-03-13

## Immediate — Grow the catalog

The pipeline and site are fully operational. Run the daemon and approve ideas until you have 10+ products.

Good seeds to run:
```
/run freelancing
/run coding
/run marketing
/run operations
/run design
```

Each new product will:
1. Be generated with hard-quota category distribution (4×prompts, 2×checklist, 2×swipe-file, 1×guide, 1×n8n per 10-idea batch)
2. Get a plain-text Claude-written description (paste-ready into Gumroad WYSIWYG editor)
3. Send a compact Telegram notification with a link to the vitrine product page
4. Open the vitrine page → click "📋 Copy description for Gumroad" → paste into Gumroad
5. Create the Gumroad listing, reply `/seturl {id} {url}`
6. Site updates and pushes automatically

## Upload branded cover to each Gumroad product

The generic cover is at: `site/images/cover-default.png`
Upload it to each product's Gumroad listing as the cover image.

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
