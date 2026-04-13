import { corsJson, parseJson, requireUser } from "./index.js";

/**
 * POST /api/remind
 * Generate follow-up reminder email text using Claude Haiku.
 *
 * Body: { user_id, invoice_id, tone }
 * tone: "friendly" | "professional" | "firm"
 * Returns: { subject, body, tone }
 */
export async function handleRemind(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, invoice_id, tone } = body;

  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  // Get invoice
  const invoice = await env.DB.prepare(
    "SELECT * FROM invoices WHERE id = ? AND user_id = ?"
  ).bind(invoice_id, user.id).first();

  if (!invoice) return corsJson(env, { error: "Invoice not found" }, 404);

  // Pro feature check for AI reminders (free users get a template)
  if (user.tier !== "pro") {
    return corsJson(env, {
      subject: `Follow-up: Invoice for ${formatAmount(invoice.amount_cents, invoice.currency)}`,
      body: generateBasicReminder(invoice),
      tone: "professional",
      is_template: true,
    });
  }

  // Rate limiting
  const minuteKey = `ratelimit:remind:${user.id}:${Math.floor(Date.now() / 60000)}`;
  const rlRaw = await env.KV.get(minuteKey);
  const rlCount = rlRaw ? parseInt(rlRaw) : 0;
  if (rlCount >= 5) {
    return corsJson(env, { error: "Too many requests. Please wait a moment." }, 429);
  }
  await env.KV.put(minuteKey, String(rlCount + 1), { expirationTtl: 120 });

  const selectedTone = tone || "professional";
  const daysOverdue = invoice.due_date
    ? Math.max(0, Math.floor((Date.now() - new Date(invoice.due_date).getTime()) / 86400000))
    : 0;

  const systemPrompt = `You are a professional email writer helping freelancers follow up on unpaid invoices.

Write a payment reminder email with the following tone: ${selectedTone}
- "friendly": warm, assumes good intent, casual but clear
- "professional": business-like, polite, firm about the amount owed
- "firm": direct, mentions consequences (late fees, pausing work), still professional

Return a JSON object with:
- subject: string — email subject line
- body: string — email body (plain text, no HTML). Use \\n for line breaks.

Keep it concise (3-5 short paragraphs). Never be rude or threatening.
Include the specific amount and how many days overdue.
Return ONLY valid JSON, no markdown fences.`;

  const context = [
    `Client name: ${invoice.client_name}`,
    `Amount: ${formatAmount(invoice.amount_cents, invoice.currency)}`,
    `Invoice date: ${invoice.invoice_date || "unknown"}`,
    `Due date: ${invoice.due_date || "unknown"}`,
    `Days overdue: ${daysOverdue}`,
    `Previous reminders sent: ${invoice.reminders_sent}`,
    invoice.email_subject ? `Original email subject: ${invoice.email_subject}` : "",
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
        model: "claude-haiku-4-20250414",
        max_tokens: 800,
        system: systemPrompt,
        messages: [{ role: "user", content: context }],
      }),
    });

    if (!anthropicRes.ok) {
      const err = await anthropicRes.text();
      console.error("Anthropic API error:", err);
      // Fallback to template
      return corsJson(env, {
        subject: `Follow-up: Invoice for ${formatAmount(invoice.amount_cents, invoice.currency)}`,
        body: generateBasicReminder(invoice),
        tone: selectedTone,
        is_template: true,
      });
    }

    const result = await anthropicRes.json();
    const text = result.content?.[0]?.text || "";
    const jsonStr = text.replace(/^```(?:json)?\s*/, "").replace(/\s*```$/, "").trim();

    let parsed;
    try {
      parsed = JSON.parse(jsonStr);
    } catch {
      return corsJson(env, {
        subject: `Follow-up: Invoice for ${formatAmount(invoice.amount_cents, invoice.currency)}`,
        body: generateBasicReminder(invoice),
        tone: selectedTone,
        is_template: true,
      });
    }

    // Update reminder count
    await env.DB.prepare(
      "UPDATE invoices SET reminders_sent = reminders_sent + 1, last_reminder_at = datetime('now'), updated_at = datetime('now') WHERE id = ?"
    ).bind(invoice.id).run();

    return corsJson(env, {
      subject: parsed.subject,
      body: parsed.body,
      tone: selectedTone,
      is_template: false,
    });
  } catch (e) {
    console.error("Remind error:", e.message);
    return corsJson(env, {
      subject: `Follow-up: Invoice for ${formatAmount(invoice.amount_cents, invoice.currency)}`,
      body: generateBasicReminder(invoice),
      tone: "professional",
      is_template: true,
    });
  }
}

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

function formatAmount(cents, currency = "USD") {
  const symbols = { USD: "$", EUR: "€", GBP: "£", CAD: "CA$", AUD: "A$" };
  const symbol = symbols[currency] || `${currency} `;
  return `${symbol}${(cents / 100).toFixed(2)}`;
}

function generateBasicReminder(invoice) {
  const amount = formatAmount(invoice.amount_cents, invoice.currency);
  const daysOverdue = invoice.due_date
    ? Math.max(0, Math.floor((Date.now() - new Date(invoice.due_date).getTime()) / 86400000))
    : 0;

  return `Hi ${invoice.client_name},

I hope you're doing well. I'm writing to follow up on the invoice for ${amount}${invoice.due_date ? ` that was due on ${invoice.due_date}` : ""}.${daysOverdue > 0 ? ` It is now ${daysOverdue} day${daysOverdue > 1 ? "s" : ""} overdue.` : ""}

Could you please let me know the status of this payment? If it has already been sent, please disregard this message.

Thank you for your prompt attention to this matter.

Best regards`;
}
