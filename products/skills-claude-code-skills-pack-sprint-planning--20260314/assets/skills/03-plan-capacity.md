---
name: plan-capacity
trigger: /plan-capacity
description: >
  Calculates available team capacity for the upcoming sprint by factoring in
  headcount, PTO, ceremonies, and historical velocity. Outputs a per-member
  story point budget and a total sprint capacity recommendation. Use this skill
  before every sprint planning session to ground your commitments in real data
  rather than guesswork.
tags: [agile, sprint-planning, capacity, scrum, estimation]
author: Sprint Planning Skills Pack
version: 1.0.0
---

# Skill: plan-capacity

## Purpose

This skill helps agile team leads and scrum masters quickly calculate how many story points a team can realistically commit to in an upcoming sprint. It accounts for team size, individual availability, recurring ceremony overhead, and the team's historical velocity to produce a defensible, data-driven capacity budget.

Use this skill at the start of sprint planning or during backlog refinement when you need to set realistic expectations for how much work the team can absorb.

---

## When to Use

- Before sprint planning to establish a story point ceiling
- When team composition has changed (new members, departures, part-time contributors)
- When PTO or holidays will affect availability in the coming sprint
- When the team's historical velocity has shifted and needs recalibration
- When stakeholders are pushing for commitments beyond realistic capacity

---

## How Claude Should Execute This Skill

Follow these steps in order. Do not skip steps or combine them unless the user has already provided the required inputs.

### Step 1 — Gather Required Inputs

If the user has not provided inputs in the slash command invocation, prompt for the following. Ask for all missing items in a single message, not one at a time.

**Required inputs:**
1. **Sprint duration** — How many working days is the sprint? (e.g., 10 days for a 2-week sprint)
2. **Team members** — List each member by name or role, along with their capacity percentage (100% = full-time, 50% = half-time, etc.)
3. **PTO and absences** — For each member, how many days will they be absent during this sprint?
4. **Historical velocity** — What has the team's average story point velocity been over the last 3 sprints? If unknown, ask for a rough estimate or note that a default assumption will be used.

**Optional inputs (use defaults if not provided):**
- **Ceremony overhead** — How many hours per sprint are spent in ceremonies (standups, planning, retro, review, refinement)? Default: 8 hours per sprint for a 2-week sprint.
- **Focus factor** — What percentage of available time is spent on actual feature work (excluding interruptions, code reviews, slack messages)? Default: 70%.
- **Sprint goal context** — Any brief description of what the sprint is targeting (used for narrative framing in the output only).

### Step 2 — Calculate Individual Capacity

For each team member, apply the following formula:

1. **Available days** = (Sprint working days − PTO days) × Capacity percentage
2. **Available hours** = Available days × 8 hours
3. **Ceremony hours** = Total ceremony hours × Capacity percentage
4. **Net productive hours** = (Available hours − Ceremony hours) × Focus factor
5. **Individual story point budget** = Net productive hours ÷ Hours per story point

To derive **hours per story point**, use historical velocity:

- Hours per story point = (Total team productive hours in an average past sprint) ÷ Historical average velocity

If historical velocity is unknown, use a conservative default of **4 hours per story point** and flag this assumption prominently in the output.

### Step 3 — Calculate Total Sprint Capacity

1. Sum all individual story point budgets to get the **raw team capacity**.
2. Apply a **10% buffer reduction** to account for unplanned work and emergencies: Recommended sprint capacity = Raw team capacity × 0.90.
3. Round the final number down to the nearest whole number.

### Step 4 — Validate Against Historical Velocity

Compare the recommended sprint capacity to the team's 3-sprint average velocity.

- If the recommended capacity is **within 15%** of historical velocity: signal green — capacity looks healthy and consistent.
- If it is **more than 15% below** historical velocity: flag that the team may be under-resourced this sprint and recommend reducing commitments accordingly.
- If it is **more than 15% above** historical velocity: flag a risk of over-commitment and recommend the team revisit their focus factor or PTO data.

### Step 5 — Format and Deliver Output

Produce a clean, structured output using the format defined in the Output Format section below. Include all calculations transparently so the team can audit or adjust assumptions.

---

## Output Format

