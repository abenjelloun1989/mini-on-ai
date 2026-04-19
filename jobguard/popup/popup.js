/**
 * JobGuard — Popup
 */

const API_BASE = "https://jobguard-api.kirozdormu.workers.dev";
const FREE_LIMIT = 5;
const MAX_LENGTH = 15000;

let userId = null;
let currentTier = "free";

// ─── Init ────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  // Dark mode — runs before render to avoid flash
  (function () {
    const toggle = document.getElementById("darkModeToggle");
    const stored = localStorage.getItem("jg-theme");
    if (stored === "light") {
      document.body.classList.add("light-mode");
      if (toggle) toggle.textContent = "☀";
    }
    if (toggle) {
      toggle.addEventListener("click", () => {
        const isLight = document.body.classList.toggle("light-mode");
        localStorage.setItem("jg-theme", isLight ? "light" : "dark");
        toggle.textContent = isLight ? "☀" : "☾";
      });
    }
  })();

  // Load user
  const stored = await chrome.storage.local.get(["userId", "tier"]);
  userId = stored.userId;
  currentTier = stored.tier || "free";

  if (!userId) {
    showError("Extension not registered. Please reinstall.");
    return;
  }

  // Wire up tabs
  document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");
      tab.classList.add("active");
      document.getElementById(`tab-${tab.dataset.tab}`).style.display = "block";
      if (tab.dataset.tab === "account") loadAccount();
    });
  });

  // Settings button
  document.getElementById("settingsBtn").addEventListener("click", () => {
    chrome.runtime.openOptionsPage();
  });

  // Textarea — char count + enable button
  const textarea = document.getElementById("postingText");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const charCount = document.getElementById("charCount");

  textarea.addEventListener("input", () => {
    const len = textarea.value.trim().length;
    charCount.textContent = `${len.toLocaleString()} / ${MAX_LENGTH.toLocaleString()}`;
    charCount.className = `char-count${len >= 30 ? " ready" : ""}`;
    analyzeBtn.disabled = len < 30;
  });

  // Ctrl+Enter submits
  textarea.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !analyzeBtn.disabled) {
      e.preventDefault();
      runAnalysis(textarea.value.trim());
    }
  });

  // Analyze button
  analyzeBtn.addEventListener("click", () => {
    const text = textarea.value.trim();
    if (text.length >= 30) runAnalysis(text);
  });

  // Analyze current page
  document.getElementById("analyzePageBtn").addEventListener("click", async () => {
    const btn = document.getElementById("analyzePageBtn");
    btn.textContent = "📄 Extracting…";
    btn.disabled = true;
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.body.innerText,
      });
      const text = results?.[0]?.result?.trim() || "";
      if (text.length < 30) {
        btn.textContent = "📄 Nothing found on page";
        setTimeout(() => { btn.textContent = "📄 Analyze current page"; btn.disabled = false; }, 2000);
        return;
      }
      // Truncate if needed and fill textarea
      const clipped = text.slice(0, MAX_LENGTH);
      textarea.value = clipped;
      textarea.dispatchEvent(new Event("input"));
      btn.textContent = "📄 Analyze current page";
      btn.disabled = false;
      // Auto-run analysis
      runAnalysis(clipped);
    } catch (e) {
      console.error("Page extract error:", e);
      btn.textContent = "📄 Could not read page";
      setTimeout(() => { btn.textContent = "📄 Analyze current page"; btn.disabled = false; }, 2000);
    }
  });

  // Upgrade banner
  document.getElementById("upgradeBannerBtn")?.addEventListener("click", startUpgrade);

  // Load usage badge
  loadUsageBadge();
});

// ─── Usage badge (header) ────────────────────────────────────────────────────

async function loadUsageBadge() {
  try {
    const res = await fetch(`${API_BASE}/api/usage?user_id=${userId}`);
    if (!res.ok) return;
    const data = await res.json();
    currentTier = data.tier;
    await chrome.storage.local.set({ tier: data.tier });

    const badge = document.getElementById("tierBadge");
    if (data.tier === "pro") {
      badge.textContent = "Pro";
      badge.classList.add("tier-badge--pro");
    }

    // Show upgrade banner if at limit
    if (data.tier !== "pro" && data.usage_this_month >= FREE_LIMIT) {
      document.getElementById("upgradeBanner").style.display = "block";
    }
  } catch (e) {
    console.error("Usage load error:", e);
  }
}

// ─── Analysis ────────────────────────────────────────────────────────────────

