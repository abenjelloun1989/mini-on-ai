/**
 * store.js — lightweight shared state + localStorage persistence.
 */

const LS = {
  theme: "fin-theme",            // "light" | "dark" | null (=auto)
  lastCategory: "fin-last-cat",  // last used budget_line_id
  decisions: "fin-decisions",    // affordability decision log
  privacyDismissed: "fin-privacy-ok",
};

export const store = {
  // current YYYY-MM being viewed (shared across screens)
  month: new Date().toISOString().slice(0, 7),
  // cache of budget lines (refreshed by loadBudgetLines)
  budgetLines: [],

  getTheme() { return localStorage.getItem(LS.theme); },
  setTheme(v) { v ? localStorage.setItem(LS.theme, v) : localStorage.removeItem(LS.theme); },

  getLastCategory() { return localStorage.getItem(LS.lastCategory) || null; },
  setLastCategory(id) { id ? localStorage.setItem(LS.lastCategory, id) : localStorage.removeItem(LS.lastCategory); },

  getDecisions() {
    try { return JSON.parse(localStorage.getItem(LS.decisions) || "[]"); } catch { return []; }
  },
  addDecision(d) {
    const list = store.getDecisions();
    list.unshift({ ...d, at: new Date().toISOString() });
    localStorage.setItem(LS.decisions, JSON.stringify(list.slice(0, 50)));
  },

  isPrivacyDismissed() { return localStorage.getItem(LS.privacyDismissed) === "1"; },
  dismissPrivacy() { localStorage.setItem(LS.privacyDismissed, "1"); },
};

/** Shift current month by delta and return new value. */
export function shiftMonth(month, delta) {
  const [y, m] = month.split("-").map(Number);
  const d = new Date(y, m - 1 + delta, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}
