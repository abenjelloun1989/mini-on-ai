# Claude Code Skills Pack: Automated Report Generation — 5 Skills for Scheduling and Distributing Recurring Reports

> For analytics leads and operations analysts, this pack covers parameterized report templating, scheduling logic, multi-format export (PDF, CSV, Slack), recipient segmentation, and delivery audit logging across 5 skills so they can eliminate manual report-running from their weekly workflow entirely

---

## What's in This Pack

A five-skill pack that helps analytics leads and operations analysts fully automate recurring report workflows — from parameterized template authoring and schedule configuration through multi-format export, recipient segmentation, and delivery audit logging — so no report ever needs to be run manually again.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/build-report-template`** — `01-parameterized-report-template.md`
   Scaffolds a reusable, parameterized report template that accepts dynamic inputs (date ranges, filters, metrics) and renders consistent output structures for downstream formatting and export.

**2. `/schedule-report`** — `02-report-schedule-configurator.md`
   Generates scheduling logic (cron expressions, interval configs, or workflow trigger definitions) for recurring report runs, including timezone handling, retry policies, and skip-holiday rules.

**3. `/export-report`** — `03-multi-format-report-exporter.md`
   Produces export pipeline code that renders a completed report into one or more target formats — PDF (print-ready), CSV (raw data), and Slack Block Kit message — from a single shared data payload.

**4. `/segment-recipients`** — `04-recipient-segment-router.md`
   Builds recipient segmentation logic that maps report variants, data scopes, and delivery channels to the correct audience groups based on role, team, or subscription rules.

**5. `/log-report-delivery`** — `05-delivery-audit-logger.md`
   Instruments a delivery audit logging layer that records every report dispatch event — recipient, format, timestamp, status, and error detail — to a structured log store for traceability and SLA monitoring.

---

## How to Install

1. **Create a `skills/` directory** in your project root (if it doesn't exist):
   ```bash
   mkdir -p skills
   ```

2. **Copy all skill files** from the `skills/` folder in this pack:
   ```bash
   cp skills/*.md /your-project/skills/
   ```

3. **Run Claude Code** in your project directory — all skills are immediately available:
   ```bash
   claude
   ```

---

## Quick Reference

| Skill | Trigger | File |
|-------|---------|------|
| Scaffolds a reusable, parameterized report template that accepts dynamic inputs (date ranges, filters, metrics) and renders consistent output structures for downstream formatting and export. | `/build-report-template` | `01-parameterized-report-template.md` |
| Generates scheduling logic (cron expressions, interval configs, or workflow trigger definitions) for recurring report runs, including timezone handling, retry policies, and skip-holiday rules. | `/schedule-report` | `02-report-schedule-configurator.md` |
| Produces export pipeline code that renders a completed report into one or more target formats — PDF (print-ready), CSV (raw data), and Slack Block Kit message — from a single shared data payload. | `/export-report` | `03-multi-format-report-exporter.md` |
| Builds recipient segmentation logic that maps report variants, data scopes, and delivery channels to the correct audience groups based on role, team, or subscription rules. | `/segment-recipients` | `04-recipient-segment-router.md` |
| Instruments a delivery audit logging layer that records every report dispatch event — recipient, format, timestamp, status, and error detail — to a structured log store for traceability and SLA monitoring. | `/log-report-delivery` | `05-delivery-audit-logger.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
