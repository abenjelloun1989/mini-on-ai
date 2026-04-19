import { corsJson, parseJson, requireUser } from "./index.js";

const STRIPE_PRICE_ID = "REPLACE_WITH_STRIPE_PRICE_ID"; // $7/month
const SITE_URL = "https://mini-on-ai.com";

// ─── POST /api/subscribe ──────────────────────────────────────────────────────

export async function handleSubscribe(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id } = body;
  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);
  if (user.tier === "pro") return corsJson(env, { error: "Already subscribed to Pro" }, 400);

  const params = new URLSearchParams({
    "mode": "subscription",
    "line_items[0][price]": STRIPE_PRICE_ID,
    "line_items[0][quantity]": "1",
    "metadata[user_id]": user_id,
    "subscription_data[metadata][user_id]": user_id,
    "success_url": `${SITE_URL}/jobguard.html?upgraded=1`,
    "cancel_url": `${SITE_URL}/jobguard.html`,
  });
  if (user.email) params.set("customer_email", user.email);

  const ctrl = new AbortController();
  const timeout = setTimeout(() => ctrl.abort(), 10000);
  let res;
  try {
    res = await fetch("https://api.stripe.com/v1/checkout/sessions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.STRIPE_SECRET_KEY}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: params,
      signal: ctrl.signal,
    });
  } catch (e) {
    clearTimeout(timeout);
    console.error("Stripe Checkout error:", e.message);
    return corsJson(env, { error: "Payment setup failed. Please try again." }, 500);
  }
  clearTimeout(timeout);

  if (!res.ok) {
    console.error("Stripe Checkout error:", await res.text());
    return corsJson(env, { error: "Payment setup failed. Please try again." }, 500);
  }

  const session = await res.json();
  return corsJson(env, { checkout_url: session.url });
}

// ─── POST /api/webhook/stripe ─────────────────────────────────────────────────

export async function handleStripeWebhook(request, env) {
  const payload = await request.text();
  const signature = request.headers.get("stripe-signature");

  if (!env.STRIPE_WEBHOOK_SECRET) {
    console.error("STRIPE_WEBHOOK_SECRET not configured");
    return new Response("Webhook secret not configured", { status: 500 });
  }
  if (!signature) return new Response("Missing stripe-signature", { status: 400 });

  const isValid = await verifyStripeSignature(payload, signature, env.STRIPE_WEBHOOK_SECRET);
  if (!isValid) return new Response("Invalid signature", { status: 400 });

  let event;
  try { event = JSON.parse(payload); }
  catch { return new Response("Invalid JSON", { status: 400 }); }

  const type = event.type;
  const obj = event.data?.object;

  if (type === "checkout.session.completed" && obj.mode === "subscription") {
    const userId = obj.metadata?.user_id;
    if (userId) {
      await env.DB.prepare(
        "UPDATE users SET tier = 'pro', stripe_customer_id = ?, stripe_subscription_id = ?, email = COALESCE(?, email), updated_at = datetime('now') WHERE id = ?"
      ).bind(obj.customer, obj.subscription, obj.customer_details?.email || null, userId).run();
    }
  }

  if (type === "customer.subscription.deleted") {
    await env.DB.prepare(
      "UPDATE users SET tier = 'free', stripe_subscription_id = NULL, updated_at = datetime('now') WHERE stripe_subscription_id = ? AND (pro_source IS NULL OR pro_source != 'ltd')"
    ).bind(obj.id).run();
  }

  if (type === "invoice.payment_failed") {
    console.warn("Payment failed for subscription:", obj.subscription);
  }

  return new Response("ok", { status: 200 });
}

// ─── GET /api/subscription ────────────────────────────────────────────────────

export async function getSubscription(request, env) {
  const userId = new URL(request.url).searchParams.get("user_id");
  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  return corsJson(env, {
    tier: user.tier,
    pro_source: user.pro_source || null,
    has_subscription: !!user.stripe_subscription_id,
    email: user.email || null,
  });
}

// ─── POST /api/portal ─────────────────────────────────────────────────────────

export async function handlePortal(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id } = body;
  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);
  if (!user.stripe_customer_id) return corsJson(env, { error: "No active subscription" }, 400);

  const ctrl = new AbortController();
  const timeout = setTimeout(() => ctrl.abort(), 10000);
  let res;
  try {
    res = await fetch("https://api.stripe.com/v1/billing_portal/sessions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.STRIPE_SECRET_KEY}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        "customer": user.stripe_customer_id,
        "return_url": `${SITE_URL}/jobguard.html`,
      }),
      signal: ctrl.signal,
    });
  } catch (e) {
    clearTimeout(timeout);
    console.error("Stripe Portal error:", e.message);
    return corsJson(env, { error: "Could not open billing portal." }, 500);
  }
  clearTimeout(timeout);

  if (!res.ok) {
    console.error("Stripe Portal error:", await res.text());
    return corsJson(env, { error: "Could not open billing portal." }, 500);
  }

  const session = await res.json();
  return corsJson(env, { portal_url: session.url });
}

// ─── Stripe webhook signature verification ────────────────────────────────────

async function verifyStripeSignature(payload, signatureHeader, secret) {
  try {
    const parts = signatureHeader.split(",").reduce((acc, part) => {
      const [key, value] = part.split("=");
      acc[key.trim()] = value;
      return acc;
    }, {});

    const timestamp = parts.t;
    const signature = parts.v1;
    if (!timestamp || !signature) return false;

    const age = Math.abs(Date.now() / 1000 - parseInt(timestamp));
    if (age > 300) return false;

    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );
    const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${timestamp}.${payload}`));
    const expected = Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, "0")).join("");
    return expected === signature;
  } catch {
    return false;
  }
}
