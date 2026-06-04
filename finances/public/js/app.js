/**
 * app.js — bootstrap: theme, service worker, router, tab bar + FAB wiring.
 */
import { store } from "./store.js";
import { api, DEMO } from "./api.js";
import { fmtMonthLabel, balanceStatus, toast } from "./ui.js";

import { renderAccueil } from "./screens/accueil.js";
import { renderHistorique } from "./screens/historique.js";
import { renderStats } from "./screens/stats.js";
import { renderReserves } from "./screens/reserves.js";
import { renderChat } from "./screens/chat.js";
import { renderReglages } from "./screens/reglages.js";
import { openTxSheet } from "./screens/add-tx.js";

const SCREENS = {
  accueil: renderAccueil,
  historique: renderHistorique,
  stats: renderStats,
  reserves: renderReserves,
  chat: renderChat,
  reglages: renderReglages,
};

const view = document.getElementById("view");
let current = "accueil";

// ─── Theme ────────────────────────────────────────────────────────────────────
function applyTheme() {
  const t = store.getTheme(); // "light" | "dark" | null(auto)
  const root = document.documentElement;
  root.classList.remove("theme-light", "theme-dark");
  if (t === "light") root.classList.add("theme-light");
  if (t === "dark") root.classList.add("theme-dark");
  updateThemeIcon();
}
function effectiveDark() {
  const t = store.getTheme();
  if (t === "dark") return true;
  if (t === "light") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}
function updateThemeIcon() {
  document.getElementById("themeToggle").textContent = effectiveDark() ? "☀️" : "🌙";
}
document.getElementById("themeToggle").addEventListener("click", () => {
  store.setTheme(effectiveDark() ? "light" : "dark");
  applyTheme();
});

// ─── Router ────────────────────────────────────────────────────────────────────
export async function navigate(route, opts = {}) {
  if (!SCREENS[route]) route = "accueil";
  current = route;
  // Highlight active tab (reglages has no tab)
  document.querySelectorAll(".tab").forEach((t) =>
    t.classList.toggle("active", t.dataset.route === route)
  );
  view.scrollTop = 0;
  window.scrollTo(0, 0);
  await SCREENS[route](view, opts);
}
// expose for cross-screen navigation
window.appNavigate = navigate;
// re-render the current screen in place (after a save/delete elsewhere)
window.appReload = (opts) => navigate(current, opts);

// ─── App bar: month + balance badge ────────────────────────────────────────────
export async function refreshAppbar() {
  document.getElementById("appbarMonth").textContent = fmtMonthLabel(store.month);
  try {
    const stats = await api.stats(store.month);
    const bal = stats.income - stats.expenses;
    const s = balanceStatus(bal);
    document.getElementById("balanceBadge").textContent = s.emoji;
  } catch { /* ignore */ }
}
window.refreshAppbar = refreshAppbar;

// ─── Tab bar + FAB ─────────────────────────────────────────────────────────────
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => navigate(tab.dataset.route));
});
document.getElementById("settingsBtn").addEventListener("click", () => navigate("reglages"));
document.getElementById("fab").addEventListener("click", () => openTxSheet());

// ─── Service worker ────────────────────────────────────────────────────────────
if ("serviceWorker" in navigator && !DEMO) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("service-worker.js").catch(() => {});
  });
}
window.addEventListener("offline", () => toast("Mode hors ligne", { type: "err" }));

// ─── Boot ──────────────────────────────────────────────────────────────────────
applyTheme();
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", updateThemeIcon);

async function boot() {
  try {
    store.budgetLines = await api.budgetLines.list();
  } catch { store.budgetLines = []; }
  await refreshAppbar();
  await navigate("accueil");
}
boot();
