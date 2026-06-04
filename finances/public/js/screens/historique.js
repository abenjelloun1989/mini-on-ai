/**
 * historique.js — month transaction list, grouped by day, swipe-to-delete + undo.
 */
import { api } from "../api.js";
import { store, shiftMonth } from "../store.js";
import { money, fmtDate, fmtMonthLabel, escHtml, toast, skeletonLines } from "../ui.js";
import { openTxSheet } from "./add-tx.js";

let filterLineId = null;
let searchOpen = false;
let searchTerm = "";

export async function renderHistorique(view, opts = {}) {
  if (opts.budgetLineId !== undefined) filterLineId = opts.budgetLineId || null;

  view.innerHTML = `
    <div class="month-nav">
      <button id="mPrev">‹</button>
      <span class="m-label" id="mLabel">${fmtMonthLabel(store.month)}</span>
      <button id="mNext">›</button>
    </div>
    ${filterLineId ? `<button class="link-btn" id="clearFilter">✕ Filtre actif — tout afficher</button>` : ""}
    <button class="link-btn" id="toggleSearch">${searchOpen ? "Masquer la recherche" : "🔍 Rechercher"}</button>
    <input class="search-bar" id="searchBar" placeholder="Rechercher…" ${searchOpen ? "" : "hidden"} value="${escHtml(searchTerm)}" />
    <div id="txList">${skeletonLines(4)}</div>
    <div class="month-total" id="monthTotal"></div>
  `;

  view.querySelector("#mPrev").onclick = () => { store.month = shiftMonth(store.month, -1); window.refreshAppbar?.(); renderHistorique(view); };
  view.querySelector("#mNext").onclick = () => { store.month = shiftMonth(store.month, 1); window.refreshAppbar?.(); renderHistorique(view); };
  view.querySelector("#clearFilter") && (view.querySelector("#clearFilter").onclick = () => { filterLineId = null; renderHistorique(view); });
  view.querySelector("#toggleSearch").onclick = () => { searchOpen = !searchOpen; if (!searchOpen) searchTerm = ""; renderHistorique(view); };
  const sb = view.querySelector("#searchBar");
  if (searchOpen) { sb.focus(); sb.oninput = () => { searchTerm = sb.value; paint(); }; }

  let txs = [];
  try { txs = await api.transactions.list(store.month); } catch { txs = []; }

  function paint() {
    let list = txs.slice();
    if (filterLineId) list = list.filter((t) => t.budget_line_id === filterLineId);
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      list = list.filter((t) => (t.label || "").toLowerCase().includes(q) || (t.budget_name || "").toLowerCase().includes(q));
    }

    const listEl = view.querySelector("#txList");
    if (!list.length) {
      listEl.innerHTML = `<div class="empty"><div class="emo">🧾</div>Aucune transaction</div>`;
      view.querySelector("#monthTotal").textContent = "";
      return;
    }

    // group by day
    const groups = {};
    for (const t of list) (groups[t.date] = groups[t.date] || []).push(t);
    const days = Object.keys(groups).sort((a, b) => b.localeCompare(a));

    listEl.innerHTML = days.map((day) => `
      <div class="day-group">
        <div class="day-head">${escHtml(fmtDate(day))}</div>
        ${groups[day].map(rowHtml).join("")}
      </div>
    `).join("");

    const total = list.reduce((s, t) => s + t.amount, 0);
    view.querySelector("#monthTotal").innerHTML = `Total : <span style="color:${total < 0 ? "var(--red)" : "var(--green)"}">${money(total)}</span>`;

    listEl.querySelectorAll(".tx-row").forEach((row) => wireRow(row, txs.find((t) => t.id === row.dataset.id)));
  }
  paint();
}

function rowHtml(t) {
  const color = t.budget_color || "var(--subtle)";
  const cat = t.budget_name ? `${t.budget_emoji || ""} ${t.budget_name}` : "Sans catégorie";
  const cls = t.amount < 0 ? "neg" : "pos";
  return `
    <div class="tx-row" data-id="${escHtml(t.id)}">
      <span class="dot" style="background:${escHtml(color)}"></span>
      <div class="tx-main">
        <div class="tx-label">${escHtml(t.label)}</div>
        <div class="tx-cat">${escHtml(cat)}</div>
      </div>
      <span class="tx-amt ${cls}">${money(t.amount)}</span>
      <button class="tx-delete" data-del="${escHtml(t.id)}">Suppr.</button>
    </div>`;
}

function wireRow(row, tx) {
  if (!tx) return;
  let startX = 0, dx = 0, swiping = false;

  row.addEventListener("touchstart", (e) => { startX = e.touches[0].clientX; swiping = true; }, { passive: true });
  row.addEventListener("touchmove", (e) => {
    if (!swiping) return;
    dx = e.touches[0].clientX - startX;
  }, { passive: true });
  row.addEventListener("touchend", () => {
    if (dx < -40) row.classList.add("swiped");
    else if (dx > 20) row.classList.remove("swiped");
    swiping = false; dx = 0;
  });

  // tap row body → edit (ignore when swiped open)
  row.querySelector(".tx-main").addEventListener("click", () => {
    if (row.classList.contains("swiped")) { row.classList.remove("swiped"); return; }
    openTxSheet(tx);
  });
  row.querySelector(".tx-amt").addEventListener("click", () => {
    if (row.classList.contains("swiped")) { row.classList.remove("swiped"); return; }
    openTxSheet(tx);
  });
  row.querySelector(".tx-delete").addEventListener("click", () => deleteWithUndo(tx, row));
}

async function deleteWithUndo(tx, row) {
  row.style.display = "none"; // optimistic hide
  let undone = false;
  const dismiss = toast("Transaction supprimée", {
    duration: 5000,
    action: { label: "Annuler", onClick: () => { undone = true; row.style.display = ""; row.classList.remove("swiped"); } },
  });
  setTimeout(async () => {
    if (undone) return;
    try {
      await api.transactions.remove(tx.id);
      window.refreshAppbar?.();
    } catch {
      row.style.display = ""; toast("Échec de la suppression", { type: "err" });
    }
  }, 5000);
}
