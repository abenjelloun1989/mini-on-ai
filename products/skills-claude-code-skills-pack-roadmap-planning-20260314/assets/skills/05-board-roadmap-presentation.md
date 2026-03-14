---
name: board-roadmap-presentation
trigger: /build-board-deck
description: >
  Assembles a concise, board-level roadmap presentation from sizing summaries,
  priority scores, and the roadmap narrative. Frames quarterly bets in terms of
  business outcomes and risk trade-offs. Use this skill when you need to present
  the product roadmap to a board of directors, executive committee, or senior
  investors and require a polished, defensible narrative that connects
  engineering priorities to company strategy and financial outcomes.
tags:
  - roadmap
  - board
  - presentation
  - quarterly-planning
  - product-strategy
---

# Skill: Board Roadmap Presentation

## Purpose

Transform raw planning artifacts — opportunity sizing summaries, prioritization scoring matrices, and the now-next-later roadmap narrative — into a structured, board-ready presentation. The output should be immediately usable as speaker notes with slide-by-slide content, or as a standalone executive briefing document. Every slide must connect a product decision to a business outcome or a managed risk.

---

## When to Use This Skill

- You have completed opportunity sizing, priority scoring, and a roadmap narrative (from other skills in this pack or equivalent documents) and need to present to the board or C-suite.
- A quarterly business review, board meeting, or investor update is approaching and you need to frame the roadmap defensibly.
- Stakeholders are misaligned and you need a single authoritative document that reflects agreed-upon priorities in board-appropriate language.
- You are responding to board pressure to explain resource allocation or sequencing decisions.

---

## Inputs Required

Before running this skill, have at least one of the following available in your conversation or attached as files:

- **Opportunity sizing summary** — market size, revenue potential, or customer impact estimates per initiative
- **Priority scoring matrix** — scored and ranked feature or initiative list (e.g., RICE, ICE, or weighted scoring output)
- **Roadmap narrative** — now-next-later or quarterly roadmap written in prose or structured format
- **Optional:** OKRs, strategic pillars, or board-approved company goals to anchor the framing
- **Optional:** Known risks, dependencies, or constraints to surface as trade-off slides

If none of these inputs are present, ask the user to paste or describe the key initiatives and their relative priorities before proceeding.

---

## Execution Instructions

Follow these steps in order. Do not skip steps. Do not produce the final output until all steps are complete.

### Step 1 — Audit Available Inputs

Review everything the user has provided. Identify:
- Which planning artifacts are present (sizing, scores, narrative, OKRs)
- How many initiatives or themes are in scope
- The time horizon (e.g., Q3 2025, H2 2025, FY2026)
- Any stated audience context (board composition, investor type, internal exec team)

If the time horizon or audience is not stated, ask one clarifying question before continuing. Do not ask multiple questions at once.

### Step 2 — Identify the Three to Five Quarterly Bets

Distill all initiatives into no more than five "bets" — the strategic choices the company is making this quarter. A bet is a cluster of related work that can be described in one sentence with a measurable business outcome attached.

Rules for forming bets:
- Each bet must map to at least one business outcome (revenue, retention, cost reduction, risk mitigation, market expansion)
- Each bet must have an implicit or explicit opportunity cost (what is not being done as a result)
- Do not list more than five bets; consolidate smaller items into themes
- Label each bet with a short, memorable name (3–5 words, no jargon)

### Step 3 — Map Each Bet to Business Outcomes and Risks

For each bet, produce a structured entry containing:

- **Bet name** (short label)
- **One-sentence description** (what is being built or decided)
- **Primary business outcome** (quantified where data exists: "targets $X ARR," "reduces churn by Y%," "cuts infra cost by $Z/month")
- **Strategic pillar or OKR alignment** (if provided)
- **Key risk or trade-off** (what could go wrong, or what is being deprioritized)
- **Confidence level** (High / Medium / Low, based on sizing and scoring data)

### Step 4 — Draft the Slide-by-Slide Structure

Produce a complete slide outline using the following required structure. Each slide entry must include a suggested headline, 3–5 bullet points or a short paragraph of speaker notes, and any data callouts.

**Required Slides:**

1. **Title Slide**
   - Company name, presentation title ("Q[X] Product Roadmap"), date, presenter name placeholder

2. **Strategic Context (1 slide)**
   - Where the company is today relative to plan
   - 1–2 sentences on the market moment or competitive pressure driving this roadmap
   - Reference to board-approved goals or OKRs this roadmap serves

3. **What We Are Betting On This Quarter (1 slide)**
   - Visual-friendly list of the three to five bets with one-line descriptions
   - This is the anchor slide; everything else supports it

4. **Bet Deep-Dives (1 slide per bet, maximum 5 slides)**
   - One slide per bet following the structure from Step 3
   - Lead with the business outcome, not the feature description
   - Include the risk or trade-off explicitly — boards expect candor

5. **Resource and Capacity Reality Check (1 slide)**
   - How the team is allocated across bets (percentages or headcount, not task lists)
   - Flag any significant dependencies on other teams, vendors, or external timelines
   - Surface any bets that are at risk due to capacity constraints

6. **What We Are Not Doing (1 slide)**
   - Explicitly list two to four items that were scoped out and why
   - Frame as deliberate trade-offs, not failures
   - This slide builds board confidence in prioritization discipline

7. **Risk Register Summary (1 slide)**
   - Top three risks across the entire roadmap (not per-bet)
   - For each risk: likelihood (H/M/L), impact (H/M/L), mitigation plan in one sentence

