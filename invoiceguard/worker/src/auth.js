import { corsJson, parseJson, requireUser, currentMonth } from "./index.js";

const FREE_INVOICE_LIMIT = 5;

/**
 * POST /api/auth/register
 * Register an anonymous user with a client-generated UUID.
 * Idempotent — if the user already exists, returns their info.
 */
export async function handleRegister(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id } = body;
  if (!user_id || typeof user_id !== "string" || user_id.length < 10) {
    return corsJson(env, { error: "Invalid user_id" }, 400);
  }

  // Check if user exists
  const existing = await requireUser(env, user_id);
  if (existing) {
    const usage = await getUsageData(env, existing.id);
    return corsJson(env, {
      user_id: existing.id,
      tier: existing.tier,
      invoices_this_month: usage.invoice_count,
      limit: existing.tier === "pro" ? null : FREE_INVOICE_LIMIT,
    });
  }

  // Create new user
  await env.DB.prepare(
    "INSERT INTO users (id, tier) VALUES (?, 'free')"
  ).bind(user_id).run();

  return corsJson(env, {
    user_id,
    tier: "free",
    invoices_this_month: 0,
    limit: FREE_INVOICE_LIMIT,
  });
}

/**
 * GET /api/usage?user_id=...
 * Returns current month's usage and tier info.
 */
export async function getUsage(request, env) {
  const userId = new URL(request.url).searchParams.get("user_id");
  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  const usage = await getUsageData(env, user.id);

  // Count active invoices (not cancelled/paid)
  const active = await env.DB.prepare(
    "SELECT COUNT(*) as cnt FROM invoices WHERE user_id = ? AND status IN ('sent', 'overdue')"
  ).bind(user.id).first();

  return corsJson(env, {
    user_id: user.id,
    tier: user.tier,
    invoices_this_month: usage.invoice_count,
    active_invoices: active?.cnt || 0,
    limit: user.tier === "pro" ? null : FREE_INVOICE_LIMIT,
  });
}

/**
 * Get usage data for current month.
 */
async function getUsageData(env, userId) {
  const month = currentMonth();
  const row = await env.DB.prepare(
    "SELECT invoice_count FROM usage_tracking WHERE user_id = ? AND month = ?"
  ).bind(userId, month).first();
  return { invoice_count: row ? row.invoice_count : 0 };
}
