# Skill: chrome-extension-playbook

## Purpose
Complete playbook for building, hardening, monetizing, and distributing a Chrome extension. Extracted from two shipped extensions (ClauseGuard v1.3.0, InvoiceGuard v1.1.0). Read this at the start of any new extension project.

## Trigger
User says anything like: "let's build a new chrome extension", "new extension", "next extension idea", "build an extension for X"

---

## Shared Codebase (always start here — don't recode what already exists)

A `_shared/` directory at the repo root contains canonical utilities shared across all extensions. **Always use these — never rewrite them per-extension.**

### Starting a new extension — copy the shell first

```bash
# 1. Copy the annotated popup template (one-time copy, not synced):
cp _shared/popup-shell.html {name}/popup/popup.html

# 2. Search for every <!-- CUSTOMIZE: ... --> comment and update it.
#    The shell has the correct header/tabs/account-tab/state-machine already wired.

# 3. Sync shared.js + shared.css into the new popup/ directory:
python3 scripts/sync_shared.py      # copies shared.js + shared.css into every popup/
python3 scripts/check_syntax.py     # syntax-checks all 13+ JS files
```

**`_shared/popup-shell.html` is a copy-once template** (each extension customizes its own copy). `shared.js` and `shared.css` ARE synced continuously by `sync_shared.py` — never edit the per-extension copies.

### What's in `_shared/utils.js`

Four functions, loaded via `<script src="shared.js">` in every popup.html (before popup.js):

```js
escHtml(str)                              // HTML-safe string (div.textContent trick)
escAttr(str)                             // attribute-safe string
copyText(btn, text, resetLabel = "Copy") // clipboard + "✓ Copied!" + isConnected guard
initDarkMode(storageKey, toggleId)       // reads localStorage, applies body.light-mode, wires toggle
```

### What's in `_shared/base.css`

Shared CSS loaded via `<link rel="stylesheet" href="shared.css">` (after popup.css in `<head>`):

**Utilities:**
- Universal reset (`*` box-sizing)
- `@media (prefers-reduced-motion)` global disable
- `body.light-mode { ... }` token overrides (harmless on dark-only extensions)
- `.hidden { display: none !important; }`, `.char-count`, `.usage-row`

**Content components (JobGuard pattern — harmless no-ops on other extensions):**
- `.flag-card` family (danger/warning/green variants + header/icon/title/body/quote)
- `.section-title`, `.tips-list`, `.tip-item`, `.tip-num`

**Structural layout (shared across all new extensions via popup-shell.html):**
- `.header`, `.header-left`, `.header-right`, `.header-title`
- `.tabs`, `.tab`, `.tab.active`, `.tab-content`, `.tab-content.active`
- `.pro-chip` (Pro badge inside a tab label), `.pro-gate`, `.pro-gate-icon`
- `.btn-primary`, `.btn-secondary`, `.btn-text` (all using `var(--accent, var(--brand, #6366f1))`)
- `.account-section`, `.account-card`, `.account-card-label`, `.account-card-value`, `.account-card-desc`
- `.ltd-row`, `.ltd-input`, `.ltd-message`, `.account-footer`
- `.loading-wrap`, `.loading-text`, `.loading-sub`, `.loading-spinner` (CSS keyframe)

All structural styles use CSS var fallbacks — they work in all three extension colorways without modification. Existing extensions do NOT need to remove their popup.css equivalents; popup.css loads after shared.css and overrides cleanly.

### popup.html wiring for every new extension

Start from `_shared/popup-shell.html` (see above). If wiring manually:

```html
<head>
  <link rel="stylesheet" href="popup.css">
  <link rel="stylesheet" href="shared.css">   <!-- after popup.css so shared wins ties -->
</head>
<body>
  ...
  <script src="shared.js"></script>            <!-- before popup.js -->
  <script src="popup.js"></script>
</body>
```

### popup.js — what to call, what NOT to write

