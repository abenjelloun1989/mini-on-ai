import { corsJson, parseJson, requireUser, currentMonth } from "./index.js";

const CONTRACT_TYPES = [
  "general", "freelance", "nda", "employment", "saas", "lease", "investment",
];

const MAX_CONTRACT_LENGTH = 15000;
const FREE_MONTHLY_LIMIT = 3;
const PRO_MONTHLY_LIMIT = 500;   // hard cap — costs $3.50 max vs $7 revenue
const RATE_LIMIT_PER_MINUTE = 5; // per user, blocks batch scripts

// ─────────────────────────────────────────────────────────────────────────────
// Claude prompt for contract analysis
// ─────────────────────────────────────────────────────────────────────────────

function buildAnalysisPrompt(contractText, contractType) {
  return `You are a contract analyst helping freelancers and small business owners understand contracts in plain English. You are NOT a lawyer. Analyze the following contract text and return ONLY valid JSON (no markdown fences, no extra text).

CONTRACT TYPE: ${contractType}
Use this to calibrate what is normal vs. concerning for this type of agreement.

Return this exact JSON structure:
{
  "disclaimer": "This is an AI-powered analysis for informational purposes only. It is not legal advice. Consult a qualified attorney before signing any contract.",
  "risk_score": <integer 1-10, where 1=very safe, 10=extremely risky>,
  "risk_label": "<Low Risk|Moderate Risk|High Risk|Critical Risk>",
  "plain_english_summary": "<2-4 sentences: what this contract actually commits you to, in everyday language. Start with 'This contract says you agree to...'>",
  "clauses": [
    {
      "id": <sequential integer>,
      "category": "<payment|ip|liability|termination|non_compete|confidentiality|indemnity|scope|timeline|dispute|insurance|data_privacy|exclusivity|other>",
      "title": "<short descriptive title, e.g. 'Net-60 Payment Terms'>",
      "original_text": "<exact quote from the contract, max 200 chars>",
      "risk_level": "<green|yellow|red>",
      "explanation": "<1-2 sentences: what this clause means in plain English>",
      "concern": "<null if green, otherwise: 1-2 sentences explaining WHY this is risky for YOU specifically>",
      "suggested_change": "<null if green, otherwise: concrete reworded clause text that would be fairer>"
    }
  ],
  "red_flags": [
    {
      "clause_id": <references clauses[].id>,
      "severity": "<warning|danger>",
      "title": "<short title, e.g. 'Unlimited Liability'>",
      "explanation": "<2-3 sentences: what could go wrong, with a concrete scenario>"
    }
  ],
  "missing_protections": [
    {
      "category": "<same categories as clauses>",
      "title": "<what is missing, e.g. 'Late Payment Penalty'>",
      "why_it_matters": "<1-2 sentences>",
      "suggested_clause": "<ready-to-use clause text they could request be added>"
    }
  ],
  "negotiation_tips": [
    "<1 sentence actionable tip>"
  ]
}

Rules:
- Analyze EVERY substantive clause, not just risky ones. Green clauses show the contract is fair in those areas.
- For freelancers: pay special attention to payment terms (net-30+ is a yellow flag), IP assignment (work-for-hire traps), scope creep clauses, kill fees, and non-competes.
- For NDAs: check duration, definition breadth, carve-outs, and whether it is mutual.
- For employment: check non-compete scope, IP assignment, termination conditions, garden leave.
- red_flags: only include yellow and red clauses. Sort by severity (danger first).
- missing_protections: check for late payment penalties, termination notice periods, liability caps, dispute resolution, force majeure. Only flag ones actually missing.
- negotiation_tips: 2-4 concrete tips specific to THIS contract.
- Keep all explanations jargon-free. Write for someone with no legal background.
- risk_score calibration: 1-3 = standard/fair contract, 4-6 = some concerning clauses but negotiable, 7-8 = significantly one-sided, 9-10 = predatory/should not sign without major changes.

CONTRACT TEXT:
${contractText}`;
}

