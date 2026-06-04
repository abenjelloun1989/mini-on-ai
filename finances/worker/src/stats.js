/**
 * stats.js — aggregate financial figures for a month (no raw transactions leak).
 */
import { corsJson, MONTH_RE, currentMonth } from "./lib.js";

/** Shift a YYYY-MM month by `delta` months. */
function shiftMonth(month, delta) {
  const [y, m] = month.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + delta, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}

/** Income / expenses totals for a single month. */
async function monthTotals(env, month) {
  const row = await env.DB.prepare(
    `SELECT
       COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) AS income,
       COALESCE(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 0) AS expenses
     FROM transactions WHERE substr(date, 1, 7) = ?`
  ).bind(month).first();
  return { income: row?.income || 0, expenses: row?.expenses || 0 };
}

/**
 * Compute the full stats payload for a month.
 * Returns { income, expenses, by_budget_line, last_3_months }.
 */
export async function computeStats(env, month) {
  const m = MONTH_RE.test(month || "") ? month : currentMonth();

  const totals = await monthTotals(env, m);

  // Spending per active budget line (expenses only, as positive numbers)
  const { results: lines } = await env.DB.prepare(
    `SELECT b.id, b.name, b.color, b.emoji, b.monthly_limit AS "limit",
            COALESCE((
              SELECT SUM(-t.amount) FROM transactions t
              WHERE t.budget_line_id = b.id
                AND t.amount < 0
                AND substr(t.date, 1, 7) = ?
            ), 0) AS spent
     FROM budget_lines b
     WHERE b.is_active = 1
     ORDER BY b.sort_order ASC, b.created_at ASC`
  ).bind(m).all();

  const by_budget_line = (lines || []).map((l) => {
    const limit = l.limit || 0;
    const spent = l.spent || 0;
    const remaining = limit - spent;
    const pct = limit > 0 ? Math.round((spent / limit) * 100) : (spent > 0 ? 100 : 0);
    return { id: l.id, name: l.name, color: l.color, emoji: l.emoji, limit, spent, remaining, pct };
  });

  // Last 3 months (including requested), oldest first
  const months = [shiftMonth(m, -2), shiftMonth(m, -1), m];
  const last_3_months = [];
  for (const mm of months) {
    const t = await monthTotals(env, mm);
    last_3_months.push({ month: mm, income: t.income, expenses: t.expenses });
  }

  return {
    income: totals.income,
    expenses: totals.expenses,
    by_budget_line,
    last_3_months,
  };
}

export async function getStats(request, env) {
  const url = new URL(request.url);
  const month = url.searchParams.get("month") || currentMonth();
  if (!MONTH_RE.test(month)) return corsJson(env, { error: "month invalide" }, 400);
  return corsJson(env, await computeStats(env, month));
}
