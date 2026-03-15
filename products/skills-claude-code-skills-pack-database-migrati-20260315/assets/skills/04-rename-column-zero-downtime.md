---
name: rename-column-zero-downtime
trigger: /rename-column
description: >
  Generates a complete multi-phase zero-downtime column rename strategy using
  the expand-contract pattern. Use this skill whenever you need to rename a
  database column in a live production system without downtime, data loss, or
  breaking application code mid-deployment. Produces migration scripts, dual-write
  shim code, backfill queries, and sequenced cutover steps.
requires:
  - Table name and current column name
  - Desired new column name
  - Database engine (PostgreSQL, MySQL, SQLite, etc.)
  - ORM or query layer in use (optional but recommended)
tags: [database, migration, zero-downtime, schema, expand-contract]
---

# Skill: Zero-Downtime Column Rename (`/rename-column`)

## Purpose

Renaming a column in production is deceptively dangerous. A naive `ALTER TABLE RENAME COLUMN` will break running application instances the moment it executes. This skill implements the **expand-contract pattern** — a multi-phase approach where both the old and new column names coexist temporarily, giving you safe, rollback-friendly deployments.

---

## When to Use This Skill

- Renaming any column in a table that receives live traffic
- When you cannot afford a maintenance window
- When multiple application versions may run simultaneously (blue/green, canary deployments)
- When the column is referenced in indexes, foreign keys, or views

---

## What Claude Will Produce

1. **Phase 0 — Analysis**: Dependency audit (indexes, FKs, views, triggers, app code references)
2. **Phase 1 — Expand**: Migration to add the new column alongside the old one
3. **Phase 2 — Dual-Write Shim**: Application-layer code to write to both columns simultaneously
4. **Phase 3 — Backfill**: Query to populate the new column from existing data
5. **Phase 4 — Cutover**: Migration to switch reads to the new column; remove dual-write
6. **Phase 5 — Contract**: Migration to drop the old column after confidence period
7. **Rollback Plan**: Specific revert steps for each phase

---

## Execution Instructions for Claude

### Step 1 — Gather Context

Before generating anything, confirm you have:
- `<table>` — the target table name
- `<old_column>` — current column name
- `<new_column>` — desired column name
- `<db_engine>` — e.g., PostgreSQL 15, MySQL 8, SQLite 3
- `<orm>` — e.g., ActiveRecord, SQLAlchemy, Prisma, TypeORM, raw SQL (ask if not provided)
- `<language>` — application language (Ruby, Python, TypeScript, Go, etc.)

If any required input is missing, ask for it before proceeding. Do not guess table structure.

### Step 2 — Run Dependency Audit

Emit a checklist of what the engineer must verify manually, plus any queries to discover dependencies:

- Query all indexes referencing `<old_column>`
- Query all foreign key constraints
- Query views, materialized views, and triggers
- Grep pattern for application code (`old_column` string literals, ORM attribute names)
- Check generated columns or computed defaults referencing the column

### Step 3 — Generate Phase 1 (Expand Migration)

- Add `<new_column>` with the **same data type, nullability, and default** as `<old_column>`
- Do NOT copy constraints that would cause uniqueness conflicts during dual-write
- Label the migration file with a timestamp prefix and `_expand` suffix
- Include an `up` and `down` method

### Step 4 — Generate Phase 2 (Dual-Write Shim)

- Write application-layer code that writes to **both** `<old_column>` and `<new_column>` on every INSERT and UPDATE
- Write reads from `<old_column>` (unchanged at this phase)
- If ORM is provided, generate the specific model/schema change
- If raw SQL, generate middleware or repository-layer wrapper
- Flag any bulk update paths that bypass the ORM and must be updated separately

### Step 5 — Generate Phase 3 (Backfill Query)

- Generate a **batched** backfill query (never a single `UPDATE` with no `WHERE` on large tables)
- Default batch size: 1000 rows; parameterize it
- Include a `WHERE <new_column> IS NULL` guard so it is safe to re-run
- Provide an estimated progress query
- Warn if the column has a NOT NULL constraint that must be deferred

