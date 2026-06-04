/**
 * reglages.js — settings: config, budget-line manager, import/export, danger zone.
 */
import { api } from "../api.js";
import { store } from "../store.js";
import { money, escHtml, toast, skeletonLines } from "../ui.js";

const PALETTE = ["#3498db", "#e74c3c", "#f39c12", "#27ae60", "#9b59b6", "#1F3864"];

export async function renderReglages(view) {
  view.innerHTML = `
    <button class="settings-back" id="back">‹ Retour</button>
    <div id="cfgCard" class="card">${skeletonLines(4)}</div>
    <div class="section-title">Postes de budget</div>
    <div id="blList"></div>
    <button class="btn btn-sm btn-ghost" id="addBl" style="width:100%">+ Ajouter un poste</button>
    <div class="section-title">Données</div>
    <div class="card">
      <button class="btn btn-sm btn-ghost" id="exportBtn" style="width:100%;margin-bottom:8px">⬇️ Exporter (JSON)</button>
      <button class="btn btn-sm btn-ghost" id="importBtn" style="width:100%">⬆️ Importer (JSON)</button>
      <input type="file" id="importFile" accept="application/json" hidden />
    </div>
    <div class="section-title">Zone de danger</div>
    <div class="card danger">
      <p style="margin:0 0 10px;font-size:14px">Supprime <b>toutes</b> les données (transactions, postes, config, chat).</p>
      <button class="btn btn-sm" id="wipeBtn" style="width:100%">Supprimer toutes les données</button>
    </div>
  `;
  view.querySelector("#back").onclick = () => window.appNavigate("accueil");

  await Promise.all([loadConfig(view), loadBudgetLines(view)]);

  view.querySelector("#addBl").onclick = () => editBudgetLine(view, null);
  view.querySelector("#exportBtn").onclick = () => exportData();
  view.querySelector("#importBtn").onclick = () => view.querySelector("#importFile").click();
  view.querySelector("#importFile").onchange = (e) => importData(view, e.target.files[0]);
  view.querySelector("#wipeBtn").onclick = () => wipeAll(view);
}

// ─── Config ─────────────────────────────────────────────────────────────────
async function loadConfig(view) {
  let cfg;
  try { cfg = await api.config.get(); } catch { cfg = {}; }
  const card = view.querySelector("#cfgCard");
  card.innerHTML = `
    <div class="field"><label>Revenu mensuel net</label><input id="cIncome" inputmode="decimal" value="${escHtml(cfg.monthly_income ?? 0)}" /></div>
    <div class="field"><label>Cash liquide</label><input id="cCash" inputmode="decimal" value="${escHtml(cfg.cash ?? 0)}" /></div>
    <div class="row-2">
      <div class="field"><label>Épargne investie</label><input id="cInv" inputmode="decimal" value="${escHtml(cfg.savings_invested ?? 0)}" /></div>
      <div class="field"><label>Réserve minimale</label><input id="cMin" inputmode="decimal" value="${escHtml(cfg.minimum_reserve ?? 0)}" /></div>
    </div>
    <div class="row-2">
      <div class="field"><label>Épargne en attente</label><input id="cPend" inputmode="decimal" value="${escHtml(cfg.savings_pending ?? 0)}" /></div>
      <div class="field"><label>Disponible le</label><input id="cPendDate" type="date" value="${escHtml(cfg.savings_pending_date || "")}" /></div>
    </div>
    <div class="field"><label>Note personnelle</label><textarea id="cNote" rows="2">${escHtml(cfg.budget_note || "")}</textarea></div>
    <div class="section-title" style="margin-left:0">Événements ponctuels</div>
    <div id="events"></div>
    <button class="link-btn" id="addEvent">+ Ajouter un événement</button>
    <div style="height:10px"></div>
    <button class="btn" id="saveCfg">Enregistrer</button>
  `;

  let events = Array.isArray(cfg.one_time_events) ? cfg.one_time_events.slice() : [];
  const evWrap = card.querySelector("#events");
  function paintEvents() {
    evWrap.innerHTML = events.map((e, i) => `
      <div class="event-row">
        <input type="date" data-i="${i}" data-k="date" value="${escHtml(e.date || "")}" />
        <input data-i="${i}" data-k="label" placeholder="Libellé" value="${escHtml(e.label || "")}" />
        <input data-i="${i}" data-k="amount" inputmode="decimal" placeholder="±€" value="${escHtml(e.amount ?? "")}" style="max-width:80px" />
        <button data-del="${i}">✕</button>
      </div>`).join("");
    evWrap.querySelectorAll("input").forEach((inp) => inp.oninput = () => {
      const i = +inp.dataset.i, k = inp.dataset.k;
      events[i][k] = k === "amount" ? parseFloat(inp.value.replace(",", ".")) || 0 : inp.value;
    });
    evWrap.querySelectorAll("[data-del]").forEach((b) => b.onclick = () => { events.splice(+b.dataset.del, 1); paintEvents(); });
  }
  paintEvents();
  card.querySelector("#addEvent").onclick = () => { events.push({ date: "", label: "", amount: 0 }); paintEvents(); };

  card.querySelector("#saveCfg").onclick = async () => {
    const num = (id) => parseFloat((card.querySelector(id).value || "0").replace(",", ".")) || 0;
    const payload = {
      monthly_income: num("#cIncome"), cash: num("#cCash"),
      savings_invested: num("#cInv"), minimum_reserve: num("#cMin"),
      savings_pending: num("#cPend"), savings_pending_date: card.querySelector("#cPendDate").value || "",
      budget_note: card.querySelector("#cNote").value.trim(),
      one_time_events: events.filter((e) => e.date || e.label || e.amount),
    };
    try { await api.config.put(payload); toast("Réglages enregistrés ✓", { type: "ok" }); window.refreshAppbar?.(); }
    catch (e) { toast(e.message || "Erreur", { type: "err" }); }
  };
}

