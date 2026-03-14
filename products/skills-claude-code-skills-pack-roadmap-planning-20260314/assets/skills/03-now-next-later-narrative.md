---
name: now-next-later-narrative
trigger: /draft-roadmap
description: >
  Converts a prioritized feature list into a cohesive Now / Next / Later
  roadmap narrative that explains sequencing rationale in plain language
  suitable for both engineering teams and business stakeholders. Use this
  skill whenever you have a ranked or scored feature list and need to
  communicate the "why behind the order" — not just the order itself.
pack: Claude Code Skills Pack — Roadmap Planning (Quarterly Planning & Priority Alignment)
version: 1.0.0
---

# Skill: Now-Next-Later Narrative (`/draft-roadmap`)

## Purpose

Product lists and scoring matrices tell you *what* to build. This skill
produces the narrative layer that tells every audience *why* you are
building things in this sequence, what tradeoffs were made, and what
success looks like at each horizon. The output is a ready-to-share
document, not a rough draft.

---

## When to Use This Skill

- You have a feature list (raw, scored, or partially ordered) and need to
  turn it into a presentable roadmap narrative.
- You are preparing for a quarterly planning meeting, board review, or
  all-hands and need a plain-language explanation of priorities.
- You want a single artifact that works for both a technical audience
  (engineering) and a business audience (leadership, sales, customers).

---

## Inputs Claude Should Expect

The user will provide one or more of the following after the slash command.
If any critical input is missing, ask before proceeding.

| Input | Required | Notes |
|---|---|---|
| Feature list | **Yes** | Can be plain text, bullet list, table, or CSV paste |
| Horizon definitions | No | Defaults: Now = current quarter, Next = next 1–2 quarters, Later = 6–12+ months |
| Strategic theme or goal | No | E.g., "reduce churn," "expand upmarket," "platform stability" |
| Audience emphasis | No | "engineering," "executive," or "mixed" (default: mixed) |
| Constraints or dependencies | No | Known blockers, team capacity notes, external dependencies |

---

## Execution Steps

Follow these steps in order every time `/draft-roadmap` is invoked.

### Step 1 — Parse and Clarify Inputs

1. Read everything the user has provided after the command.
2. Identify the feature list. If items are already scored or ranked, note
   the scoring method.
3. Check for horizon definitions. If absent, use the defaults above and
   state them explicitly at the top of the output.
4. If the feature list contains fewer than 3 items or more than 40 items,
   flag this before proceeding and ask the user to confirm scope.
5. If no strategic theme is provided, infer one from the feature list and
   confirm it with a one-sentence statement before writing the narrative.

### Step 2 — Assign Features to Horizons

Apply the following placement logic. Show your reasoning only if the user
asks; otherwise embed rationale in the narrative prose rather than in a
visible scoring table.

- **Now** — Features that are already in progress, unblock other work,
  address an active customer pain or revenue risk, or have the highest
  combined impact-and-readiness score.
- **Next** — Features that depend on Now work being complete, require
  design or discovery still underway, or represent the next logical step
  toward the strategic theme.
- **Later** — Features that are high-value but early in definition,
  depend on market signals not yet confirmed, require capabilities not yet
  built, or are explicitly lower priority given current constraints.

If a feature could reasonably belong to two horizons, place it in the
earlier one and note the condition that would accelerate or defer it.

### Step 3 — Draft the Narrative Document

Produce the full document using the structure below. Do not skip sections.
Write in clear, confident prose. Avoid jargon unless the user's own inputs
use it.

---

#### Document Structure

**Title**
`[Product / Initiative Name] Roadmap — [Quarter or Date Range]`
If no name is provided, use: `Product Roadmap — [Current Period]`

---

**Strategic Context** *(2–4 sentences)*
State the one or two outcomes the team is optimizing for this period.
Connect the roadmap sequence explicitly to those outcomes. This section
must answer: *"Why are we doing this work in this order?"*

---

**Roadmap at a Glance** *(summary table)*
A compact three-column table for quick scanning.

| Now | Next | Later |
|---|---|---|
| Feature A | Feature D | Feature G |
| Feature B | Feature E | Feature H |
| Feature C | Feature F | Feature I |

---

**Now — [Horizon Label and Timeframe]**

- Opening sentence: what the Now bucket accomplishes collectively.
- One short paragraph per feature or logical cluster of features:
  - What it is (1 sentence, plain language)
  - Why it is prioritized now (dependency, urgency, customer impact)
  - What "done" looks like (success signal, not a full acceptance criteria)
- Closing sentence: how completing Now sets up the Next horizon.

---

**Next — [Horizon Label and Timeframe]**

Same structure as Now. Additionally include:
- Any conditions or milestones from Now that must be true before Next work
  begins.
- One sentence on resource or capacity assumptions if relevant.

---

**Later — [Horizon Label and Timeframe]**

Same structure as Now. Additionally include:
- A brief note on what would pull any Later item earlier (trigger
  conditions).
- A brief note on what would remove an item entirely (invalidating
  assumptions).

---

