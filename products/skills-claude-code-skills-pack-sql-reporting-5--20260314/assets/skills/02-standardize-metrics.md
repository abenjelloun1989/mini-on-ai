---
name: standardize-metrics
trigger: /standardize-metrics
description: >
  Converts ad-hoc or inconsistently defined metric calculations into standardized,
  reusable metric definitions. Enforces agreed naming conventions, canonical formulas,
  and inline documentation so that every metric means the same thing across every
  report, dashboard, and query in the codebase.
when_to_use: >
  Use this skill whenever you encounter metrics defined differently across files,
  team members using different column names for the same concept, undocumented
  magic numbers or filter conditions, or when onboarding a new reporting domain
  that needs a single source of truth for calculations.
tags:
  - sql
  - metrics
  - standardization
  - documentation
  - data-quality
---

# Skill: Standardize Metrics

## Purpose

Take raw, ad-hoc, or inconsistently defined metric calculations — found in SQL
files, dbt models, BI tool expressions, spreadsheet formulas, or plain English
descriptions — and produce canonical, fully documented metric definitions that
can be copy-pasted into any query or referenced as a shared library.

---

## How Claude Should Execute This Skill

### Step 1 — Gather Input

Accept one or more of the following inputs from the user:

- Pasted SQL snippets or fragments containing inline calculations
- File paths to `.sql`, `.yml`, or `.py` files to scan
- A plain English description of what a metric is supposed to measure
- A list of metric names with inconsistent definitions found across the codebase
- An existing metrics dictionary in any format that needs reformatting

If the user provides a file path, read the file and extract all calculations,
aggregations, CASE expressions, and derived columns. If the user provides only
a metric name with no formula, ask one clarifying question to confirm the
intended calculation before proceeding.

### Step 2 — Audit and Catalog Existing Definitions

For each metric found or described:

1. Identify every distinct formula variant (even minor differences in filters,
   column names, or NULL handling count as separate variants).
2. Note where each variant appears (file name, line number, or context label).
3. Flag any of the following problems:
   - **Naming inconsistency** — same concept, different names (e.g., `rev`,
     `revenue`, `total_revenue`, `gross_rev`)
   - **Formula drift** — same name, different calculation logic
   - **Undocumented filters** — WHERE or HAVING conditions baked into the
     metric without explanation
   - **Hardcoded values** — magic numbers, hardcoded dates, or literal strings
     inside calculations
   - **NULL ambiguity** — no explicit COALESCE or NULLIF handling
   - **Scope ambiguity** — unclear whether the metric is gross, net, per-user,
     cumulative, etc.

### Step 3 — Propose a Canonical Definition

For each unique metric, produce a canonical definition block using the
structure defined in the Output Format section below. When multiple formula
variants exist:

- Choose the most complete and defensible formula as the canonical version.
- Document the rejected variants and explain why they were not chosen.
- If the correct formula cannot be determined from context alone, present the
  top two candidates and ask the user to confirm before finalizing.

### Step 4 — Apply Naming Conventions

Apply the following naming rules unless the user specifies a different
convention:

- **snake_case** for all metric names
- **Prefix by domain** when a domain is identifiable:
  - Revenue metrics → `rev_`
  - User/customer metrics → `usr_`
  - Engagement metrics → `eng_`
  - Operational metrics → `ops_`
  - Marketing metrics → `mkt_`
- **Suffix by aggregation type** when the metric is a specific aggregation:
  - Totals → `_total`
  - Averages → `_avg`
  - Rates or percentages → `_rate` or `_pct`
  - Counts → `_count`
  - Distinct counts → `_distinct_count`
- **Avoid abbreviations** unless they are universally understood in the domain
  (e.g., `mrr` for Monthly Recurring Revenue is acceptable; `rev_fr_act_cust`
  is not).

If the user supplies their own naming convention guide, follow it exactly and
note any conflicts with the input metrics.

### Step 5 — Write Inline SQL Documentation

Each canonical metric must include a SQL comment block directly above the
formula. The comment block must answer:

1. **What it measures** — one sentence business definition
2. **Formula logic** — plain English explanation of the calculation
3. **Included/excluded** — what is deliberately included or excluded and why
4. **Grain** — the expected row grain at which this metric is computed
5. **Owner** — leave as `-- Owner: [team or individual]` placeholder if unknown
6. **Last reviewed** — leave as `-- Last reviewed: [YYYY-MM-DD]` placeholder

### Step 6 — Generate Output Artifacts

Produce the following outputs in order:

1. **Audit Summary** — a short table listing every variant found, its
   location, and the problem flags raised.
2. **Canonical Metric Definitions** — one block per metric, formatted as
   described below.
3. **Migration Notes** — for each variant that differs from the canonical
   definition, a one-line note explaining what needs to change in the source
   file.
4. **Optional: dbt Metrics YAML** — if the user requests it or if dbt files
   are detected in the input, also render the definitions in dbt Semantic Layer
   `metrics:` YAML format.

---

## Output Format

