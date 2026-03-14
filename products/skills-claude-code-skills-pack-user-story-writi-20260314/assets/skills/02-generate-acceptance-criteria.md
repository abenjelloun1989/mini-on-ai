---
name: generate-acceptance-criteria
trigger: /gen-criteria
description: >
  Generates a comprehensive set of Given/When/Then acceptance criteria from a
  user story. Use this skill when you have a user story and need to define
  clear, testable conditions that confirm the feature works as intended before
  development begins. Covers primary success scenarios, alternate paths, and
  key functional requirements. Eliminates ambiguity by making implicit
  expectations explicit.
tags:
  - product-management
  - user-stories
  - acceptance-criteria
  - agile
  - requirements
---

# Skill: Generate Acceptance Criteria

## Purpose

Convert a user story into a complete, structured set of Given/When/Then acceptance criteria. Each criterion must be unambiguous, independently testable, and written so that both developers and QA engineers can verify it without interpretation.

## When to Use

- You have a user story (formal or informal) and need testable acceptance criteria before handing off to engineering
- Stakeholders or developers are asking "how do we know when this is done?"
- You want to surface hidden assumptions or edge cases before sprint planning
- You are preparing a Jira ticket and need an AC section

## How to Execute This Skill

Follow these steps precisely when `/gen-criteria` is invoked:

### Step 1 — Parse the Input

Read the user story provided by the user. Accept any of these formats:

- Formal: "As a [role], I want [capability], so that [benefit]"
- Informal: A plain-language description of a feature or requirement
- Partial: A fragment like "users should be able to reset their password"

If the input is ambiguous or critically incomplete (missing the action, the actor, or the goal), ask one focused clarifying question before proceeding. Do not ask multiple questions at once.

### Step 2 — Identify the Scenario Categories

Before writing criteria, silently identify:

1. **Primary success path** — the happy path where everything works as expected
2. **Input validation** — what constitutes valid vs. invalid data or state
3. **Permission and role boundaries** — who can and cannot perform the action
4. **System state dependencies** — what must be true before the action is possible
5. **Feedback and communication** — what the system must show or do in response
6. **Negative/failure paths** — what happens when the action fails or is blocked

Not every story requires criteria in all six categories. Include only the categories that are relevant.

### Step 3 — Write the Acceptance Criteria

Write each criterion using strict Given/When/Then format:

- **Given** — the precondition or system state before the action
- **When** — the specific action the user or system takes
- **Then** — the observable, verifiable outcome

**Formatting rules:**

- Label each criterion with a sequential number: AC-1, AC-2, AC-3, etc.
- Use a short title in bold above each criterion (e.g., **Successful Submission**)
- Write in plain, precise English — no jargon, no vague words like "appropriate," "correctly," or "properly"
- Each criterion must be independently testable (one condition per Then clause)
- If a Then clause contains "and," consider splitting into two separate criteria
- Use concrete values where possible (e.g., "within 3 seconds" not "quickly"; "a red inline error message" not "an error")

### Step 4 — Add a Notes Section (if needed)

After the criteria, include a brief **Open Questions** section if any assumptions were made that a product owner or stakeholder should confirm. Format as a bulleted list. If no open questions exist, omit this section entirely.

### Step 5 — Output the Final Document

Deliver the result using this exact structure:

---

**User Story:**
[Restate the user story as parsed, cleaned up if informal]

**Acceptance Criteria:**

**AC-1 — [Short Title]**
- Given [precondition]
- When [action]
- Then [outcome]

**AC-2 — [Short Title]**
- Given [precondition]
- When [action]
- Then [outcome]

[Continue for all relevant criteria]

**Open Questions:** *(omit section if none)*
- [Question 1]
- [Question 2]

---

## Constraints and Quality Rules

- **Minimum criteria count:** Generate at least 4 criteria per story. Simple stories may have 4–6; complex stories may have 8–12.
- **No vague language:** Flag and replace any term that cannot be objectively measured or observed.
- **No implementation detail:** Criteria describe observable behavior, not how the system achieves it. Do not mention specific technologies, database operations, or code-level behavior.
- **One Then per criterion:** Compound Then clauses must be split unless the outcomes are inseparable (e.g., a modal closes AND focus returns to the trigger button).
- **Testability check:** Before including any criterion, ask: "Could a QA engineer write a test case for this without asking follow-up questions?" If no, rewrite it.
- **Restate the story:** Always restate the user story at the top of output so the criteria are self-contained and pasteable into a ticket.

## Usage Examples

### Example 1 — Formal User Story

**Invocation:**
/gen-criteria As a registered user, I want to reset my password via email, so that I can regain access to my account if I forget my credentials.

**Expected output structure:**

User Story: As a registered user, I want to reset my password via email, so that I can regain access to my account if I forget my credentials.

Acceptance Criteria:

AC-1 — Reset Email Sent for Valid Account
- Given a user is on the "Forgot Password" page
- When they enter an email address associated with an active account and submit the form
- Then the system sends a password reset email to that address within 60 seconds

AC-2 — No Account Disclosure for Unknown Email
- Given a user is on the "Forgot Password" page
- When they enter an email address not associated with any account and submit the form
- Then the system displays the message "If an account exists for this email, you will receive a reset link shortly" and does not send an email

AC-3 — Reset Link Expires After 24 Hours
- Given a password reset email has been sent
- When the user clicks the reset link more than 24 hours after it was issued
- Then the system displays an expiration message and prompts the user to request a new link

AC-4 — Successful Password Update
- Given a user has clicked a valid, unexpired reset link
- When they enter a new password that meets the password policy and submit the form
- Then their password is updated, they are redirected to the login page, and a confirmation message is displayed

AC-5 — Password Policy Enforcement
- Given a user is on the password reset form
- When they enter a new password shorter than 8 characters or containing no numbers
- Then the form displays an inline error message describing the specific requirement that was not met and does not submit

AC-6 — Link Can Only Be Used Once
- Given a user has already used a reset link to successfully change their password
- When they attempt to use the same reset link again
- Then the system displays an invalid or expired link message and does not allow a password change

---

### Example 2 — Informal Feature Request

**Invocation:**
/gen-criteria Users need to be able to export their order history as a CSV file.

**What Claude will do:**
Restate as a clean user story, infer the likely actor (logged-in customer), then generate criteria covering: successful export, empty state (no orders), file format and content requirements, large data set handling, and permission boundary (unauthenticated users cannot export).

---

### Example 3 — Partial or Ambiguous Input

**Invocation:**
/gen-criteria Admins should see a dashboard.

**What Claude will do:**
Identify that "dashboard" is underspecified. Ask one clarifying question: "What is the primary information or action the admin dashboard needs to display or enable? For example: user management metrics, recent activity, system health indicators, or something else?" Once answered, generate full criteria.

---

## Notes for Skill Maintenance

- This skill pairs well with `/gen-story` (story writing) and `/gen-dod` (definition of done)
- If the user provides multiple user stories at once, generate a separate AC block for each, clearly labeled
- Do not generate test cases or QA scripts — this skill produces acceptance criteria only; test case generation is a separate concern