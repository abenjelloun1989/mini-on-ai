import { corsJson, parseJson, requireUser, currentMonth } from "./index.js";

const MAX_INPUT_LENGTH = 15000;
const FREE_MONTHLY_LIMIT = 5;
const PRO_MONTHLY_LIMIT = 200;
const RATE_LIMIT_PER_MINUTE = 5;

// ─── Claude prompt ────────────────────────────────────────────────────────────

function buildPrompt(postingText) {
  return `You are a freelance career advisor helping freelancers evaluate job postings. Analyze the following job posting and return ONLY valid JSON (no markdown fences, no extra text).

Return this exact JSON structure:
{
  "risk_score": <integer 1-10, where 1=very safe/legit, 10=extreme risk/scam>,
  "risk_label": "<Looks Legit|Proceed with Caution|High Risk|Avoid — Likely Scam>",
  "platform_detected": "<Upwork|LinkedIn|Indeed|Freelancer|Fiverr|Other|Unknown>",
  "summary": "<2-3 sentences: honest plain-English verdict on this posting. Start with 'This posting...' Be direct — if it looks like a scam, say so.>",
  "red_flags": [
    {
      "id": <sequential integer>,
      "severity": "<danger|warning>",
      "category": "<scam|spec_work|lowball|scope_creep|ip_grab|payment|vague|off_platform|personal_info|other>",
      "title": "<short title, e.g. 'Requests Unpaid Test Project'>",
      "quote": "<exact quote from posting if available, otherwise null>",
      "explanation": "<1-2 sentences: why this is a red flag and what it means for you>"
    }
  ],
  "green_signals": [
    {
      "title": "<short title, e.g. 'Clear Deliverables Listed'>",
      "explanation": "<1 sentence: why this is a good sign>"
    }
  ],
  "market_rate_note": "<null if no budget/rate mentioned, otherwise: 1-2 sentences comparing stated rate to typical market rate for the skills listed. Include a realistic range.>",
  "negotiation_tips": [
    "<1 sentence, actionable tip specific to this posting>"
  ]
}

Categories explained:
- scam: fake job, impersonation, request for personal info or upfront payment
- spec_work: request for free work samples, test projects, or unpaid trials
- lowball: pay below market rate for skills required
- scope_creep: vague or unlimited deliverables, "other duties as required"
- ip_grab: client claims ownership of pre-existing work, tools, or processes
- payment: unclear payment terms, net-60+, milestone-less structure
- vague: critical details missing (budget, timeline, company identity, deliverables)
- off_platform: requests to move communication/payment outside the platform
- personal_info: early requests for personal details, ID, bank info

Risk score calibration:
1-3 = Looks legit — professional posting with clear terms
4-6 = Proceed with caution — some concerns worth clarifying before applying
7-8 = High risk — multiple serious red flags, apply only with protective conditions
9-10 = Avoid — scam signals or predatory terms

Rules:
- Be specific and direct. Name the actual red flag with a quote when possible.
- green_signals: only include if genuinely present (clear budget, named company, detailed brief, etc.). Empty array if none.
- market_rate_note: compare budget to typical freelance market rates for the specific skills mentioned.
- negotiation_tips: 2-4 tips specific to THIS posting (e.g. "Ask for 50% upfront before starting")
- If the posting is very short or low-quality, note this as a vague flag.
- IMPORTANT: If the text appears to be a list of multiple job postings (a search results page, a job board listing page), do NOT analyze individual listings. Instead: set risk_score to 0, risk_label to "Not a job posting", summary to "This looks like a search results or listing page, not a single job posting. Please open a specific job and click Analyze again.", red_flags to [], green_signals to [], market_rate_note to null, negotiation_tips to [].

JOB POSTING TEXT:
${postingText}`;
}

// ─── POST /api/analyze ────────────────────────────────────────────────────────