8. **Success Metrics and Review Cadence (1 slide)**
   - How progress will be measured at the end of the quarter
   - Key leading indicators the board should track
   - When the next roadmap review will occur

9. **Ask / Decision Required (1 slide)**
   - What the board needs to approve, align on, or acknowledge
   - Frame as a clear decision or endorsement request, not an open discussion prompt
   - If no decision is needed, label this "For Information" and state what follow-up looks like

### Step 5 — Apply Board-Level Language Rules

Before finalizing, review all content against these rules and revise any violations:

- **No engineering jargon.** Replace terms like "refactor," "technical debt," "sprint," "microservices," or "CI/CD" with plain business language unless the board is known to be technical.
- **Lead with outcomes, not outputs.** "Reduce customer onboarding time by 40%" is correct. "Build a new onboarding flow" is not sufficient on its own.
- **Quantify wherever possible.** Use numbers from the sizing and scoring inputs. If a number is estimated, label it as such (e.g., "est. $1.2M ARR impact").
- **One idea per bullet.** No compound bullets. No bullets longer than 20 words.
- **Confidence must be honest.** Do not present medium-confidence estimates as certainties. Flag uncertainty explicitly.
- **Slide headlines must be assertions, not topics.** "We Are Prioritizing Retention Over Expansion This Quarter" is correct. "Retention Strategy" is not.

### Step 6 — Produce the Final Output

Deliver the complete presentation as a structured Markdown document using the format below. Include every slide. Do not summarize or truncate.

---

## Output Format

Use this exact structure for the deliverable:

---
BOARD ROADMAP PRESENTATION
[Company Name Placeholder] | [Quarter and Year] | Prepared by: [Name Placeholder]
---

SLIDE 1 — TITLE
Headline: [Presentation title]
Subheadline: [Quarter, year, presenter]

---

SLIDE 2 — STRATEGIC CONTEXT
Headline: [Assertion headline]
Speaker Notes:
- [Bullet]
- [Bullet]
- [Bullet]
Data Callout: [Any metric worth highlighting visually]

---

[Continue for all slides in sequence]

---

APPENDIX (Optional)
Include here: full priority scoring table, detailed sizing assumptions, or initiative list that did not make the main deck but may be requested in Q&A.

---

## Quality Rules

The final output must satisfy all of the following before being delivered:

- [ ] Contains all nine required slides
- [ ] Every bet has a named business outcome with at least one number
- [ ] Every bet has an explicit risk or trade-off statement
- [ ] No slide has more than five bullets
- [ ] No bullet exceeds 20 words
- [ ] All slide headlines are assertions (verb present)
- [ ] "What We Are Not Doing" slide contains at least two items
- [ ] Risk register contains exactly three risks with likelihood, impact, and mitigation
- [ ] Final slide contains a clear ask or decision request
- [ ] Zero instances of engineering jargon in the main deck (appendix is exempt)

If any rule cannot be satisfied due to insufficient input data, flag it explicitly with: **[DATA MISSING: describe what is needed]** and proceed with the best available information.

---

## Usage Examples

### Example 1 — Full Artifacts Provided

/build-board-deck

I've attached our Q3 priority scoring matrix and the now-next-later narrative from last week's planning session. Our OKRs are focused on reducing time-to-value for new enterprise customers and expanding into the DACH region. Board meeting is in 10 days. Audience is five board members, two of whom are operators and three are financial investors.

> Claude will audit the attached files, identify the top bets, map them to the enterprise and DACH OKRs, and produce a nine-slide deck with financial investor-friendly language. Engineering terms will be replaced with business outcomes throughout.

---

### Example 2 — Narrative Only, No Scoring Matrix

/build-board-deck

Here's our roadmap narrative: [paste]. We don't have a formal scoring matrix but I can tell you our top three priorities are: (1) launching the self-serve tier, (2) SOC 2 compliance, (3) rebuilding the reporting module. The board wants to understand why we're doing compliance before growth features.

> Claude will ask for the time horizon, then construct the bet structure from the stated priorities, explicitly address the compliance-vs-growth trade-off in the "What We Are Not Doing" and Risk slides, and frame SOC 2 as a revenue enabler (unlocks enterprise deals) rather than a cost center.

---

### Example 3 — Minimal Input, High Urgency

/build-board-deck

I have a board call in 48 hours. I don't have formal planning docs. Our main bets this quarter are: finishing the mobile app, cutting AWS costs by 30%, and starting work on an AI recommendations feature. We're a Series B SaaS company, $8M ARR, growing 80% YoY.

> Claude will acknowledge the limited inputs, ask one question (what is the primary board concern — growth, burn, or product differentiation), then construct a best-effort deck using the stated initiatives. All estimates will be flagged as [DATA MISSING] or labeled "to be confirmed" so the user knows what to validate before the call. The AI recommendations bet will be framed as a future-quarter setup, not a Q deliverable, unless the user confirms otherwise.

---

## Notes for Skill Maintenance

- This skill is most effective when run after the `opportunity-sizing`, `priority-scoring`, and `roadmap-narrative` skills in this pack have been completed. It is designed as the final assembly step.
- If the user has board feedback from a prior quarter, ask them to share it. Recurring board concerns (e.g., "the board always asks about hiring plan") should be incorporated into the Strategic Context or Risk slides.
- Slide count is intentionally constrained to nine. Do not add slides without explicit user instruction. Board presentations that exceed twelve slides lose credibility.