### Canonical Metric Definition Block (SQL)

Each block follows this exact structure:

    -- ============================================================
    -- Metric: <canonical_metric_name>
    -- ============================================================
    -- Definition : <One-sentence business definition>
    -- Formula    : <Plain English description of the calculation>
    -- Includes   : <What is counted/summed and under what conditions>
    -- Excludes   : <What is explicitly excluded and why>
    -- Grain      : <Row grain, e.g. "one row per order" or "one row per user per day">
    -- Owner      : <Team or individual responsible>
    -- Last reviewed: <YYYY-MM-DD>
    -- ============================================================
    <canonical_sql_expression> AS <canonical_metric_name>

### Audit Summary Table

| Variant Name | Location | Formula | Problems Flagged |
|---|---|---|---|
| `rev` | reports/sales.sql:14 | `SUM(amount)` | Naming: too abbreviated; NULL ambiguity |
| `total_revenue` | dashboards/kpis.sql:88 | `SUM(COALESCE(amount,0))` | None — promoted to canonical |

### Migration Note Format

For each non-canonical variant:

    -- MIGRATION: Replace `rev` in reports/sales.sql:14
    --   Change : SUM(amount)
    --   To     : SUM(COALESCE(amount, 0))
    --   Rename : rev → rev_gross_total

---

## Constraints and Quality Rules

- **Never silently drop a variant.** Every formula found must appear in the
  audit summary even if it is clearly wrong.
- **Never invent business logic.** If the correct filter or scope cannot be
  inferred from the code or context, ask before assuming.
- **Preserve dialect compatibility.** If the input SQL uses a specific dialect
  (BigQuery, Snowflake, Redshift, Postgres, DuckDB), keep the canonical
  formula in the same dialect. Note the dialect at the top of the output.
- **No hardcoded values in canonical definitions.** Replace any magic numbers
  or literal dates with named comments explaining what the value represents,
  or suggest a parameter/variable approach.
- **NULL handling is mandatory.** Every SUM or AVG in a canonical definition
  must use COALESCE or equivalent. Every division must use NULLIF in the
  denominator.
- **One definition per metric name.** A canonical metric name must map to
  exactly one formula. If two legitimately different concepts share a name,
  disambiguate them with a suffix before finalizing.
- **Do not modify source files** unless the user explicitly asks. Default
  behavior is to output definitions and migration notes only.

---

## Usage Examples

### Example 1 — Reconcile Revenue Variants Across Two Files

    /standardize-metrics

    I have two files with conflicting revenue definitions:

    -- File: warehouse/sales_report.sql
    SELECT
      SUM(order_total) AS revenue
    FROM orders
    WHERE status != 'cancelled'

    -- File: dashboards/exec_summary.sql
    SELECT
      SUM(COALESCE(gross_amount, 0)) AS total_rev
    FROM orders
    WHERE order_status NOT IN ('cancelled', 'refunded')
      AND created_at >= '2023-01-01'

    Please standardize these into one canonical revenue metric.

Claude will audit both variants, flag the mismatched column names
(`order_total` vs `gross_amount`), the different exclusion lists, and the
hardcoded date filter in the second file. It will ask whether refunds should
be excluded from the canonical definition, then produce a single canonical
`rev_gross_total` definition with migration notes for both files.

---

### Example 2 — Standardize a New Metric from a Plain English Description

    /standardize-metrics

    We need a standard "Customer Activation Rate" metric. It should be the
    percentage of signed-up users who completed at least one purchase within
    their first 30 days. We use Snowflake SQL. There's no existing definition —
    this is net new.

Claude will confirm the grain (one row per user), clarify whether "signed-up"
means account creation date or email verification date, then produce a fully
documented canonical metric definition in Snowflake SQL with the correct
`NULLIF` denominator guard and a `-- Grain: one row per user` annotation.

---

### Example 3 — Bulk Standardize a dbt Project's Ad-Hoc Metrics

    /standardize-metrics --output=dbt-yaml

    Please scan all .sql files under models/marts/ and extract every metric
    calculation. I want:
    1. An audit of all inconsistencies found
    2. Canonical SQL definitions
    3. A dbt Semantic Layer metrics YAML file I can drop into my project

Claude will read each file in `models/marts/`, catalog every aggregation and
derived column, group them by apparent business concept, apply naming
conventions, produce the audit summary and canonical SQL blocks, and then
render a complete `metrics.yml` file in dbt Semantic Layer format ready for
direct use.

---

## Notes for Skill Maintenance

- If the team adopts a formal metrics catalog tool (e.g., dbt Semantic Layer,
  Looker LookML, Cube.dev), update the Output Format section to include that
  tool's native definition syntax as an additional artifact.
- Naming convention prefixes can be overridden per-project by placing a
  `metrics-conventions.yml` file in the project root. If that file is detected,
  Claude should load it and apply it instead of the defaults above.
- This skill pairs naturally with `scaffold-query` (for building queries that
  consume these metrics) and `audit-query-performance` (for checking whether
  metric calculations are causing slow query plans).