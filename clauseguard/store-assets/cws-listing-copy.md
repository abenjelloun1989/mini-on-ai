# ClauseGuard — CWS Listing Copy (v1.3.1)

## Extension Name (45 chars max)
ClauseGuard — AI Contract & NDA Analyzer

## Short Description (132 chars max)
Spot red flags in any contract before you sign. AI-powered risk score, clause rewrites, and negotiation tips — free.

## Detailed Description (5000 chars max — paste as-is)

**AI contract review — spot red flags before you sign**

ClauseGuard analyzes any contract, NDA, or legal document for risks, red flags, and unfair clauses in under 30 seconds. Plain English explanations, suggested clause rewrites, and negotiation tips — no lawyer required for a first-pass review.

**How it works:**
1. Paste contract text, drag-and-drop a PDF, or click "Analyze current page" on any contract webpage
2. Click Analyze (or press Ctrl+Enter) — results in under 30 seconds
3. Review your risk score, red flags, and copy-ready clause rewrites
4. Your results stay saved — reopen the extension anytime without losing your analysis

**What you get:**
✓ Risk Score (1–10) — instant color-coded assessment of contract fairness
✓ Red Flags — dangerous clauses flagged in plain English with "what could go wrong" explanations
✓ Suggested Changes — ready-to-use rewordings for every risky clause, copy with one click
✓ Missing Protections — spots important clauses absent from the contract (late payment penalties, liability caps, IP ownership clauses, etc.)
✓ Negotiation Tips — actionable advice tailored to this specific contract
✓ Context preserved — your contract and results survive closing and reopening the popup
✓ Expand to full page — open ClauseGuard in a full browser tab for a larger, more comfortable reading experience

**Works on:**
– Freelance contracts & service agreements
– NDAs (non-disclosure agreements)
– Employment offers & agreements
– SaaS terms of service
– Lease contracts
– Any contract text you paste, drag-and-drop as PDF, or extract from a webpage

**Free plan:** 3 full analyses per month — risk score, all red flags, and suggested rewrites included. No account needed.

**Pro plan ($7/month):** Unlimited analyses + contract comparison (diff two versions side by side) + PDF export + saved clause library (save, organize, delete, and export fair clauses for reuse).

**Lifetime Deal:** Available for a limited time via selected partner platforms. Redeem a lifetime code in the Account tab for permanent Pro access.

**Privacy:** ClauseGuard uses a randomly generated anonymous ID. We do not collect your name, email, or personal information. Contract text is processed for analysis and not stored beyond what is needed. You can delete all your data at any time from the Account tab. We never sell or share your data.

⚠️ ClauseGuard is an AI-powered tool for informational purposes only. It does not constitute legal advice. For high-stakes contracts, always consult a qualified attorney.

Built by mini-on-ai.com — AI tools for freelancers and small businesses.

---

## Category
Productivity

## Language
English

---

## Screenshots — what to capture (5 screenshots, 1280×800 recommended)

Current screenshots in `store-assets/` were generated for v1.2.0 and are still valid.
Regenerate if you want to show the character count indicator or the new library delete/export UI.

### screenshot-1-input.png
**What to show:** The popup in its default state — textarea with character counter below it, "Analyze current page" button, PDF upload button, "3 analyses remaining" usage line, blue "Analyze Contract" button.
**Caption:** "Paste any contract, drag-and-drop a PDF, or analyze the current page in one click"

### screenshot-2-risk-score.png
**What to show:** Results view — colored risk badge (e.g. 8/10 HIGH RISK), plain-English summary, 2–3 red flags visible.
**Caption:** "Instant risk score (1–10) with plain-English explanations of every red flag"

### screenshot-3-clause-rewrite.png
**What to show:** A clause card expanded — original quote, explanation, ⚠ concern box, "Suggested change" box with Copy button.
**Caption:** "Risky clauses explained — with copy-ready rewrites to negotiate a fairer deal"

### screenshot-4-missing-protections.png
**What to show:** "Missing Protections" section — 2–3 items with yellow left border, why-it-matters text, and copy-ready clause text.
**Caption:** "Spots missing protections — IP ownership, liability caps, late payment clauses, and more"

### screenshot-5-full-page.png
**What to show:** Full-page expanded view (⤢ button in header) — large risk score banner, results content below.
**Caption:** "Expand to full page for a comfortable desktop experience"

---

## Marquee tile (1400×560) tagline
AI contract review. Spot red flags before you sign. Free Chrome extension.

## Promo tile (440×280) tagline
ClauseGuard
AI Contract Analyzer
Free · No signup needed

---

## Store keywords (work into listing naturally for CWS internal search)
contract review, AI contract analyzer, NDA analyzer, contract red flag detector, freelance contract review, legal document review, contract risk score, unfair clause detector, contract analysis, employment contract review

---

## What changed in v1.3.1 (for your own notes — don't paste in store)

- **Tab switching fixed** — renamed internal `setupTabs()` wrapper to `_initTabs()` to prevent it shadowing the shared utility, which caused an infinite recursion that broke all tabs and PDF upload after popup reload
- **PDF upload restored** — was broken as a side-effect of the tab recursion bug; now works correctly on every popup open
- **Light mode fixed** — CSS custom property cascade was unreliable in Chrome extension popup context; fixed by setting inline styles directly on `document.documentElement` via `_applyTheme()`
- **CSP violation fixed** — inline `<script>` in popup.html blocked by MV3 `script-src 'self'`; extracted to `popup/icons-loader.js`
- **Account view** — replaced shield emoji 🛡 with ClauseGuard logo (icon48.png) in the Free Plan card

---

## What changed in v1.3.0 (for your own notes — don't paste in store)

### Frontend
- **Character count** live counter below textarea — shows X / 15,000, turns green at ≥50 chars
- **Ctrl+Enter / Cmd+Enter** submits analysis (keyboard shortcut)
- **Drag-and-drop PDF** onto textarea — reuses existing PDF extractor
- **Context persistence** — contract text and full results survive popup close/reopen within same browser session (chrome.storage.session)
- **Clipboard fix** — shared copyText() helper; shows "Copy failed" instead of silent false positive
- **Compare tab** — change count summary (X changes — Y favorable, Z unfavorable) + empty state message
- **Library** — delete individual clauses (✕ button), export all clauses as .txt file, retry button on load failure
- **Pro gates** — Compare/Library tab gates disappear immediately after LTD code redemption (no popup restart)
- **Account tab** — shows this month's analysis count for Pro users
- clipboardWrite permission added to manifest
- prefers-reduced-motion: animations disabled for accessibility

### Backend (security hardening)
- Stripe webhook signature now **mandatory** — was bypassable if secret not configured
- LTD users **protected** from accidental downgrade when Stripe subscription deleted
- LTD code enumeration fixed — unified error message for invalid/used codes
- Claude response null-guarded + validated (risk_score + clauses presence checked)
- /api/compare length validation — prevents large payload abuse
- Usage count is now an atomic check-and-increment (race condition fixed)
- GDPR: DELETE /api/user endpoint added
- Debug info removed from production 500 responses

## What changed in v1.2.0 (for reference)
- Removed Google Doc import (replaced by PDF upload + paste)
- Added expand-to-full-page button (⤢ in header)
- Full-page mode redesigned: single-column, 72px risk score banner, 15px base font
- Account tab: LTD code redemption field
- Worker model updated to claude-haiku-4-5 (resolves 404 errors)
- max_tokens bumped to 8192 (resolves JSON truncation on long contracts)
