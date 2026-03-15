# Claude Code Skills Pack: Database Migration — 5 Skills for Safe Schema Changes in Production

> For backend engineers and DBAs, this pack automates migration script generation, rollback planning, pre-flight validation, zero-downtime column renaming, and post-migration verification so they can ship schema changes confidently without data loss or downtime incidents.

---

## What's in This Pack

Automates safe schema change workflows for backend engineers and DBAs, covering migration script generation, rollback planning, pre-flight validation, zero-downtime column renaming, and post-migration verification.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/gen-migration`** — `01-generate-migration-script.md`
   Generates a versioned, idempotent migration script from a schema diff or natural-language description, following naming conventions and including up/down blocks.

**2. `/plan-rollback`** — `02-plan-migration-rollback.md`
   Analyzes a migration script and produces a detailed rollback plan with compensating SQL, dependency order, and risk annotations for each reversible and irreversible step.

**3. `/preflight-check`** — `03-validate-migration-preflight.md`
   Runs pre-flight checks against the target database to detect lock contention risks, missing indexes, constraint violations, and estimated execution time before applying any changes.

**4. `/rename-column`** — `04-rename-column-zero-downtime.md`
   Generates a multi-phase zero-downtime column rename strategy using the expand-contract pattern, including dual-write shim code, backfill queries, and cutover steps.

**5. `/verify-migration`** — `05-verify-post-migration.md`
   Produces and executes a post-migration verification checklist that validates row counts, constraint integrity, index health, application query compatibility, and replication lag after a migration completes.

---

## How to Install

1. **Create a `skills/` directory** in your project root (if it doesn't exist):
   ```bash
   mkdir -p skills
   ```

2. **Copy all skill files** from the `skills/` folder in this pack:
   ```bash
   cp skills/*.md /your-project/skills/
   ```

3. **Run Claude Code** in your project directory — all skills are immediately available:
   ```bash
   claude
   ```

---

## Quick Reference

| Skill | Trigger | File |
|-------|---------|------|
| Generates a versioned, idempotent migration script from a schema diff or natural-language description, following naming conventions and including up/down blocks. | `/gen-migration` | `01-generate-migration-script.md` |
| Analyzes a migration script and produces a detailed rollback plan with compensating SQL, dependency order, and risk annotations for each reversible and irreversible step. | `/plan-rollback` | `02-plan-migration-rollback.md` |
| Runs pre-flight checks against the target database to detect lock contention risks, missing indexes, constraint violations, and estimated execution time before applying any changes. | `/preflight-check` | `03-validate-migration-preflight.md` |
| Generates a multi-phase zero-downtime column rename strategy using the expand-contract pattern, including dual-write shim code, backfill queries, and cutover steps. | `/rename-column` | `04-rename-column-zero-downtime.md` |
| Produces and executes a post-migration verification checklist that validates row counts, constraint integrity, index health, application query compatibility, and replication lag after a migration completes. | `/verify-migration` | `05-verify-post-migration.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
