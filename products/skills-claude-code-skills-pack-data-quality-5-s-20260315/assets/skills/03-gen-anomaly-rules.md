---
name: gen-anomaly-rules
trigger: /gen-anomaly-rules
description: >
  Generates statistical anomaly detection rules for pipeline metrics using
  z-score, IQR, or seasonality-aware thresholds. Use this skill when you need
  to programmatically flag unexpected shifts in data volume, value distributions,
  or metric behavior before they surface in dashboards or downstream decisions.
  Best suited for data engineers and analytics leads instrumenting monitoring
  on top of existing pipelines or data contracts.
tags: [data-quality, anomaly-detection, monitoring, statistics, pipeline]
---

# Skill: gen-anomaly-rules

## Purpose

Analyze a described or sampled dataset/metric and produce ready-to-use anomaly
detection rules. Rules are grounded in statistical methods appropriate to the
data's characteristics and output as executable code or structured configuration
depending on the target environment.

## When to Use

- A metric (row count, revenue, conversion rate, etc.) needs automated alerting
- A pipeline column has known historical variance that should be bounded
- You need seasonality-aware rules for weekly or daily cyclical data
- You want IQR-based outlier detection for skewed or non-normal distributions
- You are building a monitoring layer on top of a data contract

---

## Execution Instructions

Follow these steps in order when `/gen-anomaly-rules` is invoked.

### Step 1 — Gather Context

Parse the user's invocation for the following inputs. If any required input is
missing, ask before proceeding.

**Required:**
- `metric` — The name and description of the metric or column being monitored
  (e.g., `daily_order_count`, `revenue_usd`, `signup_conversion_rate`)
- `method` — Detection method: `zscore`, `iqr`, or `seasonal`
  - If not provided, infer from data characteristics described (see Step 2)

**Optional:**
- `sample_data` — Inline historical values, a file path, or a description of
  the distribution (e.g., "roughly normal, mean ~10k, std ~800")
- `sensitivity` — `low`, `medium` (default), or `high`
  - low: fewer alerts, wider thresholds
  - medium: balanced thresholds
  - high: tight thresholds, more sensitive to drift
- `target` — Output format: `python`, `sql`, `yaml`, or `json`
  - Defaults to `python` if not specified
- `cadence` — How often the metric is evaluated: `hourly`, `daily`, `weekly`
  - Required for `seasonal` method; ask if missing
- `context` — Any business rules or known acceptable anomalies to exclude

---

### Step 2 — Infer Method If Not Specified

Use these heuristics to select the best method when the user has not specified:

| Signal | Recommended Method |
|---|---|
| Data has strong day-of-week or hour-of-day pattern | `seasonal` |
| Data is skewed, has outliers, or is non-normal | `iqr` |
| Data is roughly normal, continuous, symmetric | `zscore` |
| Cadence is weekly or metric resets on a cycle | `seasonal` |
| User describes "volume" or "count" metrics | `iqr` (counts are often right-skewed) |

State the inferred method and brief rationale before generating rules.

---

### Step 3 — Calculate or Estimate Thresholds

Apply the chosen method using provided sample data or stated distribution
parameters. If no data is provided, generate parameterized rules with clearly
labeled placeholder values.

**Z-Score:**
- Sensitivity low → threshold ±3.5
- Sensitivity medium → threshold ±3.0
- Sensitivity high → threshold ±2.5
- Formula: `z = (value - mean) / std_dev`
- Flag when `|z| > threshold`

**IQR:**
- Sensitivity low → multiplier 3.0
- Sensitivity medium → multiplier 1.5
- Sensitivity high → multiplier 1.0
- Lower bound: `Q1 - multiplier * IQR`
- Upper bound: `Q3 + multiplier * IQR`
- Flag when value falls outside bounds

**Seasonal:**
- Build expected value from same-period historical average
  (e.g., mean of all previous Mondays for a daily metric)
- Apply a percentage deviation band based on sensitivity:
  - low → ±25%
  - medium → ±15%
  - high → ±10%
- Also apply an absolute floor deviation to avoid over-alerting on small values
- Flag when deviation from expected exceeds band

---

### Step 4 — Generate Output

Produce the anomaly detection rule in the requested target format.

**All outputs must include:**
1. A header comment block with: metric name, method, sensitivity, thresholds
   used, date generated, and any assumptions made
2. The core detection logic (function, query, or config block)
3. A human-readable alert message template with the metric name, observed value,
   expected range, and percent deviation
4. Inline comments explaining each threshold or parameter so it can be tuned

**Python output:** A self-contained function that accepts a value and
historical context, returns a dict with `is_anomaly` (bool),
`method`, `observed`, `expected_range`, `deviation`, and `message`.

**SQL output:** A CTE-based query using window functions where applicable.
Parameterize thresholds as clearly labeled CTEs or variables at the top.

**YAML output:** A monitoring rule block compatible with Great Expectations or
a generic config schema with `rule_name`, `metric`, `method`, `thresholds`,
and `alert_template` keys.

**JSON output:** Equivalent to YAML but in JSON format, suitable for ingestion
by custom monitoring frameworks.

---

### Step 5 — Summarize and Recommend

After generating the rule, provide a short (3–5 line) summary covering:
- Which method was used and why it fits this metric
- Any assumptions made about the distribution or historical data
- One concrete recommendation for improving the rule over time
  (e.g., "Retrain baseline every 90 days" or "Add a minimum sample size guard")
- Any known limitations of the chosen method for this use case

---

## Constraints and Quality Rules

- Never hard-code business-sensitive values or credentials
- Always label placeholder values with `REPLACE_WITH_*` naming convention
- If sample data has fewer than 30 points, warn that thresholds may be unstable
- Do not silently fall back to a different method — always state the method used
- Seasonal rules require at least 2 full cycles of historical data; warn if this
  may not be satisfied
- All thresholds must be explainable in plain language within the output
- Generated code must be runnable without modification when real parameters
  are supplied (no pseudo-code)
- SQL output must be ANSI-compatible unless a dialect is specified by the user

---

## Usage Examples

### Example 1 — Row Count Monitoring in Python

/gen-anomaly-rules metric=daily_order_count method=iqr sensitivity=medium target=python

Claude will generate a Python function that computes IQR-based bounds from a
historical array of daily order counts, returning an anomaly verdict and
structured alert payload with medium sensitivity thresholds (1.5× IQR).

---

### Example 2 — Seasonal Revenue Rule in SQL

/gen-anomaly-rules metric=daily_revenue_usd method=seasonal cadence=daily sensitivity=high target=sql context="Revenue spikes expected on the first of each month due to subscription renewals"

Claude will generate a SQL query using window functions to compute same-day-of-week
historical averages, apply ±10% deviation bands, and exclude the known first-of-month
spike pattern per the provided business context. Output includes a CTE with
clearly parameterized threshold values.

---

### Example 3 — Conversion Rate Rule as YAML Config

/gen-anomaly-rules metric=signup_conversion_rate method=zscore sensitivity=low target=yaml sample_data="mean=0.042, std=0.006, distribution=normal"

Claude will generate a YAML monitoring rule block using ±3.5 standard deviation
thresholds derived from the stated distribution parameters, formatted for use
in a Great Expectations-compatible or custom YAML monitoring config, with an
alert message template referencing the metric name and observed deviation.