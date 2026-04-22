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
  try {
    await initPopup();
  } catch (e) {
    console.error("JobGuard popup init error:", e);
    // Show recovery UI instead of blank tab
    const analyzeTab = document.getElementById("tab-analyze");
    if (analyzeTab) analyzeTab.innerHTML = `
      <div style="text-align:center;padding:28px 16px;">
        <p style="font-size:20px;margin-bottom:8px;">⚠️</p>
        <p style="font-weight:600;margin-bottom:6px;">Something went wrong</p>
        <p style="font-size:12px;color:var(--text-muted);margin-bottom:16px;">
          The extension encountered an error on startup.
        </p>
        <button class="btn-primary" id="resetStateBtn">Reset &amp; Recover</button>
      </div>`;
    document.getElementById("resetStateBtn")?.addEventListener("click", async () => {
      await chrome.storage.local.remove(["jgLastAnalysis", "jgHistory", "jgFullPage"]);
      window.location.reload();
    });
  }
});

async function initPopup() {
  // Dark mode — provided by shared.js
  initDarkMode("jg-theme", "darkModeToggle");

  // Load user
  const stored = await chrome.storage.local.get(["userId", "tier"]);
  userId = stored.userId;
  currentTier = stored.tier || "free";

  if (!userId) {
    showError("Extension not registered. Please reinstall.");
    return;
  }

  // Restore last analysis if available — wrapped in its own try/catch so bad
  // saved data never prevents the popup from opening
  const { jgLastAnalysis } = await chrome.storage.local.get("jgLastAnalysis");
  if (jgLastAnalysis?.analysis) {
    try {
      document.getElementById("inputSection").style.display = "none";
      document.getElementById("results").style.display = "block";
      renderResults(jgLastAnalysis.analysis, null, null, { restored: true, ts: jgLastAnalysis.ts });
    } catch (e) {
      console.error("Failed to restore last analysis (clearing bad state):", e);
      await chrome.storage.local.remove("jgLastAnalysis");
      document.getElementById("inputSection").style.display = "flex";
    }
  }

  // Wire up tabs — shared utility from shared.js
  setupTabs((tabName) => {
    if (tabName === "account") loadAccount();
    if (tabName === "history") loadHistory();
  });

  // Settings button (optional — not always in header)
  document.getElementById("settingsBtn")?.addEventListener("click", () => {
    chrome.runtime.openOptionsPage();
  });

  // Header expand button — open full-page report
  document.getElementById("headerExpandBtn")?.addEventListener("click", () => {
    chrome.tabs.create({ url: chrome.runtime.getURL("popup/fullpage.html") });
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

      // Extraction function: JSON-LD first (works for SPAs like HelloWork),
      // then semantic selectors, then body fallback
      const extractFn = () => {
        // ── Strategy 1: JSON-LD structured data ─────────────────────────────
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        for (const script of scripts) {
          try {
            const data = JSON.parse(script.textContent);
            const isJobPosting = data['@type'] === 'JobPosting' || data.JobTitle || data.jobTitle;
            if (!isJobPosting) continue;
            const strip = html => (html || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
            const parts = [];
            const title = data.title || data.JobTitle || data.jobTitle;
            const company = data.hiringOrganization?.name || data.Company || data.company;
            const location = data.jobLocation?.address?.addressLocality
              || data.jobLocation?.address?.addressRegion
              || data.City || data.city;
            const contract = data.employmentType || data.ContractType || data.contractType;
            const salary = data.baseSalary?.value?.value
              || data.Salary || data.salary;
            const description = strip(data.description || data.Description || "");
            const qualifications = strip(data.qualifications || data.Qualifications || "");
            const responsibilities = strip(data.responsibilities || data.Responsibilities || "");
            const skills = data.skills ? (Array.isArray(data.skills) ? data.skills.join(", ") : data.skills) : null;
            const education = data.educationRequirements?.credentialCategory
              || (Array.isArray(data.Education) ? data.Education.join(", ") : data.Education);
            const experience = data.experienceRequirements?.monthsOfExperience
              ? `${data.experienceRequirements.monthsOfExperience} months`
              : data.Experience || data.experience;
            const sector = Array.isArray(data.Sector) ? data.Sector.join(", ") : (data.Sector || data.sector);

            if (title) parts.push(`Job Title: ${title}`);
            if (company) parts.push(`Company: ${company}`);
            if (location) parts.push(`Location: ${location}`);
            if (contract) parts.push(`Contract type: ${contract}`);
            if (salary) parts.push(`Salary: ${salary}`);
            if (sector) parts.push(`Sector: ${sector}`);
            if (education) parts.push(`Education required: ${education}`);
            if (experience) parts.push(`Experience required: ${experience}`);
            if (skills) parts.push(`Skills: ${skills}`);
            if (description) parts.push(`\nJob Description:\n${description}`);
            if (responsibilities) parts.push(`\nResponsibilities:\n${responsibilities}`);
            if (qualifications) parts.push(`\nQualifications:\n${qualifications}`);

            const result = parts.join("\n");
            if (result.length > 150) return result;
          } catch (e) { /* invalid JSON, skip */ }
        }

        // ── Strategy 2: semantic DOM selectors ──────────────────────────────
        const selectors = [
          '[itemprop="description"]',
          '[class*="job-description"]', '[class*="jobDescription"]',
          '[class*="offer-description"]', '[class*="job-detail"]',
          '[class*="job_description"]', '[class*="posting-description"]',
          'article', 'main',
        ];
        for (const sel of selectors) {
          const el = document.querySelector(sel);
          if (el) {
            const t = el.innerText?.trim() || "";
            if (t.length > 300) return t;
          }
        }

        // ── Strategy 3: body fallback ────────────────────────────────────────
        return document.body.innerText?.trim() || "";
      };

      let results = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: extractFn });
      let text = results?.[0]?.result?.trim() || "";

      // If too short — SPA may still be loading. Wait 2s and retry once.
      if (text.length < 200) {
        btn.textContent = "📄 Waiting for page…";
        await new Promise(r => setTimeout(r, 2000));
        results = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: extractFn });
        text = results?.[0]?.result?.trim() || "";
      }

      if (text.length < 100) {
        btn.textContent = "📄 Nothing found — try pasting";
        setTimeout(() => { btn.textContent = "📄 Analyze current page"; btn.disabled = false; }, 2500);
        return;
      }

      // Cap at 8000 chars (JSON-LD extraction is already focused, no sidebar noise)
      const clipped = text.slice(0, 8000);
      textarea.value = clipped;
      textarea.dispatchEvent(new Event("input"));
      btn.textContent = "📄 Analyze current page";
      btn.disabled = false;
      runAnalysis(clipped);
    } catch (e) {
      console.error("Page extract error:", e);
      btn.textContent = "📄 Could not read page";
      setTimeout(() => { btn.textContent = "📄 Analyze current page"; btn.disabled = false; }, 2000);
    }
  });

  // Upgrade banner
  document.getElementById("upgradeBannerBtn")?.addEventListener("click", () => startUpgrade(API_BASE, userId));

  // Load usage badge
  loadUsageBadge();
}

