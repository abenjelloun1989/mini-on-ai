# Next Steps

Last updated: 2026-03-12

## Immediate: Grow the Catalog (M7)

Run 4 more times:
  python3 scripts/run_pipeline.py --seed "marketing"
  python3 scripts/run_pipeline.py --seed "freelancing"
  python3 scripts/run_pipeline.py --seed "writing"
  python3 scripts/run_pipeline.py --seed "coding"

Target: 5 products before going public.

## Then: Deploy Site Publicly (M8)

Fastest path — Netlify drag-and-drop:
1. Go to netlify.com
2. Drag the site/ folder onto the deploy zone
3. Get a public URL instantly
4. Update SITE_URL in .env

## Then: Auto-scheduling (M9)

Set up launchd to run daily at 9am.
See docs/launchd-setup.md (to be created).

## Then: Git (M10)

  git init
  git add .
  git commit -m "V1 complete"
  # push to GitHub
