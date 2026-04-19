import { corsJson, parseJson, requireUser, currentMonth } from "./index.js";

const FREE_MONTHLY_LIMIT = 5;

export async function handleRegister(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id } = body;
  if (!user_id || typeof user_id !== "string" || user_id.length < 10) {
    return corsJson(env, { error: "Invalid user_id" }, 400);
  }

  const existing = await requireUser(env, user_id);
  if (existing) {
    const usage = await getUsageData(env, existing.id);
    return corsJson(env, {
      user_id: existing.id,
      tier: existing.tier,
      usage_this_month: usage.count,
      limit: existing.tier === "pro" ? null : FREE_MONTHLY_LIMIT,
    });
  }

  await env.DB.prepare(
    "INSERT INTO users (id, tier) VALUES (?, 'free')"
  ).bind(user_id).run();

  return corsJson(env, {
    user_id,
    tier: "free",
    usage_this_month: 0,
    limit: FREE_MONTHLY_LIMIT,
  });
}

export async function getUsage(request, env) {
  const userId = new URL(request.url).searchParams.get("user_id");
  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  const usage = await getUsageData(env, user.id);

  return corsJson(env, {
    user_id: user.id,
    tier: user.tier,
    usage_this_month: usage.count,
    limit: user.tier === "pro" ? null : FREE_MONTHLY_LIMIT,
  });
}

async function getUsageData(env, userId) {
  const month = currentMonth();
  const row = await env.DB.prepare(
    "SELECT analysis_count FROM usage_tracking WHERE user_id = ? AND month = ?"
  ).bind(userId, month).first();
  return { count: row ? row.analysis_count : 0 };
}
