---
name: plan-migration-rollback
trigger: /plan-rollback
description: >
  Analyzes a migration script and produces a detailed rollback plan with
  compensating SQL, dependency order, and risk annotations for each step.
  Use this skill before applying any schema change to production to ensure
  you have a tested, sequenced recovery path if the migration needs to be
  reversed. Works with PostgreSQL, MySQL, and SQLite migration scripts.
tags: [database, migrations, rollback, safety, schema]
---

# Skill: Plan Migration Rollback

## Purpose

Given a migration script (file path or inline SQL), produce a complete rollback
plan that a DBA or engineer can execute immediately if the forward migration
must be reverted. Each step in the rollback plan is annotated with risk level,
reversibility status, estimated data impact, and the exact compensating SQL to
run.

---

## When to Use This Skill

- Before applying any migration to a staging or production database
- After writing a migration script that includes destructive operations
- When reviewing a teammate's migration PR and assessing rollback safety
- As part of a pre-flight checklist before a deployment window

---

## Execution Instructions

### Step 1 — Accept Input

Accept one or more of the following as input:

1. **File path** to a migration script (e.g., `migrations/0042_add_user_roles.sql`)
2. **Inline SQL** pasted directly into the prompt
3. **Migration tool file** (Flyway `.sql`, Alembic `upgrade()` block,
   Liquibase changeset, Prisma migration, Rails `change`/`up` block)

If no input is provided, ask the user:
> "Please provide the migration script — either paste the SQL or give me the
> file path."

If a file path is given, read the file contents before proceeding.

### Step 2 — Parse and Classify Each Operation

Walk through the migration script sequentially. For each discrete SQL
statement or logical operation, classify it:

**Reversible operations** (compensating SQL can be generated automatically):
- `CREATE TABLE` → rollback is `DROP TABLE`
- `ADD COLUMN` → rollback is `DROP COLUMN`
- `CREATE INDEX` → rollback is `DROP INDEX`
- `ADD CONSTRAINT` / `ADD FOREIGN KEY` → rollback is `DROP CONSTRAINT`
- `CREATE VIEW` → rollback is `DROP VIEW`
- `ALTER COLUMN` (type widening, nullable change) → rollback restores prior definition
- `RENAME INDEX` → rollback renames back

**Conditionally reversible operations** (require data backup or snapshot):
- `ALTER COLUMN` (type narrowing, e.g., `VARCHAR(255)` → `VARCHAR(50)`) — data
  truncation risk
- `DROP DEFAULT` / `SET DEFAULT` — safe if no writes occurred after migration
- `RENAME COLUMN` — safe only if application code is also rolled back atomically
- `RENAME TABLE` — same as rename column

**Irreversible operations** (flag prominently; no automatic rollback):
- `DROP TABLE`
- `DROP COLUMN`
- `TRUNCATE`
- Data `UPDATE` or `DELETE` without a shadow/backup table
- `ALTER COLUMN` with lossy type cast

### Step 3 — Determine Rollback Dependency Order

Rollback must execute in the **reverse order** of the forward migration. Apply
these additional ordering rules:

1. Drop foreign key constraints **before** dropping the tables they reference
2. Re-create constraints **after** re-creating the tables they depend on
3. Index creation in rollback comes **after** table/column restoration
4. If the migration inserts seed data, the rollback must delete it **first**

Produce a numbered rollback sequence that reflects this ordering.

### Step 4 — Generate the Rollback Plan Document

Output the rollback plan using the exact format specified in the Output Format
section below.

### Step 5 — Add a Summary Risk Assessment

After the step-by-step plan, provide a concise risk summary:
- Overall rollback risk: **LOW / MEDIUM / HIGH / CRITICAL**
- Count of irreversible steps
- Estimated rows affected (if detectable from the script or schema context)
- Recommended rollback window (time estimate)
- Any prerequisites (e.g., "requires point-in-time snapshot taken before migration")

---

## Output Format

Use this exact structure:

---

## Rollback Plan: `<migration filename or first 60 chars of inline SQL>`

**Generated for:** `<detected dialect: PostgreSQL / MySQL / SQLite / unknown>`
**Forward migration steps detected:** `<N>`
**Rollback steps:** `<N>`

---

### Step-by-Step Rollback (execute in this order)

#### Rollback Step 1 — `<short description>`

**Reverses forward step:** `<N>`
**Risk:** 🟢 LOW | 🟡 MEDIUM | 🔴 HIGH | ⛔ IRREVERSIBLE
**Reversibility:** Automatic | Requires snapshot | Manual / Not possible

**Compensating SQL:**

```sql
-- <compensating statement(s)>
```

**Notes:** `<any caveats, data considerations, locking behavior, or warnings>`

---

_(repeat for each step)_

---

### Risk Summary

| Metric | Value |
|---|---|
| Overall Rollback Risk | 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH / ⛔ CRITICAL |
| Irreversible Steps | `<N>` |
| Reversible Steps | `<N>` |
| Estimated Rows Affected | `<N or "unknown — check before running">` |
| Recommended Rollback Window | `<e.g., "< 5 minutes" or "requires maintenance window">` |
| Snapshot Required Before Migrating | Yes / No |

### Prerequisites Before Running Rollback

- `<bulleted list of any required preconditions>`

### Warnings

- `<bulleted list of any irreversible steps or data loss risks>`

---

## Constraints and Quality Rules

- **Never omit irreversible steps.** Always include them in the plan with a
  clear ⛔ annotation and an explanation of why rollback is not possible.
- **Do not silently skip steps.** If compensating SQL cannot be generated (e.g.,
  a `DROP COLUMN` in the forward migration), state explicitly that the rollback
  requires a database restore or manual data reconstruction.
- **Use dialect-correct SQL.** Generate syntax appropriate for the detected
  database engine. If dialect cannot be determined, default to standard SQL and
  note the assumption.
- **Preserve forward step numbering.** Each rollback step must reference which
  forward step it reverses so the engineer can cross-reference easily.
- **Flag locking risks.** For operations that take `ACCESS EXCLUSIVE` locks
  (e.g., `ALTER TABLE` on PostgreSQL), note the lock type and potential
  impact on production traffic.
- **Do not execute anything.** This skill only produces plans — it never runs
  SQL against a live database.
- **One rollback plan per invocation.** If multiple migration files are given,
  ask the user to confirm whether they want a combined plan or separate plans.

---

## Examples

### Example 1 — Simple table addition

/plan-rollback migrations/0042_add_orders_table.sql

Produces a rollback plan reversing the `CREATE TABLE orders` statement, any
associated indexes and foreign keys, in correct dependency order.

---

### Example 2 — Inline SQL with a destructive step

/plan-rollback

```sql
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP;
ALTER TABLE users DROP COLUMN legacy_token VARCHAR(255);
CREATE INDEX idx_users_last_login ON users(last_login_at);
```

Produces a three-step rollback plan where the `DROP COLUMN` step is marked
⛔ IRREVERSIBLE with a note that `legacy_token` data cannot be recovered
without a prior snapshot.

---

### Example 3 — Alembic migration file

/plan-rollback app/alembic/versions/2024_10_15_add_role_permissions.py

Claude reads the `upgrade()` function, ignores the existing `downgrade()` if
present (or compares it for completeness), and produces a rollback plan with
risk annotations that the existing `downgrade()` may be missing.

---