```js
// Call these (provided by shared.js — do NOT redefine them):
initDarkMode("jg-theme", "darkModeToggle");   // use extension-specific storage key
copyText(btn, text, resetLabel);
escHtml(str);
escAttr(str);

// DO NOT define your own versions of these functions — if you redefine them,
// the per-extension copy will shadow the shared one. Delete any duplicate.
```

### Design System (Claude Design handoff)

`_shared/claude-design-brief.md` is a ready-to-paste prompt for **claude.ai/design**. It describes all three extensions, constraints (380px, no web fonts, WCAG AA), and requests:
- Unified CSS design token set (canonical `--accent`/`--surface`/`--border` variable names)
- Component HTML+CSS library (15 components, copy-paste-ready)
- SVG icon set (extension marks + UI icons + InvoiceGuard status dots)
- Full JobGuard popup mockup (input + results + account tab)
- Chrome Web Store icon guidance (16/48/128px export)

After the design handoff, Claude Code implements the output by updating `_shared/base.css` and normalizing token names across all three extensions.

---

## Stack (defaults — don't deviate without a reason)

| Layer | Choice | Notes |
|-------|--------|-------|
| Extension | Chrome MV3 | Service worker background, popup, options page |
| Content script | Only if DOM injection needed | InvoiceGuard injects into Gmail; ClauseGuard doesn't need it |
| Backend | Cloudflare Worker + D1 + KV | D1 = SQLite database; KV = response cache (30-day TTL) |
| AI | Claude Haiku | Fast + cheap. 25s AbortController timeout on every fetch |
| Payments | Stripe Checkout + Customer Portal | webhook mandatory (HMAC-SHA256) |
| Deploy | `npx wrangler deploy` in `{name}/worker/` | |
| Hosting | CWS (Chrome Web Store) | Manual upload per version |

---

## 1. Manifest Template

```json
{
  "manifest_version": 3,
  "name": "[ProductName] — [Benefit Phrase]",
  "version": "1.0.0",
  "description": "[One line: what it does + who it's for, ≤132 chars]",
  "permissions": ["storage", "activeTab", "clipboardWrite"],
  "host_permissions": ["https://[your-worker].workers.dev/*"],
  "background": { "service_worker": "background/service-worker.js" },
  "action": { "default_popup": "popup/popup.html", "default_icon": { "48": "icons/icon48.png", "128": "icons/icon128.png" } },
  "options_page": "options/options.html",
  "icons": { "48": "icons/icon48.png", "128": "icons/icon128.png" }
}
```

**Add `"alarms"` to permissions** if the extension needs background polling (e.g. overdue checks).

**Add content_scripts** only when you need DOM injection:
```json
"content_scripts": [{
  "matches": ["https://mail.google.com/*"],
  "run_at": "document_start",
  "js": ["content/[name].js"],
  "css": ["content/[name].css"]
}]
```

---

## 2. Worker Architecture

### Standard routes every extension gets

```
POST   /api/auth/register         — anonymous UUID registration (idempotent)
GET    /api/usage?user_id=...     — tier + monthly usage count
POST   /api/[core-action]         — the main AI feature (analyze, parse, remind…)
POST   /api/subscribe             — create Stripe Checkout session
POST   /api/webhook/stripe        — Stripe lifecycle events (mandatory signature check)
GET    /api/subscription          — current subscription status
POST   /api/portal                — create Stripe Customer Portal session
POST   /api/ltd/redeem            — lifetime deal code redemption
DELETE /api/user?user_id=...      — GDPR deletion (users + all their data)
GET    /api/health                — binding status check (DB, KV, env vars)
```

### Shared helpers (copy verbatim into index.js)

```js
function corsJson(env, obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

async function parseJson(request) {
  try { return await request.json(); }
  catch { return { error: "Invalid JSON" }; }
}

async function requireUser(env, userId) {
  if (!userId) return null;
  return env.DB.prepare(
    "SELECT id, tier, pro_source FROM users WHERE id = ?"
  ).bind(userId).first();
}

function currentMonth() {
  return new Date().toISOString().slice(0, 7); // "YYYY-MM"
}
```

