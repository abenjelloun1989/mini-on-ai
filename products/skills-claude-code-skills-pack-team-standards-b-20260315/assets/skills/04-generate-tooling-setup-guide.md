---
name: generate-tooling-setup-guide
trigger: /gen-tooling-guide
description: >
  Scans the project's configuration files (ESLint, Prettier, stylelint, Husky,
  lint-staged, EditorConfig, tsconfig, .nvmrc, Makefile, package.json scripts,
  etc.) and produces a comprehensive, step-by-step linting, formatting, and
  tooling setup guide. Each tool is explained in plain language — what it does,
  why the team chose it, and how its rules enforce specific coding standards.
  Designed for new hires who need to get their local environment aligned with
  team conventions quickly and understand the reasoning behind each decision.
when_to_use: >
  Use this skill when onboarding new engineers, when tooling changes and the
  docs need refreshing, or when the team wants a single authoritative reference
  for "how we set up our dev environment." Works best on projects that already
  have at least a few config files in place.
---

# Skill: generate-tooling-setup-guide

## Purpose

Read the project's existing configuration files and generate a human-friendly
`TOOLING_SETUP.md` that walks a new engineer through every linting, formatting,
and code-quality tool the team uses — including setup steps, key rule
explanations, and the rationale behind each choice.

---

## Execution Instructions

Follow these steps in order. Do not skip steps even if a config file appears
simple.

### Step 1 — Discover Configuration Files

Search the repository root and common subdirectories for the following files.
Record every file found; note files that are absent.

Config files to look for:

- `.eslintrc`, `.eslintrc.js`, `.eslintrc.cjs`, `.eslintrc.json`, `.eslintrc.yaml`, `eslint.config.js`
- `.prettierrc`, `.prettierrc.js`, `.prettierrc.json`, `prettier.config.js`
- `.stylelintrc`, `stylelint.config.js`
- `.editorconfig`
- `tsconfig.json`, `tsconfig.base.json`, `tsconfig.*.json`
- `.nvmrc`, `.node-version`, `.tool-versions`
- `.huskyrc`, `.husky/` directory, `husky` config in `package.json`
- `lint-staged.config.js`, `.lintstagedrc`, `lint-staged` key in `package.json`
- `commitlint.config.js`, `.commitlintrc`
- `Makefile`, `Taskfile.yml`, `justfile`
- `package.json` — capture `scripts`, `engines`, `volta`, and `packageManager` fields
- `.npmrc`, `.yarnrc`, `.yarnrc.yml`, `pnpm-workspace.yaml`
- `babel.config.js`, `.babelrc`
- `vitest.config.ts`, `jest.config.js`, `jest.config.ts`
- `playwright.config.ts`, `cypress.config.ts`
- `.github/workflows/` — any CI files that run lint or format checks

### Step 2 — Parse and Summarize Each Tool

For each discovered config file, extract:

1. **Tool name and version** (from `package.json` devDependencies if present)
2. **Purpose** — one sentence describing what the tool enforces
3. **Key rules or settings** — the 3–8 most impactful options configured
4. **Rule rationale** — infer why each rule exists based on its name, value, and
   common industry context; flag where rationale is uncertain with `[inferred]`
5. **Integration points** — where the tool runs (editor, pre-commit, CI)

### Step 3 — Determine Node / Runtime Version Requirements

Check `.nvmrc`, `.node-version`, `.tool-versions`, `engines` in `package.json`,
and `volta` field. Document the required Node version and the recommended
version manager.

### Step 4 — Map the Pre-commit and CI Pipeline

Trace the full automation chain:

- Which hooks exist in Husky (or equivalent)?
- What does `lint-staged` run on which file globs?
- Which CI workflow steps run lint, type-check, or format verification?
- Are there any `package.json` scripts that orchestrate multiple checks?

Produce a short pipeline diagram in ASCII or Markdown table form.

### Step 5 — Generate TOOLING_SETUP.md

Write the output file using the structure below. Use plain, welcoming language
suitable for a developer who is competent but new to this specific codebase.

