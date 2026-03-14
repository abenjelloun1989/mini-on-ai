---
name: summarize-sprint-review
trigger: /summarize-sprint-review
description: >
  Produces a structured sprint review summary from completed tickets and notes.
  Use this skill immediately after a sprint review meeting or at sprint close to
  capture what was delivered, what was deferred, key decisions made, and
  recommended carry-over actions for the next sprint. Designed for agile team
  leads and scrum masters who need a clean, shareable artifact in minutes rather
  than hours.
tags: [agile, sprint, review, summary, scrum]
---

# Skill: summarize-sprint-review

## Purpose

Transform raw sprint data — completed tickets, deferred items, meeting notes,
and team commentary — into a polished, structured sprint review summary that
stakeholders can read immediately and the team can act on in the next sprint.

---

## When to Use This Skill

- Immediately after a sprint review ceremony to document outcomes
- At sprint close when async input is collected rather than a live meeting
- When a project manager or stakeholder requests a retrospective-ready summary
- When carrying work forward and needing clear justification for what moved

---

## Inputs Claude Should Expect

The user will provide one or more of the following. Prompt for anything missing
before proceeding:

1. **Sprint identifier** — Sprint number, name, or date range (e.g., "Sprint 24"
   or "Oct 7–18")
2. **Completed tickets** — A list, export, or paste of tickets marked Done,
   including ticket IDs, titles, and story points if available
3. **Deferred / incomplete tickets** — Items that were in scope but did not
   finish, with reason if known
4. **Sprint goal** — The original stated goal for this sprint
5. **Meeting notes or commentary** — Raw notes, bullet points, Slack threads,
   or verbal summary of what was discussed
6. **Team capacity context** — Optional: planned vs. actual capacity, absences,
   or blockers that affected delivery

If the user invokes the skill with no additional input, ask:

> "Please share the sprint details you'd like me to summarize. At minimum,
> provide the sprint identifier, a list of completed tickets, and any deferred
> items. Meeting notes and the original sprint goal are helpful but optional."

---

## Execution Steps

Follow these steps in order. Do not skip steps or combine outputs prematurely.

### Step 1 — Parse and Organize Raw Input

- Read all provided material carefully before writing anything
- Identify and categorize each ticket or item as: Completed, Deferred,
  Partially Complete, or Blocked
- Extract any decisions, risks, dependencies, or action items mentioned in notes
- Note any items that appear ambiguous and flag them for clarification or
  assumption

### Step 2 — Assess Sprint Goal Achievement

- Compare completed work against the stated sprint goal
- Determine one of three outcomes: Goal Met, Goal Partially Met, Goal Not Met
- Write a 1–2 sentence plain-language assessment explaining why

### Step 3 — Compute Delivery Metrics (if story points are available)

- Sum story points for Completed tickets
- Sum story points for Deferred and Incomplete tickets
- Calculate completion rate as a percentage
- If story points are absent, report ticket count instead and note the absence

### Step 4 — Draft the Summary Document

Produce the summary in the exact structure defined in the Output Format section
below. Do not invent sections or reorder them.

### Step 5 — Generate Carry-Over Recommendations

For each deferred or incomplete item, recommend one of the following actions and
provide a one-line rationale:

- **Carry over as-is** — Work is nearly complete or still high priority
- **Re-estimate before carrying over** — Scope was unclear; needs refinement
- **Deprioritize** — No longer aligned with current goals or blocked externally
- **Split** — Too large; a subset of value can ship sooner

### Step 6 — Review for Quality

Before outputting, verify:

- Every completed ticket appears in the summary
- Every deferred ticket has a carry-over recommendation
- No jargon is used that was not present in the source material
- The tone is neutral, factual, and professional
- The summary could be understood by a stakeholder who did not attend the review

---

## Output Format

Produce the summary using this exact structure:

---

# Sprint Review Summary — [Sprint Identifier]

**Date:** [Review date or sprint end date]
**Team / Project:** [If provided; otherwise omit]
**Sprint Goal:** [Restate the original goal verbatim or as provided]
**Goal Outcome:** [Met / Partially Met / Not Met] — [1–2 sentence explanation]

---

## Delivery at a Glance

| Metric | Value |
|---|---|
| Story Points Completed | [X pts] |
| Story Points Deferred | [X pts] |
| Completion Rate | [X%] |
| Tickets Completed | [X] |
| Tickets Deferred | [X] |

