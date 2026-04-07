/**
 * Cloudflare Worker — "Build Your Own" product generator
 *
 * Routes:
 *   POST /generate      — generate a custom product, store in KV, return preview
 *   POST /checkout      — create Stripe Checkout session ($9)
 *   GET  /download      — verify Stripe payment, serve ZIP
 *   POST /ats-analyze   — ATS resume analysis, store in KV, return preview
 *   POST /ats-checkout  — create Stripe Checkout session ($5) for full ATS analysis
 *   GET  /ats-download  — verify Stripe payment, return full ATS analysis JSON
 *
 * CF Environment variables (Settings → Variables):
 *   ANTHROPIC_API_KEY   (Secret) — Anthropic API key
 *   STRIPE_SECRET_KEY   (Secret) — Stripe secret key (sk_live_... or sk_test_...)
 *   TURNSTILE_SECRET    (Secret, optional) — Cloudflare Turnstile secret for bot protection
 *
 * CF KV Namespace binding (Settings → Variables → KV Namespace Bindings):
 *   PRODUCTS_KV — create a KV namespace named "products" and bind it as PRODUCTS_KV
 *
 * Deploy:
 *   1. Create KV namespace "products" in Cloudflare dashboard → Workers & Pages → KV
 *   2. Paste this file into a new Worker (Workers & Pages → Create → Worker)
 *   3. Bind KV: Worker → Settings → Variables → KV Namespace Bindings → Add: PRODUCTS_KV → products
 *   4. Add secrets: ANTHROPIC_API_KEY, STRIPE_SECRET_KEY (and optionally TURNSTILE_SECRET)
 *   5. Set success_url domain in SITE_URL below if different
 */

const ALLOWED_ORIGIN = "https://mini-on-ai.com";
const SITE_URL = "https://mini-on-ai.com";

const CATEGORY_LABELS = {
  "prompt-packs": "Prompt Pack",
  "checklist":    "Checklist",
  "mini-guide":   "Mini Guide",
  "swipe-file":   "Swipe File",
};

// ─────────────────────────────────────────────────────────────────────────────
// Main dispatch
// ─────────────────────────────────────────────────────────────────────────────

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return corsOk();

    const url  = new URL(request.url);
    const path = url.pathname;

    if (path === "/generate" && request.method === "POST") {
      return handleGenerate(request, env);
    }
    if (path === "/checkout" && request.method === "POST") {
      return handleCheckout(request, env);
    }
    if (path === "/download" && request.method === "GET") {
      return handleDownload(url, env);
    }
    if (path === "/ats-analyze" && request.method === "POST") {
      return handleAtsAnalyze(request, env);
    }
    if (path === "/ats-checkout" && request.method === "POST") {
      return handleAtsCheckout(request, env);
    }
    if (path === "/ats-download" && request.method === "GET") {
      return handleAtsDownload(url, env);
    }

    return corsJson({ error: "Not found" }, 404);
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// /generate — call Anthropic, store in KV, return preview
// ─────────────────────────────────────────────────────────────────────────────

async function handleGenerate(request, env) {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";

  // Rate limit: max 3 generations per IP per hour
  if (!(await checkRateLimit(env, ip))) {
    return corsJson({ error: "Rate limit reached (3 per hour). Try again later." }, 429);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return corsJson({ error: "Invalid JSON" }, 400);
  }

  const description = (body.description || "").trim();
  const category    = (body.category || "prompt-packs").trim();

  if (!description || description.length < 10) {
    return corsJson({ error: "Please describe your use case (at least 10 characters)." }, 400);
  }
  if (description.length > 1000) {
    return corsJson({ error: "Description too long (max 1000 characters)." }, 400);
  }
  if (!CATEGORY_LABELS[category]) {
    return corsJson({ error: "Invalid category." }, 400);
  }

  // Optional Turnstile bot check
  if (env.TURNSTILE_SECRET) {
    const token = body.cf_turnstile_response || "";
    const valid = await validateTurnstile(env.TURNSTILE_SECRET, token, ip);
    if (!valid) return corsJson({ error: "Bot check failed. Please try again." }, 403);
  }

  // Generate with Anthropic Haiku
  let generated;
  try {
    generated = await generateProduct(env.ANTHROPIC_API_KEY, description, category);
  } catch (e) {
    console.error("Generation error:", e.message);
    return corsJson({ error: "Generation failed. Please try again." }, 500);
  }

  // Store full product in KV (24h TTL)
  const id = crypto.randomUUID();
  await env.PRODUCTS_KV.put(
    `prod:${id}`,
    JSON.stringify({ ...generated, category, description }),
    { expirationTtl: 86400 }
  );

  // Return preview (first 5 items only)
  const items       = Array.isArray(generated.items) ? generated.items : [];
  const preview     = items.slice(0, 5);
  const total_count = items.length;

  return corsJson({ id, title: generated.title, category,
    category_label: CATEGORY_LABELS[category], preview, total_count });
}

