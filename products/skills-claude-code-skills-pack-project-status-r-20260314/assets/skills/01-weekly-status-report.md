---
name: weekly-status-report
trigger: /weekly-status
description: >
  Compiles accomplishments, in-progress work, and next-week plans from raw
  notes, ticket data, or freeform input into a polished, formatted weekly
  status report ready to send to stakeholders. Use this skill at the end of
  each sprint or work week when you need to communicate team progress without
  spending time on manual write-ups.
tags:
  - reporting
  - stakeholder-communication
  - project-management
version: 1.0.0
---

# Weekly Status Report Skill

## Purpose

Transform raw project data — jira exports, bullet-point notes, Slack summaries, commit logs, or verbal brain-dumps — into a clean, professional weekly status report. The output is stakeholder-ready: structured, scannable, and free of internal jargon.

## When to Use

- End of sprint or work week wrap-ups
- Regular cadence updates to leadership, clients, or cross-functional partners
- When you have scattered notes that need to become a coherent narrative
- Any time you want a consistent, repeatable status report format without manual formatting effort

---

## Execution Instructions

Follow these steps precisely every time `/weekly-status` is invoked.

### Step 1 — Gather Input

Prompt the user for source material if not already provided in the command. Ask for any combination of:

- Raw bullet notes from the week
- Ticket/issue data (Jira, Linear, GitHub Issues, Asana exports)
- Previous week's report (for continuity)
- Team name or project name
- Reporting period (default to "current week" if not stated)
- Intended audience (engineering team, exec leadership, client, etc.)
- Any known risks, blockers, or escalations to highlight

If the user provides material inline with the command, proceed directly to Step 2 without asking follow-up questions unless critical information is missing.

### Step 2 — Analyze and Categorize

Parse all provided input and sort every item into one of five buckets:

1. **Completed This Week** — work that reached done/shipped/closed status
2. **In Progress** — actively being worked, partially complete, or in review
3. **Planned for Next Week** — committed work starting in the coming week
4. **Risks and Blockers** — anything that could slow or stop progress
5. **Decisions Needed / Asks** — items requiring stakeholder input or approval

Apply these rules during categorization:

- Merge duplicate or overlapping items into single, clear statements
- Strip ticket IDs from the prose unless the audience is technical (keep them as parenthetical references only, e.g., "Deployed auth service (PROJ-412)")
- Elevate impact language: prefer "Shipped user onboarding flow, reducing drop-off path by 2 steps" over "Closed PROJ-399"
- Flag anything mentioned as blocked, at-risk, or delayed and move it to bucket 4
- If the audience is executive or client-facing, remove implementation details; if technical, preserve them

### Step 3 — Draft the Report

Produce the report using the exact structure below. Do not skip sections; write "None this week" if a section is empty.

---

**WEEKLY STATUS REPORT**
**Project / Team:** [name]
**Reporting Period:** [Week of Month DD, YYYY]
**Prepared by:** [name or "Team" if not specified]
**Audience:** [e.g., Engineering Leadership / Client / Exec Team]

---

**SUMMARY**

Two to four sentences. State the overall health of the week in plain language. Mention the single biggest win and any significant concern. This paragraph should stand alone — a reader who reads only this section should understand the week.

---

**ACCOMPLISHED THIS WEEK**

Bulleted list. Each item is one clear sentence starting with a past-tense action verb (Shipped, Completed, Resolved, Merged, Deployed, Finalized, Closed). Include measurable outcomes where possible.

- [Achievement 1]
- [Achievement 2]
- [Achievement 3]

---

**IN PROGRESS**

Bulleted list. Each item names the work, its current state, and an expected completion or next milestone.

- [Work item] — [current state], targeting [date or milestone]
- [Work item] — [current state], targeting [date or milestone]

---

**PLANNED FOR NEXT WEEK**

Bulleted list of committed work starting in the coming week. Prioritize by importance.

- [Planned item 1]
- [Planned item 2]
- [Planned item 3]

---

**RISKS AND BLOCKERS**

