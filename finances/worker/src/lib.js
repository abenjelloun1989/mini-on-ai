/**
 * lib.js — shared helpers: CORS responses, JSON parsing, input validation.
 */

export function corsHeaders(env) {
  return {
    "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Cf-Access-Jwt-Assertion",
    "Access-Control-Allow-Credentials": "true",
    "Vary": "Origin",
  };
}

export function corsJson(env, obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(env) },
  });
}

export function corsOk(env) {
  return new Response(null, { status: 204, headers: corsHeaders(env) });
}

/** Parse a JSON request body, returning {} on any failure. */
export async function parseJson(request) {
  try {
    const text = await request.text();
    if (!text) return {};
    return JSON.parse(text);
  } catch {
    return null; // signal malformed body
  }
}

// ─── Validation ───────────────────────────────────────────────────────────────

export const MONTH_RE = /^\d{4}-\d{2}$/;
export const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
export const HEX_COLOR_RE = /^#[0-9a-fA-F]{6}$/;

/** Coerce to a finite number or return null. */
export function num(v) {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

/** Trim + length-cap a string; returns "" for nullish. */
export function str(v, max = 500) {
  if (v === null || v === undefined) return "";
  return String(v).trim().slice(0, max);
}

/** Current month as YYYY-MM (UTC). */
export function currentMonth() {
  return new Date().toISOString().slice(0, 7);
}

/** Today as YYYY-MM-DD (UTC). */
export function today() {
  return new Date().toISOString().slice(0, 10);
}
