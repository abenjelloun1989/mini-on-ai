/**
 * ClauseGuard API — Cloudflare Worker
 *
 * Routes:
 *   POST /api/auth/register   — register anonymous user (UUID)
 *   GET  /api/usage           — get monthly usage count + tier
 *   POST /api/analyze         — analyze a contract with Claude
 *   POST /api/compare         — compare two contract versions (Pro)
 *   POST /api/subscribe       — create Stripe Checkout session ($7/month)
 *   POST /api/webhook/stripe  — Stripe webhook handler
 *   GET  /api/subscription    — get subscription status
 *   POST /api/portal          — create Stripe Customer Portal session
 *   GET  /api/history         — get analysis history
 *   POST /api/clauses         — save a clause (Pro)
 *   GET  /api/clauses         — list saved clauses (Pro)
 *   DELETE /api/clauses/:id   — delete a saved clause (Pro)
 *
 * Environment:
 *   DB               — D1 database binding
 *   KV               — KV namespace for analysis JSON cache
 *   ANTHROPIC_API_KEY — secret
 *   STRIPE_SECRET_KEY — secret
 *   STRIPE_WEBHOOK_SECRET — secret
 *   ALLOWED_ORIGIN   — chrome-extension:// URL
 */

import { handleRegister, getUsage } from "./auth.js";
import { handleAnalyze, handleCompare, getHistory } from "./analyze.js";
import {
  handleSubscribe,
  handleStripeWebhook,
  getSubscription,
  handlePortal,
} from "./billing.js";

export default {
  async fetch(request, env) {
    // CORS preflight
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

      // Analysis
      if (path === "/api/analyze" && request.method === "POST") {
        return handleAnalyze(request, env);
      }
      if (path === "/api/compare" && request.method === "POST") {
        return handleCompare(request, env);
      }
      if (path === "/api/history" && request.method === "GET") {
        return getHistory(request, env);
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

      // Clauses (Pro)
      if (path === "/api/clauses" && request.method === "POST") {
        return handleSaveClause(request, env);
      }
      if (path === "/api/clauses" && request.method === "GET") {
        return handleListClauses(request, env);
      }
      if (path.startsWith("/api/clauses/") && request.method === "DELETE") {
        return handleDeleteClause(request, env, path);
      }

      return corsJson(env, { error: "Not found" }, 404);
    } catch (e) {
      console.error("Unhandled error:", e.message, e.stack);
      return corsJson(env, { error: "Internal server error" }, 500);
    }
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Clauses endpoints (Pro only)
// ─────────────────────────────────────────────────────────────────────────────

async function handleSaveClause(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const user = await requireUser(env, body.user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);
  if (user.tier !== "pro") return corsJson(env, { error: "Pro subscription required" }, 403);

  const { category, title, clause_text, notes } = body;
  if (!category || !title || !clause_text) {
    return corsJson(env, { error: "Missing required fields: category, title, clause_text" }, 400);
  }

  const id = crypto.randomUUID();
  await env.DB.prepare(
    "INSERT INTO saved_clauses (id, user_id, category, title, clause_text, notes) VALUES (?, ?, ?, ?, ?, ?)"
  ).bind(id, user.id, category, title, clause_text, notes || null).run();

  return corsJson(env, { id, category, title });
}

async function handleListClauses(request, env) {
  const userId = new URL(request.url).searchParams.get("user_id");
  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);
  if (user.tier !== "pro") return corsJson(env, { error: "Pro subscription required" }, 403);

  const { results } = await env.DB.prepare(
    "SELECT id, category, title, clause_text, notes, created_at FROM saved_clauses WHERE user_id = ? ORDER BY created_at DESC"
  ).bind(user.id).all();

  return corsJson(env, { clauses: results });
}

async function handleDeleteClause(request, env, path) {
  const clauseId = path.split("/").pop();
  const userId = new URL(request.url).searchParams.get("user_id");
  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  await env.DB.prepare(
    "DELETE FROM saved_clauses WHERE id = ? AND user_id = ?"
  ).bind(clauseId, user.id).run();

  return corsJson(env, { deleted: true });
}

// ─────────────────────────────────────────────────────────────────────────────
// Shared helpers (exported for use in other modules)
// ─────────────────────────────────────────────────────────────────────────────

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
      "Access-Control-Allow-Headers": "Content-Type, X-User-ID",
    },
  });
}

export async function parseJson(request) {
  try {
    return await request.json();
  } catch {
    return { error: "Invalid JSON" };
  }
}

export async function requireUser(env, userId) {
  if (!userId) return null;
  const user = await env.DB.prepare(
    "SELECT id, email, tier, stripe_customer_id, stripe_subscription_id FROM users WHERE id = ?"
  ).bind(userId).first();
  return user || null;
}

export function currentMonth() {
  return new Date().toISOString().slice(0, 7); // 'YYYY-MM'
}
