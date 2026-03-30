/**
 * Cloudflare Worker — Brevo email subscribe proxy
 *
 * Receives { email } from the mini-on-ai.com subscribe forms and
 * forwards to Brevo API using the secret key stored in CF environment.
 *
 * Deploy:
 *   1. Paste this file into Cloudflare Workers (dashboard.cloudflare.com → Workers & Pages → Create)
 *   2. Add secret:  Settings → Variables → Add variable (type: Secret)
 *                   Name: BREVO_API_KEY   Value: xkeysib-...
 *   3. Add plain:   Name: BREVO_LIST_ID   Value: 2
 *   4. Copy the worker URL (e.g. https://subscribe.YOUR-SUBDOMAIN.workers.dev)
 *   5. Set BREVO_SUBSCRIBE_URL=<worker URL> in your .env and rebuild the site
 */

const ALLOWED_ORIGIN = "https://mini-on-ai.com";

export default {
  async fetch(request, env) {
    // CORS preflight
    if (request.method === "OPTIONS") {
      return cors(new Response(null, { status: 204 }));
    }

    if (request.method !== "POST") {
      return cors(new Response("Method Not Allowed", { status: 405 }));
    }

    let email;
    try {
      const body = await request.json();
      email = (body.email || "").trim().toLowerCase();
    } catch {
      return cors(new Response(JSON.stringify({ error: "Invalid JSON" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      }));
    }

    if (!email || !email.includes("@")) {
      return cors(new Response(JSON.stringify({ error: "Invalid email" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      }));
    }

    const listId = parseInt(env.BREVO_LIST_ID || "2", 10);

    const brevoRes = await fetch("https://api.brevo.com/v3/contacts", {
      method: "POST",
      headers: {
        "api-key": env.BREVO_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        listIds: [listId],
        updateEnabled: true,
      }),
    });

    // 201 = created, 204 = already exists (updated) — both are success
    if (brevoRes.ok || brevoRes.status === 204) {
      return cors(new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }));
    }

    const err = await brevoRes.text();
    console.error("Brevo error", brevoRes.status, err);
    return cors(new Response(JSON.stringify({ error: "Subscription failed" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    }));
  },
};

function cors(response) {
  const res = new Response(response.body, response);
  res.headers.set("Access-Control-Allow-Origin", ALLOWED_ORIGIN);
  res.headers.set("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.headers.set("Access-Control-Allow-Headers", "Content-Type");
  return res;
}