// ─────────────────────────────────────────────────────────────────────────────
// /checkout — create Stripe Checkout session
// ─────────────────────────────────────────────────────────────────────────────

async function handleCheckout(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return corsJson({ error: "Invalid JSON" }, 400);
  }

  const { product_id } = body;
  if (!product_id) return corsJson({ error: "Missing product_id." }, 400);

  // Verify the product actually exists in KV (can't fake a product_id)
  const productJson = await env.PRODUCTS_KV.get(`prod:${product_id}`);
  if (!productJson) {
    return corsJson({ error: "Product not found or expired. Please generate again." }, 404);
  }

  const product = JSON.parse(productJson);

  // Create Stripe Checkout session
  const stripeRes = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: {
      "Authorization":  `Bearer ${env.STRIPE_SECRET_KEY}`,
      "Content-Type":   "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      "payment_method_types[]":                          "card",
      "line_items[0][price_data][currency]":             "usd",
      "line_items[0][price_data][unit_amount]":          "900",
      "line_items[0][price_data][product_data][name]":   product.title,
      "line_items[0][price_data][product_data][description]": product.description || "",
      "line_items[0][quantity]":                         "1",
      "mode":                                            "payment",
      "metadata[product_id]":                            product_id,
      "success_url": `${SITE_URL}/build.html?session_id={CHECKOUT_SESSION_ID}`,
      "cancel_url":  `${SITE_URL}/build.html`,
    }),
  });

  if (!stripeRes.ok) {
    const err = await stripeRes.text();
    console.error("Stripe error:", err);
    return corsJson({ error: "Payment setup failed. Please try again." }, 500);
  }

  const session = await stripeRes.json();
  return corsJson({ checkout_url: session.url });
}

// ─────────────────────────────────────────────────────────────────────────────
// /download — verify Stripe payment, serve ZIP
// ─────────────────────────────────────────────────────────────────────────────

