# Lead Nurture Sequence Logic Builder for Demand Gen Teams

Built for demand gen managers who already know *what* nurture is and need a repeatable framework to architect sequences that actually convert. Map every lead path by persona, funnel stage, and engagement signal so no contact rots in a generic drip.

---

## 1. Start With the Branching Matrix, Not the Email

Before writing a single subject line, build your logic skeleton. A nurture sequence is a decision tree — and most teams fail because they write content before defining the branches.

**Your base matrix has three axes:**
- **Persona** (e.g., VP of Engineering, IT Director, Procurement Lead)
- **Funnel Stage** (MQL, SAL, SQL, Re-engage)
- **Engagement Score Tier** (Cold: 0–29, Warm: 30–59, Hot: 60+)

**Tips:**
- A VP of Engineering at MQL/Warm is a different sequence than a Procurement Lead at MQL/Warm — even if they downloaded the same asset. Build separate branches, not separate emails.
- Start with 3 personas × 3 stages × 3 tiers. That's 27 possible paths. You won't build all 27 on day one — prioritize the 5–6 that represent 80% of your pipeline volume.
- Use a whiteboard tool like Miro or FigJam to map branches visually before touching your MAP. Skipping this step is why sequences break.

---

## 2. Define Stage-Exit Criteria Before Sequencing Content

A sequence without exit logic is just a newsletter. Every stage needs a clear "this lead moves when..." rule baked in from the start.

**Tips:**
- MQL → SAL exit trigger example: Lead scores 50+, visits pricing page twice in 7 days, *and* is from a company with 200+ employees. All three conditions, not just score.
- SAL → SQL should require a human touchpoint confirmation — don't automate this handoff. Your sequence should surface the lead to SDR queue when criteria are met, not auto-advance.
- Build a "sequence timeout" rule: if a lead shows zero engagement after 4 touches over 21 days, route to re-engagement path automatically. No manual review required.

---

## 3. Map Engagement Score to Cadence Velocity

Sending the same 7-day cadence to a cold lead and a hot lead is a waste of both. Velocity should mirror intent signals.

**Recommended cadence by tier:**

| Tier | Cadence | Channel Mix |
|------|---------|-------------|
| Cold (0–29) | 1 touch/10 days | Email only |
| Warm (30–59) | 1 touch/5 days | Email + LinkedIn |
| Hot (60+) | 1 touch/2–3 days | Email + LinkedIn + SDR call |

**Tips:**
- Score jumps matter as much as absolute score. A lead that goes from 20 → 45 in 72 hours deserves Hot-tier velocity even if they haven't crossed 60 yet. Build a "rapid score increase" trigger (e.g., +20 points in <4 days).
- Warm leads who open 3+ emails but never click should trigger a content-format branch — switch from text emails to a short video or interactive assessment.
- Don't increase cadence without changing content. Sending more of the same thing faster just accelerates unsubscribes.

---

## 4. Build Persona-Specific Content Forks at the Mid-Funnel

Generic nurture kills mid-funnel momentum. By SAL stage, every persona should be in a fully differentiated content path.

**Tips:**
- VP of Engineering at SAL stage: sequence should lead with technical depth — architecture docs, integration specs, peer case studies from similar tech stacks. No ROI calculators yet.
- Finance/Procurement persona at SAL: flip it — lead with TCO comparison, vendor risk frameworks, and security/compliance one-pagers. Technical content here causes drop-off.
- Fork trigger example: When a lead first engages with your MAP, tag them based on job title taxonomy (pull from enrichment tools like Clearbit or ZoomInfo). Use that tag to route into the correct content fork automatically at sequence enrollment.

---

## 5. Design the Re-Engagement Branch as a First-Class Sequence

Most teams treat re-engagement as a last-ditch blast. Build it as a structured 4-touch sequence with its own exit logic.

**Tips:**
- Touch 1: Pattern interrupt. Change the sender name to a senior leader (CMO, VP Sales). Subject line should acknowledge the silence: *"Still worth your time?"* — open rates on these run 15–22% higher than standard nurture emails.
- Touch 2 (Day 7): New asset type they haven't seen — if they only consumed blog content, offer a benchmark report or short webinar.
- Touch 3 (Day 14): Low-friction CTA — a poll, a 1-question survey, or an invite to a live event. You're looking for *any* engagement signal to re-score and re-route.
- Touch 4 (Day 21): Sunset email. Make it explicit. "We'll stop sending — let us know if the timing is wrong." Leads who click "timing is wrong" go into a 90-day dormant sequence, not the trash.

---

## Quick-Reference Summary

- **Build the logic matrix first** — persona × stage × engagement tier — before writing content
- **Exit criteria define sequence value** — every stage needs specific, multi-condition graduation rules
- **Cadence velocity must match engagement score**, including rapid-score-increase triggers
- **Fork content by persona no later than SAL stage** — generic mid-funnel content kills pipeline
- **Re-engagement is a structured sequence**, not a one-off blast — build it with 4 touches and a sunset step
- **Automate routing decisions**; reserve human review for SQL handoffs only
- **Audit sequences quarterly**: if a branch has <8% CTR over 60 days, it's broken — rebuild the content, not just the subject line