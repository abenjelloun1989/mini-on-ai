---
name: draft-release-notes
trigger: /draft-release-notes
description: >
  Transforms technical changelog entries, git commit logs, or raw diff summaries
  into polished, end-user-facing release notes. Produces plain-language summaries,
  highlights key improvements, and maintains a consistent, approachable tone
  suitable for public publishing on GitHub Releases, product blogs, or docs sites.
when_to_use: >
  Use this skill after generating a changelog or when you have a list of changes
  ready and need to communicate them clearly to end users — not internal engineers.
  Ideal before tagging a release, publishing to npm/PyPI, or posting release
  announcements.
---

# Skill: Draft Release Notes

## Purpose

Convert technical changelog entries, commit summaries, or raw change lists into
release notes that non-technical and technical end users can both understand and
appreciate. The output should feel like a product announcement, not a git log.

---

## Inputs Claude Will Accept

Claude should handle any of these input forms when this skill is triggered:

- A raw git log or `git cliff` / `conventional-commit` output pasted inline
- A path to an existing `CHANGELOG.md` or partial changelog section
- A freeform bullet list of changes the user types directly
- A version number with a request to read the repo's git history automatically

If no input is provided, ask the user:
> "Please paste your changelog entries, commit log, or change list — or tell me
> the version number and I'll read the git history."

---

## Execution Steps

Follow these steps in order every time the skill runs.

### Step 1 — Gather and Parse the Raw Changes

- Accept the input provided (pasted text, file path, or version tag).
- If a file path is given, read the relevant version section from the file.
- If a version tag is given (e.g., `v2.4.0`), run:
  `git log <previous-tag>...<version-tag> --oneline --no-merges`
  to retrieve commits, then parse them.
- Identify and group changes into these categories:
  - **New Features** — net-new capabilities users can act on
  - **Improvements** — enhancements to existing functionality
  - **Bug Fixes** — problems that were resolved
  - **Performance** — speed, memory, or efficiency gains
  - **Security** — vulnerability patches or hardening (always highlight these)
  - **Deprecations** — features being phased out
  - **Breaking Changes** — anything requiring user action to upgrade

### Step 2 — Identify the Highlight

- Choose 1–3 changes that are most impactful or exciting for end users.
- These become the opening "What's new in X" highlights section.
- Prioritize: new features > security fixes > significant performance wins.
- Do NOT highlight internal refactors, CI changes, or dependency bumps as
  highlights unless they directly affect users.

### Step 3 — Translate Technical Language

Apply these translation rules to every entry:

| Avoid (technical)                        | Use instead (plain language)                  |
|------------------------------------------|-----------------------------------------------|
| "Refactored authentication middleware"   | "Sign-in is now faster and more reliable"     |
| "Fixed null pointer dereference in X"    | "Fixed a crash that occurred when X happened" |
| "Upgraded lodash to 4.17.21"             | Omit unless it fixes a user-visible issue     |
| "Added support for Node 20 LTS"          | "Now compatible with Node.js 20 LTS"          |
| "Deprecated `legacyMode` flag"           | "The `legacyMode` option is deprecated — see Migration below" |

Rules:
- Write in second person ("you can now…") or active voice ("we fixed…").
- No internal ticket numbers, PR numbers, or commit hashes in the public output
  (optionally include a collapsed "Full Changelog" link at the bottom).
- Keep each bullet to one sentence unless a brief second sentence adds essential
  user context.
- Spell out what the user can NOW DO differently — not what the code does internally.

### Step 4 — Handle Breaking Changes

If any breaking changes exist:
- Create a dedicated **⚠️ Breaking Changes** section at the TOP of the notes,
  before all other sections.
- For each breaking change, include:
  1. What changed (one sentence)
  2. Who is affected (e.g., "Users of the `config.legacy` API")
  3. What action to take (e.g., "Replace `config.legacy` with `config.v2`")
- Never bury breaking changes inside other sections.

### Step 5 — Compose the Release Notes Document

Assemble the final output in this structure:

```
# Release Notes — [Product Name] [Version]
**Released:** [Date or "today"]

## What's New
[1–3 sentence narrative highlight of the most exciting changes]

## ⚠️ Breaking Changes  ← only if applicable
[Breaking change entries with migration guidance]

## ✨ New Features
[Bullet list]

## 🔧 Improvements
[Bullet list]

## 🐛 Bug Fixes
[Bullet list]

## ⚡ Performance
[Bullet list — omit section if empty]

## 🔒 Security
[Bullet list — omit section if empty]

## 📢 Deprecations
[Bullet list — omit section if empty]

---
[Full Changelog](link) — optional, ask user if they want this line
```

Omit any section that has no entries. Do not include empty headers.

### Step 6 — Tone and Style Check

Before outputting, verify the draft meets these standards:

- [ ] No jargon a non-engineer would not understand without a definition
- [ ] No internal team references, Jira/Linear ticket IDs, or usernames
- [ ] Breaking changes are at the top if present
- [ ] Security fixes are present and clearly labeled if applicable
- [ ] Tone is positive and user-focused ("you can now…", "we've improved…")
- [ ] Version number and product name are correct
- [ ] Length is proportionate — a patch release should not read like a major launch

### Step 7 — Offer Follow-Up Options

After delivering the draft, offer:

> **Next steps:**
> - `/generate-changelog` — generate structured changelog entries from git history
> - Ask me to adjust the tone (more formal / more casual)
> - Ask me to shorten to a Twitter/X-length announcement
> - Ask me to add a migration guide section

---

## Constraints and Quality Rules

- **Never fabricate changes.** Only document what appears in the provided input.
- **Never include internal-only information** (infra details, employee names,
  internal tooling references) in the output.
- **Security fixes must always be surfaced** — never omit or downplay them.
- **Breaking changes must always be first** — never buried.
- If the input is ambiguous (e.g., a vague commit message), note it inline as
  `[Needs clarification: describe what this change does for users]` rather than
  guessing incorrectly.
- Default date to "today" if none is provided; ask if precision matters.
- Default product name to the repo name if detectable; otherwise use a placeholder.

---

## Usage Examples

### Example 1 — Paste a commit log directly

/draft-release-notes

feat: add OAuth2 PKCE support for CLI auth flow
feat: dark mode toggle in dashboard settings
fix: resolve infinite spinner on empty project list
fix: correct timezone offset in exported CSV reports
perf: reduce initial bundle size by 34% via code splitting
chore: upgrade React to 18.3.0
chore: migrate CI from CircleCI to GitHub Actions
security: patch XSS vulnerability in markdown renderer (CVE-2024-3821)
BREAKING CHANGE: removed deprecated `--token` flag; use `--api-key` instead

Version: v3.1.0, Product: Acme CLI

---

### Example 2 — Point to a changelog file section

/draft-release-notes

File: ./CHANGELOG.md, section for version 1.8.2
Audience: non-technical SaaS users
Tone: friendly and encouraging

---

### Example 3 — Generate from git history automatically

/draft-release-notes

Version tag: v0.9.0 (compare against v0.8.3)
Product name: Relay SDK
Include full changelog link: yes

---

## Output Format

Deliver the release notes as clean Markdown, ready to paste into:
- GitHub / GitLab Releases
- A docs site release page
- A product blog post intro
- A README "Latest Release" section

Always end with the follow-up options from Step 7.