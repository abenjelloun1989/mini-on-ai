---
name: gen-incident-report
trigger: /gen-incident-report
description: >
  Produces a structured data incident summary report from validation failures,
  anomaly signals, or freshness alerts. Use this skill whenever a data quality
  issue has been detected and you need to communicate root cause, impact, and
  remediation steps to stakeholders, on-call engineers, or incident trackers.
  Best used after running validation checks or anomaly detection rules that have
  surfaced concrete failure signals.
tags: [data-quality, incident-management, reporting, pipeline-validation]
---

# Skill: gen-incident-report

## Purpose

Generate a complete, structured data incident report from raw failure signals —
validation errors, anomaly detections, freshness breaches, or manual
observations. The report must be immediately shareable with data engineers,
analytics leads, and business stakeholders without further editing.

---

## When to Use This Skill

- One or more validation checks have failed in a data pipeline
- An anomaly detection rule has fired on a metric or dataset
- A freshness monitor has flagged a table as stale
- An analyst has manually noticed something wrong in a dashboard or query result
- A post-incident review is being drafted after data has been corrected

---

## Execution Instructions

Follow these steps in order every time this skill is invoked.

### Step 1 — Collect Input Context

Before generating the report, identify what the user has provided. Accept any
combination of the following:

- Raw validation failure output (JSON, YAML, plain text, log lines)
- Anomaly detection rule results or statistical summaries
- Table names, pipeline names, or dataset identifiers
- Error messages, row counts, or metric values
- Freshness timestamps or SLA breach details
- Any prior notes, hypotheses, or Slack/ticket text from the user

If critical information is missing (e.g., no dataset name or no failure
description), ask the user for it before proceeding. Do not fabricate specific
table names, row counts, or metric values — use placeholders clearly marked as
`[UNKNOWN — please specify]` when data is unavailable.

### Step 2 — Classify Incident Severity

Assign a severity level based on the signals provided. Use the following rubric:

| Severity | Label    | Criteria                                                                 |
|----------|----------|--------------------------------------------------------------------------|
| SEV-1    | Critical | Production dashboards or ML models are consuming bad data right now      |
| SEV-2    | High     | Data is wrong in a key table; downstream impact is likely but unconfirmed|
| SEV-3    | Medium   | Validation failed but data is not yet consumed downstream                |
| SEV-4    | Low      | Minor anomaly, no confirmed downstream impact, likely self-correcting    |

If severity cannot be determined from the input, default to SEV-2 and note the
assumption explicitly in the report.

### Step 3 — Identify Impacted Assets

List all datasets, tables, pipelines, dashboards, models, or reports that are
confirmed or likely affected. Distinguish clearly between:

- **Confirmed impacted**: directly referenced in the failure signal
- **Likely impacted**: downstream consumers of the confirmed assets
- **Under investigation**: assets that may be affected but are unconfirmed

### Step 4 — Formulate Root Cause Hypothesis

Based on the failure signals, propose the most likely root cause. Structure the
hypothesis as:

- **Observed symptom**: what the validation or anomaly rule detected
- **Probable cause**: the most likely upstream reason (schema change, late
  arrival, source system issue, transformation bug, etc.)
- **Confidence**: High / Medium / Low, with a one-sentence justification
- **Alternative hypotheses**: one or two other plausible explanations to rule out

Do not state a hypothesis as fact. Use language like "most likely," "probable,"
or "evidence suggests."

### Step 5 — Assess Downstream Risk

For each confirmed or likely impacted asset, describe:

- What business process or decision relies on this data
- Whether incorrect data has already been consumed (yes / no / unknown)
- The blast radius: how many dashboards, reports, or stakeholders are affected
- Whether any automated processes (ML scoring, financial reporting, alerting)
  may have acted on bad data

### Step 6 — Write Recommended Remediation Steps

Provide a prioritized, numbered action list. Each step must include:

- **Owner role** (e.g., "Data Engineer," "Pipeline On-Call," "Analytics Lead")
- **Action** described concisely and specifically
- **Expected outcome** of completing the step

Structure remediation in three phases:
1. **Immediate (0–2 hours)**: stop the bleeding, prevent further propagation
2. **Short-term (2–24 hours)**: fix the root cause, reprocess affected data
3. **Long-term (1–2 weeks)**: add safeguards to prevent recurrence

### Step 7 — Assemble the Report

Output the report in the exact format defined in the Output Format section
below. Do not skip any section. If a section cannot be populated, write
"Insufficient information — [what is needed]" rather than omitting it.

