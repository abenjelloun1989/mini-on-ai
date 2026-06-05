/**
 * add-tx.js — the Add/Edit Transaction bottom sheet (3 steps, no navigation).
 */
import { api } from "../api.js";
import { store } from "../store.js";
import { money, statusColor, escHtml, toast, fmtDate } from "../ui.js";

const sheet = document.getElementById("txSheet");
const backdrop = document.getElementById("sheetBackdrop");

let st = null; // working state

/** Today's date as YYYY-MM-DD in the user's local timezone (not UTC). */
function localDate() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** Open the sheet. Pass an existing tx object to edit. */
export function openTxSheet(tx = null) {
  st = {
    editing: tx ? tx.id : null,
    amount: tx ? Math.abs(tx.amount).toString() : "",
    type: tx ? (tx.amount >= 0 ? "income" : "expense") : "expense",
    categoryId: tx ? tx.budget_line_id : store.getLastCategory(),
    label: tx ? tx.label : "",
    date: tx ? tx.date : localDate(),
    notes: tx ? tx.notes || "" : "",
    notesOpen: !!(tx && tx.notes),
    step: tx ? 3 : 1,
  };
  backdrop.hidden = false;
  sheet.hidden = false;
  sheet.setAttribute("aria-hidden", "false");
  backdrop.onclick = closeTxSheet;
  render();
}

export function closeTxSheet() {
  sheet.hidden = true;
  backdrop.hidden = true;
  sheet.setAttribute("aria-hidden", "true");
  st = null;
}

function dots() {
  return `<div class="steps-dots">${[1, 2, 3].map((i) => `<span class="${i <= st.step ? "on" : ""}"></span>`).join("")}</div>`;
}

function render() {
  if (st.step === 1) return renderAmount();
  if (st.step === 2) return renderCategory();
  return renderConfirm();
}

// ─── Step 1: amount ───────────────────────────────────────────────────────────
function renderAmount() {
  sheet.innerHTML = `
    <div class="sheet-grip"></div>
    <h2>${st.editing ? "Modifier" : "Nouvelle transaction"}</h2>
    ${dots()}
    <div class="amount-display ${st.type}" id="amtDisplay">${displayAmount()}</div>
    <input class="amount-input" id="amtInput" inputmode="decimal" placeholder="0,00"
           value="${escHtml(st.amount)}" autocomplete="off" />
    <div class="toggle-row">
      <button id="tExpense" class="${st.type === "expense" ? "on-expense" : ""}">DÉPENSE</button>
      <button id="tIncome" class="${st.type === "income" ? "on-income" : ""}">REVENU</button>
    </div>
    <div style="height:14px"></div>
    <button class="btn" id="nextBtn">Continuer</button>
    <div style="height:8px"></div>
    <button class="btn btn-ghost" id="cancelBtn">Annuler</button>
  `;
  const input = sheet.querySelector("#amtInput");
  const disp = sheet.querySelector("#amtDisplay");
  input.focus();
  input.addEventListener("input", () => {
    st.amount = input.value.replace(",", ".").replace(/[^0-9.]/g, "");
    disp.textContent = displayAmount();
  });
  sheet.querySelector("#tExpense").onclick = () => { st.type = "expense"; render(); setTimeout(() => sheet.querySelector("#amtInput").focus(), 0); };
  sheet.querySelector("#tIncome").onclick = () => { st.type = "income"; render(); setTimeout(() => sheet.querySelector("#amtInput").focus(), 0); };
  sheet.querySelector("#cancelBtn").onclick = closeTxSheet;
  sheet.querySelector("#nextBtn").onclick = () => {
    if (!validAmount()) { toast("Saisis un montant", { type: "err" }); return; }
    st.step = 2; render();
  };
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") sheet.querySelector("#nextBtn").click(); });
}

function displayAmount() {
  const n = parseFloat(st.amount);
  const v = Number.isFinite(n) ? n : 0;
  return (st.type === "expense" ? "-" : "+") + money(v);
}
function validAmount() {
  const n = parseFloat(st.amount);
  return Number.isFinite(n) && n > 0;
}

