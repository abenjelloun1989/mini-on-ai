/**
 * reserves.js — wealth snapshot, "Puis-je me le permettre ?" tool, 12-month projection.
 */
import { api } from "../api.js";
import { store } from "../store.js";
import { money, fmtMonthLabel, escHtml, toast, skeletonLines } from "../ui.js";

let projChart = null;
let projOpen = false;

function tickColor() { return getComputedStyle(document.body).color; }
function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }

export async function renderReserves(view) {
  if (projChart) { projChart.destroy(); projChart = null; }
  view.innerHTML = `<div class="card">${skeletonLines(3)}</div>`;

  let config, lines;
  try {
    [config, lines] = await Promise.all([api.config.get(), api.budgetLines.list()]);
  } catch { view.innerHTML = `<div class="empty">Impossible de charger les réserves</div>`; return; }

  const availableNow = (config.cash || 0) - (config.minimum_reserve || 0);
  const availableAfter = availableNow + (config.savings_pending || 0);
  const pendDate = config.savings_pending_date;

  view.innerHTML = `
    <div class="section-title">Patrimoine</div>
    <div class="wealth-grid">
      <div class="wealth-card"><div class="wc-lbl">💵 Cash liquide (maintenant)</div><div class="wc-val">${money(config.cash || 0)}</div></div>
      <div class="wealth-card"><div class="wc-lbl">📈 Épargne en attente${pendDate ? ` (dispo le ${escHtml(pendDate)})` : ""}</div><div class="wc-val">${money(config.savings_pending || 0)}</div></div>
      <div class="wealth-card"><div class="wc-lbl">🔒 Épargne investie (ne pas casser)</div><div class="wc-val">${money(config.savings_invested || 0)}</div></div>
    </div>

    <div class="section-title">Puis-je me le permettre ?</div>
    <div class="card">
      <div class="field" style="margin-bottom:8px">
        <input id="affAmt" inputmode="decimal" placeholder="Montant de l'achat" autocomplete="off" />
      </div>
      <div id="affResult"></div>
      <div id="affImpact" class="afford-impact"></div>
      <div style="height:10px"></div>
      <button class="btn btn-sm btn-ghost" id="affSave" hidden>Enregistrer cette décision</button>
    </div>

    <div class="card">
      <div class="collapse-head" id="projHead">
        <span>📅 Projection sur 12 mois</span><span id="projCaret">${projOpen ? "▾" : "▸"}</span>
      </div>
      <div id="projBody" ${projOpen ? "" : "hidden"}>
        <div class="chart-wrap"><canvas id="proj"></canvas></div>
        <div style="overflow-x:auto"><table class="proj-table" id="projTable"></table></div>
      </div>
    </div>
  `;

  // ── Affordability tool (live) ──
  const amtEl = view.querySelector("#affAmt");
  const resEl = view.querySelector("#affResult");
  const impEl = view.querySelector("#affImpact");
  const saveBtn = view.querySelector("#affSave");
  let lastEval = null;

  function evalAff() {
    const x = parseFloat((amtEl.value || "").replace(",", "."));
    if (!Number.isFinite(x) || x <= 0) { resEl.innerHTML = ""; impEl.textContent = ""; saveBtn.hidden = true; return; }
    let verdict, cls, after = availableNow - x;
    if (x <= availableNow) {
      cls = "afford-ok"; verdict = `✅ Oui — ${money(availableNow - x, true)} de marge disponible maintenant`;
    } else if (x <= availableAfter) {
      cls = "afford-warn"; verdict = `⚠️ Attends${pendDate ? ` le ${escHtml(pendDate)}` : " l'échéance"} — ${money(availableAfter - x, true)} disponible après`;
    } else {
      cls = "afford-no"; verdict = `❌ Dépasse ta réserve même après l'échéance`;
    }
    resEl.innerHTML = `<div class="afford-result ${cls}">${verdict}</div>`;
    impEl.textContent = `Ton dispo passerait de ${money(availableNow, true)} à ${money(after, true)}`;
    saveBtn.hidden = false;
    lastEval = { amount: x, verdict, available_before: availableNow, available_after: after };
  }
  amtEl.addEventListener("input", evalAff);
  saveBtn.onclick = () => { if (lastEval) { store.addDecision(lastEval); toast("Décision enregistrée ✓", { type: "ok" }); } };

  // ── Projection ──
  view.querySelector("#projHead").onclick = async () => {
    projOpen = !projOpen;
    view.querySelector("#projBody").hidden = !projOpen;
    view.querySelector("#projCaret").textContent = projOpen ? "▾" : "▸";
    if (projOpen) buildProjection(view, config, lines);
  };
  if (projOpen) buildProjection(view, config, lines);
}

