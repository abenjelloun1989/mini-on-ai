# Deployment Guide

## Overview

The `site/` folder is a static website. Deploy it to any static host.
After each pipeline run, git auto-commits the site changes.
Connect your git repo to Netlify for auto-deploy on push.

---

## Step 1 — Push to GitHub

```bash
# Create a new repo on github.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/mini-on-ai.git
git push -u origin main
```

---

## Step 2 — Deploy to Netlify (recommended, free)

### Option A: Netlify drag-and-drop (fastest, no git needed)
1. Go to https://app.netlify.com
2. Drag the `site/` folder onto the deploy zone
3. You get a public URL like `https://random-name.netlify.app`

### Option B: Netlify connected to GitHub (auto-deploy on push)
1. Go to https://app.netlify.com → "Add new site" → "Import an existing project"
2. Connect GitHub → select this repo
3. Set **Publish directory**: `site`
4. Deploy
5. Every `git push` will automatically redeploy the site

### After deploying:
Update `.env`:
```
SITE_URL=https://your-site.netlify.app
```

---

## Step 3 — Start the Telegram Bot (persistent)

The bot runs as a background macOS service.

```bash
# Copy plist to LaunchAgents
cp launchd/com.mini-on-ai.bot.plist ~/Library/LaunchAgents/

# Load and start it
launchctl load ~/Library/LaunchAgents/com.mini-on-ai.bot.plist

# Verify it's running
launchctl list | grep mini-on-ai
```

The bot starts automatically on login and restarts if it crashes.

To stop it:
```bash
launchctl unload ~/Library/LaunchAgents/com.mini-on-ai.bot.plist
```

---

## Step 4 — Schedule Daily Pipeline Runs

```bash
# Copy plist to LaunchAgents
cp launchd/com.mini-on-ai.pipeline.plist ~/Library/LaunchAgents/

# Load it
launchctl load ~/Library/LaunchAgents/com.mini-on-ai.pipeline.plist
```

Pipeline runs every day at 9:00 AM.
Results reported to Telegram automatically.

---

## Logs

All logs are in `logs/`:
```
logs/bot.log           — Telegram bot output
logs/bot-error.log     — Bot errors
logs/pipeline.log      — Pipeline run output
logs/pipeline-error.log — Pipeline errors
```

---

## Full Auto-deploy Flow (once everything is set up)

```
9:00 AM — launchd triggers run_pipeline.py
         → generates product
         → updates site/
         → git commit + git push
         → Netlify detects push → redeploys site (< 30s)
         → Telegram: "New product published 🎉"
```

No manual action needed.