// ─── Step 2: category ─────────────────────────────────────────────────────────
async function renderCategory() {
  sheet.innerHTML = `
    <div class="sheet-grip"></div>
    <h2>Catégorie</h2>
    ${dots()}
    <div class="cat-grid" id="catGrid"></div>
    <div style="height:14px"></div>
    <button class="btn btn-ghost" id="backBtn">Retour</button>
  `;
  sheet.querySelector("#backBtn").onclick = () => { st.step = 1; render(); };

  let stats;
  try { stats = await api.stats(store.month); } catch { stats = { by_budget_line: [] }; }
  const grid = sheet.querySelector("#catGrid");

  const cards = stats.by_budget_line.map((l) => `
    <button class="cat-card ${st.categoryId === l.id ? "selected" : ""}" data-id="${escHtml(l.id)}">
      <div class="cat-emoji">${escHtml(l.emoji || "📦")}</div>
      <div class="cat-name">${escHtml(l.name)}</div>
      <div class="cat-rem">${money(l.remaining, true)} restant</div>
      <div class="cat-bar" style="width:${Math.min(l.pct, 100)}%;background:${statusColor(l.pct)}"></div>
    </button>
  `).join("");
  const none = `
    <button class="cat-card ${!st.categoryId ? "selected" : ""}" data-id="">
      <div class="cat-emoji">🏷️</div>
      <div class="cat-name">Sans catégorie</div>
      <div class="cat-rem">&nbsp;</div>
    </button>`;
  grid.innerHTML = cards + none;

  grid.querySelectorAll(".cat-card").forEach((c) => {
    c.onclick = () => {
      st.categoryId = c.dataset.id || null;
      const meta = stats.by_budget_line.find((l) => l.id === st.categoryId);
      if (!st.label) st.label = meta ? meta.name : "";
      st.step = 3; render();
    };
  });
}

// ─── Step 3: label + confirm ──────────────────────────────────────────────────
function renderConfirm() {
  sheet.innerHTML = `
    <div class="sheet-grip"></div>
    <h2>${st.type === "expense" ? "Dépense" : "Revenu"} · ${displayAmount()}</h2>
    ${dots()}
    <div class="field">
      <label>Libellé</label>
      <input id="fLabel" value="${escHtml(st.label)}" placeholder="Ex : Courses" />
    </div>
    <div class="field">
      <label>Date</label>
      <input id="fDate" type="date" value="${escHtml(st.date)}" />
    </div>
    <button class="notes-toggle" id="notesToggle">${st.notesOpen ? "− Masquer la note" : "+ Ajouter une note"}</button>
    <div class="field" id="notesField" ${st.notesOpen ? "" : "hidden"}>
      <textarea id="fNotes" rows="2" placeholder="Note (optionnel)">${escHtml(st.notes)}</textarea>
    </div>
    <div style="height:8px"></div>
    <button class="btn ${st.type === "expense" ? "btn-red" : "btn-green"}" id="saveBtn">Enregistrer</button>
    <div style="height:8px"></div>
    <button class="btn btn-ghost" id="backBtn2">Retour</button>
  `;
  sheet.querySelector("#backBtn2").onclick = () => { st.step = 2; render(); };
  sheet.querySelector("#notesToggle").onclick = () => {
    st.notes = sheet.querySelector("#fNotes").value;
    st.notesOpen = !st.notesOpen; render();
  };
  sheet.querySelector("#saveBtn").onclick = save;
}

async function save() {
  st.label = sheet.querySelector("#fLabel").value.trim() || "Sans libellé";
  st.date = sheet.querySelector("#fDate").value || localDate();
  const notesEl = sheet.querySelector("#fNotes");
  if (notesEl) st.notes = notesEl.value.trim();

  const n = parseFloat(st.amount);
  const amount = st.type === "expense" ? -Math.abs(n) : Math.abs(n);
  const payload = {
    amount, date: st.date, label: st.label,
    budget_line_id: st.categoryId || null,
    notes: st.notes || null,
  };

  const btn = sheet.querySelector("#saveBtn");
  btn.disabled = true; btn.textContent = "…";
  try {
    const wasEditing = st.editing; // capture before closeTxSheet() nulls st
    if (wasEditing) await api.transactions.update(wasEditing, payload);
    else await api.transactions.create(payload);
    store.setLastCategory(st.categoryId);
    closeTxSheet(); // st = null from here on
    toast(wasEditing ? "Modifié ✓" : "Enregistré ✓", { type: "ok" });
    if (window.refreshAppbar) window.refreshAppbar();
    if (window.appReload) window.appReload();
  } catch (e) {
    btn.disabled = false; btn.textContent = "Enregistrer";
    toast(e.message || "Erreur", { type: "err" });
  }
}
