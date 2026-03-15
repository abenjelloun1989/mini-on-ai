---
name: validate-migration-preflight
trigger: /preflight-check
description: >
  Runs pre-flight checks against a target database before applying a migration.
  Detects lock contention risks, missing indexes, constraint violations, and
  estimates execution time. Use this before every schema change in staging or
  production to catch problems that would cause downtime or data loss.
when_to_use: >
  Always run before executing any migration script in a non-development
  environment. Especially critical for tables with >1M rows, tables under
  heavy write load, or changes involving NOT NULL constraints, foreign keys,
  or column type alterations.
---

# Skill: validate-migration-preflight

## Purpose

Analyze a migration script and the live target database to surface risks
before a single line of DDL executes. Produce a structured report that gives
the engineer a clear go / no-go decision with specific remediation steps for
every issue found.

---

## Inputs

The user will provide one or more of the following. Ask for anything missing
before proceeding.

| Input | Required | Description |
|---|---|---|
| Migration file or SQL | Yes | Path to file or inline SQL |
| Target environment | Yes | staging / production / named env |
| Database connection | Yes | DSN, env var name, or config key |
| Table names affected | Auto-detected | Parsed from the migration SQL |
| Maintenance window | Optional | How many minutes are available |

If no migration SQL is provided, check the current directory for files
matching `*.sql`, `migrations/*.sql`, or `db/migrate/*.rb` and ask the user
to confirm which file to check.

---

## Execution Steps

Follow these steps in order. Do not skip steps. Show progress as you work.

### Step 1 — Parse the Migration

1. Read the migration file or inline SQL provided by the user.
2. Extract every DDL and DML statement.
3. Identify the operation type for each statement:
   - ADD COLUMN, DROP COLUMN, RENAME COLUMN, ALTER COLUMN
   - ADD CONSTRAINT, DROP CONSTRAINT, ADD INDEX, DROP INDEX
   - CREATE TABLE, DROP TABLE, RENAME TABLE
   - UPDATE, DELETE (bulk data changes)
4. List the affected tables and operations in a summary block at the top
   of your output before running any checks.

### Step 2 — Gather Table Statistics

For each affected table, run the following queries against the target database.
Use read-only queries only — never execute writes during pre-flight.

Row count:
  SELECT COUNT(*) FROM {table};
  (For large tables, use: SELECT reltuples FROM pg_class WHERE relname = '{table}';)

Table size:
  SELECT pg_size_pretty(pg_total_relation_size('{table}'));

Current locks:
  SELECT pid, mode, granted, query
  FROM pg_locks l
  JOIN pg_stat_activity a ON l.pid = a.pid
  WHERE relation = '{table}'::regclass;

Active long-running queries on the table:
  SELECT pid, now() - query_start AS duration, state, query
  FROM pg_stat_activity
  WHERE query ILIKE '%{table}%'
    AND state != 'idle'
    AND query_start < now() - interval '30 seconds';

Autovacuum status:
  SELECT last_autovacuum, last_autoanalyze, n_dead_tup
  FROM pg_stat_user_tables
  WHERE relname = '{table}';

### Step 3 — Run Lock Contention Check

For each DDL statement, determine the lock level it requires:

- ACCESS EXCLUSIVE: ALTER TABLE (most forms), DROP TABLE, TRUNCATE
- SHARE: CREATE INDEX (non-concurrent)
- No table lock: CREATE INDEX CONCURRENTLY

Flag HIGH RISK if:
- The operation requires ACCESS EXCLUSIVE AND the table has >100k rows
- Any existing lock on the table is not immediately granted
- A long-running query (>30s) is active on the table

Flag MEDIUM RISK if:
- The operation requires ACCESS EXCLUSIVE AND the table has 10k–100k rows
- Autovacuum is currently running on the table

Flag LOW RISK if:
- The operation uses CONCURRENTLY or targets a table with <10k rows

### Step 4 — Run Index Analysis

For each affected table:

1. Check if the migration adds a unique constraint or foreign key. Verify
   whether a supporting index already exists.
2. Check if the migration drops an index that is used by an existing
   foreign key constraint.
3. For new indexes being created without CONCURRENTLY on a table >100k rows,
   flag and recommend using CREATE INDEX CONCURRENTLY instead.
4. Estimate index build time using: ~1 minute per 1M rows as a baseline.
   Adjust up if the table has high dead tuple count (bloat factor).

### Step 5 — Run Constraint Violation Check

For any constraint being added (NOT NULL, UNIQUE, CHECK, FOREIGN KEY):

NOT NULL check:
  SELECT COUNT(*) FROM {table} WHERE {column} IS NULL;