Deliver output in the following structure. Use Markdown formatting so it renders well in Claude Code's interface.

---

## Sprint Capacity Plan

**Sprint:** [Sprint name or number if provided, otherwise "Upcoming Sprint"]
**Duration:** [X working days]
**Planning date:** [Today's date]

---

### Team Availability

| Team Member | Role / Notes | Sprint Days | PTO Days | Available Days | Capacity % | Effective Days |
|---|---|---|---|---|---|---|
| [Name] | [Role] | [X] | [X] | [X] | [X%] | [X] |
| ... | | | | | | |
| **Total** | | | | | | **[X]** |

---

### Capacity Assumptions

- **Sprint working days:** [X]
- **Ceremony overhead:** [X hours per sprint]
- **Focus factor:** [X%]
- **Hours per story point:** [X hours] _(derived from historical velocity / assumed default)_
- **Historical average velocity:** [X points] _(last 3 sprints: [X], [X], [X] — or "not provided")_

---

### Individual Story Point Budgets

| Team Member | Net Productive Hours | Story Points Available |
|---|---|---|
| [Name] | [X hrs] | [X pts] |
| ... | | |
| **Raw Team Total** | **[X hrs]** | **[X pts]** |

---

### Recommended Sprint Capacity

> **[X story points]**
> _(Raw capacity of [X] pts × 0.90 buffer = [X] pts, rounded down)_

---

### Velocity Check

- **Historical average velocity:** [X pts]
- **Recommended capacity:** [X pts]
- **Variance:** [+/- X%]
- **Signal:** 🟢 Healthy / 🟡 Under-resourced / 🔴 Risk of over-commitment

[One sentence of plain-language interpretation of the signal.]

---

### Recommendations

[2–4 bullet points with specific, actionable recommendations based on the calculation results. Examples: adjust PTO coverage, revisit focus factor, defer a particular backlog theme given reduced capacity, flag a capacity risk to stakeholders before planning begins.]

---

## Constraints and Quality Rules

- **Always show your math.** Every number in the output must be traceable to an input or a stated assumption. Do not produce a final number without showing intermediate calculations.
- **Flag all assumptions explicitly.** If the user did not provide historical velocity, ceremony hours, or focus factor, state the default being used and mark it clearly with _(assumed default)_.
- **Never round up.** When rounding story point budgets, always round down. It is always safer to under-commit than over-commit.
- **Do not invent team member names.** Use only the names or roles the user provides. If unnamed, label them Member A, Member B, etc.
- **Do not recommend specific backlog items.** This skill is for capacity calculation only. Do not suggest which stories to include in the sprint — that is the team's decision.
- **Keep recommendations specific.** Vague advice like "plan better" is not acceptable. Recommendations must reference specific numbers or conditions from the current calculation.
- **One output block only.** Do not produce multiple versions or ask clarifying questions after the output is delivered. Deliver one clean result. If assumptions need revisiting, the user can re-invoke the skill.
- **Preserve team data privacy.** Do not store, reference, or infer personal information about team members beyond what is needed for the calculation.

---

## Usage Examples

### Example 1 — Full inputs provided inline

/plan-capacity sprint=14 team="Alice 100%, Bob 100%, Carmen 80%, Dev 50%" pto="Bob 2 days, Carmen 1 day" velocity="42, 38, 45" ceremonies=10 focus=70

Claude will parse all inputs directly from the invocation, skip the input-gathering step, run calculations, and deliver the full capacity plan immediately.

---

### Example 2 — Minimal invocation, Claude prompts for details

/plan-capacity

Claude will respond with a single prompt asking for sprint duration, team members and capacity percentages, PTO, and historical velocity. Once the user replies with that information, Claude runs the full calculation and delivers the output.

---

### Example 3 — Partial inputs with a sprint context note

/plan-capacity sprint=10 team="Jordan 100%, Sam 100%, Riley 60%" pto="Jordan 1 day" velocity=unknown goal="Finish payment gateway integration"

Claude will use the provided inputs, apply the default hours-per-story-point assumption since velocity is unknown, flag that assumption clearly, and include the sprint goal as narrative context in the output header. The velocity check section will note that historical data was not available and recommend the team track this sprint's actuals for future calibration.