async function runAnalysis(text) {
  const inputSection = document.getElementById("inputSection");
  const loadingState = document.getElementById("loadingState");
  const results = document.getElementById("results");

  inputSection.style.display = "none";
  loadingState.style.display = "flex";
  results.style.display = "none";
  results.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, posting_text: text }),
    });

    const data = await res.json();

    loadingState.style.display = "none";
    results.style.display = "block";

    if (!res.ok) {
      if (res.status === 429 && data.upgrade_required) {
        results.innerHTML = `
          <div style="text-align:center;padding:20px;">
            <p style="font-size:20px;margin-bottom:8px;">🔒</p>
            <p style="font-weight:600;margin-bottom:6px;">Monthly limit reached</p>
            <p style="font-size:12px;color:var(--text-muted);margin-bottom:16px;">You've used all ${FREE_LIMIT} free analyses this month.</p>
            <button class="btn-primary btn-full" id="upgradeResultBtn">Upgrade to Pro — $7/month</button>
          </div>`;
        document.getElementById("upgradeResultBtn")?.addEventListener("click", startUpgrade);
        inputSection.style.display = "flex";
        return;
      }
      renderError(data.error || "Analysis failed. Please try again.", text);
      return;
    }

    renderResults(data.analysis, data.usage, text);

    // Update badge
    if (data.usage) {
      currentTier = data.usage.tier;
      const badge = document.getElementById("tierBadge");
      if (data.usage.tier === "pro") {
        badge.textContent = "Pro";
        badge.classList.add("tier-badge--pro");
      }
    }

  } catch (e) {
    console.error("Analysis error:", e);
    loadingState.style.display = "none";
    results.style.display = "block";
    renderError("Network error. Please try again.", text);
  }
}

function renderResults(analysis, usage, originalText) {
  const results = document.getElementById("results");

  // Risk banner colour
  const score = analysis.risk_score || 0;
  let bannerClass = "green";
  if (score >= 9) bannerClass = "red";
  else if (score >= 7) bannerClass = "orange";
  else if (score >= 4) bannerClass = "yellow";

  // Red flags
  const redFlagsHtml = (analysis.red_flags || []).map(f => `
    <div class="flag-card flag-card--${f.severity === "danger" ? "danger" : "warning"}">
      <div class="flag-header">
        <span class="flag-icon">${f.severity === "danger" ? "🔴" : "🟡"}</span>
        <span class="flag-title">${escHtml(f.title)}</span>
      </div>
      <div class="flag-body">${escHtml(f.explanation)}</div>
      ${f.quote ? `<div class="flag-quote">"${escHtml(f.quote)}"</div>` : ""}
    </div>
  `).join("");

  // Green signals
  const greenHtml = (analysis.green_signals || []).map(g => `
    <div class="flag-card flag-card--green">
      <div class="flag-header">
        <span class="flag-icon">✅</span>
        <span class="flag-title">${escHtml(g.title)}</span>
      </div>
      <div class="flag-body">${escHtml(g.explanation)}</div>
    </div>
  `).join("");

  // Negotiation tips
  const tipsHtml = (analysis.negotiation_tips || []).map((tip, i) => `
    <div class="tip-item">
      <span class="tip-num">${i + 1}</span>
      <span>${escHtml(tip)}</span>
    </div>
  `).join("");

  // Usage line
  const usageLine = usage && currentTier !== "pro"
    ? `<p style="font-size:11px;color:var(--text-muted);margin-top:10px;text-align:right">${usage.count} / ${usage.limit} analyses used this month</p>`
    : "";

  results.innerHTML = `
    <div class="risk-banner risk-banner--${bannerClass}">
      <div class="risk-score-circle">${score}</div>
      <div class="risk-info">
        <div class="risk-label">${escHtml(analysis.risk_label || "Unknown")}</div>
        ${analysis.platform_detected && analysis.platform_detected !== "Unknown"
          ? `<div class="risk-platform">${escHtml(analysis.platform_detected)}</div>`
          : ""}
      </div>
    </div>

    <div class="result-summary">${escHtml(analysis.summary || "")}</div>

    ${(analysis.red_flags || []).length > 0 ? `
      <div class="section-title">🚩 Red flags (${analysis.red_flags.length})</div>
      <div class="flag-list">${redFlagsHtml}</div>
    ` : ""}

    ${analysis.market_rate_note ? `
      <div class="section-title">💰 Market rate</div>
      <div class="market-rate">${escHtml(analysis.market_rate_note)}</div>
    ` : ""}

    ${(analysis.green_signals || []).length > 0 ? `
      <div class="section-title">✅ Good signs</div>
      <div class="flag-list">${greenHtml}</div>
    ` : ""}

    ${(analysis.negotiation_tips || []).length > 0 ? `
      <div class="section-title">💡 Before you apply</div>
      <div class="tips-list">${tipsHtml}</div>
    ` : ""}

    <div class="results-footer">
      <button class="btn-secondary" id="newAnalysisBtn">← Analyze another</button>
      <button class="btn-secondary" id="copyResultBtn">📋 Copy</button>
    </div>
    ${usageLine}
  `;

  document.getElementById("newAnalysisBtn").addEventListener("click", () => {
    results.style.display = "none";
    results.innerHTML = "";
    const inputSection = document.getElementById("inputSection");
    inputSection.style.display = "flex";
    document.getElementById("postingText").value = "";
    document.getElementById("charCount").textContent = `0 / ${MAX_LENGTH.toLocaleString()}`;
    document.getElementById("analyzeBtn").disabled = true;
    // Show upgrade banner if at limit
    if (usage && currentTier !== "pro" && usage.count >= FREE_LIMIT) {
      document.getElementById("upgradeBanner").style.display = "block";
    }
  });

  document.getElementById("copyResultBtn").addEventListener("click", (e) => {
    const text = buildCopyText(analysis);
    copyText(e.currentTarget, text);
  });
}

