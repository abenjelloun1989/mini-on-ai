# Claude Code Skills Pack: User Story Writing — 5 Skills for Turning Requirements Into Actionable Tickets

> For product managers and business analysts, this pack converts raw feature requests into well-structured user stories, acceptance criteria, edge case lists, definition-of-done checklists, and Jira-ready ticket descriptions so they can eliminate ambiguity before development starts

---

## What's in This Pack

Converts raw feature requests into fully structured, development-ready artifacts including user stories, acceptance criteria, edge cases, definition-of-done checklists, and Jira tickets for product managers and business analysts.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/draft-story`** — `01-draft-user-story.md`
   Transforms a raw feature request or brief description into a properly formatted user story using the As a / I want / So that structure with clear role, goal, and business value.

**2. `/gen-criteria`** — `02-generate-acceptance-criteria.md`
   Generates a comprehensive set of Given/When/Then acceptance criteria from a user story, covering the primary success scenarios and key functional requirements.

**3. `/find-edge-cases`** — `03-identify-edge-cases.md`
   Analyzes a user story and its acceptance criteria to surface a prioritized list of edge cases, boundary conditions, and failure scenarios that development and QA must account for.

**4. `/build-dod`** — `04-build-definition-of-done.md`
   Produces a tailored definition-of-done checklist for a user story covering coding, testing, documentation, accessibility, and stakeholder sign-off requirements.

**5. `/format-jira`** — `05-format-jira-ticket.md`
   Assembles all story components — user story, acceptance criteria, edge cases, and definition of done — into a fully structured, copy-paste-ready Jira ticket description with labeled sections and story point guidance.

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
| Transforms a raw feature request or brief description into a properly formatted user story using the As a / I want / So that structure with clear role, goal, and business value. | `/draft-story` | `01-draft-user-story.md` |
| Generates a comprehensive set of Given/When/Then acceptance criteria from a user story, covering the primary success scenarios and key functional requirements. | `/gen-criteria` | `02-generate-acceptance-criteria.md` |
| Analyzes a user story and its acceptance criteria to surface a prioritized list of edge cases, boundary conditions, and failure scenarios that development and QA must account for. | `/find-edge-cases` | `03-identify-edge-cases.md` |
| Produces a tailored definition-of-done checklist for a user story covering coding, testing, documentation, accessibility, and stakeholder sign-off requirements. | `/build-dod` | `04-build-definition-of-done.md` |
| Assembles all story components — user story, acceptance criteria, edge cases, and definition of done — into a fully structured, copy-paste-ready Jira ticket description with labeled sections and story point guidance. | `/format-jira` | `05-format-jira-ticket.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
