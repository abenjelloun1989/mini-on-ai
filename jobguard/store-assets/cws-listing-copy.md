# JobGuard — CWS Listing Copy (v1.0.2)

## Extension Name (≤45 chars)
JobGuard — AI Job Posting Analyzer

## Short Description (≤132 chars)
Spot scam signals, spec work traps, and lowball pay in any job posting before you apply. Free AI analyzer for freelancers.

## Detailed Description

**JobGuard — Know if a job posting is worth your time before you apply**

Tired of wasting hours on applications that lead nowhere — or worse, spec work requests and fake job postings? JobGuard analyzes any job posting in seconds and tells you exactly what to watch out for.

HOW IT WORKS:
1. Open any job posting on Upwork, LinkedIn, Indeed, Fiverr, or any job board
2. Click "Analyze current page" in the JobGuard popup
3. Get a 1–10 risk score, every red flag explained in plain English, and specific tips before you apply

WHAT JOBGUARD FLAGS:
✓ Scam signals — off-platform payment requests, fake urgency, missing company info
✓ Spec work traps — unpaid test projects, free samples, "prove your skills" requests
✓ Lowball pay — budget below market rate for the skills listed, with a market rate comparison
✓ Scope creep risk — vague deliverables, unlimited revisions, "other duties as required"
✓ IP overreach — claims on your pre-existing tools, background work, or processes
✓ Payment red flags — no upfront deposit mentioned, net-60+, unclear milestones
✓ Negotiation tips — specific questions to ask before you commit

WORKS ON:
Any page in Chrome — Upwork, LinkedIn, Indeed, Freelancer, Fiverr, Toptal, AngelList, and any other job board. Paste text directly if you prefer.

PLANS:
Free — 5 analyses per month. All red flag categories, risk score, market rate note, negotiation tips.
Pro ($7/month) — 200 analyses per month. Upgrade directly inside the extension.
Lifetime Deal — available at mini-on-ai.com/jobguard.html

PRIVACY:
JobGuard uses anonymous IDs — no account, no login, no email required. The full text of job postings is never stored. Only your usage count and a brief analysis summary are saved. You can delete all data at any time from the extension settings.

⚠ JobGuard is an AI tool that flags common warning signs. It does not guarantee any posting is safe or legitimate. Always do your own due diligence before accepting work.

Built by mini-on-ai.com

---

## Screenshots (5 required, 1280×800)

1. **Input state** — popup open showing "Analyze current page" button + textarea + character count
2. **High-risk result** — amber/red risk banner (score 8/10, "High Risk"), 3 red flags visible
3. **Flag detail** — single danger flag card expanded showing quote + explanation
4. **Looks legit result** — green banner (score 2/10, "Looks Legit") + green signals + tips
5. **Account tab** — usage counter + LTD code redemption field

## Keywords
job posting analyzer, job scam detector, freelance job red flags, upwork job analyzer, AI job analyzer, Chrome extension freelancer, spec work detector, job posting chrome extension

---

## What changed in v1.0.2 (for your own notes — don't paste in store)

- **Analyze tab blank fix** — shared CSS hides all `.tab-content` by default; the active tab div was missing its `active` class, so the input form was invisible on every popup open. Fixed by adding `active` class to `#tab-analyze` in popup.html AND updating `setupTabs()` in shared.js to initialize the active tab on call (self-healing for future extensions).
- **CSP fix** — inline `<script>` in popup.html blocked by MV3 `script-src 'self'`; extracted to `popup/icons-loader.js`.

## What changed in v1.0.1 (for your own notes — don't paste in store)

- Initial CWS review submission (unused release, superseded by v1.0.2).

## Category
Productivity

## Language
English
