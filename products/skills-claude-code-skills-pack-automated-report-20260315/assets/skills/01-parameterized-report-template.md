---
name: parameterized-report-template
trigger: /build-report-template
version: 1.0.0
description: >
  Scaffolds a reusable, parameterized report template that accepts dynamic
  inputs (date ranges, filters, metrics) and renders consistent output
  structures ready for downstream formatting, export, and distribution.
  Use this skill whenever you need to create a new recurring report from
  scratch or standardize an existing ad-hoc report into a repeatable template.
tags: [reporting, templates, analytics, automation]
---

# Skill: Parameterized Report Template

## Purpose

Generate a fully wired, parameterized report template file that separates
data-fetching logic, parameter definitions, and rendering concerns. The
output must be immediately usable by the scheduling, export, and delivery
skills in this pack without modification.

## When To Use

- You need a new recurring report (daily, weekly, monthly, ad-hoc)
- An existing script generates a report but has hardcoded dates or filters
- You want to standardize output shape before hooking into PDF/CSV/Slack export
- You are onboarding a new metric or data source into the reporting pipeline

## When NOT To Use

- You only need a one-time query with no reuse intent
- The report has no dynamic parameters (use a static export instead)
- You need to schedule or deliver an already-built template (use the
  scheduling or delivery skills instead)

---

## Execution Instructions

Follow these steps precisely when `/build-report-template` is invoked.

### Step 1 — Gather Requirements

Ask the user (or infer from context) the following before generating any code.
If the invocation already includes arguments, extract from those first.

Required inputs:
1. **Report name** — snake_case identifier (e.g., `weekly_revenue_summary`)
2. **Primary data source** — table name, API endpoint, or data warehouse query
3. **Date range parameter style** — choose one:
   - `rolling` (e.g., last N days)
   - `fixed_window` (explicit start_date / end_date)
   - `fiscal_period` (quarter or month label)
4. **Filter dimensions** — list of filterable fields (e.g., region, product_id, channel)
5. **Metrics** — list of output columns/measures to include
6. **Output format target** — which downstream exports this feeds (pdf, csv, slack, all)

If any required input is missing and cannot be reasonably inferred, pause
and ask before proceeding. Do not generate a template with placeholder TODOs
for required fields.

### Step 2 — Scaffold the Template File

Generate a single Python file named `{report_name}_template.py` with the
following sections in order:

1. **Module docstring** — one-paragraph description of what the report covers,
   who it is for, and how often it typically runs.

2. **Imports block** — include only what is needed; do not import unused libs.

3. **ReportParams dataclass** — typed parameter object with:
   - `date_range` field matching the chosen style
   - One field per filter dimension with sensible defaults (None = no filter)
   - `metrics` field defaulting to the full list but allowing subset selection
   - `output_formats` list field

4. **validate_params(params: ReportParams) -> None** — raises `ValueError`
   with a descriptive message if any parameter combination is invalid
   (e.g., end_date before start_date, empty metrics list).

5. **fetch_data(params: ReportParams) -> pd.DataFrame** — stub with:
   - Clearly marked `# DATA SOURCE:` comment showing the table/endpoint
   - Parameter binding using the params object (no f-string SQL injection)
   - Return type annotation

6. **transform_data(df: pd.DataFrame, params: ReportParams) -> pd.DataFrame**
   — applies filters, aggregations, and column renames to produce a
   normalized output schema.

7. **render_report(params: ReportParams) -> ReportOutput** — orchestrates
   fetch → validate → transform and returns a `ReportOutput` named tuple
   containing: `title`, `generated_at`, `params_snapshot`, `dataframe`,
   `summary_stats`.

8. **CLI entry point** — `if __name__ == "__main__"` block using `argparse`
   that maps CLI flags directly to `ReportParams` fields so the template can
   be run manually or called by the scheduler skill.

### Step 3 — Generate the Schema File

Alongside the template, generate `{report_name}_schema.json` that documents:
- Each parameter name, type, default value, and description
- Each output column name, data type, and description
- Required vs optional parameter flags

This schema is consumed by the scheduling and export skills for validation.

### Step 4 — Generate the Test Fixture

Create `tests/test_{report_name}_template.py` with:
- One test for valid params producing a non-empty DataFrame
- One test per validation rule in `validate_params`
- Mocked data source so tests run without live DB/API access
- A sample `ReportParams` fixture representing the most common use case

### Step 5 — Output Summary

After generating all files, print a summary block:

  FILES CREATED
  ─────────────────────────────────────────────
  {report_name}_template.py      — main template
  {report_name}_schema.json      — parameter + output schema
  tests/test_{report_name}_template.py  — test suite

  NEXT STEPS
  ─────────────────────────────────────────────
  1. Fill in the fetch_data() query body with your actual data source logic
  2. Run: python {report_name}_template.py --help  to verify CLI
  3. Run: pytest tests/test_{report_name}_template.py
  4. Use /schedule-report to attach a run cadence
  5. Use /export-report to configure PDF, CSV, or Slack output

---

## Constraints and Quality Rules

- **No hardcoded dates.** All date logic must flow through `ReportParams`.
- **No raw string SQL.** Use parameterized queries or ORM bindings only.
- **Typed signatures required.** Every function must have full type annotations.
- **Dataclass, not dict.** Parameters must be a `@dataclass` or `Pydantic BaseModel`,
  never a plain dictionary passed around.
- **Consistent output schema.** The `dataframe` inside `ReportOutput` must
  always have the same columns regardless of filter combination — use empty
  rows, not missing columns, when filters return no data.
- **One file per report.** Do not create a generic base class shared across
  reports; each template must be self-contained for portability.
- **No print statements in library code.** Use `logging` with the module logger.
- **Schema file must stay in sync.** If you modify the template params or
  output columns, update the schema JSON in the same change.

---

## Usage Examples

### Example 1 — Weekly Revenue Summary

/build-report-template name=weekly_revenue_summary source=sales.transactions date_range=rolling filters=region,channel metrics=gross_revenue,order_count,aov output=pdf,csv

Generates a rolling 7-day revenue report filterable by region and channel,
exporting to both PDF and CSV. Claude will ask for confirmation of the
metrics list before generating.

---

### Example 2 — Monthly Churn Report with Fixed Window

/build-report-template name=monthly_churn source=analytics.user_events date_range=fixed_window filters=plan_tier,cohort_month metrics=churned_users,churn_rate,ltv_at_churn output=slack

Generates a fixed start/end date churn template that posts a summary to
Slack. The schema file will mark `start_date` and `end_date` as required
with no defaults.

---

### Example 3 — Ad-hoc Conversion Funnel (Minimal Invocation)

/build-report-template name=conversion_funnel source=events.funnel_steps

When minimal arguments are supplied, Claude will interactively ask for
date range style, filters, and metrics before proceeding, then scaffold
the complete template once all required inputs are collected.

---

## Integration Notes

- The scheduler skill (`/schedule-report`) expects the CLI entry point
  generated in Step 2 and the schema file generated in Step 3.
- The export skill (`/export-report`) reads `output_formats` from
  `ReportParams` to determine which renderers to activate.
- The delivery skill (`/deliver-report`) reads `summary_stats` from
  `ReportOutput` to build notification payloads.
- The audit skill (`/audit-report-log`) records the `params_snapshot`
  from `ReportOutput` for traceability.