# Claude Code Skills Pack: Sprint Planning — 5 Skills for Agile Ceremony Preparation and Execution

> For agile team leads and scrum masters, this pack automates backlog grooming, sprint goal writing, capacity planning, story point estimation, and sprint review summaries so they can run tighter ceremonies in half the prep time

---

## What's in This Pack

Automates backlog grooming, sprint goal writing, capacity planning, story point estimation, and sprint review summaries so agile team leads and scrum masters can run tighter ceremonies in half the prep time.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/groom-backlog`** — `01-groom-backlog.md`
   Analyzes raw backlog items and rewrites them as properly structured user stories with acceptance criteria, flags duplicates, and surfaces missing details that need product owner clarification.

**2. `/write-sprint-goal`** — `02-write-sprint-goal.md`
   Synthesizes the selected sprint stories into a concise, outcome-focused sprint goal statement aligned to business objectives, along with a one-paragraph rationale for stakeholder communication.

**3. `/plan-capacity`** — `03-plan-capacity.md`
   Calculates available team capacity for the upcoming sprint by factoring in headcount, PTO, ceremonies, and historical velocity, then outputs a recommended story point budget per team member.

**4. `/estimate-stories`** — `04-estimate-stories.md`
   Generates relative story point estimates for a list of user stories using complexity, effort, and uncertainty heuristics, with a brief justification for each estimate to anchor team discussion.

**5. `/summarize-sprint-review`** — `05-summarize-sprint-review.md`
   Produces a structured sprint review summary from completed tickets and notes, covering what was delivered, what was deferred, key decisions made, and recommended carry-over actions for the next sprint.

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
| Analyzes raw backlog items and rewrites them as properly structured user stories with acceptance criteria, flags duplicates, and surfaces missing details that need product owner clarification. | `/groom-backlog` | `01-groom-backlog.md` |
| Synthesizes the selected sprint stories into a concise, outcome-focused sprint goal statement aligned to business objectives, along with a one-paragraph rationale for stakeholder communication. | `/write-sprint-goal` | `02-write-sprint-goal.md` |
| Calculates available team capacity for the upcoming sprint by factoring in headcount, PTO, ceremonies, and historical velocity, then outputs a recommended story point budget per team member. | `/plan-capacity` | `03-plan-capacity.md` |
| Generates relative story point estimates for a list of user stories using complexity, effort, and uncertainty heuristics, with a brief justification for each estimate to anchor team discussion. | `/estimate-stories` | `04-estimate-stories.md` |
| Produces a structured sprint review summary from completed tickets and notes, covering what was delivered, what was deferred, key decisions made, and recommended carry-over actions for the next sprint. | `/summarize-sprint-review` | `05-summarize-sprint-review.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
