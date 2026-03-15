---
name: gen-row-validations
trigger: /gen-row-validations
description: >
  Generates row-level data validation checks covering null rates, range bounds,
  referential integrity, and regex pattern matching. Outputs either executable
  dbt tests (schema.yml + generic tests) or a Great Expectations suite
  (JSON/Python checkpoint). Use this skill whenever you need to enforce data
  quality contracts at the row level before data reaches downstream models,
  dashboards, or stakeholders.
when_to_use: >
  - A new table or model is entering a pipeline and needs baseline quality gates
  - A data contract has been defined and must be translated into executable checks
  - An incident revealed missing, out-of-range, or malformed values and you need
    preventive rules going forward
  - An analytics lead wants automated freshness + validity enforcement in CI
tags: [data-quality, dbt, great-expectations, validation, testing]
---

# Skill: gen-row-validations

## Purpose

Translate a table schema, data contract description, or sample data into
executable row-level validation checks. Output is immediately usable in a dbt
project or a Great Expectations suite — no manual editing required to run.

---

## Inputs Claude Should Collect

Before generating output, Claude must identify:

1. **Target table / model name** — e.g., `orders`, `fct_payments`, `raw.events`
2. **Column list with types** — provided inline, from a schema file, or inferred
   from sample data the user pastes
3. **Output format** — `dbt` (default) or `great-expectations`
4. **Validation categories requested** (default: all four):
   - `nulls` — null rate thresholds per column
   - `ranges` — numeric / date min–max bounds
   - `referential` — foreign key or accepted-values checks
   - `regex` — pattern matching for string fields
5. **Severity level** — `warn` or `error` (dbt) / `warning` or `failure`
   (Great Expectations). Default: `error` / `failure`
6. **Optional context** — existing data contract text, SLA notes, known bad
   patterns, or sample rows

If critical inputs are missing, Claude must ask one clarifying question before
proceeding. Do not generate placeholder output with unknown column names.

---

## Execution Steps

### Step 1 — Parse Schema

Read the provided schema, DDL, or sample data. Build an internal column
inventory:

- Column name
- Data type (string, numeric, date/timestamp, boolean, id/foreign key)
- Nullable flag if stated
- Any domain hints from names (e.g., `email`, `zip_code`, `user_id`, `amount`)

### Step 2 — Classify Columns by Validation Type

Apply the following heuristics automatically unless the user overrides:

| Column characteristic | Auto-applied checks |
|-----------------------|---------------------|
| Any column named `*_id` or typed as FK | `not_null` + `relationships` (dbt) or `expect_column_values_to_not_be_null` + referential suite |
| Numeric columns (`amount`, `price`, `qty`, `count`, `rate`) | `not_null` + range bounds |
| Date / timestamp columns | range bounds (not before 2000-01-01, not after now + 1 day) |
| String columns with domain names (`email`, `phone`, `zip`, `status`, `country_code`) | regex pattern |
| Boolean columns | `accepted_values: [true, false]` |
| Any column with `NOT NULL` in DDL | `not_null` |

### Step 3 — Generate Validation Rules

**For dbt output**, produce:
1. A `schema.yml` block under the correct model name with `tests:` entries per
   column
2. Any custom generic test macros needed (e.g., `not_null_proportion`) as
   separate `.sql` macro stubs
3. A brief `# Validation summary` comment block at the top of the YAML

**For Great Expectations output**, produce:
1. A Python file using the `great_expectations` fluent API
2. One `ExpectationSuite` named `<table_name>.row_validations`
3. Expectations grouped by category with inline comments explaining each rule
4. A runnable `checkpoint` block at the bottom

### Step 4 — Apply Severity

- dbt: add `config: severity: error` (or `warn`) to each test block
- Great Expectations: set `result_format` and `mostly` threshold accordingly
  (`mostly: 1.0` for `failure`, `mostly: 0.95` for `warning` unless user
  specifies a different threshold)

### Step 5 — Output Final Artifact

Emit the complete file(s) in a single fenced code block per file. Follow each
file with a **Validation Coverage Summary** table listing every column, which
checks were applied, and the severity.

---

## Output Format Rules

- dbt YAML must be valid indented YAML — no tabs, consistent 2-space indent
- Great Expectations Python must be compatible with GE >= 0.18 (fluent API)
- All regex patterns must be valid Python `re` module syntax
- Numeric bounds must use real numbers, not pseudocode (e.g., `0` not `<zero>`)
- Do not emit TODO comments or placeholder values — if a bound cannot be
  inferred, ask the user before generating
- File names follow convention:
  - dbt: `models/<model_name>/schema.yml`
  - GE: `validations/<table_name>_suite.py`

---

## Constraints and Quality Rules

- **Never invent column names** not present in the user-supplied schema
- **Never use generic bounds** (e.g., `max: 9999999`) without user confirmation
  when the column has a clear domain (e.g., `age` should cap at 120)
- Each check must be independently runnable — no dependencies between test
  blocks that would cause silent failures
- For referential integrity checks in dbt, always specify both `to:` table and
  `field:` — never leave them as placeholders
- Null rate thresholds: default is `not_null` (0% nulls allowed) unless the
  column is explicitly nullable, in which case use `not_null_proportion`
  with `at_least: 0.95` as the default
- Regex patterns for common domains must use these validated defaults:
  - email: `^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`
  - US zip: `^\d{5}(-\d{4})?$`
  - phone (E.164): `^\+?[1-9]\d{1,14}$`
  - ISO country code: `^[A-Z]{2}$`
  - UUID: `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`

---

## Usage Examples

### Example 1 — dbt tests for an orders table

/gen-row-validations

Table: fct_orders
Format: dbt
Columns:
  order_id UUID NOT NULL
  customer_id INT NOT NULL (FK → dim_customers.customer_id)
  order_date DATE NOT NULL
  status VARCHAR (values: placed, shipped, delivered, cancelled)
  total_amount NUMERIC NOT NULL
  email VARCHAR

Expected output: `models/fct_orders/schema.yml` with not_null, relationships,
accepted_values, range, and regex (email) tests at error severity.

---

### Example 2 — Great Expectations suite with nullable columns and warnings

/gen-row-validations

Table: raw.events
Format: great-expectations
Severity: warning
Columns:
  event_id VARCHAR NOT NULL
  user_id INT NOT NULL
  event_type VARCHAR NOT NULL (values: click, view, purchase, signup)
  occurred_at TIMESTAMP NOT NULL
  session_duration_seconds INT (nullable, min 0 max 86400)
  referrer_url VARCHAR (nullable)

Expected output: `validations/raw_events_suite.py` with a GE fluent suite,
`mostly: 0.95` on nullable columns, and a runnable checkpoint block.

---

### Example 3 — Targeted regex + null checks only

/gen-row-validations

Table: dim_customers
Format: dbt
Checks: nulls, regex
Columns:
  customer_id INT NOT NULL
  email VARCHAR NOT NULL
  phone VARCHAR
  country_code CHAR(2) NOT NULL
  zip_code VARCHAR

Expected output: `models/dim_customers/schema.yml` with only not_null and
regex pattern tests — no range or referential checks generated.

---

## Validation Coverage Summary (Template)

After emitting the file(s), always append this table:

| Column | not_null | range | referential | regex | severity |
|--------|----------|-------|-------------|-------|----------|
| ...    | ✓ / –   | ✓ / –| ✓ / –      | ✓ / –| error/warn |

Use `✓` for applied, `–` for not applicable or not requested.