### CORS preflight (always include)

```js
if (request.method === "OPTIONS") {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, DELETE, PATCH, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
```

---

## 3. DB Schema

### Tables every extension gets

```sql
-- Core user table
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  tier TEXT NOT NULL DEFAULT 'free',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  email TEXT,
  pro_source TEXT,              -- NULL = subscription, 'ltd' = lifetime deal
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Lifetime deal codes
CREATE TABLE IF NOT EXISTS ltd_codes (
  code TEXT PRIMARY KEY,
  redeemed_by TEXT REFERENCES users(id),
  redeemed_at TEXT
);

-- Monthly usage tracking (one row per user per month)
CREATE TABLE IF NOT EXISTS usage_tracking (
  user_id TEXT NOT NULL,
  month TEXT NOT NULL,          -- 'YYYY-MM'
  action_count INTEGER NOT NULL DEFAULT 0,
  UNIQUE(user_id, month)
);
```

### Migrations to run on every new extension before first deploy

```sql
-- If starting from an older schema without pro_source:
ALTER TABLE users ADD COLUMN pro_source TEXT;

-- LTD codes table (if not already created):
CREATE TABLE IF NOT EXISTS ltd_codes (
  code TEXT PRIMARY KEY,
  redeemed_by TEXT REFERENCES users(id),
  redeemed_at TEXT
);
```

Run via Wrangler: `npx wrangler d1 execute [DB_NAME] --command "ALTER TABLE..."`

---

## 4. Monetization Model

### Tier definitions

| Feature | Free | Pro ($7/month) |
|---------|------|----------------|
| Core AI actions | 3/month | 500/month (hard cap) |
| [Premium feature A] | ✗ | ✓ |
| [Premium feature B] | ✗ | ✓ |
| CSV export | ✗ | ✓ |
| Priority support | ✗ | ✓ |
| Lifetime Deal (LTD) | — | One-time code, pro_source='ltd' |

### Atomic usage increment (prevents race conditions)

```js
// Increment if under limit — single query, no pre-read
await env.DB.prepare(`
  INSERT INTO usage_tracking (user_id, month, action_count)
  VALUES (?, ?, 1)
  ON CONFLICT(user_id, month) DO UPDATE
  SET action_count = action_count + 1
  WHERE action_count < ?
`).bind(userId, currentMonth(), FREE_LIMIT).run();

// Check if increment succeeded
const row = await env.DB.prepare(
  "SELECT action_count FROM usage_tracking WHERE user_id = ? AND month = ?"
).bind(userId, currentMonth()).first();

if (!row || row.action_count > FREE_LIMIT) {
  return corsJson(env, { error: "Monthly limit reached. Upgrade to Pro." }, 429);
}
```

### Upgrade flow
1. User hits limit → popup shows upgrade banner
2. Click upgrade → `POST /api/subscribe` → returns `{ checkout_url }`
3. `chrome.tabs.create({ url: checkout_url })` opens Stripe Checkout
4. Payment → Stripe fires `checkout.session.completed` webhook
5. Worker updates `users.tier = 'pro'`
6. Next popup open: `GET /api/usage` returns `tier: 'pro'` → Pro gates disappear **immediately** (call `updateProGates(true)` on success)

---

## 5. Security Checklist (ship nothing without all of these)

### Stripe webhook — mandatory verification

```js
async function handleStripeWebhook(request, env) {
  const payload = await request.text();
  const signature = request.headers.get("stripe-signature");

  // BOTH must be present — no fallthrough
  if (!env.STRIPE_WEBHOOK_SECRET) {
    console.error("STRIPE_WEBHOOK_SECRET not configured");
    return new Response("Webhook secret not configured", { status: 500 });
  }
  if (!signature) {
    return new Response("Missing stripe-signature", { status: 400 });
  }
  const isValid = await verifyStripeSignature(payload, signature, env.STRIPE_WEBHOOK_SECRET);
  if (!isValid) {
    return new Response("Invalid signature", { status: 400 });
  }
  // ... handle events
}
```

