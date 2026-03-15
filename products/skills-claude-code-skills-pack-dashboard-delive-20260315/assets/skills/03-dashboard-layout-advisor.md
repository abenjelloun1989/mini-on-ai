---
name: dashboard-layout-advisor
trigger: /layout-dashboard
description: >
  Recommends optimal dashboard layout structure, visual hierarchy, and widget
  placement based on audience role and decision-making priorities. Use this
  skill when you need to design or redesign a dashboard for a specific audience
  and want to ensure the most critical information is surfaced first, visual
  flow guides attention effectively, and the layout supports fast decision-making
  without cognitive overload.
tags: [dashboard, layout, visualization, executive, analytics]
---

# Dashboard Layout Advisor

## Purpose

This skill analyzes dashboard requirements and produces a concrete, opinionated
layout recommendation. It accounts for audience role, decision-making context,
available metrics, and visualization best practices to deliver a prioritized
widget placement plan with clear rationale.

---

## When to Use This Skill

- You are building a new dashboard and need a starting layout structure
- An existing dashboard feels cluttered or gets poor engagement from stakeholders
- You are adapting a technical dashboard for an executive or non-technical audience
- You need to justify layout decisions to stakeholders with written rationale
- You are standardizing dashboard templates across a data product

---

## Inputs Required

Before executing, gather the following from the user. If any are missing, ask
for them explicitly before proceeding.

1. **Audience role** — Who is the primary viewer? (e.g., C-suite executive, VP of Sales,
   operations manager, product analyst, finance director)
2. **Key decisions** — What decisions does this dashboard need to support? List 1–5.
3. **Available metrics/widgets** — What data points, charts, or KPIs are available to
   place? A rough list is sufficient.
4. **Dashboard platform** (optional) — e.g., Tableau, Looker, Power BI, Metabase,
   custom web. Affects layout constraints.
5. **Screen context** (optional) — Primary viewing context: desktop browser, large
   display/TV, mobile, or mixed.
6. **Refresh cadence** (optional) — Real-time, hourly, daily, weekly. Affects what
   belongs above the fold.

---

## Execution Instructions

Follow these steps in order. Do not skip steps.

### Step 1 — Classify the Audience Decision Profile

Map the audience role to a decision profile:

- **Executive/C-suite**: Needs headline KPIs, trend direction, and exceptions only.
  Minimal detail. High signal-to-noise ratio. Time-constrained viewers.
- **Director/VP**: Needs KPIs plus one layer of drill-down. Wants to spot
  department-level issues and compare performance across teams or segments.
- **Manager/Ops**: Needs operational metrics, queue states, and actionable
  status indicators. Wants to identify what needs attention today.
- **Analyst**: Needs full data access, filters, comparison tools, and
  exploratory flexibility. Tolerates and expects density.

State which profile applies and note any hybrid characteristics.

### Step 2 — Establish Visual Hierarchy Zones

Define four layout zones for the dashboard canvas:

**Zone A — Hero Row (Top, Full Width)**
Reserved for 1–3 headline KPIs as large scorecards or single-number tiles.
These must answer the question: "Are we on track?" at a glance.
Rule: Never more than 3 items. No charts. Numbers and trend indicators only.

**Zone B — Primary Insight Area (Upper Middle, Dominant Width)**
The main chart or visualization that drives the core narrative. This is the
single most important visual. Allocate 50–60% of horizontal width if possible.
Place supporting context chart(s) in the remaining width of this row.

**Zone C — Supporting Detail Row (Lower Middle)**
2–4 secondary charts or breakdowns. These answer follow-up questions raised
by Zone B. Segment performance, time comparisons, contributing factors.

**Zone D — Reference / Appendix Row (Bottom)**
Tables, detailed breakdowns, low-priority metrics, data freshness indicators,
and filter controls. Audience-dependent: Executives rarely scroll here;
analysts live here.

### Step 3 — Assign Available Metrics to Zones

Take the user's metric/widget list and explicitly assign each item to a zone
(A, B, C, or D). For each assignment, provide a one-line rationale.

If a metric does not belong on this dashboard for this audience, say so and
explain why. Recommend where it should go instead (e.g., a separate drill-down
dashboard, a data table export).

### Step 4 — Specify Widget Types

For each assigned metric, recommend the specific visualization type:

- **Scorecard/KPI tile** — Single number with period-over-period delta and trend arrow
- **Line chart** — Trend over time, especially for continuous metrics
- **Bar chart** — Comparison across categories or time periods (discrete)
- **Stacked bar** — Part-to-whole composition over time
- **Donut/Pie** — Use sparingly; only when there are ≤5 segments and composition is the point
- **Table** — Multi-dimensional lookup; belongs in Zone D only
- **Bullet chart** — Actual vs. target; preferred over gauge charts
- **Heat map** — Pattern across two dimensions simultaneously
- **Map** — Geographic distribution only when geography is the primary dimension

