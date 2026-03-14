# Claude Code Skills Pack: Project Status Reporting — 5 Skills for Stakeholder Communication and Risk Visibility

> For project managers and engineering leads, this pack generates weekly status reports, RAG status summaries, risk and blocker escalations, milestone progress narratives, and executive briefing snapshots so they can keep every stakeholder aligned without spending hours writing updates

---

## What's in This Pack

Generates stakeholder-ready status reports, risk escalations, and executive briefings for project managers and engineering leads so they can keep every audience aligned without spending hours writing updates.

This pack includes **5 ready-to-use Claude Code skills**:

**1. `/weekly-status`** — `01-weekly-status-report.md`
   Compiles accomplishments, in-progress work, and next-week plans from raw notes or ticket data into a formatted weekly status report ready to send to stakeholders.

**2. `/rag-status`** — `02-rag-status-summary.md`
   Evaluates project health across scope, schedule, budget, and team dimensions and produces a Red-Amber-Green status summary with concise justifications for each rating.

**3. `/escalate-risks`** — `03-risk-blocker-escalation.md`
   Transforms a list of risks or blockers into a structured escalation memo with impact assessment, urgency level, owner assignments, and recommended mitigations.

**4. `/milestone-narrative`** — `04-milestone-progress-narrative.md`
   Converts milestone completion data and delivery dates into a clear prose narrative showing progress against plan, variance explanations, and revised forecasts.

**5. `/exec-briefing`** — `05-executive-briefing-snapshot.md`
   Distills full project status details into a concise executive briefing snapshot — three to five bullet points covering overall health, key wins, top risks, and immediate asks.

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
| Compiles accomplishments, in-progress work, and next-week plans from raw notes or ticket data into a formatted weekly status report ready to send to stakeholders. | `/weekly-status` | `01-weekly-status-report.md` |
| Evaluates project health across scope, schedule, budget, and team dimensions and produces a Red-Amber-Green status summary with concise justifications for each rating. | `/rag-status` | `02-rag-status-summary.md` |
| Transforms a list of risks or blockers into a structured escalation memo with impact assessment, urgency level, owner assignments, and recommended mitigations. | `/escalate-risks` | `03-risk-blocker-escalation.md` |
| Converts milestone completion data and delivery dates into a clear prose narrative showing progress against plan, variance explanations, and revised forecasts. | `/milestone-narrative` | `04-milestone-progress-narrative.md` |
| Distills full project status details into a concise executive briefing snapshot — three to five bullet points covering overall health, key wins, top risks, and immediate asks. | `/exec-briefing` | `05-executive-briefing-snapshot.md` |

---

## Tips

- Each skill works independently — use only the ones you need
- Skills can be combined in the same session (e.g. scaffold a component, then review it)
- Customize any `.md` file to match your project's conventions
- Add the `skills/` folder to git to share the pack across your team
