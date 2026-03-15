---
name: generate-migration-script
trigger: /gen-migration
description: >
  Generates a versioned, idempotent database migration script from either a
  schema diff (before/after DDL) or a natural-language description of the
  desired change. Output includes a timestamped filename, an `up` block to
  apply the change, and a `down` block to reverse it safely. Use this skill
  whenever you need to introduce schema changes — new tables, column additions,
  index creation, constraint changes, or type alterations — and want a
  production-ready script that can be run repeatedly without side effects.
when_to_use: >
  Invoke /gen-migration when you have a schema change to make and need a
  ready-to-commit migration file. Works from a natural-language description
  ("add a non-nullable email column to users"), a before/after DDL pair, or
  an ORM model diff. Not intended for data backfills (use a separate seeding
  skill) or destructive bulk deletes (those require an explicit data-loss
  review step first).
---

# Skill: generate-migration-script

## Purpose

Produce a single, self-contained migration script that is:

- **Versioned** — filename encodes a UTC timestamp so migrations sort and apply in order.
- **Idempotent** — every DDL statement is guarded so re-running the script produces no error and no duplicate change.
- **Reversible** — a `down` block undoes exactly what `up` does, in the correct reverse order.
- **Dialect-aware** — SQL syntax matches the target database engine (PostgreSQL, MySQL, or SQLite).

---

## Inputs Claude Should Collect

Before generating, confirm the following. If the user has not supplied them, ask in a single grouped prompt — do not ask one at a time.

1. **Change description** — natural language, DDL snippet, or ORM model diff.
2. **Target database engine** — PostgreSQL (default), MySQL 8+, or SQLite 3.
3. **Migration tool / framework** — raw SQL files, Flyway, Liquibase, golang-migrate, Alembic, Active Record, Knex, or Prisma. Determines file naming convention and block syntax.
4. **Schema / namespace** — the database schema or namespace affected (e.g., `public`, `app`, bare table names).
5. **Existing table DDL** (if modifying a table) — paste current `CREATE TABLE` or describe existing columns so guards can be accurate.

If any input is ambiguous (e.g., column type not specified), apply a safe default and call it out in a `## Assumptions` section at the top of the output.

---

## Execution Steps

Follow these steps in order every time the skill runs.

### Step 1 — Parse the Change Request

Identify the change category:

- `CREATE TABLE` — new table
- `ADD COLUMN` — new column on existing table
- `DROP COLUMN` — remove column (flag as destructive, require explicit confirmation)
- `RENAME COLUMN` — column rename (note: use zero-downtime rename skill for production; emit a warning here)
- `ADD INDEX` / `DROP INDEX` — index management
- `ADD CONSTRAINT` / `DROP CONSTRAINT` — foreign keys, unique, check constraints
- `ALTER COLUMN TYPE` — type change (flag as potentially destructive)
- `CREATE SCHEMA` / `DROP SCHEMA` — namespace changes
- `RENAME TABLE` — table rename

For destructive categories (`DROP COLUMN`, `ALTER COLUMN TYPE` narrowing, `DROP TABLE`), prepend a `⚠️ DESTRUCTIVE CHANGE` warning block to the output before the script.

### Step 2 — Determine Filename

Use the following convention based on the selected tool:

| Tool | Format |
|---|---|
| Raw SQL / golang-migrate | `{YYYYMMDDHHMMSS}_{snake_case_description}.{up\|down}.sql` |
| Flyway | `V{YYYYMMDDHHMMSS}__{Snake_Case_Description}.sql` (up only; down is `U` prefix) |
| Alembic | Python file; emit a `.py` stub with `upgrade()` / `downgrade()` |
| Active Record | `{YYYYMMDDHHMMSS}_snake_case_description.rb` |
| Knex | `{YYYYMMDDHHMMSS}_snake_case_description.js` |
| Liquibase | `{YYYYMMDDHHMMSS}-snake-case-description.xml` or `.yaml` |
| Prisma | Note: Prisma manages its own versioning; emit a `migration.sql` body only |

Use the current UTC time as the timestamp. If Claude cannot determine real time, use the placeholder `YYYYMMDDHHMMSS` and instruct the user to replace it before committing.

### Step 3 — Write the `up` Block

Apply the following idempotency guards per change type:

**PostgreSQL**

- `CREATE TABLE IF NOT EXISTS`
- `ADD COLUMN IF NOT EXISTS`
- Index: `CREATE INDEX IF NOT EXISTS` / `CREATE UNIQUE INDEX IF NOT EXISTS`
- Schema: `CREATE SCHEMA IF NOT EXISTS`
- For `DROP COLUMN` / `DROP TABLE`: wrap in a `DO $$ BEGIN ... EXCEPTION WHEN ... END $$;` block or use `IF EXISTS`

**MySQL**