---

## Output Format

Produce the report as clean Markdown using the following template:

---

# Data Incident Report

**Incident ID:** INC-[YYYYMMDD]-[sequential number or identifier]
**Severity:** [SEV-1 / SEV-2 / SEV-3 / SEV-4] — [Label]
**Status:** [Investigating / Mitigating / Resolved]
**Detected At:** [timestamp or "Unknown"]
**Reported By:** [user name, system, or skill trigger]
**Last Updated:** [timestamp]

---

## Summary

[Two to three sentences. What failed, where, and what the immediate concern is.
Written for a non-technical stakeholder.]

---

## Impacted Assets

### Confirmed Impacted
- [asset name] — [type: table / dashboard / pipeline / model] — [brief impact description]

### Likely Impacted
- [asset name] — [type] — [reason for suspicion]

### Under Investigation
- [asset name] — [type] — [what needs to be checked]

---

## Root Cause Hypothesis

**Observed Symptom:**
[What the validation failure or anomaly signal showed, with specific values if available.]

**Probable Cause:**
[Most likely explanation.]

**Confidence:** [High / Medium / Low]
[One sentence justifying the confidence level.]

**Alternative Hypotheses to Investigate:**
1. [Alternative 1]
2. [Alternative 2]

---

## Downstream Risk Assessment

| Asset | Business Process Affected | Bad Data Already Consumed? | Blast Radius |
|-------|--------------------------|---------------------------|--------------|
| [name] | [process] | [Yes / No / Unknown] | [description] |

---

## Recommended Remediation

### Phase 1 — Immediate (0–2 hours)
1. **[Owner Role]** — [Action] → [Expected outcome]
2. **[Owner Role]** — [Action] → [Expected outcome]

### Phase 2 — Short-Term (2–24 hours)
1. **[Owner Role]** — [Action] → [Expected outcome]
2. **[Owner Role]** — [Action] → [Expected outcome]

### Phase 3 — Long-Term (1–2 weeks)
1. **[Owner Role]** — [Action] → [Expected outcome]
2. **[Owner Role]** — [Action] → [Expected outcome]

---

## Timeline of Events

| Time | Event |
|------|-------|
| [time] | [event description] |

---

## Open Questions

- [Question that must be answered to close this incident]
- [Question about impact scope or root cause]

---

## Notes

[Any additional context, links to related incidents, runbooks, or tickets.]

---

## Constraints and Quality Rules

- **Never fabricate data.** Do not invent row counts, timestamps, table names,
  or metric values. Use `[UNKNOWN]` placeholders for anything not provided.
- **Severity must be justified.** Always explain in one sentence why the chosen
  severity level was assigned.
- **Root cause is a hypothesis.** Never present it as confirmed fact unless the
  user explicitly states it has been confirmed.
- **Remediation steps must have owners.** Every action item needs a role assigned.
- **Keep the Summary section accessible.** Assume a non-technical reader will
  read only that section. Avoid jargon.
- **Use past tense for confirmed events, present tense for ongoing conditions.**
- **All timestamps should include timezone** where known. Use UTC if unspecified.
- **Do not include internal tool names or infrastructure details** in the Summary
  section — reserve those for the technical sections.

---

## Usage Examples

### Example 1 — Validation failure with log output

/gen-incident-report

I ran the row validation suite on `orders.order_items` and got this output:
  - NULL check failed on column `product_id`: 4,821 nulls found (expected 0)
  - Referential integrity check failed: 1,203 order_item_id values not in `orders.orders`
Pipeline: `dbt_orders_daily`, run at 2024-03-15 06:00 UTC
The `sales_by_product` Looker dashboard pulls from this table every morning.

---

### Example 2 — Anomaly detection signal with minimal context

/gen-incident-report

Our anomaly detector fired on `revenue_metrics.daily_gmv`. The z-score was 4.7
for yesterday's value — $2.1M vs a 30-day average of $8.4M. Not sure if it's a
pipeline issue or a real business drop. Affects the CFO dashboard.

---

### Example 3 — Freshness breach escalation

/gen-incident-report

Table `warehouse.inventory_snapshot` hasn't updated in 18 hours. SLA is 4 hours.
The last successful load was 2024-03-14 22:00 UTC. Three downstream models depend
on it: `supply_chain_forecast`, `reorder_alerts`, and `store_inventory_dashboard`.
The reorder alerts job runs at 08:00 UTC and may have already fired with stale data.