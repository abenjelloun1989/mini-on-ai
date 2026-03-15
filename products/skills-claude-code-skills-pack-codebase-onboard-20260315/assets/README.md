# Claude Code Skills Pack: Codebase Onboarding Docs — 5 Skills for Getting New Engineers Up to Speed Fast

For engineering leads and staff engineers, this pack generates architecture overviews, maps module dependencies, documents environment setup steps, explains key design decisions, and produces contributor guides so new hires can become productive in days instead of weeks

## What's included

- **5 ready-to-use SKILL.md files** — drop into your project's `skills/` folder, no setup required
- **guide.md** — installation instructions and quick-reference table for all 5 skills
- Each skill is immediately usable with its slash-command trigger

## Skills in this pack

- `skills/01-architecture-overview.md` — `/gen-architecture` — Analyzes the codebase structure and generates a high-level architecture overview document covering system components, data flow, service boundaries, and technology stack decisions.
- `skills/02-module-dependency-map.md` — `/map-dependencies` — Scans the codebase to map and document inter-module and inter-service dependencies, producing a visual-ready dependency graph with written explanations of coupling points and critical paths.
- `skills/03-environment-setup-guide.md` — `/gen-env-setup` — Inspects configuration files, scripts, and tooling to generate a step-by-step local environment setup guide covering prerequisites, installation, configuration, and verification steps for new engineers.
- `skills/04-design-decisions-explainer.md` — `/explain-decisions` — Mines git history, comments, and code patterns to surface and document key architectural and technical design decisions, explaining the context, trade-offs, and rationale behind why the codebase is built the way it is.
- `skills/05-contributor-guide.md` — `/gen-contributor-guide` — Produces a tailored contributor guide covering branching strategy, code style conventions, PR and review process, testing requirements, and deployment workflow so new engineers know exactly how to contribute from day one.

## Quick Start

1. Copy the `skills/` folder into your project root
2. Run `claude` in your project directory
3. Use any skill trigger listed above

## Files

- `skills/` — 5 SKILL.md files, one per skill
- `guide.md` — Installation guide and quick-reference table
- `README.md` — This file