// ─── Usage badge (header) ────────────────────────────────────────────────────

async function loadUsageBadge() {
  try {
    const res = await fetch(`${API_BASE}/api/usage?user_id=${userId}`);
    if (!res.ok) return;
    const data = await res.json();
    currentTier = data.tier;
    await chrome.storage.local.set({ tier: data.tier });

    updateTierBadge(data.tier);

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
        document.getElementById("upgradeResultBtn")?.addEventListener("click", () => startUpgrade(API_BASE, userId));
        inputSection.style.display = "flex";
        return;
      }
      renderError(data.error || "Analysis failed. Please try again.", text);
      return;
    }

    // If AI detected a listing page (not a single job posting), show a friendly message
    if (data.analysis?.risk_score === 0) {
      loadingState.style.display = "none";
      results.style.display = "block";
      results.innerHTML = `
        <div style="text-align:center;padding:24px;">
          <p style="font-size:28px;margin-bottom:10px;">🔍</p>
          <p style="font-weight:600;margin-bottom:6px;">This looks like a listing page</p>
          <p style="font-size:12px;color:var(--text-muted);margin-bottom:16px;">
            Open a single job posting and click Analyze again.
          </p>
          <button class="btn-secondary" id="backFromListBtn">← Go back</button>
        </div>`;
      document.getElementById("backFromListBtn").addEventListener("click", () => {
        results.style.display = "none";
        results.innerHTML = "";
        inputSection.style.display = "flex";
      });
      return;
    }

    renderResults(data.analysis, data.usage, text);
    saveLastAnalysis(data.analysis);
    saveToHistory(data.analysis);

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