export async function handleAnalyze(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, posting_text } = body;

  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found. Please reinstall the extension." }, 404);

  // Validate input
  if (!posting_text || typeof posting_text !== "string") {
    return corsJson(env, { error: "Missing posting_text" }, 400);
  }
  const trimmed = posting_text.trim();
  if (trimmed.length < 30) {
    return corsJson(env, { error: "Posting text too short (minimum 30 characters)." }, 400);
  }
  if (trimmed.length > MAX_INPUT_LENGTH) {
    return corsJson(env, { error: `Posting text too long (maximum ${MAX_INPUT_LENGTH} characters).` }, 400);
  }

  // Rate limit: 5/minute per user
  const minuteKey = `ratelimit:${user.id}:${Math.floor(Date.now() / 60000)}`;
  const rlRaw = await env.KV.get(minuteKey);
  const rlCount = rlRaw ? parseInt(rlRaw) : 0;
  if (rlCount >= RATE_LIMIT_PER_MINUTE) {
    return corsJson(env, { error: "Too many requests. Please wait a moment." }, 429);
  }
  await env.KV.put(minuteKey, String(rlCount + 1), { expirationTtl: 120 });

  // Atomic monthly usage increment
  const month = currentMonth();
  const limit = user.tier === "pro" ? PRO_MONTHLY_LIMIT : FREE_MONTHLY_LIMIT;

  const incrementResult = await env.DB.prepare(
    `INSERT INTO usage_tracking (user_id, month, analysis_count) VALUES (?, ?, 1)
     ON CONFLICT(user_id, month) DO UPDATE
     SET analysis_count = analysis_count + 1
     WHERE analysis_count < ?`
  ).bind(user.id, month, limit).run();

  if (incrementResult.meta.changes === 0) {
    const current = await env.DB.prepare(
      "SELECT analysis_count FROM usage_tracking WHERE user_id = ? AND month = ?"
    ).bind(user.id, month).first();
    const count = current ? current.analysis_count : 0;

    if (user.tier !== "pro") {
      return corsJson(env, {
        error: "Monthly limit reached",
        limit: FREE_MONTHLY_LIMIT,
        usage: count,
        upgrade_required: true,
      }, 429);
    }
    return corsJson(env, {
      error: `Monthly limit of ${PRO_MONTHLY_LIMIT} analyses reached. Contact support if you need more.`,
      limit: PRO_MONTHLY_LIMIT,
      usage: count,
    }, 429);
  }

  // Call Claude Haiku
  let analysis;
  try {
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5",
        max_tokens: 4096,
        messages: [{ role: "user", content: buildPrompt(trimmed) }],
      }),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      console.error("Anthropic error:", resp.status, errText);
      throw new Error(`Anthropic ${resp.status}`);
    }

    const data = await resp.json();
    if (!data.content?.[0]?.text) throw new Error("Empty response from Anthropic");
    const text = data.content[0].text.trim();

    const clean = text.replace(/^```[a-z]*\n?/m, "").replace(/\n?```$/m, "").trim();
    const match = clean.match(/\{[\s\S]*\}/);
    if (!match) throw new Error("No JSON in response");
    analysis = JSON.parse(match[0]);

    if (typeof analysis.risk_score !== "number" || !Array.isArray(analysis.red_flags)) {
      throw new Error("Incomplete analysis response from AI");
    }
  } catch (e) {
    console.error("Analysis error:", e.message);
    return corsJson(env, { error: "Analysis failed. Please try again." }, 500);
  }

  // Store in D1 for history
  const analysisId = crypto.randomUUID();
  await env.DB.prepare(
    "INSERT INTO analyses (id, user_id, risk_score, red_flag_count, platform, summary) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(
    analysisId,
    user.id,
    analysis.risk_score,
    (analysis.red_flags || []).length,
    analysis.platform_detected || "Unknown",
    analysis.summary || "",
  ).run();

  // Fetch updated usage
  const updatedUsage = await env.DB.prepare(
    "SELECT analysis_count FROM usage_tracking WHERE user_id = ? AND month = ?"
  ).bind(user.id, month).first();

  return corsJson(env, {
    analysis_id: analysisId,
    analysis,
    usage: {
      count: updatedUsage?.analysis_count ?? 1,
      limit: user.tier === "pro" ? null : FREE_MONTHLY_LIMIT,
      tier: user.tier,
    },
  });
}