Use a simple table for clarity. If none, write "None this week."

| Item | Impact | Owner | Status |
|------|--------|-------|--------|
| [Risk or blocker] | [High / Medium / Low] | [Person or team] | [Blocked / Monitoring / Escalated] |

---

**DECISIONS NEEDED / ASKS**

Bulleted list of specific requests to the reader. Be direct: state what is needed, who needs to act, and by when if time-sensitive.

- [Ask 1]
- [Ask 2]

---

**METRICS (optional)**

Include only if the user provides quantitative data. Use a table.

| Metric | This Week | Last Week | Target |
|--------|-----------|-----------|--------|
| [Metric name] | [value] | [value] | [value] |

---

### Step 4 — Tone and Style Calibration

Adjust the language register based on audience:

- **Exec / Leadership:** High-level, outcome-focused, no acronyms without expansion, no ticket IDs in body text, lead with business impact
- **Client-facing:** Professional, confident, avoid internal tool names and jargon, frame risks constructively
- **Engineering team:** Technical detail welcome, ticket references acceptable, precise and direct
- **Default (unspecified):** Professional but accessible, moderate detail, outcome-focused

### Step 5 — Quality Check

Before delivering the report, verify:

- [ ] Every bullet starts with an action verb or a noun phrase (no "we did" or "the team worked on")
- [ ] The Summary section is self-contained and could be forwarded on its own
- [ ] No section is missing (each has content or explicit "None this week")
- [ ] Risks table has at least an owner and impact level for every row
- [ ] Dates use a consistent format (Month DD, YYYY or Week of...)
- [ ] Report reads cleanly without the source material — no raw ticket dumps, no unformatted paste artifacts
- [ ] Total length is appropriate: 300–600 words for exec audiences, up to 800 words for technical audiences

### Step 6 — Deliver and Offer Refinement

Output the completed report. Immediately after the report, add a brief line:

> *To adjust tone, expand any section, add metrics, or reformat for a specific tool (Confluence, Notion, email), just ask.*

---

## Constraints and Rules

- **Never fabricate data.** If information is missing, leave a bracketed placeholder like `[owner TBD]` or ask the user for the missing detail rather than inventing it.
- **Do not include internal commentary** or meta-notes inside the report output itself. Keep the deliverable clean.
- **Preserve confidentiality signals.** If the user marks anything as sensitive or internal-only, do not include it in client-facing versions and flag it explicitly.
- **Maintain section order.** Do not reorder the report structure even if some sections are sparse.
- **One report per invocation** unless the user explicitly asks for multiple audience variants.

---

## Usage Examples

### Example 1 — From Raw Notes

/weekly-status

Team: Platform Engineering
Week: June 9–13
Audience: Engineering Director

Notes:
- Finished the database migration for tenant isolation, took longer than expected but done
- Still working on the API rate limiting feature, about 70% done, should ship Tuesday
- Started oncall runbook updates, not done yet
- Deploy pipeline broke Thursday morning, fixed by noon, no customer impact
- Need approval on the Q3 infra budget proposal before end of month
- Redis upgrade blocked waiting on security sign-off

---

### Example 2 — From Ticket Export

/weekly-status Project: Mobile App | Audience: Client (Acme Corp) | Period: Week of June 9

Closed tickets: MOBI-88 login bug fix, MOBI-91 push notification redesign shipped to staging, MOBI-94 accessibility audit completed
In progress: MOBI-97 dark mode (50%), MOBI-99 performance profiling (just started)
Next: MOBI-100 App Store submission prep, MOBI-101 beta tester feedback review
Blocker: MOBI-97 waiting on final design assets from client design team

---

### Example 3 — Minimal Input with Audience Escalation

/weekly-status

Here's my messy notes from this week — please turn into an exec summary for our VP:
shipped v2.1 hotfix for the checkout crash affecting 3% of users. onboarding redesign is in QA. two engineers out sick so sprint velocity was down. next week finishing onboarding and starting the referral program feature. no major blockers but the third-party SMS provider has been flaky, watching it.