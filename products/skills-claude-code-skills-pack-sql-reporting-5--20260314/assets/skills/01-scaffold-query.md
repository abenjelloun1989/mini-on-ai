---
name: scaffold-query
trigger: /scaffold-query
description: >
  Generates a complete, structured SQL query scaffold from a plain-language
  description of the desired report. Use this skill whenever you need to
  translate a reporting requirement into a production-ready SQL skeleton that
  includes CTEs, joins, filters, grouping logic, and inline documentation.
  Ideal for bootstrapping new reports, onboarding analysts to unfamiliar schemas,
  or ensuring consistent query structure across a team.
tags: [sql, reporting, scaffolding, query-building, analytics]
---

# Skill: scaffold-query

## Purpose

Transform a plain-language report description into a complete, annotated SQL query scaffold. The output should be immediately usable as a starting point — not pseudocode, but real, runnable SQL with clearly marked placeholders for values that cannot be inferred from the description.

---

## When to Use This Skill

- You have a reporting requirement written in business language and need a SQL starting point
- You want to enforce consistent query structure (CTEs over subqueries, explicit aliasing, etc.)
- You are scaffolding a report for a schema you will refine later
- You need to communicate query logic to a non-technical stakeholder before implementation

---

## Execution Instructions

Follow these steps in order every time `/scaffold-query` is invoked.

### Step 1 — Parse the Input

Read the user's plain-language description carefully. Extract and identify:

1. **Report subject** — what entity or metric is the report about?
2. **Data sources** — table names, system names, or logical entities mentioned (explicit or implied)
3. **Dimensions** — fields to group or segment by (e.g., region, date, product category)
4. **Metrics** — aggregations or measures required (e.g., total revenue, count of users, average order value)
5. **Filters** — time ranges, status conditions, business rules, or exclusions
6. **Relationships** — any joins implied between entities
7. **Output shape** — is this a summary, a detail row report, a ranked list, a time series?

If any critical element is ambiguous or missing, **state your assumption explicitly** in a comment block at the top of the scaffold before proceeding. Do not ask clarifying questions unless the description is so incomplete that no reasonable scaffold can be produced.

### Step 2 — Plan the Query Structure

Before writing SQL, briefly outline (in a short prose or bullet block above the SQL) the query architecture you will use:

- List each CTE and its purpose in one sentence
- Identify the primary join chain
- Note any aggregation stages
- Flag any fields that will need placeholder values

This plan helps the user validate your understanding before reading 50+ lines of SQL.

### Step 3 — Write the SQL Scaffold

Produce a complete SQL scaffold following all rules in the **Quality Rules** section below.

The scaffold must include, in order:

1. **Header comment block** — report name, description, author placeholder, date placeholder, assumptions
2. **CTEs** — one CTE per logical step; never nest subqueries when a CTE is cleaner
3. **Final SELECT** — the output-facing query against the last CTE
4. **ORDER BY** — always include a sensible default ordering
5. **Inline comments** — every CTE and every non-obvious column or join condition must have a `-- comment` explaining its purpose

### Step 4 — Add a Placeholder Index

After the SQL block, output a Markdown table listing every placeholder used in the scaffold, its location, and what the user needs to supply.

| Placeholder | Location | What to supply |
|---|---|---|
| `<your_schema>` | All table references | Schema name for your environment |
| `'2024-01-01'` | date_spine CTE WHERE clause | Actual reporting start date |

### Step 5 — Offer Next Steps

End with a short **Next Steps** section (3–5 bullet points) suggesting:
- Which placeholders to resolve first
- Which joins may need index investigation
- Whether a metric definition standard should be applied (hint toward `/define-metric`)
- Whether a performance audit is appropriate once data volumes are known (hint toward `/audit-query-performance`)

---

## Quality Rules

Adhere to these rules on every invocation without exception.

**Structure**
- Always use CTEs (`WITH` clauses), never correlated subqueries or nested `SELECT` statements in the `FROM` clause
- Each CTE must do exactly one logical thing — split liberally rather than overloading a single CTE
- The final `SELECT` should read from the last CTE only, not directly from base tables
- Always use explicit `JOIN` syntax (never implicit comma joins)
- Always qualify every column reference with its table alias

