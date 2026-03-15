# Claude Code Skills Pack: Automated Report Generation — 5 Skills for Scheduling and Distributing Recurring Reports

For analytics leads and operations analysts, this pack covers parameterized report templating, scheduling logic, multi-format export (PDF, CSV, Slack), recipient segmentation, and delivery audit logging across 5 skills so they can eliminate manual report-running from their weekly workflow entirely

## What's included

- **5 ready-to-use SKILL.md files** — drop into your project's `skills/` folder, no setup required
- **guide.md** — installation instructions and quick-reference table for all 5 skills
- Each skill is immediately usable with its slash-command trigger

## Skills in this pack

- `skills/01-parameterized-report-template.md` — `/build-report-template` — Scaffolds a reusable, parameterized report template that accepts dynamic inputs (date ranges, filters, metrics) and renders consistent output structures for downstream formatting and export.
- `skills/02-report-schedule-configurator.md` — `/schedule-report` — Generates scheduling logic (cron expressions, interval configs, or workflow trigger definitions) for recurring report runs, including timezone handling, retry policies, and skip-holiday rules.
- `skills/03-multi-format-report-exporter.md` — `/export-report` — Produces export pipeline code that renders a completed report into one or more target formats — PDF (print-ready), CSV (raw data), and Slack Block Kit message — from a single shared data payload.
- `skills/04-recipient-segment-router.md` — `/segment-recipients` — Builds recipient segmentation logic that maps report variants, data scopes, and delivery channels to the correct audience groups based on role, team, or subscription rules.
- `skills/05-delivery-audit-logger.md` — `/log-report-delivery` — Instruments a delivery audit logging layer that records every report dispatch event — recipient, format, timestamp, status, and error detail — to a structured log store for traceability and SLA monitoring.

## Quick Start

1. Copy the `skills/` folder into your project root
2. Run `claude` in your project directory
3. Use any skill trigger listed above

## Files

- `skills/` — 5 SKILL.md files, one per skill
- `guide.md` — Installation guide and quick-reference table
- `README.md` — This file
