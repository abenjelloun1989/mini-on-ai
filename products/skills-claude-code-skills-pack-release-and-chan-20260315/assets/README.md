# Claude Code Skills Pack: Release and Changelog Documentation — 5 Skills for Communicating Code Changes Clearly

For DevOps engineers and release managers, this pack generates human-readable changelogs from git commits, categorizes breaking vs non-breaking changes, drafts release notes for end users, documents migration steps for version upgrades, and creates internal post-release summaries so they can ship releases with clear communication every time

## What's included

- **5 ready-to-use SKILL.md files** — drop into your project's `skills/` folder, no setup required
- **guide.md** — installation instructions and quick-reference table for all 5 skills
- Each skill is immediately usable with its slash-command trigger

## Skills in this pack

- `skills/01-generate-changelog.md` — `/gen-changelog` — Parses raw git commit history between two refs and generates a structured, human-readable changelog grouped by change type (feat, fix, chore, etc.).
- `skills/02-classify-breaking-changes.md` — `/classify-breaking` — Analyzes commits, diffs, or changelog entries to identify and clearly flag breaking versus non-breaking changes with severity ratings and affected surface areas.
- `skills/03-draft-release-notes.md` — `/draft-release-notes` — Transforms technical changelog entries into polished, end-user-facing release notes with plain language summaries, highlights, and a consistent tone for public publishing.
- `skills/04-document-migration-steps.md` — `/gen-migration-guide` — Generates step-by-step migration guides for version upgrades, covering deprecated APIs, configuration changes, and required code modifications with before/after examples.
- `skills/05-post-release-summary.md` — `/post-release-summary` — Creates an internal post-release summary report covering what shipped, known issues, rollback procedures, and follow-up action items for engineering and stakeholder teams.

## Quick Start

1. Copy the `skills/` folder into your project root
2. Run `claude` in your project directory
3. Use any skill trigger listed above

## Files

- `skills/` — 5 SKILL.md files, one per skill
- `guide.md` — Installation guide and quick-reference table
- `README.md` — This file
