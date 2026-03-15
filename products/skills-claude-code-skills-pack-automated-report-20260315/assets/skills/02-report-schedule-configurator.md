---
name: report-schedule-configurator
trigger: /schedule-report
description: >
  Generates scheduling logic for recurring report runs. Use this skill when you
  need to configure cron expressions, interval-based schedules, or workflow
  trigger definitions for automated reports. Handles timezone normalization,
  retry policies, skip-holiday rules, and produces ready-to-use config output
  in multiple formats (cron, YAML, JSON, Airflow DAG stubs). Best used after
  a report template exists and you need to operationalize its delivery cadence.
tags: [scheduling, automation, cron, reporting, operations]
version: 1.0.0
---

# Skill: Report Schedule Configurator

## Purpose

Transform a plain-language report cadence description into production-ready
scheduling configuration. Output is immediately usable in cron daemons,
workflow orchestrators (Airflow, Prefect, Dagster), CI/CD schedulers, or
custom job runners.

---

## When to Use This Skill

- You know a report needs to run on a recurring basis and need the exact schedule config
- You have timezone complexity (e.g., "run at 9 AM Eastern, but the server is UTC")
- You need retry logic for flaky data pipelines
- You want to skip report runs on public holidays or business blackout periods
- You need to export the schedule config in a specific format for your stack

---

## Execution Instructions

Follow these steps in order every time `/schedule-report` is invoked.

### Step 1 — Gather Schedule Requirements

If the user's invocation is incomplete, ask clarifying questions before
generating any output. Required information:

- **Frequency**: How often should the report run? (daily, weekly, monthly, custom)
- **Run time**: What time of day? (e.g., "9 AM", "end of business")
- **Timezone**: What timezone does the requester think in? What timezone does the server run in?
- **Report name or ID**: Used to label the generated config
- **Target format**: cron string, YAML config, JSON config, Airflow DAG stub, or all

Optional but ask if not provided:
- Retry policy: How many retries on failure? Delay between retries?
- Holiday skip rules: Which country/region calendar? What to do instead — skip entirely, or run next business day?
- Dependency gates: Does this report depend on a data refresh completing first?
- Notification on failure: Where should alerts go?

Do not fabricate values for timezone, retry count, or holiday region.
Ask explicitly if missing.

---

### Step 2 — Resolve Timezone

Always produce two timezone representations:
1. **Local time** — as the requester described it
2. **UTC equivalent** — what the cron expression or scheduler config should use

Use standard IANA timezone names (e.g., `America/New_York`, `Europe/London`).
Never use abbreviations like EST or BST in config output — they are ambiguous.

If the user gives an abbreviation, resolve it and confirm:
> "I'm treating EST as America/New_York (UTC-5 standard, UTC-4 daylight). Is that correct?"

For schedules that must stay pinned to a wall-clock time (e.g., always 9 AM
Eastern regardless of DST), note whether the cron expression needs to shift
seasonally and provide both summer and winter variants if relevant.

---

### Step 3 — Generate the Cron Expression

Produce a standard 5-field cron expression:

  ┌───── minute (0–59)
  │ ┌───── hour (0–23, in UTC)
  │ │ ┌───── day of month (1–31)
  │ │ │ ┌───── month (1–12)
  │ │ │ │ ┌───── day of week (0–7, 0 and 7 = Sunday)
  │ │ │ │ │
  * * * * *

Label every field. Include a plain-English translation directly beneath the
expression. Flag any expressions that have known compatibility differences
between cron implementations (e.g., Vixie cron vs. POSIX vs. AWS EventBridge).

---

### Step 4 — Generate Retry Policy

Produce retry config based on user input or sensible defaults:

Default retry policy (use unless overridden):
- Max retries: 3
- Retry delay: 5 minutes, exponential backoff (5m, 10m, 20m)
- Failure alert after: all retries exhausted
- Dead-letter behavior: log to audit table, send alert

Output retry config in the requested format. Example YAML:

  retry_policy:
    max_attempts: 3
    backoff_strategy: exponential
    initial_delay_minutes: 5
    alert_on_exhaustion: true