function buildProjection(view, config, lines) {
  const plannedExpenses = lines.filter((l) => l.is_active).reduce((s, l) => s + l.monthly_limit, 0);
  const income = config.monthly_income || 0;
  const events = config.one_time_events || [];

  const start = store.month;
  const rows = [];
  let cumulative = config.cash || 0;
  for (let i = 0; i < 12; i++) {
    const [y, m] = start.split("-").map(Number);
    const d = new Date(y, m - 1 + i, 1);
    const ym = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;

    const monthEvents = events.filter((e) => (e.date || "").slice(0, 7) === ym);
    const eventInflow = monthEvents.filter((e) => e.amount > 0).reduce((s, e) => s + e.amount, 0);
    const eventOutflow = monthEvents.filter((e) => e.amount < 0).reduce((s, e) => s + (-e.amount), 0);
    const pendingInflow = (config.savings_pending_date || "").slice(0, 7) === ym ? (config.savings_pending || 0) : 0;

    const revenus = income + eventInflow + pendingInflow;
    const depenses = plannedExpenses + eventOutflow;
    const balance = revenus - depenses;
    cumulative += balance;

    rows.push({
      ym, revenus, depenses, balance, cumulative,
      events: monthEvents.map((e) => e.label).filter(Boolean).join(", ") + (pendingInflow ? (monthEvents.length ? ", " : "") + "Épargne dispo" : ""),
    });
  }

  // Chart
  const canvas = view.querySelector("#proj");
  if (projChart) projChart.destroy();
  const minRes = config.minimum_reserve || 0;
  projChart = new Chart(canvas, {
    type: "line",
    data: {
      labels: rows.map((r) => r.ym.slice(2)),
      datasets: [
        {
          label: "Trésorerie cumulée", data: rows.map((r) => Math.round(r.cumulative)),
          borderColor: cssVar("--navy"), backgroundColor: "rgba(31,56,100,.12)", fill: true, tension: .25,
          pointBackgroundColor: rows.map((r) => r.events ? cssVar("--purple") : cssVar("--navy")),
          pointRadius: rows.map((r) => r.events ? 5 : 3),
        },
        {
          label: "Réserve minimale", data: rows.map(() => minRes),
          borderColor: cssVar("--red"), borderDash: [6, 6], pointRadius: 0, fill: false,
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: tickColor() } }, tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${money(c.raw)}` } } },
      scales: {
        x: { ticks: { color: tickColor() }, grid: { display: false } },
        y: { ticks: { color: tickColor() }, grid: { color: "rgba(128,128,128,.15)" } },
      },
    },
  });

  // Table
  view.querySelector("#projTable").innerHTML = `
    <thead><tr><th>Mois</th><th>Revenus</th><th>Dépenses</th><th>Balance</th><th>Tréso.</th><th>Événements</th></tr></thead>
    <tbody>
      ${rows.map((r) => `
        <tr class="${r.cumulative < (config.minimum_reserve || 0) ? "neg" : ""}">
          <td>${escHtml(fmtMonthLabel(r.ym))}</td>
          <td>${money(r.revenus, true)}</td>
          <td>${money(r.depenses, true)}</td>
          <td>${money(r.balance, true)}</td>
          <td>${money(r.cumulative, true)}</td>
          <td>${escHtml(r.events || "—")}</td>
        </tr>`).join("")}
    </tbody>`;
}
