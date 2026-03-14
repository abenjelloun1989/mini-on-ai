---
name: Format Jira Ticket
trigger: /format-jira
description: Assembles all user story components — user story, acceptance criteria, edge cases, and definition of done — into a fully structured, copy-paste-ready Jira ticket description with labeled sections and story point guidance. Use this skill as the final assembly step after drafting your story components, or provide a raw feature request and Claude will generate all sections inline before assembling the ticket.
tags: [product-management, jira, user-stories, tickets, requirements]
---

# Skill: Format Jira Ticket

## Purpose

This skill produces a complete, Jira-ready ticket description that a product manager or business analyst can copy directly into a Jira issue without additional editing. It either assembles pre-written story components provided in the prompt or generates all missing sections from a raw feature request before assembling them. The output eliminates ambiguity for developers by ensuring every ticket has consistent structure, clear acceptance criteria, known edge cases, and an explicit definition of done.

## When to Use This Skill

- You have already drafted some or all story components (user story, acceptance criteria, edge cases, DoD) and want them formatted into a single Jira description block.
- You have a raw feature request or brief and want a fully structured Jira ticket generated in one step.
- You are preparing a sprint backlog and need multiple tickets formatted consistently.
- You want story point guidance based on the complexity surfaced in the ticket.

---

## How to Execute This Skill

Follow these steps in order every time this skill is triggered.

### Step 1 — Assess What Has Been Provided

Read the user's input carefully and determine which of the following components are already present:

- **User Story** — A sentence in the format "As a [persona], I want [action] so that [benefit]."
- **Acceptance Criteria** — A numbered or bulleted list of testable conditions.
- **Edge Cases** — A list of boundary conditions, error states, or non-happy-path scenarios.
- **Definition of Done** — A checklist of completion standards the team must meet.

If any component is missing, proceed to Step 2. If all components are present, skip to Step 3.

### Step 2 — Generate Any Missing Components

For each missing component, generate it now based on the feature context provided. Apply the following rules:

**User Story (if missing)**
- Extract the persona, desired action, and business benefit from the input.
- Write exactly one user story sentence: "As a [persona], I want [action] so that [benefit]."
- If multiple personas are implied, write the primary story and note secondary personas in the Context section.

**Acceptance Criteria (if missing)**
- Write 4–8 discrete, testable criteria.
- Each criterion must be falsifiable — a QA engineer should be able to write a test for it.
- Use present tense: "The system displays…", "The user can…", "An error message appears…"
- Number each criterion starting from 1.

**Edge Cases (if missing)**
- List 4–8 edge cases covering: empty/null states, maximum input boundaries, unauthorized access attempts, network or system failure conditions, concurrent user actions, and unexpected input formats.
- Phrase each as a scenario: "When [condition], then [expected behavior]."

**Definition of Done (if missing)**
- Include checkboxes covering: code reviewed, unit tests written and passing, integration tests passing, accessibility checked (WCAG 2.1 AA), design QA approved, product owner sign-off, documentation updated, and feature flag or release configuration confirmed if applicable.
- Add or remove items only if the feature context makes a standard item clearly irrelevant.

### Step 3 — Determine Story Point Guidance

Analyze the assembled components and assign a recommended story point estimate using the Fibonacci scale (1, 2, 3, 5, 8, 13).

Use these guidelines:

| Points | Signal |
|--------|--------|
| 1–2 | Trivial change, single component, no edge cases, no external dependencies |
| 3 | Small feature, clear scope, 1–2 integrations, few edge cases |
| 5 | Moderate complexity, multiple components, several edge cases, some unknowns |
| 8 | High complexity, cross-system impact, many edge cases, significant unknowns |
| 13 | Candidate for splitting; story is too large for a single sprint ticket |

Provide the recommended estimate and a one-sentence rationale. If the story scores 13, flag it explicitly and suggest how to split it.

### Step 4 — Assemble the Jira Ticket

Output the complete ticket using exactly the template below. Do not omit any section. Do not add extra commentary outside the ticket block.

---

## Output Template

Reproduce this structure exactly. Replace all placeholder text with real content.

---

