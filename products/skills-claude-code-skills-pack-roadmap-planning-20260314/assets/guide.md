# Claude Code Skills Pack: Roadmap Planning — 5 Skills for Quarterly Planning and Priority Alignment

> For product managers and heads of engineering, this pack builds opportunity sizing summaries, prioritization scoring matrices, now-next-later roadmap narratives, dependency mapping notes, and board-level roadmap presentations so they can move from chaotic feature lists to a defensible, stakeholder-approved plan

---

## What's in This Pack

Transforms chaotic feature lists into defensible, stakeholder-approved quarterly roadmaps by generating opportunity sizing summaries, prioritization matrices, roadmap narratives, dependency maps, and board-ready presentations for product managers and engineering leaders.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/size-opportunity`** — `01-opportunity-sizing.md`
   Synthesizes raw feature requests, customer data, and market signals into structured opportunity sizing summaries with estimated reach, revenue impact, and strategic fit scores.

**2. `/score-priorities`** — `02-prioritization-matrix.md`
   Builds a weighted scoring matrix that ranks features and initiatives against configurable criteria such as effort, impact, confidence, and strategic alignment to produce a defensible priority stack.

**3. `/draft-roadmap`** — `03-now-next-later-narrative.md`
   Converts a prioritized feature list into a cohesive now-next-later roadmap narrative that explains the sequencing rationale in plain language suitable for engineering teams and business stakeholders.

**4. `/map-dependencies`** — `04-dependency-mapping.md`
   Analyzes a set of planned initiatives and generates structured dependency mapping notes that surface blockers, sequencing constraints, and cross-team handoffs before they derail execution.

**5. `/build-board-deck`** — `05-board-roadmap-presentation.md`
   Assembles a concise, board-level roadmap presentation from sizing summaries, priority scores, and the roadmap narrative, framing quarterly bets in terms of business outcomes and risk trade-offs.

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
| Synthesizes raw feature requests, customer data, and market signals into structured opportunity sizing summaries with estimated reach, revenue impact, and strategic fit scores. | `/size-opportunity` | `01-opportunity-sizing.md` |
| Builds a weighted scoring matrix that ranks features and initiatives against configurable criteria such as effort, impact, confidence, and strategic alignment to produce a defensible priority stack. | `/score-priorities` | `02-prioritization-matrix.md` |
| Converts a prioritized feature list into a cohesive now-next-later roadmap narrative that explains the sequencing rationale in plain language suitable for engineering teams and business stakeholders. | `/draft-roadmap` | `03-now-next-later-narrative.md` |
| Analyzes a set of planned initiatives and generates structured dependency mapping notes that surface blockers, sequencing constraints, and cross-team handoffs before they derail execution. | `/map-dependencies` | `04-dependency-mapping.md` |
| Assembles a concise, board-level roadmap presentation from sizing summaries, priority scores, and the roadmap narrative, framing quarterly bets in terms of business outcomes and risk trade-offs. | `/build-board-deck` | `05-board-roadmap-presentation.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
