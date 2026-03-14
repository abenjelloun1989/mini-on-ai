---
name: opportunity-sizing
trigger: /size-opportunity
description: >
  Synthesizes raw feature requests, customer data, and market signals into
  structured opportunity sizing summaries. Use this skill whenever you need
  to evaluate one or more potential features or initiatives and produce a
  defensible, stakeholder-ready summary of reach, revenue impact, and
  strategic fit before committing to roadmap prioritization.
when_to_use: >
  Invoke this skill at the start of a planning cycle when you have a messy
  collection of feature requests, support tickets, sales feedback, or market
  research and need to turn that raw signal into a structured opportunity
  document that product, engineering, and executive stakeholders can act on.
---

# Opportunity Sizing Skill

## Purpose

Transform unstructured input — feature requests, customer quotes, revenue data, competitive signals, usage metrics — into a concise, scored **Opportunity Sizing Summary** for each candidate initiative. The output must be immediately usable in a quarterly planning meeting or board deck without additional editing.

---

## How to Execute This Skill

Follow these steps in order every time `/size-opportunity` is invoked.

### Step 1 — Gather and Clarify Input

Before doing any analysis, audit what the user has provided. You need at minimum:

- A named initiative or feature area (even a rough working title)
- At least one signal of customer or market demand (requests, quotes, ticket volume, survey data, or competitive evidence)

If either of these is missing, **ask for them before proceeding**. Do not fabricate demand signals.

If the user provides partial data for scoring dimensions (reach, revenue, strategic fit), acknowledge the gaps explicitly in the output and note what assumptions were made to fill them.

Accepted input formats: plain prose, bullet lists, pasted Slack threads, CSV snippets, copied spreadsheet rows, or a mix of all of the above.

---

### Step 2 — Extract and Normalize Key Data Points

From the raw input, identify and extract:

| Data Type | What to Look For |
|---|---|
| **Customer reach** | Number of accounts, users, or segments affected; frequency of request; percentage of ARR represented |
| **Revenue signals** | Expansion revenue potential, churn risk if not built, new logo pull-through, pricing leverage |
| **Strategic signals** | Alignment to company strategy, competitive differentiation, platform/foundation value, regulatory requirement |
| **Effort signals** | Any engineering estimates, complexity hints, dependency mentions, or prior scoping notes |
| **Time sensitivity** | Deadlines, competitive windows, contractual commitments, seasonal factors |

If a data type is completely absent, note it as **"No data provided"** in the summary — never invent numbers.

---

### Step 3 — Score Each Opportunity

Apply the following three scoring dimensions. Use a **1–5 integer scale** for each.

#### 3a. Reach Score (1–5)
Estimate how many customers, users, or revenue dollars are directly affected.

| Score | Signal |
|---|---|
| 1 | Fewer than 5 accounts or <1% of user base |
| 2 | 5–25 accounts or 1–5% of user base |
| 3 | 26–100 accounts or 6–15% of user base |
| 4 | 101–500 accounts or 16–40% of user base |
| 5 | 500+ accounts or >40% of user base |

If data is insufficient, assign a score of **"?"** and explain why.

#### 3b. Revenue Impact Score (1–5)
Estimate the combined effect of new revenue, expansion, and churn prevention.

| Score | Signal |
|---|---|
| 1 | Minimal — hygiene improvement, no direct revenue tie |
| 2 | Low — retention risk for a small segment, marginal upsell |
| 3 | Moderate — clear expansion path or retention of meaningful ARR |
| 4 | High — opens a new buyer segment or protects significant ARR |
| 5 | Critical — material new revenue stream, strategic pricing lever, or major churn risk mitigation |

#### 3c. Strategic Fit Score (1–5)
Assess alignment to company strategy, product vision, and platform coherence.

| Score | Signal |
|---|---|
| 1 | Off-roadmap distraction, serves one customer's edge case |
| 2 | Loosely related, hard to frame as strategic |
| 3 | Consistent with strategy but not a priority thrust |
| 4 | Directly advances a stated strategic priority |
| 5 | Core to company strategy, differentiating, or foundational |

#### 3d. Composite Score
Calculate a simple composite: **(Reach + Revenue Impact + Strategic Fit) / 3**, rounded to one decimal place. This is a directional signal, not a final ranking.

---

### Step 4 — Write the Opportunity Sizing Summary

Produce one summary block per initiative. Use exactly the structure below. Do not add extra sections or omit any field.

---

**OPPORTUNITY SIZING SUMMARY**

**Initiative:** [Name or working title]

**One-Line Description:** [What this is in plain language — one sentence, no jargon]