function renderResults(analysis, usage, originalText, opts = {}) {
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
    ${opts.restored ? `
      <div class="restored-notice">
        <span>Last analysis · ${opts.ts ? new Date(opts.ts).toLocaleDateString() : ""}</span>
        <button class="btn-text" id="clearRestoredBtn">Analyze new →</button>
      </div>
    ` : ""}
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
      <button class="btn-secondary" id="newAnalysisBtn">← New</button>
      <button class="btn-secondary" id="copyResultBtn">📋 Copy</button>
      <button class="btn-secondary" id="resultsExpandBtn">⤢ Full page</button>
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

  document.getElementById("resultsExpandBtn").addEventListener("click", () => openFullPage(analysis));

  document.getElementById("clearRestoredBtn")?.addEventListener("click", () => {
    results.style.display = "none";
    results.innerHTML = "";
    document.getElementById("inputSection").style.display = "flex";
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
      // Use .onclick to avoid stacking duplicate listeners on repeated tab visits
      document.getElementById("manageSubBtn").onclick = openPortal;
    } else {
      document.getElementById("upgradeBtn").onclick = () => startUpgrade(API_BASE, userId);
      document.getElementById("redeemBtn").onclick = redeemLtd;
      document.getElementById("ltdCodeInput").onkeydown = (e) => {
        if (e.key === "Enter") redeemLtd();
      };
    }
  } catch (e) {
    console.error("Account load error:", e);
  }
}

// ─── Billing actions ──────────────────────────────────────────────────────────

// startUpgrade(apiBase, userId) — provided by shared.js

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
      updateTierBadge("pro");
      // Show pro actions immediately without waiting for full reload
      document.getElementById("freeActions")?.style.setProperty("display", "none");
      document.getElementById("proActions")?.style.setProperty("display", "block");
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

// ─── Persistence & History ────────────────────────────────────────────────────

async function saveLastAnalysis(analysis) {
  await chrome.storage.local.set({ jgLastAnalysis: { analysis, ts: Date.now() } });
}

async function saveToHistory(analysis) {
  const { jgHistory = [] } = await chrome.storage.local.get("jgHistory");
  jgHistory.unshift({ analysis, ts: Date.now() });
  await chrome.storage.local.set({ jgHistory: jgHistory.slice(0, 10) });
}

async function loadHistory() {
  const { jgHistory = [] } = await chrome.storage.local.get("jgHistory");
  const container = document.getElementById("historyList");
  if (!jgHistory.length) {
    container.innerHTML = `<p class="history-empty">No analyses yet — run your first analysis to see it here.</p>`;
    return;
  }
  container.innerHTML = jgHistory.map((item, i) => {
    const a = item.analysis;
    const score = a.risk_score || 0;
    const cls = score >= 9 ? "red" : score >= 7 ? "orange" : score >= 4 ? "yellow" : "green";
    const date = new Date(item.ts).toLocaleDateString();
    const platform = a.platform_detected && a.platform_detected !== "Unknown"
      ? a.platform_detected : "Unknown platform";
    return `
      <div class="history-card">
        <div class="history-score history-score--${cls}">${score}</div>
        <div class="history-info">
          <div class="history-label">${escHtml(a.risk_label || "Unknown")}</div>
          <div class="history-meta">${escHtml(platform)} · ${date}</div>
        </div>
        <button class="btn-secondary history-restore" data-index="${i}">Restore</button>
      </div>`;
  }).join("");

  container.querySelectorAll(".history-restore").forEach(btn => {
    btn.addEventListener("click", () => {
      const item = jgHistory[parseInt(btn.dataset.index)];
      // Switch to Analyze tab and show restored result
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");
      document.querySelector('[data-tab="analyze"]').classList.add("active");
      document.getElementById("tab-analyze").style.display = "block";
      document.getElementById("inputSection").style.display = "none";
      document.getElementById("loadingState").style.display = "none";
      document.getElementById("results").style.display = "block";
      renderResults(item.analysis, null, null, { restored: true, ts: item.ts });
    });
  });
}

async function openFullPage(analysis) {
  await chrome.storage.local.set({ jgFullPage: { analysis, ts: Date.now() } });
  chrome.tabs.create({ url: chrome.runtime.getURL("popup/fullpage.html") });
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

// copyText() and escHtml() are provided by shared.js

function showError(msg) {
  document.body.innerHTML = `<div style="padding:20px;color:#ef4444;font-size:12px;">${escHtml(msg)}</div>`;
}
