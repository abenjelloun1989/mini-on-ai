# Skills

This directory contains two types of skill files — both are markdown documents for Claude, not executable files.

---

## Type 1: Pipeline Documentation

Reference docs for each pipeline stage. Claude reads these to implement or debug a specific stage.

| File | Stage | Script |
|------|-------|--------|
| trend-scan.md | Scan for ideas | scripts/trend_scan.py |
| idea-rank.md | Score and select ideas | scripts/idea_rank.py |
| product-generate.md | Generate product content | scripts/generate_product.py |
| product-package.md | Package assets | scripts/package_product.py |
| website-update.md | Update showcase site | scripts/update_site.py |
| telegram-report.md | Send Telegram notification | scripts/telegram_notify.py |

---

## Type 2: Active Workflow Skills

Behaviors Claude should apply proactively at the start of certain tasks — not tied to a single script.

| File | Trigger | What it does |
|------|---------|--------------|
| sales-counsel.md | User asks about sales / "counsel me" | Fetches live Gumroad + Reddit data, analyzes performance, proposes concrete next actions |
| pattern-detect.md | New planning session starts (plan mode) | Scans git log + command coverage for repeated patterns; proposes up to 2 new skills |