**Customer & Market Signal:**
[2–4 sentences synthesizing the demand evidence. Cite specific data points where available — e.g., "Requested by 34 enterprise accounts representing ~$2.1M ARR" or "Appeared in 18% of churn survey responses in Q3." If data is thin, say so plainly.]

**Estimated Reach:**
[Quantified estimate or range. State the basis for the estimate. Flag if assumed.]

**Revenue Impact Assessment:**
[2–3 sentences covering new revenue potential, expansion opportunity, churn risk, and pricing leverage. Be specific where data allows.]

**Strategic Fit Rationale:**
[2–3 sentences explaining why this does or does not align to current company strategy, product vision, or competitive positioning.]

**Key Assumptions & Data Gaps:**
[Bulleted list of assumptions made and what data would sharpen the analysis. If no gaps, write "None identified."]

**Scores:**
- Reach: X / 5
- Revenue Impact: X / 5
- Strategic Fit: X / 5
- **Composite: X.X / 5**

**Recommended Next Step:**
[One concrete action — e.g., "Validate reach estimate with CS team before scoring final," "Include in prioritization matrix," "Deprioritize — revisit in H2," "Escalate for executive decision due to strategic weight."]

---

Repeat this block for every initiative provided in a single invocation. If more than five initiatives are provided at once, flag this to the user and confirm whether they want all sized in one pass or in batches.

---

### Step 5 — Produce a Comparison Table (When 2+ Initiatives Are Provided)

When the user provides multiple initiatives, append a summary comparison table after all individual blocks.

| Initiative | Reach | Revenue Impact | Strategic Fit | Composite |
|---|---|---|---|---|
| [Name] | X/5 | X/5 | X/5 | X.X/5 |

Sort the table by Composite score descending. Add a one-sentence note below the table flagging any initiative where scores diverge significantly (e.g., high strategic fit but low reach) as a discussion point for prioritization.

---

## Constraints and Quality Rules

- **Never fabricate data.** If a number is estimated or assumed, label it clearly with "(estimated)" or "(assumed)." If data is absent, write "No data provided" — do not substitute a plausible-sounding figure.
- **Write for a mixed audience.** The summary must be readable by a VP of Product, a CFO, and an engineering lead. Avoid internal team slang. Spell out acronyms on first use.
- **Be concise but complete.** Each section should be dense with signal, not padded. Cut filler phrases like "it is important to note that."
- **Scores are directional, not definitive.** Always remind the user that scores are a starting point for discussion, not a final prioritization decision.
- **One summary block per initiative.** Do not combine two initiatives into one block even if they are related.
- **Preserve the user's own data.** If the user gives you a specific number (e.g., "47 customers have requested this"), use that number verbatim — do not round, reinterpret, or override it.
- **Flag conflicts.** If the input contains contradictory signals (e.g., two sources give different request counts), surface both and note the discrepancy rather than silently choosing one.

---

## Usage Examples

### Example 1 — Single Initiative from Slack Paste

/size-opportunity

Here's a dump from Slack and our support inbox. Customers keep asking for SSO support. We've had 22 enterprise accounts mention it in the last 90 days — those accounts are roughly $1.8M ARR. Our sales team says 3 deals worth about $400K are blocked on it. We're also seeing it in 30% of enterprise churn surveys. Strategically we're pushing upmarket so this feels important.

---

Expected behavior: Claude produces a single Opportunity Sizing Summary for "SSO Support," extracts the specific data points provided, assigns scores across all three dimensions with rationale grounded in the provided data, notes any gaps (e.g., no effort estimate provided), and suggests a recommended next step.

---

### Example 2 — Multiple Initiatives from a Feature List

/size-opportunity

We have three things we're debating for Q3:

1. Bulk export to CSV — lots of power users ask for it, not sure how many, seems like a nice-to-have
2. Native Salesforce integration — we've lost 2 deals this quarter because we don't have it, both were 6-figure ACV, our main competitor just shipped this
3. Redesigned onboarding flow — our activation rate is 34% and we think better onboarding could move it to 50%+, that would affect all new signups which is about 600/month

---

Expected behavior: Claude produces three individual Opportunity Sizing Summary blocks followed by a comparison table sorted by composite score. For "Bulk export to CSV," Claude flags the reach data gap and assigns a "?" score for reach. Claude notes in the comparison table discussion that the Salesforce integration has a strong revenue signal despite unknown total reach.

---

### Example 3 — Thin Input Requiring Clarification

/size-opportunity

We should probably build an AI assistant feature.

---

Expected behavior: Claude does **not** attempt to size this opportunity. Instead, Claude asks the user for: (1) a more specific description of what the AI assistant would do and for whom, and (2) at least one signal of customer or market demand — such as customer requests, competitive pressure, or internal strategy documentation — before proceeding. Claude explains what it needs and why, keeping the response brief and actionable.