# Skills

This directory contains **skill specifications** — markdown documents that describe how each pipeline stage works. They are documentation for Claude, not executable files.

## What these are

Each `.md` file defines:
- Purpose of the stage
- Inputs and outputs
- Claude prompt templates
- Success criteria

Claude reads these to understand how to implement or debug each stage.

## What these are NOT

These are NOT Claude Code custom skills (the type defined in `.claude/` config).
They are project documentation only.

## Registering as Claude Code Skills (optional)

If you want to run these stages as `/skill-name` commands in Claude Code,
you would need to register them in your Claude Code settings.

See the Claude Code documentation on custom skills/commands.
The files in this directory can serve as the basis for those commands.

## Files

| File | Stage | Script |
|------|-------|--------|
| trend-scan.md | Scan for ideas | scripts/trend_scan.py |
| idea-rank.md | Score and select ideas | scripts/idea_rank.py |
| product-generate.md | Generate product content | scripts/generate_product.py |
| product-package.md | Package assets | scripts/package_product.py |
| website-update.md | Update showcase site | scripts/update_site.py |
| telegram-report.md | Send Telegram notification | scripts/telegram_notify.py |