---

### Step 5 — Generate Holiday Skip Rules

If holiday skipping is requested:

- Identify the holiday calendar region (ISO 3166-1 country code or named region)
- Define the skip behavior: `skip` (no run) or `defer` (run next business day)
- Output as a structured config block, not embedded in the cron expression itself
- Recommend a holiday calendar library or API appropriate to the user's stack
  (e.g., `holidays` Python library, Airflow's `HolidayCalendar`, Google Calendar API)

Example YAML:

  holiday_rules:
    region: US
    calendar: federal_holidays
    behavior: defer
    defer_to: next_business_day

---

### Step 6 — Assemble Final Output

Produce a single, consolidated output block containing all of the following
sections (omit sections that are not applicable):

1. **Schedule Summary** — Plain English description of what was configured
2. **Cron Expression** — With field labels and plain-English translation
3. **Timezone Note** — Local vs. UTC, DST considerations
4. **YAML Config Block** — Full schedule config ready to paste
5. **JSON Config Block** — Same config in JSON (omit if user did not request)
6. **Airflow DAG Stub** — Minimal Python snippet (omit if user did not request)
7. **Retry Policy** — Structured config block
8. **Holiday Rules** — If applicable
9. **Validation Checklist** — 3–5 items the user should verify before deploying

---

## Output Quality Rules

- Every cron expression must be validated against standard cron syntax before output
- Never output a cron expression without its plain-English translation
- All times in config files must be UTC; local time appears only in comments
- YAML must be valid and consistently indented (2 spaces)
- JSON must be valid and pretty-printed (2-space indent)
- If a schedule has DST edge cases, call them out explicitly — do not silently ignore
- Flag if a schedule would fire more than 500 times per month (unusual, may indicate error)
- Do not invent holiday calendar data — reference established libraries or APIs

---

## Constraints

- Do not generate schedules with sub-minute granularity (use a queue/event system instead)
- Do not embed business logic (data transforms, report content) in scheduling output
- Keep Airflow DAG stubs minimal — schedule_interval and basic operator only, no DAG content
- If the user asks for a "real-time" schedule, redirect to event-driven architecture guidance
- Maximum one config output per format per invocation — no variations unless explicitly requested

---

## Usage Examples

### Example 1 — Simple Weekly Report

/schedule-report name="Weekly Sales Summary" frequency="every Monday" time="8 AM" timezone="Chicago" format="cron, YAML" retries=3

Expected output includes:
- Cron: `0 14 * * 1` (UTC, with CST/CDT note)
- YAML block with retry policy
- DST note about shifting between UTC-6 and UTC-5

---

### Example 2 — Monthly Report with Holiday Skipping

/schedule-report name="Monthly Finance Close" frequency="first business day of month" time="6 AM ET" format="YAML, Airflow" skip-holidays="US federal" defer-behavior="next_business_day"

Expected output includes:
- Cron approximation with note that first-business-day logic requires holiday-aware scheduler
- Airflow DAG stub using `BranchPythonOperator` or `HolidayCalendar`
- Holiday rules config block for US federal calendar
- Explicit note that pure cron cannot handle "first business day" without wrapper logic

---

### Example 3 — High-Frequency Operational Report

/schedule-report name="Hourly Ops Digest" frequency="every hour" time="on the hour" timezone="UTC" format="cron, JSON" retries=2 alert-on-failure="ops-alerts@company.com"

Expected output includes:
- Cron: `0 * * * *`
- JSON config with retry and alert fields populated
- Flag that 744 monthly runs is high-volume; confirm this is intentional
- Note that no holiday skipping is applicable for hourly cadences

---

## Notes for Claude

- Always confirm timezone interpretation before generating config if the user used an abbreviation
- If the user provides conflicting signals (e.g., "daily at 9 AM every weekday"), resolve the conflict explicitly before generating output
- Prefer YAML as the default format if the user does not specify
- This skill produces scheduling config only — it does not generate report content, delivery logic, or recipient lists (those are handled by other skills in this pack)