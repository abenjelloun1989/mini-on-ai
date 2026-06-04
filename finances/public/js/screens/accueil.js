/**
 * accueil.js — home dashboard: month totals, progress, budget-line pills.
 */
import { api } from "../api.js";
import { store } from "../store.js";
import { money, statusColor, balanceStatus, escHtml, skeletonLines } from "../ui.js";

export async function renderAccueil(view) {
  view.innerHTML = `
    <div class="card">
      <div class="bignum-row">
        <div class="bignum"><div class="lbl">Dépensé ce mois</div><div class="val" id="accSpent">—</div></div>
        <div class="bignum" style="text-align:right"><div class="lbl">Budget total</div><div class="val" id="accBudget">—</div></div>
      </div>
      <div class="progress"><span id="accBar" style="width:0%"></span></div>
      <div id="accBalance" style="margin-top:12px;font-weight:700"></div>
    </div>
    <div class="section-title">Mes postes</div>
    <div class="pills" id="accPills">${skeletonLines(1)}</div>
  `;

  let stats;
  try {
    stats = await api.stats(store.month);
  } catch {
    view.querySelector("#accSpent").textContent = "—";
    return;
  }

  const totalSpent = stats.expenses;
  const totalBudget = stats.by_budget_line.reduce((s, l) => s + l.limit, 0);
  const pct = totalBudget > 0 ? Math.round((totalSpent / totalBudget) * 100) : 0;
  const balance = stats.income - stats.expenses;
  const bs = balanceStatus(balance);

  view.querySelector("#accSpent").textContent = money(totalSpent);
  view.querySelector("#accBudget").textContent = money(totalBudget);
  const bar = view.querySelector("#accBar");
  bar.style.width = Math.min(pct, 100) + "%";
  bar.style.background = statusColor(pct);
  view.querySelector("#accBalance").innerHTML =
    `${bs.emoji} Balance du mois : <span style="color:${bs.color}">${money(balance)}</span>`;

  const pills = view.querySelector("#accPills");
  if (!stats.by_budget_line.length) {
    pills.innerHTML = `<div class="empty" style="padding:20px">Aucun poste. Ajoute-en dans ⚙️ Réglages.</div>`;
    return;
  }
  pills.innerHTML = stats.by_budget_line.map((l) => `
    <button class="pill" data-id="${escHtml(l.id)}">
      <div class="pill-name">${escHtml(l.emoji || "")} ${escHtml(l.name)}</div>
      <div class="pill-rem" style="color:${statusColor(l.pct)}">${money(l.remaining, true)}</div>
      <div class="pill-fill" style="width:${Math.min(l.pct, 100)}%;background:${statusColor(l.pct)}"></div>
    </button>
  `).join("");

  pills.querySelectorAll(".pill").forEach((p) => {
    p.addEventListener("click", () => {
      window.appNavigate("historique", { budgetLineId: p.dataset.id });
    });
  });
}
