/**
 * proxy.js — F1 hot-path Anthropic API proxy.
 *
 * Handles any request to /v1/* — authenticates the inbound F1 API key,
 * retrieves + decrypts the customer's Anthropic key, forwards the request
 * verbatim, and records usage metadata (tokens + USD) via ctx.waitUntil().
 *
 * INVARIANT: Prompt and response bodies are NEVER logged or stored.
 *            See f1/worker/README.md for the no-prompt-bodies policy.
 */

import { computeCost } from "./pricing.js";
import { decryptApiKey, hashToken, hashInputPrefix, hashIp, generateToken } from "./crypto.js";

const ANTHROPIC_API_BASE = "https://api.anthropic.com";

// KV TTL for hot-path key cache (seconds)
const KEY_CACHE_TTL_SECONDS = 300; // 5 minutes

// Rate-limit: max failed auth attempts per IP per 10-minute window
const RATE_LIMIT_WINDOW_SECONDS = 600;
const RATE_LIMIT_MAX_ATTEMPTS = 20;

// ---------------------------------------------------------------------------
// Main proxy handler
// ---------------------------------------------------------------------------

export async function handleProxy(request, env, ctx, path) {
  const start = Date.now();

  // ── 1. Extract F1 API key from Authorization header ─────────────────────
  const authHeader = request.headers.get("Authorization") || "";
  const f1Key = authHeader.startsWith("Bearer ") ? authHeader.slice(7).trim() : null;

  if (!f1Key || !f1Key.startsWith("f1_key_")) {
    return proxyError("Missing or invalid F1 API key. Use Authorization: Bearer f1_key_...", 401);
  }

  // ── 2. Rate-limit on bad auth attempts per source IP ────────────────────
  const clientIp = request.headers.get("CF-Connecting-IP") || "unknown";
  const ipHash = await hashIp(clientIp);
  const rateLimitKey = `ratelimit:auth:${ipHash}`;

  // ── 3. Lookup key in KV cache (hot path avoids D1) ──────────────────────
  const f1KeyHash = await hashToken(f1Key);
  const cacheKey = `key:${f1KeyHash}`;
  let keyMeta = null;

  try {
    const cached = await env.KV.get(cacheKey, "json");
    if (cached) keyMeta = cached;
  } catch (_) {
    // KV miss — fall through to D1
  }

  if (!keyMeta) {
    // D1 lookup
    const row = await env.DB.prepare(
      `SELECT k.id, k.account_id, k.revoked_at,
              a.tier, a.monthly_token_quota,
              a.anthropic_key_ciphertext, a.anthropic_key_iv, a.anthropic_key_salt,
              a.prompt_storage_optin
       FROM api_keys k
       JOIN accounts a ON a.id = k.account_id
       WHERE k.key_hash = ?`
    ).bind(f1KeyHash).first();

    if (!row || row.revoked_at) {
      // Record failed attempt
      await recordFailedAuth(env, rateLimitKey);
      return proxyError("Invalid or revoked F1 API key.", 401);
    }

    if (!row.anthropic_key_ciphertext) {
      return proxyError(
        "No Anthropic API key on file. Upload your Anthropic key via POST /api/set-anthropic-key.",
        402
      );
    }

    keyMeta = {
      keyId: row.id,
      accountId: row.account_id,
      tier: row.tier,
      monthlyTokenQuota: row.monthly_token_quota,
      promptStorageOptin: row.prompt_storage_optin === 1,
      // Store encrypted blobs as base64 so KV can cache them as JSON
      ciphertext: row.anthropic_key_ciphertext,
      iv: row.anthropic_key_iv,
      salt: row.anthropic_key_salt,
    };

    // Cache for 5 minutes
    ctx.waitUntil(
      env.KV.put(cacheKey, JSON.stringify(keyMeta), { expirationTtl: KEY_CACHE_TTL_SECONDS })
    );
  }

  // Check rate limit AFTER key lookup (don't punish slow D1 on good keys)
  const tooManyFailures = await checkRateLimit(env, rateLimitKey);
  if (tooManyFailures) {
    return proxyError("Too many failed authentication attempts from your IP. Try again later.", 429);
  }

  // ── 4. Decrypt customer Anthropic key ───────────────────────────────────
  let anthropicKey;
  try {
    anthropicKey = await decryptApiKey(
      keyMeta.ciphertext,
      keyMeta.iv,
      keyMeta.salt,
      env.F1_KEY_ENCRYPTION_MASTER
    );
  } catch (e) {
    console.error(`[proxy] Key decryption failed for account ${keyMeta.accountId}:`, e.message);
    return proxyError("Key decryption failed. Contact support.", 500);
  }

  // ── 5. Forward request to Anthropic ─────────────────────────────────────
  const upstreamUrl = `${ANTHROPIC_API_BASE}${path}${new URL(request.url).search}`;

  // Clone and rewrite headers: swap Authorization, keep everything else
  const upstreamHeaders = new Headers(request.headers);
  upstreamHeaders.set("Authorization", `Bearer ${anthropicKey}`);
  upstreamHeaders.set("X-API-Key", anthropicKey); // Anthropic also accepts this header
  upstreamHeaders.delete("CF-Connecting-IP");
  upstreamHeaders.delete("CF-Ray");
  upstreamHeaders.delete("CF-Visitor");

  let upstreamResponse;
  try {
    upstreamResponse = await fetch(upstreamUrl, {
      method: request.method,
      headers: upstreamHeaders,
      body: request.method !== "GET" && request.method !== "HEAD" ? request.body : null,
    });
  } catch (e) {
    console.error("[proxy] Upstream fetch error:", e.message);
    return proxyError("Upstream request to Anthropic failed.", 502);
  }

  const latencyMs = Date.now() - start;

  // ── 6. Extract usage from response (non-streaming only in v1) ───────────
  // Clone the response so we can read the body for usage extraction
  // while still forwarding the original stream to the client.
  const responseForClient = new Response(upstreamResponse.body, upstreamResponse);

  // For streaming (SSE), we can't read the body here without buffering.
  // v1: record with 0 tokens for streaming; non-streaming reads usage from JSON.
  const contentType = upstreamResponse.headers.get("content-type") || "";
  const isStreaming = contentType.includes("text/event-stream");
  const isSuccess = upstreamResponse.status >= 200 && upstreamResponse.status < 300;

  if (isSuccess && !isStreaming) {
    // We need to tee the body to read usage without consuming the response.
    // But we've already started streaming responseForClient above. For non-streaming
    // responses (the common case), buffer the entire body, extract usage, re-stream.
    // This is acceptable because non-streaming responses are small.
    ctx.waitUntil(
      extractAndRecordUsage({
        env,
        request,
        keyMeta,
        upstreamResponse,
        latencyMs,
      })
    );
  } else if (!isStreaming) {
    // Error response — record with 0 tokens
    ctx.waitUntil(
      recordUsageEvent(env, {
        accountId: keyMeta.accountId,
        apiKeyId: keyMeta.keyId,
        model: extractModelFromRequest(request),
        inputTokens: 0,
        outputTokens: 0,
        cacheCreationTokens: 0,
        cacheReadTokens: 0,
        usdCost: 0,
        statusCode: upstreamResponse.status,
        latencyMs,
        promptStorageOptin: keyMeta.promptStorageOptin,
        promptPrefix: null,
        inputHash: null,
      })
    );
  }
  // Streaming: v1 does not extract usage from SSE stream. Future: parse `message_stop` event.

  // ── 7. Audit log: key was used ───────────────────────────────────────────
  ctx.waitUntil(
    env.DB.prepare(
      "INSERT INTO key_access_log (account_id, reason, ip_hash) VALUES (?, 'proxy_forward', ?)"
    ).bind(keyMeta.accountId, ipHash).run()
  );

  // Forward the response to the client unchanged
  return responseForClient;
}