function renderError(message, originalText) {
  const results = document.getElementById("results");
  results.innerHTML = `
    <div style="text-align:center;padding:24px;">
      <p style="font-size:24px;margin-bottom:8px;">⚠️</p>
      <p style="font-size:12px;color:var(--text-muted);margin-bottom:12px;">${escHtml(message)}</p>
      <button class="btn-primary" id="retryBtn">Try again</button>
    </div>`;
  document.getElementById("retryBtn").addEventListener("click", () => runAnalysis(originalText));
  document.getElementById("inputSection").style.display = "flex";
}

// ─── Account Tab ──────────────────────────────────────────────────────────────

async function loadAccount() {
  try {
    const res = await fetch(`${API_BASE}/api/usage?user_id=${userId}`);
    if (!res.ok) return;
    const data = await res.json();
    currentTier = data.tier;

    document.getElementById("accountTier").textContent = data.tier === "pro" ? "Pro ✓" : "Free";
    document.getElementById("accountUsage").textContent = data.tier === "pro"
      ? `${data.usage_this_month} (unlimited)`
      : `${data.usage_this_month} / ${FREE_LIMIT}`;

    if (data.tier === "pro") {
      document.getElementById("freeActions").style.display = "none";
      document.getElementById("proActions").style.display = "block";
      document.getElementById("manageSubBtn").addEventListener("click", openPortal);
    } else {
      document.getElementById("upgradeBtn").addEventListener("click", startUpgrade);
      document.getElementById("redeemBtn").addEventListener("click", redeemLtd);
      document.getElementById("ltdCodeInput").addEventListener("keydown", (e) => {
        if (e.key === "Enter") redeemLtd();
      });
    }
  } catch (e) {
    console.error("Account load error:", e);
  }
}

// ─── Billing actions ──────────────────────────────────────────────────────────

async function startUpgrade() {
  try {
    const res = await fetch(`${API_BASE}/api/subscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
    const data = await res.json();
    if (data.checkout_url) {
      chrome.tabs.create({ url: data.checkout_url });
    } else {
      alert(data.error || "Failed to start checkout.");
    }
  } catch (e) {
    alert("Network error. Please try again.");
  }
}

async function openPortal() {
  try {
    const res = await fetch(`${API_BASE}/api/portal`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
    const data = await res.json();
    if (data.portal_url) {
      chrome.tabs.create({ url: data.portal_url });
    } else {
      alert(data.error || "Could not open billing portal.");
    }
  } catch (e) {
    alert("Network error. Please try again.");
  }
}

async function redeemLtd() {
  const codeInput = document.getElementById("ltdCodeInput");
  const msgEl = document.getElementById("ltdMessage");
  const code = codeInput.value.trim();
  if (!code) return;

  msgEl.textContent = "Checking…";
  msgEl.className = "ltd-message";

  try {
    const res = await fetch(`${API_BASE}/api/redeem-ltd`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, code }),
    });
    const data = await res.json();
    if (data.success) {
      await chrome.storage.local.set({ tier: "pro" });
      currentTier = "pro";
      msgEl.textContent = "✓ Lifetime access activated!";
      msgEl.className = "ltd-message ltd-message--ok";
      // Refresh account UI
      setTimeout(() => loadAccount(), 800);
    } else {
      msgEl.textContent = data.error || "Invalid code.";
      msgEl.className = "ltd-message ltd-message--err";
    }
  } catch (e) {
    msgEl.textContent = "Network error. Please try again.";
    msgEl.className = "ltd-message ltd-message--err";
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function buildCopyText(analysis) {
  const lines = [
    `JobGuard Analysis — ${analysis.risk_label} (${analysis.risk_score}/10)`,
    "",
    analysis.summary || "",
  ];
  if (analysis.red_flags?.length) {
    lines.push("", "Red Flags:");
    analysis.red_flags.forEach(f => lines.push(`• [${f.severity.toUpperCase()}] ${f.title}: ${f.explanation}`));
  }
  if (analysis.market_rate_note) {
    lines.push("", "Market Rate:", analysis.market_rate_note);
  }
  if (analysis.negotiation_tips?.length) {
    lines.push("", "Before you apply:");
    analysis.negotiation_tips.forEach((t, i) => lines.push(`${i + 1}. ${t}`));
  }
  return lines.join("\n");
}

function copyText(btn, text, resetLabel = "📋 Copy") {
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = "✓ Copied!";
    setTimeout(() => { if (btn.isConnected) btn.textContent = resetLabel; }, 2000);
  }).catch(() => {
    btn.textContent = "Copy failed";
    setTimeout(() => { if (btn.isConnected) btn.textContent = resetLabel; }, 2000);
  });
}

function showError(msg) {
  document.body.innerHTML = `<div style="padding:20px;color:#ef4444;font-size:12px;">${escHtml(msg)}</div>`;
}

function escHtml(str) {
  if (!str) return "";
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}
