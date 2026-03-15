---
name: generate-contributing-guide
trigger: /gen-contributing
description: >
  Generates a comprehensive CONTRIBUTING.md file tailored to the current
  project. Infers branching strategy, commit conventions, PR process, and
  tooling from existing repo artifacts, then produces a ready-to-commit
  guide that helps new hires contribute confidently from day one.
when_to_use: >
  Use when onboarding new engineers, when no CONTRIBUTING.md exists, or when
  the existing one is outdated and doesn't reflect how the team actually works.
  Best run after the codebase has at least a few merged PRs and a package
  manifest to inspect.
---

# Skill: Generate Contributing Guide

## Purpose

Analyze the current repository and produce a complete, project-specific
CONTRIBUTING.md that covers everything a new hire needs to make their first
pull request without asking for help.

---

## Execution Steps

Follow these steps in order. Do not skip inference steps — the quality of
the output depends on reading real project context before writing.

### Step 1 — Inventory Existing Artifacts

Scan the repo for signals that reveal how the team works:

- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or equivalent
  for language, tooling, and script commands
- `.github/` for existing PR templates, issue templates, workflow files
- `.eslintrc*`, `.prettierrc*`, `ruff.toml`, `.golangci.yml`, or equivalent
  linting configs
- `CHANGELOG.md` or commit history to infer commit message format
  (Conventional Commits, Angular, freeform, etc.)
- Existing branch names in remote refs or recent git log to infer branching
  strategy (GitFlow, trunk-based, feature branches, etc.)
- `README.md` for setup instructions already documented
- `Makefile` or `justfile` for common developer commands
- Any existing `CONTRIBUTING.md` or `docs/contributing*` to avoid
  contradicting documented decisions

### Step 2 — Identify Key Conventions

From the artifacts above, determine:

| Convention | What to look for |
|---|---|
| Branching strategy | Branch name patterns: `feat/`, `fix/`, `main`+`develop`, single `main` |
| Commit format | Commit messages in git log; presence of `commitlint` config |
| PR size norms | Average diff size from recent merged PRs if accessible |
| Review requirements | `CODEOWNERS`, required reviewers in branch protection settings |
| Test requirements | CI workflow steps, coverage thresholds in config files |
| Release process | Tags, `semantic-release`, `changesets`, manual changelog |

If a convention cannot be inferred, insert a clearly marked placeholder:
`[TODO: confirm with team]`

### Step 3 — Draft the CONTRIBUTING.md

Write the file using the structure below. Populate each section with
project-specific details from Step 2. Do not use generic filler content —
every sentence should reflect the actual project.

**Required sections in this order:**

1. **Welcome** — One short paragraph. Who this guide is for and what it
   helps them do. Mention the project name.

2. **Prerequisites** — Exact versions or version ranges for runtime,
   package manager, and any required global tools. Link to the README
   setup section if it already covers installation.

3. **Getting Started Locally** — Numbered steps from clone to running
   tests successfully. Use the actual commands found in Step 1.

4. **Branching Strategy** — Name the strategy. Show the branch naming
   pattern with one concrete example per branch type used on this project.

5. **Commit Message Format** — Show the format. If Conventional Commits,
   include the type list actually used in this repo. Provide 2–3 real
   example commit messages in a code block.

6. **Opening a Pull Request** — Checklist a contributor must complete
   before marking PR ready. Reference any PR template found in Step 1.
   State the expected turnaround time for review if it can be inferred.

7. **Code Review Expectations** — What reviewers look for. What authors
   should do when they receive feedback. Tone and communication norms.

8. **Testing Requirements** — How to run the test suite. Coverage
   threshold if configured. What kinds of tests are required for what
   kinds of changes.

9. **CI / Linting** — List the CI checks that must pass. Show the command
   to run linting locally. Note any auto-fix commands available.

10. **Release Process** — How versions are cut. Who does it. Whether
    contributors need to update a changelog or if it is automated.

11. **Onboarding Checklist** — A checkbox list for a new hire's first week:
    repo access, local setup, read key docs, shadow a PR review, open a
    small first PR. Tailor items to what is available in this repo.

12. **Getting Help** — Where to ask questions (Slack channel placeholder,
    GitHub Discussions, mailing list). Who to contact for what.

### Step 4 — Self-Review Before Output

Before writing the final file, verify:

- [ ] No section contains generic Lorem-ipsum-style filler
- [ ] All commands are copied from actual project scripts, not invented
- [ ] Every `[TODO: confirm with team]` placeholder is used sparingly and
      only where inference was genuinely impossible
- [ ] The branching and commit sections do not contradict each other
- [ ] The document reads as written by someone who knows this codebase

### Step 5 — Write the File

Write the completed CONTRIBUTING.md to the repository root.

If a CONTRIBUTING.md already exists, ask the user:
> "A CONTRIBUTING.md already exists. Should I (A) overwrite it, (B) write
> to CONTRIBUTING.new.md for manual review, or (C) show a diff of
> proposed changes?"

Wait for their response before writing.

---

## Output Format Rules

- Use standard Markdown: ATX headings (`##`, `###`), fenced code blocks
  with language tags, and GitHub Flavored Markdown task list syntax
  (`- [ ]`) for checklists
- Maximum one H1 heading at the top of the file (`# Contributing`)
- Code examples must use real project commands, not placeholder commands
  like `npm run <script>`
- Tone: direct, friendly, authoritative — written for a senior engineer
  joining a team, not a beginner learning to code
- Length: aim for 400–700 lines. Long enough to be complete, short enough
  to be read in one sitting
- Do not include a table of contents unless the file exceeds 600 lines

---

## Constraints

- Never invent tooling or scripts that don't exist in the project
- Never assert a branching strategy you cannot support with evidence from
  the repo
- If the repo is brand new with no history, state this clearly and produce
  a recommended-defaults version, labeled as such at the top of the file
- Do not duplicate content already in README.md — link to it instead
- Do not include a Code of Conduct section — that belongs in a separate
  CODE_OF_CONDUCT.md

---

## Usage Examples

**Example 1 — Basic invocation on an existing Node.js project:**

  /gen-contributing

Claude scans the repo, finds `package.json` with lint/test scripts,
`.github/pull_request_template.md`, and `commitlint.config.js`, then
generates a CONTRIBUTING.md using Conventional Commits format and the
existing PR template checklist.

---

**Example 2 — New repo with no history:**

  /gen-contributing

Claude finds only a `pyproject.toml` and empty `src/` directory, notes
that no conventions can be inferred, and produces a CONTRIBUTING.md with
recommended defaults for a Python project (trunk-based branching,
Conventional Commits, `ruff` for linting), each section labeled
`[RECOMMENDED DEFAULT — confirm with team]`.

---

**Example 3 — Overwrite guard in action:**

  /gen-contributing

Claude detects an existing CONTRIBUTING.md dated 18 months ago. It prompts
the user to choose between overwrite, writing to CONTRIBUTING.new.md, or
showing a diff. User chooses option B. Claude writes the new version to
CONTRIBUTING.new.md and prints a summary of the major differences from
the original.

---

## Related Skills in This Pack

- `/infer-conventions` — Surfaces naming patterns and folder structure
  rationale without generating a full guide
- `/gen-decision-log` — Creates an ADR template explaining why key
  architectural choices were made
- `/gen-tooling-guide` — Produces the linting and tooling setup guide
  referenced in the CI / Linting section above