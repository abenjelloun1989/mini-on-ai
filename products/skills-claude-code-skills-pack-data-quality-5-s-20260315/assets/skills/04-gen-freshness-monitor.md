---
name: gen-freshness-monitor
trigger: /gen-freshness-monitor
description: >
  Generates data freshness monitoring configurations that track last-updated
  timestamps across tables and partitions, define staleness thresholds aligned
  to business SLAs, and emit structured alerts when data falls behind schedule.
  Use this skill whenever you need to detect delayed or stale data before it
  surfaces in dashboards or downstream pipelines.
when_to_use: >
  Invoke when onboarding a new table into a monitoring stack, when an SLA
  agreement has been defined for a data asset, or when a stakeholder has
  reported discovering stale data too late. Best used after source tables,
  update cadences, and alert channels are known.
---

# Skill: gen-freshness-monitor

## Purpose

Produce a complete, ready-to-deploy freshness monitoring configuration for one
or more data tables or partitions. Output includes timestamp detection logic,
staleness threshold rules, alert severity tiers, and remediation guidance —
formatted for the target monitoring framework specified by the user.

---

## Inputs to Collect

Before generating any output, Claude must identify the following. If any are
missing from the invocation, ask the user in a single consolidated prompt
before proceeding.

1. **Table(s) or dataset(s)** — fully qualified names (e.g., `analytics.orders`)
2. **Expected update cadence** — how often each table should refresh
   (e.g., every 15 minutes, hourly, daily at 06:00 UTC)
3. **Timestamp column(s)** — the column(s) that indicate last update
   (e.g., `updated_at`, `_etl_loaded_at`, partition date column)
4. **SLA window** — maximum acceptable lag before an alert fires
   (e.g., data must be no older than 2 hours past scheduled refresh)
5. **Target framework** — where the config will be deployed:
   - `dbt` (dbt Cloud or dbt Core freshness blocks)
   - `great_expectations` (GE checkpoint YAML)
   - `monte_carlo` (Monte Carlo monitors API-style JSON)
   - `custom_sql` (portable SQL + cron alert query)
   - `generic` (framework-agnostic YAML, default if unspecified)
6. **Alert channels** — where notifications should go
   (e.g., Slack `#data-alerts`, PagerDuty, email, webhook URL)
7. **Severity tiers** *(optional)* — whether to distinguish warn vs. error
   thresholds (defaults to a single error threshold if not provided)
8. **Partition column** *(optional)* — if the table is partitioned, the column
   used to identify the latest partition (e.g., `event_date`, `dt`)

---

## Execution Steps

### Step 1 — Validate Inputs

- Confirm all required inputs (1–6) are present.
- If any are missing, generate a single consolidated question block asking only
  for what is missing. Do not proceed until inputs are confirmed.
- If the user provides a cadence but no SLA window, default the SLA window to
  `cadence × 2` and state this assumption explicitly.

### Step 2 — Analyze Cadence and Derive Thresholds

For each table:

- Parse the stated cadence into minutes (e.g., "daily at 06:00 UTC" = 1440 min
  interval with an anchor time).
- Calculate threshold values:
  - **warn_after**: SLA window × 0.75 (if severity tiers requested)
  - **error_after**: SLA window exactly as stated
  - **critical_after**: SLA window × 1.5 (only if pager/on-call channel given)
- Round thresholds to the nearest sensible unit (minutes for sub-hourly cadence,
  hours for daily or slower cadence).
- Note if the table is partitioned and adjust logic to check the latest partition
  rather than a single row max timestamp.

### Step 3 — Generate Monitoring Configuration

Produce the configuration in the target framework format. Follow the format
rules in the Output Formats section below. Every configuration must include:

- Table identifier and timestamp column
- Threshold definitions (warn / error / critical as applicable)
- A human-readable description of what the monitor checks
- Alert routing to the specified channels
- A `remediation_hint` field with 2–3 concrete first-response actions

### Step 4 — Generate Companion SQL Verification Query

Always include a standalone SQL query the user can run manually to verify
freshness right now, regardless of the target framework. Format as a clearly
labeled code block. The query must:

- Return `table_name`, `last_updated_at`, `minutes_since_update`,
  `is_stale` (boolean), and `threshold_minutes`
- Work in standard SQL (note any dialect-specific adjustments needed)

### Step 5 — Summarize and Flag Risks

After the configuration output, provide a short summary (≤10 lines) that:

- Lists each monitor created and its thresholds
- Calls out any assumptions made (e.g., defaulted SLA windows)
- Flags tables where the timestamp column may not reliably reflect source
  freshness (e.g., if only an ETL load time is available, not a source
  system timestamp)
