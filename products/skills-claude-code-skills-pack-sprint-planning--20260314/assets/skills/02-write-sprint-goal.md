---
name: write-sprint-goal
trigger: /write-sprint-goal
description: Synthesizes selected sprint stories into a concise, outcome-focused sprint goal statement aligned to business objectives, along with a one-paragraph rationale for stakeholder communication.
tags: [agile, sprint-planning, scrum, backlog, ceremonies]
version: 1.0.0
---

# Skill: Write Sprint Goal

## Purpose

Use this skill when you have a set of sprint stories selected and need to articulate a clear, outcome-focused sprint goal that unifies the work, communicates business value, and gives the team a shared definition of sprint success. This skill is designed for scrum masters, agile coaches, and team leads preparing for or running sprint planning ceremonies.

Run this skill after backlog grooming and story selection, before or during the sprint planning meeting. It produces two deliverables: a crisp sprint goal statement and a stakeholder-facing rationale paragraph.

---

## How to Execute This Skill

When the `/write-sprint-goal` command is invoked, follow these steps precisely:

### Step 1 — Gather Input

Identify the sprint stories to synthesize. Accept input in any of these forms:
- A pasted list of story titles, descriptions, or acceptance criteria provided inline
- A numbered or bulleted list of user stories in standard format ("As a [user], I want [action], so that [outcome]")
- A mix of story IDs with brief descriptions
- A free-form description of the sprint's planned work

If no stories are provided with the command, immediately ask the user:

> "Please share the stories selected for this sprint. You can paste titles, user stories, or a brief description of each. Also let me know the broader business objective or product theme this sprint is meant to advance, if you have one."

Do not proceed until you have at least a basic picture of the sprint's intended work.

### Step 2 — Extract Themes and Outcomes

Analyze the provided stories and identify:
- The **primary user or customer segment** most affected by this sprint's work
- The **core capability or improvement** being delivered (what will be true after this sprint that wasn't before)
- The **business or product objective** the work advances (e.g., retention, onboarding, performance, revenue, compliance)
- Any **secondary themes** present across multiple stories
- Stories that are **enabling work** (technical debt, infrastructure) versus **user-facing outcomes**

Prioritize user-facing outcomes when crafting the goal. If the sprint is primarily technical, frame the goal around the capability or risk mitigation it enables.

### Step 3 — Draft the Sprint Goal Statement

Write a sprint goal that meets ALL of the following criteria:

**Content rules:**
- Focuses on the **outcome or capability delivered**, not a list of features shipped
- Names the **beneficiary** (the user, customer, or business function)
- Implies or states **measurable success** where possible
- Connects to a **business objective** without being vague or generic
- Stands on its own — a stakeholder who hasn't read the stories should understand why this sprint matters

**Format rules:**
- One sentence, two sentences maximum
- 15–35 words
- Written in plain language — no jargon, acronyms, or internal ticket references
- Present tense or near-future framing ("By end of sprint, [users] can..." or "We enable [users] to...")
- Must NOT be a task list ("We will build X, fix Y, and add Z")
- Must NOT be a vague platitude ("Improve user experience" or "Deliver value to customers")

**Bad examples to avoid:**
- "Complete tickets AUTH-12, AUTH-13, DASH-04, and DASH-05." ← task list, not a goal
- "Make the product better for users." ← meaningless
- "Finish authentication work and start on the dashboard." ← describes work, not outcome

**Good example pattern:**
- "Enable new customers to complete account setup without contacting support, reducing onboarding friction and support ticket volume."

### Step 4 — Write the Stakeholder Rationale Paragraph

After the sprint goal, write a single paragraph (4–6 sentences) that:
- Restates the goal in context
- Briefly describes the stories included and how they connect to the goal
- Explains the business case — why this work matters now
- Names any risk, dependency, or strategic priority this sprint addresses
- Is written for a non-technical stakeholder (product owner, executive sponsor, business partner) who will read it in a status update or planning doc

The paragraph should be professional but not stilted. Avoid bullet points. Write in third person or team-inclusive "we" voice consistently throughout.

### Step 5 — Flag Gaps or Risks

After delivering the sprint goal and rationale, add a brief **Flags** section if any of the following are true:
- Stories in the sprint appear to span multiple unrelated themes (goal coherence risk)
- No clear user-facing outcome was identifiable — the sprint appears to be entirely technical
- The sprint seems overloaded with work that a single goal cannot honestly represent
- A business objective was not provided and could not be inferred — note what additional context would improve the goal

Format flags as a short bulleted list under a `> ⚑ Flags` blockquote. If no flags exist, omit the section entirely.

### Step 6 — Offer Iteration

After delivering the outputs, ask:

> "Would you like me to adjust the tone, reframe around a different business objective, or generate 2–3 alternative sprint goal options to choose from?"

---

## Output Format

Deliver the skill output in this exact structure:

---

**Sprint Goal**

[One to two sentence sprint goal statement]

---

**Stakeholder Rationale**

[One paragraph, 4–6 sentences]

---

> ⚑ Flags *(if applicable)*
> - [Flag 1]
> - [Flag 2]

---

Do not add headers beyond what is specified. Do not include the story list back in the output unless the user asks for a summary table. Keep the output scannable and copy-paste ready for a planning doc or slide.

---

## Constraints and Quality Rules

- Never fabricate business context that wasn't provided. If you don't know the business objective, say so and ask, or note the assumption you are making explicitly.
- Do not write a sprint goal that is simply the name of an epic or feature ("Complete the Checkout Redesign"). Goals must describe outcomes for people.
- If the user provides only one or two stories, note that a sprint goal is most meaningful with a fuller picture of sprint scope, but proceed with what is available.
- Avoid passive voice in the sprint goal statement. Use active, direct construction.
- The rationale paragraph must remain distinct from the goal — do not restate the goal sentence verbatim as the paragraph opener.
- Do not include story point totals, velocity references, or capacity data in the goal or rationale unless the user explicitly requests it.

---

## Usage Examples

### Example 1 — Full story list provided

/write-sprint-goal

Stories selected for Sprint 24:
- As a new user, I want to verify my email at signup so my account is secure
- As a new user, I want to complete my profile in fewer than 3 steps so I can get started quickly
- As a new user, I want to receive a welcome email with next steps so I know what to do after signing up
- As an admin, I want to see which users have not completed onboarding so I can follow up
Business objective: Improve new user activation rate

---

### Example 2 — Story titles only, no business context

/write-sprint-goal

Sprint stories:
- Payment retry logic on failed transactions
- Email notification for failed payments
- Dunning management flow for overdue accounts
- Internal dashboard: overdue account view

---

### Example 3 — Mixed technical and user-facing work, with a note

/write-sprint-goal

Sprint 11 scope:
- Migrate authentication service to new identity provider
- Update API token expiration logic
- User-facing: "Remember me" persistent login feature
- Performance: reduce login page load time by 40%
- Security audit findings: remediate 3 medium-severity issues

Goal we're loosely aiming for: make login faster and more secure without disrupting current users