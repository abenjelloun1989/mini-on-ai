---
name: build-definition-of-done
trigger: /build-dod
description: >
  Produces a tailored Definition of Done (DoD) checklist for a given user story.
  Covers coding standards, testing requirements, documentation, accessibility,
  performance, security, and stakeholder sign-off. Use this skill whenever a
  user story needs a concrete, team-actionable completion contract before it
  enters a sprint or development queue.
tags: [user-stories, agile, definition-of-done, quality, product-management]
---

# Skill: Build Definition of Done (`/build-dod`)

## Purpose

Convert a user story (and any supporting context) into a thorough, checklist-style
Definition of Done that leaves no ambiguity about what "finished" means. The output
gives developers, QA engineers, designers, and stakeholders a shared contract they
can verify before a ticket is closed.

---

## When to Use This Skill

- A user story has been written but lacks explicit completion criteria.
- A team is about to pull a ticket into a sprint and wants to align on quality gates.
- A product manager or BA needs to communicate non-functional requirements alongside
  functional ones without writing a separate spec.
- You want to reduce back-and-forth at the end of a sprint by agreeing upfront on
  what "done" looks like.

---

## Inputs Claude Should Expect

The user will invoke this skill with one or more of the following (in any order):

1. **The user story itself** — a "As a… I want… So that…" statement or a plain
   description of the feature.
2. **Story type hint** (optional) — e.g., UI feature, API endpoint, data migration,
   bug fix, infrastructure change.
3. **Team context** (optional) — stack, compliance requirements, accessibility
   standard (WCAG level), existing team DoD items to extend, or items to exclude.
4. **Ticket ID or title** (optional) — used to label the output.

If the user provides only a bare story with no additional context, proceed with
reasonable defaults and note any assumptions made.

---

## Execution Steps

Follow these steps in order every time `/build-dod` is invoked.

### Step 1 — Parse and Clarify (internal reasoning, not shown to user)

- Identify the story type (UI, API, data, infrastructure, cross-cutting, etc.).
- Note any explicitly mentioned constraints (compliance, stack, accessibility level).
- Flag any critical missing context that would materially change the checklist.
  - If one or two quick clarifying questions would significantly improve output,
    ask them before generating. Limit to a maximum of two questions.
  - If the story is detailed enough to proceed, skip straight to generation.

### Step 2 — Generate the DoD Checklist

Produce checklist sections in the order listed below. Include every section;
omit individual items only when they are clearly irrelevant to the story type
(e.g., "UI rendering" items for a pure backend migration). When omitting a whole
section, include the section header with a one-line note explaining why it was
skipped.

#### Required Sections and Default Items

**1. Code Quality**
- [ ] Code reviewed and approved by at least one peer
- [ ] No new linting errors or warnings introduced
- [ ] No TODO or debug statements left in production code
- [ ] Follows team naming conventions and style guide
- [ ] No unnecessary code duplication (DRY principles applied)

**2. Testing**
- [ ] Unit tests written for all new logic (minimum coverage threshold met — state assumed % if not specified)
- [ ] Integration tests cover key interaction points
- [ ] All existing tests pass with no regressions
- [ ] Edge cases identified in the user story are covered by tests
- [ ] Test data cleaned up or isolated (no shared state leakage)

**3. Functional Verification**
- [ ] All acceptance criteria from the user story pass manually
- [ ] Feature behaves correctly in all in-scope browsers/devices/environments
- [ ] Error states and empty states are handled gracefully
- [ ] Feature works end-to-end in a staging or pre-production environment

**4. Documentation**
- [ ] Inline code comments added where logic is non-obvious
- [ ] README or relevant wiki page updated if setup/config changes
- [ ] API endpoints documented (e.g., OpenAPI/Swagger) if applicable
- [ ] Changelog or release notes entry added if applicable

**5. Accessibility**
- [ ] Meets WCAG 2.1 AA standards (or the level specified in context)
- [ ] All interactive elements are keyboard-navigable
- [ ] Appropriate ARIA labels and roles applied to dynamic content
- [ ] Color contrast ratios verified with an automated tool
- [ ] Screen reader tested on at least one major screen reader (NVDA, VoiceOver, etc.)

**6. Performance**
- [ ] No obvious N+1 queries or redundant network calls introduced
- [ ] Page load / API response time within agreed thresholds (state assumed threshold if not specified)
- [ ] Assets optimized (images compressed, bundles within size budget) if applicable

**7. Security**
- [ ] User input validated and sanitized on the server side
- [ ] No sensitive data exposed in logs, URLs, or client-side storage
- [ ] Authentication and authorization checks in place for new routes/actions
- [ ] Dependencies introduced are free of known critical vulnerabilities (e.g., checked via Dependabot or Snyk)

**8. Deployment & Operations**
- [ ] Feature flag or rollback strategy defined if the change is high-risk
- [ ] Environment variables and secrets managed via approved secrets store
- [ ] Monitoring/alerting updated to cover new failure modes
- [ ] Migration scripts (if any) tested and reversible

