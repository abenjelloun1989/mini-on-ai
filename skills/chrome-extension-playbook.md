# Skill: chrome-extension-playbook

## Purpose
Complete playbook for building, hardening, monetizing, and distributing a Chrome extension. Extracted from two shipped extensions (ClauseGuard v1.3.0, InvoiceGuard v1.1.0). Read this at the start of any new extension project.

## Trigger
User says anything like: "let's build a new chrome extension", "new extension", "next extension idea", "build an extension for X"

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

```js
// In DOMContentLoaded — runs before render to avoid flash
(function() {
  const toggle = document.getElementById("darkModeToggle");
  const stored = localStorage.getItem("ig-theme");
  if (stored === "light") {
    document.body.classList.add("light-mode");
    if (toggle) toggle.textContent = "☀";
  }
  if (toggle) {
    toggle.addEventListener("click", function() {
      const isLight = document.body.classList.toggle("light-mode");
      localStorage.setItem("ig-theme", isLight ? "light" : "dark");
      toggle.textContent = isLight ? "☀" : "☾";
    });
  }
})();
```

```css
/* CSS variables for dark (default) */
:root {
  --bg: #0f0f1a;
  --surface: #1a1a2e;
  --border: #2a2a45;
  --text: #e2e2f0;
  --text-muted: #8b8bab;
  --accent: #6366f1;  /* change per extension */
}

/* Light mode overrides */
body.light-mode {
  --bg: #ffffff;
  --surface: #f5f5f7;
  --border: #e5e5ea;
  --text: #1d1d1f;
  --text-muted: #6e6e73;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
```

### Copy buttons — shared helper (never silent)

```js
function copyText(btn, text, resetLabel = "📋 Copy") {
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = "✓ Copied!";
    setTimeout(() => { if (btn.isConnected) btn.textContent = resetLabel; }, 2000);
  }).catch(() => {
    btn.textContent = "Copy failed";
    setTimeout(() => { if (btn.isConnected) btn.textContent = resetLabel; }, 2000);
  });
}
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

### HTML escaping (always escape user-facing strings)

```js
function escHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
```

---

## 7. Landing Page Formula (`site/{name}.html`)

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

## 8. CWS Listing Formula

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

## 9. Distribution Checklist (run in this exact order)

```
[ ] 1. Deploy worker: cd {name}/worker && npx wrangler deploy
[ ] 2. Run D1 migrations (pro_source column + ltd_codes table)
[ ] 3. Build CWS zip: cd {name} && zip -r ../store-assets/{name}-{version}.zip . --exclude "worker/*" --exclude "store-assets/*" --exclude ".DS_Store"
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

## 10. Narrative Formula

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

## 11. Accent Color Selection

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
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
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

- `clauseguard/` — popup-only extension (no content script), contract analysis, clause library, compare feature
- `invoiceguard/` — content script extension (Gmail DOM injection), invoice tracking, badge alerts, reminder generation
- `clauseguard/worker/src/billing.js` — Stripe webhook pattern (copy the verifyStripeSignature function)
- `clauseguard/worker/src/ltd.js` — LTD redemption module (copy and adapt for each new extension)
- `site/clauseguard.html` — landing page structure (indigo accent, legal domain)
- `site/invoiceguard.html` — landing page structure (emerald accent, finance domain)
