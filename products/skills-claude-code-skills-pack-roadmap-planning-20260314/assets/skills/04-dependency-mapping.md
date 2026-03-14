---
name: dependency-mapping
trigger: /map-dependencies
description: Analyzes a set of planned initiatives and generates structured dependency mapping notes that surface blockers, sequencing constraints, and cross-team handoffs before they derail execution. Use this skill when you have a list of planned features, projects, or initiatives and need to understand what must happen before what, who needs to hand off to whom, and where hidden blockers are lurking. Best used after initial feature ideation and before committing to a quarterly roadmap timeline.
---

# Dependency Mapping Skill

## Purpose

This skill transforms a raw list of planned initiatives into a structured dependency map that gives product managers and engineering leads a clear picture of sequencing constraints, cross-team handoffs, and potential blockers — before those issues surface mid-sprint and derail execution.

The output is a set of dependency mapping notes that can be shared with stakeholders, fed into sprint planning, or used to pressure-test a quarterly roadmap narrative.

---

## When to Use This Skill

- You have 3 or more initiatives planned for an upcoming quarter and need to sequence them
- You suspect some work is blocked by other work but haven't mapped it explicitly
- You are preparing a roadmap presentation and need to justify sequencing decisions
- You've identified cross-team dependencies informally and want to formalize them
- A planning meeting is coming up and you want to walk in with a defensible execution order

---

## How to Invoke

/map-dependencies [paste your initiative list or describe your planned work]

You can provide input as:
- A bulleted list of initiative names
- A rough feature backlog
- A paragraph describing planned work
- A mix of initiative names with brief context notes

The more context you provide per initiative (owning team, rough scope, known dependencies), the more precise the output. If context is sparse, Claude will flag assumptions explicitly.

---

## Execution Instructions

When this skill is triggered, follow these steps in order:

### Step 1 — Parse and Normalize the Initiative List

Read the provided input and extract each distinct initiative. Assign each a short reference label (e.g., I-1, I-2, I-3) for use throughout the dependency map. If initiative names are ambiguous or overlapping, note this and ask for clarification before proceeding — do not silently merge or split initiatives.

List the normalized initiatives at the top of your output under a section called **Initiatives Identified** so the user can confirm you've parsed their input correctly.

### Step 2 — Identify Dependency Types

For each initiative, analyze the input and apply your knowledge of common product and engineering dependencies to identify relationships. Classify each dependency using exactly one of these four types:

- **Technical Dependency** — Initiative B cannot be built until Initiative A delivers a specific technical component (API, data model, infrastructure, auth layer, etc.)
- **Data Dependency** — Initiative B requires data that Initiative A will produce, instrument, or migrate
- **Team/Resource Dependency** — Initiative B requires work, review, approval, or a handoff from a team that is also responsible for Initiative A
- **Sequencing Constraint** — Initiative B will be significantly harder, riskier, or more expensive to execute if Initiative A has not been completed first, even if B is technically possible without A

If a dependency fits multiple types, list the primary type and note the secondary type in parentheses.

### Step 3 — Build the Dependency Map

Produce a dependency map structured as follows for each identified dependency relationship:

**From:** [Initiative label and name]
**To:** [Initiative label and name]
**Dependency Type:** [one of the four types above]
**Description:** One to two sentences explaining specifically what must be delivered, decided, or handed off, and why the receiving initiative is blocked or constrained without it.
**Blocking Severity:** Rate as Critical / High / Medium using the criteria below:
  - Critical — work on the downstream initiative cannot begin at all without this
  - High — work can begin but a key milestone or launch will be blocked
  - Medium — work can proceed but will require rework, workarounds, or coordination overhead
**Recommended Action:** One concrete action the team should take to manage or resolve this dependency (e.g., "Schedule API contract review with Platform team by end of Week 2," "Confirm data schema before beginning Initiative B instrumentation")

Repeat this block for every dependency pair identified. If no dependency exists between two initiatives, do not manufacture one.

### Step 4 — Produce a Sequencing Summary

After the full dependency map, write a **Sequencing Summary** section. This section should:

- Recommend a logical execution order for the initiatives based on the dependencies identified
- Group initiatives into sequencing tiers where appropriate (e.g., Tier 1: must start first, Tier 2: can begin once Tier 1 milestones are hit, Tier 3: can proceed in parallel or after Tier 2)
- Call out any circular dependencies explicitly — if Initiative A depends on B and B depends on A, surface this as a planning risk and suggest how to break the loop
- Note any initiatives that are fully independent and can be safely parallelized

