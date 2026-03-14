---
name: risk-blocker-escalation
trigger: /escalate-risks
description: >
  Transforms a raw list of risks or blockers into a structured escalation memo
  complete with impact assessment, urgency classification, owner assignments,
  and recommended mitigations. Use this skill whenever risks or blockers need
  to be surfaced to stakeholders, leadership, or cross-functional teams in a
  clear, actionable format that drives decisions rather than just reporting
  problems.
when_to_use: >
  Use /escalate-risks when you have one or more risks or blockers that require
  visibility beyond the immediate team — for example, before a steering
  committee meeting, when a blocker is threatening a milestone, when a risk
  has escalated in severity, or when you need a paper trail for accountability
  and follow-up.
---

# Skill: Risk & Blocker Escalation Memo

## Purpose

Convert raw risk and blocker information into a polished escalation memo that
gives recipients exactly what they need: what is at stake, how urgent it is,
who owns it, and what should happen next. The output should be ready to send
with minimal editing.

---

## How to Execute This Skill

Follow these steps in order every time `/escalate-risks` is invoked.

### Step 1 — Gather Input

Collect the raw information the user provides. This may arrive as:

- A bullet list of risks or blockers pasted inline
- A description of a single critical blocker
- A mix of technical and process risks in rough notes
- References to tickets, Jira issues, or project documents in the workspace

If the user provides no input at all, ask for it before proceeding:
> "Please share the risks or blockers you want to escalate. A rough bullet list
> is fine — I'll structure everything from there."

### Step 2 — Parse and Classify Each Risk or Blocker

For each item identified, extract or infer:

- **Title**: A short, plain-language label (≤10 words)
- **Description**: What is happening and why it is a problem (2–4 sentences)
- **Category**: Choose one — Technical / Resource / Dependency / Process /
  External / Compliance
- **Impact**: What breaks, slips, or degrades if this is not resolved. Be
  specific about affected milestones, teams, customers, or revenue where
  possible.
- **Urgency Level**: Assign one of the following tiers based on the timeline
  to impact:
  - 🔴 **Critical** — Impact materialises within 24–48 hours or is already
    occurring; escalation required immediately
  - 🟠 **High** — Impact materialises within the current sprint or week;
    decision needed within 1–2 days
  - 🟡 **Medium** — Impact materialises within 2–4 weeks; action needed this
    sprint
  - 🟢 **Low** — Impact is possible but not imminent; monitor and plan
- **Blast Radius**: Who or what is affected (team names, systems, downstream
  dependencies, customers)
- **Proposed Owner**: The person or role best positioned to resolve or
  unblock this item. If the user has not specified an owner, infer from
  context or flag as "Owner: TBD — assign before sending"
- **Recommended Mitigation**: One primary action and, where helpful, a
  fallback or contingency option

### Step 3 — Sort by Urgency

Order all items in the memo from most urgent to least urgent (Critical →
High → Medium → Low). Within the same urgency tier, place items with the
broadest blast radius first.

### Step 4 — Write the Escalation Memo

Produce the memo using the exact structure below. Do not omit sections or
reorder them.

---

