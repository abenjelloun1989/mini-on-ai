/**
 * stats.js — donut (spend by category) + grouped bar (Prévu vs Réel) + insights.
 */
import { api } from "../api.js";
import { store, shiftMonth } from "../store.js";
import { money, fmtMonthLabel, statusColor, escHtml, skeletonLines } from "../ui.js";

let period = 1; // months: 1 | 3 | 6
let donutChart = null;
let barChart = null;

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}
function tickColor() {
  return getComputedStyle(document.body).color;
}

export async function renderStats(view) {
  destroyCharts();
  view.innerHTML = `
    <div class="month-nav">
      <button id="mPrev">‹</button>
      <span class="m-label">${fmtMonthLabel(store.month)}</span>
      <button id="mNext">›</button>
    </div>
    <div class="toggle-pills">
      <button data-p="1" class="${period === 1 ? "active" : ""}">Ce mois</button>
      <button data-p="3" class="${period === 3 ? "active" : ""}">3 mois</button>
      <button data-p="6" class="${period === 6 ? "active" : ""}">6 mois</button>
    </div>
    <div class="insight" id="insight">${skeletonLines(1)}</div>
    <div class="card"><div class="chart-wrap"><canvas id="donut"></canvas></div></div>
    <div id="catList"></div>
    <div class="section-title">Prévu vs Réel</div>
    <div class="card"><div class="chart-wrap"><canvas id="bar"></canvas></div></div>
  `;
  view.querySelector("#mPrev").onclick = () => { store.month = shiftMonth(store.month, -1); window.refreshAppbar?.(); renderStats(view); };
  view.querySelector("#mNext").onclick = () => { store.month = shiftMonth(store.month, 1); window.refreshAppbar?.(); renderStats(view); };
  view.querySelectorAll(".toggle-pills button").forEach((b) => b.onclick = () => { period = +b.dataset.p; renderStats(view); });

  // Aggregate the last `period` months ending at store.month
  const months = Array.from({ length: period }, (_, i) => shiftMonth(store.month, -(period - 1 - i)));
  let agg = {};
  try {
    const all = await Promise.all(months.map((m) => api.stats(m)));
    for (const s of all) {
      for (const l of s.by_budget_line) {
        const a = agg[l.id] || (agg[l.id] = { id: l.id, name: l.name, color: l.color, emoji: l.emoji, limit: 0, spent: 0 });
        a.limit += l.limit;
        a.spent += l.spent;
      }
    }
  } catch { /* empty */ }

  const lines = Object.values(agg).map((a) => ({
    ...a,
    remaining: a.limit - a.spent,
    pct: a.limit > 0 ? Math.round((a.spent / a.limit) * 100) : (a.spent > 0 ? 100 : 0),
  }));
  const spentLines = lines.filter((l) => l.spent > 0);

  // Insight
  const over = lines.filter((l) => l.spent > l.limit && l.limit > 0);
  const inBudget = lines.length - over.length;
  let insight;
  if (over.length === 0) insight = `${inBudget}/${lines.length} postes dans le budget 🟢`;
  else { const worst = over.sort((a, b) => (b.spent - b.limit) - (a.spent - a.limit))[0]; insight = `⚠️ ${escHtml(worst.name)} dépasse le budget de ${money(worst.spent - worst.limit, true)}`; }
  view.querySelector("#insight").textContent = insight;

  // Donut
  if (spentLines.length) {
    donutChart = new Chart(view.querySelector("#donut"), {
      type: "doughnut",
      data: {
        labels: spentLines.map((l) => l.name),
        datasets: [{ data: spentLines.map((l) => Math.round(l.spent * 100) / 100), backgroundColor: spentLines.map((l) => l.color), borderWidth: 0 }],
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: "62%",
        plugins: {
          legend: { position: "bottom", labels: { color: tickColor(), boxWidth: 12, padding: 12 } },
          tooltip: { callbacks: { label: (c) => `${c.label}: ${money(c.raw)}` } },
        },
      },
    });
  } else {
    view.querySelector("#donut").parentElement.innerHTML = `<div class="empty">Aucune dépense sur la période</div>`;
  }

  // Category list
  view.querySelector("#catList").innerHTML = lines.length ? lines.map((l) => `
    <div class="card stat-line">
      <div class="sl-head">
        <span class="sl-name">${escHtml(l.emoji || "")} ${escHtml(l.name)}</span>
        <span class="sl-amt">${money(l.spent, true)} / ${money(l.limit, true)} · ${l.pct}%</span>
      </div>
      <div class="progress"><span style="width:${Math.min(l.pct, 100)}%;background:${statusColor(l.pct)}"></span></div>
    </div>
  `).join("") : "";

  // Grouped bar — Prévu vs Réel
  if (lines.length) {
    barChart = new Chart(view.querySelector("#bar"), {
      type: "bar",
      data: {
        labels: lines.map((l) => l.emoji || l.name.slice(0, 4)),
        datasets: [
          { label: "Prévu", data: lines.map((l) => l.limit), backgroundColor: cssVar("--blue") },
          { label: "Réel", data: lines.map((l) => Math.round(l.spent * 100) / 100), backgroundColor: cssVar("--navy") },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: tickColor() } },
          tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${money(c.raw)}` } },
        },
        scales: {
          x: { ticks: { color: tickColor() }, grid: { display: false } },
          y: { ticks: { color: tickColor() }, grid: { color: "rgba(128,128,128,.15)" } },
        },
      },
    });
  }
}

function destroyCharts() {
  if (donutChart) { donutChart.destroy(); donutChart = null; }
  if (barChart) { barChart.destroy(); barChart = null; }
}
