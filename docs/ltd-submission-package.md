# LTD Submission Package — ClauseGuard

Three platforms, step-by-step. Do them in this order: PitchGround first (self-serve, live today), SaaSMantra second (application form, ~1 week reply), DealMirror third (email-based).

---

## Before you start: 1 prerequisite (30 min of code)

**The LTD redemption flow doesn't exist yet.** When someone buys a lifetime deal on any of these platforms, they get a code (e.g. `CG-XXXX-XXXX`). Your extension needs to accept that code and activate Pro permanently — right now it only knows about Stripe subscriptions.

You need to build this before activating any listing:

1. **D1 table `ltd_codes`**: columns `code TEXT PRIMARY KEY`, `redeemed_by TEXT`, `redeemed_at INTEGER`
2. **Worker endpoint `POST /redeem-ltd`**: validates the code exists + hasn't been redeemed, marks it redeemed, sets the user's account to `pro_lifetime = true`
3. **Extension UI**: a text field in the Account/Settings tab: "Have a lifetime deal code? Enter it here → [Redeem]"

Without this, you can list but can't activate. Build this before you set the listing live.

---

## ─── PLATFORM 1: PitchGround Marketplace ───

**Why first:** Self-serve, no approval needed, live within hours. 70% revenue to you.

**Revenue split:** You keep 70%. PitchGround takes 30%. Payout after 60 days.