// ─────────────────────────────────────────────────────────────────────────────
// POST /api/analyze
// ─────────────────────────────────────────────────────────────────────────────

export async function handleAnalyze(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, contract_text, contract_type = "general" } = body;

  // Validate user
  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found. Please register first." }, 404);

  // Validate input
  if (!contract_text || typeof contract_text !== "string") {
    return corsJson(env, { error: "Missing contract_text" }, 400);
  }
  const trimmed = contract_text.trim();
  if (trimmed.length < 50) {
    return corsJson(env, { error: "Contract text too short (minimum 50 characters)." }, 400);
  }
  if (trimmed.length > MAX_CONTRACT_LENGTH) {
    return corsJson(env, { error: `Contract text too long (maximum ${MAX_CONTRACT_LENGTH} characters). Please trim or split the document.` }, 400);
  }
  if (!CONTRACT_TYPES.includes(contract_type)) {
    return corsJson(env, { error: `Invalid contract_type. Must be one of: ${CONTRACT_TYPES.join(", ")}` }, 400);
  }

  // ── Rate limit: max 5 analyses per minute per user (blocks batch scripts) ──
  const minuteKey = `ratelimit:${user.id}:${Math.floor(Date.now() / 60000)}`;
  const rlRaw = await env.KV.get(minuteKey);
  const rlCount = rlRaw ? parseInt(rlRaw) : 0;
  if (rlCount >= RATE_LIMIT_PER_MINUTE) {
    return corsJson(env, {
      error: "Too many requests. Please wait a moment before analyzing another contract.",
    }, 429);
  }
  await env.KV.put(minuteKey, String(rlCount + 1), { expirationTtl: 120 });

  // ── Monthly usage limits ──
  const month = currentMonth();
  const usage = await env.DB.prepare(
    "SELECT analysis_count FROM usage_tracking WHERE user_id = ? AND month = ?"
  ).bind(user.id, month).first();
  const count = usage ? usage.analysis_count : 0;

  if (user.tier !== "pro") {
    if (count >= FREE_MONTHLY_LIMIT) {
      return corsJson(env, {
        error: "Monthly limit reached",
        limit: FREE_MONTHLY_LIMIT,
        usage: count,
        upgrade_required: true,
      }, 429);
    }
  } else {
    // Pro hard cap — prevents abuse from batch scripts
    if (count >= PRO_MONTHLY_LIMIT) {
      return corsJson(env, {
        error: `You've reached the monthly analysis limit (${PRO_MONTHLY_LIMIT}). Contact support if you need more.`,
        limit: PRO_MONTHLY_LIMIT,
        usage: count,
      }, 429);
    }
  }

  // Call Claude Haiku
  let analysis;
  try {
    const prompt = buildAnalysisPrompt(trimmed, contract_type);
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5",
        max_tokens: 8192,
        messages: [{ role: "user", content: prompt }],
      }),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      console.error("Anthropic error:", resp.status, errText);
      throw new Error(`Anthropic ${resp.status}`);
    }

    const data = await resp.json();
    const text = data.content[0].text.trim();

    // Strip markdown fences and extract JSON
    const clean = text.replace(/^```[a-z]*\n?/m, "").replace(/\n?```$/m, "").trim();
    const match = clean.match(/\{[\s\S]*\}/);
    if (!match) throw new Error("No JSON in response");
    analysis = JSON.parse(match[0]);
  } catch (e) {
    console.error("Analysis error:", e.message, e.stack);
    return corsJson(env, { error: "Analysis failed. Please try again.", _debug: e.message }, 500);
  }

  // Store analysis
  const analysisId = crypto.randomUUID();

  // Increment usage count (upsert)
  await env.DB.prepare(
    "INSERT INTO usage_tracking (user_id, month, analysis_count) VALUES (?, ?, 1) ON CONFLICT(user_id, month) DO UPDATE SET analysis_count = analysis_count + 1"
  ).bind(user.id, month).run();

  // Store metadata in D1
  await env.DB.prepare(
    "INSERT INTO analyses (id, user_id, risk_score, clause_count, red_flag_count, contract_type, summary) VALUES (?, ?, ?, ?, ?, ?, ?)"
  ).bind(
    analysisId,
    user.id,
    analysis.risk_score || 0,
    (analysis.clauses || []).length,
    (analysis.red_flags || []).length,
    contract_type,
    analysis.plain_english_summary || "",
  ).run();

  // Store full analysis JSON in KV (30-day TTL)
  await env.KV.put(
    `analysis:${analysisId}`,
    JSON.stringify(analysis),
    { expirationTtl: 30 * 86400 }
  );

  // Get updated usage
  const updatedUsage = await env.DB.prepare(
    "SELECT analysis_count FROM usage_tracking WHERE user_id = ? AND month = ?"
  ).bind(user.id, month).first();

  return corsJson(env, {
    analysis_id: analysisId,
    analysis,
    usage: {
      count: updatedUsage.analysis_count,
      limit: user.tier === "pro" ? null : FREE_MONTHLY_LIMIT,
      tier: user.tier,
    },
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// POST /api/compare (Pro only)
// ─────────────────────────────────────────────────────────────────────────────

export async function handleCompare(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, contract_text_old, contract_text_new, contract_type = "general" } = body;

  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);
  if (user.tier !== "pro") return corsJson(env, { error: "Pro subscription required" }, 403);

  if (!contract_text_old || !contract_text_new) {
    return corsJson(env, { error: "Both contract_text_old and contract_text_new are required" }, 400);
  }

  const prompt = `Compare these two versions of a contract (type: ${contract_type}). Return ONLY valid JSON (no markdown fences).

Return this structure:
{
  "changes": [
    {
      "type": "<added|removed|modified>",
      "category": "<payment|ip|liability|termination|non_compete|confidentiality|indemnity|scope|timeline|dispute|insurance|data_privacy|exclusivity|other>",
      "title": "<short description of the change>",
      "old_text": "<original clause text or null if added>",
      "new_text": "<new clause text or null if removed>",
      "impact": "<favorable|neutral|unfavorable>",
      "explanation": "<1-2 sentences: what this change means for you>"
    }
  ],
  "overall_assessment": "<1-2 sentences: is the new version better or worse for you?>",
  "risk_change": "<improved|unchanged|worsened>"
}

OLD VERSION:
${contract_text_old.slice(0, MAX_CONTRACT_LENGTH)}

NEW VERSION:
${contract_text_new.slice(0, MAX_CONTRACT_LENGTH)}`;

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
        max_tokens: 8192,
        messages: [{ role: "user", content: prompt }],
      }),
    });

    if (!resp.ok) throw new Error(`Anthropic ${resp.status}`);

    const data = await resp.json();
    const text = data.content[0].text.trim();
    const clean = text.replace(/^```[a-z]*\n?/m, "").replace(/\n?```$/m, "").trim();
    const match = clean.match(/\{[\s\S]*\}/);
    if (!match) throw new Error("No JSON in response");

    return corsJson(env, JSON.parse(match[0]));
  } catch (e) {
    console.error("Compare error:", e.message);
    return corsJson(env, { error: "Comparison failed. Please try again." }, 500);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// GET /api/history?user_id=...
// ─────────────────────────────────────────────────────────────────────────────

export async function getHistory(request, env) {
  const url = new URL(request.url);
  const userId = url.searchParams.get("user_id");
  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  const { results } = await env.DB.prepare(
    "SELECT id, risk_score, clause_count, red_flag_count, contract_type, summary, created_at FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 20"
  ).bind(user.id).all();

  return corsJson(env, { analyses: results });
}
