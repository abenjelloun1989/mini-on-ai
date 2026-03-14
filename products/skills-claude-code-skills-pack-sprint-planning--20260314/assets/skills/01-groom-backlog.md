---
name: groom-backlog
trigger: /groom-backlog
description: Analyzes raw backlog items and rewrites them as properly structured user stories with acceptance criteria, flags duplicates, and surfaces missing details that need product owner clarification.
pack: Claude Code Skills Pack: Sprint Planning
category: agile / ceremony-preparation
when-to-use: Run this skill before a backlog refinement session or sprint planning meeting when you have a list of raw, unformatted, or inconsistently written backlog items that need to be shaped into sprint-ready user stories.
---

# Skill: groom-backlog

## Purpose

Transform a raw list of backlog items — tickets, notes, Slack messages, Jira dumps, bullet points, or rough feature requests — into properly structured, sprint-ready user stories with clear acceptance criteria. Simultaneously identify duplicates, surface ambiguities, and produce a prioritized list of questions for the Product Owner.

---

## When to Use This Skill

- Before a sprint planning meeting and you need stories to be well-formed
- After a discovery session that produced rough notes and feature ideas
- When a backlog has grown organically and become inconsistent in quality
- When onboarding a new team and standardizing existing backlog items
- Any time you invoke `/groom-backlog` in Claude Code

---

## How Claude Should Execute This Skill

Follow these steps in order. Do not skip steps or combine them silently.

### Step 1 — Ingest and Inventory the Raw Input

1. Accept the raw backlog items from the user. These may be pasted directly, provided as a file path, or described inline.
2. Parse and number every distinct item, even if they are poorly formatted or duplicated.
3. Display a brief **Intake Summary** before proceeding:
   - Total items received
   - Format/source detected (e.g., "Jira export," "freeform bullet list," "meeting notes")
   - Any items that could not be parsed — ask the user to clarify before continuing

### Step 2 — Detect and Flag Duplicates

1. Compare all items semantically, not just lexically. Two items are duplicates if they describe the same user need, even if worded differently.
2. Group suspected duplicates together.
3. For each duplicate group:
   - Label them `[DUPLICATE GROUP A]`, `[DUPLICATE GROUP B]`, etc.
   - Recommend which single item to keep (choose the most complete one) and why
   - List the others as candidates for merge or deletion
4. Do not discard duplicates silently — always surface them for PO review.

### Step 3 — Rewrite Each Item as a User Story

For every non-duplicate item (and for the kept item from each duplicate group), rewrite it using the following canonical format:

**User Story Title:** A short, imperative-mood title (5–10 words)

**As a** [specific user role or persona],
**I want to** [perform a specific action or achieve a goal],
**so that** [I receive a specific benefit or business outcome].

Rules for the As-a/I-want/So-that statement:
- The user role must be specific (not "user" — use "registered customer," "admin," "first-time visitor," etc.)
- If the role is unclear from context, flag it in the PO Questions section (Step 5)
- The benefit must be business-meaningful, not a restatement of the action

### Step 4 — Write Acceptance Criteria

For each user story, write 3–6 acceptance criteria using **Given/When/Then** (Gherkin-lite) format:

**Acceptance Criteria:**

- **Given** [precondition or context], **When** [the user takes an action], **Then** [the system responds with a specific, verifiable outcome].

Rules for acceptance criteria:
- Each criterion must be independently testable
- At least one criterion should cover the happy path
- Include at least one edge case or error state if the story involves data input, permissions, or external dependencies
- Do not write acceptance criteria so broad they cannot be verified by a QA engineer in a single test case
- If critical information is missing to write a criterion, insert a placeholder: `[NEEDS CLARIFICATION: describe what is missing]`

### Step 5 — Surface PO Clarification Questions

After rewriting all stories, produce a **Product Owner Clarification Queue** — a numbered list of questions the PO must answer before these stories can be considered sprint-ready.