**Naming**
- CTE names: `snake_case`, descriptive, noun-first (e.g., `active_customers`, `revenue_by_region`, `date_spine`)
- Column aliases: `snake_case`, no abbreviations unless universally understood (e.g., `id`, `qty` is acceptable; `r_tot_cst` is not)
- Table aliases: short but readable (2–4 characters, derived from table name — `ord` for `orders`, `cust` for `customers`)

**Placeholders**
- Use angle-bracket placeholders for unknowns: `<table_name>`, `<date_column>`, `<threshold_value>`
- Never invent table or column names that were not mentioned or strongly implied — use a placeholder instead
- Mark every placeholder with a `-- PLACEHOLDER:` comment on the same line

**SQL Dialect**
- Default to ANSI SQL unless the user specifies a dialect (PostgreSQL, BigQuery, Snowflake, etc.)
- If dialect-specific syntax would be clearly better (e.g., `DATE_TRUNC` for Postgres, `DATE_SPINE` for BigQuery), note the assumption and provide the ANSI fallback in a comment
- Never use `SELECT *` anywhere in the scaffold

**Formatting**
- Uppercase SQL keywords (`SELECT`, `FROM`, `WHERE`, `GROUP BY`, `LEFT JOIN`, etc.)
- One clause per line; indent continuation lines by 4 spaces
- Commas at the end of lines (not leading commas)
- Blank line between each CTE definition

**Correctness**
- Every column in the final `SELECT` that is not an aggregate must appear in the `GROUP BY` (if aggregation is used)
- Do not use `HAVING` when `WHERE` suffices
- Include `COALESCE` or `NULLIF` guards on metrics that could produce misleading NULLs or division-by-zero errors
- Always cast ambiguous date strings explicitly

---

## Output Format

Respond in this exact order:

1. **Assumptions** (Markdown blockquote) — list any assumptions made due to missing info
2. **Query Architecture** (Markdown bullet list) — brief plan as described in Step 2
3. **SQL Scaffold** (fenced SQL code block)
4. **Placeholder Index** (Markdown table)
5. **Next Steps** (Markdown bullet list)

---

## Usage Examples

### Example 1 — Basic Sales Summary

**Invocation:**
/scaffold-query Monthly revenue by product category for the last 12 months, broken out by region, excluding cancelled orders. We use a Postgres database.

**What Claude will produce:**
A scaffold with a `date_spine` CTE for the 12-month window, an `orders_filtered` CTE that excludes cancelled status, a `revenue_aggregated` CTE grouping by month, category, and region, and a final SELECT with proper date truncation using Postgres `DATE_TRUNC`. Placeholders will mark the schema, the exact status values for cancellation, and the category/region column names.

---

### Example 2 — Customer Cohort Report

**Invocation:**
/scaffold-query I need a cohort retention report showing what percentage of customers who made their first purchase in a given month came back to buy again in each of the following 6 months.

**What Claude will produce:**
A scaffold with a `first_purchase` CTE identifying each customer's acquisition month, a `subsequent_purchases` CTE finding all later orders, a `cohort_activity` CTE joining the two with a month-offset calculation, and a `retention_rates` CTE computing percentages using `COALESCE` to guard against division by zero. A placeholder index will flag the orders table name, customer ID column, and date column.

---

### Example 3 — Executive KPI Dashboard Feed

**Invocation:**
/scaffold-query Scaffold a query for a weekly executive dashboard. It needs: total new signups, total revenue, average order value, and churn count for the current week vs prior week, all in a single row output for easy dashboard ingestion. Snowflake dialect.

**What Claude will produce:**
A scaffold using Snowflake-compatible `DATE_TRUNC('week', ...)` syntax, with separate CTEs for `current_week_signups`, `prior_week_signups`, `current_week_revenue`, `prior_week_revenue`, and `churn_events`, all pivoted into a single-row final SELECT using conditional aggregation. Week-over-week delta columns will be included with `NULLIF` guards on denominators. The placeholder index will flag all source table names and the definition of "churn" (a note will suggest running `/define-metric` for the churn definition).

---

## Notes for Skill Maintainers

- If a user provides a database schema (DDL or table list), incorporate actual column and table names and remove the corresponding placeholders
- If the user has already run `/define-metric`, reference those standardized metric definitions in the scaffold comments rather than inventing aggregation logic
- This skill intentionally does not execute or validate the SQL — it scaffolds only. Pair with `/audit-query-performance` after the query is connected to real data