### LTD downgrade protection

```js
// subscription.deleted handler — never downgrade LTD users
await env.DB.prepare(`
  UPDATE users
  SET tier = 'free', stripe_subscription_id = NULL, updated_at = datetime('now')
  WHERE stripe_subscription_id = ?
  AND (pro_source IS NULL OR pro_source != 'ltd')
`).bind(subscriptionId).run();
```

### LTD code anti-enumeration

```js
const ltdCode = await env.DB.prepare(
  "SELECT * FROM ltd_codes WHERE code = ?"
).bind(code.trim().toUpperCase()).first();

// Single unified error for both invalid and already-used
if (!ltdCode || ltdCode.redeemed_by) {
  return corsJson(env, { error: "This code is not valid or has already been used." }, 400);
}
```

### API timeouts on every external call

```js
// Anthropic — 25s
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 25000);
try {
  const res = await fetch("https://api.anthropic.com/...", { ...opts, signal: controller.signal });
} finally {
  clearTimeout(timeout);
}

// Stripe — 10s
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 10000);
try {
  const res = await fetch("https://api.stripe.com/...", { ...opts, signal: controller.signal });
} finally {
  clearTimeout(timeout);
}
```

### Anthropic response guard (before any .text access)

```js
if (!result.content?.[0]?.text) {
  throw new Error("Empty response from Anthropic");
}
const text = result.content[0].text.trim();
```

### No debug info in error responses

```js
// Wrong:
return corsJson(env, { error: "Internal error", detail: e.message }, 500);

// Right:
console.error("Analyze error:", e);
return corsJson(env, { error: "Analysis failed. Please try again." }, 500);
```

### Input length limits (both client and server)

```js
const MAX_INPUT = 15000; // chars
if (!input || input.length < 50) return corsJson(env, { error: "Input too short." }, 400);
if (input.length > MAX_INPUT) return corsJson(env, { error: `Input must be under ${MAX_INPUT} characters.` }, 400);
```

---

## 6. UX Patterns

### Dark mode toggle

**Call `initDarkMode()` from `shared.js` — do not write the IIFE yourself.**

```js
// In initPopup() / DOMContentLoaded, FIRST LINE (before any render, avoids FOUC):
initDarkMode("{name}-theme", "darkModeToggle");
// e.g. "jg-theme" for JobGuard, "ig-theme" for InvoiceGuard
```

Add the toggle button in popup.html header:
```html
<button class="btn-icon" id="darkModeToggle" title="Toggle theme">☾</button>
```