async function handleDownload(url, env) {
  const sessionId = url.searchParams.get("session_id");
  if (!sessionId) return corsJson({ error: "Missing session_id." }, 400);

  // Replay protection — each paid session can only download once
  const downloadedKey = `downloaded:${sessionId}`;
  const alreadyServed = await env.PRODUCTS_KV.get(downloadedKey);
  if (alreadyServed) {
    return new Response(
      "This download link has already been used. Each purchase allows one download. " +
      "Please contact hello@mini-on-ai.com with your Stripe receipt if you need another copy.",
      { status: 410, headers: { "Access-Control-Allow-Origin": ALLOWED_ORIGIN } }
    );
  }

  // Retrieve and verify Stripe session
  const stripeRes = await fetch(
    `https://api.stripe.com/v1/checkout/sessions/${sessionId}`,
    { headers: { "Authorization": `Bearer ${env.STRIPE_SECRET_KEY}` } }
  );

  if (!stripeRes.ok) return corsJson({ error: "Invalid session." }, 400);

  const session = await stripeRes.json();
  if (session.payment_status !== "paid") {
    return corsJson({ error: "Payment not completed." }, 402);
  }

  const productId = session.metadata?.product_id;
  if (!productId) return corsJson({ error: "No product linked to this payment." }, 400);

  // Get product from KV
  const productJson = await env.PRODUCTS_KV.get(`prod:${productId}`);
  if (!productJson) {
    return new Response(
      "Your product has expired (products are stored for 24h). " +
      "Please contact hello@mini-on-ai.com with your Stripe receipt.",
      { status: 410, headers: { "Access-Control-Allow-Origin": ALLOWED_ORIGIN } }
    );
  }

  const product = JSON.parse(productJson);
  const zip     = buildZip(product);
  const name    = sanitizeFilename(product.title);

  // Mark this session as downloaded (24h TTL matches product TTL)
  await env.PRODUCTS_KV.put(downloadedKey, "1", { expirationTtl: 86400 });

  return new Response(zip, {
    headers: {
      "Content-Type":        "application/zip",
      "Content-Disposition": `attachment; filename="${name}.zip"`,
      "Cache-Control":       "no-store",
      "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    },
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// /ats-analyze — ATS resume analysis, store in KV, return preview
// ─────────────────────────────────────────────────────────────────────────────

const ATS_PROMPT = (resumeText, jobDescription, jobTitle) => `Analyze this resume against the job description for ATS (Applicant Tracking System) compatibility. Return ONLY valid JSON, no markdown fences:

{
  "ats_score": <integer 0-100>,
  "keyword_analysis": {
    "matched": ["keyword1", "keyword2"],
    "missing": ["keyword1", "keyword2"],
    "match_rate": <float 0.0-1.0>
  },
  "section_feedback": [
    {"section": "summary", "status": "strong|weak|missing", "suggestion": "specific actionable suggestion"},
    {"section": "experience", "status": "strong|weak|missing", "suggestion": "specific actionable suggestion"},
    {"section": "skills", "status": "strong|weak|missing", "suggestion": "specific actionable suggestion"},
    {"section": "education", "status": "strong|weak|missing", "suggestion": "specific actionable suggestion"}
  ],
  "improved_bullets": [
    {"original": "original bullet from resume", "improved": "rewritten version with keywords and metrics", "reason": "why this is better for ATS"}
  ],
  "formatting_tips": ["tip1", "tip2"],
  "overall": "one paragraph recommendation"
}

Rules:
- ats_score: base on keyword match rate, section completeness, and formatting quality
- matched/missing: extract actual skills, technologies, and requirements from the job description
- improved_bullets: pick up to 5 weakest bullets from the resume and rewrite them to include relevant keywords and quantifiable metrics
- Be specific and actionable in all suggestions

Resume:
${resumeText}

Job Description:
${jobDescription}
${jobTitle ? `\nJob Title: ${jobTitle}` : ""}`;

async function handleAtsAnalyze(request, env) {
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";

  if (!(await checkRateLimit(env, ip))) {
    return corsJson({ error: "Rate limit reached (3 per hour). Try again later." }, 429);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return corsJson({ error: "Invalid JSON" }, 400);
  }

  const resumeText      = (body.resume_text || "").trim();
  const jobDescription  = (body.job_description || "").trim();
  const jobTitle        = (body.job_title || "").trim();

  if (!resumeText || resumeText.length < 50) {
    return corsJson({ error: "Please paste your full resume (at least 50 characters)." }, 400);
  }
  if (resumeText.length > 10000) {
    return corsJson({ error: "Resume too long (max 10,000 characters)." }, 400);
  }
  if (!jobDescription || jobDescription.length < 30) {
    return corsJson({ error: "Please paste the job description (at least 30 characters)." }, 400);
  }
  if (jobDescription.length > 5000) {
    return corsJson({ error: "Job description too long (max 5,000 characters)." }, 400);
  }

  // Generate ATS analysis with Claude Haiku
  let analysis;
  try {
    const prompt = ATS_PROMPT(resumeText, jobDescription, jobTitle);
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key":         env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
      },
      body: JSON.stringify({
        model:      "claude-haiku-4-5-20251001",
        max_tokens: 2048,
        messages:   [{ role: "user", content: prompt }],
      }),
    });

    if (!resp.ok) throw new Error(`Anthropic ${resp.status}`);

    const data = await resp.json();
    const text = data.content[0].text.trim();
    const clean = text.replace(/^```[a-z]*\n?/m, "").replace(/\n?```$/m, "").trim();
    const match = clean.match(/\{[\s\S]*\}/);
    if (!match) throw new Error("No JSON in response");
    analysis = JSON.parse(match[0]);
  } catch (e) {
    console.error("ATS analysis error:", e.message);
    return corsJson({ error: "Analysis failed. Please try again." }, 500);
  }

  // Store full analysis in KV (24h TTL)
  const id = crypto.randomUUID();
  await env.PRODUCTS_KV.put(
    `ats:${id}`,
    JSON.stringify(analysis),
    { expirationTtl: 86400 }
  );

  // Return preview only (free tier)
  const matched = analysis.keyword_analysis?.matched || [];
  const missing = analysis.keyword_analysis?.missing || [];
  const tips    = analysis.formatting_tips || [];
  const bullets = analysis.improved_bullets || [];

  return corsJson({
    id,
    ats_score:               analysis.ats_score || 0,
    matched_keywords:        matched.slice(0, 3),
    missing_count:           missing.length,
    formatting_tips_preview: tips.slice(0, 2),
    total_improvements:      bullets.length,
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// /ats-checkout — Stripe Checkout for full ATS analysis ($5)
// ─────────────────────────────────────────────────────────────────────────────

async function handleAtsCheckout(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return corsJson({ error: "Invalid JSON" }, 400);
  }

  const { analysis_id } = body;
  if (!analysis_id) return corsJson({ error: "Missing analysis_id." }, 400);

  const stored = await env.PRODUCTS_KV.get(`ats:${analysis_id}`);
  if (!stored) {
    return corsJson({ error: "Analysis not found or expired. Please run a new check." }, 404);
  }

  const stripeRes = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: {
      "Authorization":  `Bearer ${env.STRIPE_SECRET_KEY}`,
      "Content-Type":   "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      "payment_method_types[]":                          "card",
      "line_items[0][price_data][currency]":             "usd",
      "line_items[0][price_data][unit_amount]":          "500",
      "line_items[0][price_data][product_data][name]":   "Full ATS Resume Analysis",
      "line_items[0][price_data][product_data][description]": "Complete keyword analysis, rewritten bullet points, section feedback, and optimization tips",
      "line_items[0][quantity]":                         "1",
      "mode":                                            "payment",
      "metadata[analysis_id]":                           analysis_id,
      "success_url": `${SITE_URL}/ats.html?session_id={CHECKOUT_SESSION_ID}`,
      "cancel_url":  `${SITE_URL}/ats.html`,
    }),
  });

  if (!stripeRes.ok) {
    console.error("Stripe error:", await stripeRes.text());
    return corsJson({ error: "Payment setup failed. Please try again." }, 500);
  }

  const session = await stripeRes.json();
  return corsJson({ checkout_url: session.url });
}