- Notes if any cadence is unusually aggressive (< 5 minutes) or slow (> 7 days)
  and asks the user to confirm

---

## Output Formats

### generic / default YAML

    freshness_monitors:
      - table: <schema.table>
        description: <human-readable string>
        timestamp_column: <column_name>
        partition_column: <column_name or null>
        schedule:
          cadence_minutes: <int>
          anchor_time_utc: <HH:MM or null>
        thresholds:
          warn_after_minutes: <int or null>
          error_after_minutes: <int>
          critical_after_minutes: <int or null>
        alerts:
          - channel: <channel_name>
            severity: <warn|error|critical>
        remediation_hint: |
          <step 1>
          <step 2>
          <step 3>

### dbt

Produce a `sources.yml` block using dbt's native `freshness:` syntax with
`warn_after` and `error_after` using `count` and `period` keys. Include a
comment block above each source node explaining the SLA.

### great_expectations

Produce a GE `ExpectationSuite`-style YAML with
`expect_column_values_to_be_dateutil_parseable` and a custom
`expect_table_row_count_to_be_freshness_compliant` note explaining that a
custom expectation or `expect_column_max_to_be_between` with a dynamic
`max_value` of `NOW() - INTERVAL` is required.

### custom_sql

Produce a SQL alert query intended to be run on a cron schedule. Output as
a single query that returns rows only when staleness is detected.

---

## Constraints and Quality Rules

- Never invent timestamp column names. Use only what the user provides; if
  unsure, surface the assumption explicitly.
- Always prefer source-system timestamps over ETL load timestamps when both
  are available. If only a load timestamp is available, add a warning comment
  in the config.
- Thresholds must be positive integers. Do not produce fractional minute values.
- Do not generate alert channel credentials, tokens, or webhook URLs — only
  reference the channel name/identifier the user provides.
- If multiple tables share the same cadence and SLA, consolidate them under a
  shared threshold block rather than repeating identical values.
- All time values in configurations must be expressed in UTC unless the user
  explicitly specifies a timezone; if so, note the timezone offset in a comment.
- Output must be directly copy-pasteable. No placeholder prose inside config
  blocks (e.g., do not write `<insert your token here>` inside a YAML value —
  use an environment variable reference like `${SLACK_WEBHOOK_URL}` instead).

---

## Examples

### Example 1 — Single daily table, dbt framework

    /gen-freshness-monitor
    Table: analytics.daily_revenue_summary
    Timestamp column: dbt_updated_at
    Cadence: daily at 07:00 UTC
    SLA: data must be fresh within 3 hours of scheduled run
    Framework: dbt
    Alert channel: Slack #data-alerts (warn), PagerDuty revenue-oncall (error)

Expected output: a `sources.yml` freshness block with `warn_after: {count: 2,
period: hour}` and `error_after: {count: 3, period: hour}`, plus the companion
SQL verification query and a risk summary noting that `dbt_updated_at` is a
model completion timestamp rather than a source system timestamp.

---

### Example 2 — Partitioned event table, custom SQL framework

    /gen-freshness-monitor
    Table: events.clickstream
    Partition column: event_date
    Timestamp column: max(event_timestamp) within latest partition
    Cadence: hourly
    SLA: no more than 2 hours stale
    Framework: custom_sql
    Alert channel: webhook https://hooks.example.com/data-alerts
    Severity tiers: yes

Expected output: a SQL alert query that checks the latest partition date,
computes max event_timestamp, and returns a row flagged as warn (90 min),
error (120 min), or critical (180 min); plus the companion verification query.

---

### Example 3 — Multiple tables, generic YAML

    /gen-freshness-monitor
    Tables: warehouse.inventory_snapshot, warehouse.purchase_orders,
            warehouse.shipment_tracking
    Timestamp column (all): updated_at
    Cadence: every 30 minutes
    SLA: within 1 hour
    Framework: generic
    Alert channel: Slack #warehouse-ops

Expected output: a single generic YAML file with three monitor entries sharing
a consolidated threshold block (warn: 45 min, error: 60 min), the companion
SQL query as a UNION across all three tables, and a summary noting that all
three monitors share identical thresholds and can be managed as a group.

---

## Notes for Claude

- Keep configuration output clean and directly usable — no filler commentary
  inside code blocks.
- Place all explanatory text, assumptions, and risk flags outside of and after
  the configuration code blocks.
- If the user asks for multiple frameworks in one invocation, produce each as a
  separate clearly labeled section.
- When in doubt about a threshold or cadence interpretation, state the
  interpretation you used and ask the user to confirm rather than silently
  choosing.