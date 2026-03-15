---
name: metric-interpretation-summarizer
trigger: /interpret-metric
description: >
  Produces plain-language summaries that explain what a metric measures, why it
  moved, and what business action it implies. Use this skill whenever a dashboard
  output needs to be translated into a clear, executive-ready narrative — no
  statistical jargon, no ambiguity, just signal and recommended action.
tags: [analytics, executive-communication, metrics, dashboard, kpi]
version: 1.0.0
---

# Metric Interpretation Summarizer

## Purpose

This skill takes a raw metric — a number, a percentage change, a trend line, or a table of values — and produces a structured plain-language summary that answers three questions every business stakeholder needs:

1. **What does this metric actually measure?**
2. **Why did it move the way it did?**
3. **What should the business do about it?**

Use `/interpret-metric` when you have dashboard data ready but need the written narrative that makes it actionable for an executive audience.

---

## When to Use This Skill

- A metric has changed significantly (up or down) and you need to explain it without relying on the reader's statistical literacy
- You are building an executive briefing, board update, or weekly business review and need metric-level write-ups
- A stakeholder has asked "what does this number mean?" and you need a fast, credible answer
- You are populating a dashboard annotation, callout card, or insight panel
- You want a first draft of a metric narrative before a review meeting

---

## Input Requirements

Provide as much of the following as you have available. The skill works with partial information but produces stronger output with more context.

**Required (at least one):**
- The metric name and its current value
- The change (absolute and/or percentage) versus a prior period or target

**Strongly Recommended:**
- Time period covered (e.g., "Week of June 2–8", "Q2 2025", "trailing 30 days")
- Comparison baseline (prior week, prior quarter, same period last year, budget, forecast)
- Business unit, product line, or segment the metric belongs to

**Optional but Valuable:**
- Known contributing factors, events, or anomalies (promotions, outages, seasonality)
- Related metrics or leading indicators that moved in the same window
- The audience (e.g., CFO, VP of Marketing, board of directors)
- Desired tone (neutral/analytical, cautious, optimistic, urgent)

---

## Execution Steps

Follow these steps in order for every `/interpret-metric` invocation.

### Step 1 — Parse and Confirm the Input

Read all provided data carefully. Identify:
- The metric name and category (revenue, engagement, operational, quality, etc.)
- The numeric value(s) and the direction of movement
- The comparison period and baseline
- Any stated or implied audience

If critical information is missing (e.g., no metric name or no value provided), ask one clarifying question before proceeding. Do not ask multiple questions at once.

### Step 2 — Classify the Signal

Determine the nature of the movement:
- **Positive deviation** — metric moved favorably versus baseline
- **Negative deviation** — metric moved unfavorably versus baseline
- **Flat / within noise** — change is within normal variance; flag this explicitly
- **Mixed signal** — directionally positive on one dimension, negative on another

Note whether the magnitude is material. A 0.3% change in conversion rate may be noise; a 0.3% change in gross margin at scale may be significant. Use context clues from the input to make this judgment. State your classification in the output.

### Step 3 — Draft the Three-Part Narrative

Write each section in plain business English. Avoid formulas, p-values, statistical jargon, and hedging language unless the audience is explicitly technical.

**Section A: What This Metric Measures (1–3 sentences)**
Explain the metric's definition in non-technical terms. State what business behavior or outcome it reflects. If the metric is composite or derived, briefly explain how it is constructed.

**Section B: Why It Moved (2–5 sentences)**
Explain the most likely drivers of the change. If root cause is known from the input, state it directly. If it is inferred, use language like "likely driven by" or "consistent with." Acknowledge uncertainty where it exists — do not fabricate causality. Reference any supporting or contradicting signals from related metrics if provided.

**Section C: Recommended Action (1–4 sentences)**
State a clear, concrete business response. Scale the urgency to match the signal classification. Avoid vague recommendations like "monitor closely" — instead specify who should act, on what, and with what priority. If no action is warranted (e.g., metric is on track), say so explicitly and explain why.

### Step 4 — Write the One-Line Executive Summary

Produce a single sentence — maximum 25 words — that could stand alone as a callout card or slide annotation. It must contain the metric, the direction of movement, and the implication.

Format: **[Metric] [moved direction] [by amount] [in period], [driven by / despite / due to X], suggesting [implication or action].**

### Step 5 — Apply Formatting and Quality Checks

Before delivering output, verify:
- [ ] No statistical jargon without plain-language explanation
- [ ] No fabricated data points not present in the original input
- [ ] Signal classification is stated
- [ ] All three narrative sections are present
- [ ] Executive summary is 25 words or fewer
- [ ] Tone matches stated audience (default: senior business leader, neutral-analytical)
- [ ] Recommended action is specific, not generic

---

## Output Format

Deliver output in this exact structure:

---
**Metric:** [Name]
**Period:** [Time window]
**Signal:** [Positive deviation / Negative deviation / Flat / Mixed]

**Executive Summary**
[One-sentence callout, ≤25 words]

**What This Metric Measures**
[1–3 sentences]

**Why It Moved**
[2–5 sentences]

**Recommended Action**
[1–4 sentences]
---

Do not add sections beyond this structure unless the user explicitly requests additional analysis.

---

## Constraints and Quality Rules

- **Never invent numbers.** If a value is not provided, say so and note what data would be needed.
- **Never use passive-voice hedging to mask uncertainty.** If causality is unknown, say "the driver is unclear from available data" rather than inventing a plausible-sounding reason.
- **Keep each section within its length limit.** Executives do not read long metric cards.
- **Default audience is a non-technical senior business leader** unless stated otherwise.
- **Do not include raw data tables** in the output unless the user requests a supporting data appendix.
- **Tone is neutral-analytical by default.** Shift to cautious or urgent only when the signal classification warrants it or the user requests it.

---

## Usage Examples

### Example 1 — Revenue Metric with Known Driver

/interpret-metric
Metric: Monthly Recurring Revenue (MRR)
Value: $4.2M
Change: +$310K (+8%) vs. prior month
Period: May 2025
Context: New enterprise tier launched April 28. Three new logos closed in May averaging $85K ACV.

### Example 2 — Engagement Metric with Negative Movement

/interpret-metric
Metric: 7-Day Active Users
Value: 142,000
Change: -18,400 (-11.5%) vs. same week last month
Period: Week of June 2–8, 2025
Audience: VP of Product
Context: No major releases this week. Competitor launched a free tier on June 1.

### Example 3 — Operational Metric, Minimal Context

/interpret-metric
Metric: Customer Support Ticket Resolution Time (median)
Value: 47 hours
Change: +12 hours vs. Q1 2025 average
Period: Q2 2025 (April–June)
Audience: COO

---

## Notes for Skill Maintainers

- This skill is intentionally scoped to single-metric interpretation. For multi-metric dashboard narratives, use the `kpi-narrative-generator` skill in this pack.
- If the user provides a screenshot or data table instead of structured text, extract the relevant metric values before beginning Step 1.
- This skill pairs well with `/annotate-chart` (chart annotation writing) and `/draft-exec-briefing` (executive briefing drafts) when a full deliverable is needed.