### Step 6 — Generate Phase 4 (Cutover Migration + App Update)

- Migration: add NOT NULL constraint to `<new_column>` if applicable (using a check constraint + validate pattern for PostgreSQL)
- Application update: switch all reads to `<new_column>`; remove dual-write; read and write only `<new_column>`
- Generate updated model/query code

### Step 7 — Generate Phase 5 (Contract Migration)

- Migration to drop `<old_column>`
- Warn: this phase is **irreversible** without a restore; recommend waiting at least one full deploy cycle
- Include index cleanup for any indexes that were on `<old_column>`

### Step 8 — Generate Rollback Plan

For each phase, provide an explicit rollback:

| Phase | Rollback Action |
|-------|-----------------|
| Phase 1 | Run `down` migration to drop new column |
| Phase 2 | Revert app code to single-write on old column |
| Phase 3 | No rollback needed; backfill is non-destructive |
| Phase 4 | Revert app reads to old column; restore dual-write |
| Phase 5 | Restore from backup only — emphasize this clearly |

---

## Output Format Rules

- Group output under clearly labeled `## Phase N — <Name>` headings
- All SQL must be formatted and include a header comment with the db engine and timestamp placeholder
- All application code must include language + framework in a comment
- Batched queries must include a loop example (shell script or language-native)
- Every migration must have both `up` and `down` implementations
- End with a **Deployment Checklist** summarizing the order of operations

---

## Constraints and Quality Rules

- Never generate a single-statement `RENAME COLUMN` as the only output — always use the full expand-contract pattern
- Never generate an unbatched `UPDATE table SET new_col = old_col` without a WHERE clause and batch logic
- Always warn when a column has unique indexes — dual-write requires careful handling
- Always warn when a column is a foreign key source or target
- Flag if `<old_column>` and `<new_column>` differ only in case — some engines treat these as identical
- PostgreSQL: use `ALTER TABLE ... ADD CONSTRAINT ... NOT VALID` + `VALIDATE CONSTRAINT` pattern for zero-lock NOT NULL additions
- MySQL: note that `ALTER TABLE` may lock depending on engine version; recommend `pt-online-schema-change` or `gh-ost` for large tables
- Do not generate code that removes `<old_column>` in the same migration that adds `<new_column>`

---

## Usage Examples

### Example 1 — PostgreSQL with ActiveRecord

/rename-column table=users old=full_name new=display_name db=postgresql orm=activerecord language=ruby

Produces all five phase migrations as `.rb` ActiveRecord migration files, a dual-write concern module, a batched Ruby backfill script, and a rollback table.

---

### Example 2 — MySQL with SQLAlchemy

/rename-column table=orders old=customer_id new=buyer_id db=mysql8 orm=sqlalchemy language=python

Produces Alembic migration files for each phase, a SQLAlchemy model update with dual-write event listeners, a batched Python backfill using `LIMIT`/`OFFSET`, and a note recommending `gh-ost` for the Phase 5 drop given MySQL locking behavior.

---

### Example 3 — PostgreSQL with Raw SQL

/rename-column table=products old=desc new=description db=postgresql14 orm=raw language=typescript

Produces raw `.sql` migration files, a TypeScript repository class showing dual-write in the `save()` method, a `psql`-compatible batched backfill shell script, and a warning that `desc` is a reserved word in some contexts that may have caused prior quoting requirements to be audited.

---

## Deployment Checklist Template

Claude must append this filled-in checklist at the end of every response:

- [ ] Phase 1 migration reviewed and tested in staging
- [ ] Dual-write shim deployed and verified in staging
- [ ] Backfill query run in staging; row counts match
- [ ] Backfill query run in production (batched, monitored)
- [ ] New column verified: no NULLs, data matches old column
- [ ] Phase 4 cutover migration deployed to staging
- [ ] Application reads verified against new column in staging
- [ ] Phase 4 deployed to production
- [ ] Monitoring period observed (recommended: minimum 1 deploy cycle)
- [ ] Phase 5 drop migration deployed — **point of no return**