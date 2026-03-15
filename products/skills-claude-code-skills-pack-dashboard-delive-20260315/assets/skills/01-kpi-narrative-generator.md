---
name: kpi-narrative-generator
trigger: /narrate-kpis
version: 1.0.0
description: >
  Converts raw KPI values, targets, and period-over-period changes into a
  coherent written narrative explaining business performance. Use this skill
  when you need to transform dashboard numbers into clear, executive-ready
  prose without manually drafting performance summaries.
tags: [analytics, executive-communication, kpi, narrative, reporting]
---

# KPI Narrative Generator

## Purpose

This skill takes structured KPI data — including current values, targets, prior
period comparisons, and trend direction — and produces a polished written
narrative suitable for executive briefings, stakeholder emails, or dashboard
summary panels. It removes the manual effort of translating numbers into
business language.

## When to Use

- You have a set of KPI values from a dashboard export, spreadsheet, or query
  result and need a written summary of performance
- You are preparing a weekly, monthly, or quarterly business review and need
  the "story behind the numbers"
- A stakeholder has asked for a plain-language explanation of what the metrics
  mean for the business
- You want consistent, tone-controlled narrative across multiple reporting
  periods

## Input Requirements

Provide KPI data in any of these formats when invoking the skill:

**Option A — Inline values in the command:**
```
/narrate-kpis Revenue: $4.2M (target $4.0M, +12% MoM), DAU: 87K (target 90K, -3% MoM), Churn: 2.1% (target <2.5%, flat MoM)
```

**Option B — Paste a table or CSV block after the command:**
```
/narrate-kpis
KPI, Actual, Target, Prior Period, Change
Monthly Revenue, $4.2M, $4.0M, $3.75M, +12%
Daily Active Users, 87K, 90K, 89.7K, -3%
Churn Rate, 2.1%, <2.5%, 2.1%, flat
```

**Option C — Reference a file:**
```
/narrate-kpis use kpis.csv for Q2 executive summary
```

**Minimum required fields per KPI:**
- KPI name
- Current value

**Strongly recommended fields (include when available):**
- Target or benchmark
- Prior period value or percentage change
- Time period (e.g., "April 2025", "Week 18", "Q2")
- Business unit or segment (if applicable)

## Execution Steps

Claude must follow these steps in order when this skill is triggered:

### Step 1 — Parse and Validate Input

- Extract all KPI names, values, targets, and change figures from the input
- Identify the reporting period if stated; if not stated, note it as unspecified
- Flag any KPI that is missing both a target and a prior-period comparison —
  these can still be narrated but with reduced context
- If the input is ambiguous or incomplete, ask one focused clarifying question
  before proceeding (e.g., "What time period does this data cover?")

### Step 2 — Classify Each KPI

For each KPI, determine and record internally:

| Dimension | Options |
|---|---|
| Performance status | On track / At risk / Exceeded / Missed |
| Trend direction | Improving / Declining / Stable / Insufficient data |
| Business signal | Positive / Neutral / Negative / Mixed |

Use these classifications to govern tone and emphasis in the narrative — do not
output this classification table in the final response unless the user asks for
it.

### Step 3 — Determine Narrative Structure

Select the appropriate structure based on the number of KPIs provided:

- **1–3 KPIs:** Single unified paragraph with natural transitions
- **4–7 KPIs:** Two to three paragraphs grouped by theme (e.g., growth metrics,
  efficiency metrics, risk indicators) or by performance status
- **8+ KPIs:** Opening summary sentence, thematic sections with brief headers,
  closing outlook sentence

### Step 4 — Write the Narrative

Apply all writing rules listed in the Constraints section. The narrative must:

1. Open with an overall performance verdict (strong, mixed, or challenging
   period) grounded in the data
2. Discuss each KPI with its value, context (vs. target or prior period), and
   a one-sentence business interpretation
3. Highlight the most significant positive result and the most significant
   concern explicitly
4. Close with a forward-looking sentence that is grounded in the data (not
   speculative) — e.g., referencing trajectory, whether targets appear
   achievable, or what to monitor

### Step 5 — Apply Tone Calibration

