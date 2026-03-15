---
name: create-decision-log-template
trigger: /gen-decision-log
description: >
  Generates a reusable Architecture Decision Record (ADR) template plus a
  seeded decision log that captures key architectural choices already visible
  in the codebase. Each entry includes context, options considered, the chosen
  option, and the rationale — so new hires understand *why* the codebase is
  shaped the way it is, not just *what* it looks like.
when_to_use: >
  Run this once when onboarding materials are being assembled, or whenever the
  team realizes important architectural reasoning lives only in people's heads.
  Re-run with a focus path to generate scoped decision logs for a subsystem.
---

# Skill: create-decision-log-template (`/gen-decision-log`)

## Purpose

New engineers waste days reverse-engineering decisions that were made for good
reasons nobody wrote down. This skill produces two artifacts:

1. **`docs/decisions/ADR-TEMPLATE.md`** — a blank, reusable ADR template the
   team can fill in for future decisions.
2. **`docs/decisions/ADR-0000-index.md`** — a running index of all ADRs.
3. **`docs/decisions/ADR-NNNN-<slug>.md`** — one seeded ADR per significant
   architectural pattern detected in the codebase (typically 3–8 records).

---

## Execution Steps

Follow these steps in order. Do not skip steps or merge them.

### Step 1 — Understand the Scope

- Check whether the user provided a path argument (e.g., `/gen-decision-log src/payments`).
- If a path was given, limit codebase analysis to that subtree.
- If no path was given, analyze the entire repository.
- Note any existing `docs/decisions/` or `docs/adr/` folder; if found, read
  existing ADRs to avoid duplicating decisions already documented.

### Step 2 — Detect Architectural Signals

Scan the codebase for patterns that imply deliberate architectural choices.
Look for signals including but not limited to:

- **Framework / runtime choice** — which web framework, ORM, test runner, etc.
- **Monorepo vs. polyrepo** — workspace configs (`pnpm-workspace.yaml`,
  `nx.json`, `lerna.json`, `Cargo.toml` workspaces, etc.)
- **State management strategy** — Redux, Zustand, server state only, etc.
- **API style** — REST, GraphQL, tRPC, gRPC; inferred from route files and
  schema files.
- **Authentication approach** — JWT, session cookies, OAuth provider libraries.
- **Database / storage layer** — migration files, ORM models, raw SQL patterns.
- **Error handling conventions** — global handlers, Result/Either types, try/catch patterns.
- **Testing philosophy** — unit-heavy vs. integration-heavy, e2e presence,
  mocking strategy inferred from test files.
- **CSS / styling strategy** — Tailwind, CSS Modules, styled-components, etc.
- **Deployment target signals** — Dockerfiles, serverless config, platform
  config files (fly.toml, vercel.json, etc.)

For each signal detected, note:
- Where in the codebase the evidence lives (file paths).
- What alternative approaches were *not* chosen (infer from context).
- Likely rationale (performance, team familiarity, ecosystem fit, compliance,
  scale requirements, etc.).

Aim to surface **3–8 decisions**. Do not manufacture decisions for trivial
choices. Prefer fewer, higher-signal ADRs over many shallow ones.

### Step 3 — Write the ADR Template

Create `docs/decisions/ADR-TEMPLATE.md` using exactly this structure:

---
Template content to write verbatim (fill placeholders with instructions):

    # ADR-NNNN: [Short imperative title]
    
    **Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]
    **Date:** YYYY-MM-DD
    **Deciders:** [Names or team]
    **Tags:** [e.g., architecture, security, performance, dx]
    
    ## Context
    
    [Describe the situation and forces at play. What problem needed solving?
    What constraints existed? Keep this factual and neutral.]
    
    ## Decision Drivers
    
    - [Driver 1 — e.g., must support horizontal scaling]
    - [Driver 2]
    - [Driver 3]
    
    ## Options Considered
    
    ### Option A: [Name]
    [Brief description]
    - ✅ Pro: ...
    - ❌ Con: ...
    
    ### Option B: [Name]
    [Brief description]
    - ✅ Pro: ...
    - ❌ Con: ...
    
    ## Decision
    
    **We chose Option X.**
    
    [One paragraph explaining why this option best satisfies the decision drivers.]
    
    ## Consequences
    
    - [Positive outcome expected]
    - [Trade-off accepted]
    - [Follow-up action required, if any]
    
    ## References
    
    - [Link or citation if applicable]