---

## Output File Structure: TOOLING_SETUP.md

Use exactly this section order:

1. **Title and Intro** — one paragraph explaining what this file covers and who it is for
2. **Prerequisites** — Node version, package manager, any global installs required
3. **Quick Start** — the minimal set of commands to get fully set up (install deps, run first lint pass)
4. **Tool-by-Tool Reference** — one sub-section per tool, each containing:
   - What it is
   - Why we use it
   - How to run it locally
   - Key configuration highlights (bullet list of rules + rationale)
   - Common errors and how to fix them (if inferable from config)
5. **Pre-commit Hooks** — what runs automatically before a commit and why
6. **CI Checks** — what the pipeline enforces and how to reproduce failures locally
7. **Editor Setup** — recommended VS Code extensions or IDE settings derived from config
8. **Troubleshooting** — at least 3 common setup issues with solutions
9. **Keeping the Guide Updated** — one paragraph instructing the reader to re-run `/gen-tooling-guide` after modifying config files

---

## Output Constraints

- Write to `TOOLING_SETUP.md` in the repository root unless the user specifies
  another path with `--output <path>`
- Do not invent tools or rules that are not present in the config files
- When rationale cannot be determined with confidence, write `[inferred]` after
  the explanation rather than stating it as fact
- Keep each "Key configuration highlights" bullet to one line of rule + one line
  of rationale — do not write paragraphs per rule
- Use fenced code blocks for all shell commands
- Use a second-person, active voice throughout ("Run this command", "You will
  see", "Your editor should")
- If a major category of tooling is absent (e.g., no formatter found), note the
  gap explicitly in the relevant section with a callout block
- Target reading level: an experienced developer who is new to this repo, not a
  beginner tutorial

---

## Flags and Options

| Flag | Behavior |
|---|---|
| `--output <path>` | Write the guide to a custom path instead of `TOOLING_SETUP.md` |
| `--dry-run` | Print the guide to the terminal without writing a file |
| `--verbose` | Include extended rationale and full rule lists instead of top 3–8 |
| `--ci-only` | Scope the output to CI-relevant checks only, skip editor setup |

---

## Quality Rules

Before finalizing the output, verify:

- [ ] Every tool mentioned in the guide has a corresponding config file that was
      actually found in the repo
- [ ] The Quick Start section can be followed top-to-bottom without referencing
      other sections
- [ ] All shell commands use the correct package manager (npm / yarn / pnpm)
      as detected from lockfiles or `packageManager` field
- [ ] No section is empty — if content cannot be determined, write an explicit
      note explaining what is missing and how to fill it in
- [ ] The pre-commit pipeline diagram accurately reflects what is in the Husky
      and lint-staged config

---

## Usage Examples

**Basic usage — generate the guide from project root:**

  /gen-tooling-guide

Expected result: `TOOLING_SETUP.md` is created at the repo root covering all
discovered tools with rationale and setup steps.

---

**Write guide to a custom docs directory:**

  /gen-tooling-guide --output docs/onboarding/tooling-setup.md

Expected result: Same content written to `docs/onboarding/tooling-setup.md`
instead of the root. Useful for projects that keep all onboarding docs in one
place.

---

**Preview without writing a file, full rule detail:**

  /gen-tooling-guide --dry-run --verbose

Expected result: The complete guide is printed to the terminal with extended
rule explanations and full configuration listings. Use this to review before
committing the file, or to share as a gist during a team review.

---

## Notes for Claude

- If `package.json` is absent entirely, state clearly at the top of the output
  that the project type could not be determined and list which files were used
  as the basis for the guide.
- If conflicting configs are found (e.g., two ESLint config files), flag the
  conflict in the Troubleshooting section and recommend which to canonicalize.
- Preserve any inline comments found in JS-format config files — these often
  contain the most reliable rationale and should be quoted directly rather than
  paraphrased.
- When a tool is present in `devDependencies` but has no config file, note it
  as "installed but unconfigured" and suggest the team add a config or remove
  the dependency to reduce confusion for new hires.