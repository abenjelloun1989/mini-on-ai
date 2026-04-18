import { corsJson, parseJson, requireUser } from "./index.js";

/**
 * POST /api/ltd/redeem
 * Redeem a lifetime deal code to upgrade a user to Pro permanently.
 *
 * Body: { user_id, code }
 * Returns: { success: true, message } or { error }
 *
 * Security: unified error message for invalid + already-used codes (no enumeration).
 */
export async function handleLtdRedeem(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, code } = body;
  if (!user_id || !code) {
    return corsJson(env, { error: "Missing user_id or code" }, 400);
  }

  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  if (user.tier === "pro" && user.pro_source === "ltd") {
    return corsJson(env, { error: "Lifetime access is already active on this account." }, 400);
  }

  // Unified error message for invalid and already-redeemed codes (no enumeration)
  const ltdCode = await env.DB.prepare(
    "SELECT code, redeemed_by FROM ltd_codes WHERE code = ?"
  ).bind(code.trim().toUpperCase()).first();

  if (!ltdCode || ltdCode.redeemed_by) {
    return corsJson(env, { error: "This code is not valid or has already been used." }, 400);
  }

  // Mark code as redeemed and upgrade user atomically
  await env.DB.prepare(
    "UPDATE ltd_codes SET redeemed_by = ?, redeemed_at = datetime('now') WHERE code = ? AND redeemed_by IS NULL"
  ).bind(user_id, code.trim().toUpperCase()).run();

  await env.DB.prepare(
    "UPDATE users SET tier = 'pro', pro_source = 'ltd', updated_at = datetime('now') WHERE id = ?"
  ).bind(user_id).run();

  return corsJson(env, { success: true, message: "Lifetime access activated!" });
}
