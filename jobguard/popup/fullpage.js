/**
 * JobGuard — Full Page Report
 * Reads analysis from chrome.storage.local and renders a printable report.
 */

document.addEventListener("DOMContentLoaded", async () => {
  // Wire up print button (inline onclick blocked by MV3 CSP)
  document.getElementById("printBtn").addEventListener("click", () => window.print());

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
        <span class="flag-title">${escHtml(f.title)}</span>
      </div>
      <div class="flag-body">${escHtml(f.explanation)}</div>
      ${f.quote ? `<div class="flag-quote">"${escHtml(f.quote)}"</div>` : ""}
    </div>
  `).join("");

  const greenHtml = (a.green_signals || []).map(g => `
    <div class="flag-card green">
      <div class="flag-header">
        <span class="flag-icon">✅</span>
        <span class="flag-title">${escHtml(g.title)}</span>
      </div>
      <div class="flag-body">${escHtml(g.explanation)}</div>
    </div>
  `).join("");

  const tipsHtml = (a.negotiation_tips || []).map((tip, i) => `
    <div class="tip-item">
      <span class="tip-num">${i + 1}</span>
      <span>${escHtml(tip)}</span>
    </div>
  `).join("");

  document.getElementById("report").innerHTML = `
    <div class="risk-banner ${cls}">
      <div class="score-circle">${score}</div>
      <div>
        <div class="risk-label">${escHtml(a.risk_label || "Unknown")}</div>
        ${a.platform_detected && a.platform_detected !== "Unknown"
          ? `<div class="risk-platform">${escHtml(a.platform_detected)}</div>` : ""}
      </div>
    </div>

    ${a.summary ? `<div class="summary">${escHtml(a.summary)}</div>` : ""}

    ${(a.red_flags || []).length ? `
      <div class="section-title">🚩 Red flags (${a.red_flags.length})</div>
      <div class="flag-list">${redFlagsHtml}</div>
    ` : ""}

    ${a.market_rate_note ? `
      <div class="section-title">💰 Market rate</div>
      <div class="market-rate">${escHtml(a.market_rate_note)}</div>
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

// escHtml() is provided by shared.js