// ─────────────────────────────────────────────────────────────────────────────
// /ats-download — verify payment, return full ATS analysis
// ─────────────────────────────────────────────────────────────────────────────

async function handleAtsDownload(url, env) {
  const sessionId = url.searchParams.get("session_id");
  if (!sessionId) return corsJson({ error: "Missing session_id." }, 400);

  // Replay protection
  const downloadedKey = `ats-downloaded:${sessionId}`;
  const alreadyServed = await env.PRODUCTS_KV.get(downloadedKey);
  if (alreadyServed) {
    return corsJson({ error: "This analysis has already been retrieved. Contact hello@mini-on-ai.com if you need it again." }, 410);
  }

  // Verify Stripe payment
  const stripeRes = await fetch(
    `https://api.stripe.com/v1/checkout/sessions/${sessionId}`,
    { headers: { "Authorization": `Bearer ${env.STRIPE_SECRET_KEY}` } }
  );

  if (!stripeRes.ok) return corsJson({ error: "Invalid session." }, 400);

  const session = await stripeRes.json();
  if (session.payment_status !== "paid") {
    return corsJson({ error: "Payment not completed." }, 402);
  }

  const analysisId = session.metadata?.analysis_id;
  if (!analysisId) return corsJson({ error: "No analysis linked to this payment." }, 400);

  const stored = await env.PRODUCTS_KV.get(`ats:${analysisId}`);
  if (!stored) {
    return corsJson({ error: "Analysis expired (24h). Please run a new check and contact hello@mini-on-ai.com with your receipt." }, 410);
  }

  // Mark as downloaded
  await env.PRODUCTS_KV.put(downloadedKey, "1", { expirationTtl: 86400 });

  const analysis = JSON.parse(stored);
  return corsJson(analysis);
}

// ─────────────────────────────────────────────────────────────────────────────
// Anthropic generation
// ─────────────────────────────────────────────────────────────────────────────