UNIQUE check:
  SELECT {column}, COUNT(*) FROM {table}
  GROUP BY {column} HAVING COUNT(*) > 1;

FOREIGN KEY check:
  SELECT COUNT(*) FROM {child_table}
  WHERE {fk_column} NOT IN (SELECT {pk_column} FROM {parent_table});

CHECK constraint:
  SELECT COUNT(*) FROM {table} WHERE NOT ({check_expression});

If any query returns a count > 0, mark that check as FAILED and include
the exact count of violating rows in the report.

### Step 6 — Estimate Execution Time

Produce an estimated execution time for the full migration:

- DDL on empty or tiny table (<10k rows): <1 second
- ADD COLUMN with DEFAULT (pre-Postgres 11): rows × 0.5ms
- ADD COLUMN with DEFAULT (Postgres 11+): <1 second
- CREATE INDEX non-concurrent: ~1 min per 1M rows
- CREATE INDEX CONCURRENTLY: ~2–3 min per 1M rows
- ALTER COLUMN type rewrite: ~2 min per 1M rows
- Bulk UPDATE/DELETE: estimate from row count × 0.1ms baseline

Sum all estimates. If total exceeds the user's stated maintenance window,
flag the migration as TOO LONG and recommend splitting or sequencing it.

### Step 7 — Compile and Output the Report

Produce the final report using the format defined below. Do not omit any
section even if there are no issues in that section (write "None detected").

---

## Output Format

Pre-Flight Check Report
=======================
Migration:    {filename or "inline SQL"}
Target:       {environment} — {database name}
Checked at:   {timestamp}
Overall:      GO ✅  |  NO-GO ❌  |  PROCEED WITH CAUTION ⚠️

OVERALL STATUS is NO-GO if any check has FAILED status.
OVERALL STATUS is PROCEED WITH CAUTION if any check is HIGH RISK.
OVERALL STATUS is GO if all checks pass with LOW or MEDIUM risk only.

---

### Affected Tables
{table name} — {row count} rows — {table size}
(repeat for each table)

---

### Lock Contention
Risk Level: {HIGH / MEDIUM / LOW}
{Findings or "None detected"}
Recommendation: {specific action or "None required"}

---

### Index Analysis
Risk Level: {HIGH / MEDIUM / LOW}
{Findings or "None detected"}
Recommendation: {specific action or "None required"}

---

### Constraint Violations
Status: {FAILED / PASSED}
{For each constraint checked: constraint name, violating row count, sample values if available}
Recommendation: {specific fix — data cleanup query, backfill script, etc.}

---

### Execution Time Estimate
Estimated total: {X minutes Y seconds}
Maintenance window: {value provided or "Not specified"}
Status: {WITHIN WINDOW / TOO LONG / WINDOW NOT SPECIFIED}
Breakdown:
  {statement}: {estimate}
  (repeat for each statement)

---

### Remediation Actions Required
(Only present if status is NO-GO or PROCEED WITH CAUTION)
1. {Specific action with exact SQL or command where applicable}
2. ...

---

## Constraints and Quality Rules

- Never execute INSERT, UPDATE, DELETE, or DDL during pre-flight. Read only.
- If the database connection fails, halt immediately and report the error.
  Do not guess or fabricate statistics.
- If table statistics are stale (last_autoanalyze > 7 days), note this and
  recommend running ANALYZE before re-running the check.
- Always show the exact queries you ran. Do not summarize them away.
- If running against production, confirm with the user before connecting.
  Print: "You are about to run pre-flight checks against PRODUCTION. Confirm? (yes/no)"
- Row count estimates from pg_class are acceptable for tables >1M rows.
  Use exact COUNT(*) for tables under 1M rows.
- All risk levels must be justified with specific data, not just asserted.

---

## Usage Examples

### Example 1 — Check a migration file against staging

/preflight-check migrations/20240815_add_user_preferences.sql staging

Claude will parse the file, connect to staging, run all five checks,
and output the full report with GO/NO-GO status.

---

### Example 2 — Inline SQL with maintenance window

/preflight-check
SQL: ALTER TABLE orders ADD COLUMN fulfillment_region VARCHAR(64) NOT NULL DEFAULT 'us-east';
Environment: production
Window: 10 minutes

Claude will warn that this requires ACCESS EXCLUSIVE on the orders table,
check row count, verify Postgres version for instant default support,
and validate the window is sufficient.

---

### Example 3 — Pre-flight before a zero-downtime rename

/preflight-check db/migrate/20240901_rename_user_email_to_primary_email.rb production

Claude will detect the column rename, check for application queries still
using the old column name if query logs are accessible, assess lock risk,
and recommend the shadow-column approach if the table exceeds the risk threshold.