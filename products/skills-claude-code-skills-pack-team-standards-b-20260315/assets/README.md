# Claude Code Skills Pack: Team Standards Bootstrapping — 5 Skills for Communicating Coding Conventions to New Hires

For engineering leads and DevEx teams, this pack infers coding conventions from existing code, generates a CONTRIBUTING.md from scratch, documents naming patterns and folder structure rationale, produces a linting and tooling setup guide, and creates a decision log template capturing why key architectural choices were made so new team members understand not just what the rules are but why they exist.

## What's included

- **5 ready-to-use SKILL.md files** — drop into your project's `skills/` folder, no setup required
- **guide.md** — installation instructions and quick-reference table for all 5 skills
- Each skill is immediately usable with its slash-command trigger

## Skills in this pack

- `skills/01-infer-coding-conventions.md` — `/infer-conventions` — Scans the existing codebase to infer implicit coding conventions, naming patterns, and structural norms, then produces a structured conventions summary ready for documentation.
- `skills/02-generate-contributing-guide.md` — `/gen-contributing` — Generates a comprehensive CONTRIBUTING.md from scratch covering branching strategy, commit message format, PR process, code review expectations, and onboarding steps tailored to the project.
- `skills/03-document-folder-structure.md` — `/doc-structure` — Produces a human-readable folder structure map annotated with the rationale behind each directory's purpose, naming choice, and organizational principle so new hires understand the why, not just the what.
- `skills/04-generate-tooling-setup-guide.md` — `/gen-tooling-guide` — Creates a step-by-step linting, formatting, and tooling setup guide derived from the project's config files, explaining each tool's role and how the rules enforce team standards.
- `skills/05-create-decision-log-template.md` — `/gen-decision-log` — Generates an Architecture Decision Record (ADR) template and seeds it with a starter decision log capturing key architectural choices already present in the codebase, including context, options considered, and rationale.

## Quick Start

1. Copy the `skills/` folder into your project root
2. Run `claude` in your project directory
3. Use any skill trigger listed above

## Files

- `skills/` — 5 SKILL.md files, one per skill
- `guide.md` — Installation guide and quick-reference table
- `README.md` — This file