// ─── Budget lines ─────────────────────────────────────────────────────────────
async function loadBudgetLines(view) {
  let lines;
  try { lines = await api.budgetLines.list(); } catch { lines = []; }
  store.budgetLines = lines;
  const wrap = view.querySelector("#blList");
  if (!lines.length) { wrap.innerHTML = `<div class="empty" style="padding:16px">Aucun poste</div>`; return; }

  wrap.innerHTML = lines.map((l, i) => `
    <div class="bl-item ${l.is_active ? "" : "inactive"}" data-id="${escHtml(l.id)}">
      <span class="bl-emoji">${escHtml(l.emoji || "📦")}</span>
      <div class="bl-main">
        <div class="bl-name">${escHtml(l.name)}</div>
        <div class="bl-sub">${money(l.monthly_limit, true)}/mois ${l.is_active ? "" : "· inactif"}</div>
      </div>
      <span class="bl-swatch" style="background:${escHtml(l.color)}"></span>
      <button class="icon-btn" data-up="${i}" ${i === 0 ? "disabled style=opacity:.3" : ""}>↑</button>
      <button class="icon-btn" data-down="${i}" ${i === lines.length - 1 ? "disabled style=opacity:.3" : ""}>↓</button>
      <button class="icon-btn" data-edit="${escHtml(l.id)}">✏️</button>
    </div>`).join("");

  wrap.querySelectorAll("[data-edit]").forEach((b) => b.onclick = () => editBudgetLine(view, lines.find((l) => l.id === b.dataset.edit)));
  wrap.querySelectorAll("[data-up]").forEach((b) => b.onclick = () => reorder(view, lines, +b.dataset.up, -1));
  wrap.querySelectorAll("[data-down]").forEach((b) => b.onclick = () => reorder(view, lines, +b.dataset.down, 1));
}

async function reorder(view, lines, i, dir) {
  const j = i + dir;
  if (j < 0 || j >= lines.length) return;
  const a = lines[i], b = lines[j];
  try {
    await Promise.all([
      api.budgetLines.update(a.id, { sort_order: j }),
      api.budgetLines.update(b.id, { sort_order: i }),
    ]);
    loadBudgetLines(view);
  } catch { toast("Échec du réordonnancement", { type: "err" }); }
}

