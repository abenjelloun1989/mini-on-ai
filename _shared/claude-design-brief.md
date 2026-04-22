# Claude Design Brief — mini-on-ai Chrome Extension Suite

> **How to use:** Paste this entire document into claude.ai/design as your starting prompt.
> Ask Claude Design to produce a handoff bundle: design tokens (CSS), component HTML/CSS snippets, and SVG icons.
> The output will be implemented directly in the three extensions by Claude Code.

---

## 1. Project Overview

I'm building a suite of Chrome extensions under the **mini-on-ai.com** brand. All three extensions share:

- A dark-first aesthetic with a single accent color per extension
- A 380 × 560 px popup window (Chrome's physical constraint)
- A monetization model: Free tier (3 uses/month) → Pro tier ($7/month or lifetime deal)
- The same structural layout: header → tab navigation → tab content → optional full-page report

The three extensions are:

### ClauseGuard — AI Contract Analyzer
Users paste a contract (or upload a PDF). The extension calls Claude to identify red flags, analyze all clauses, flag missing protections, and generate negotiation tips. Results show a risk score badge + categorized clause cards.
- **Accent color:** Indigo `#6366f1`
- **Icon concept:** Shield with a checkmark (protection / defense)
- **Tabs:** Analyze · Compare (Pro) · Library (Pro) · Account

### InvoiceGuard — Gmail Invoice Tracker
Scans the user's Gmail inbox for invoice/payment emails, extracts amounts and due dates, and tracks payment status (Sent · Overdue · Paid · Cancelled). Shows a dashboard of invoices with status dots, amounts, and a reminder-email generator.
- **Accent color:** Indigo `#6366f1`, with amber `#f59e0b` for overdue status
- **Icon concept:** Invoice/receipt with a clock or lightning bolt (time-sensitive payments)
- **UI:** Dashboard list (no tabs) → detail panel slide-in

### JobGuard — Job Offer Analyzer
Users paste a job offer letter. The extension calls Claude to analyze compensation fairness, identify red flags (non-competes, IP assignment), spot missing protections (severance, PTO), and give negotiation tips. Includes a full-page printable report.
- **Accent color:** Amber `#f59e0b`
- **Icon concept:** Briefcase with a magnifying glass or star (scrutiny / opportunity)
- **Tabs:** Analyze · History (Pro) · Account

---

## 2. Current Visual State

All three extensions currently share this CSS foundation:

```css
/* Dark theme base */
--bg:        #0f0f1a;    /* page background — near-black with blue tint */
--surface:   #1a1a2e;    /* card / header background */
--border:    #2a2a45;    /* card borders, dividers */
--text:      #e0e0e0;    /* primary text */
--text-muted:#8b8bab;    /* secondary text, labels */
--danger:    #ef4444;    /* red flags, errors, overdue */
--warning:   #f59e0b;    /* warnings, medium-risk items */
--success:   #10b981;    /* paid, low-risk, positive */
```

**Current problems to solve:**
1. Emoji placeholders used as icons (🎟 🛡 📋 ⚖️) — need proper SVG icons
2. CSS token names diverge across extensions (`--accent` vs `--brand`, `--danger` vs `--red`) — need a canonical unified token set
3. Buttons, cards, and tabs have slightly different implementations in each extension — need a single canonical component set
4. Extension store icons (16/48/128px PNGs) are generated programmatically from a simple shield SVG — need better icon designs per extension

---

## 3. Hard Constraints

| Constraint | Detail |
|---|---|
| **Popup size** | 380px wide × max 560px tall (Chrome limit). Content scrolls vertically within this. |
| **No web fonts** | CSP blocks external requests. Must use system font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` |
| **No external icon fonts** | No Font Awesome, no Heroicons CDN. All icons must be inline `<svg>` or `<img src="icon.svg">` |
| **Dark mode primary** | Extensions are dark by default. JobGuard and InvoiceGuard have a light mode toggle (persisted in localStorage). ClauseGuard is dark-only. |
| **WCAG AA contrast** | All text on dark backgrounds must pass 4.5:1 contrast ratio minimum. |
| **Animation budget** | Only `transition: opacity/color/border-color 0.15s`. No keyframe animations on interactive elements (except a loading spinner). |
| **Self-contained** | Each extension is a standalone Chrome extension zip. No shared CDN. |

---

## 4. What I'm Asking For

Please produce a complete **design handoff bundle** containing:

### 4.1 Unified Design Token Set

A single CSS `:root` block with canonical variable names that work for all three extensions. Three colorway variants:

```
ClauseGuard:   --accent: #6366f1; --accent-hover: #4f46e5;
InvoiceGuard:  --accent: #6366f1; --accent-hover: #4f46e5; (+ amber for overdue status)
JobGuard:      --accent: #f59e0b; --accent-hover: #d97706;
```

The base dark tokens should be the same across all three. Include:
- Light mode override block (`body.light-mode { ... }`)
- Semantic color aliases: `--danger`, `--warning`, `--success`, `--danger-dim`, `--warning-dim`, `--success-dim` (dimmed versions for card backgrounds)

**Naming convention to use:** `--accent`, `--surface`, `--border`, `--text`, `--text-muted`, `--bg`, `--danger`, `--success`, `--warning`

### 4.2 Component HTML + CSS

Exact, copy-paste-ready HTML snippets + CSS for each component. The CSS should use only the token names from 4.1 (no hardcoded hex values). Components needed:

1. **Header bar** — logo icon (16px) + extension title + tier badge + dark mode toggle button + expand-to-fullpage button
2. **Tab navigation** — horizontal tabs with active underline, Pro chip badge on locked tabs
3. **Primary button** — full-width, accent-colored, with disabled state
4. **Secondary button** — ghost/outline style
5. **Text button** — link-style, accent color
6. **Icon button** — small square, used for dark toggle and expand
7. **Tier badge** — "Free" (muted) and "Pro" (accent) variants
8. **Pro gate** — centered upsell screen with emoji icon, heading, description, upgrade button
9. **Flag card** — used for contract/job offer red flags; variants: `--danger`, `--warning`, `--neutral`; subcomponents: icon + title + body + optional quote
10. **Result card** — generic card for a clause or positive finding; green/neutral variant
11. **Section title** — small caps label above a group of cards
12. **Tip item** — numbered tip with accent-colored number + body text
13. **Account card** — generic info card used in Account tab (plan card, usage card)
14. **LTD redemption** — text input + button in a row, with status message below
15. **Upgrade banner** — appears inside the main tab when limit is reached; accent gradient background

### 4.3 SVG Icon Set

All icons as inline `<svg>` elements. Provide at two sizes: 14×14 (UI use) and 48×48 (store icon / loading state use). No external dependencies — pure SVG paths.

**Extension mark icons (each extension's identity):**
- **ClauseGuard:** Shield shape with a checkmark inside. Clean, solid. Indigo fill. Should work as a 128px store icon.
- **InvoiceGuard:** Receipt/document shape with a small clock overlay or lightning bolt. Indigo fill.
- **JobGuard:** Briefcase shape with a small magnifying glass or star overlay. Amber fill.

**UI icons (shared across extensions):**
- Expand / fullpage (outward arrows or maximize)
- Dark mode toggle (moon icon)
- Light mode (sun icon)
- Copy to clipboard
- Back arrow (← New analysis)
- Download / export
- Check / success
- Lock (Free tier)
- Star or diamond (Pro tier)
- Upload / file

**Status dots (InvoiceGuard):**
- Overdue: pulsing red dot animation (CSS only)
- Sent: amber dot
- Paid: green dot
- Cancelled: grey dot

### 4.4 Full Popup Mockup

One complete popup mockup showing the entire visual design. Use **JobGuard** as the reference extension (amber accent, dark theme). Show two states:

**State A — Input state:**
Header (JobGuard branding) → tabs (Analyze active, History Pro, Account) → textarea input area → usage indicator ("2 of 3 analyses used") → amber Analyze button (enabled)

**State B — Results state:**
Header → tabs → risk score badge + "← New analysis" button → summary paragraph → Red Flags section (2–3 flag cards) → Tips section (2 numbered tips) → Negotiation Tips

Also show:
- **Account tab** — all three account cards (plan card showing "Free Plan" + upgrade button, usage card "2/3", LTD code input)
- **Pro gate variant** — History tab with gate screen

### 4.5 Extension Store Icon Guidance

Each extension needs 16px, 48px, and 128px PNG icons for the Chrome Web Store. The icons must:
- Have a solid colored background (not transparent) — CWS rejects fully transparent icons
- Be recognizable at 16px
- Pass CWS visual review (no screenshots, no text at small sizes)

Please provide:
- The recommended background color per extension
- The SVG mark optimized for each size (16px may need a simplified version)
- Guidance on how to render the SVG to PNG (e.g. using Inkscape, Sharp, or a Canvas script)

---

## 5. Output Format

Please structure your output as follows:

### tokens.css
```css
/* Paste into _shared/ and distribute to extensions */
:root { ... }
body.light-mode { ... }
```

### components.css
```css
/* One file with all component styles using var(--token) names */
.flag-card { ... }
.btn-primary { ... }
/* etc. */
```

### components.html
```html
<!-- One snippet per component, with comments -->
<!-- FLAG CARD — danger variant -->
<div class="flag-card flag-card--danger">...</div>

<!-- ACCOUNT CARD -->
<div class="account-card">...</div>
```

### icons.svg
```svg
<!-- All icons in a single SVG file using <symbol id="icon-name"> -->
<!-- Usage: <svg><use href="#icon-shield-check"/></svg> -->
<svg xmlns="http://www.w3.org/2000/svg">
  <symbol id="icon-shield-check" viewBox="0 0 24 24">...</symbol>
  ...
</svg>
```

### store-icons/
- `clauseguard-128.svg` — ready to export to PNG
- `invoiceguard-128.svg`
- `jobguard-128.svg`
- `EXPORT.md` — instructions for rendering to PNG at 16/48/128px

---

## 6. Implementation Context

The output will be implemented by Claude Code directly in these files:

```
_shared/
  base.css        ← add tokens.css + components.css content here
  utils.js        ← not changed by this design sprint
  popup-shell.html ← update markup to match final component HTML

clauseguard/popup/popup.css   ← add :root { --accent: #6366f1; ... }
invoiceguard/popup/popup.css  ← add :root { --accent: #6366f1; ... }
jobguard/popup/popup.css      ← add :root { --accent: #f59e0b; ... }
```

After this sprint, Claude Code will:
1. Replace the current emoji placeholders with the new SVG icons
2. Normalize token names across all three extensions to the canonical set
3. Replace extension-specific component CSS with the shared versions
4. Export store icons to PNG and update CWS listings

Please make the output as concrete and copy-paste-ready as possible. Claude Code will implement it without further design interpretation.