- Use `CREATE TABLE IF NOT EXISTS`
- Column existence must be checked via `INFORMATION_SCHEMA` in a stored procedure snippet; emit the procedure, call it, then drop it
- Index: check `INFORMATION_SCHEMA.STATISTICS` before creating

**SQLite**

- `CREATE TABLE IF NOT EXISTS`
- `CREATE INDEX IF NOT EXISTS`
- Column additions are safe to wrap with a `PRAGMA table_info` check only if generating application-level migration code; otherwise note the limitation

Always place a transaction boundary around the `up` block where the engine supports DDL transactions (PostgreSQL yes, MySQL no — note this explicitly, SQLite yes for DDL).

### Step 4 — Write the `down` Block

Reverse every operation in `up` in **reverse order**. Apply the same idempotency guards (`DROP ... IF EXISTS`). For destructive `up` operations (e.g., `DROP COLUMN`), the `down` block should attempt to recreate the column with a `DEFAULT NULL` or the original type if known, and include a comment that data cannot be automatically restored.

### Step 5 — Emit Assumptions and Notes

Append a `## Assumptions & Review Notes` section listing:

- Any type defaults chosen (e.g., `VARCHAR(255)` when length was unspecified)
- Whether the change is safe to run online without locking (flag long-running operations: adding a non-nullable column without a default on large tables, building an index without `CONCURRENTLY`, etc.)
- Recommended pre-flight checks (link to `/preflight-check` skill if applicable)
- Any follow-up steps required (e.g., backfilling data before dropping `NOT NULL` default)

---

## Output Format

Produce output in this exact structure:

1. A short **Summary** line (one sentence).
2. `⚠️ DESTRUCTIVE CHANGE` warning block, if applicable.
3. **Filename** to use when saving the file.
4. The **migration script** in a fenced code block with the correct language tag (`sql`, `python`, `ruby`, `js`, `xml`).
5. **`## Assumptions & Review Notes`** section.

Do not include explanatory prose inside the code block. All commentary belongs in the Assumptions section or as SQL comments (`-- comment`) that a DBA can read in the script itself.

---

## Constraints and Quality Rules

- Never emit `DROP TABLE` or `DROP COLUMN` without an `IF EXISTS` guard.
- Never omit a `down` block. If a rollback is genuinely impossible (e.g., dropped a column whose data is gone), emit a `down` stub with a clear `-- MANUAL INTERVENTION REQUIRED` comment.
- Default to `BIGINT` for new primary keys unless the user specifies otherwise.
- Default new timestamp columns to `TIMESTAMPTZ` on PostgreSQL; `DATETIME` on MySQL; `TEXT` (ISO-8601) on SQLite.
- Do not add `NOT NULL` constraints without a `DEFAULT` value unless the user explicitly requests it and confirms the table is empty or will be backfilled first.
- Flag any index that should use `CONCURRENTLY` (PostgreSQL) to avoid table locks — do not silently omit `CONCURRENTLY`.
- Keep each migration file focused on a single logical change. If the request spans multiple unrelated changes, split into separate numbered files and say so.

---

## Usage Examples

**Example 1 — Add a column from natural language**

/gen-migration Add a nullable `deleted_at` timestamptz column to the `orders` table in PostgreSQL using golang-migrate

Expected output includes:
- Filename: `20240115143000_add_deleted_at_to_orders.up.sql` and `...down.sql`
- `up`: `ALTER TABLE orders ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;`
- `down`: `ALTER TABLE orders DROP COLUMN IF EXISTS deleted_at;`

---

**Example 2 — New table from a schema description**

/gen-migration Create a `payment_methods` table with id (bigint PK), user_id (bigint FK to users), provider (varchar 50, not null), token (text, not null), created_at (timestamptz). Target: PostgreSQL, Flyway.

Expected output includes:
- Flyway filename: `V20240115143000__Create_payment_methods_table.sql`
- `CREATE TABLE IF NOT EXISTS` with all columns, FK constraint, and index on `user_id`
- A matching undo migration file stub

---

**Example 3 — Destructive change with warning**

/gen-migration Drop the `legacy_code` column from the `products` table. PostgreSQL, raw SQL.

Expected output includes:
- `⚠️ DESTRUCTIVE CHANGE` warning with a reminder to verify no application code references `legacy_code`
- `up`: `ALTER TABLE products DROP COLUMN IF EXISTS legacy_code;`
- `down`: stub with `-- MANUAL INTERVENTION REQUIRED: data in legacy_code cannot be recovered after this migration runs`
- Note recommending a pre-flight check and a backup before applying

---

## Related Skills

- `/preflight-check` — validate this migration against a live or shadow database before applying
- `/rollback-plan` — generate a runbook for emergency rollback procedures
- `/rename-column-zero-downtime` — safe multi-step column rename that avoids locking
- `/post-migration-verify` — confirm the schema change applied correctly and application is healthy