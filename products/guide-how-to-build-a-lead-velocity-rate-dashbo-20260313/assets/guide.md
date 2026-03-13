# How to Build a Lead Velocity Rate Dashboard Mini-Guide

**For sales and marketing leaders** who already track pipeline metrics but want a forward-looking signal beyond lagging indicators like MQLs closed or revenue booked. This guide covers how to calculate Lead Velocity Rate (LVR), wire it into your existing stack, and act on what it tells you.

---

## 1. What LVR Actually Measures (and Why It Beats MQL Volume)

LVR measures the month-over-month percentage growth of your qualified leads pipeline. Unlike closed-won revenue, it predicts future revenue 60–90 days out with no lag. A healthy, compounding LVR gives you early warning on acceleration or decay before it shows up in your CRM pipeline value.

**Formula:**
`LVR = ((Qualified Leads This Month − Qualified Leads Last Month) / Qualified Leads Last Month) × 100`

**Tips:**
- Define "qualified lead" once and lock it. Using SQL (Sales Qualified Lead) is most predictive; MQLs introduce marketing noise. If you're using both, track separate LVR lines.
- A 10–15% month-over-month LVR typically maps to 2–3× annual growth. Benchmark your number against that range to calibrate expectations.
- Exclude recycled or re-engaged leads from the count. Only net-new qualification events should increment the numerator.

---

## 2. Choose Your Data Sources Before You Build

LVR only works if your qualified lead definition maps cleanly to a CRM stage or marketing automation status — not a gut call.

**Tips:**
- In Salesforce, filter on `Lead Status = "Qualified"` or `Opportunity Stage = "Discovery"` with a `CreatedDate` in the current month. Pull this via a custom report type and schedule it to refresh daily.
- In HubSpot, use the "Became a Sales Qualified Lead Date" contact property. Build a contact list filtered by that date range and feed it into a custom report or export it to your BI tool.
- If your CRM data is messy, use your marketing automation system (Marketo, Pardot) as the source of truth for qualification timestamps — it's usually cleaner than rep-entered data.

---

## 3. Build the Dashboard in Three Layers

Don't try to visualize everything at once. Structure the dashboard in three information layers:

**Layer 1 — Trend Line:** A line chart showing LVR % by month for the trailing 12 months. This is your headline view.

**Layer 2 — Segment Breakdown:** LVR split by channel (paid, organic, outbound, partner), region, or product line. This shows *where* growth is accelerating or stalling.

**Layer 3 — Leading Context:** Adjacent metrics that explain LVR movement — SDR activity volume, campaign spend, ICP match rate. These are diagnostic, not primary.

**Tips:**
- In Looker or Tableau, use a calculated field for LVR %: `(current_month_sqls - prior_month_sqls) / prior_month_sqls * 100`. Add a reference line at your target LVR (e.g., 12%) to make variance visible at a glance.
- Set a 3-month rolling average alongside the raw monthly figure. Single-month LVR spikes from events or campaigns are misleading without the smoothed trend.
- Color-code threshold bands: red below 5%, yellow 5–10%, green 10%+. Adjust thresholds to your growth stage.

---

## 4. Interpret Signals Before Calling a Meeting

LVR moves before revenue does. Here's how to read common patterns:

| Signal | What It Likely Means |
|---|---|
| LVR drops 2+ months in a row | Pipeline compression coming in Q+1. Check SDR activity and top-of-funnel spend. |
| LVR high but ACV declining | Volume up, quality down. Audit ICP fit of new SQLs. |
| LVR flat despite more spend | Channel efficiency problem. Reallocate budget. |
| LVR spikes after event | Likely one-time bump. Wait for 2-month normalization before claiming trend. |

**Tips:**
- Compare LVR against your revenue target math. If you need $2M next quarter and your current LVR only supports $1.4M based on historical conversion rates, you have a 6-week window to intervene.
- Flag LVR deceleration in your weekly sales-marketing sync — not just the monthly board report. Six weeks is roughly your reaction window before it becomes a missed quarter.

---

## 5. Automate Alerts, Not Just Reports

A dashboard nobody checks is worthless. Push LVR insights to where decisions already happen.

**Tips:**
- Set a Slack or Teams alert via your BI tool or Zapier: if month-to-date qualified lead count is more than 15% below the prior month pace by the 15th of the month, trigger a notification to the VP of Sales and Head of Demand Gen.
- Schedule a monthly LVR commentary email (auto-generated via your BI tool's digest feature) that includes the trend line image, the raw numbers, and three pre-filled "why this matters" bullet points that your team updates before sending to leadership.
- Assign a dashboard owner — typically a RevOps analyst — who validates the numbers monthly before they circulate. One bad data month destroys trust in the metric permanently.

---

## Quick-Reference Summary

- **LVR formula:** `((This Month SQLs − Last Month SQLs) / Last Month SQLs) × 100`
- Lock your qualified lead definition to one stage or status before building anything
- Target 10–15% monthly LVR as a proxy for 2–3× annual growth
- Structure dashboards in three layers: trend, segment, context
- Use a 3-month rolling average to smooth event-driven spikes
- Two consecutive months of LVR decline = act now, not next quarter
- Automate threshold alerts; don't rely on manual dashboard checks
- Assign a single RevOps owner to validate and maintain data integrity