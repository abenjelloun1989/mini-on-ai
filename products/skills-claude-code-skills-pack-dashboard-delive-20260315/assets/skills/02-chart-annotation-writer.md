---
name: chart-annotation-writer
trigger: /annotate-chart
description: >
  Generates concise, context-aware annotations for chart anomalies, inflection
  points, and trend shifts. Use this skill whenever a dashboard chart contains
  data patterns that require guided interpretation — spikes, drops, reversals,
  plateaus, or seasonal deviations — and you need viewer-ready callout text
  without writing it manually. Designed for analytics engineers and data product
  managers preparing charts for executive or stakeholder audiences.
when_to_use: >
  Invoke when you have chart data (raw numbers, a description, or a data export)
  and need annotation copy that explains *what happened*, *why it matters*, and
  *what to watch next*. Best used after metric thresholds have been defined and
  before the dashboard is published or shared.
---

# Chart Annotation Writer

## Purpose

Produce precise, business-readable annotations for chart inflection points,
anomalies, and trend shifts. Each annotation must be immediately usable as
callout text — no editing required by the requester.

---

## Inputs Claude Should Expect

The user will provide one or more of the following. Accept any combination.

- **Chart description** — a plain-English description of what the chart shows
- **Data snippet** — a table, CSV paste, or list of values with time labels
- **Metric name** — e.g., "Weekly Active Users," "Gross Margin %," "Cart Abandonment Rate"
- **Date range** — the time window the chart covers
- **Anomaly location** — specific date(s) or range(s) to annotate
- **Business context** — product launches, campaigns, incidents, or external events
- **Audience** — who will view the chart (e.g., C-suite, board, ops team)
- **Annotation style** — callout label, tooltip text, slide note, or inline caption

If critical inputs are missing, ask one focused clarifying question before
proceeding. Do not ask multiple questions at once.

---

## Execution Steps

Follow these steps in order for every `/annotate-chart` invocation.

### Step 1 — Parse the Chart Signal

Identify every notable data event in the provided data or description:

- **Spike** — sudden upward movement exceeding normal variance
- **Drop** — sudden downward movement exceeding normal variance
- **Inflection point** — trend direction change (growth to decline, or vice versa)
- **Plateau** — extended flat period after a trend
- **Acceleration / deceleration** — rate-of-change shift without direction reversal
- **Seasonal deviation** — performance above or below expected seasonal pattern

Label each event with its type, approximate date or range, and magnitude if
data is available (e.g., "+34% week-over-week" or "lowest value in 6 months").

### Step 2 — Prioritize Events

Rank events by business significance, not just magnitude. Apply this priority
order:

1. Events that cross a defined threshold or target
2. Events with the largest absolute or percentage deviation
3. Events that reverse an established trend
4. Events that confirm or contradict a prior annotation or forecast

Annotate the top 1–4 events unless the user requests a specific count.

### Step 3 — Draft Each Annotation

For each selected event, write annotation copy using this three-part structure:

**What** — one sentence stating the observable fact with the metric, date, and
direction.

**Why** — one sentence offering the most plausible business explanation, framed
as likely cause or contributing factor. If no context was provided, flag this as
"cause unconfirmed."

**Watch** — one sentence indicating what to monitor next or what this event
implies for upcoming periods. Omit if the event is historical with no forward
relevance.

Keep each annotation under 40 words total. Prioritize clarity over completeness.

### Step 4 — Format the Output

Structure the response as follows:

---

## Chart Annotations — [Metric Name] — [Date Range]

### Annotation [N]: [Event Type] — [Date or Range]

**Label text (short):** [5–8 word callout, suitable for a chart label]

**Full annotation:**
[What. Why. Watch.]

**Placement note:** [Where on the chart this annotation should appear — e.g.,
"Place callout at the week of [date], pointing to the peak value."]

---

Repeat for each annotation. After all annotations, include:

### Usage Notes
- Confirm causal context with the data or business team before publishing.
- [Any flags raised during analysis — e.g., missing baseline, ambiguous date range.]

---

## Constraints and Quality Rules

- **Length:** Each full annotation must be 25–40 words. Label text must be 5–8 words.
- **Tone:** Neutral and factual. No alarm language ("crisis," "disaster") and no
  unwarranted optimism ("incredible growth"). Let the data speak.
- **Causation:** Never assert a cause as confirmed unless the user explicitly
  provided it. Use hedged language: "likely driven by," "coinciding with,"
  "may reflect."
- **Numbers:** Always include the metric value, percentage change, or comparative
  figure when data is available. Vague annotations ("values went up") are not acceptable.
- **Audience calibration:** For C-suite or board audiences, remove operational
  detail and lead with business implication. For ops or analytics audiences,
  include more precise numeric context.
- **No jargon:** Avoid technical data terms (p-value, outlier, standard deviation)
  unless the user has indicated a technical audience.
- **Accuracy gate:** If the provided data is ambiguous or contradictory, flag it
  in the Usage Notes rather than guessing.

---

## Usage Examples

### Example 1 — Single spike annotation from data paste

/annotate-chart
Metric: Daily Revenue
Date range: Jan 1–31
Audience: VP of Sales
Data: [table showing Jan 18 spike to $2.1M vs. $1.3M daily average]
Context: Flash sale ran Jan 17–18

Expected output: One annotation identifying the Jan 18 revenue spike,
attributing it to the flash sale, and noting whether the post-sale days
show retention or reversion to baseline.

---

### Example 2 — Trend reversal across a quarter

/annotate-chart
Metric: Monthly Active Users
Date range: Q3 (Jul–Sep)
Audience: C-suite
Description: MAU grew steadily July–August then declined 18% in September.
No context provided.

Expected output: Two annotations — one marking the August peak and one
marking the September decline. Cause flagged as unconfirmed. Watch note
recommends monitoring October MAU for recovery signal.

---

### Example 3 — Multiple anomalies with audience specification

/annotate-chart
Metric: Cart Abandonment Rate
Date range: Last 12 weeks
Audience: Product and Engineering team
Description: Rate spiked to 74% in week 6, dropped back to 61% in week 8,
and has plateaued at 63–65% for the last four weeks.
Context: Checkout redesign launched week 7.

Expected output: Three annotations — week 6 spike (pre-launch baseline risk),
week 8 drop (redesign impact), and the weeks 9–12 plateau (stabilization
or ceiling effect). Causal attribution applied to the redesign launch.
Watch note flags whether 63–65% represents improvement over pre-redesign norm.

---

## Notes for Skill Maintainers

- This skill is part of the Dashboard Delivery pack. It is designed to feed
  into `/draft-executive-briefing` and `/generate-kpi-narrative` when a full
  dashboard communication package is needed.
- If the user's chart covers multiple metrics, ask which metric to prioritize
  or run annotation sets sequentially, one metric at a time.
- Update audience calibration guidance as new stakeholder personas are added
  to the pack's shared context.