const PROMPTS = {
  "prompt-packs": (desc) => `Generate a prompt pack of exactly 20 AI prompts for: "${desc}"

Return ONLY valid JSON, no markdown fences:
{
  "title": "Short title (5-8 words)",
  "description": "One sentence: who it's for and what it does",
  "items": ["Full prompt text here", ...20 items]
}`,

  "checklist": (desc) => `Generate a practical checklist of exactly 20 actionable items for: "${desc}"

Return ONLY valid JSON, no markdown fences:
{
  "title": "Short title (5-8 words)",
  "description": "One sentence: who it's for and what it does",
  "items": ["Action item text", ...20 items]
}`,

  "mini-guide": (desc) => `Write a focused mini-guide about: "${desc}"

Return ONLY valid JSON, no markdown fences:
{
  "title": "Short title (5-8 words)",
  "description": "One sentence: who it's for and what it does",
  "items": [
    "## Introduction\\n2-3 sentences setting up the problem.",
    "## Step 1: [Name]\\nContent here.",
    "## Step 2: [Name]\\nContent here.",
    "## Step 3: [Name]\\nContent here.",
    "## Step 4: [Name]\\nContent here.",
    "## Conclusion\\nClosing thoughts and next actions."
  ]
}`,

  "swipe-file": (desc) => `Generate a swipe file of 20 copy-ready examples for: "${desc}"

Return ONLY valid JSON, no markdown fences:
{
  "title": "Short title (5-8 words)",
  "description": "One sentence: who it's for and what it does",
  "items": ["Copy-ready example text", ...20 items]
}`,
};

async function generateProduct(apiKey, description, category) {
  const prompt = PROMPTS[category](description);

  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method:  "POST",
    headers: {
      "x-api-key":         apiKey,
      "anthropic-version": "2023-06-01",
      "content-type":      "application/json",
    },
    body: JSON.stringify({
      model:      "claude-haiku-4-5-20251001",
      max_tokens: 4096,
      messages:   [{ role: "user", content: prompt }],
    }),
  });

  if (!resp.ok) {
    throw new Error(`Anthropic ${resp.status}: ${await resp.text()}`);
  }

  const data = await resp.json();
  const text = data.content[0].text.trim();

  // Extract JSON — strip any accidental markdown fences
  const clean = text.replace(/^```[a-z]*\n?/m, "").replace(/\n?```$/m, "").trim();
  const match = clean.match(/\{[\s\S]*\}/);
  if (!match) throw new Error("No JSON in Anthropic response");

  return JSON.parse(match[0]);
}

// ─────────────────────────────────────────────────────────────────────────────
// ZIP builder (pure JS, no compression — text files only)
// ─────────────────────────────────────────────────────────────────────────────

function buildZip(product) {
  const folder = sanitizeFilename(product.title);
  const files  = [
    { name: `${folder}/README.md`,      content: buildReadme(product) },
    { name: `${folder}/content.md`,     content: buildContentMd(product) },
    { name: `${folder}/content.json`,   content: buildContentJson(product) },
  ];
  return createZip(files);
}

function buildReadme(product) {
  const label = CATEGORY_LABELS[product.category] || product.category;
  return [
    `# ${product.title}`,
    "",
    `**Type:** ${label}`,
    `**Description:** ${product.description || ""}`,
    "",
    "## How to use",
    "",
    "- `content.md` — human-readable, copy-paste friendly",
    "- `content.json` — structured data, import into your tools",
    "",
    "---",
    "",
    `Generated by [mini-on-ai.com](https://mini-on-ai.com)`,
    `For your use case: *${product.description}*`,
  ].join("\n");
}

function buildContentMd(product) {
  const items = Array.isArray(product.items) ? product.items : [];
  let md = `# ${product.title}\n\n${product.description || ""}\n\n---\n\n`;

  if (product.category === "mini-guide") {
    md += items.join("\n\n");
  } else {
    items.forEach((item, i) => {
      md += `**${i + 1}.** ${item}\n\n`;
    });
  }
  return md;
}

function buildContentJson(product) {
  return JSON.stringify({
    title:       product.title,
    description: product.description,
    category:    product.category,
    items:       product.items,
    source:      "mini-on-ai.com",
  }, null, 2);
}