**What We Are Not Doing (and Why)**
Bullet list of 3–6 items that were considered but deliberately excluded
from all three horizons this period. For each, give a one-line reason.
This section prevents recurring debates and demonstrates rigor.

---

**Open Questions and Risks**
Bullet list of the top 3–5 unresolved questions or risks that could
change the plan. Format each as:
`[Risk / Question]: [Potential impact on roadmap if unresolved]`

---

**How to Read This Roadmap** *(optional, include only for mixed or
executive audiences)*
Two to three sentences explaining that Later does not mean "never," that
the plan is a living document, and who owns decisions to move items
between horizons.

---

### Step 4 — Tone and Style Calibration

Apply the following rules to every sentence in the output.

- **Confidence without false certainty.** Use "we expect," "the goal is,"
  "this positions us to" — not "this will guarantee."
- **Active voice.** Write "shipping X unblocks Y" not "Y is unblocked by X."
- **No filler phrases.** Remove "leverage," "synergy," "best-in-class,"
  "move the needle," and similar buzzwords unless the user's own brief uses
  them.
- **Consistent tense.** Now = present tense. Next and Later = future tense.
- **Audience calibration:**
  - *Engineering emphasis:* include more detail on dependencies,
    technical preconditions, and "done" definitions.
  - *Executive emphasis:* lead with customer and revenue impact; keep
    feature descriptions to one sentence each.
  - *Mixed (default):* balance both; use plain language throughout.

### Step 5 — Final Quality Check

Before outputting, verify:

- [ ] Every feature from the input list appears in exactly one horizon.
- [ ] Strategic Context directly references the overall goal or theme.
- [ ] "What We Are Not Doing" contains at least 3 items.
- [ ] No section is missing from the document structure.
- [ ] The Roadmap at a Glance table matches the features described in the
      narrative sections.
- [ ] The document could be handed to a stakeholder today with no further
      editing required.

---

## Output Format Rules

- Deliver the full document in Markdown.
- Use `##` for horizon headings, `###` for feature sub-sections if needed.
- The Roadmap at a Glance table must appear before the narrative sections.
- Total length: 600–1,200 words for typical inputs (10–20 features).
  Scale up only if the feature list is large and complexity demands it.
- Do not include meta-commentary about the skill or your process in the
  output. Deliver the document only.

---

## Constraints and Hard Rules

1. **Never invent features.** Only work with what the user provides.
   If the list is too thin to fill a horizon, say so and ask for more
   input rather than padding.
2. **Never assign a feature to a horizon without a stated rationale.**
   The rationale may live in the narrative prose, but it must be present.
3. **Do not produce a timeline or Gantt chart.** This skill produces
   narrative and horizon buckets, not dates or sprints.
4. **Do not include effort estimates** unless the user explicitly provides
   them. Do not infer T-shirt sizes or story points.
5. **Keep the "What We Are Not Doing" section honest.** Only list items
   that appeared in the user's input or that were clearly implied by the
   strategic context. Do not fabricate exclusions.

---

## Usage Examples

### Example 1 — Basic feature list, default settings

/draft-roadmap

Strategic goal: reduce time-to-value for new users

Feature list (already scored, higher = higher priority):
- Onboarding checklist (92)
- SSO / SAML support (88)
- In-app tooltip guidance (85)
- Bulk CSV import (79)
- Admin audit log (74)
- Public API v2 (68)
- Custom roles and permissions (61)
- White-label branding (44)
- Offline mode (38)
- Native mobile app (31)

*Claude will infer Now/Next/Later from scores and the stated goal, confirm
the strategic theme, and produce the full narrative document.*

---

### Example 2 — Explicit horizons and engineering audience

/draft-roadmap audience=engineering

Now (Q3): Payment retry logic, Webhook reliability fixes, Rate limiting on API
Next (Q4): Multi-currency support, Invoice PDF generation, Usage-based billing
Later (H1 next year): Revenue recognition reporting, Dunning workflow builder, Tax automation

Constraints: Payment retry depends on infra team completing queue migration by end of August. Multi-currency needs new FX rate service — discovery starts Q3.

*Claude will produce a technically detailed narrative that calls out the
queue migration dependency explicitly and frames Later triggers around
the FX service readiness.*

---

### Example 3 — Minimal input, mixed audience, name provided

/draft-roadmap

Product: Aria Analytics
Goal: expand into mid-market accounts
Features to prioritize this quarter: role-based dashboards, data export,
embedded reporting, custom alerts, team workspaces, API access,
white-label option, SOC 2 certification, SLA reporting, audit trails

*Claude will ask to confirm the inferred strategic theme, then assign
features to horizons based on typical mid-market expansion sequencing
(compliance and access controls early, customization later), and produce
the full document.*

---

## Notes for Skill Maintainers

- The horizon timeframe defaults (Now = current quarter, Next = 1–2
  quarters, Later = 6–12+ months) can be overridden per invocation by
  the user. If your team uses different labels (e.g., "This Sprint /
  This Half / Future"), add that to the user's prompt.
- This skill pairs naturally with `prioritization-matrix` (for scoring
  inputs) and `board-roadmap-presentation` (for converting this narrative
  into slide-ready content) from the same pack.