TICKET TITLE: [Concise imperative title, e.g., "Add email verification step to registration flow"]

STORY TYPE: [Story / Bug / Task / Spike — choose the most appropriate]

STORY POINTS (Recommended): [Fibonacci number] — [One-sentence rationale]

---

## User Story

As a [persona], I want [action] so that [benefit].

**Context:**
[1–3 sentences of background that a developer picking up this ticket cold would need to understand why this work matters and where it fits in the product. Include relevant links, prior tickets, or dependencies if provided by the user.]

---

## Acceptance Criteria

1. [Criterion]
2. [Criterion]
3. [Criterion]
4. [Criterion]
[Continue as needed, maximum 8]

---

## Edge Cases

- When [condition], then [expected behavior].
- When [condition], then [expected behavior].
- When [condition], then [expected behavior].
- When [condition], then [expected behavior].
[Continue as needed, maximum 8]

---

## Definition of Done

- [ ] Code reviewed and approved by at least one peer
- [ ] Unit tests written and all passing
- [ ] Integration tests written and all passing
- [ ] Accessibility reviewed against WCAG 2.1 AA standards
- [ ] Design QA completed and signed off
- [ ] Product owner has accepted the implementation
- [ ] Relevant documentation updated (API docs, README, Confluence, etc.)
- [ ] No new console errors or warnings introduced
- [ ] Feature deployed to staging and smoke-tested
- [ ] [Add any feature-specific items derived from the acceptance criteria]

---

## Notes & Open Questions

[List any assumptions made during ticket creation, dependencies on other teams or tickets, open questions that need answers before or during development, or risks identified. If none exist, write "None at this time."]

---

**Labels:** [Suggest 2–4 Jira labels based on the feature area, e.g., authentication, frontend, payments, notifications]
**Epic Link:** [If an epic was mentioned, reference it here. Otherwise write "To be assigned."]
**Suggested Assignee:** [If a team or role was mentioned, note it. Otherwise write "To be assigned."]

---

## Output Quality Rules

Enforce these rules on every ticket produced:

1. **No vague acceptance criteria.** Words like "works correctly," "looks good," or "is fast" are not acceptable. Every criterion must describe a specific, observable, testable outcome.
2. **No orphaned edge cases.** Every edge case must connect to a scenario that could plausibly occur given the feature described. Do not invent unrelated scenarios.
3. **Consistent tense.** Acceptance criteria use present tense. Edge cases use conditional structure ("When… then…"). Definition of Done uses past participle ("Code reviewed…").
4. **Title is imperative.** The ticket title must start with an action verb: Add, Remove, Update, Fix, Implement, Display, Allow, Prevent, etc.
5. **Story points must be justified.** Never provide a point estimate without the one-sentence rationale.
6. **Flag oversized stories.** Any ticket that warrants 13 points must include a split recommendation before the ticket body.
7. **Self-contained output.** The assembled ticket must make sense to a developer who has no prior context beyond what is written in the ticket itself.

---

## Usage Examples

### Example 1 — Assemble from existing components

/format-jira

User story: As a returning customer, I want to save multiple shipping addresses to my profile so that I can check out faster on future orders.

Acceptance criteria:
1. Users can add up to 5 shipping addresses.
2. Each address requires name, street, city, state, zip, and country.
3. Users can set one address as default.
4. The default address is pre-selected at checkout.
5. Users can delete any saved address.

Edge cases: Already written — address limit reached, invalid zip code entered, user deletes the default address.

DoD: Standard team checklist applies.

---

### Example 2 — Generate all components from a raw brief

/format-jira

Feature request: We need a way for admins to bulk-deactivate user accounts from the admin dashboard. Marketing wants this so they can clean up inactive accounts at the end of each quarter. It should work on up to 500 accounts at a time.

---

### Example 3 — Flag and split an oversized story

/format-jira

We want to rebuild the entire checkout flow including cart management, address selection, payment method handling, order review, confirmation emails, and post-purchase upsell recommendations. Users should be able to complete checkout as a guest or as a logged-in account holder.

[Claude should recognize this as a 13-point story, flag it, propose a split into 4–6 smaller tickets, and then format the first logical ticket in the series.]