// Minimal ZIP creator — stored (no compression), text files
function createZip(files) {
  const enc         = new TextEncoder();
  const localParts  = [];
  const centralDirs = [];
  let   offset      = 0;

  for (const file of files) {
    const name = enc.encode(file.name);
    const data = enc.encode(file.content);
    const crc  = crc32(data);
    const size = data.length;

    // Local file header (30 bytes + filename)
    const lh = new Uint8Array(30 + name.length);
    const lv = new DataView(lh.buffer);
    lv.setUint32(0,  0x04034b50, true); // signature
    lv.setUint16(4,  20,         true); // version needed
    lv.setUint16(6,  0,          true); // flags
    lv.setUint16(8,  0,          true); // compression: stored
    lv.setUint16(10, 0,          true); // mod time
    lv.setUint16(12, 0,          true); // mod date
    lv.setUint32(14, crc,        true); // crc32
    lv.setUint32(18, size,       true); // compressed size
    lv.setUint32(22, size,       true); // uncompressed size
    lv.setUint16(26, name.length,true); // filename length
    lv.setUint16(28, 0,          true); // extra length
    lh.set(name, 30);

    // Central directory entry (46 bytes + filename)
    const cd = new Uint8Array(46 + name.length);
    const cv = new DataView(cd.buffer);
    cv.setUint32(0,  0x02014b50, true);
    cv.setUint16(4,  20,         true);
    cv.setUint16(6,  20,         true);
    cv.setUint16(8,  0,          true);
    cv.setUint16(10, 0,          true);
    cv.setUint16(12, 0,          true);
    cv.setUint16(14, 0,          true);
    cv.setUint32(16, crc,        true);
    cv.setUint32(20, size,       true);
    cv.setUint32(24, size,       true);
    cv.setUint16(28, name.length,true);
    cv.setUint16(30, 0,          true);
    cv.setUint16(32, 0,          true);
    cv.setUint16(34, 0,          true);
    cv.setUint16(36, 0,          true);
    cv.setUint32(38, 0,          true);
    cv.setUint32(42, offset,     true); // local header offset
    cd.set(name, 46);

    localParts.push(lh, data);
    centralDirs.push(cd);
    offset += lh.length + data.length;
  }

  const cdSize = centralDirs.reduce((s, c) => s + c.length, 0);
  const eocd   = new Uint8Array(22);
  const ev     = new DataView(eocd.buffer);
  ev.setUint32(0,  0x06054b50,     true);
  ev.setUint16(4,  0,              true);
  ev.setUint16(6,  0,              true);
  ev.setUint16(8,  files.length,   true);
  ev.setUint16(10, files.length,   true);
  ev.setUint32(12, cdSize,         true);
  ev.setUint32(16, offset,         true);
  ev.setUint16(20, 0,              true);

  const all       = [...localParts, ...centralDirs, eocd];
  const totalSize = all.reduce((s, p) => s + p.length, 0);
  const result    = new Uint8Array(totalSize);
  let   pos       = 0;
  for (const part of all) { result.set(part, pos); pos += part.length; }
  return result;
}

// CRC-32 table
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let j = 0; j < 8; j++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    t[i] = c;
  }
  return t;
})();

function crc32(data) {
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < data.length; i++) {
    crc = (crc >>> 8) ^ CRC_TABLE[(crc ^ data[i]) & 0xFF];
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

async function checkRateLimit(env, ip) {
  const hour = Math.floor(Date.now() / 3_600_000);
  const key  = `ratelimit:${ip}:${hour}`;
  const count = parseInt(await env.PRODUCTS_KV.get(key) || "0", 10);
  if (count >= 3) return false;
  await env.PRODUCTS_KV.put(key, String(count + 1), { expirationTtl: 3600 });
  return true;
}

async function validateTurnstile(secret, token, ip) {
  if (!token) return false;
  try {
    const res  = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body:   new URLSearchParams({ secret, response: token, remoteip: ip }),
    });
    const data = await res.json();
    return data.success === true;
  } catch {
    return false;
  }
}

function sanitizeFilename(name) {
  return (name || "product").replace(/[^a-zA-Z0-9 \-_]/g, "").trim().slice(0, 60);
}

function corsJson(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      "Content-Type":                "application/json",
      "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    },
  });
}

function corsOk() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin":  ALLOWED_ORIGIN,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
