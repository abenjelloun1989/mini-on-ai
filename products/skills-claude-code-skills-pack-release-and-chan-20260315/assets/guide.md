# Claude Code Skills Pack: Release and Changelog Documentation — 5 Skills for Communicating Code Changes Clearly

> For DevOps engineers and release managers, this pack generates human-readable changelogs from git commits, categorizes breaking vs non-breaking changes, drafts release notes for end users, documents migration steps for version upgrades, and creates internal post-release summaries so they can ship releases with clear communication every time

---

## What's in This Pack

Generates human-readable changelogs, categorizes breaking changes, drafts release notes, documents migration steps, and creates post-release summaries so DevOps engineers and release managers can ship releases with clear communication every time.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/gen-changelog`** — `01-generate-changelog.md`
   Parses raw git commit history between two refs and generates a structured, human-readable changelog grouped by change type (feat, fix, chore, etc.).

**2. `/classify-breaking`** — `02-classify-breaking-changes.md`
   Analyzes commits, diffs, or changelog entries to identify and clearly flag breaking versus non-breaking changes with severity ratings and affected surface areas.

**3. `/draft-release-notes`** — `03-draft-release-notes.md`
   Transforms technical changelog entries into polished, end-user-facing release notes with plain language summaries, highlights, and a consistent tone for public publishing.

**4. `/gen-migration-guide`** — `04-document-migration-steps.md`
   Generates step-by-step migration guides for version upgrades, covering deprecated APIs, configuration changes, and required code modifications with before/after examples.

**5. `/post-release-summary`** — `05-post-release-summary.md`
   Creates an internal post-release summary report covering what shipped, known issues, rollback procedures, and follow-up action items for engineering and stakeholder teams.

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
| Parses raw git commit history between two refs and generates a structured, human-readable changelog grouped by change type (feat, fix, chore, etc.). | `/gen-changelog` | `01-generate-changelog.md` |
| Analyzes commits, diffs, or changelog entries to identify and clearly flag breaking versus non-breaking changes with severity ratings and affected surface areas. | `/classify-breaking` | `02-classify-breaking-changes.md` |
| Transforms technical changelog entries into polished, end-user-facing release notes with plain language summaries, highlights, and a consistent tone for public publishing. | `/draft-release-notes` | `03-draft-release-notes.md` |
| Generates step-by-step migration guides for version upgrades, covering deprecated APIs, configuration changes, and required code modifications with before/after examples. | `/gen-migration-guide` | `04-document-migration-steps.md` |
| Creates an internal post-release summary report covering what shipped, known issues, rollback procedures, and follow-up action items for engineering and stakeholder teams. | `/post-release-summary` | `05-post-release-summary.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
