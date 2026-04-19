/**
 * JobGuard API — Cloudflare Worker
 *
 * Routes:
 *   POST /api/auth/register    — register anonymous user (UUID)
 *   GET  /api/usage            — monthly usage count + tier
 *   POST /api/analyze          — analyze a job posting with Claude
 *   POST /api/subscribe        — create Stripe Checkout session ($7/month)
 *   POST /api/webhook/stripe   — Stripe webhook handler
 *   GET  /api/subscription     — subscription status
 *   POST /api/portal           — Stripe Customer Portal session
 *   POST /api/redeem-ltd       — lifetime deal code redemption
 *   DELETE /api/user           — GDPR: delete all user data
 *   GET  /api/health           — binding status check
 *
 * Environment bindings:
 *   DB                    — D1 database
 *   KV                    — KV namespace (rate limiting)
 *   ANTHROPIC_API_KEY     — secret
 *   STRIPE_SECRET_KEY     — secret
 *   STRIPE_WEBHOOK_SECRET — secret
 *   ALLOWED_ORIGIN        — chrome-extension:// URL
 */

import { handleRegister, getUsage } from "./auth.js";
import { handleAnalyze } from "./analyze.js";
import {
  handleSubscribe,
  handleStripeWebhook,
  getSubscription,
  handlePortal,
} from "./billing.js";
import { handleRedeemLtd } from "./ltd.js";

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return corsOk(env);

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // Auth
      if (path === "/api/auth/register" && request.method === "POST") {
        return handleRegister(request, env);
      }
      if (path === "/api/usage" && request.method === "GET") {
        return getUsage(request, env);
      }

      // Core feature
      if (path === "/api/analyze" && request.method === "POST") {
        return handleAnalyze(request, env);
      }

      // LTD
      if (path === "/api/redeem-ltd" && request.method === "POST") {
        return handleRedeemLtd(request, env);
      }

      // Billing
      if (path === "/api/subscribe" && request.method === "POST") {
        return handleSubscribe(request, env);
      }
      if (path === "/api/webhook/stripe" && request.method === "POST") {
        return handleStripeWebhook(request, env);
      }
      if (path === "/api/subscription" && request.method === "GET") {
        return getSubscription(request, env);
      }
      if (path === "/api/portal" && request.method === "POST") {
        return handlePortal(request, env);
      }

      // GDPR
      if (path === "/api/user" && request.method === "DELETE") {
        return handleDeleteUser(request, env);
      }

      // Health
      if (path === "/api/health" && request.method === "GET") {
        const checks = {};
        try { await env.DB.prepare("SELECT 1").first(); checks.db = "ok"; } catch (e) { checks.db = "FAIL: " + e.message; }
        try { await env.KV.get("__health__"); checks.kv = "ok"; } catch (e) { checks.kv = "FAIL: " + e.message; }
        checks.anthropic_key = env.ANTHROPIC_API_KEY ? "set" : "MISSING";
        checks.stripe_key = env.STRIPE_SECRET_KEY ? "set" : "MISSING";
        return corsJson(env, checks);
      }

      return corsJson(env, { error: "Not found" }, 404);
    } catch (e) {
      console.error("Unhandled error:", e.message, e.stack);
      return corsJson(env, { error: "Internal server error" }, 500);
    }
  },
};

// ─── GDPR ────────────────────────────────────────────────────────────────────

async function handleDeleteUser(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const user = await requireUser(env, body.user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  await env.DB.batch([
    env.DB.prepare("DELETE FROM analyses WHERE user_id = ?").bind(user.id),
    env.DB.prepare("DELETE FROM usage_tracking WHERE user_id = ?").bind(user.id),
    env.DB.prepare("DELETE FROM users WHERE id = ?").bind(user.id),
  ]);

  console.log(`User deleted: ${user.id}`);
  return corsJson(env, { deleted: true });
}

// ─── Shared helpers (exported for use in other modules) ───────────────────────

export function corsJson(env, obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*",
    },
  });
}

export function corsOk(env) {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*",
      "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

export async function parseJson(request) {
  try { return await request.json(); }
  catch { return { error: "Invalid JSON" }; }
}

export async function requireUser(env, userId) {
  if (!userId) return null;
  const user = await env.DB.prepare(
    "SELECT id, email, tier, stripe_customer_id, stripe_subscription_id, pro_source FROM users WHERE id = ?"
  ).bind(userId).first();
  return user || null;
}

export function currentMonth() {
  return new Date().toISOString().slice(0, 7);
}
