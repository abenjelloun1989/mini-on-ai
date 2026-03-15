---
name: verify-post-migration
trigger: /verify-migration
description: >
  Produces and executes a post-migration verification checklist that validates
  row counts, constraint integrity, index health, application query compatibility,
  and replication lag after a migration completes. Use this immediately after
  running any schema migration in staging or production to confirm the change
  landed safely before closing the deployment window.
tags: [database, migration, verification, production-safety]
---

# Skill: verify-post-migration

## Purpose

After a schema migration runs, this skill generates and executes a structured
verification checklist tailored to the specific migration that was applied. It
catches silent failures — broken constraints, bloated indexes, dropped rows,
stalled replication — before they surface as application errors or data loss.

**When to use:**
- Immediately after applying a migration script in any environment
- Before closing a deployment window or cutover
- When validating a rollback after a failed migration
- As part of a CI gate in staging before promoting to production

---

## How Claude Should Execute This Skill

### Step 1 — Gather Context

Ask the user for the following if not already provided in the command:

1. **Migration file or description** — the SQL script or migration name that was just applied
2. **Database type** — PostgreSQL, MySQL, MariaDB, or SQLite
3. **Environment** — staging, production, or local
4. **Tables affected** — list of tables touched by the migration
5. **Pre-migration row counts** (optional) — if the user captured them before running
6. **Connection method** — how to run queries (psql, mysql CLI, ORM shell, etc.)

If the user provides a migration file directly, parse it to infer affected tables,
column changes, constraint additions, and index operations automatically.

---

### Step 2 — Build the Verification Checklist

Generate a numbered checklist scoped to what the migration actually changed.
Only include sections relevant to the migration. Do not include checks for
operations the migration did not perform.

**Section A — Row Count Validation**
- For each affected table, generate a query to count current rows
- If pre-migration counts were provided, generate a comparison query
- Flag any table where the count changed unexpectedly (e.g., rows dropped by a DELETE or CASCADE)

Example query pattern:
SELECT COUNT(*) AS current_count FROM {table_name};

For comparison:
SELECT
  {pre_count} AS before_migration,
  COUNT(*) AS after_migration,
  COUNT(*) - {pre_count} AS delta
FROM {table_name};

**Section B — Constraint Integrity**
- For each new or modified constraint (FK, UNIQUE, NOT NULL, CHECK), generate a query that would have failed at migration time if violated
- Verify no orphaned foreign key rows exist
- Verify no NULL values in newly NOT NULL columns

PostgreSQL FK orphan check pattern:
SELECT child.id
FROM {child_table} child
LEFT JOIN {parent_table} parent ON child.{fk_column} = parent.{pk_column}
WHERE parent.{pk_column} IS NULL;

**Section C — Index Health**
- For each new index, verify it was created and is not in an invalid or building state
- For PostgreSQL: query pg_indexes and pg_stat_user_indexes
- For MySQL: query INFORMATION_SCHEMA.STATISTICS

PostgreSQL index validity check:
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = '{table_name}';

PostgreSQL bloat / invalid index check:
SELECT relname, indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE relname = '{table_name}';

**Section D — Application Query Compatibility**
- If the migration renamed or dropped columns, generate test queries that simulate what the application would run
- Confirm renamed columns are accessible under the new name
- Confirm dropped columns are no longer referenced (prompt user to verify ORM models)
- List any queries from the codebase the user should test manually

**Section E — Replication Lag (Production Only)**
- Skip this section for local and staging unless the user requests it
- For PostgreSQL streaming replication:

SELECT
  client_addr,
  state,
  sent_lsn,
  write_lsn,
  flush_lsn,
  replay_lsn,
  (sent_lsn - replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;

- Flag lag above 10 MB or replication state not in 'streaming'
- For MySQL/MariaDB: SHOW REPLICA STATUS\G — flag Seconds_Behind_Source > 30

---

### Step 3 — Execute or Present Queries

Determine the execution mode:

- **If Claude Code has database access configured:** run each query directly,
  capture output, and evaluate results inline.
- **If no direct access:** present all queries in clearly labeled, copy-pasteable
  blocks with instructions for the user to run them and paste back results.

When results are returned, evaluate each one and produce a pass/fail verdict
with a short explanation.

---

### Step 4 — Produce the Verification Report

Output a structured report in this format:

---
## Post-Migration Verification Report

**Migration:** {migration name or file}
**Environment:** {environment}
**Database:** {db type}
**Verified at:** {timestamp}

### Summary

| Check | Status | Notes |
|---|---|---|
| Row counts | ✅ PASS / ❌ FAIL / ⚠️ WARNING | ... |
| Constraint integrity | ✅ / ❌ / ⚠️ | ... |
| Index health | ✅ / ❌ / ⚠️ | ... |
| Query compatibility | ✅ / ❌ / ⚠️ | ... |
| Replication lag | ✅ / ❌ / ⚠️ / — SKIPPED | ... |

### Overall Status: ✅ SAFE TO PROCEED / ❌ ROLLBACK RECOMMENDED / ⚠️ INVESTIGATE BEFORE PROCEEDING

### Detail

{One paragraph per failed or warned check explaining what was found and what to do next.}

### Recommended Next Steps

{Numbered list of actions based on findings.}
---

---

## Constraints and Quality Rules

- **Never assume success.** Every check must have a concrete query and an
  explicit pass/fail evaluation. Do not mark anything passing without evidence.
- **Scope checks to the migration.** Do not generate generic database health
  checks unrelated to what changed. Keep the checklist signal-to-noise high.
- **Flag ambiguity.** If you cannot determine whether a check passed because
  output is missing or ambiguous, mark it ⚠️ WARNING and explain what the user
  needs to provide.
- **Production extra caution.** When environment is production, add a reminder
  before each destructive or blocking query (e.g., queries that acquire locks).
- **Replication section is production-only by default** unless the user
  explicitly requests it for other environments.
- **No query execution without confirmation** in production environments.
  Present the queries first, confirm with the user, then execute.
- **Always output the report** even if all checks pass. The report is the
  artifact that gets attached to the deployment record.

---

## Usage Examples

### Example 1 — Simple column addition

/verify-migration migration: add_phone_to_users.sql env: staging db: postgresql

Claude will parse the migration file, identify the users table, generate row
count and NOT NULL checks for the new phone column, verify the column exists
in pg_attribute, and produce a report. No replication check (staging).

---

### Example 2 — Production index creation with replication

/verify-migration migration: 20240815_add_orders_idx.sql env: production db: postgresql tables: orders

Claude will generate index validity and bloat queries for the orders table,
include the replication lag check, present all queries for user confirmation
before running, then produce the full report with overall status.

---

### Example 3 — Post-rollback verification

/verify-migration migration: rollback_of_rename_user_email.sql env: production db: mysql tables: users verify: rollback

Claude will verify the original column name is restored, FK constraints are
intact, application query patterns against the original column name succeed,
and no rows were lost during the rename-rollback cycle.