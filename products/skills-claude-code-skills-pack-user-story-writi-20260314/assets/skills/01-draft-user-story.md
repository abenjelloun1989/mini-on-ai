---
name: draft-user-story
trigger: /draft-story
description: >
  Transforms a raw feature request, rough idea, or brief description into a
  properly formatted user story using the "As a / I want / So that" structure.
  Surfaces the user role, concrete goal, and business value so development
  teams have unambiguous intent before a ticket is written. Use this skill
  whenever a stakeholder has described a feature informally and you need a
  clean, structured story ready for refinement or sprint planning.
tags:
  - product-management
  - user-stories
  - requirements
  - agile
---

# Skill: Draft User Story (`/draft-story`)

## Purpose

Convert a raw feature request or informal description into a single, well-structured user story using the standard **As a / I want / So that** format. The output should eliminate role ambiguity, clarify the desired behaviour, and make the business value explicit — giving engineers and designers everything they need to understand *who* they are building for, *what* they are building, and *why* it matters.

---

## When to Use This Skill

- A stakeholder or PM has described a feature in plain language and it needs to be formalised.
- A Jira ticket exists with only a title or one-line description.
- A meeting note or Slack message contains a feature idea that needs structure before backlog refinement.
- You want to sanity-check whether a feature request has a clear user role and business value.

---

## Execution Instructions

Follow these steps exactly whenever `/draft-story` is invoked.

### Step 1 — Parse the Raw Input

Read the feature request provided after the `/draft-story` command. Identify:

1. **Who** is described or implied (the user role).
2. **What** they want to do or have (the goal or capability).
3. **Why** they want it (the business value or benefit).

If any of these three elements is missing or ambiguous, note it and make a reasonable inference based on context. Flag inferences explicitly so the user can correct them.

### Step 2 — Identify the User Role

- Choose the most specific role that accurately describes the person benefiting from the feature. Avoid vague roles like "user" or "person" unless no more specific role can be inferred.
- If multiple roles are present, draft a separate user story for each role.
- Common role examples: `admin`, `new user`, `returning customer`, `product manager`, `billing user`, `mobile user`, `guest visitor`, `team lead`.

### Step 3 — Articulate the Goal

- State what the user wants to *do* or *achieve*, not what the system should *technically do*.
- Write in active voice from the user's perspective.
- Keep the goal to a single, discrete capability. If the request contains more than one distinct capability, split it into multiple stories and label them clearly (Story 1, Story 2, etc.).

### Step 4 — Define the Business Value

- Explain the *outcome* or *benefit* the user gains — not a restatement of the goal.
- Business value should answer: "What does this enable or improve for the user or the business?"
- Avoid vague value statements like "so that it is easier." Be specific.

### Step 5 — Write the Formatted User Story

Output the story in this exact format:

---

**User Story**

**As a** [specific user role],
**I want** [clear, discrete goal or capability],
**So that** [concrete business value or benefit].

---

### Step 6 — Add a Story Title

Provide a concise ticket-ready title above the story in this format:

**Title:** [Action] + [Object] + [Context if needed]

Example: `Enable Password Reset via Email for Registered Users`

### Step 7 — Surface Assumptions and Flags

After the formatted story, include a short **Assumptions & Flags** section. List:

- Any role, goal, or value that was inferred rather than stated explicitly.
- Ambiguities the author should confirm before the story goes into a sprint.
- Scope concerns if the request seems too large for a single story.

Use a simple bulleted list. Keep this section concise — 2 to 5 bullets maximum.

### Step 8 — Offer Next Steps

End with a brief **Next Steps** line suggesting which other skills in this pack to run next, such as generating acceptance criteria (`/acceptance-criteria`) or identifying edge cases (`/edge-cases`).

---

## Output Format Rules

- Use the exact **As a / I want / So that** wording. Do not substitute synonyms.
- Bold the three structural keywords: **As a**, **I want**, **So that**.
- Each clause must be on its own line.
- The story must be one sentence per clause — no sub-clauses, no lists inside the story itself.
- The Title must be in title case.
- Total output length: short and scannable. The story itself should never exceed 3 lines. Supporting sections should be concise.
- Do not add acceptance criteria, test cases, or definition of done to this output — those are handled by separate skills in this pack.

---

## Quality Rules

| Rule | Requirement |
|---|---|
| One story per capability | Split compound requests into numbered stories |
| No technical implementation detail | Stories describe user need, not system behaviour |
| Specific user role | Never use "user" alone if a more specific role can be inferred |
| Business value is an outcome | Must describe a benefit, not restate the goal |
| Active voice | All three clauses written from the user's perspective |
| No jargon in the story itself | Plain language only; jargon goes in flags if needed |

---

## Usage Examples

### Example 1 — Simple Feature Request

**Invocation:**

/draft-story Users should be able to reset their password if they forget it

**Output:**

**Title:** Reset Forgotten Password via Email for Registered Users

**User Story**

**As a** registered user who has forgotten their password,
**I want** to receive a password reset link at my registered email address,
**So that** I can regain access to my account without contacting support.

**Assumptions & Flags**
- Assumed the reset mechanism is email-based; confirm if SMS or authenticator app reset is also in scope.
- Assumed "users" means registered users with existing accounts; guest checkout users may need a separate story.

**Next Steps:** Run `/acceptance-criteria` to define the conditions this story must meet, or `/edge-cases` to capture failure scenarios such as expired links or unrecognised email addresses.

---

### Example 2 — Vague Business Request with Multiple Capabilities

**Invocation:**

/draft-story The dashboard needs to be better — managers should see team performance and also be able to export reports

**Output:**

Two distinct capabilities detected. Splitting into separate stories.

---

**Story 1**

**Title:** View Team Performance Summary on Manager Dashboard

**User Story**

**As a** team manager,
**I want** to view a summary of my team's performance metrics on my dashboard,
**So that** I can identify trends and address issues without pulling separate reports.

---

**Story 2**

**Title:** Export Team Performance Reports from Manager Dashboard

**User Story**

**As a** team manager,
**I want** to export my team's performance data as a downloadable report,
**So that** I can share results with stakeholders outside the platform.

---

**Assumptions & Flags**
- "Better" is subjective — the two capabilities above are the concrete requests inferred. Confirm no additional improvements are intended.
- "Performance metrics" is undefined — confirm which KPIs are in scope before development begins.
- Export format (CSV, PDF, Excel) is unspecified; capture this in acceptance criteria.

**Next Steps:** Run `/acceptance-criteria` on each story individually to lock down metric definitions and export format requirements.

---

### Example 3 — Well-Described Request

**Invocation:**

/draft-story As a new customer completing their first purchase, I want to save my payment details so I don't have to re-enter them next time

**Output:**

**Title:** Save Payment Details After First Purchase for New Customers

**User Story**

**As a** new customer completing their first purchase,
**I want** to save my payment details securely for future use,
**So that** I can check out faster on subsequent visits without re-entering my card information.

**Assumptions & Flags**
- Input was well-structured; minimal inference required.
- "Securely" has been added to the goal — confirm compliance requirements (PCI-DSS) are understood by the team before this story is accepted into a sprint.
- Confirm whether "save details" is opt-in (prompted at checkout) or opt-out (saved by default).

**Next Steps:** Run `/acceptance-criteria` to define the opt-in flow and security requirements, or `/definition-of-done` to ensure compliance checkpoints are included before sign-off.