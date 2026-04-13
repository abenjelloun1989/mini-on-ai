import { corsJson, parseJson, requireUser } from "./index.js";

const RATE_LIMIT_PER_MINUTE = 5;

/**
 * POST /api/parse
 * Extract invoice fields from raw email text using Claude Haiku.
 *
 * Body: { user_id, email_text, email_subject?, sender_email? }
 * Returns: { client_name, client_email, amount_cents, currency, invoice_date, due_date, invoice_number, confidence }
 */
export async function handleParse(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, email_text, email_subject, sender_email } = body;

  let user = await requireUser(env, user_id);
  if (!user) {
    // Auto-register (handles silent registration failures)
    await env.DB.prepare("INSERT OR IGNORE INTO users (id, tier) VALUES (?, 'free')").bind(user_id).run();
    user = await requireUser(env, user_id);
  }
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  if (!email_text || email_text.length < 10) {
    return corsJson(env, { error: "Email text is too short to parse." }, 400);
  }

  if (email_text.length > 15000) {
    return corsJson(env, { error: "Email text is too long. Maximum 15,000 characters." }, 413);
  }

  // Rate limiting
  const minuteKey = `ratelimit:parse:${user.id}:${Math.floor(Date.now() / 60000)}`;
  const rlRaw = await env.KV.get(minuteKey);
  const rlCount = rlRaw ? parseInt(rlRaw) : 0;
  if (rlCount >= RATE_LIMIT_PER_MINUTE) {
    return corsJson(env, { error: "Too many requests. Please wait a moment." }, 429);
  }
  await env.KV.put(minuteKey, String(rlCount + 1), { expirationTtl: 120 });

  // Call Claude Haiku
  const systemPrompt = `You are an invoice data extractor. Given the text of an email (and optionally a subject line and sender email), extract structured invoice information.

Return a JSON object with these fields:
- client_name: string — the company or person who sent the invoice (or to whom the invoice is addressed)
- client_email: string|null — email address of the client if found
- amount: number — the total amount (as a decimal, e.g. 1500.00)
- currency: string — 3-letter currency code (USD, EUR, GBP, etc.), default "USD"
- invoice_date: string|null — date the invoice was issued (YYYY-MM-DD format)
- due_date: string|null — payment due date (YYYY-MM-DD format). If "Net 30" or similar, calculate from invoice_date
- invoice_number: string|null — invoice number/reference if present
- confidence: "high"|"medium"|"low" — how confident you are in the extraction

If you cannot determine a field with reasonable confidence, set it to null.
Return ONLY valid JSON, no markdown fences or extra text.`;

  const userMessage = [
    email_subject ? `Subject: ${email_subject}` : "",
    sender_email ? `From: ${sender_email}` : "",
    "",
    "Email body:",
    email_text.slice(0, 12000),
  ].filter(Boolean).join("\n");

  try {
    const anthropicRes = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 500,
        system: systemPrompt,
        messages: [{ role: "user", content: userMessage }],
      }),
    });

    if (!anthropicRes.ok) {
      const err = await anthropicRes.text();
      console.error("Anthropic API error:", err);
      return corsJson(env, { error: "AI parsing failed. Please try again." }, 502);
    }

    const result = await anthropicRes.json();
    const text = result.content?.[0]?.text || "";

    // Strip markdown fences if present
    const jsonStr = text.replace(/^```(?:json)?\s*/, "").replace(/\s*```$/, "").trim();

    let parsed;
    try {
      parsed = JSON.parse(jsonStr);
    } catch {
      console.error("Failed to parse AI response:", text);
      return corsJson(env, { error: "Could not parse invoice data. Please enter details manually." }, 422);
    }

    // Convert amount to cents
    const amountCents = parsed.amount ? Math.round(parsed.amount * 100) : null;

    return corsJson(env, {
      client_name: parsed.client_name || null,
      client_email: parsed.client_email || sender_email || null,
      amount_cents: amountCents,
      currency: parsed.currency || "USD",
      invoice_date: parsed.invoice_date || null,
      due_date: parsed.due_date || null,
      invoice_number: parsed.invoice_number || null,
      confidence: parsed.confidence || "low",
    });
  } catch (e) {
    console.error("Parse error:", e.message);
    return corsJson(env, { error: "Failed to analyze email. Please try again." }, 500);
  }
}