Keep this section concise — 150 to 300 words. It should be skimmable in a planning meeting.

### Step 5 — Surface the Top Blockers

Write a **Top Blockers to Resolve Now** section that lists the three to five most urgent dependency issues requiring immediate attention. Format each as a one-line action item with an owner placeholder in brackets. This section is designed to be dropped directly into a planning doc or shared in Slack.

Example format:
- Confirm auth service API contract with [Platform Team] before Initiative B design begins
- Resolve data schema ownership between [Data Eng] and [Backend] for Initiative D migration
- Identify whether [DevOps] capacity exists to support Initiative A infrastructure work in Q1

### Step 6 — Flag Assumptions and Gaps

Close with an **Assumptions and Gaps** section. List any places where you made an assumption due to missing information, and any questions the user should answer to make the dependency map more accurate. Be direct — if the input was too sparse to produce a reliable map, say so and specify exactly what additional context is needed.

---

## Output Format Rules

- Use Markdown headers and bold labels throughout
- Each dependency block must use the exact field labels specified in Step 3
- Do not use tables — dependency blocks should be written as labeled field lists for readability in planning docs and Notion pages
- The full output should be structured so any section can be extracted and dropped into a separate document independently
- Do not editorialize about whether the initiatives are good ideas — focus entirely on dependency structure and sequencing
- If the initiative list contains fewer than 3 items, ask the user if they want to add more before proceeding, since a map with fewer than 3 nodes rarely surfaces meaningful insight

---

## Quality Rules

- Every dependency you surface must be grounded in something present in the user's input or in a clearly stated assumption — do not invent dependencies to make the output look more thorough
- Blocking Severity ratings must be consistent — if you rate something Critical, the description must explain why work literally cannot proceed without it
- Recommended Actions must be specific and actionable, not generic (not "coordinate with the team" — instead "schedule a 30-minute API contract alignment between [Team A] and [Team B] before the end of sprint 1")
- The Sequencing Summary must logically follow from the dependency map — do not recommend an order that contradicts the dependencies you identified
- If you identify a circular dependency, you must flag it explicitly — never silently resolve it by picking an arbitrary order

---

## Usage Examples

### Example 1 — Early-Stage Quarter Planning

/map-dependencies
Here are our Q2 initiatives:
- Rebuild the onboarding flow (owned by Growth)
- Launch SSO/SAML authentication (owned by Platform)
- Introduce usage-based billing (owned by Revenue Eng)
- Add an admin dashboard for enterprise accounts (owned by Product + Backend)
- Instrument product analytics across core flows (owned by Data)

Expected output: A full dependency map across all five initiatives, with the SSO work likely surfacing as a critical upstream dependency for enterprise admin dashboard, and analytics instrumentation flagged as a sequencing constraint before usage-based billing reporting can be built. Sequencing tiers and top blockers included.

---

### Example 2 — Focused Dependency Check on Two Teams

/map-dependencies
We have three projects landing this quarter that touch the data platform team:
- Real-time recommendation engine (ML team)
- Customer segmentation tool (Product)
- Data warehouse migration from Redshift to BigQuery (Data Eng)

Need to know if the warehouse migration is going to block the other two and in what ways.

Expected output: A targeted dependency map with particular focus on how the warehouse migration creates downstream risk for both the recommendation engine and segmentation tool. Likely surfaces data schema changes and pipeline availability as Critical or High severity blockers. Recommended actions will focus on migration sequencing and freeze windows.

---

### Example 3 — Pressure-Testing a Roadmap Before a Board Review

/map-dependencies
We're presenting our H1 roadmap to the board next week. Want to make sure we haven't missed any dependencies that would embarrass us if a board member asks. Here are the six initiatives:
- API v2 public launch
- Self-serve upgrade flow
- SOC 2 Type II certification
- Mobile app (iOS first)
- Partner integration marketplace
- Automated dunning and payment retry logic

Expected output: A complete dependency map across all six initiatives, with SOC 2 likely flagged as a cross-cutting constraint affecting API v2 public launch and partner marketplace timelines, and payment retry logic surfacing as a prerequisite for the self-serve upgrade flow to be fully functional. Board-ready sequencing summary included. Assumptions section will flag any missing information about team ownership or technical architecture that could affect the map's accuracy.