function editBudgetLine(view, line) {
  const sheet = document.getElementById("txSheet");
  const backdrop = document.getElementById("sheetBackdrop");
  const isNew = !line;
  const l = line || { name: "", monthly_limit: "", color: PALETTE[0], emoji: "", is_active: 1 };

  sheet.hidden = false; backdrop.hidden = false; backdrop.onclick = close;
  sheet.innerHTML = `
    <div class="sheet-grip"></div>
    <h2>${isNew ? "Nouveau poste" : "Modifier le poste"}</h2>
    <div class="field"><label>Nom</label><input id="blName" value="${escHtml(l.name)}" placeholder="Ex : Restaurants" /></div>
    <div class="row-2">
      <div class="field"><label>Emoji</label><input id="blEmoji" value="${escHtml(l.emoji || "")}" placeholder="🍽️" maxlength="2" /></div>
      <div class="field"><label>Budget mensuel</label><input id="blLimit" inputmode="decimal" value="${escHtml(l.monthly_limit)}" /></div>
    </div>
    <div class="field"><label>Couleur</label>
      <div style="display:flex;gap:10px" id="palette">
        ${PALETTE.map((c) => `<button data-c="${c}" style="width:34px;height:34px;border-radius:999px;border:${c === l.color ? "3px solid var(--text)" : "1px solid var(--border)"};background:${c}"></button>`).join("")}
      </div>
    </div>
    <div class="field"><label><input type="checkbox" id="blActive" ${l.is_active ? "checked" : ""} /> Actif</label></div>
    <button class="btn" id="blSave">Enregistrer</button>
    <div style="height:8px"></div>
    ${!isNew ? `<button class="btn btn-ghost" id="blDelete" style="color:var(--red)">Supprimer</button><div style="height:8px"></div>` : ""}
    <button class="btn btn-ghost" id="blCancel">Annuler</button>
  `;
  let color = l.color;
  sheet.querySelectorAll("#palette button").forEach((b) => b.onclick = () => {
    color = b.dataset.c;
    sheet.querySelectorAll("#palette button").forEach((x) => x.style.border = x.dataset.c === color ? "3px solid var(--text)" : "1px solid var(--border)");
  });
  sheet.querySelector("#blCancel").onclick = close;
  sheet.querySelector("#blSave").onclick = async () => {
    const payload = {
      name: sheet.querySelector("#blName").value.trim(),
      monthly_limit: parseFloat((sheet.querySelector("#blLimit").value || "0").replace(",", ".")) || 0,
      emoji: sheet.querySelector("#blEmoji").value.trim() || null,
      color,
      is_active: sheet.querySelector("#blActive").checked ? 1 : 0,
    };
    if (!payload.name) { toast("Nom requis", { type: "err" }); return; }
    try {
      if (isNew) await api.budgetLines.create(payload);
      else await api.budgetLines.update(l.id, payload);
      close(); toast("Enregistré ✓", { type: "ok" }); loadBudgetLines(view);
    } catch (e) { toast(e.message || "Erreur", { type: "err" }); }
  };
  if (!isNew) sheet.querySelector("#blDelete").onclick = async () => {
    if (!confirm(`Supprimer « ${l.name} » ?`)) return;
    try { await api.budgetLines.remove(l.id); close(); toast("Supprimé", { type: "ok" }); loadBudgetLines(view); }
    catch (e) { toast(e.message || "Impossible de supprimer", { type: "err" }); }
  };

  function close() { sheet.hidden = true; backdrop.hidden = true; }
}

// ─── Export / Import ──────────────────────────────────────────────────────────
async function exportData() {
  toast("Préparation de l'export…");
  const [config, budget_lines] = await Promise.all([api.config.get(), api.budgetLines.list()]);
  // Gather transactions across a 36-month window.
  const now = new Date();
  const months = [];
  for (let i = -35; i <= 0; i++) { const d = new Date(now.getFullYear(), now.getMonth() + i, 1); months.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`); }
  const txArrays = await Promise.all(months.map((m) => api.transactions.list(m).catch(() => [])));
  const transactions = txArrays.flat();

  const blob = new Blob([JSON.stringify({ exported_at: new Date().toISOString(), config, budget_lines, transactions }, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `finances-export-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

async function importData(view, file) {
  if (!file) return;
  let data;
  try { data = JSON.parse(await file.text()); } catch { toast("Fichier JSON invalide", { type: "err" }); return; }
  const nLines = (data.budget_lines || []).length, nTx = (data.transactions || []).length;
  if (!confirm(`Importer ${nLines} postes et ${nTx} transactions ? (ajouté aux données existantes)`)) return;

  try {
    // Create budget lines, mapping old id → new id
    const idMap = {};
    for (const l of data.budget_lines || []) {
      const created = await api.budgetLines.create({ name: l.name, monthly_limit: l.monthly_limit, color: l.color, emoji: l.emoji, is_active: l.is_active, sort_order: l.sort_order });
      idMap[l.id] = created.id;
    }
    for (const t of data.transactions || []) {
      await api.transactions.create({ date: t.date, label: t.label, amount: t.amount, budget_line_id: idMap[t.budget_line_id] || null, notes: t.notes });
    }
    if (data.config) await api.config.put(data.config);
    toast("Import terminé ✓", { type: "ok" });
    renderReglages(view);
    window.refreshAppbar?.();
  } catch (e) { toast("Échec de l'import : " + (e.message || ""), { type: "err" }); }
}

// ─── Wipe ───────────────────────────────────────────────────────────────────
async function wipeAll(view) {
  const word = prompt('Tape "SUPPRIMER" pour tout effacer définitivement :');
  if (word !== "SUPPRIMER") { if (word !== null) toast("Annulé", {}); return; }
  try {
    // delete transactions across a wide window
    const now = new Date();
    for (let i = -47; i <= 0; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
      const m = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
      const txs = await api.transactions.list(m).catch(() => []);
      for (const t of txs) await api.transactions.remove(t.id);
    }
    const lines = await api.budgetLines.list();
    for (const l of lines) await api.budgetLines.remove(l.id).catch(() => {});
    await api.config.put({});
    await api.chat.clear().catch(() => {});
    toast("Toutes les données ont été supprimées", { type: "ok" });
    window.refreshAppbar?.();
    renderReglages(view);
  } catch (e) { toast("Échec : " + (e.message || ""), { type: "err" }); }
}
