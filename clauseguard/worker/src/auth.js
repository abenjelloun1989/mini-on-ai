import { corsJson, parseJson, requireUser, currentMonth } from "./index.js";

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
      usage_this_month: usage.analysis_count,
      limit: existing.tier === "pro" ? null : 3,
    });
  }

  // Create new user
  await env.DB.prepare(
    "INSERT INTO users (id, tier) VALUES (?, 'free')"
  ).bind(user_id).run();

  return corsJson(env, {
    user_id,
    tier: "free",
    usage_this_month: 0,
    limit: 3,
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

  return corsJson(env, {
    user_id: user.id,
    tier: user.tier,
    usage_this_month: usage.analysis_count,
    limit: user.tier === "pro" ? null : 3,
  });
}

/**
 * Get usage data for current month.
 */
async function getUsageData(env, userId) {
  const month = currentMonth();
  const row = await env.DB.prepare(
    "SELECT analysis_count FROM usage_tracking WHERE user_id = ? AND month = ?"
  ).bind(userId, month).first();
  return { analysis_count: row ? row.analysis_count : 0 };
}
