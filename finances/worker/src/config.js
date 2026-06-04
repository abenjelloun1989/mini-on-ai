/**
 * config.js — read/write the single config row (id=1), data stored as JSON text.
 */
import { corsJson, parseJson, num, str, DATE_RE } from "./lib.js";

const DEFAULT_CONFIG = {
  monthly_income: 0,
  budget_note: "",
  cash: 0,
  savings_invested: 0,
  savings_pending: 0,
  savings_pending_date: "",
  minimum_reserve: 0,
  one_time_events: [],
};

export async function readConfig(env) {
  const row = await env.DB.prepare("SELECT data FROM config WHERE id = 1").first();
  let data = {};
  try { data = row ? JSON.parse(row.data) : {}; } catch { data = {}; }
  return { ...DEFAULT_CONFIG, ...data };
}

export async function getConfig(request, env) {
  return corsJson(env, await readConfig(env));
}

/** Sanitize an incoming config object into the known shape. */
function sanitizeConfig(body) {
  const out = { ...DEFAULT_CONFIG };
  out.monthly_income = num(body.monthly_income) ?? 0;
  out.cash = num(body.cash) ?? 0;
  out.savings_invested = num(body.savings_invested) ?? 0;
  out.savings_pending = num(body.savings_pending) ?? 0;
  out.minimum_reserve = num(body.minimum_reserve) ?? 0;
  out.budget_note = str(body.budget_note, 2000);
  out.savings_pending_date = DATE_RE.test(body.savings_pending_date || "")
    ? body.savings_pending_date : "";

  const events = Array.isArray(body.one_time_events) ? body.one_time_events : [];
  out.one_time_events = events.slice(0, 100).map((e) => ({
    date: DATE_RE.test(e?.date || "") ? e.date : "",
    label: str(e?.label, 120),
    amount: num(e?.amount) ?? 0,
  })).filter((e) => e.date || e.label || e.amount);

  return out;
}

export async function putConfig(request, env) {
  const body = await parseJson(request);
  if (!body) return corsJson(env, { error: "Invalid JSON" }, 400);
  const clean = sanitizeConfig(body);
  await env.DB.prepare(
    "UPDATE config SET data = ?, updated_at = datetime('now') WHERE id = 1"
  ).bind(JSON.stringify(clean)).run();
  return corsJson(env, clean);
}
