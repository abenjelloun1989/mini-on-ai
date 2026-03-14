---
name: identify-edge-cases
trigger: /find-edge-cases
description: >
  Analyzes a user story and its acceptance criteria to surface a prioritized
  list of edge cases, boundary conditions, and failure scenarios that
  development and QA must account for. Use this skill whenever a user story
  feels "complete" but you want to stress-test it before handing it to
  engineers — catching ambiguity, missing states, and risky inputs before a
  single line of code is written.
tags: [user-stories, qa, edge-cases, product-management, requirements]
---

# Skill: Identify Edge Cases (`/find-edge-cases`)

## Purpose

Given a user story and (optionally) its acceptance criteria, produce a
comprehensive, prioritized list of edge cases, boundary conditions, and failure
scenarios. The output should be immediately usable by developers writing unit
tests and QA engineers building test plans.

---

## When to Use This Skill

- After drafting a user story but before sprint planning or ticket grooming
- When a story involves numeric inputs, date ranges, permissions, or multi-step
  flows
- When QA has flagged a story as under-specified
- Before writing acceptance criteria, to discover hidden requirements
- Any time a stakeholder asks "what could go wrong?"

---

## How to Invoke

```
/find-edge-cases [user story and/or acceptance criteria pasted inline]
```

Optionally include:
- The feature area or domain (e.g., "checkout flow," "user authentication")
- Known constraints (e.g., "mobile only," "must support offline mode")
- Existing acceptance criteria if already written

---

## Execution Instructions

Follow these steps in order every time the skill is triggered.

### Step 1 — Parse the Input

1. Extract the user story in standard format:
   **As a** [persona], **I want** [goal], **so that** [benefit].
   If the input is not in this format, infer the persona, goal, and benefit
   from the raw text before proceeding.
2. Extract any acceptance criteria provided (Given/When/Then or bullet form).
3. Identify the core domain (e.g., payments, authentication, file upload,
   search, notifications).
4. Note any explicit constraints or technical details mentioned.

### Step 2 — Generate Edge Case Candidates

Systematically examine the story through each of the following lenses. For
each lens, generate as many candidate edge cases as apply — do not filter yet.

**Boundary Values**
- Minimum and maximum allowed values for every numeric, text, or date field
- Off-by-one scenarios (just under, at, and just over each limit)
- Empty, zero, null, and undefined inputs

**Invalid & Unexpected Input**
- Wrong data types (e.g., letters in a numeric field)
- Malformed formats (e.g., invalid email, phone, URL, date string)
- Inputs that are individually valid but invalid in combination
- Extremely long strings or excessively large numbers
- Special characters, Unicode, emoji, right-to-left text, whitespace-only

**State & Timing**
- First-time use vs. returning user
- Concurrent actions (two users or tabs acting simultaneously)
- Race conditions in multi-step flows
- Session expiry mid-task
- Network interruption at each step of the flow
- Partial completion / abandoned flows and what state is left behind

**Permissions & Roles**
- Unauthenticated access attempts
- Users with insufficient permissions trying to perform the action
- Privilege escalation attempts
- Account suspended, locked, or deleted mid-session

**Data Relationships & Dependencies**
- Referenced record no longer exists (deleted or archived)
- Required upstream step was skipped or failed
- Downstream system is unavailable or returns an error
- Duplicate submissions (double-click, back-button resubmit)
- Stale data displayed after a background update

**Volume & Performance**
- Zero results vs. one result vs. maximum results
- Paginated lists at page boundaries
- Very large files, datasets, or bulk operations
- Slow or timeout responses from external services

**Integration & Environment**
- Third-party API returns unexpected payload or error code
- Feature behavior on different devices, browsers, or OS versions (if relevant)
- Timezone and locale differences (dates, currency, number formats)
- Daylight saving time transitions, leap years, month-end dates

**Business Logic Conflicts**
- Applying multiple discounts, rules, or statuses simultaneously
- Actions performed in an unexpected sequence
- Retroactive changes that affect historical records
- Edge cases specific to the stated business domain

### Step 3 — Prioritize Each Edge Case

Assign a priority to every edge case using this rubric:

