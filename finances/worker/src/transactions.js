/**
 * transactions.js — CRUD for transactions.
 */
import { corsJson, parseJson, num, str, MONTH_RE, DATE_RE, currentMonth, today } from "./lib.js";

export async function listTransactions(request, env) {
  const url = new URL(request.url);
  const month = url.searchParams.get("month") || currentMonth();
  if (!MONTH_RE.test(month)) return corsJson(env, { error: "month invalide" }, 400);

  const { results } = await env.DB.prepare(
    `SELECT t.id, t.date, t.label, t.amount, t.budget_line_id, t.notes, t.created_at,
            b.name AS budget_name, b.color AS budget_color, b.emoji AS budget_emoji
     FROM transactions t
     LEFT JOIN budget_lines b ON b.id = t.budget_line_id
     WHERE substr(t.date, 1, 7) = ?
     ORDER BY t.date DESC, t.created_at DESC`
  ).bind(month).all();

  return corsJson(env, results || []);
}

export async function createTransaction(request, env) {
  const body = await parseJson(request);
  if (!body) return corsJson(env, { error: "Invalid JSON" }, 400);

  const amount = num(body.amount);
  if (amount === null || amount === 0) return corsJson(env, { error: "amount invalide" }, 400);

  const date = DATE_RE.test(body.date || "") ? body.date : today();
  const label = str(body.label, 120) || "Sans libellé";
  const notes = str(body.notes, 1000) || null;
  const budgetLineId = body.budget_line_id ? str(body.budget_line_id, 40) : null;

  if (budgetLineId) {
    const exists = await env.DB.prepare("SELECT 1 FROM budget_lines WHERE id = ?")
      .bind(budgetLineId).first();
    if (!exists) return corsJson(env, { error: "budget_line_id inconnu" }, 400);
  }

  const row = await env.DB.prepare(
    `INSERT INTO transactions (date, label, amount, budget_line_id, notes)
     VALUES (?, ?, ?, ?, ?)
     RETURNING id, date, label, amount, budget_line_id, notes, created_at`
  ).bind(date, label, amount, budgetLineId, notes).first();

  return corsJson(env, row, 201);
}

export async function updateTransaction(request, env, id) {
  const body = await parseJson(request);
  if (!body) return corsJson(env, { error: "Invalid JSON" }, 400);

  const existing = await env.DB.prepare("SELECT * FROM transactions WHERE id = ?")
    .bind(id).first();
  if (!existing) return corsJson(env, { error: "Introuvable" }, 404);

  const amount = body.amount !== undefined ? (num(body.amount) ?? existing.amount) : existing.amount;
  const date = body.date !== undefined && DATE_RE.test(body.date) ? body.date : existing.date;
  const label = body.label !== undefined ? (str(body.label, 120) || existing.label) : existing.label;
  const notes = body.notes !== undefined ? (str(body.notes, 1000) || null) : existing.notes;
  let budgetLineId = body.budget_line_id !== undefined
    ? (body.budget_line_id ? str(body.budget_line_id, 40) : null)
    : existing.budget_line_id;

  if (budgetLineId && body.budget_line_id !== undefined) {
    const exists = await env.DB.prepare("SELECT 1 FROM budget_lines WHERE id = ?")
      .bind(budgetLineId).first();
    if (!exists) return corsJson(env, { error: "budget_line_id inconnu" }, 400);
  }

  const row = await env.DB.prepare(
    `UPDATE transactions SET date=?, label=?, amount=?, budget_line_id=?, notes=?
     WHERE id=?
     RETURNING id, date, label, amount, budget_line_id, notes, created_at`
  ).bind(date, label, amount, budgetLineId, notes, id).first();

  return corsJson(env, row);
}

export async function deleteTransaction(request, env, id) {
  await env.DB.prepare("DELETE FROM transactions WHERE id = ?").bind(id).run();
  return corsJson(env, { ok: true });
}
