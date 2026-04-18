/**
 * InvoiceGuard API — Cloudflare Worker
 *
 * Routes:
 *   POST /api/auth/register    — register anonymous user (UUID)
 *   GET  /api/usage            — get monthly usage count + tier
 *   POST /api/invoices         — create (track) an invoice
 *   GET  /api/invoices         — list user's invoices
 *   PATCH /api/invoices/:id    — update invoice (status, notes, etc.)
 *   DELETE /api/invoices/:id   — delete an invoice
 *   POST /api/parse            — AI: extract invoice fields from email text
 *   POST /api/remind           — AI: generate follow-up reminder email
 *   POST /api/subscribe        — create Stripe Checkout session ($7/month)
 *   POST /api/webhook/stripe   — Stripe webhook handler
 *   GET  /api/subscription     — get subscription status
 *   POST /api/portal           — create Stripe Customer Portal session
 *
 * Environment:
 *   DB               — D1 database binding
 *   KV               — KV namespace for rate limiting + cache
 *   ANTHROPIC_API_KEY — secret
 *   STRIPE_SECRET_KEY — secret
 *   STRIPE_WEBHOOK_SECRET — secret
 *   ALLOWED_ORIGIN   — chrome-extension:// URL
 */

import { handleRegister, getUsage } from "./auth.js";
import { handleCreateInvoice, handleListInvoices, handleUpdateInvoice, handleDeleteInvoice } from "./invoices.js";
import { handleParse } from "./parse.js";
import { handleRemind } from "./remind.js";
import {
  handleSubscribe,
  handleStripeWebhook,
  getSubscription,
  handlePortal,
} from "./billing.js";
import { handleLtdRedeem } from "./ltd.js";

export default {
  async fetch(request, env) {
    // Set origin for this request (used by all corsJson/corsOk calls)
    setRequestOrigin(request, env);

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

      // Invoices CRUD
      if (path === "/api/invoices" && request.method === "POST") {
        return handleCreateInvoice(request, env);
      }
      if (path === "/api/invoices" && request.method === "GET") {
        return handleListInvoices(request, env);
      }
      if (path.startsWith("/api/invoices/") && request.method === "PATCH") {
        return handleUpdateInvoice(request, env, path);
      }
      if (path.startsWith("/api/invoices/") && request.method === "DELETE") {
        return handleDeleteInvoice(request, env, path);
      }

      // AI endpoints
      if (path === "/api/parse" && request.method === "POST") {
        return handleParse(request, env);
      }
      if (path === "/api/remind" && request.method === "POST") {
        return handleRemind(request, env);
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

      // LTD
      if (path === "/api/ltd/redeem" && request.method === "POST") {
        return handleLtdRedeem(request, env);
      }

      // GDPR: user data deletion
      if (path === "/api/user" && request.method === "DELETE") {
        const userId = new URL(request.url).searchParams.get("user_id");
        if (!userId) return corsJson(env, { error: "Missing user_id" }, 400);
        await env.DB.prepare("DELETE FROM invoices WHERE user_id = ?").bind(userId).run();
        await env.DB.prepare("DELETE FROM users WHERE id = ?").bind(userId).run();
        return corsJson(env, { success: true });
      }

      return corsJson(env, { error: "Not found" }, 404);
    } catch (e) {
      console.error("Unhandled error:", e.message, e.stack);
      return corsJson(env, { error: "Internal server error" }, 500);
    }
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Shared helpers (exported for use in other modules)
// ─────────────────────────────────────────────────────────────────────────────

// Per-request origin — set at the start of each fetch, used by all helpers
let _currentOrigin = "*";

export function setRequestOrigin(request, env) {
  const origin = request.headers.get("Origin") || "";
  const ext = env.ALLOWED_ORIGIN || "";
  if (origin === "https://mail.google.com") { _currentOrigin = origin; return; }
  if (origin.startsWith("chrome-extension://")) { _currentOrigin = origin; return; }
  _currentOrigin = ext || "*";
}

export function corsJson(env, obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": _currentOrigin,
      "Vary": "Origin",
    },
  });
}

export function corsOk(env) {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": _currentOrigin,
      "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-User-ID",
      "Vary": "Origin",
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
    "SELECT id, email, tier, stripe_customer_id, stripe_subscription_id, pro_source FROM users WHERE id = ?"
  ).bind(userId).first();
  return user || null;
}

export function currentMonth() {
  return new Date().toISOString().slice(0, 7); // 'YYYY-MM'
}