| Priority | Label | Criteria |
|----------|-------|----------|
| P1 | **Critical** | Data loss, security risk, financial error, or complete feature failure |
| P2 | **High** | Significant user-facing bug, incorrect output, or broken flow |
| P3 | **Medium** | Degraded experience, unclear messaging, or recoverable error |
| P4 | **Low** | Minor cosmetic issue, unlikely scenario, or nice-to-have guard |

### Step 4 — Deduplicate and Organize

- Remove duplicates or near-duplicates; keep the most specific version.
- Group edge cases under logical categories (use the lens names from Step 2
  as category headers, dropping any empty categories).
- Within each category, sort by priority descending (P1 first).

### Step 5 — Produce the Output

Render the final output exactly as specified in the Output Format section below.

---

## Output Format

Produce the following sections in order. Do not omit any section.

---

### 📋 Story Summary

Restate the parsed user story in one sentence and list any acceptance criteria
provided. If none were provided, note that explicitly.

---

### ⚠️ Edge Cases by Category

For each non-empty category, use this structure:

#### [Category Name]

| # | Edge Case | Priority | Notes / Recommended Handling |
|---|-----------|----------|-------------------------------|
| 1 | [Concise description of the scenario] | P1 / P2 / P3 / P4 | [Brief note on expected behavior or mitigation] |

---

### 🔢 Priority Summary

A flat, ranked list of all P1 and P2 edge cases across all categories — the
"must address before release" shortlist. Format as a numbered list with the
category name in brackets.

---

### 💡 Recommended Acceptance Criteria Additions

List 3–8 new acceptance criteria statements (in Given/When/Then format) derived
directly from the P1 and P2 edge cases. These are ready to paste into the
ticket.

---

### 🚩 Open Questions

List any ambiguities or assumptions encountered during analysis that a product
manager or stakeholder must resolve before development begins. Format as a
bulleted list of questions.

---

## Quality Rules

- **Be specific.** Every edge case must describe a concrete scenario, not a
  vague category. Write "User submits a quantity of 0" not "invalid quantity."
- **Be actionable.** Every Notes column entry must state what the system
  *should* do, not just that "this could be a problem."
- **Do not pad.** Only include edge cases that are plausible given the story's
  domain. Omit absurd or technically impossible scenarios.
- **No duplicates.** If two edge cases are substantially the same, merge them.
- **Prioritize ruthlessly.** Not every edge case is P1. Use the rubric strictly.
- **Acceptance criteria additions must be testable.** Each Given/When/Then must
  describe a condition that a tester can verify with a pass/fail result.
- **Open questions must be answerable.** Frame each question so a product
  manager can respond with a direct decision, not more questions.

---

## Usage Examples

### Example 1 — Basic invocation with a raw story

/find-edge-cases

As a registered user, I want to upload a profile photo so that other users can
recognize me.

---

### Example 2 — Story with acceptance criteria included

/find-edge-cases

**User Story:**
As a checkout customer, I want to apply a promo code to my order so that I
receive the advertised discount.

**Acceptance Criteria:**
- Given a valid promo code, when I apply it, then the discount appears in the
  order summary.
- Given an expired promo code, when I apply it, then I see an error message.
- Given a valid promo code, when I complete the order, then the discounted
  total is charged to my card.

---

### Example 3 — Story with domain context and constraints

/find-edge-cases

Feature area: Mobile banking — fund transfers
Constraint: iOS and Android only; offline mode not supported

As a bank account holder, I want to transfer funds to another account within
the same bank so that I can pay people without visiting a branch.

Known constraint: Transfers above $10,000 require two-factor authentication.
Maximum single transfer limit is $25,000. Users can have up to 10 saved
payees.

---

## Notes for Claude

- If the user provides only a feature description without a formal story,
  proceed by inferring the persona and goal — do not ask for clarification
  before producing output.
- If acceptance criteria are missing, note this in the Story Summary and
  generate edge cases based on the story alone; your Recommended Acceptance
  Criteria Additions section becomes especially valuable in this case.
- If the story is very short or vague, generate a broader set of edge cases
  and flag the vagueness in the Open Questions section rather than refusing
  to proceed.
- Always complete the full output format. Never truncate the edge case table
  with "and more…" — enumerate every item found.