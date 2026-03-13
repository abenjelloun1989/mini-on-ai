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
1. Be generated with diverse category (checklist, swipe-file, guide, n8n-template, or prompts)
2. Get a rich Claude-written Gumroad description (stored in meta.json)
3. Send a Telegram notification with tap-to-copy fields + zip attachment
4. You create the Gumroad listing in ~30 sec, reply `/seturl {id} {url}`
5. Site updates and pushes automatically

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
