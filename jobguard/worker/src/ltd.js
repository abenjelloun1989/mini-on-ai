import { corsJson, parseJson, requireUser } from "./index.js";

const INVALID_CODE_MSG = "This code is not valid or has already been used.";

export async function handleRedeemLtd(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, code } = body;
  if (!user_id || typeof user_id !== "string") return corsJson(env, { error: "Missing user_id" }, 400);
  if (!code || typeof code !== "string") return corsJson(env, { error: "Missing code" }, 400);

  const normalizedCode = code.trim().toUpperCase();
  if (normalizedCode.length < 4) return corsJson(env, { error: "Invalid code format" }, 400);

  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  const ltdCode = await env.DB.prepare(
    "SELECT code, redeemed_by FROM ltd_codes WHERE code = ?"
  ).bind(normalizedCode).first();

  if (!ltdCode) return corsJson(env, { error: INVALID_CODE_MSG }, 400);

  if (ltdCode.redeemed_by) {
    // Idempotent — same user can re-redeem (e.g. after reinstall)
    if (ltdCode.redeemed_by === user_id) {
      return corsJson(env, { success: true, tier: "pro", pro_source: "ltd" });
    }
    return corsJson(env, { error: INVALID_CODE_MSG }, 400);
  }

  const now = Math.floor(Date.now() / 1000);
  await env.DB.prepare(
    "UPDATE ltd_codes SET redeemed_by = ?, redeemed_at = ? WHERE code = ?"
  ).bind(user_id, now, normalizedCode).run();

  await env.DB.prepare(
    "UPDATE users SET tier = 'pro', pro_source = 'ltd', updated_at = datetime('now') WHERE id = ?"
  ).bind(user_id).run();

  return corsJson(env, { success: true, tier: "pro", pro_source: "ltd" });
}