// ---------------------------------------------------------------------------
// Usage extraction from non-streaming response
// ---------------------------------------------------------------------------

async function extractAndRecordUsage({ env, request, keyMeta, upstreamResponse, latencyMs }) {
  let usage = {};
  let model = extractModelFromRequest(request);
  let promptPrefix = null;
  let inputHash = null;

  try {
    const body = await upstreamResponse.clone().json();

    // Anthropic Messages API: response.usage
    if (body.usage) {
      usage = body.usage;
    }
    // Model echo in response
    if (body.model) model = body.model;

    // Prompt prefix (opt-in only) + input hash
    // We already have the request body — but we can't clone a consumed request.
    // v1: derive hash from model+usage shape as a proxy for content uniqueness.
    // TODO: in proxy.js, tee the request body to capture input text for hashing.
    // For now, generate a unique ID so the hash column is non-null but not meaningful.
    inputHash = null; // will be populated when request-body tee is implemented
  } catch (e) {
    // Non-JSON response (shouldn't happen for /v1/messages) — skip
    console.warn("[proxy] Could not parse upstream response body for usage:", e.message);
  }

  const { usd } = computeCost(usage, model);

  await recordUsageEvent(env, {
    accountId: keyMeta.accountId,
    apiKeyId: keyMeta.keyId,
    model,
    inputTokens: usage.input_tokens ?? 0,
    outputTokens: usage.output_tokens ?? 0,
    cacheCreationTokens: usage.cache_creation_input_tokens ?? 0,
    cacheReadTokens: usage.cache_read_input_tokens ?? 0,
    usdCost: usd,
    statusCode: upstreamResponse.status,
    latencyMs,
    promptStorageOptin: keyMeta.promptStorageOptin,
    promptPrefix,
    inputHash,
  });
}