CSS design tokens (keep in each extension's own popup.css — accent differs per extension):
```css
:root {
  --bg: #0f0f1a;
  --surface: #1a1a2e;
  --surface-2: #242440;
  --border: #2a2a45;
  --text: #e2e2f0;
  --text-muted: #8b8bab;
  --accent: #F59E0B;        /* pick one per extension */
  --accent-dim: rgba(245,158,11,0.15);
  --green: #10b981;
  --green-dim: rgba(16,185,129,0.12);
  --danger: #ef4444;
  --danger-dim: rgba(239,68,68,0.12);
  --warning: #f59e0b;
  --warning-dim: rgba(245,158,11,0.12);
  --radius: 8px;
}
body.light-mode {
  --bg: #ffffff; --surface: #f5f5f7; --surface-2: #ebebef;
  --border: #e5e5ea; --text: #1d1d1f; --text-muted: #6e6e73;
}
```

`@media (prefers-reduced-motion)` and `*` reset are provided by `shared.css` — do NOT add them to popup.css.

### Copy buttons — use `copyText()` from shared.js (never silent)

```js
// Already available from shared.js — just call it:
copyText(btn, text, "📋 Copy");   // resetLabel is optional
```

### Retry buttons on all error states (never dead-end)

```js
function showError(container, message, retryFn) {
  container.innerHTML = `
    <div style="text-align:center;padding:20px;">
      <p style="color:var(--danger);font-size:12px;margin-bottom:8px;">${escHtml(message)}</p>
      <button class="btn-text" id="retryBtn">Try again</button>
    </div>`;
  document.getElementById("retryBtn")?.addEventListener("click", retryFn);
}
```

### Keyboard shortcuts

```js
// In any form or textarea
form.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !submitBtn.disabled) {
    e.preventDefault();
    submitBtn.click();
  }
});

// In overlays/panels
overlay.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeOverlay();
});
```

### HTML escaping — use `escHtml()` / `escAttr()` from shared.js

```js
// Already available from shared.js — just call them:
`<div>${escHtml(str)}</div>`          // for innerHTML content
`<div data-id="${escAttr(id)}">`      // for attribute values
// DO NOT redefine these — the shared version uses the correct div.textContent approach
```

---

## 7. Icon Generation (recolor the existing icon — never draw from scratch)

All extensions share the same shield + checkmark shape. New icons are generated by **pixel-level luminance remapping** of the InvoiceGuard source icon. This keeps the family look consistent and takes ~2 minutes.

### How it works

Each source pixel has a luminance value 0–255:
- **Dark pixels** (lum < 110): background — remap to the new extension's bg color
- **Mid pixels** (lum 110–235): shield body — remap to the new accent color
- **Light pixels** (lum > 235): white checkmark — keep white

### Python script (run once, generates all three icon sizes)

```python
#!/usr/bin/env python3
"""
generate_icons.py — Recolor InvoiceGuard icons for a new extension.
Requires: pip install Pillow numpy
Usage: python3 generate_icons.py {new_extension_name}
"""
import numpy as np, sys
from pathlib import Path
from PIL import Image

# ── Configure these per extension ─────────────────────────────────────────────
# (R, G, B) tuples — tune to match extension accent color
BG_DARK    = (22,  8,   0)    # darkest bg pixel  → jobguard amber example
BG_LIGHT   = (50,  22,  0)    # lighter bg pixel
SHIELD_DARK  = (180, 100, 10)  # darkest shield pixel
SHIELD_LIGHT = (253, 224, 100) # lightest shield pixel (near accent)
# ──────────────────────────────────────────────────────────────────────────────

def remap(arr):
    out = arr.copy()
    lum = (0.299 * arr[:,:,0] + 0.587 * arr[:,:,1] + 0.114 * arr[:,:,2])

    # Background zone: dark pixels
    bg_mask = lum < 110
    t_bg = np.clip((lum[bg_mask] - 0) / 110, 0, 1)[..., None]
    out[bg_mask, :3] = (
        np.array(BG_DARK) * (1 - t_bg) + np.array(BG_LIGHT) * t_bg
    ).astype(np.uint8)

    # Shield zone: mid-luminance pixels
    sh_mask = (lum >= 110) & (lum <= 235)
    t_sh = np.clip((lum[sh_mask] - 110) / 125, 0, 1)[..., None]
    out[sh_mask, :3] = (
        np.array(SHIELD_DARK) * (1 - t_sh) + np.array(SHIELD_LIGHT) * t_sh
    ).astype(np.uint8)

    # Checkmark zone: very light pixels — keep white, leave unchanged
    return out

ROOT = Path(__file__).parent
SOURCE_DIR = ROOT / "invoiceguard" / "icons"   # source to recolor
DEST_DIR   = ROOT / sys.argv[1] / "icons"
DEST_DIR.mkdir(parents=True, exist_ok=True)

for size in [16, 48, 128]:
    src = SOURCE_DIR / f"icon-{size}.png"
    img = np.array(Image.open(src).convert("RGBA"))
    img = remap(img)
    out_path = DEST_DIR / f"icon-{size}.png"
    Image.fromarray(img).save(out_path)
    print(f"  wrote {out_path.relative_to(ROOT)}")
```

### Calibrating the colors

Run the script, then view the generated icon. Tune `BG_DARK/BG_LIGHT` and `SHIELD_DARK/SHIELD_LIGHT` until it matches the extension's accent:

| Accent | BG_DARK | BG_LIGHT | SHIELD_DARK | SHIELD_LIGHT |
|--------|---------|----------|-------------|--------------|
| Amber `#F59E0B` | (22,8,0) | (50,22,0) | (180,100,10) | (253,224,100) |
| Indigo `#6366F1` | (8,8,30) | (22,22,60) | (80,80,200) | (160,162,255) |
| Rose `#F43F5E` | (30,5,10) | (60,10,20) | (180,40,70) | (255,130,150) |

### Manifest icon entries (both dash and no-dash variants for Chrome compatibility)

After generating, **copy each icon to both naming conventions** (Chrome can be finicky):

```bash
cp icons/icon-48.png icons/icon48.png
cp icons/icon-128.png icons/icon128.png
```

Manifest.json must reference the exact filenames present:
```json
"icons": { "16": "icons/icon-16.png", "48": "icons/icon48.png", "128": "icons/icon128.png" },
"action": { "default_icon": { "48": "icons/icon48.png", "128": "icons/icon128.png" } }
```

---

## 8. Landing Page Formula (`site/{name}.html`)

### Head (required meta tags)

```html
<meta property="og:title" content="[ProductName] — [Benefit Phrase]">
<meta property="og:description" content="[One sentence, 100-130 chars, benefit-focused]">
<meta property="og:image" content="https://mini-on-ai.com/assets/[name]-og.png">
<meta property="og:url" content="https://mini-on-ai.com/[name].html">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="[ProductName] — [Benefit Phrase]">
<meta name="twitter:description" content="[Same as og:description]">
<meta name="twitter:image" content="https://mini-on-ai.com/assets/[name]-og.png">
```

### Page sections (in order)

1. **Hero** — Gradient headline (`<h1>`), 1-line subheadline (18px, muted), primary CTA button ("Add to Chrome — Free"), secondary link ("See how it works ↓"). Pick one accent color per extension.

2. **How it works** — 3 numbered steps with a screenshot or illustration per step.

3. **Features grid** — 6 cards: icon (emoji or SVG) + bold title + 1-line description. Focus on concrete outcomes, not "AI-powered" fluff.

4. **Pricing table** — Free vs Pro columns. List every feature with ✓ or ✗. Show price prominently. Mention LTD option if deals are in progress.

5. **FAQ** — 5–6 Q&A pairs. Always cover:
   - Privacy / what data is accessed
   - AI limitations (not a substitute for professional advice)
   - Supported content types / platforms
   - Free vs Pro difference
   - How to delete data (GDPR)

6. **JSON-LD structured data** (FAQPage schema) — mirror the HTML FAQ exactly. Improves Google rich results.

### What NOT to include
- Roadmap items or "coming soon" features — only what works today
- "AI-powered" as a headline — use the specific action verb instead
- Screenshots of non-existent UI states

---

## 9. CWS Listing Formula

**Name:** ≤45 chars — `[ProductName] — [Benefit Phrase]`
Example: "ClauseGuard — AI Contract & NDA Analyzer"

**Short description:** ≤132 chars — start with a strong verb, include primary keyword, end with target audience or differentiator.
Example: "Spot red flags in any contract before you sign. Free AI contract analyzer for freelancers and teams."

**Detailed description structure (5000 chars max):**
```
[Bold headline — same as name]

[1-paragraph intro: what it does, who it's for, key differentiator]

HOW IT WORKS:
1. [Step one — install/open]
2. [Step two — core action]
3. [Step three — result]

WHAT YOU GET:
✓ [Feature 1]
✓ [Feature 2]
✓ [Feature 3]
✓ [Feature 4]
✓ [Feature 5]
✓ [Feature 6]
✓ [Feature 7]

PLANS:
Free — [3 core features]
Pro ($7/month) — Everything in Free + [premium features]
Lifetime Deal — Available via [mini-on-ai.com/[name]]

PRIVACY:
[What data is accessed. What is NOT stored. Anonymous-first model explanation.]

⚠ [ProductName] is an AI tool and does not provide [legal/financial/professional] advice.

Built by mini-on-ai.com
```

**Screenshots:** 5 at 1280×800 pixels
1. Input state (empty or with sample input, UI visible)
2. Main output (core AI result)
3. Detail / drill-down view
4. Premium feature (Pro-gated)
5. Full-page / expanded view or alternative use case

**Keywords:** research before writing. Use: `[primary keyword], AI, Chrome extension, free, [target user], [use case keyword], [competitor alternative keyword]`

---

## 10. Distribution Checklist (run in this exact order)

```
[ ] 0. Sync shared code:     python3 scripts/sync_shared.py     (copies shared.js + shared.css, runs node --check)
[ ] 0. Syntax check all:     python3 scripts/check_syntax.py    (catch syntax errors before packaging)
[ ] 1. Deploy worker:        cd {name}/worker && npx wrangler deploy
[ ] 2. Run D1 migrations (pro_source column + ltd_codes table)
[ ] 3. Build CWS zip:
        cd {name} && zip -r store-assets/{name}-{version}.zip . \
          --exclude "worker/*" --exclude "store-assets/*" \
          --exclude ".DS_Store" --exclude "*/.DS_Store" --exclude "*.zip"
[ ] 3b. Validate zip:        python3 scripts/validate_zip.py {name}
[ ] 4. Upload zip to CWS dashboard + update listing copy + screenshots
[ ] 5. Update site/{name}.html — change "pending review" to "Live on CWS", add real install URL
[ ] 6. python3 scripts/update_site.py --rebuild-all && git push
[ ] 7. Submit to AlternativeTo (alternativeto.net/add) — wait if weekend, they pause submissions
[ ] 8. Submit to SaaSHub (saashub.com/add-product)
[ ] 9. Submit to G2 (g2.com/products/new)
[ ] 10. Email LTD marketplaces: DealFuel → RocketHub → DealMirror → PitchGround → SaaSMantra
[ ] 11. Write 1 commercial-intent blog post: python3 scripts/generate_blog_post.py --topic "[keyword phrase]"
[ ] 12. Update factory_state.md and distribution_state.md
```

**Smoke test before uploading to CWS (load unpacked in Chrome):**
```
[ ] Extension loads without console errors
[ ] shared.js and shared.css appear in DevTools > Network
[ ] Copy button: shows "✓ Copied!" → resets after 2s
[ ] Dark mode toggle: persists after popup close/reopen (check localStorage key is {name}-theme)
[ ] Full-page report (if applicable): content fills viewport, print button works
[ ] Analyze/core flow: input → result renders → context restored on reopen
[ ] Account tab: shows correct tier, LTD redemption field present
```

**LTD outreach email template:**
```
Subject: Partnership inquiry — [ProductName] Chrome Extension

Hi [Name],

I'm the developer of [ProductName], a Chrome extension that [one-line description].

It's live on the Chrome Web Store with [X] installs and currently priced at $7/month.
I'd like to discuss a lifetime deal listing on [Platform].

Landing page: https://mini-on-ai.com/[name].html
CWS listing: [CWS URL]

Happy to provide demo access. Let me know if you need anything.

[Name]
```

---

## 11. Narrative Formula

**The pitch structure (use everywhere — popup store description, landing page hero, blog posts, LTD outreach):**

```
Problem:  [User] wastes time manually [doing X], risking [bad outcome].
Solution: [ProductName] is a free Chrome extension that [does X automatically]
          without [the painful part].
Proof:    [Specific technical feature that builds trust] — live on Chrome Web Store.
CTA:      Add to Chrome — Free
```

**Examples from live extensions:**
- ClauseGuard: "Freelancers sign contracts without reading the fine print, risking hidden auto-renewals and one-sided IP grabs. ClauseGuard reads the contract for you and flags every risky clause in seconds — no legal background needed."
- InvoiceGuard: "Freelancers lose thousands chasing unpaid invoices manually across Gmail. InvoiceGuard scans your inbox, tracks every invoice, and generates a polished follow-up email in one click."

**Word rules:**
- ✓ Use: scans, flags, generates, tracks, extracts, exports, detects
- ✗ Avoid: AI-powered, cutting-edge, revolutionary, next-generation, seamless
- ✗ Avoid em-dashes in CWS listings (some platforms strip them)

---

## 12. Accent Color Selection

Pick one color per extension. Apply to: hero gradient, badge, CTA button, status indicators.

| Extension | Color | Hex | Why |
|-----------|-------|-----|-----|
| ClauseGuard | Indigo | `#6366F1` | Legal/professional |
| InvoiceGuard | Emerald | `#10B981` | Money/success |
| Next extension | Pick from: Amber `#F59E0B`, Rose `#F43F5E`, Sky `#0EA5E9`, Violet `#8B5CF6` | — | Match the domain |

---

## File Structure for a New Extension

```
{name}/
├── manifest.json
├── icons/
│   ├── icon-16.png          # generated by scripts/generate_icons.py
│   ├── icon-48.png
│   ├── icon48.png           # copy of icon-48.png (Chrome needs both naming conventions)
│   ├── icon-128.png
│   └── icon128.png          # copy of icon-128.png
├── popup/
│   ├── popup.html           # START FROM: cp _shared/popup-shell.html {name}/popup/popup.html
│   ├── popup.js             # calls initDarkMode(), escHtml(), copyText() from shared.js
│   ├── popup.css            # extension-specific styles only; :root tokens here
│   ├── shared.js            # AUTO-GENERATED by sync_shared.py — do not edit
│   ├── shared.css           # AUTO-GENERATED by sync_shared.py — do not edit
│   ├── fullpage.html        # printable report (if extension has a full-page view)
│   └── fullpage.js          # reads from chrome.storage.local, calls escHtml() from shared.js
├── background/
│   └── service-worker.js
├── options/
│   ├── options.html
│   └── options.js
├── content/               # only if DOM injection needed
│   ├── {name}.js
│   └── {name}.css
├── store-assets/
│   ├── cws-listing-copy.md
│   ├── screenshot-1-input.png
│   ├── screenshot-2-output.png
│   ├── screenshot-3-detail.png
│   ├── screenshot-4-premium.png
│   ├── screenshot-5-fullpage.png
│   └── {name}-{version}.zip   # built at release time
└── worker/
    ├── wrangler.toml
    ├── package.json
    └── src/
        ├── index.js           # router + shared helpers
        ├── billing.js         # Stripe + LTD
        ├── [feature].js       # core AI action
        └── ltd.js             # LTD code redemption
```

---

## Reference Implementations

- `clauseguard/` — popup-only (no content script), contract analysis, clause library, compare feature (v1.3.1+)
- `invoiceguard/` — content script (Gmail DOM injection), invoice tracking, badge alerts, reminder generation (v1.1.1+)
- `jobguard/` — popup + fullpage report, page text extraction (JSON-LD → semantic → body fallback), history tab (v1.0.1+)
- `clauseguard/worker/src/billing.js` — Stripe webhook pattern (copy `verifyStripeSignature`)
- `clauseguard/worker/src/ltd.js` — LTD redemption module (copy and adapt per extension)
- `site/clauseguard.html` — landing page structure (indigo accent, legal domain)
- `site/invoiceguard.html` — landing page structure (indigo accent, finance domain)

## Shared Infrastructure

| File | Purpose |
|------|---------|
| `_shared/popup-shell.html` | **Copy-once** annotated HTML template for new extensions — start every new popup.html from this |
| `_shared/utils.js` | Canonical JS utilities — edit here, never in per-extension copies |
| `_shared/base.css` | Canonical shared CSS — edit here, never in per-extension copies |
| `_shared/claude-design-brief.md` | Paste into claude.ai/design to get unified tokens, component CSS/HTML, SVG icons |
| `scripts/sync_shared.py` | Copies shared files into all extensions + runs node --check |
| `scripts/check_syntax.py` | Syntax-checks all 13+ JS files across all extensions |
| `scripts/validate_zip.py` | Validates zip contents before CWS upload |
