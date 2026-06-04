/**
 * budget-lines.js — CRUD for budget_lines.
 */
import { corsJson, parseJson, num, str, HEX_COLOR_RE } from "./lib.js";

export async function listBudgetLines(request, env) {
  const { results } = await env.DB.prepare(
    `SELECT id, name, monthly_limit, color, emoji, is_active, sort_order, created_at
     FROM budget_lines ORDER BY sort_order ASC, created_at ASC`
  ).all();
  return corsJson(env, results || []);
}

export async function createBudgetLine(request, env) {
  const body = await parseJson(request);
  if (!body) return corsJson(env, { error: "Invalid JSON" }, 400);

  const name = str(body.name, 60);
  const limit = num(body.monthly_limit);
  if (!name) return corsJson(env, { error: "name requis" }, 400);
  if (limit === null || limit < 0) return corsJson(env, { error: "monthly_limit invalide" }, 400);

  const color = HEX_COLOR_RE.test(body.color || "") ? body.color : "#3498db";
  const emoji = str(body.emoji, 8) || null;
  const sortOrder = num(body.sort_order) ?? 0;
  const isActive = body.is_active === 0 || body.is_active === false ? 0 : 1;

  const row = await env.DB.prepare(
    `INSERT INTO budget_lines (name, monthly_limit, color, emoji, is_active, sort_order)
     VALUES (?, ?, ?, ?, ?, ?)
     RETURNING id, name, monthly_limit, color, emoji, is_active, sort_order, created_at`
  ).bind(name, limit, color, emoji, isActive, sortOrder).first();

  return corsJson(env, row, 201);
}

export async function updateBudgetLine(request, env, id) {
  const body = await parseJson(request);
  if (!body) return corsJson(env, { error: "Invalid JSON" }, 400);

  const existing = await env.DB.prepare("SELECT * FROM budget_lines WHERE id = ?")
    .bind(id).first();
  if (!existing) return corsJson(env, { error: "Introuvable" }, 404);

  const name = body.name !== undefined ? str(body.name, 60) || existing.name : existing.name;
  const limit = body.monthly_limit !== undefined ? (num(body.monthly_limit) ?? existing.monthly_limit) : existing.monthly_limit;
  const color = body.color !== undefined && HEX_COLOR_RE.test(body.color) ? body.color : existing.color;
  const emoji = body.emoji !== undefined ? (str(body.emoji, 8) || null) : existing.emoji;
  const isActive = body.is_active !== undefined ? (body.is_active ? 1 : 0) : existing.is_active;
  const sortOrder = body.sort_order !== undefined ? (num(body.sort_order) ?? existing.sort_order) : existing.sort_order;

  const row = await env.DB.prepare(
    `UPDATE budget_lines SET name=?, monthly_limit=?, color=?, emoji=?, is_active=?, sort_order=?
     WHERE id=?
     RETURNING id, name, monthly_limit, color, emoji, is_active, sort_order, created_at`
  ).bind(name, limit, color, emoji, isActive, sortOrder, id).first();

  return corsJson(env, row);
}

export async function deleteBudgetLine(request, env, id) {
  // Block hard-delete if transactions reference it; caller should deactivate instead.
  const ref = await env.DB.prepare(
    "SELECT COUNT(*) AS n FROM transactions WHERE budget_line_id = ?"
  ).bind(id).first();
  if (ref && ref.n > 0) {
    return corsJson(env, {
      error: "Cette ligne a des transactions. Désactive-la plutôt que de la supprimer.",
      has_transactions: true,
    }, 409);
  }
  await env.DB.prepare("DELETE FROM budget_lines WHERE id = ?").bind(id).run();
  return corsJson(env, { ok: true });
}