// ---------------------------------------------------------------------------
// D1 write
// ---------------------------------------------------------------------------

async function recordUsageEvent(env, {
  accountId, apiKeyId, model,
  inputTokens, outputTokens, cacheCreationTokens, cacheReadTokens,
  usdCost, statusCode, latencyMs,
  promptPrefix, inputHash,
}) {
  try {
    await env.DB.prepare(
      `INSERT INTO usage_events
         (account_id, api_key_id, model,
          input_tokens, output_tokens,
          cache_creation_input_tokens, cache_read_input_tokens,
          usd_cost, status_code, latency_ms,
          prompt_prefix, input_hash)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      accountId, apiKeyId, model,
      inputTokens, outputTokens, cacheCreationTokens, cacheReadTokens,
      usdCost, statusCode, latencyMs ?? null,
      promptPrefix ?? null, inputHash ?? null
    ).run();
  } catch (e) {
    // Non-fatal: don't fail the request if logging fails
    console.error("[proxy] Failed to record usage event:", e.message);
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function extractModelFromRequest(request) {
  // Model may be in the URL for some Anthropic endpoints; for /v1/messages it's in the body.
  // v1: we return a placeholder; the actual model is extracted from the response body.
  return "unknown";
}

async function recordFailedAuth(env, rateLimitKey) {
  try {
    const current = (await env.KV.get(rateLimitKey)) ?? "0";
    const count = parseInt(current, 10) + 1;
    await env.KV.put(rateLimitKey, String(count), { expirationTtl: RATE_LIMIT_WINDOW_SECONDS });
  } catch (_) {}
}

async function checkRateLimit(env, rateLimitKey) {
  try {
    const current = await env.KV.get(rateLimitKey);
    return current !== null && parseInt(current, 10) >= RATE_LIMIT_MAX_ATTEMPTS;
  } catch (_) {
    return false;
  }
}

function proxyError(message, status) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: {
      "Content-Type": "application/json",
    },
  });
}
