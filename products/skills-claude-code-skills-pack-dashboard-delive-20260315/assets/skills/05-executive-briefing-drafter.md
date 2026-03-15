---
name: executive-briefing-drafter
trigger: /draft-briefing
description: >
  Assembles a structured executive briefing document from multiple dashboard
  metrics and data inputs. Synthesizes key findings, flags risks, and proposes
  recommended next steps in a format ready for C-suite or senior stakeholder
  consumption. Use this skill whenever you need to convert raw dashboard outputs,
  KPI summaries, or analyst notes into a polished, narrative-driven briefing
  document — without manual write-up effort.
when_to_use: >
  Invoke this skill when you have a collection of metrics, KPIs, or dashboard
  screenshots/exports and need to produce a board-ready or exec-ready briefing.
  Best used at end-of-week, end-of-sprint, or ahead of a business review meeting.
---

# Skill: Executive Briefing Drafter

## Purpose

Transform raw dashboard data, KPI snapshots, and analyst notes into a
structured executive briefing document. The output should read as if a senior
analyst spent two hours synthesizing the data — concise, confident, and
actionable.

---

## How to Execute This Skill

Follow these steps in order every time `/draft-briefing` is invoked.

### Step 1 — Collect and Confirm Inputs

Before drafting anything, identify what the user has provided:

- **Required:** At least one set of metrics or KPI values (numbers, tables,
  or narrative descriptions of dashboard state)
- **Optional but preferred:**
  - Time period covered (e.g., "Week of June 9", "Q2 FY2025")
  - Prior period values for comparison (MoM, QoQ, YoY)
  - Business context or strategic priorities
  - Audience type (CEO, board, department heads, investors)
  - Any known risks, anomalies, or flagged items from the data team

If the time period or audience is missing, make a reasonable assumption and
state it explicitly at the top of the briefing. Do not ask clarifying questions
unless critical data is entirely absent.

---

### Step 2 — Categorize the Metrics

Group the provided metrics into logical business domains before writing.
Common categories include (adapt to what is provided):

- Revenue & Growth
- Customer / User Metrics
- Operational Performance
- Cost & Margin
- Product / Feature Metrics
- Risk or Compliance Indicators

If a metric does not fit a category, create a "Other Key Indicators" section.

---

### Step 3 — Identify the Narrative Arc

Before writing, internally determine:

1. **The headline story** — What is the single most important thing happening
   in this data? (positive trend, missed target, emerging risk, inflection point)
2. **Supporting signals** — 2–4 metrics that reinforce or complicate the headline
3. **Tension or risk** — What could go wrong or is already showing strain?
4. **The "so what"** — What decisions or actions does this data demand?

This narrative arc must be reflected in the briefing structure.

---

### Step 4 — Draft the Briefing Document

Produce the briefing using the following structure exactly:

---

**EXECUTIVE BRIEFING**
**Period:** [Time period]
**Prepared for:** [Audience — state assumption if not provided]
**Prepared by:** [Leave as "Analytics Team" unless user specifies]
**Date:** [Today's date or leave as placeholder: YYYY-MM-DD]

---

#### 1. Situation Summary (3–5 sentences)

Write a plain-language paragraph that captures the overall state of the
business as reflected in the data. Lead with the most important finding.
Avoid jargon. Write for someone who will read only this section.

---

#### 2. Key Findings

List 4–7 bullet points. Each bullet must:
- Name the metric
- State the current value
- Compare to prior period (if available) with direction indicator (▲ ▼ →)
- Provide one sentence of business interpretation

Format:
`• [Metric Name]: [Value] ([▲/▼/→ X% vs. prior period]) — [Interpretation]`

---

#### 3. Risks and Watch Items

List 2–4 items that warrant attention. These may be:
- Metrics trending in the wrong direction
- Metrics missing targets by a meaningful threshold (>5% unless otherwise noted)
- External factors visible in the data
- Data quality issues or gaps that limit confidence

Format each as:
`⚠ [Risk Label]: [Description of the risk and why it matters]`

---

#### 4. Recommended Next Steps

List 3–5 concrete, actionable recommendations. Each must:
- Be tied directly to a finding or risk from sections above
- Specify who should act (use role titles, not names)
- Include a suggested timeframe (this week / by end of quarter / immediate)

Format:
`→ [Action] — Owner: [Role] | Timeline: [Timeframe]`

---

#### 5. Appendix: Data Notes (optional)

Include only if relevant:
- Assumptions made in the briefing
- Known data quality issues
- Definitions for any non-standard metrics
- Sources referenced

---

### Step 5 — Apply Quality Rules Before Outputting

Check the draft against these rules before delivering:

- [ ] No more than 600 words in the body (sections 1–4)
- [ ] Every metric cited in Section 2 must come from user-provided data —
      do not fabricate values
- [ ] Risks must be grounded in the data, not generic business advice
- [ ] Next steps must be specific, not vague ("investigate further" is not acceptable
      unless paired with a specific hypothesis to investigate)
- [ ] No passive voice in Section 1 (Situation Summary)
- [ ] Tone is confident and direct — no hedging phrases like "it seems" or
      "it could be argued"
- [ ] If an assumption was made (audience, time period, benchmark), it is
      explicitly labeled as an assumption

---

## Constraints

- **Do not invent metric values.** If a value is not provided, note it as
  "[data not provided]" in the relevant section.
- **Do not recommend tools, vendors, or platforms** unless the user explicitly
  asks for technology recommendations.
- **Keep the total document under one page** when printed at standard margins.
  If inputs are extensive, prioritize the most strategically significant findings.
- **Match tone to audience.** Board-level briefings use more strategic framing.
  Department-head briefings can be more operational.

---

## Usage Examples

### Example 1 — Weekly Business Review

/draft-briefing Week of June 9. Audience: CEO and CFO. Metrics: Revenue $2.1M (target $2.3M), New Customers 412 (up 8% MoM), Churn 3.2% (up from 2.7% last month), CAC $184 (down 12% MoM), Support ticket volume up 40% WoW following product release.

Expected output: A full briefing with churn and support spike framed as the
headline risk, revenue miss as supporting tension, and CAC improvement as the
positive signal. Next steps should address churn investigation and support
capacity.

---

### Example 2 — Quarterly Board Briefing

/draft-briefing Q2 FY2025 board briefing. Audience: Board of Directors. Data: ARR $18.4M (up 22% YoY), NRR 108%, Gross Margin 71% (down from 74% Q1), Headcount 134, Burn rate $1.1M/month, Runway 14 months. Strategic priority is path to profitability.

Expected output: Briefing framed around the profitability narrative. Gross
margin compression and burn rate flagged as risks. NRR and ARR growth as
supporting positives. Next steps tied to margin recovery and runway extension.

---

### Example 3 — Minimal Input / Quick Draft

/draft-briefing Monthly metrics for e-commerce ops team. GMV $4.7M, orders 18,200, average order value $258, fulfillment rate 94.1%, return rate 8.3%.

Expected output: Claude states assumed time period and audience, drafts a
complete briefing using available data, flags that prior-period comparisons
are unavailable, and notes this as a data gap in the Appendix.

---

## Notes for Maintainers

- This skill pairs naturally with `kpi-narrative-generator` (for per-metric
  narratives) and `chart-annotation-writer` (for visual annotation copy).
- If users want a slide-ready version instead of a document, they should
  specify "slide format" in their invocation — Claude will then condense each
  section to bullet-only format suitable for a deck.
- To update the default word limit or section structure, edit Step 4 and the
  quality rules in Step 5 together so they stay consistent.