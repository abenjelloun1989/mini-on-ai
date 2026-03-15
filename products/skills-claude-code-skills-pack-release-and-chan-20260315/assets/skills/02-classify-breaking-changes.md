---
name: classify-breaking-changes
trigger: /classify-breaking
description: >
  Analyzes commits, diffs, or changelog entries to identify and clearly flag
  breaking versus non-breaking changes with severity ratings and affected
  surface areas. Use this skill whenever you need to communicate release risk,
  prepare upgrade guides, or triage changes before cutting a release.
when_to_use: |
  - Before publishing a release to flag what requires consumer action
  - When reviewing a PR or diff for API/contract safety
  - When triaging a list of commits into a structured changelog
  - When a team needs a risk assessment before deploying to production
---

# Skill: Classify Breaking Changes

## Purpose

Examine raw input — git log output, diff hunks, changelog prose, or a mix —
and produce a structured classification of every change as either **BREAKING**
or **NON-BREAKING**, with a severity rating and a description of the affected
surface area. Output must be immediately usable by release managers drafting
release notes or migration guides.

---

## Input Formats Accepted

Accept any of the following as input (or a combination):

- Raw `git log` or `git log --oneline` output
- `git diff` or patch file content
- A plain-text list of change descriptions
- An existing draft changelog or release notes document
- A GitHub/GitLab PR description or merge commit message

If no input is pasted inline, ask the user to provide one of the above before
proceeding.

---

## Execution Steps

### Step 1 — Parse and Normalize Input

1. Read all provided content.
2. Split into individual logical change units (one commit, one diff hunk, one
   bullet point, or one described change per unit).
3. Discard noise: formatting commits, typo fixes in comments, CI config tweaks
   that have no consumer-visible effect — mark these as `INTERNAL` and do not
   classify further.

### Step 2 — Classify Each Change

For every change unit, apply the following decision logic:

**BREAKING** if the change does any of the following:
- Removes or renames a public API endpoint, method, function, class, or type
- Changes the signature of a public function (parameter types, order, required
  vs optional, return type)
- Alters the schema of a database table, REST response body, GraphQL type, or
  serialized data format in a non-additive way
- Changes default behavior in a way that breaks existing consumers without
  opt-in
- Drops support for a runtime, language version, OS, or protocol version
- Removes a configuration key or changes its accepted values
- Changes authentication or authorization requirements

**NON-BREAKING** if the change:
- Adds a new optional parameter with a default value
- Adds a new endpoint, method, or field without removing existing ones
- Improves performance with no interface change
- Fixes a bug toward the documented/intended behavior
- Adds deprecation warnings without removal
- Updates documentation, tests, or internal tooling with no public surface change

When uncertain, lean toward **BREAKING** and note the uncertainty.

### Step 3 — Assign Severity Rating

For every BREAKING change, assign one of three severity levels:

| Severity | Meaning |
|----------|---------|
| **CRITICAL** | Consumers will experience failures immediately on upgrade with no workaround |
| **HIGH** | Consumers must take explicit migration action before upgrading |
| **MEDIUM** | Consumers may be affected depending on usage pattern; migration is straightforward |

For NON-BREAKING changes, no severity rating is required.

### Step 4 — Identify Affected Surface Areas

Tag each change with one or more surface area labels from this list (add
unlisted ones as needed):

`API` · `CLI` · `SDK` · `Database/Schema` · `Config` · `Auth` · `Types/Interfaces`
`Events/Webhooks` · `Serialization` · `Runtime/Platform` · `UI/UX` · `Internal`

### Step 5 — Produce Output

Write the final report using the format specified below. Do not truncate or
omit changes; every parsed unit must appear in the output.

---

## Output Format

```
# Breaking Change Classification Report

**Source:** <brief description of input, e.g., "git log v2.3.0..HEAD, 14 commits">
**Generated:** <today's date>
**Summary:** X BREAKING changes (Y CRITICAL, Z HIGH, W MEDIUM) · N NON-BREAKING · M INTERNAL

---

## ⛔ BREAKING CHANGES

### [CRITICAL | HIGH | MEDIUM] <Short title of change>
- **Commit/Reference:** <hash, PR number, or "N/A">
- **Surface Area:** <label(s)>
- **What changed:** <one or two sentences — what was removed, renamed, or altered>
- **Consumer impact:** <what breaks for existing users and under what conditions>
- **Migration hint:** <what a consumer must do to adapt; mark "See migration guide" if complex>

_(Repeat block for each breaking change)_

---

## ✅ NON-BREAKING CHANGES

| Reference | Surface Area | Description |
|-----------|-------------|-------------|
| <hash/ref> | <label> | <one-line description> |

_(One row per non-breaking change)_

---

## 🔧 INTERNAL / SKIPPED

| Reference | Reason Skipped |
|-----------|---------------|
| <hash/ref> | <e.g., "CI config only", "comment typo"> |

---

## Risk Summary

<2–4 sentences summarizing overall release risk, which surface areas are most
affected, and whether a major version bump is warranted under SemVer.>
```

---

## Constraints and Quality Rules

- **Never omit a change.** Every input unit must appear in exactly one section.
- **Be specific.** "API changed" is not acceptable. Name the endpoint, method,
  field, or type that changed.
- **Migration hints are mandatory** for every CRITICAL and HIGH severity item.
  For MEDIUM items, provide a hint if the migration path is non-obvious.
- **SemVer guidance is required** in the Risk Summary: state explicitly whether
  the changes warrant a PATCH, MINOR, or MAJOR version bump.
- **Do not invent changes.** If the input is ambiguous, note the ambiguity in
  the "What changed" field rather than assuming.
- **Use plain language.** Avoid jargon that a release manager or technical
  writer without deep domain knowledge could not act on.
- **Tables must be valid Markdown.** All pipe-delimited tables must render
  correctly.

---

## Usage Examples

### Example 1 — Classify commits from a git log

/classify-breaking

```
a1b2c3d Remove deprecated /v1/users endpoint
e4f5g6h Add /v2/users endpoint with pagination support
i7j8k9l Change `user.role` field from string to enum
m0n1o2p Fix null pointer in payment processor
q3r4s5t Update README installation steps
```

---

### Example 2 — Classify a diff before merging

/classify-breaking

Paste the output of `git diff main..release/3.0` below and I will classify
every hunk for breaking risk before you merge.

_(User pastes diff content)_

---

### Example 3 — Classify a draft changelog for a pending release

/classify-breaking

Here is our draft changelog for v4.2.0. Please classify each item, flag
anything that should block this release from being called a minor version bump,
and produce the full report.

- Removed `legacy_auth` config key
- Added support for OAuth 2.1
- Renamed `ClientOptions.timeout` to `ClientOptions.timeoutMs`
- Improved retry logic for transient network errors
- Dropped Node.js 14 support

---

## Notes for Claude

- If the user provides a version number (e.g., "we are going from v2.3.0 to
  v2.4.0"), validate whether the planned version bump is consistent with the
  changes found and flag any mismatch in the Risk Summary.
- If the user asks for a machine-readable format (JSON, YAML), produce the same
  data structure in the requested format instead of Markdown tables.
- If no input is provided with the trigger, respond with a one-paragraph
  explanation of what input to provide and in what format.