# How to Build a Notion CRM That Actually Gets Used

If you've built and abandoned at least one Notion CRM, this guide is for you. Most Notion CRMs die because they're over-engineered at setup and under-maintained in practice. What follows is the exact structure, status logic, and daily habit that keeps a lightweight CRM alive for freelancers and small business owners managing up to 200 contacts.

---

## 1. One Database, Not Four

The classic mistake: separate databases for Contacts, Companies, Deals, and Notes, all linked together. The maintenance tax kills you within two weeks.

**Use a single Contacts + Deals database** where each record is a person *and* the relationship stage with them.

- Each row = one contact. Fields: Name, Company (plain text), Status, Last Contacted (date), Next Action (text), Deal Value (number), Source (select).
- Only add a second database if you have genuine one-to-many complexity — e.g., you regularly manage 3+ deals per client simultaneously.
- Resist adding fields speculatively. Start with seven fields. You can always add; you won't delete.

---

## 2. Status Logic That Reflects Real Work

Most CRM pipelines are aspirational. They have stages like "Nurture" and "Qualified" that sound right but mean nothing in daily use.

**Use six statuses maximum, each with a clear trigger:**

| Status | What it means |
|---|---|
| **Lead** | Haven't contacted yet |
| **Reached Out** | You sent the first message |
| **Active** | Ongoing conversation or open proposal |
| **Client** | Currently paying |
| **Dormant** | No contact in 60+ days, worth revisiting |
| **Closed** | Lost, irrelevant, or do-not-contact |

- If you can't define the trigger for moving someone *out* of a stage, delete the stage.
- "Dormant" does the heavy lifting most CRMs miss — it's your re-engagement list and it fills itself via a filter: `Last Contacted > 60 days ago AND Status = Active`.
- Never use "Follow Up" as a status. That's an action, not a stage. Put it in Next Action instead.

---

## 3. The Three Views You'll Actually Open

You don't need 12 saved views. You need three, and they should load in under two seconds.

- **Today View:** Filter by `Next Action Date = Today` or `Reminder = Today`. This is your morning task list. If it shows more than 10 people, your Next Action dates are dishonest — reschedule ruthlessly.
- **Pipeline View:** Group by Status. No date filter. Shows you the shape of your business at a glance — how many Active vs. Dormant, where revenue is stalled.
- **Dormant Reactivation View:** Filter `Status = Dormant`, sort by `Deal Value` descending. Open this every Friday. Pick two people to re-engage. Write two sentences each.

---

## 4. Capture That Takes Under 90 Seconds

CRMs die because logging a conversation feels like filing taxes. Remove every possible step between the interaction and the record.

- Create a **Notion mobile widget** or browser bookmark that opens directly to "New Contact" with a pre-filled template. The template should have only: Name, Status (defaulting to "Reached Out"), and Next Action.
- Use a **recurring daily reminder** (calendar or phone) at 5:00 PM labeled "Update CRM — 5 min." Not "review CRM." Specific action, specific time.
- If a conversation happens and you're not near Notion: text yourself one line — "Sarah Chen / Acme / follow up Monday re: proposal." Clear it during your 5 PM block. This prevents the "I'll remember" lie.

---

## 5. The Weekly 15-Minute Review

A CRM without a review cadence is a graveyard. This review has four steps and a hard time limit.

1. **Scan Active contacts** — Does everyone have a Next Action? If not, add one or move them to Dormant. (3 min)
2. **Check Dormant view** — Pick two to reactivate. Write the outreach now, don't schedule it. (5 min)
3. **Log any stale conversations** — Anything from the past week you didn't capture in real time. (4 min)
4. **Update one deal value** — Keeps the numbers honest for monthly revenue forecasting. (1 min)
5. **Stop.** If it regularly bleeds past 15 minutes, you have a complexity problem, not a discipline problem.

---

## 6. When to Add Complexity (and When Not To)

Adding features feels like progress. It usually isn't.

- **Add a linked Notes database** only when you're regularly scrolling through a long text field to find something — typically after 6+ months of use.
- **Add email integration** (e.g., Notion + Zapier + Gmail) only if you have more than 50 active conversations and are missing follow-ups weekly despite the daily habit.
- **Never add a "Lead Score" field** unless you have someone else populating it. Manual scoring gets abandoned by day three.

---

## Quick-Reference Summary

- **One database** to start. Separate only when the complexity is real, not anticipated.
- **Six statuses max**, each defined by a clear entry/exit trigger. Dormant is your secret weapon.
- **Three views only:** Today, Pipeline, Dormant Reactivation.
- **Capture in under 90 seconds** — widget, daily reminder, text-yourself fallback.
- **15-minute weekly review**, four steps, hard stop.
- **Add complexity only after a felt pain point**, never preemptively.