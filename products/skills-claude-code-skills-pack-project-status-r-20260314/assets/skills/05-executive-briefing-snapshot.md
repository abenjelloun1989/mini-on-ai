---
name: Executive Briefing Snapshot
trigger: /exec-briefing
description: >
  Distills full project status details into a concise executive briefing snapshot
  for senior leadership and non-technical stakeholders. Produces three to five
  tightly written bullet points covering overall project health, key wins, top
  risks, and any immediate decisions or actions required from leadership.
  Use this skill when you need to communicate project status upward quickly,
  prepare for a steering committee, or give an executive sponsor a fast read
  before a meeting.
tags: [reporting, executive, stakeholder-communication, status, risk]
---

# Executive Briefing Snapshot

## Purpose

Generate a crisp, senior-leadership-ready briefing from raw project status
information. Executives do not need every detail — they need signal. This skill
filters noise, surfaces what matters most, and frames it in language that
supports fast decision-making.

---

## When to Use

- Before a steering committee, board update, or executive sponsor check-in
- When a senior stakeholder asks "what's the status in two minutes or less?"
- As the final step after running `/weekly-status` or `/rag-status` to produce
  an upward-facing summary
- When a project has a critical risk or blocker that needs to reach leadership
  immediately

---

## How Claude Should Execute This Skill

Follow these steps in order every time `/exec-briefing` is invoked.

### Step 1 — Gather Input

Collect all available project context from:

1. Any text, notes, or status details the user pastes directly into the prompt
2. Files mentioned or attached (status reports, JIRA exports, meeting notes,
   risk logs, milestone trackers, prior briefings)
3. Answers to clarifying questions if critical context is missing (see Step 2)

If the user provides no input at all, ask one consolidated question before
proceeding:

> "Please share the current project status — this can be rough notes, a prior
> report, bullet points, or a file. Also let me know the project name, the
> briefing date, and the audience if possible."

Do not ask multiple rounds of clarifying questions. Ask once, then proceed with
whatever is provided.

### Step 2 — Identify the Four Signal Categories

Before writing, mentally sort all available information into these four
categories. Every bullet in the final output must map to at least one:

| Category | What belongs here |
|---|---|
| **Overall Health** | RAG status, schedule position, budget position, team capacity, general trajectory |
| **Key Wins** | Milestones hit, deliverables shipped, risks retired, stakeholder approvals received |
| **Top Risks** | Active blockers, unresolved dependencies, slippage threats, resource gaps, open decisions causing delay |
| **Immediate Asks** | Decisions, approvals, escalations, or introductions needed from the executive audience right now |

If a category has nothing meaningful to report, omit it rather than padding with
filler. Every bullet must earn its place.

### Step 3 — Write the Briefing

Produce the briefing using the exact output format specified below. Apply all
quality rules before finalising.

### Step 4 — Offer a Follow-On

After delivering the briefing, offer one short follow-on line:

> "Let me know if you'd like a version formatted for email, a slide title block,
> or a spoken two-minute read-aloud script."

---

## Output Format

Use this structure exactly. Do not add sections, headings, or narrative prose
outside of it.

---

**EXECUTIVE BRIEFING SNAPSHOT**
**Project:** [Project Name]
**Date:** [Briefing Date]
**Prepared for:** [Audience — e.g., Executive Sponsor, Steering Committee]

---

• [Bullet 1]
• [Bullet 2]
• [Bullet 3]
• [Bullet 4 — include only if material content warrants it]
• [Bullet 5 — include only if material content warrants it]

---

**Bottom line:** [One sentence. State the single most important thing the
executive needs to know or do right now.]

---

## Bullet Writing Rules

Apply every rule to every bullet without exception.

**Length:** Each bullet must be 25 words or fewer. If you cannot say it in 25
words, the thinking is not clear enough yet — sharpen it.

**Structure:** Lead with the most important word or phrase. Put the "so what"
before the "how." Example: "Launch on track — all five integration tests passed
this week, final UAT begins Monday."

**Voice:** Active, direct, declarative. No passive constructions. No hedging
phrases like "it appears" or "it seems." No filler like "please note that."

**Numbers over adjectives:** Write "14 of 16 milestones complete" not "most
milestones complete." Write "three weeks behind schedule" not "significantly
delayed."

**No jargon without definition:** If a technical term is unavoidable, add a
two-word gloss in parentheses. Assume the reader is a business executive, not
an engineer.

**Asks must be specific:** An "Immediate Ask" bullet must name who needs to do
what by when. Vague asks ("leadership support needed") are not permitted.

**RAG colour coding:** If RAG status is known, include it in the Overall Health
bullet as a plain-English label: Green (on track), Amber (at risk), or Red
(critical issue). Never use colour alone without the label.

---

## Quality Checklist

Before delivering output, verify every item:

- [ ] Three to five bullets total — not fewer, not more (unless a category
      genuinely has nothing to report)
- [ ] Each bullet is 25 words or fewer
- [ ] Every bullet maps to one of the four signal categories
- [ ] The Bottom Line sentence is one sentence, action-oriented, and unambiguous
- [ ] No passive voice in any bullet
- [ ] All numbers are specific, not qualitative
- [ ] Any "Immediate Ask" names a person, action, and deadline
- [ ] No internal acronyms or project-specific shorthand without a gloss
- [ ] The briefing could be read aloud in under 60 seconds

---

## Usage Examples

### Example 1 — From Pasted Notes

/exec-briefing

Here's our current status for the Orion platform migration:
- We're 3 weeks into a 12-week programme
- Phase 1 data migration completed on time last Friday
- Cloud infra provisioning is blocked — security review hasn't started yet,
  owner is Sam Chen's team, we need sign-off by end of week or Phase 2 slips
- Budget is tracking 8% under forecast
- Team morale is good, no attrition
- Next milestone is Phase 2 kick-off, currently scheduled for Monday
Audience: CTO and CFO pre-read for Thursday's steering committee.

---

### Example 2 — From an Attached Status Report

/exec-briefing project-status-week-14.md

Audience is the CEO. She has two minutes max. Focus on the delivery risk and
the vendor contract decision she needs to make.

---

### Example 3 — Minimal Input, Fast Turnaround

/exec-briefing

Project Phoenix. We're red. Demo to the client is in 10 days and the API
integration is broken. We need the VP of Engineering to unblock the vendor
escalation today. Everything else is fine.

---

## Constraints and Guardrails

- **Never inflate status.** If the project is Red, say Red. Do not soften
  language to protect feelings or avoid uncomfortable conversations.
- **Never invent data.** If a number is not in the provided context, do not
  estimate it. Either ask for it or note it as "data not provided."
- **Confidentiality:** Do not include individual performance commentary,
  compensation details, or HR matters in the briefing output.
- **No recommendations beyond the asks.** This skill surfaces information and
  frames decisions — it does not prescribe strategy unless the user explicitly
  requests it.
- **Length discipline is non-negotiable.** If you find yourself wanting to add
  a sixth bullet, a paragraph of context, or a table, you are writing a status
  report, not an executive briefing. Use `/weekly-status` for that instead.