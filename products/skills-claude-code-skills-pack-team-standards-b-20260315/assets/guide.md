# Claude Code Skills Pack: Team Standards Bootstrapping — 5 Skills for Communicating Coding Conventions to New Hires

> For engineering leads and DevEx teams, this pack infers coding conventions from existing code, generates a CONTRIBUTING.md from scratch, documents naming patterns and folder structure rationale, produces a linting and tooling setup guide, and creates a decision log template capturing why key architectural choices were made so new team members understand not just what the rules are but why they exist.

---

## What's in This Pack

Helps engineering leads and DevEx teams codify and communicate coding conventions to new hires by inferring patterns from existing code, generating contribution guides, documenting structural rationale, and capturing architectural decision history.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/infer-conventions`** — `01-infer-coding-conventions.md`
   Scans the existing codebase to infer implicit coding conventions, naming patterns, and structural norms, then produces a structured conventions summary ready for documentation.

**2. `/gen-contributing`** — `02-generate-contributing-guide.md`
   Generates a comprehensive CONTRIBUTING.md from scratch covering branching strategy, commit message format, PR process, code review expectations, and onboarding steps tailored to the project.

**3. `/doc-structure`** — `03-document-folder-structure.md`
   Produces a human-readable folder structure map annotated with the rationale behind each directory's purpose, naming choice, and organizational principle so new hires understand the why, not just the what.

**4. `/gen-tooling-guide`** — `04-generate-tooling-setup-guide.md`
   Creates a step-by-step linting, formatting, and tooling setup guide derived from the project's config files, explaining each tool's role and how the rules enforce team standards.

**5. `/gen-decision-log`** — `05-create-decision-log-template.md`
   Generates an Architecture Decision Record (ADR) template and seeds it with a starter decision log capturing key architectural choices already present in the codebase, including context, options considered, and rationale.

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
| Scans the existing codebase to infer implicit coding conventions, naming patterns, and structural norms, then produces a structured conventions summary ready for documentation. | `/infer-conventions` | `01-infer-coding-conventions.md` |
| Generates a comprehensive CONTRIBUTING.md from scratch covering branching strategy, commit message format, PR process, code review expectations, and onboarding steps tailored to the project. | `/gen-contributing` | `02-generate-contributing-guide.md` |
| Produces a human-readable folder structure map annotated with the rationale behind each directory's purpose, naming choice, and organizational principle so new hires understand the why, not just the what. | `/doc-structure` | `03-document-folder-structure.md` |
| Creates a step-by-step linting, formatting, and tooling setup guide derived from the project's config files, explaining each tool's role and how the rules enforce team standards. | `/gen-tooling-guide` | `04-generate-tooling-setup-guide.md` |
| Generates an Architecture Decision Record (ADR) template and seeds it with a starter decision log capturing key architectural choices already present in the codebase, including context, options considered, and rationale. | `/gen-decision-log` | `05-create-decision-log-template.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