---

### Step 4 — Write the Seeded ADRs

For each architectural decision identified in Step 2:

- Assign a sequential number starting at `ADR-0001`.
- Create a slug from the decision title (lowercase, hyphens, no special chars).
- Write the file to `docs/decisions/ADR-NNNN-<slug>.md`.
- Use the template structure from Step 3.
- Set **Status** to `Accepted` (these are decisions already in effect).
- Set **Date** to today's date unless git history suggests an earlier date.
- Under **Options Considered**, include at least two alternatives (the chosen
  one plus at least one realistic alternative that was likely evaluated).
- Under **Rationale**, be honest about inferred vs. certain reasoning. Use the
  phrase *"Based on the codebase evidence, the likely rationale is…"* when
  the reasoning is inferred rather than explicitly documented.
- Keep each ADR under 60 lines. Concise and scannable beats exhaustive.

### Step 5 — Write the Index

Create `docs/decisions/ADR-0000-index.md`:

    # Architecture Decision Records
    
    This directory contains ADRs for [PROJECT NAME — infer from package.json or
    repo name].
    
    | # | Title | Status | Date |
    |---|-------|--------|------|
    | ADR-0001 | [title] | Accepted | YYYY-MM-DD |
    | ...       | ...     | ...      | ...        |
    
    ## How to Add a New ADR
    
    1. Copy `ADR-TEMPLATE.md` to `ADR-NNNN-short-title.md` (next number in sequence).
    2. Fill in all sections. "Options Considered" must have at least two options.
    3. Open a PR; the ADR is merged when the decision is finalized.
    4. Update this index.
    
    ## Further Reading
    
    - [Documenting Architecture Decisions — Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

### Step 6 — Report to the User

After writing all files, print a summary:

    ✅ Decision log created
    
    Files written:
      docs/decisions/ADR-TEMPLATE.md
      docs/decisions/ADR-0000-index.md
      docs/decisions/ADR-0001-<slug>.md
      ... (list each)
    
    Decisions captured:
      1. [ADR title] — [one-line description]
      2. ...
    
    ⚠️  Review recommended:
      - [Any decision where reasoning was inferred, not certain]
    
    Next step: Share docs/decisions/ in your CONTRIBUTING.md and add a note
    to your onboarding checklist to read the ADRs on day one.

---

## Output Format Rules

- All files are Markdown.
- Use ATX headings (`#`, `##`, `###`), never Setext.
- Tables use GFM pipe syntax.
- Filenames: `ADR-NNNN-kebab-case-title.md` (four-digit zero-padded number).
- Never fabricate specific names of people, dates from the past, or technical
  constraints not evidenced by the codebase.
- Do not create more than 8 seeded ADRs in a single run; prompt the user to
  run again with a focused path if the codebase warrants more.

---

## Constraints

- **Do not overwrite** existing ADR files. If `docs/decisions/ADR-0001-*.md`
  already exists, start numbering new ADRs at the next available slot and note
  this in the summary.
- **Inferred reasoning must be labeled.** Never present inferred rationale as
  confirmed fact.
- **No placeholder filler.** Every section in a seeded ADR must have real
  content. Remove template instruction text before writing.
- **Scope respect.** If the user passed a path, do not include decisions from
  outside that path.

---

## Usage Examples

### Example 1 — Full repository scan

    /gen-decision-log

Analyzes the entire repo, produces ADR template + index + seeded ADRs for all
major architectural patterns found (e.g., Next.js App Router choice, Prisma
over raw SQL, JWT authentication strategy).

### Example 2 — Scoped to a subsystem

    /gen-decision-log src/billing

Limits detection to the `src/billing` subtree. Produces ADRs relevant only to
that domain — e.g., idempotency key strategy, Stripe SDK version pinning,
webhook verification approach.

### Example 3 — Brownfield project with existing ADRs

    /gen-decision-log --dir docs/arch

Reads existing ADRs in `docs/arch/`, skips decisions already documented, and
only generates new ADRs for patterns not yet captured. Adds new entries to the
existing index.