/**
 * chat.js — AI financial assistant. Receives ONLY aggregated figures, never
 * individual transactions.
 */
import { corsJson, parseJson, str, currentMonth } from "./lib.js";
import { computeStats } from "./stats.js";
import { readConfig } from "./config.js";

const MODEL = "claude-opus-4-8";
const HISTORY_FOR_CONTEXT = 20;
const HISTORY_FOR_LIST = 50;

function eur(n) {
  return `${Math.round((n + Number.EPSILON) * 100) / 100}€`;
}

function buildSystemPrompt(month, stats, config) {
  const balance = stats.income - stats.expenses;
  const availableNow = (config.cash || 0) - (config.minimum_reserve || 0);
  const availableAfter = (config.cash || 0) + (config.savings_pending || 0) - (config.minimum_reserve || 0);

  const lines = stats.by_budget_line
    .map((l) => `${l.emoji || "•"} ${l.name} | ${eur(l.spent)} / ${eur(l.limit)} | ${l.pct}%`)
    .join("\n") || "(aucune ligne de budget)";

  const trend = stats.last_3_months
    .map((m) => `${m.month} : revenus ${eur(m.income)}, dépenses ${eur(m.expenses)}`)
    .join("\n");

  return `Tu es un assistant financier personnel. Tu réponds en français, de façon
concise et bienveillante. Tu n'as accès qu'à des données agrégées
(totaux par catégorie, soldes) — jamais aux transactions individuelles.
Si une question nécessite une transaction précise, oriente l'utilisateur
vers l'onglet Historique.

CONTEXTE FINANCIER (mis à jour à chaque message)
Mois : ${month}
Revenus : ${eur(stats.income)} | Dépenses : ${eur(stats.expenses)} | Balance : ${eur(balance)}

LIGNES DE BUDGET
${lines}

RÉSERVES
Cash : ${eur(config.cash || 0)}
Épargne en attente : ${eur(config.savings_pending || 0)} (dispo le ${config.savings_pending_date || "—"})
Épargne investie : ${eur(config.savings_invested || 0)}
Dispo maintenant : ${eur(availableNow)}
Dispo après échéance : ${eur(availableAfter)}

TENDANCE (3 derniers mois — totaux uniquement)
${trend}

Réponds en moins de 150 mots sauf si vraiment nécessaire.`;
}

export async function getChat(request, env) {
  const { results } = await env.DB.prepare(
    `SELECT id, role, content, created_at FROM chat_messages
     ORDER BY created_at DESC, rowid DESC LIMIT ?`
  ).bind(HISTORY_FOR_LIST).all();
  return corsJson(env, (results || []).reverse());
}

export async function clearChat(request, env) {
  await env.DB.prepare("DELETE FROM chat_messages").run();
  return corsJson(env, { ok: true });
}

export async function postChat(request, env) {
  const body = await parseJson(request);
  if (!body) return corsJson(env, { error: "Invalid JSON" }, 400);
  const message = str(body.message, 4000);
  if (!message) return corsJson(env, { error: "Message vide" }, 400);

  if (!env.ANTHROPIC_API_KEY) {
    return corsJson(env, { error: "Assistant non configuré (clé API manquante)." }, 503);
  }

  const month = currentMonth();
  const [stats, config, history] = await Promise.all([
    computeStats(env, month),
    readConfig(env),
    env.DB.prepare(
      `SELECT role, content FROM chat_messages
       ORDER BY created_at DESC, rowid DESC LIMIT ?`
    ).bind(HISTORY_FOR_CONTEXT).all(),
  ]);

  const priorMessages = (history.results || [])
    .reverse()
    .map((m) => ({ role: m.role, content: m.content }));

  const systemPrompt = buildSystemPrompt(month, stats, config);

  let reply;
  try {
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 700,
        system: systemPrompt,
        messages: [...priorMessages, { role: "user", content: message }],
      }),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      console.error("Anthropic error:", resp.status, errText);
      return corsJson(env, { error: "L'assistant est temporairement indisponible." }, 502);
    }

    const data = await resp.json();
    reply = data?.content?.[0]?.text?.trim();
    if (!reply) return corsJson(env, { error: "Réponse vide de l'assistant." }, 502);
  } catch (e) {
    console.error("Chat fetch failed:", e);
    return corsJson(env, { error: "Erreur réseau avec l'assistant." }, 502);
  }

  // Persist both messages (best-effort; don't fail the response if this errors)
  try {
    await env.DB.batch([
      env.DB.prepare("INSERT INTO chat_messages (role, content) VALUES ('user', ?)").bind(message),
      env.DB.prepare("INSERT INTO chat_messages (role, content) VALUES ('assistant', ?)").bind(reply),
    ]);
  } catch (e) {
    console.error("Failed to persist chat:", e);
  }

  return corsJson(env, { reply });
}
