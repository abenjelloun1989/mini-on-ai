# Claude Code Skills Pack: Database Migration — 5 Skills for Safe Schema Changes in Production

For backend engineers and DBAs, this pack automates migration script generation, rollback planning, pre-flight validation, zero-downtime column renaming, and post-migration verification so they can ship schema changes confidently without data loss or downtime incidents.

## What's included

- **5 ready-to-use SKILL.md files** — drop into your project's `skills/` folder, no setup required
- **guide.md** — installation instructions and quick-reference table for all 5 skills
- Each skill is immediately usable with its slash-command trigger

## Skills in this pack

- `skills/01-generate-migration-script.md` — `/gen-migration` — Generates a versioned, idempotent migration script from a schema diff or natural-language description, following naming conventions and including up/down blocks.
- `skills/02-plan-migration-rollback.md` — `/plan-rollback` — Analyzes a migration script and produces a detailed rollback plan with compensating SQL, dependency order, and risk annotations for each reversible and irreversible step.
- `skills/03-validate-migration-preflight.md` — `/preflight-check` — Runs pre-flight checks against the target database to detect lock contention risks, missing indexes, constraint violations, and estimated execution time before applying any changes.
- `skills/04-rename-column-zero-downtime.md` — `/rename-column` — Generates a multi-phase zero-downtime column rename strategy using the expand-contract pattern, including dual-write shim code, backfill queries, and cutover steps.
- `skills/05-verify-post-migration.md` — `/verify-migration` — Produces and executes a post-migration verification checklist that validates row counts, constraint integrity, index health, application query compatibility, and replication lag after a migration completes.

## Quick Start

1. Copy the `skills/` folder into your project root
2. Run `claude` in your project directory
3. Use any skill trigger listed above

## Files

- `skills/` — 5 SKILL.md files, one per skill
- `guide.md` — Installation guide and quick-reference table
- `README.md` — This file
