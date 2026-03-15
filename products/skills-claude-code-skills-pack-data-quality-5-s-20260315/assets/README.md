# Claude Code Skills Pack: Data Quality — 5 Skills for Pipeline Validation and Anomaly Detection

For data engineers and analytics leads, this pack generates data contract definitions, row-level validation checks, statistical anomaly detection rules, data freshness monitors, and incident summary reports so they can catch data issues before they reach dashboards or decision-makers.

## What's included

- **5 ready-to-use SKILL.md files** — drop into your project's `skills/` folder, no setup required
- **guide.md** — installation instructions and quick-reference table for all 5 skills
- Each skill is immediately usable with its slash-command trigger

## Skills in this pack

- `skills/01-gen-data-contract.md` — `/gen-data-contract` — Generates a formal data contract definition for a dataset, including schema, field-level expectations, ownership metadata, and SLA commitments.
- `skills/02-gen-row-validations.md` — `/gen-row-validations` — Produces row-level validation checks (null rates, range bounds, referential integrity, regex patterns) as executable dbt tests or Great Expectations suites.
- `skills/03-gen-anomaly-rules.md` — `/gen-anomaly-rules` — Builds statistical anomaly detection rules using z-score, IQR, or seasonality-aware thresholds to flag unexpected volume, distribution, or value shifts in pipeline metrics.
- `skills/04-gen-freshness-monitor.md` — `/gen-freshness-monitor` — Creates data freshness monitoring configurations that track last-updated timestamps, define staleness thresholds, and emit alerts when tables or partitions fall behind SLA.
- `skills/05-gen-incident-report.md` — `/gen-incident-report` — Produces a structured data incident summary report from validation failures or anomaly signals, including root cause hypothesis, impacted assets, downstream risk, and recommended remediation steps.

## Quick Start

1. Copy the `skills/` folder into your project root
2. Run `claude` in your project directory
3. Use any skill trigger listed above

## Files

- `skills/` — 5 SKILL.md files, one per skill
- `guide.md` — Installation guide and quick-reference table
- `README.md` — This file