> If story points were not provided, replace point rows with ticket counts only
> and add a note: "Story points not available; counts reflect ticket volume."

---

## What Was Delivered

List each completed ticket as a bullet. Format:

- **[TICKET-ID]** [Ticket title] — [One sentence on the value delivered or what
  changed, written for a non-technical stakeholder if possible] *(X pts)*

Group by theme or epic if five or more tickets were completed and groupings are
apparent from the data. If no natural groupings exist, list chronologically or
by priority order.

---

## What Was Deferred

List each deferred or incomplete item as a bullet. Format:

- **[TICKET-ID]** [Ticket title] — [Reason for deferral if known; otherwise
  state "Reason not specified"] *(X pts)*

---

## Key Decisions Made

List decisions captured in meeting notes or implied by deferral/completion
patterns. Format as numbered items:

1. [Decision statement] — [Brief context or rationale if available]

If no decisions were documented, write:
> "No explicit decisions were recorded in the provided notes."

---

## Risks and Dependencies Surfaced

Bullet any risks, blockers, or cross-team dependencies mentioned or implied.
If none, write:
> "No risks or dependencies were flagged in this sprint review."

---

## Carry-Over Recommendations for Next Sprint

For each deferred item, provide a recommendation row:

| Ticket | Title | Recommendation | Rationale |
|---|---|---|---|
| [ID] | [Title] | Carry over as-is / Re-estimate / Deprioritize / Split | [One line] |

---

## Suggested Sprint Notes for Retrospective

Provide 2–4 brief observations the team may want to surface in the retrospective.
These are observations only — not prescriptive. Format as bullets:

- [Observation]

---

*Summary generated by /summarize-sprint-review — Claude Code Skills Pack: Sprint Planning*

---

## Constraints and Quality Rules

- **Accuracy over completeness:** If data is missing, say so explicitly rather
  than fabricating plausible details
- **No invented decisions:** Only record decisions that are stated or clearly
  implied in the provided notes
- **Neutral tone:** Do not editorialize or assign blame for deferred items
- **Ticket fidelity:** Do not paraphrase ticket titles in ways that change their
  meaning; use original titles
- **Stakeholder-readable:** Descriptions of delivered work should be
  understandable to someone outside the engineering team
- **Consistent units:** Do not mix story points and hours in the same metric row
- **No markdown in ticket titles:** If source titles contain special characters,
  preserve them but escape if they break table rendering
- **Flag ambiguity:** If a ticket's status is unclear from the input, list it
  under a short "Items Needing Clarification" note before the main summary

---

## Usage Examples

### Example 1 — Full data provided

/summarize-sprint-review

Sprint 24 (Oct 7–18). Goal: "Enable self-serve onboarding for SMB customers."

Completed: AUTH-112 (Login with SSO, 5pts), ONBRD-88 (Welcome email sequence,
3pts), ONBRD-91 (Account setup wizard step 1, 8pts), ONBRD-92 (Account setup
wizard step 2, 8pts), BILLING-44 (Stripe webhook retry logic, 3pts)

Deferred: ONBRD-93 (Account setup wizard step 3, 8pts) — ran out of time;
ONBRD-99 (In-app tooltip tour, 5pts) — design not finalized

Notes: Team agreed to not block launch on tooltip tour. Decision made to ship
wizard steps 1 and 2 to beta users next week pending QA sign-off. Dependency on
design team for ONBRD-99 assets flagged as recurring bottleneck.

---

### Example 2 — Minimal data, no story points

/summarize-sprint-review

Sprint: Q3 Week 6. Goal not defined for this sprint.
Done: Fix checkout bug, Update privacy policy page, Refactor auth middleware
Not done: Dark mode implementation (deprioritized by PM mid-sprint), API rate
limiting (still in progress, ~60% done)
No meeting notes available.

---

### Example 3 — Notes-heavy, ticket list sparse

/summarize-sprint-review

Sprint 11. Goal: "Reduce page load time below 2 seconds on mobile."

Completed tickets: PERF-07, PERF-09, PERF-11 (no titles or points available)

Meeting notes: We hit the goal on the product listing page but not checkout.
Checkout is down to 2.8s from 4.1s which the team felt was good enough to
ship. Decision: accept 2.8s for now and revisit in Sprint 13 after the
infrastructure upgrade. PERF-12 (image CDN migration) was not started because
the vendor access credentials were delayed — this is now a P1 dependency for
next sprint. Team morale note: three engineers flagged that scope kept changing
mid-sprint which made estimation hard.