Avoid recommending gauge charts, 3D charts, or overly decorative visuals.

### Step 5 — Define Spacing and Proportion Rules

Provide explicit proportion guidance:

- State the recommended grid system (e.g., 12-column grid)
- Specify column span for each widget (e.g., "4 of 12 columns each" for Zone A)
- Recommend minimum row heights for readability
- Flag any widgets that should not share a row due to cognitive conflict

### Step 6 — Write the Layout Recommendation Document

Produce the final output using the format defined below.

---

## Output Format

Deliver the recommendation as a structured document with these sections:

---

### Dashboard Layout Recommendation

**Dashboard:** [Name or purpose from user input]
**Audience:** [Role and decision profile classification]
**Platform:** [If provided; otherwise "Platform-agnostic"]
**Date:** [Today's date]

---

#### Audience Decision Profile

[2–4 sentences describing what this audience needs to do with this dashboard
and what that means for layout priorities.]

---

#### Layout Structure Overview

[A text-based grid diagram showing zone layout. Use ASCII block notation.
Label each zone with its contents at a high level.]

Example format:

┌─────────────────────────────────────────────────────────────┐
│  ZONE A: Hero KPIs                                          │
│  [KPI 1]          [KPI 2]          [KPI 3]                  │
├────────────────────────────────┬────────────────────────────┤
│  ZONE B: Primary Visual        │  ZONE B: Supporting        │
│  [Main Chart - 60%]            │  [Context Chart - 40%]     │
├──────────────┬─────────────────┴────────────────────────────┤
│  ZONE C      │  ZONE C         │  ZONE C                    │
│  [Chart 1]   │  [Chart 2]      │  [Chart 3]                 │
├──────────────┴─────────────────┴────────────────────────────┤
│  ZONE D: Detail Table / Reference Metrics / Filters         │
└─────────────────────────────────────────────────────────────┘

---

#### Widget Placement Plan

| Widget | Metric/Content | Zone | Viz Type | Grid Span | Rationale |
|--------|---------------|------|----------|-----------|-----------|
| ...    | ...           | ...  | ...      | ...       | ...       |

---

#### Excluded Metrics

List any metrics from the input that were excluded, with a brief reason and
suggested alternate placement (separate dashboard, export, tooltip, etc.).

---

#### Layout Rationale

[3–5 bullet points explaining the key layout decisions and the reasoning
behind zone assignments, visual hierarchy choices, and any trade-offs made.]

---

#### Implementation Notes

[2–4 practical notes for the person building this dashboard. Include any
platform-specific considerations if the platform was specified, filter
placement recommendations, and mobile/responsive notes if relevant.]

---

## Constraints and Quality Rules

- Always complete all six steps before producing output
- Never recommend more than 3 items in Zone A
- Do not place tables in Zone A, B, or C
- Do not recommend pie/donut charts with more than 5 segments
- Do not recommend 3D charts, gauge charts, or radial charts under any circumstances
- Every widget placement must include a rationale tied to the audience decision profile
- If fewer than 3 available metrics are provided, ask the user for more before proceeding
- If the audience role is ambiguous, ask one clarifying question before classifying
- Keep the Layout Rationale bullets focused on decisions, not generic best practices
- The ASCII grid must reflect the actual proportions recommended, not a generic template

---

## Usage Examples

### Example 1 — Executive Revenue Dashboard

/layout-dashboard
Audience: Chief Revenue Officer
Decisions: Is revenue on track this quarter? Which regions are underperforming? Should we adjust the forecast?
Metrics: Total ARR, Net New ARR, Churn ARR, ARR by Region (bar), Pipeline Coverage Ratio, Win Rate, Monthly Recurring Revenue trend, Top 10 Deals table, Forecast vs. Actuals line chart
Platform: Tableau
Screen: Desktop browser

---

### Example 2 — Operations Manager Fulfillment Dashboard

/layout-dashboard
Audience: Warehouse Operations Manager
Decisions: Are orders shipping on time today? Where are the bottlenecks? Do I need to reallocate staff?
Metrics: Orders Shipped Today, On-Time Ship Rate, Orders in Backlog, Average Pick Time, Pack Station Utilization by Station, Error Rate, Returns Initiated, Hourly Order Volume chart
Platform: Metabase
Screen: Large display mounted in warehouse

---

### Example 3 — Product Analyst Engagement Dashboard

/layout-dashboard
Audience: Senior Product Analyst
Decisions: Which features are driving activation? Where are users dropping off in onboarding? How does engagement compare across cohorts?
Metrics: DAU/MAU ratio, Feature Adoption by Feature (table), Onboarding Funnel conversion, Session Length distribution, Retention Curves by cohort, Event counts by user segment, A/B test results table
Platform: Looker
Screen: Desktop browser