Default tone is **professional and direct** — suitable for a VP or C-suite
reader. Adjust if the user specifies otherwise:

- `tone:casual` — use conversational language, shorter sentences, first person
- `tone:technical` — retain metric precision, include statistical qualifiers
- `tone:investor` — emphasize growth vectors, market positioning language,
  forward indicators

### Step 6 — Output the Result

Deliver the narrative as clean prose. Do not include the classification table,
internal reasoning, or step labels in the output unless explicitly requested.

Optionally append a **Key Callouts** bullet list (3 bullets maximum) if the
data contains a notable outlier, a trend break, or a metric requiring immediate
attention.

---

## Constraints and Quality Rules

**Language and style:**
- Write in third person by default ("The business delivered…", "Revenue
  exceeded…") unless `tone:casual` is specified
- Use precise numbers as provided — do not round without the user's instruction
- Avoid filler phrases: "It is worth noting that…", "As we can see…",
  "Clearly…"
- Do not use the word "robust" or "synergy"
- Keep sentences under 30 words; break longer constructions into two sentences
- Do not editorialize beyond what the data supports — no causal claims unless
  the user provides context

**Accuracy rules:**
- Never invent a number, target, or trend not present in the input
- If a metric is missing its target, write "against no stated target" rather
  than omitting context
- If change direction is ambiguous (e.g., higher churn is worse, higher revenue
  is better), apply standard business logic — if unsure, ask before writing

**Length targets:**
- 1–3 KPIs: 80–150 words
- 4–7 KPIs: 150–300 words
- 8+ KPIs: 300–500 words

**Forbidden outputs:**
- Do not produce a bullet list as the primary output — the deliverable is prose
- Do not include "In conclusion" as a closing phrase
- Do not add recommendations or action items unless the user appends
  `+actions` to the command

---

## Usage Examples

### Example 1 — Minimal inline input

**Command:**
```
/narrate-kpis Revenue: $4.2M (target $4.0M, +12% MoM), Churn: 2.3% (target <2.5%, +0.2pp MoM)
```

**Expected output style:**
A single paragraph opening with a positive overall verdict, noting revenue
exceeded target by 5% and grew 12% month-over-month, then addressing churn as
elevated but within acceptable bounds, closing with a note that churn momentum
warrants monitoring in the next period.

---

### Example 2 — Multi-KPI table with period context

**Command:**
```
/narrate-kpis period:"Q1 2025" audience:"CFO"
KPI, Actual, Target, QoQ Change
Net Revenue, $12.8M, $12.0M, +7%
Gross Margin, 61%, 65%, -4pp
CAC, $142, $130, +9%
LTV:CAC Ratio, 3.8x, 4.0x, -0.3x
Logo Churn, 1.2%, <2%, flat
```

**Expected output style:**
Two paragraphs — first covering the positive revenue result with the margin
compression caveat, second addressing the unit economics picture (CAC pressure,
LTV:CAC below target) with a closing sentence noting that logo churn stability
provides a stabilizing signal despite cost headwinds.

---

### Example 3 — Adding tone and action items

**Command:**
```
/narrate-kpis tone:investor +actions
ARR: $18.4M (target $17M, +22% YoY), NRR: 112% (target 115%, -3pp YoY),
Sales Cycle: 47 days (target 40 days, +5 days YoY), Win Rate: 28% (target 32%, -4pp YoY)
```

**Expected output style:**
Investor-register narrative emphasizing strong ARR growth above plan, then
addressing NRR and sales efficiency as the key variables to resolve for
continued growth quality. Followed by a **Recommended Actions** section (3
bullets maximum) covering NRR recovery levers, sales cycle investigation, and
win rate analysis — each action grounded in a specific metric from the input.

---

## Notes for Skill Maintenance

- If the user provides segment-level breakdowns (e.g., by region or product
  line), apply the same narrative logic per segment and add a one-sentence
  aggregate view at the top
- When invoked from a file reference, confirm the file was read correctly by
  echoing the KPI count before producing the narrative: "Narrating 6 KPIs for
  [period]…"
- This skill does not produce charts, tables, or visualizations — route those
  requests to the appropriate chart-annotation or dashboard-layout skills in
  this pack