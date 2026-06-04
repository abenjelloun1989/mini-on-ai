/**
 * index.js — Cloudflare Worker entry. CORS + Cloudflare Access auth on every
 * request, then path/method dispatch to the API handlers.
 */
import { corsJson, corsOk } from "./lib.js";
import { requireAccess } from "./auth.js";
import { listBudgetLines, createBudgetLine, updateBudgetLine, deleteBudgetLine } from "./budget-lines.js";
import { listTransactions, createTransaction, updateTransaction, deleteTransaction } from "./transactions.js";
import { getConfig, putConfig } from "./config.js";
import { getStats } from "./stats.js";
import { getChat, postChat, clearChat } from "./chat.js";

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return corsOk(env);

    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    if (!path.startsWith("/api/")) {
      return corsJson(env, { error: "Not found" }, 404);
    }

    // Auth gate — every API route requires a valid Cloudflare Access JWT.
    const auth = await requireAccess(request, env);
    if (!auth.ok) return corsJson(env, { error: auth.error }, auth.status);

    try {
      // /api/budget-lines  (+ /:id)
      const blMatch = path.match(/^\/api\/budget-lines(?:\/([^/]+))?$/);
      if (blMatch) {
        const id = blMatch[1];
        if (!id && method === "GET") return listBudgetLines(request, env);
        if (!id && method === "POST") return createBudgetLine(request, env);
        if (id && method === "PUT") return updateBudgetLine(request, env, id);
        if (id && method === "DELETE") return deleteBudgetLine(request, env, id);
        return corsJson(env, { error: "Method not allowed" }, 405);
      }

      // /api/transactions  (+ /:id)
      const txMatch = path.match(/^\/api\/transactions(?:\/([^/]+))?$/);
      if (txMatch) {
        const id = txMatch[1];
        if (!id && method === "GET") return listTransactions(request, env);
        if (!id && method === "POST") return createTransaction(request, env);
        if (id && method === "PUT") return updateTransaction(request, env, id);
        if (id && method === "DELETE") return deleteTransaction(request, env, id);
        return corsJson(env, { error: "Method not allowed" }, 405);
      }

      // /api/config
      if (path === "/api/config") {
        if (method === "GET") return getConfig(request, env);
        if (method === "PUT") return putConfig(request, env);
        return corsJson(env, { error: "Method not allowed" }, 405);
      }

      // /api/stats
      if (path === "/api/stats") {
        if (method === "GET") return getStats(request, env);
        return corsJson(env, { error: "Method not allowed" }, 405);
      }

      // /api/chat
      if (path === "/api/chat") {
        if (method === "GET") return getChat(request, env);
        if (method === "POST") return postChat(request, env);
        if (method === "DELETE") return clearChat(request, env);
        return corsJson(env, { error: "Method not allowed" }, 405);
      }

      return corsJson(env, { error: "Not found" }, 404);
    } catch (e) {
      console.error("Unhandled error:", e);
      return corsJson(env, { error: "Erreur serveur." }, 500);
    }
  },
};
