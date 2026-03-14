---
name: Milestone Progress Narrative
trigger: /milestone-narrative
description: >
  Converts milestone completion data and delivery dates into a clear prose
  narrative showing progress against plan, variance explanations, and revised
  forecasts. Use this skill when you need to communicate milestone status to
  stakeholders in a readable, context-rich format rather than raw data tables.
  Ideal for sprint reviews, monthly progress reports, steering committee updates,
  and project health summaries.
tags: [project-management, reporting, milestones, forecasting, stakeholder-communication]
---

# Milestone Progress Narrative

## Purpose

Transform raw milestone data — planned dates, actual completion dates, percentage
progress, and contextual notes — into a polished prose narrative that tells the
story of where the project stands, why any variances occurred, and what the
revised outlook looks like. The output should be immediately shareable with
stakeholders who need clarity, not spreadsheets.

---

## When to Use This Skill

- Weekly or monthly project status reporting cycles
- After a sprint or phase completes and delivery dates need to be reconciled
- When a milestone has slipped and leadership needs a clear explanation
- Before a steering committee or executive review where narrative context matters
- When consolidating multiple workstream milestones into a single project story

---

## How to Invoke

/milestone-narrative [milestone data or file reference] [optional: reporting period] [optional: audience]

**Examples:**

/milestone-narrative "M1: Design Complete — planned Apr 1, delivered Apr 3. M2: Backend API — planned Apr 15, currently 60% complete. M3: QA Sign-off — planned Apr 28, not started." reporting-period="April" audience="engineering leadership"

/milestone-narrative @milestones.csv reporting-period="Q2 Sprint 3" audience="executive sponsors"

/milestone-narrative "Phase 1 done on time. Phase 2 delayed 2 weeks due to third-party API integration issues. Phase 3 revised forecast is June 14 instead of May 31." audience="client stakeholders"

---

## Execution Instructions

Follow these steps precisely when this skill is triggered:

### Step 1 — Parse and Validate Input

1. Extract all milestone entries from the provided input, file, or inline text.
2. For each milestone, identify:
   - **Milestone name or label**
   - **Planned completion date**
   - **Actual completion date** (if delivered) or **current percent complete** (if in progress)
   - **Status** — derive as: Completed, On Track, At Risk, or Delayed
   - **Variance** — calculate days ahead or behind plan (positive = ahead, negative = behind)
   - **Any reason or context** provided for variance
3. Note the **reporting period** if supplied; default to "current period" if not given.
4. Note the **target audience** if supplied; default to "project stakeholders."
5. If critical data is missing (e.g., no dates at all, no milestone names), ask the
   user one focused clarifying question before proceeding. Do not guess at dates.

### Step 2 — Classify Overall Project Health

Based on the milestone data, assign an overall health indicator:

- **Green** — All milestones on track or completed; no delays exceeding 3 days
- **Amber** — One or more milestones delayed or at risk; overall delivery date
  not yet threatened
- **Red** — Critical path milestone delayed; overall delivery date at risk or
  already missed

Use this classification to open the narrative and set the right tone throughout.

### Step 3 — Structure the Narrative

Produce the narrative in the following sections, written in clear professional prose:

#### 3a. Executive Summary (2–4 sentences)
State overall health, the number of milestones in scope, how many are complete,
and the headline message a busy stakeholder needs to know immediately.
Reference the overall health indicator (Green / Amber / Red) by name.

#### 3b. Milestone-by-Milestone Progress
For each milestone, write 2–5 sentences covering:
- What the milestone is and why it matters
- Whether it was delivered on time, early, late, or is still in progress
- The specific variance in days (e.g., "delivered 2 days ahead of plan" or
  "currently 5 days behind the April 15 target")
- The reason for any variance, using provided context or flagging that a reason
  was not supplied
- Any dependencies or downstream effects the variance creates

Group milestones logically: Completed first, then In Progress, then Not Started.
Use a bold milestone label as a lead-in for each entry.

#### 3c. Variance Analysis
Write a short paragraph (3–6 sentences) synthesising the pattern of variances
across all milestones. Identify systemic causes if evident (e.g., resource
constraints, third-party dependencies, scope changes). Avoid blame language;
keep analysis factual and forward-looking.

#### 3d. Revised Forecast
State the current projected completion date for the overall project or phase,
compared to the original plan. If specific milestone forecasts were provided,
include them. If no revised dates were supplied but delays exist, note that a
revised forecast is pending and flag it as an action item.

#### 3e. Recommended Actions (optional, include if delays or risks exist)
List 2–4 concrete, specific recommended actions to address variances or risks.
Write each as a single sentence starting with an action verb.
Omit this section entirely if all milestones are green and on track.

### Step 4 — Calibrate Tone for Audience

Adjust language complexity and detail level based on the stated audience:

- **Executive / board / client** — Lead with impact and outcome, minimal
  technical detail, confident and decisive tone, shorter sentences
- **Engineering leadership / project management** — Include technical specifics,
  dependency detail, and process-level variance causes
- **General stakeholders** — Balanced clarity, avoid jargon, explain acronyms
  on first use, moderate detail level

If no audience is specified, default to general stakeholder tone.

### Step 5 — Format the Output

Deliver the complete narrative as clean Markdown using the structure below.
Do not include raw data tables unless the user explicitly requests them.
All dates must be written in full (e.g., April 15, 2025 — not 04/15).

---

## Output Format

# Milestone Progress Narrative — [Project or Phase Name] | [Reporting Period]

**Overall Health:** [Green / Amber / Red]
**Report Date:** [Today's date]
**Milestones in Scope:** [N] | **Completed:** [N] | **In Progress:** [N] | **Not Started:** [N]

---

## Executive Summary

[2–4 sentence summary paragraph]

---

## Milestone Progress

**[Milestone Name]**
[2–5 sentence entry]

**[Milestone Name]**
[2–5 sentence entry]

*(repeat for all milestones)*

---

## Variance Analysis

[3–6 sentence paragraph]

---

## Revised Forecast

[Forecast paragraph or flag that revised dates are pending]

---

## Recommended Actions

- [Action 1]
- [Action 2]
- [Action 3]

*(omit section if no actions needed)*

---

## Constraints and Quality Rules

1. **Never fabricate dates or percentages.** If data is missing or ambiguous,
   flag the gap explicitly rather than estimating silently.
2. **Variance must always be quantified** in days where dates are available.
   "Slightly delayed" is not acceptable — "delayed by 6 days" is.
3. **No blame language.** Write "the integration dependency created a 4-day
   delay" not "the vendor failed to deliver."
4. **Prose only in narrative sections.** Do not convert the narrative sections
   into bullet lists. Tables are only permitted if the user explicitly requests
   a data appendix alongside the narrative.
5. **Health classification must be consistent** throughout — if you open with
   Amber, every section must reflect that Amber context.
6. **Tense discipline:** Completed milestones use past tense. In-progress
   milestones use present tense. Forecasts use future tense.
7. **Recommended Actions section is conditional** — include it only when the
   health status is Amber or Red, or when the user's data explicitly flags risks.
8. **Length target:** Executive Summary ≤ 100 words. Each milestone entry
   ≤ 80 words. Total narrative should be readable in under 3 minutes.
9. **If multiple projects or phases are provided**, produce one narrative per
   project/phase unless the user asks for a consolidated view.
10. **Revised Forecast must always appear**, even if it is simply a confirmation
    that the original delivery date remains unchanged.