**Recommended LTD price:** $49 (PitchGround's data shows listings starting at $49 get 10× more views than those starting higher).

**Time to complete:** ~45 minutes.

---

### Step 1 — Create your account
1. Go to **https://app.pitchground.com/auth/sign-up**
2. Sign up with `hello@mini-on-ai.com`
3. Verify your email
4. You're now a registered vendor

---

### Step 2 — Start a new listing
1. Go to **https://app.pitchground.com/vendor/my-products**
2. Click **"List New Product to Marketplace"**
3. You'll be walked through 7 tabs: General Info → Media → Content → Pricing → Metadata → Video → Vendor Settings

---

### Step 3 — General Info tab

| Field | What to enter |
|-------|---------------|
| **Name** | `ClauseGuard` |
| **Slug** | `clauseguard-ltd` (min 6 chars) |
| **Date From** | Today |
| **Date To** | 3 months from today (their recommendation — gives time for reviews and momentum) |
| **Website Title** | `ClauseGuard — AI Contract Red Flag Detector for Freelancers` |
| **Website URL** | `https://mini-on-ai.com/clauseguard.html` |
| **Support Email** | `hello@mini-on-ai.com` |
| **Knowledgebase URL** | `https://mini-on-ai.com/clauseguard.html#faq` (the FAQ section you just built) |
| **Facebook Group URL** | Leave blank or enter `https://mini-on-ai.com` — this field is listed as optional in practice |
| **Roadmap URL** | Leave blank or enter `https://mini-on-ai.com/clauseguard.html` |

Click **Continue**.

---

### Step 4 — Media tab

**Cover image (required):**
- Size: 1920×1080 px, 16:9 ratio, max 300KB, JPG or PNG
- You already have `clauseguard/store-assets/marquee-1400x560.png` — resize it to 1920×1080 for this (free: use [squoosh.app](https://squoosh.app) or Canva)
- Simple layout: dark background, "ClauseGuard" logo top-left, tagline "AI Contract Review Chrome Extension" centered, a screenshot of the analysis panel on the right

**Screenshots (upload 3-5 from store-assets/):**
- `screenshot-1-input-state.png` — caption: "Paste any contract — results in 15 seconds"
- `screenshot-2-risk-score.png` — caption: "Risk score 1–10 plus every red flag explained in plain English"
- `screenshot-3-clause-rewrite.png` — caption: "Copy-ready clause rewrites for every risky section"
- `screenshot-4-missing-protections.png` — caption: "Spots missing protections your lawyer would charge $300/hr to find"
- `screenshot-5-pricing.png` — caption: "Free: 3 analyses/month. Pro: unlimited. LTD: pay once, use forever."

---

### Step 5 — Content tab

**Short description (200 chars max):**
```
AI Chrome extension that analyzes any contract for red flags, risky clauses, and missing protections in 15 seconds. Free to install — pay once with this LTD.
```

**Overview (key features section — write in bullet format):**
```
ClauseGuard is a free AI contract review Chrome extension built for freelancers, consultants, and small business owners who sign contracts regularly but can't afford a lawyer for every NDA or service agreement.

WHAT IT DOES:
• Analyzes any contract for red flags, risky clauses, and unfair terms in under 15 seconds
• Gives you a risk score (1–10) so you know at a glance how dangerous the contract is
• Explains every red flag in plain English — no legal jargon
• Suggests ready-to-use rewordings for risky clauses (copy with one click)
• Spots missing protections (late payment penalties, liability caps, IP ownership, etc.)
• Provides 2–4 negotiation tips tailored to your specific contract

WHAT IT WORKS ON:
• Freelance contracts & service agreements
• NDAs (non-disclosure agreements)
• Employment contracts
• SaaS terms of service
• Lease agreements
• Any contract text you paste in

HOW IT WORKS:
1. Open any contract webpage or Google Doc (or paste text into the popup)
2. Click "Analyze" — results appear in under 15 seconds
3. Review your risk score, red flags, and copy the suggested rewrites

THIS LTD INCLUDES:
• Unlimited contract analyses (no monthly limit, forever)
• Full risk scoring and red flag detection
• Suggested clause rewrites for every risky section
• Missing protections check
• Contract comparison (diff two versions)
• PDF export
• Saved clause library
• All future Pro features

WHO IT'S FOR:
Freelancers, consultants, indie hackers, small agency owners, startup founders — anyone who signs contracts and wants a fast AI first-pass before involving (or instead of) a lawyer for routine agreements.

⚠️ ClauseGuard is for informational purposes only and does not constitute legal advice. For high-stakes contracts, consult a qualified attorney.
```

**FAQ section (copy each Q&A):**

Q: Does ClauseGuard replace a lawyer?
A: No — it's a first-pass AI review tool. It helps you understand what you're signing, spot potential red flags, and prepare smarter questions before you consult a lawyer. For high-stakes contracts, always involve an attorney.

Q: What types of contracts can it analyze?
A: Freelance contracts, NDAs, employment agreements, SaaS terms of service, service agreements, lease contracts, and any other legal text you paste in.

Q: How do I redeem my LTD code?
A: Install ClauseGuard from the Chrome Web Store, open the extension, go to Account → "Enter lifetime deal code" and paste your PitchGround code. Your account is instantly upgraded to Pro lifetime.

Q: Is my contract data private?
A: Yes. ClauseGuard uses a randomly generated anonymous ID — no name or email collected. Contract text is processed for analysis and deleted after 30 days. We never sell or share your data.

Q: What browser does it work on?
A: Chrome and any Chromium-based browser (Edge, Brave, Arc).

---

### Step 6 — Pricing tab

Set **one plan** (keep it simple for your first LTD):

| Field | Value |
|-------|-------|
| **Plan Name** | `Lifetime — Unlimited` |
| **Active?** | Yes |
| **Original Price** | `$84` (= $7/month × 12 months) |
| **PitchGround Price** | `$49` |
| **Discount shown** | ~42% off |
| **Key Features** | Unlimited analyses · Full red flag detection · Suggested rewrites · Contract diff · PDF export · Clause library · All future Pro features |
| **Redemption Instructions** | 3 steps max (see below) |

**Redemption instructions (exactly 3 steps):**
```
1. Install ClauseGuard from the Chrome Web Store: https://chromewebstore.google.com/detail/clauseguard-ai-contract-n/nknbofmcikmpifeopelgngnhdcajffdl
2. Click the ClauseGuard icon in your browser toolbar to open the extension
3. Go to Account tab → enter your PitchGround code in the "Lifetime deal code" field → click Redeem
```

**Coupon codes:** PitchGround generates these automatically (5,000 codes per plan). You don't create them — they'll show up in your dashboard once the listing is live.

---

### Step 7 — Video tab (optional but recommended)

Add your Loom demo video URL here (see "Recording the Loom demo" section below).
If you skip this, the listing still goes live — add it later.

---

### Step 8 — Vendor Settings tab

- **Slack webhook** (optional): skip unless you want real-time sale notifications
- Click **Save & Publish**

Your listing is now live in the PitchGround Marketplace. Share the URL with nobody — wait for organic discovery. PitchGround has its own email list and featured slots; self-serve listings get organic marketplace traffic.

---

## ─── PLATFORM 2: SaaSMantra ───

**Why:** Application-based but indie-friendly. Smaller audience than AppSumo but much higher acceptance rate. Responds within 1-2 weeks.

**Revenue split:** Similar to PitchGround, ~30% commission.

**Time to complete:** ~15 minutes to fill the form.

---

### Step 1 — Go to the form
Open: **https://saas-mantra.paperform.co/**

---

### Step 2 — Fill in every field

**Product URL:**
```
https://mini-on-ai.com/clauseguard.html
```

**What problem does your product solve?**
```
Freelancers and small business owners sign contracts regularly — NDAs, service agreements, employment contracts — but can't justify $300/hr legal fees for every routine document. ClauseGuard gives them an AI-powered first-pass review in 15 seconds: risk score, red flags explained in plain English, suggested clause rewrites, and negotiation tips. It turns a contract from a stressful unknown into something they can actually understand and negotiate with confidence.
```

**Who are your Top 5 Competitors? (max 100 chars)**
```
LawGeex, Ironclad, Kira Systems, LegalSifter, SpellBook
```

**What are your top two goals for this promotion? (select up to 2)**
- ✓ Acquiring New Users
- ✓ Generate Seed money/revenue from the promotion

**What categories does your product fit in? (select up to 2)**
- ✓ Productivity
- ✓ Sales/Marketing

**What's your role in the company?**
```
Founder
```

**What's your Official Email id?**
```
hello@mini-on-ai.com
```

**What's the alternate way to contact you?**
```
hello@mini-on-ai.com (email only — async communication preferred)
```

---

### Step 3 — Submit
Click submit. You'll get a confirmation email. SaaSMantra typically replies within 5-10 business days. If no reply in 2 weeks, email `team@saasmantra.com` with your submission recap.

---

## ─── PLATFORM 3: DealMirror ───

**Why:** Smaller but very indie-friendly. Email-based submission — no formal form. Easy to get listed.

**How to submit:** DealMirror doesn't have a public self-serve portal. Contact them directly by email.

---

### Step 1 — Send this email

**To:** `deals@dealmirror.com`
**Subject:** `Partnership enquiry — ClauseGuard (AI contract review Chrome extension)`

**Body:**
```
Hi DealMirror team,

I'd like to list ClauseGuard as a lifetime deal on DealMirror.

ClauseGuard is a free AI contract review Chrome extension — it analyzes any contract for red flags, risky clauses, and missing protections in under 15 seconds. Live on the Chrome Web Store.

Quick overview:
• Product: AI contract review + red flag detection Chrome extension
• CWS listing: https://chromewebstore.google.com/detail/clauseguard-ai-contract-n/nknbofmcikmpifeopelgngnhdcajffdl
• Landing page: https://mini-on-ai.com/clauseguard.html
• Current price: $7/month (Pro)
• Proposed LTD price: $49 lifetime
• Target customer: freelancers, consultants, small agency owners
• Top 5 competitors: LawGeex, Ironclad, Kira Systems, LegalSifter, SpellBook

I'm happy to provide a demo video, screenshots, and any additional information you need.

Could you let me know your process and what you'd need from me to get listed?

Best,
mini-on-ai team
hello@mini-on-ai.com
```

---

### Step 2 — Follow up
If no reply in 5 business days, follow up once:

```
Subject: Re: Partnership enquiry — ClauseGuard (AI contract review Chrome extension)

Hi, following up on my email from [date]. Happy to provide any additional details. Is DealMirror currently accepting new Chrome extension listings?
```

---

## ─── Recording the Loom demo (silent screen-record) ───

**Time needed:** 20–30 minutes total (recording + basic trim). No voice, no face. Screen only.

**Install Loom:** https://loom.com — free plan allows unlimited recordings.

**Before you record:**

1. Prepare a sample contract. Use this free public NDA from Docracy:
   https://www.docracy.com/6180/standard-mutual-nda
   Open it in a browser tab.
2. Open clauseguard.html in another tab.
3. Have the Chrome extension pinned in your toolbar.
4. Set your browser zoom to 110% for readability.
5. Close all other tabs. Clean desktop background.

**Recording script (no voice needed — visuals tell the story):**

| Seconds | What to show |
|---------|--------------|
| 0–10 | Open clauseguard.html — scroll slowly from top to bottom so viewers see the hero, features, and pricing |
| 10–20 | Click "Add to Chrome" button (opens CWS listing — shows it's real and live) |
| 20–30 | Switch to the NDA tab — show it's a real contract page |
| 30–40 | Click the ClauseGuard extension icon in the toolbar |
| 40–55 | Click "Analyze current page" — wait for results (the 15-second spinner is fine to show) |
| 55–80 | Slowly scroll through the results panel: risk score → red flags → click one to expand → suggested rewrite → copy button |
| 80–100 | Click "Missing Protections" section, show what's flagged |
| 100–115 | Click "Negotiation Tips" section |
| 115–130 | Click "Upgrade to Pro" button — show the pricing modal/prompt |
| 130–150 | Switch back to clauseguard.html pricing section — end on the $7/month → $49 LTD framing |

**After recording:**
- Trim the start and end in Loom's editor (takes 2 minutes)
- Copy the share link
- Use this link in:
  - PitchGround listing → Video tab
  - Any follow-up email to SaaSMantra or DealMirror

---

## Checklist — do these in order

### Before listing goes live:
- [ ] Build LTD code redemption in ClauseGuard Worker + extension UI (30 min)
- [ ] Record Loom demo (30 min)
- [ ] Resize marquee image to 1920×1080 for PitchGround cover (5 min at squoosh.app)

### Submissions:
- [ ] PitchGround Marketplace — register + fill all 7 tabs + publish
- [ ] SaaSMantra — fill the paperform and submit
- [ ] DealMirror — send the email above

### After submitting:
- [ ] Track replies in `hello@mini-on-ai.com`
- [ ] Follow up SaaSMantra if no reply in 2 weeks
- [ ] Follow up DealMirror if no reply in 5 days
- [ ] Once first sale comes in: check D1 for redeemed codes and make sure the flow works end-to-end

---

## Expected outcomes (realistic)

| Platform | Timeline | Expected result |
|----------|----------|-----------------|
| PitchGround Marketplace | Live same day | 0-5 sales in first month organically (self-serve has low discoverability vs featured deals) |
| SaaSMantra (if accepted) | 3-6 weeks | 50-300 LTD sales on launch day · $735-4,410 gross · ~$500-3,000 net after commission |
| DealMirror (if accepted) | 4-8 weeks | 30-150 LTD sales · $440-2,200 gross · ~$300-1,500 net |

The PitchGround self-serve listing is low-traffic but gets your product indexed and lets you practice the redemption flow before a bigger launch. SaaSMantra and DealMirror are the real revenue bets.

---

## Sources

- [PitchGround Marketplace Guide](https://marketplace-guide.pitchground.com/general-info)
- [PitchGround Pricing Guide](https://marketplace-guide.pitchground.com/pricing)
- [PitchGround Terms & FAQs](https://marketplace-guide.pitchground.com/marketplace-terms-and-faqs)
- [SaaS Mantra Partnership Form](https://saas-mantra.paperform.co/)
- [AppSumo Vetting Criteria (for reference — why we skipped them)](https://appsumo.com/blog/how-we-vet-select-partners)
