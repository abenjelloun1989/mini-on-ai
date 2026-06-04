/**
 * ui.js — formatting, toasts, skeletons, markdown, small DOM helpers.
 */

const eurFmt = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" });
const eurFmt0 = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

export function money(n, compact = false) {
  const v = Number(n) || 0;
  return (compact && Number.isInteger(v) ? eurFmt0 : eurFmt).format(v);
}

export function fmtDate(iso) {
  const d = new Date(iso + (iso.length === 10 ? "T00:00:00" : ""));
  return d.toLocaleDateString("fr-FR", { weekday: "short", day: "numeric", month: "short" });
}

export function fmtMonthLabel(month) {
  // month = "YYYY-MM"
  const [y, m] = month.split("-").map(Number);
  return new Date(y, m - 1, 1).toLocaleDateString("fr-FR", { month: "long", year: "numeric" });
}

/** Escape for safe innerHTML insertion. */
export function escHtml(str) {
  if (str === null || str === undefined) return "";
  const d = document.createElement("div");
  d.textContent = String(str);
  return d.innerHTML;
}

/** Consumption status color from a 0–100+ percentage. */
export function statusColor(pct) {
  if (pct >= 100) return "var(--red)";
  if (pct >= 80) return "var(--orange)";
  return "var(--green)";
}

/** Balance badge emoji + class. */
export function balanceStatus(balance) {
  if (balance >= 0) return { emoji: "🟢", color: "var(--green)" };
  if (balance >= -400) return { emoji: "🟠", color: "var(--orange)" };
  return { emoji: "🔴", color: "var(--red)" };
}

// ─── Toasts ─────────────────────────────────────────────────────────────────

let toastHost;
export function toast(message, opts = {}) {
  toastHost = toastHost || document.getElementById("toastHost");
  const el = document.createElement("div");
  el.className = "toast" + (opts.type ? ` ${opts.type}` : "");
  el.textContent = message;

  if (opts.action) {
    const btn = document.createElement("button");
    btn.className = "toast-action";
    btn.textContent = opts.action.label;
    btn.onclick = () => { opts.action.onClick(); dismiss(); };
    el.appendChild(btn);
  }
  toastHost.appendChild(el);

  let done = false;
  const dismiss = () => {
    if (done) return; done = true;
    el.style.opacity = "0"; el.style.transition = "opacity .2s";
    setTimeout(() => el.remove(), 200);
    clearTimeout(timer);
  };
  // swipe / tap to dismiss
  el.addEventListener("click", (e) => { if (e.target === el) dismiss(); });
  const timer = setTimeout(dismiss, opts.duration || 3000);
  return dismiss;
}

// ─── Skeletons ──────────────────────────────────────────────────────────────

export function skeletonLines(n = 3) {
  return Array.from({ length: n }, () => `<div class="skel skel-line"></div>`).join("");
}

// ─── Minimal markdown (bold + bullet lists) ──────────────────────────────────

export function renderMarkdown(text) {
  const lines = String(text).split("\n");
  let html = "";
  let inList = false;
  for (let raw of lines) {
    const line = raw.trimEnd();
    const bullet = line.match(/^\s*[-*]\s+(.*)$/);
    if (bullet) {
      if (!inList) { html += "<ul>"; inList = true; }
      html += `<li>${inline(bullet[1])}</li>`;
    } else {
      if (inList) { html += "</ul>"; inList = false; }
      if (line) html += `<div>${inline(line)}</div>`;
      else html += "<br>";
    }
  }
  if (inList) html += "</ul>";
  return html;

  function inline(s) {
    return escHtml(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  }
}

// ─── DOM helper ───────────────────────────────────────────────────────────────

/** Build an element from an HTML string (first child). */
export function h(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}