**ESCALATION MEMO**
**To:** [Recipient — ask user if not provided, or default to "Project
Steering Committee"]
**From:** [Author — use name/role if provided, otherwise leave as "[Your
Name / Role]"]
**Date:** [Today's date — use file metadata or ask if unavailable]
**Project:** [Project name — infer from context or ask]
**Re:** Risk & Blocker Escalation — [Sprint / Week / Date Range]

---

**SUMMARY**

[2–4 sentence overview. State the total number of items being escalated, the
highest urgency level present, and the single most critical item requiring
immediate action. Keep this paragraph decision-maker-ready — no jargon.]

---

**ESCALATION ITEMS**

Repeat the following block for each risk or blocker:

---

### [#] [Urgency Emoji] [Title]

| Field | Detail |
|---|---|
| **Category** | [Category] |
| **Urgency** | [Urgency Level] |
| **Blast Radius** | [Affected teams / systems / customers] |
| **Owner** | [Name or Role] |
| **Decision / Action Needed By** | [Date or "Immediately"] |

**What Is Happening**
[2–4 sentences describing the risk or blocker factually and specifically.]

**Impact If Not Resolved**
[2–3 sentences describing the concrete consequence — milestone slip, system
failure, customer impact, cost, compliance breach, etc.]

**Recommended Mitigation**
- **Primary:** [Specific action, who does it, target date]
- **Contingency:** [Fallback if primary is not feasible — omit if not
  applicable]

---

[Repeat block for each item]

---

**DECISIONS REQUESTED**

[Bulleted list of the specific decisions or approvals the escalation memo is
asking recipients to make. Each bullet should be one clear, answerable
question or action item. Example: "Approve unblocking budget of $X for
third-party vendor" or "Assign dedicated QA resource to Project Y by
Friday."]

---

**NEXT STEPS & FOLLOW-UP**

[Brief table or bullet list showing what happens after this memo is received:
who responds, by when, and what the review cadence is. Example:
- Owner to confirm receipt and initial plan by [date]
- Escalation review meeting: [date/time]
- Updated status in next weekly report: [date]]

---

### Step 5 — Post-Memo Quality Check

Before delivering the output, verify each of the following. If any check
fails, revise before presenting:

- [ ] Every item has a named or explicitly flagged (TBD) owner
- [ ] Every urgency level is justified by a concrete timeline to impact
- [ ] No item is described only in jargon or acronyms without explanation
- [ ] The Summary paragraph can be read in isolation by someone with no
  project context and still communicate the key risk
- [ ] "Decisions Requested" contains at least one item
- [ ] No mitigation recommendation is vague (e.g., "investigate further" is
  not acceptable without specifying who investigates and by when)

### Step 6 — Offer Follow-On Actions

After delivering the memo, offer the following options:

> **What would you like to do next?**
> - **A** — Export this as a plain-text email draft
> - **B** — Generate a one-slide executive summary version
> - **C** — Add this escalation to the weekly status report
> - **D** — Adjust urgency levels or owner assignments

---

## Constraints and Quality Rules

- **Tone**: Professional, direct, and neutral. Do not editorialize, assign
  blame, or use alarmist language. State facts and consequences only.
- **Length per item**: Each escalation block should be concise. Aim for
  completeness over brevity, but avoid padding. A well-scoped item should
  need no more than 200 words in its description and impact fields combined.
- **Urgency discipline**: Do not default everything to Critical or High.
  Urgency must be earned by a real, specific timeline. If everything is
  Critical, nothing is.
- **Owner assignment**: Every item must have an owner or be explicitly flagged
  as needing one. An ownerless escalation item is not actionable.
- **Mitigation specificity**: Mitigations must name an action, a responsible
  party, and a target date or timeframe. "Monitor the situation" is never an
  acceptable primary mitigation.
- **No fabrication**: If project names, owners, or dates are not provided and
  cannot be inferred from workspace files, leave them as clearly marked
  placeholders rather than inventing plausible-sounding details.
- **Audience calibration**: The Summary and Decisions Requested sections must
  be readable by a non-technical executive. Technical detail belongs in the
  individual item blocks.

---

## Usage Examples

### Example 1 — Quick inline list

/escalate-risks

Blockers this week:
- API vendor hasn't delivered credentials, integration testing is blocked
- Two senior devs out sick, sprint velocity is at 40%
- Legal hasn't signed off on the data processing agreement, can't go live in
  EU region

Sending to the steering committee Thursday.

---

### Example 2 — Single critical blocker with partial details

/escalate-risks

We have a critical blocker: the production database migration script is
failing in staging with data integrity errors. Launch is in 6 days.
Owner should be Priya (DB lead). We don't have a contingency yet.

---

### Example 3 — Risk register with mixed severities

/escalate-risks

Escalating risks from the Q3 risk register for the exec briefing:
- Third-party analytics SDK has an unpatched CVE — compliance team flagged it
- Scope creep on the reporting module is adding ~3 weeks to timeline
- Cloud infrastructure costs are tracking 40% over budget projection
- Key stakeholder in the client organisation is leaving next month, no
  replacement named
- Performance testing hasn't started, launch is in 3 weeks

Recipient: CTO and PMO Director. Project: Atlas Platform Rebuild.