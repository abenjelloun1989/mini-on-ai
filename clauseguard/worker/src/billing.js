import { corsJson, parseJson, requireUser } from "./index.js";

const STRIPE_PRICE_ID = "price_1TLiESCHYMwZNPVbmmvHEIyE";
const SITE_URL = "https://mini-on-ai.com";

// -----------------------------------------------------------------------------
// POST /api/subscribe -- create Stripe Checkout session for $7/month
// -----------------------------------------------------------------------------

export async function handleSubscribe(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id } = body;
  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  if (user.tier === "pro") {
    return corsJson(env, { error: "Already subscribed to Pro" }, 400);
  }

  const params = new URLSearchParams({
    "mode": "subscription",
    "line_items[0][price]": STRIPE_PRICE_ID,
    "line_items[0][quantity]": "1",
    "metadata[user_id]": user_id,
    "subscription_data[metadata][user_id]": user_id,
    "success_url": `${SITE_URL}/clauseguard/success?session_id={CHECKOUT_SESSION_ID}`,
    "cancel_url": `${SITE_URL}/clauseguard`,
  });

  if (user.email) {
    params.set("customer_email", user.email);
  }

  const stripeRes = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.STRIPE_SECRET_KEY}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: params,
  });

  if (!stripeRes.ok) {
    const err = await stripeRes.text();
    console.error("Stripe Checkout error:", err);
    return corsJson(env, { error: "Payment setup failed. Please try again." }, 500);
  }

  const session = await stripeRes.json();
  return corsJson(env, { checkout_url: session.url });
}

// -----------------------------------------------------------------------------
// POST /api/webhook/stripe -- handle Stripe subscription lifecycle events
// -----------------------------------------------------------------------------

export async function handleStripeWebhook(request, env) {
  const payload = await request.text();
  const signature = request.headers.get("stripe-signature");

  if (env.STRIPE_WEBHOOK_SECRET && signature) {
    const isValid = await verifyStripeSignature(payload, signature, env.STRIPE_WEBHOOK_SECRET);
    if (!isValid) {
      console.error("Invalid Stripe webhook signature");
      return new Response("Invalid signature", { status: 400 });
    }
  }

  let event;
  try {
    event = JSON.parse(payload);
  } catch {
    return new Response("Invalid JSON", { status: 400 });
  }

  const type = event.type;
  const obj = event.data?.object;

  if (type === "checkout.session.completed" && obj.mode === "subscription") {
    const userId = obj.metadata?.user_id;
    if (userId) {
      await env.DB.prepare(
        "UPDATE users SET tier = 'pro', stripe_customer_id = ?, stripe_subscription_id = ?, email = COALESCE(?, email), updated_at = datetime('now') WHERE id = ?"
      ).bind(
        obj.customer,
        obj.subscription,
        obj.customer_details?.email || null,
        userId,
      ).run();
    }
  }

  if (type === "customer.subscription.deleted") {
    const subId = obj.id;
    await env.DB.prepare(
      "UPDATE users SET tier = 'free', stripe_subscription_id = NULL, updated_at = datetime('now') WHERE stripe_subscription_id = ?"
    ).bind(subId).run();
  }

  if (type === "invoice.payment_failed") {
    const subId = obj.subscription;
    console.warn("Payment failed for subscription:", subId);
  }

  return new Response("ok", { status: 200 });
}

// -----------------------------------------------------------------------------
// GET /api/subscription?user_id=...
// -----------------------------------------------------------------------------

export async function getSubscription(request, env) {
  const userId = new URL(request.url).searchParams.get("user_id");
  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  return corsJson(env, {
    tier: user.tier,
    has_subscription: !!user.stripe_subscription_id,
    email: user.email || null,
  });
}

// -----------------------------------------------------------------------------
// POST /api/portal -- create Stripe Customer Portal session
// -----------------------------------------------------------------------------

export async function handlePortal(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id } = body;
  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);
  if (!user.stripe_customer_id) {
    return corsJson(env, { error: "No active subscription" }, 400);
  }

  const stripeRes = await fetch("https://api.stripe.com/v1/billing_portal/sessions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.STRIPE_SECRET_KEY}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      "customer": user.stripe_customer_id,
      "return_url": `${SITE_URL}/clauseguard`,
    }),
  });

  if (!stripeRes.ok) {
    const err = await stripeRes.text();
    console.error("Stripe Portal error:", err);
    return corsJson(env, { error: "Could not open billing portal." }, 500);
  }

  const session = await stripeRes.json();
  return corsJson(env, { portal_url: session.url });
}

// -----------------------------------------------------------------------------
// Stripe webhook signature verification (HMAC-SHA256)
// -----------------------------------------------------------------------------

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

    const signedPayload = `${timestamp}.${payload}`;
    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );
    const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(signedPayload));
    const expected = Array.from(new Uint8Array(sig))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

    return expected === signature;
  } catch {
    return false;
  }
}