**9. Stakeholder Sign-Off**
- [ ] Product manager has reviewed and accepted the feature in staging
- [ ] Design/UX has verified implementation matches approved mockups
- [ ] QA has signed off on the test execution summary
- [ ] Any dependent teams or external stakeholders have been notified of the change

### Step 3 — Add Story-Specific Items

After the standard sections, append a section titled **"Story-Specific Additions"**
containing any checklist items that are uniquely relevant to this story based on
the inputs provided. These should be concrete and actionable, not generic.
Aim for 3–8 items. Examples of what might belong here:

- Specific third-party integrations to verify
- Compliance standards to satisfy (HIPAA, GDPR, PCI-DSS)
- Known edge cases from the requirements that don't fit standard categories
- Business rules or calculations to spot-check

If no story-specific additions are warranted, include the section header and write:
"No story-specific additions identified — the standard checklist fully covers this story."

### Step 4 — Append a Metadata Block

At the end of the document, include a small metadata block:

---
Story reference: [Ticket ID or story title provided, or "Not specified"]
Story type detected: [UI feature | API endpoint | data migration | bug fix | infrastructure | cross-cutting | other]
Assumptions made: [Bullet list of any defaults assumed, or "None"]
Suggested WCAG level applied: [AA | AAA | None — with reason]
Suggested test coverage threshold: [e.g., 80% — with reason, or "Defer to team standard"]
Generated by: /build-dod skill
---

---

## Output Format Rules

- Use GitHub-flavored Markdown checkbox syntax (`- [ ]`) for every checklist item.
- Section headers must use `##` (H2).
- The "Story-Specific Additions" section must use `##` and appear after all standard sections.
- Do not number the checklist items — checkboxes only.
- Keep each item to a single, imperative-voice sentence (starts with a verb or noun phrase, max ~120 characters).
- Do not add explanatory prose inside the checklist itself; keep it scannable.
- If context warrants a brief note under a section (e.g., "WCAG AAA applied because healthcare context was specified"), place it as a single italicized line directly under the section header, before the items.
- Total output should be directly pasteable into Jira, Linear, Notion, or a GitHub issue without reformatting.

---

## Constraints and Quality Rules

1. **Never collapse or skip core sections** without a stated reason.
2. **Never invent specific numeric thresholds** (coverage %, response times) as hard requirements if the user did not provide them — state them as defaults/assumptions in the metadata block.
3. **Security section is always included**, regardless of story type. Even a UI-only story can introduce XSS or data exposure risks.
4. **Accessibility section is always included** for any story that touches a user interface. For pure backend stories, include the header with a skip note.
5. **Be specific, not aspirational.** "Tests cover the three payment failure modes described in the story" is good. "Ensure high quality" is not acceptable.
6. **Do not duplicate acceptance criteria** from the user story verbatim inside the DoD — the DoD governs *how* work is done and *verified*, not *what* is built.
7. Output must be self-contained: a reader who has never seen the conversation should understand every item.

---

## Usage Examples

### Example 1 — UI Feature, Minimal Context

**Invocation:**

/build-dod As a returning customer, I want to see my last 10 orders on my account dashboard so that I can quickly reorder items I've bought before.

**What Claude will do:**
Detect story type as UI feature. Apply WCAG 2.1 AA defaults. Generate all nine standard
sections with the order-history context woven into story-specific additions (e.g.,
verify pagination if order count exceeds 10, check empty state for new customers,
confirm PII masking on order details). Note assumptions about coverage threshold and
response time in the metadata block.

---

### Example 2 — API Endpoint, With Team Context

**Invocation:**

/build-dod
Story: As a mobile app, I want to call a POST /cart/checkout endpoint so that I can submit an order without the user leaving the app.
Context: Node.js/Express backend, PCI-DSS compliance required, team standard is 85% unit test coverage, no UI changes in this ticket.

**What Claude will do:**
Detect story type as API endpoint. Skip accessibility items for UI rendering (note
reason). Elevate the security section with PCI-DSS–specific items (tokenization,
no raw card data in logs). Set test coverage threshold to 85% (team-provided, not
assumed). Add story-specific items for idempotency key handling, timeout/retry
behavior, and order confirmation event emission.

---

### Example 3 — Bug Fix, With Ticket ID

**Invocation:**

/build-dod
Ticket: BUG-4412 — Discount code not applied when cart contains a subscription item
Story type: Bug fix
Stack: React frontend, Python/Django backend

**What Claude will do:**
Detect story type as bug fix. Tailor the testing section to emphasize regression
test creation (a test that reproduces the original bug must be added). Add
story-specific items for verifying the fix across subscription + non-subscription
mixed carts, confirming the correct discount amount appears in the order summary,
and checking that no valid discount codes are silently rejected after the fix.
Include the ticket ID (BUG-4412) in the metadata block.