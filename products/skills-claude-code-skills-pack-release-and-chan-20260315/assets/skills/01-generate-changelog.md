---
name: generate-changelog
trigger: /gen-changelog
description: >
  Parses raw git commit history between two refs and generates a structured,
  human-readable changelog grouped by change type (feat, fix, chore, etc.).
  Use this skill whenever you need to produce a CHANGELOG entry, release notes
  draft, or a quick summary of what changed between two points in your git history.
tags: [release, changelog, git, documentation]
---

# Skill: generate-changelog

## Purpose

Transform raw git commit logs between two refs (tags, branches, or SHAs) into a
clean, structured, human-readable changelog. The output is grouped by Conventional
Commit type, highlights breaking changes prominently, and is ready to paste into
a CHANGELOG.md file or a GitHub/GitLab release page.

## When to Use

- Before cutting a release and you need a CHANGELOG.md entry
- When a project manager or stakeholder asks "what changed in this release?"
- As a first step before drafting end-user release notes (use `/gen-release-notes` next)
- Any time you want a readable summary of commits between two git refs

---

## Execution Instructions

Follow these steps exactly, in order.

### Step 1 — Collect inputs

Parse the slash-command invocation for the following arguments:

| Argument | Flag | Required | Default |
|---|---|---|---|
| Base ref (older) | `--from` | Yes | — |
| Target ref (newer) | `--to` | No | `HEAD` |
| Version label | `--version` | No | derived from `--to` |
| Output format | `--format` | No | `markdown` |

If `--from` is missing, ask the user: *"What is the base ref (tag, branch, or SHA)
you want to compare from?"* Do not proceed until it is provided.

### Step 2 — Retrieve the git log

Run the following command to get the raw commit list:

    git log <from>..<to> --pretty=format:"%H|%s|%b|%an|%ad" --date=short

If the working directory is unknown, ask the user to confirm the repo path or
run `git rev-parse --show-toplevel` first.

If the git command fails (bad ref, not a git repo, etc.), report the exact error
and stop. Do not fabricate commit data.

### Step 3 — Parse and classify each commit

For every commit line returned:

1. Extract the **type** from the Conventional Commit prefix in the subject:
   `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
2. Extract the **scope** from parentheses if present, e.g. `feat(auth):`.
3. Extract the **short description** (everything after the colon).
4. Check for a **breaking change** indicator: `!` after the type/scope OR a
   `BREAKING CHANGE:` footer in the commit body.
5. If the commit does not follow Conventional Commits format, classify it as `other`.

### Step 4 — Group and sort entries

Organize commits into the following sections in this exact order:

1. **🚨 Breaking Changes** — any commit flagged as breaking, regardless of type
2. **✨ Features** — type `feat`
3. **🐛 Bug Fixes** — type `fix`
4. **⚡ Performance** — type `perf`
5. **♻️ Refactoring** — type `refactor`
6. **📚 Documentation** — type `docs`
7. **🧪 Tests** — type `test`
8. **🔧 Build & CI** — types `build` and `ci`
9. **🧹 Chores** — type `chore`
10. **↩️ Reverts** — type `revert`
11. **📦 Other** — anything unclassified

Omit any section that has zero entries. Do not show empty headings.

### Step 5 — Format the output

Produce the changelog in the requested format (default: Markdown).

**Markdown format rules:**

- Top-level heading: `## [<version>] — <date>`
  - Use the `--version` value if provided; otherwise use the `--to` ref label.
  - Date = today's date in `YYYY-MM-DD` format.
- Each section is an H3 heading with its emoji and label.
- Each commit is a bullet: `- **[scope]** Short description. ([<short-sha>](<commit-url>))`
  - Omit `[scope]` if none was present.
  - Include the short SHA (first 7 chars). If a remote URL can be detected via
    `git remote get-url origin`, make the SHA a hyperlink to the commit.
- Breaking change entries must also appear in the **🚨 Breaking Changes** section
  AND in their original type section, marked with `⚠️ BREAKING`.
- Wrap the entire output in a code block only if the user explicitly requests it;
  otherwise output raw Markdown.

### Step 6 — Report summary statistics

After the changelog block, append a brief summary line:

> **Changelog stats:** X commits parsed — Y features, Z fixes, N breaking changes,
> M other. Range: `<from>..<to>`.

---

## Constraints and Quality Rules

- **Never fabricate commits.** Only use data returned by the actual git command.
- **Never silently drop commits.** Every commit must appear in exactly one section
  (or two sections if it is also a breaking change).
- **Preserve original descriptions.** Do not rewrite or editorialize commit messages
  beyond light cleanup (e.g., capitalize first letter, remove trailing period).
- Keep each bullet to a single line. If a commit subject is longer than 100 characters,
  truncate with `…` and add the full text as a nested blockquote.
- If zero commits are found in the range, say so explicitly:
  *"No commits found between `<from>` and `<to>`."* — do not output an empty changelog.
- Do not include merge commits (`Merge branch …`, `Merge pull request …`) unless
  they carry meaningful information. Filter them by default; add them to **Other**
  only if the user passes `--include-merges`.

---

## Usage Examples

### Example 1 — Changelog between two version tags

    /gen-changelog --from v1.4.0 --to v1.5.0 --version 1.5.0

Produces a full Markdown changelog entry for version 1.5.0, comparing all commits
after the `v1.4.0` tag up to and including `v1.5.0`.

---

### Example 2 — Changelog from a tag to HEAD (unreleased)

    /gen-changelog --from v2.0.0-rc.1

Compares `v2.0.0-rc.1..HEAD` and labels the output as `[Unreleased]` since no
`--version` or `--to` was supplied. Useful for previewing what will go into the
next release.

---

### Example 3 — Changelog between two branches with a custom version label

    /gen-changelog --from origin/release/3.1 --to origin/release/3.2 --version 3.2.0

Generates a changelog across two release branches, labelling the entry `3.2.0`.
Useful in trunk-based workflows where releases are cut from named branches rather
than tags.

---

## Output Example (truncated)

## [1.5.0] — 2024-11-12

### 🚨 Breaking Changes

- Removed legacy `/v1/users` endpoint; migrate to `/v2/users`. ([a1b2c3d](https://github.com/org/repo/commit/a1b2c3d)) ⚠️ BREAKING

### ✨ Features

- **auth** Add OAuth2 PKCE flow support. ([d4e5f6a](https://github.com/org/repo/commit/d4e5f6a))
- **api** ⚠️ BREAKING Removed legacy `/v1/users` endpoint. ([a1b2c3d](https://github.com/org/repo/commit/a1b2c3d))

### 🐛 Bug Fixes

- **payments** Correct rounding error on invoice totals. ([7890abc](https://github.com/org/repo/commit/7890abc))

**Changelog stats:** 14 commits parsed — 2 features, 1 fix, 1 breaking change, 10 other. Range: `v1.4.0..v1.5.0`.