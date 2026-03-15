---
name: document-migration-steps
trigger: /gen-migration-guide
description: >
  Generates comprehensive step-by-step migration guides for version upgrades.
  Covers deprecated APIs, configuration changes, dependency updates, and required
  code modifications with concrete before/after examples. Use this skill whenever
  a new version introduces breaking changes, deprecations, or non-trivial upgrade
  paths that users need to navigate safely.
tags: [release, migration, changelog, documentation, versioning]
---

# Skill: Generate Migration Guide

## Purpose

Produce a clear, actionable migration guide that helps developers upgrade from one
version to another without missing critical steps. The guide should eliminate
ambiguity, surface breaking changes prominently, and give readers copy-paste-ready
code examples wherever possible.

---

## When to Use This Skill

- A release introduces breaking changes to public APIs or interfaces
- Configuration file schemas have changed between versions
- Dependencies have been upgraded with incompatible version requirements
- Database schemas, environment variables, or build tooling have changed
- Deprecated features have been removed in this release
- Users need an ordered sequence of steps to upgrade safely

---

## Inputs Claude Should Gather

Before generating the guide, Claude must identify or ask for:

1. **Source version** — the version users are upgrading FROM (e.g., `v2.3.1`)
2. **Target version** — the version users are upgrading TO (e.g., `v3.0.0`)
3. **Change source** — one or more of:
   - Git diff or commit range (`git log v2.3.1..v3.0.0`)
   - Existing CHANGELOG or release notes draft
   - List of breaking changes provided inline
   - Source files showing old vs. new API signatures
4. **Audience** — end-user developers, internal engineers, or both
5. **Project type** — library, CLI tool, web service, SDK, etc. (infer from repo if possible)

If inputs are missing, Claude should scan the repository for relevant signals:
CHANGELOG.md, package.json / pyproject.toml / go.mod version fields, git tags,
and any `BREAKING_CHANGE` markers in commit messages.

---

## Execution Steps

### Step 1 — Collect and Analyze Changes

- Run or review the git log between source and target versions
- Identify all commits tagged with `BREAKING CHANGE`, `feat!`, `fix!`, or similar
- Scan for removed or renamed exports, changed function signatures, config key renames
- Note any dependency version bumps that may require user action
- Flag deprecation notices introduced in previous versions that are now enforced

### Step 2 — Categorize Changes

Group every change into one of these categories:

| Category | Description |
|---|---|
| **Breaking — API** | Removed or renamed public functions, classes, methods |
| **Breaking — Config** | Changed config file keys, formats, or required fields |
| **Breaking — CLI** | Renamed or removed flags, subcommands, or env vars |
| **Breaking — Dependencies** | Peer dependency version range changes |
| **Breaking — Data / Schema** | Database migrations, serialization format changes |
| **Deprecated** | Still works but will be removed in a future version |
| **Non-breaking — Recommended** | Optional but strongly encouraged changes |

### Step 3 — Determine Migration Order

Order steps so that earlier steps do not break later ones. General safe sequence:

1. Update the package/dependency version
2. Apply dependency or environment changes
3. Run automated codemods or migration scripts (if available)
4. Update configuration files
5. Update API call sites
6. Update CLI usage or scripts
7. Apply database/schema migrations
8. Validate and test

### Step 4 — Write the Guide

Follow the output format defined below. For every breaking change, provide:
- A one-sentence explanation of what changed and why
- A **Before** code block showing old usage
- An **After** code block showing new usage
- Any caveats, edge cases, or rollback notes

### Step 5 — Add Validation Checklist

Close the guide with a checklist users can run through to confirm the migration
is complete before deploying.

---

## Output Format

Produce the migration guide as a Markdown document with this structure:

```
# Migration Guide: v{SOURCE} → v{TARGET}

## Overview
Brief paragraph: what changed at a high level, estimated effort, any prerequisites.

## Prerequisites
- Required tool versions
- Required environment setup before starting

## Breaking Changes
### {Category Name}
#### {Change Title}
**What changed:** ...
**Before:**
\`\`\`language
// old code
\`\`\`
**After:**
\`\`\`language
// new code
\`\`\`
**Notes:** ...

(Repeat for each breaking change, grouped by category)

## Step-by-Step Migration

### Step 1 — {Action Title}
Instructions...

### Step 2 — {Action Title}
Instructions...

(Continue through all required steps in safe order)

## Deprecated Features
List features that are deprecated but not yet removed, with recommended alternatives.

## Automated Migration Tools
List any codemods, scripts, or CLI commands that automate parts of the migration.

## Validation Checklist
- [ ] Checklist item
- [ ] Checklist item

## Rollback Instructions
How to revert to the previous version if the migration fails.

## Getting Help
Links to issue tracker, docs, or support channels.
```

---

## Quality Rules

- **No vague language.** Never write "update your code accordingly." Always show exactly what to update.
- **Every breaking change gets a before/after example.** No exceptions.
- **Code blocks must specify language** for syntax highlighting.
- **Steps must be atomic and ordered.** Each step should be completable independently.
- **Flag required vs. optional steps** clearly — use `[REQUIRED]` or `[OPTIONAL]` prefixes.
- **Estimate effort** for the overall migration and for individually complex steps.
- **Do not assume context.** Write for a developer who has not followed the project's development closely.
- **Preserve existing terminology.** Use the project's own names for concepts; do not invent synonyms.
- **Include version numbers in all code examples** where relevant (e.g., `npm install pkg@3.0.0`).

---

## Usage Examples

### Example 1 — Provide a version range directly

/gen-migration-guide from v2.3.1 to v3.0.0

Claude will inspect the git log between those two tags, identify all breaking
changes, and produce the full migration guide.

---

### Example 2 — Provide a changelog draft as input

/gen-migration-guide using the CHANGELOG.md draft I just wrote, source v1.8.0 target v2.0.0, audience is external SDK users

Claude will parse the changelog, extract breaking and deprecated items, and
generate a user-facing migration guide with before/after code examples inferred
from the changelog descriptions and current source code.

---

### Example 3 — Targeted migration for a specific subsystem

/gen-migration-guide for the authentication module only, v4.1.0 to v4.2.0, focus on the new OAuth2 config format

Claude will scope the guide to auth-related changes, show the old vs. new
configuration schema, and include a step for migrating existing config files.

---

## Notes for Claude

- If no git tags exist, ask the user to supply a commit SHA range or paste relevant diffs.
- If the project has a codemod tool (e.g., jscodeshift, ast-grep configs), mention it prominently in the Automated Migration Tools section.
- If the migration involves a database schema change, add a prominent warning to back up data before proceeding.
- Keep the tone professional and neutral — migration guides are reference documents, not blog posts.
- Output the guide as a file artifact named `MIGRATION-v{SOURCE}-to-v{TARGET}.md` when the environment supports file output.