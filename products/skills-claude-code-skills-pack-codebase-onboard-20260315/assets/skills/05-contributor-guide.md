---
name: contributor-guide
trigger: /gen-contributor-guide
description: >
  Generates a tailored contributor guide covering branching strategy, code style
  conventions, PR and review process, testing requirements, and deployment workflow.
  Use this skill when onboarding new engineers who need a single authoritative
  reference for how to contribute code to this repository. Produces a
  CONTRIBUTING.md-ready document grounded in actual repo evidence rather than
  generic boilerplate.
tags: [onboarding, documentation, contributing, process]
---

# Skill: Generate Contributor Guide

## Purpose

Produce a practical, repo-specific contributor guide so new engineers understand
exactly how to make their first — and every subsequent — contribution. The output
should reflect this codebase's actual conventions, not generic advice. A new hire
should be able to read it and open a compliant PR without asking anyone for help.

---

## When to Use This Skill

- When a project has no CONTRIBUTING.md or the existing one is outdated
- When onboarding a batch of new engineers and you need a reliable reference
- After significant process changes (new branching model, CI system, linting rules)
- When preparing an open-source release that requires contribution documentation

---

## Execution Instructions

Follow these steps in order. Do not skip evidence-gathering steps — the guide
must reflect actual repo state, not assumptions.

### Step 1 — Discover Repository Evidence

Examine the repository to gather ground truth. Look for:

**Version control signals**
- Branch names visible in git history or config (`main`, `develop`, `release/*`)
- Merge commit patterns (squash, merge commits, rebases)
- Existing branch protection rules mentioned in README or CI config
- Commit message format patterns in recent history

**Code style signals**
- Linter config files: `.eslintrc*`, `.pylintrc`, `pyproject.toml`, `.rubocop.yml`,
  `checkstyle.xml`, `.golangci.yml`, `biome.json`, `prettier.config.*`, etc.
- Formatter config: `.prettierrc`, `rustfmt.toml`, `gofmt` usage in Makefile
- EditorConfig: `.editorconfig`
- Pre-commit hooks: `.pre-commit-config.yaml`, `.husky/`

**PR and review signals**
- Pull request templates: `.github/pull_request_template.md` or
  `.github/PULL_REQUEST_TEMPLATE/`
- CODEOWNERS file
- Review requirements in CI config or documented in README
- Issue templates in `.github/ISSUE_TEMPLATE/`

**Testing signals**
- Test framework config: `jest.config.*`, `pytest.ini`, `vitest.config.*`,
  `go test` usage, `rspec`, `phpunit.xml`, etc.
- Coverage thresholds in CI config or test config files
- Test directory structure and naming conventions (`*.test.ts`, `*_test.go`,
  `spec/`, `tests/`)
- CI test steps in `.github/workflows/`, `.circleci/`, `Jenkinsfile`,
  `.gitlab-ci.yml`, `Makefile`

**Deployment signals**
- Deployment scripts or Makefile targets (`deploy`, `release`, `publish`)
- CD pipeline definitions
- Environment references (`staging`, `production`, `preview`)
- Release tooling: `semantic-release`, `changesets`, `goreleaser`, `bump2version`

### Step 2 — Identify Gaps

Note any areas where evidence is thin or absent. You will fill these with clearly
labeled placeholder blocks so the engineering lead can complete them.

Use this marker format for missing information:

> ⚠️ **[NEEDS INPUT]** Describe what information is missing and what the lead
> should supply here.

### Step 3 — Draft the Contributor Guide

Write the full guide following the structure below. Every section must contain
either evidence-backed content or a clearly marked placeholder.

---

## Output Format

Produce a complete Markdown document structured as follows. Use this exact
heading hierarchy.

---

# Contributing to [Project Name]

Welcome to [Project Name]. This guide covers everything you need to contribute
code effectively. Read it end-to-end before opening your first PR.

## Table of Contents

