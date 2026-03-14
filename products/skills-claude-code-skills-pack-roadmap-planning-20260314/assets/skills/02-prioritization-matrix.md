---
name: prioritization-matrix
trigger: /score-priorities
description: Builds a weighted scoring matrix that ranks features and initiatives against configurable criteria such as effort, impact, confidence, and strategic alignment to produce a defensible priority stack. Use this skill whenever you need to move from a raw feature list to a ranked, evidence-backed priority order that can withstand stakeholder scrutiny.
version: 1.0.0
pack: Claude Code Skills Pack — Roadmap Planning
author: Claude Code
---

# Skill: Prioritization Matrix

## Purpose

Transform an unordered or loosely ordered list of features, initiatives, or bets into a weighted scoring matrix with a final ranked stack. The output must be immediately shareable with engineering leads, product leadership, and business stakeholders who need to see the reasoning behind every ranking decision.

---

## When to Use This Skill

- You have a backlog, feature list, or initiative dump that needs ranked order
- Stakeholders are debating priorities without a shared scoring framework
- You are preparing for quarterly planning and need a defensible stack before the kick-off meeting
- A previous priority list exists but needs to be re-scored against updated strategic criteria
- You want to surface hidden conflicts between high-effort, high-impact items and quick wins

---

## Inputs Claude Should Gather

Before building the matrix, Claude must collect or infer the following. If any required input is missing, ask for it before proceeding.

**Required**
1. **Feature or initiative list** — at minimum, names; descriptions are strongly preferred
2. **Scoring criteria** — accept the defaults below if the user does not specify custom criteria

**Optional but recommended**
3. **Criterion weights** — how much each criterion matters relative to the others (defaults provided)
4. **Scoring scale** — 1–5 or 1–10 (default: 1–5)
5. **Strategic context** — company stage, OKRs, north-star metric, or any stated strategic theme for the quarter
6. **Constraints** — team size, budget caps, hard deadlines, dependencies already known

If the user provides a file path, document excerpt, or pasted list, extract items from it directly. Do not ask for information that is already present in the provided content.

---

## Default Scoring Criteria and Weights

Use these defaults unless the user explicitly overrides them. Always display the active criteria and weights at the top of the matrix so readers know the scoring basis.

| Criterion | Weight | What to Score High |
|---|---|---|
| Strategic Alignment | 30% | Directly advances stated OKRs or north-star metric |
| Customer Impact | 25% | Meaningfully improves outcomes for target users |
| Effort (inverted) | 20% | Low effort scores high; high effort scores low |
| Revenue or Growth Potential | 15% | Near-term measurable business value |
| Confidence | 10% | Strength of evidence behind impact assumptions |

Weights must always sum to 100%. If the user provides custom weights that do not sum to 100%, flag the discrepancy and ask for confirmation before adjusting proportionally.

---

## Step-by-Step Execution Instructions

Follow these steps in order. Do not skip steps.

### Step 1 — Confirm Inputs

Restate the list of items to be scored and the active criteria and weights. If anything looks ambiguous or incomplete, ask one consolidated clarifying question rather than multiple sequential questions. Proceed only after the user confirms or provides corrections.

### Step 2 — Score Each Item

For each item in the list, assign a score from 1 to 5 (or the user-specified scale) for every criterion. Apply the following discipline:

- **Be explicit about assumptions.** If you lack information to score confidently, state the assumption you are making and flag the cell with an asterisk (*).
- **Calibrate relatively.** Scores should reflect the items relative to each other, not against an abstract absolute standard. If all items score 5 on a criterion, re-examine whether differentiation is possible.
- **Effort is always inverted.** A high-effort item receives a low raw score (e.g., 1 or 2) so that, after weighting, low-effort items are rewarded.
- **Do not round weighted scores prematurely.** Carry two decimal places through the calculation; round only in the final display.

### Step 3 — Calculate Weighted Scores

For each item:

1. Multiply each raw criterion score by its weight (expressed as a decimal)
2. Sum all weighted criterion scores to produce a **Total Weighted Score**
3. Round the Total Weighted Score to two decimal places for display

Example calculation for one item:
- Strategic Alignment: 4 × 0.30 = 1.20
- Customer Impact: 5 × 0.25 = 1.25
- Effort (inverted): 3 × 0.20 = 0.60
- Revenue Potential: 4 × 0.15 = 0.60
- Confidence: 3 × 0.10 = 0.30
- **Total: 3.95**

### Step 4 — Rank and Tier

- Sort all items by Total Weighted Score, descending
- Assign a **Rank** (1 = highest priority)
- Assign a **Tier** label based on score bands:

| Score Band (1–5 scale) | Tier Label |
|---|---|
| 4.00 – 5.00 | Tier 1 — Do Now |
| 3.00 – 3.99 | Tier 2 — Do Next |
| 2.00 – 2.99 | Tier 3 — Consider Later |
| Below 2.00 | Tier 4 — Deprioritize |

Adjust tier thresholds proportionally if a 1–10 scale is used.

### Step 5 — Build the Matrix Output

Produce a fully formatted Markdown table with the following columns in this order:

Rank | Item | Strategic Alignment | Customer Impact | Effort (inv.) | Revenue Potential | Confidence | Total Score | Tier

Below the table, include a **Scoring Notes** section that lists every asterisked assumption in numbered format so stakeholders know where the analysis is soft.

### Step 6 — Write the Priority Narrative

After the matrix, write a short narrative of 150–250 words that:

1. States the top three items and why they scored highest given the stated strategy
2. Calls out any surprising results (items ranked lower than intuition might suggest, or items that scored higher due to strong confidence or low effort)
3. Flags any items within 0.10 points of each other as **effectively tied** and recommends a tiebreaker discussion
4. Notes any items with two or more asterisked assumptions that should be re-scored once better data is available

### Step 7 — Offer Next Steps

End the output with a short **Next Steps** section listing three optional follow-on actions the user can take, such as:
- Running `/map-dependencies` to surface sequencing constraints
- Sharing the matrix with stakeholders for async score challenges
- Scheduling a 30-minute calibration session to align on criterion weights

---

## Output Format Requirements

- Deliver the full output in a single Markdown response
- Use a top-level H1 heading: `# Priority Scoring Matrix`
- Use H2 headings for each major section: `## Active Criteria & Weights`, `## Scored Matrix`, `## Scoring Notes`, `## Priority Narrative`, `## Next Steps`
- Tables must be valid GitHub-flavored Markdown
- Do not use HTML tags
- Do not produce a summary before the matrix; place the matrix first after the criteria block
- Maximum total response length: 1,200 words excluding the table itself; the table has no length cap
- If the item list exceeds 20 items, note that large matrices reduce readability and offer to split into themed sub-matrices

---

## Quality Rules and Constraints

- **Never fabricate scores silently.** Any score based on an assumption must be flagged with an asterisk and explained in Scoring Notes.
- **Never change criterion weights without user confirmation.** If weights are adjusted for any reason, state the change explicitly.
- **Maintain scoring discipline.** Avoid clustering all items in the 3–4 range. If the spread is narrow, note it and offer to re-examine with adjusted criterion definitions.
- **Do not editorialize priority decisions.** The matrix ranks; the human decides. Frame all narrative language as analysis, not directives.
- **Handle ties transparently.** Never break ties arbitrarily. Surface them and recommend a human decision point.
- **Respect stated constraints.** If a hard deadline or budget cap is provided, add a constraint flag (⚠) next to any item that cannot meet it, regardless of its score.

---

## Usage Examples

### Example 1 — Basic invocation with a pasted list

/score-priorities

Here are our Q3 candidates:
- Unified inbox for customer messages
- SSO / SAML support
- Mobile push notifications
- Bulk CSV export
- In-app NPS survey
- API rate-limit dashboard for developers

Our north-star is activating enterprise accounts. We are a 6-person eng team.

---

### Example 2 — Custom criteria and weights

/score-priorities

Items: Dark mode, Offline mode, Keyboard shortcuts, Accessibility audit remediation, Onboarding checklist redesign

Custom criteria:
- Engineering feasibility: 35%
- User satisfaction impact: 35%
- Brand differentiation: 20%
- Regulatory necessity: 10%

Scale: 1–10

---

### Example 3 — Re-scoring an existing list with updated strategy

/score-priorities

We ran this scoring last quarter with growth as our top criterion. We just shifted strategy to retention. Please re-score the attached initiative list against the default criteria but swap Revenue Potential weight to 10% and increase Customer Impact to 30%. Keep everything else the same.

[attached: q2-initiatives.md]

---

## Notes for Skill Maintainers

- Tier label copy (Do Now / Do Next / Consider Later / Deprioritize) is intentionally non-prescriptive to avoid overstepping the human decision-maker
- The default weight set was chosen to balance strategic and customer-centric thinking; adjust defaults in future versions based on pack user feedback
- This skill pairs naturally with `/map-dependencies` (dependency mapping) and `/build-roadmap-narrative` (now-next-later narrative) from the same pack