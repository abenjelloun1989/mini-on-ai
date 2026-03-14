---
name: RAG Status Summary
trigger: /rag-status
description: Evaluates project health across scope, schedule, budget, and team dimensions and produces a Red-Amber-Green status summary with concise justifications for each rating. Use this skill when you need a quick, scannable health check for stakeholders that surfaces risk areas without requiring them to read lengthy narrative reports.
tags: [project-management, status-reporting, risk-visibility, stakeholder-communication]
---

# RAG Status Summary Skill

## Purpose

Generate a structured Red-Amber-Green (RAG) status summary that gives stakeholders an at-a-glance view of project health. Each dimension receives a clear color rating with a one-to-two sentence justification so decision-makers can immediately identify where attention is needed.

---

## When to Use This Skill

- Weekly or bi-weekly stakeholder check-ins
- Steering committee or executive briefing preparation
- Escalation triage when something has gone wrong
- Portfolio reviews where multiple projects are compared side by side
- Any moment you need a fast, defensible health snapshot without writing a full narrative report

---

## How to Execute This Skill

Follow these steps in order every time `/rag-status` is invoked.

### Step 1 — Gather Context

Collect the information needed to make an informed rating. Look for any of the following that are available in the current session or referenced files:

- Project plan, timeline, or milestone tracker
- Sprint board, backlog, or task list
- Budget actuals versus forecast
- Recent meeting notes, stand-up summaries, or status threads
- Known risks, blockers, or issues log
- Team capacity notes (leave, attrition, hiring gaps)
- Scope change log or open change requests

If critical information for a dimension is missing, note it explicitly rather than guessing. A missing-data flag is more useful than a fabricated rating.

### Step 2 — Rate Each of the Four Dimensions

Apply RAG logic independently to each dimension using the criteria below.

**Scope**
- 🟢 GREEN — Requirements are stable; change requests are minor, agreed, and absorbed within existing capacity
- 🟡 AMBER — Notable scope changes are pending or recently approved; impact on schedule or budget is still being assessed
- 🔴 RED — Significant uncontrolled scope growth; requirements are contested, unclear, or expanding faster than the team can absorb

**Schedule**
- 🟢 GREEN — On track; milestones are being hit or minor delays have recovery plans in place
- 🟡 AMBER — One or more milestones are at risk; slippage is possible but corrective action is underway
- 🔴 RED — A key milestone has been missed or is certain to slip without immediate intervention; critical path is broken

**Budget**
- 🟢 GREEN — Spend is within approved tolerance (typically ±5–10%); forecast is aligned with plan
- 🟡 AMBER — Overspend or underspend is outside tolerance but below crisis threshold; variance has a known cause and a mitigation plan
- 🔴 RED — Significant budget overrun is confirmed or highly likely; funding gap exists with no approved resolution

**Team**
- 🟢 GREEN — Team is adequately staffed, morale is stable, no critical skill gaps or blockers
- 🟡 AMBER — Capacity pressure exists due to competing priorities, vacancies, or key-person risk; workarounds are in place
- 🔴 RED — Critical skill or headcount gap is actively impeding delivery; burnout, attrition, or conflict is escalating

### Step 3 — Write Justifications

For each dimension, write exactly one to two sentences that:
- State the specific evidence or data point driving the rating
- Name the risk or positive factor, not just the symptom
- Avoid vague language like "some challenges exist" — be concrete

### Step 4 — Derive the Overall RAG

Calculate the overall project RAG using this logic:
- Any RED dimension → Overall is RED
- No RED but one or more AMBER → Overall is AMBER
- All GREEN → Overall is GREEN

If the overall rating feels misleading given context (for example, two strong AMBER items that together represent serious risk), you may upgrade it to RED and explain the override reasoning in the overall summary line.

### Step 5 — Add an Immediate Actions Section

List up to three specific, owner-ready actions that would move the lowest-rated dimensions toward the next color up. Format as actionable imperatives, not vague suggestions.

### Step 6 — Render the Output

Use the exact format specified in the Output Format section below.

---

## Output Format

Render the summary using this structure. Do not omit any section. Do not add extra sections unless the user explicitly requests them.

---

## RAG Status Summary — [Project Name] — [Date or Sprint/Period]

### Overall Status: [🔴 RED / 🟡 AMBER / 🟢 GREEN]

[One sentence summarizing the overall project health and the primary driver of the overall rating.]

---

### Dimension Ratings

| Dimension | Status | Justification |
|-----------|--------|---------------|
| Scope | [🔴/🟡/🟢] [RED/AMBER/GREEN] | [One to two sentences of specific justification.] |
| Schedule | [🔴/🟡/🟢] [RED/AMBER/GREEN] | [One to two sentences of specific justification.] |
| Budget | [🔴/🟡/🟢] [RED/AMBER/GREEN] | [One to two sentences of specific justification.] |
| Team | [🔴/🟡/🟢] [RED/AMBER/GREEN] | [One to two sentences of specific justification.] |

---

### Immediate Actions Required

1. **[Owner or Role]** — [Specific action with clear outcome expected]
2. **[Owner or Role]** — [Specific action with clear outcome expected]
3. **[Owner or Role]** — [Specific action with clear outcome expected]

---

### Data Gaps (if any)

- [List any dimensions where data was insufficient to make a confident rating. If no gaps, omit this section entirely.]

---

## Constraints and Quality Rules

- **Never fabricate data.** If you do not have information for a dimension, say so explicitly using the Data Gaps section. A transparent unknown is always preferable to a confident guess.
- **Keep justifications tight.** One to two sentences maximum per dimension. Stakeholders reading this are time-poor. If you have more to say, save it for the weekly narrative report skill.
- **Use concrete evidence.** Reference specific milestones, dates, percentages, or named blockers wherever possible. Avoid abstract qualifiers like "somewhat" or "a bit."
- **Maintain color discipline.** Do not soften a RED to AMBER because the news is uncomfortable. Accurate ratings protect the project manager's credibility.
- **Immediate actions must be actionable.** Each action must have an implied or explicit owner and a clear outcome. "Monitor the situation" is not an acceptable action.
- **Format must be preserved.** Always render the full table and all sections. Do not collapse the output into paragraphs.
- **One summary per invocation.** If the user is asking about multiple projects, generate a separate RAG block for each project, clearly labeled.

---

## Usage Examples

### Example 1 — Invoked with project context already in session

/rag-status

Claude will read the current session context (open files, prior conversation, referenced documents) and produce a full RAG summary for the project being discussed.

---

### Example 2 — Invoked with explicit project description

/rag-status The mobile checkout redesign project is six weeks in. We've hit the first two milestones on time. A new payment provider requirement was added last week that wasn't in the original scope — the team estimates two weeks of extra work. Budget is tracking within 4% of forecast. One senior engineer is on parental leave until next month and we're feeling the capacity squeeze on the backend work.

Claude will parse the inline description and produce a RAG summary immediately, rating Scope AMBER (unabsorbed scope change), Schedule AMBER (risk from scope addition), Budget GREEN (within tolerance), and Team AMBER (temporary capacity gap), with the overall as AMBER.

---

### Example 3 — Invoked for a portfolio view

/rag-status Please generate RAG summaries for all three projects mentioned in the Q3 portfolio review document I uploaded.

Claude will produce three separate, clearly labeled RAG blocks — one per project — each following the full format. If data is sparse for any project dimension, it will flag the gap rather than estimate.