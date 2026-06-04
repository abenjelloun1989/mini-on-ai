/**
 * api.js — all /api/* calls. Uses credentials:'include' so the Cloudflare Access
 * cookie rides along. Surfaces offline + 401.
 *
 * API base: same-origin "/api" by default. If the Worker is on a separate host
 * (e.g. finances-worker.<acct>.workers.dev), set window.FINANCES_API_BASE in a
 * small inline <script> or edit API_BASE below.
 *
 * Demo mode: append ?demo=1 to the URL (or set localStorage 'fin-demo'='1') to run
 * the whole UI against in-memory fixtures — used for local visual verification
 * without a deployed Worker / D1 / Access.
 */
import { toast } from "./ui.js";

const API_BASE = (typeof window !== "undefined" && window.FINANCES_API_BASE) || "";

export const DEMO = (() => {
  try {
    const q = new URLSearchParams(location.search);
    if (q.get("demo") === "1") { localStorage.setItem("fin-demo", "1"); return true; }
    if (q.get("demo") === "0") { localStorage.removeItem("fin-demo"); return false; }
    return localStorage.getItem("fin-demo") === "1";
  } catch { return false; }
})();

async function req(method, path, body) {
  if (DEMO) return demo(method, path, body);
  let resp;
  try {
    resp = await fetch(API_BASE + path, {
      method,
      credentials: "include",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    toast("Mode hors ligne", { type: "err" });
    throw new Error("offline");
  }
  if (resp.status === 401 || resp.status === 403) {
    // Access session expired — reload so Cloudflare re-challenges.
    toast("Session expirée, reconnexion…", { type: "err" });
    setTimeout(() => location.reload(), 1200);
    throw new Error("unauthorized");
  }
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.error || `Erreur ${resp.status}`);
  return data;
}

export const api = {
  budgetLines: {
    list: () => req("GET", "/api/budget-lines"),
    create: (b) => req("POST", "/api/budget-lines", b),
    update: (id, b) => req("PUT", `/api/budget-lines/${id}`, b),
    remove: (id) => req("DELETE", `/api/budget-lines/${id}`),
  },
  transactions: {
    list: (month) => req("GET", `/api/transactions?month=${month}`),
    create: (b) => req("POST", "/api/transactions", b),
    update: (id, b) => req("PUT", `/api/transactions/${id}`, b),
    remove: (id) => req("DELETE", `/api/transactions/${id}`),
  },
  config: {
    get: () => req("GET", "/api/config"),
    put: (b) => req("PUT", "/api/config", b),
  },
  stats: (month) => req("GET", `/api/stats?month=${month}`),
  chat: {
    history: () => req("GET", "/api/chat"),
    send: (message) => req("POST", "/api/chat", { message }),
    clear: () => req("DELETE", "/api/chat"),
  },
};

// ─── Demo fixtures (in-memory, mutable) ───────────────────────────────────────

const _now = new Date();
const _ym = _now.toISOString().slice(0, 7);
const _d = (day) => `${_ym}-${String(day).padStart(2, "0")}`;

const demoState = {
  lines: [
    { id: "l1", name: "Vie courante", monthly_limit: 600, color: "#3498db", emoji: "🛒", is_active: 1, sort_order: 0, created_at: "2026-01-01" },
    { id: "l2", name: "Restaurants", monthly_limit: 200, color: "#e74c3c", emoji: "🍽️", is_active: 1, sort_order: 1, created_at: "2026-01-01" },
    { id: "l3", name: "Transport", monthly_limit: 120, color: "#f39c12", emoji: "🚗", is_active: 1, sort_order: 2, created_at: "2026-01-01" },
    { id: "l4", name: "Loisirs", monthly_limit: 150, color: "#9b59b6", emoji: "🎮", is_active: 1, sort_order: 3, created_at: "2026-01-01" },
    { id: "l5", name: "Logement", monthly_limit: 900, color: "#27ae60", emoji: "🏠", is_active: 1, sort_order: 4, created_at: "2026-01-01" },
  ],
  txs: [
    { id: "t1", date: _d(2), label: "Loyer", amount: -900, budget_line_id: "l5", notes: null },
    { id: "t2", date: _d(3), label: "Courses Carrefour", amount: -82.4, budget_line_id: "l1", notes: null },
    { id: "t3", date: _d(5), label: "Salaire", amount: 2600, budget_line_id: null, notes: null },
    { id: "t4", date: _d(6), label: "Restaurant midi", amount: -24.5, budget_line_id: "l2", notes: null },
    { id: "t5", date: _d(8), label: "Essence", amount: -65, budget_line_id: "l3", notes: null },
    { id: "t6", date: _d(9), label: "Cinéma", amount: -28, budget_line_id: "l4", notes: null },
    { id: "t7", date: _d(11), label: "Courses Lidl", amount: -54.2, budget_line_id: "l1", notes: null },
    { id: "t8", date: _d(12), label: "Resto soir", amount: -61, budget_line_id: "l2", notes: null },
    { id: "t9", date: _d(14), label: "Pharmacie", amount: -18.9, budget_line_id: "l1", notes: null },
    { id: "t10", date: _d(15), label: "Abonnement transport", amount: -75, budget_line_id: "l3", notes: null },
  ],
  config: {
    monthly_income: 2600, budget_note: "Objectif : épargner 400€/mois",
    cash: 4200, savings_invested: 15000, savings_pending: 3000,
    savings_pending_date: "2026-09-01", minimum_reserve: 1500,
    one_time_events: [
      { date: "2026-08-15", label: "Vacances", amount: -1200 },
      { date: "2026-12-20", label: "Prime", amount: 1500 },
    ],
  },
  chat: [],
  seq: 100,
};

function lineName(id) { const l = demoState.lines.find((x) => x.id === id); return l ? l.name : null; }
function lineMeta(id) { return demoState.lines.find((x) => x.id === id) || {}; }

function computeStatsDemo(month) {
  const monthTotals = (mm) => {
    let income = 0, expenses = 0;
    for (const t of demoState.txs) {
      if (t.date.slice(0, 7) !== mm) continue;
      if (t.amount > 0) income += t.amount; else expenses += -t.amount;
    }
    return { income, expenses };
  };
  const { income, expenses } = monthTotals(month);
  const by_budget_line = demoState.lines.filter((l) => l.is_active).map((l) => {
    let spent = 0;
    for (const t of demoState.txs) {
      if (t.budget_line_id === l.id && t.amount < 0 && t.date.slice(0, 7) === month) spent += -t.amount;
    }
    const limit = l.monthly_limit;
    const remaining = limit - spent;
    const pct = limit > 0 ? Math.round((spent / limit) * 100) : (spent > 0 ? 100 : 0);
    return { id: l.id, name: l.name, color: l.color, emoji: l.emoji, limit, spent, remaining, pct };
  });
  const shift = (mm, d) => { const [y, m] = mm.split("-").map(Number); const dt = new Date(y, m - 1 + d, 1); return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}`; };
  const last_3_months = [shift(month, -2), shift(month, -1), month].map((mm) => ({ month: mm, ...monthTotals(mm) }));
  return { income, expenses, by_budget_line, last_3_months };
}

async function demo(method, path, body) {
  await new Promise((r) => setTimeout(r, 120)); // simulate latency
  const id = () => "x" + (++demoState.seq);

  if (path === "/api/budget-lines" && method === "GET")
    return demoState.lines.slice().sort((a, b) => a.sort_order - b.sort_order);
  if (path === "/api/budget-lines" && method === "POST") {
    const row = { id: id(), is_active: 1, sort_order: demoState.lines.length, color: "#3498db", emoji: null, ...body };
    demoState.lines.push(row); return row;
  }
  let m = path.match(/^\/api\/budget-lines\/(.+)$/);
  if (m) {
    const i = demoState.lines.findIndex((l) => l.id === m[1]);
    if (method === "PUT") { demoState.lines[i] = { ...demoState.lines[i], ...body }; return demoState.lines[i]; }
    if (method === "DELETE") {
      if (demoState.txs.some((t) => t.budget_line_id === m[1])) throw new Error("Cette ligne a des transactions. Désactive-la.");
      demoState.lines.splice(i, 1); return { ok: true };
    }
  }

  m = path.match(/^\/api\/transactions(?:\?month=(.+))?$/);
  if (m && method === "GET") {
    const month = m[1] || _ym;
    return demoState.txs
      .filter((t) => t.date.slice(0, 7) === month)
      .sort((a, b) => (b.date + b.id).localeCompare(a.date + a.id))
      .map((t) => ({ ...t, budget_name: lineName(t.budget_line_id), budget_color: lineMeta(t.budget_line_id).color, budget_emoji: lineMeta(t.budget_line_id).emoji }));
  }
  if (path === "/api/transactions" && method === "POST") {
    const row = { id: id(), notes: null, budget_line_id: null, ...body };
    demoState.txs.push(row); return row;
  }
  m = path.match(/^\/api\/transactions\/(.+)$/);
  if (m) {
    const i = demoState.txs.findIndex((t) => t.id === m[1]);
    if (method === "PUT") { demoState.txs[i] = { ...demoState.txs[i], ...body }; return demoState.txs[i]; }
    if (method === "DELETE") { if (i >= 0) demoState.txs.splice(i, 1); return { ok: true }; }
  }

  if (path === "/api/config" && method === "GET") return { ...demoState.config };
  if (path === "/api/config" && method === "PUT") { demoState.config = { ...demoState.config, ...body }; return { ...demoState.config }; }

  m = path.match(/^\/api\/stats\?month=(.+)$/);
  if (m) return computeStatsDemo(m[1]);

  if (path === "/api/chat" && method === "GET") return demoState.chat.slice();
  if (path === "/api/chat" && method === "POST") {
    demoState.chat.push({ id: id(), role: "user", content: body.message, created_at: new Date().toISOString() });
    const reply = "**Mode démo** — voici une réponse simulée.\n\nD'après tes totaux :\n- Dépenses du mois : maîtrisées sur la plupart des postes\n- Pense à garder ta réserve minimale\n\nEn production, je répondrais avec Claude à partir de tes chiffres réels.";
    demoState.chat.push({ id: id(), role: "assistant", content: reply, created_at: new Date().toISOString() });
    return { reply };
  }
  if (path === "/api/chat" && method === "DELETE") { demoState.chat = []; return { ok: true }; }

  throw new Error("demo: route non gérée " + method + " " + path);
}
