/**
 * auth.js — Cloudflare Access (Zero Trust) JWT verification.
 *
 * Cloudflare Access signs an RS256 JWT and sends it on every request to the
 * origin as the `Cf-Access-Jwt-Assertion` header (also a CF_Authorization
 * cookie). We verify the signature against the team's public JWKS and validate
 * the iss / aud / exp / email claims.
 *
 * The JWKS is cached in globalThis so we don't refetch it on every request.
 */

const JWKS_TTL_MS = 60 * 60 * 1000; // 1 hour

// ─── base64url helpers ──────────────────────────────────────────────────────

function b64urlToBytes(b64url) {
  const b64 = b64url.replace(/-/g, "+").replace(/_/g, "/").padEnd(
    Math.ceil(b64url.length / 4) * 4,
    "="
  );
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

function b64urlToString(b64url) {
  return new TextDecoder().decode(b64urlToBytes(b64url));
}

// ─── JWKS cache ─────────────────────────────────────────────────────────────

async function getJwks(teamDomain) {
  const now = Date.now();
  const cache = globalThis.__cfAccessJwks;
  if (cache && cache.domain === teamDomain && now - cache.at < JWKS_TTL_MS) {
    return cache.keys;
  }
  const url = `https://${teamDomain}/cdn-cgi/access/certs`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`JWKS fetch failed: ${resp.status}`);
  const data = await resp.json();
  const keys = data.keys || [];
  globalThis.__cfAccessJwks = { domain: teamDomain, at: now, keys };
  return keys;
}

async function importKey(jwk) {
  return crypto.subtle.importKey(
    "jwk",
    { kty: jwk.kty, n: jwk.n, e: jwk.e, alg: "RS256", ext: true },
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["verify"]
  );
}

// ─── Verification ───────────────────────────────────────────────────────────

/**
 * Verify the Access JWT on a request.
 * @returns {{ ok: true, email: string } | { ok: false, status: number, error: string }}
 */
export async function requireAccess(request, env) {
  // Local-dev escape hatch — only honored if DEV_BYPASS_AUTH is explicitly set
  // (kept out of production via .dev.vars; never set it as a deployed secret).
  if (env.DEV_BYPASS_AUTH === "1") {
    return { ok: true, email: env.ALLOWED_EMAIL || "dev@local" };
  }

  const teamDomain = env.CF_ACCESS_TEAM_DOMAIN;
  const aud = env.CF_ACCESS_AUD;
  if (!teamDomain || !aud) {
    return { ok: false, status: 500, error: "Auth not configured" };
  }

  const token =
    request.headers.get("Cf-Access-Jwt-Assertion") ||
    cookieValue(request.headers.get("Cookie"), "CF_Authorization");
  if (!token) return { ok: false, status: 401, error: "Missing Access token" };

  const parts = token.split(".");
  if (parts.length !== 3) return { ok: false, status: 401, error: "Malformed token" };

  let header, payload;
  try {
    header = JSON.parse(b64urlToString(parts[0]));
    payload = JSON.parse(b64urlToString(parts[1]));
  } catch {
    return { ok: false, status: 401, error: "Malformed token" };
  }

  // Find the signing key by kid
  let keys;
  try {
    keys = await getJwks(teamDomain);
  } catch {
    return { ok: false, status: 503, error: "Cannot verify token" };
  }
  const jwk = keys.find((k) => k.kid === header.kid);
  if (!jwk) return { ok: false, status: 401, error: "Unknown signing key" };

  // Verify signature over `${header}.${payload}`
  let valid = false;
  try {
    const key = await importKey(jwk);
    const signed = new TextEncoder().encode(`${parts[0]}.${parts[1]}`);
    valid = await crypto.subtle.verify(
      "RSASSA-PKCS1-v1_5",
      key,
      b64urlToBytes(parts[2]),
      signed
    );
  } catch {
    valid = false;
  }
  if (!valid) return { ok: false, status: 401, error: "Invalid signature" };

  // Validate claims
  const nowSec = Math.floor(Date.now() / 1000);
  if (payload.exp && payload.exp < nowSec) {
    return { ok: false, status: 401, error: "Token expired" };
  }
  if (payload.nbf && payload.nbf > nowSec + 60) {
    return { ok: false, status: 401, error: "Token not yet valid" };
  }
  if (payload.iss !== `https://${teamDomain}`) {
    return { ok: false, status: 401, error: "Bad issuer" };
  }
  const audClaim = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
  if (!audClaim.includes(aud)) {
    return { ok: false, status: 401, error: "Bad audience" };
  }
  // Hardening: single allowed email
  if (env.ALLOWED_EMAIL && payload.email !== env.ALLOWED_EMAIL) {
    return { ok: false, status: 403, error: "Email not allowed" };
  }

  return { ok: true, email: payload.email || "" };
}

function cookieValue(cookieHeader, name) {
  if (!cookieHeader) return null;
  for (const part of cookieHeader.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return null;
}
