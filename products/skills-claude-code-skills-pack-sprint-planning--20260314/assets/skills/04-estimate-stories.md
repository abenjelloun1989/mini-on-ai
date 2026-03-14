---
name: estimate-stories
trigger: /estimate-stories
description: Generates relative story point estimates for a list of user stories using complexity, effort, and uncertainty heuristics. Produces a Fibonacci-scale estimate for each story with a concise justification to anchor team discussion during planning poker or sprint planning ceremonies.
tags: [agile, estimation, sprint-planning, scrum, backlog]
author: Claude Code Skills Pack — Sprint Planning
version: 1.0.0
---

# Skill: estimate-stories

## Purpose

This skill analyzes a list of user stories and generates relative story point estimates on the Fibonacci scale (1, 2, 3, 5, 8, 13, 21). Each estimate is accompanied by a brief justification covering the three core estimation dimensions — **complexity**, **effort**, and **uncertainty** — so the team has a concrete starting point for discussion rather than an empty room and a blank whiteboard.

Use this skill when:
- You are preparing for a sprint planning ceremony and want pre-seeded estimates
- Your team is grooming a backlog and needs a first pass before voting
- You want to identify high-uncertainty stories that need further decomposition before they can be committed
- A scrum master or team lead needs to draft estimates for async review before a synchronous session

---

## How Claude Should Execute This Skill

### Step 1: Parse the Input

Accept stories in any of the following formats provided by the user:
- A plain numbered or bulleted list of story titles
- Full user story format: "As a [role], I want [goal], so that [benefit]"
- A mixed list combining titles and full story text
- A pasted Jira export, CSV snippet, or raw notes

If the input is ambiguous or stories are missing key context, make reasonable assumptions and note them explicitly in the output. Do not halt execution to ask clarifying questions unless the input is completely uninterpretable.

### Step 2: Evaluate Each Story Across Three Dimensions

For every story, internally assess the following before assigning a point value:

**Complexity**
- How many systems, services, or components are involved?
- Does this require new architecture or extend existing patterns?
- Are there branching logic paths, edge cases, or integrations with third-party APIs?

**Effort**
- How much total work is implied — frontend, backend, testing, documentation?
- Is this clearly scoped or does it imply a chain of dependent tasks?
- Would a mid-level engineer complete this in hours, days, or a week+?

**Uncertainty**
- How well-understood is the problem and the solution approach?
- Are there unknowns, dependencies on other teams, or unclear acceptance criteria?
- Would the team need a spike or discovery session before starting?

### Step 3: Assign a Fibonacci Point Value

Map your assessment to the standard Fibonacci scale using these reference anchors:

| Points | Meaning |
|--------|---------|
| 1 | Trivial change, fully understood, minimal risk (e.g., copy update, config flag) |
| 2 | Small, well-understood task with little branching or integration |
| 3 | Straightforward feature, some effort but clear path forward |
| 5 | Medium complexity, multiple components or some uncertainty |
| 8 | Complex feature, significant effort, notable unknowns or integration risk |
| 13 | Large, high uncertainty — likely needs decomposition before sprint commitment |
| 21 | Epic-sized or severely underspecified — must be broken down before estimating |

Do not use values outside the Fibonacci sequence. Do not average between values — choose the higher value when a story sits between two options.

### Step 4: Flag Stories That Need Attention

Apply the following flags where appropriate and include them in the output table:

- 🔴 **SPLIT** — Story is 13+ points and should be decomposed into smaller stories
- 🟡 **SPIKE** — Story has high uncertainty and may require a research/discovery task first
- 🔵 **BLOCKED** — Story has a visible external dependency that must be resolved before it can start
- ✅ **READY** — Story is well-defined, appropriately sized, and ready to commit

### Step 5: Generate the Output

Produce a structured Markdown report with the following sections:

---

**Section 1: Estimation Summary Table**

A table with columns: `#`, `Story`, `Points`, `Status`, `Key Driver`

The "Key Driver" column contains a 5–10 word phrase capturing the primary reason for the estimate (e.g., "Third-party API integration, unclear rate limits").

**Section 2: Detailed Justifications**

For each story, a short paragraph (3–5 sentences) explaining the estimate across the complexity, effort, and uncertainty dimensions. Reference specific elements from the story text when possible.

**Section 3: Estimation Health Summary**

A brief paragraph (4–6 sentences) summarizing the overall health of this story set. Call out:
- The total estimated points across all stories
- How many stories are flagged for splitting or spiking
- Whether this set is sprint-committable or needs grooming first
- Any patterns observed (e.g., many stories depend on the same service, several stories lack acceptance criteria)

**Section 4: Recommended Next Steps**

A short numbered list (3–5 items) of concrete actions the scrum master or team lead should take before committing these stories to a sprint.

---

## Output Format Rules

- Use Markdown throughout — tables, headers, bold labels, and emoji flags
- Keep justification paragraphs concise — this is a discussion anchor, not a design document
- Do not invent acceptance criteria that were not implied by the story text
- Do not assign 0 points — if something is trivial, use 1
- If the user provides a team velocity or sprint capacity, reference it in the Health Summary
- Always surface assumptions made when input was incomplete

---

## Constraints and Quality Rules

- **Fibonacci only.** Never output non-standard values like 4, 6, 7, 10, or 15.
- **No false precision.** Estimation is inherently relative. Frame justifications as team discussion starters, not authoritative verdicts.
- **Err toward higher estimates when uncertain.** Underestimating costs teams more than overestimating.
- **Stories at 13+ always receive the SPLIT flag.** No exceptions, even if technically coherent.
- **Do not skip stories.** Every story in the input must appear in the output, even if the estimate is a 21 with a SPLIT flag.
- **Keep justifications story-specific.** Generic statements like "this seems complex" are not acceptable — tie the reasoning to details in the story.

---

## Usage Examples

### Example 1: Simple story list

/estimate-stories

1. Update the footer copyright year to 2025
2. Add email notification when a user's subscription is about to expire
3. Migrate user authentication from JWT to OAuth 2.0
4. Allow admins to bulk-delete inactive accounts
5. Display a loading skeleton while the dashboard data fetches

---

### Example 2: Full user story format with team context

/estimate-stories

Team velocity: 34 points. Two-week sprint. 4 engineers (1 senior, 2 mid, 1 junior).

- As a customer, I want to receive an SMS alert when my order ships, so that I know when to expect delivery.
- As an admin, I want to export all user data to CSV filtered by date range, so that I can generate compliance reports.
- As a user, I want to log in with my Google account, so that I don't have to remember a separate password.
- As a mobile user, I want the checkout flow to work offline and sync when I reconnect, so that I can shop in low-connectivity areas.

---

### Example 3: Rough notes from a backlog refinement session

/estimate-stories

Stories from today's grooming session (needs estimates before Thursday planning):

- Fix the broken pagination on the orders table
- Redesign the onboarding flow (marketing wants 3 fewer steps)
- Set up staging environment parity with production
- Add dark mode support across the entire app
- Investigate why report generation times out for large datasets
- Let users tag transactions with custom categories
- Add two-factor authentication option to account settings