- [Getting Started](#getting-started)
- [Branching Strategy](#branching-strategy)
- [Code Style and Formatting](#code-style-and-formatting)
- [Making Changes](#making-changes)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Code Review Standards](#code-review-standards)
- [Deployment and Release Workflow](#deployment-and-release-workflow)
- [Getting Help](#getting-help)

---

## Getting Started

Prerequisites and first-time setup. (Link to environment setup doc if one exists
in the repo — e.g., `docs/setup.md` or the README setup section.)

## Branching Strategy

Cover:
- Protected branches and what they represent
- Branch naming conventions with examples (`feature/`, `fix/`, `chore/`, etc.)
- How long-lived branches (if any) relate to each other
- Rebase vs. merge policy

## Code Style and Formatting

Cover:
- Languages in use and the formatter/linter for each
- How to run formatting locally (exact commands)
- Which rules are auto-enforced by CI vs. advisory
- Any naming conventions for files, functions, variables not caught by linters

## Making Changes

Cover:
- Commit message format (Conventional Commits, custom format, or freeform)
- Atomic commit guidance
- How to handle work-in-progress (draft PRs, feature flags)
- Dependency change process if relevant

## Testing Requirements

Cover:
- What types of tests exist (unit, integration, e2e, snapshot)
- Minimum coverage threshold if enforced
- How to run the full test suite locally (exact commands)
- What new code is expected to test
- How to run a single test or a subset

## Pull Request Process

Cover:
- How to open a PR (template fields, required labels, linked issues)
- Draft PR policy
- Checklist before marking ready for review
- How long PRs should stay open before follow-up

## Code Review Standards

Cover:
- Required number of approvals
- Who reviews what (CODEOWNERS if present)
- What reviewers check for (correctness, style, tests, docs)
- How to respond to review feedback
- What "approved" means before merge

## Deployment and Release Workflow

Cover:
- How code moves from merged PR to production
- Environment pipeline (staging → production or equivalent)
- Who triggers deployments
- How to verify a deployment succeeded
- Versioning and changelog process

## Getting Help

- Where to ask questions (Slack channel, GitHub Discussions, etc.)
- Who to contact for process questions
- How to report a problem with this guide

---

## Quality Rules

- **Evidence-first**: Every claim about process must be traceable to a file,
  config, or commit pattern in the repo. Do not invent conventions.
- **Exact commands**: All CLI commands must be copy-pasteable. No pseudocode.
- **No filler**: Omit sections that genuinely have no evidence and no reasonable
  default — mark them as `[NEEDS INPUT]` instead.
- **Tone**: Direct and informative. Write for a competent engineer new to this
  repo, not a beginner to software development.
- **Length**: Comprehensive but scannable. Use bullet lists for enumerable items;
  prose only where reasoning needs explanation.
- **Accuracy over completeness**: A shorter accurate guide beats a longer one
  full of guesses.

---

## Usage Examples

### Example 1 — Basic invocation

/gen-contributor-guide

Claude will scan the repository and produce a full CONTRIBUTING.md draft based
on discovered evidence, with `[NEEDS INPUT]` markers for anything it cannot
determine from the codebase alone.

---

### Example 2 — Specifying the target audience

/gen-contributor-guide for external open-source contributors, assume no internal
tooling access and no access to private Slack

Claude will scope the guide to what external contributors can actually do,
omitting internal deployment steps and replacing internal communication channels
with public alternatives (GitHub Issues, Discussions).

---

### Example 3 — Updating an existing guide

/gen-contributor-guide update the existing CONTRIBUTING.md to reflect the new
Changesets release workflow we migrated to last quarter

Claude will read the existing CONTRIBUTING.md and the Changesets config, then
produce a revised document with the release workflow section replaced and a
summary of what changed so the lead can review the diff.

---

## Output Delivery

After generating the guide, provide a brief summary section (outside the guide
itself) that lists:

1. **Sections fully populated from evidence** — what was found and where
2. **Sections partially populated** — what was inferred and the confidence level
3. **Sections marked [NEEDS INPUT]** — what the lead must supply before the
   guide is usable
4. **Recommended next step** — e.g., "Commit as CONTRIBUTING.md and share the
   three [NEEDS INPUT] items with your team lead"