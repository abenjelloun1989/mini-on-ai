# Claude Code Skills Pack: Data Quality — 5 Skills for Pipeline Validation and Anomaly Detection

> For data engineers and analytics leads, this pack generates data contract definitions, row-level validation checks, statistical anomaly detection rules, data freshness monitors, and incident summary reports so they can catch data issues before they reach dashboards or decision-makers.

---

## What's in This Pack

Generates data contracts, validation checks, anomaly detection rules, freshness monitors, and incident reports to help data engineers and analytics leads catch pipeline issues before they reach dashboards or decision-makers.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/gen-data-contract`** — `01-gen-data-contract.md`
   Generates a formal data contract definition for a dataset, including schema, field-level expectations, ownership metadata, and SLA commitments.

**2. `/gen-row-validations`** — `02-gen-row-validations.md`
   Produces row-level validation checks (null rates, range bounds, referential integrity, regex patterns) as executable dbt tests or Great Expectations suites.

**3. `/gen-anomaly-rules`** — `03-gen-anomaly-rules.md`
   Builds statistical anomaly detection rules using z-score, IQR, or seasonality-aware thresholds to flag unexpected volume, distribution, or value shifts in pipeline metrics.

**4. `/gen-freshness-monitor`** — `04-gen-freshness-monitor.md`
   Creates data freshness monitoring configurations that track last-updated timestamps, define staleness thresholds, and emit alerts when tables or partitions fall behind SLA.

**5. `/gen-incident-report`** — `05-gen-incident-report.md`
   Produces a structured data incident summary report from validation failures or anomaly signals, including root cause hypothesis, impacted assets, downstream risk, and recommended remediation steps.

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
| Generates a formal data contract definition for a dataset, including schema, field-level expectations, ownership metadata, and SLA commitments. | `/gen-data-contract` | `01-gen-data-contract.md` |
| Produces row-level validation checks (null rates, range bounds, referential integrity, regex patterns) as executable dbt tests or Great Expectations suites. | `/gen-row-validations` | `02-gen-row-validations.md` |
| Builds statistical anomaly detection rules using z-score, IQR, or seasonality-aware thresholds to flag unexpected volume, distribution, or value shifts in pipeline metrics. | `/gen-anomaly-rules` | `03-gen-anomaly-rules.md` |
| Creates data freshness monitoring configurations that track last-updated timestamps, define staleness thresholds, and emit alerts when tables or partitions fall behind SLA. | `/gen-freshness-monitor` | `04-gen-freshness-monitor.md` |
| Produces a structured data incident summary report from validation failures or anomaly signals, including root cause hypothesis, impacted assets, downstream risk, and recommended remediation steps. | `/gen-incident-report` | `05-gen-incident-report.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
