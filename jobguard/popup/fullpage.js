/**
 * JobGuard — Full Page Report
 * Reads analysis from chrome.storage.local and renders a printable report.
 */

document.addEventListener("DOMContentLoaded", async () => {
  const { jgFullPage } = await chrome.storage.local.get("jgFullPage");
  if (!jgFullPage) {
    document.getElementById("report").textContent = "No report data found. Run an analysis first.";
    return;
  }
  render(jgFullPage.analysis, jgFullPage.ts);
});

function render(a, ts) {
  const score = a.risk_score || 0;
  const cls = score >= 9 ? "red" : score >= 7 ? "orange" : score >= 4 ? "yellow" : "green";

  document.getElementById("reportMeta").textContent =
    (a.platform_detected && a.platform_detected !== "Unknown") ? a.platform_detected : "";
  document.getElementById("reportDate").textContent =
    ts ? new Date(ts).toLocaleString() : new Date().toLocaleString();

  const redFlagsHtml = (a.red_flags || []).map(f => `
    <div class="flag-card ${f.severity === "danger" ? "danger" : "warning"}">
      <div class="flag-header">
        <span class="flag-icon">${f.severity === "danger" ? "🔴" : "🟡"}</span>
        <span class="flag-title">${esc(f.title)}</span>
      </div>
      <div class="flag-body">${esc(f.explanation)}</div>
      ${f.quote ? `<div class="flag-quote">"${esc(f.quote)}"</div>` : ""}
    </div>
  `).join("");

  const greenHtml = (a.green_signals || []).map(g => `
    <div class="flag-card green">
      <div class="flag-header">
        <span class="flag-icon">✅</span>
        <span class="flag-title">${esc(g.title)}</span>
      </div>
      <div class="flag-body">${esc(g.explanation)}</div>
    </div>
  `).join("");

  const tipsHtml = (a.negotiation_tips || []).map((tip, i) => `
    <div class="tip-item">
      <span class="tip-num">${i + 1}</span>
      <span>${esc(tip)}</span>
    </div>
  `).join("");

  document.getElementById("report").innerHTML = `
    <div class="risk-banner ${cls}">
      <div class="score-circle">${score}</div>
      <div>
        <div class="risk-label">${esc(a.risk_label || "Unknown")}</div>
        ${a.platform_detected && a.platform_detected !== "Unknown"
          ? `<div class="risk-platform">${esc(a.platform_detected)}</div>` : ""}
      </div>
    </div>

    ${a.summary ? `<div class="summary">${esc(a.summary)}</div>` : ""}

    ${(a.red_flags || []).length ? `
      <div class="section-title">🚩 Red flags (${a.red_flags.length})</div>
      <div class="flag-list">${redFlagsHtml}</div>
    ` : ""}

    ${a.market_rate_note ? `
      <div class="section-title">💰 Market rate</div>
      <div class="market-rate">${esc(a.market_rate_note)}</div>
    ` : ""}

    ${(a.green_signals || []).length ? `
      <div class="section-title">✅ Good signs</div>
      <div class="flag-list">${greenHtml}</div>
    ` : ""}

    ${(a.negotiation_tips || []).length ? `
      <div class="section-title">💡 Before you apply</div>
      <div class="tips-list">${tipsHtml}</div>
    ` : ""}
  `;
}

function esc(str) {
  if (!str) return "";
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}
