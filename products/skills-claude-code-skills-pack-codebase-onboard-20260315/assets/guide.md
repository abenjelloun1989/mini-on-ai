# Claude Code Skills Pack: Codebase Onboarding Docs — 5 Skills for Getting New Engineers Up to Speed Fast

> For engineering leads and staff engineers, this pack generates architecture overviews, maps module dependencies, documents environment setup steps, explains key design decisions, and produces contributor guides so new hires can become productive in days instead of weeks

---

## What's in This Pack

Generates comprehensive onboarding documentation for new engineers — including architecture overviews, dependency maps, environment setup guides, design decision explanations, and contributor guides — so engineering leads can get new hires productive in days instead of weeks.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/gen-architecture`** — `01-architecture-overview.md`
   Analyzes the codebase structure and generates a high-level architecture overview document covering system components, data flow, service boundaries, and technology stack decisions.

**2. `/map-dependencies`** — `02-module-dependency-map.md`
   Scans the codebase to map and document inter-module and inter-service dependencies, producing a visual-ready dependency graph with written explanations of coupling points and critical paths.

**3. `/gen-env-setup`** — `03-environment-setup-guide.md`
   Inspects configuration files, scripts, and tooling to generate a step-by-step local environment setup guide covering prerequisites, installation, configuration, and verification steps for new engineers.

**4. `/explain-decisions`** — `04-design-decisions-explainer.md`
   Mines git history, comments, and code patterns to surface and document key architectural and technical design decisions, explaining the context, trade-offs, and rationale behind why the codebase is built the way it is.

**5. `/gen-contributor-guide`** — `05-contributor-guide.md`
   Produces a tailored contributor guide covering branching strategy, code style conventions, PR and review process, testing requirements, and deployment workflow so new engineers know exactly how to contribute from day one.

---

## How to Install

1. **Create a `skills/` directory** in your project root (if it doesn't exist):
   ```bash
   mkdir -p skills
   ```

2. **Copy all skill files** from the `skills/` folder in this pack:
   ```bash
   cp skills/*.md /your-project/skills/
   ```

3. **Run Claude Code** in your project directory — all skills are immediately available:
   ```bash
   claude
   ```

---

## Quick Reference

| Skill | Trigger | File |
|-------|---------|------|
| Analyzes the codebase structure and generates a high-level architecture overview document covering system components, data flow, service boundaries, and technology stack decisions. | `/gen-architecture` | `01-architecture-overview.md` |
| Scans the codebase to map and document inter-module and inter-service dependencies, producing a visual-ready dependency graph with written explanations of coupling points and critical paths. | `/map-dependencies` | `02-module-dependency-map.md` |
| Inspects configuration files, scripts, and tooling to generate a step-by-step local environment setup guide covering prerequisites, installation, configuration, and verification steps for new engineers. | `/gen-env-setup` | `03-environment-setup-guide.md` |
| Mines git history, comments, and code patterns to surface and document key architectural and technical design decisions, explaining the context, trade-offs, and rationale behind why the codebase is built the way it is. | `/explain-decisions` | `04-design-decisions-explainer.md` |
| Produces a tailored contributor guide covering branching strategy, code style conventions, PR and review process, testing requirements, and deployment workflow so new engineers know exactly how to contribute from day one. | `/gen-contributor-guide` | `05-contributor-guide.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
