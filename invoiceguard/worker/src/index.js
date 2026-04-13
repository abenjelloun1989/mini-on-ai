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
      "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
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