For each question:
- Reference the story by its title
- State exactly what is unclear or missing
- Explain why the ambiguity blocks estimation or implementation

Categorize questions using these labels:
- `[SCOPE]` — unclear boundaries of what is in or out
- `[PERSONA]` — user role is unspecified or ambiguous
- `[BUSINESS RULE]` — logic or policy is undefined
- `[DEPENDENCY]` — relies on another story, system, or team that is not referenced
- `[DESIGN]` — UX/UI decisions needed before development can begin
- `[DATA]` — data structure, source, or validation rules are missing

### Step 6 — Produce the Groomed Backlog Output

Compile everything into a single structured document with the following sections in order:

1. **Grooming Session Summary** — date, input item count, output story count, duplicate groups found, total PO questions raised
2. **Duplicate Flags** — all duplicate groups with recommendations
3. **Groomed User Stories** — all rewritten stories, each with title, As-a statement, and acceptance criteria
4. **Product Owner Clarification Queue** — all questions, numbered and categorized
5. **Grooming Checklist** — a checkbox list the team can use to confirm readiness before sprint planning:
   - [ ] All PO questions answered
   - [ ] All duplicates resolved
   - [ ] All stories reviewed by at least one developer
   - [ ] Acceptance criteria reviewed by QA
   - [ ] Stories are sized (story points not assigned by this skill — use `/estimate-stories`)

---

## Output Format Rules

- Use Markdown throughout
- Use `---` horizontal rules to separate each groomed story from the next
- Bold all Gherkin keywords (Given, When, Then, And, But)
- Use `[NEEDS CLARIFICATION: ...]` inline wherever a story has an unresolvable gap
- Never invent business rules, personas, or system behaviors — flag unknowns instead
- Keep acceptance criteria language implementation-agnostic unless the raw input specifies a technology constraint
- Stories should be written to fit a single sprint increment; if a raw item is too large, split it and note the split explicitly with `[SPLIT FROM: original item text]`

---

## Quality Constraints

- A groomed story is NOT sprint-ready if any acceptance criterion contains the phrase `[NEEDS CLARIFICATION]`
- Do not assign story points — that is handled by `/estimate-stories`
- Do not suggest priority order — that is the PO's responsibility; you may flag urgency signals found in the raw input (e.g., "ASAP," "blocking launch") but do not reorder the backlog
- Maximum of 6 acceptance criteria per story; if more are needed, the story should be split
- Minimum of 3 acceptance criteria per story; if fewer can be written, flag the story as insufficiently defined
- All user roles must be named roles, not pronouns or generic terms like "the user" or "people"

---

## Usage Examples

### Example 1 — Simple inline list

/groom-backlog

Raw items:
- add dark mode
- users should be able to reset their password
- password reset for users
- export data to CSV
- the app is slow on mobile

---

### Example 2 — File-based input with context

/groom-backlog --file ./backlog/q3-raw-items.txt --persona "B2B SaaS platform for HR managers"

(Claude will read the file, apply the B2B HR manager persona context when inferring user roles, and produce the full groomed output.)

---

### Example 3 — Single item deep-groom

/groom-backlog

Item: "notifications"

(Claude will recognize this is severely underspecified, write the most reasonable user story shell it can, mark multiple acceptance criteria as [NEEDS CLARIFICATION], and generate a full PO Clarification Queue before this item can move forward.)

---

## Notes for Claude

- If the user provides zero context about their product domain, ask one clarifying question before starting: "What type of product or platform are these backlog items for? This helps write accurate user roles and acceptance criteria."
- If the input contains more than 20 items, process them all but note in the summary that a live refinement session is recommended to review the full output with the team.
- If the user asks you to skip any step, confirm the skip but warn them which downstream quality checks will be affected.
- This skill pairs directly with `/estimate-stories` (for sizing the groomed output) and `/write-sprint-goal` (for synthesizing a goal from the groomed stories).