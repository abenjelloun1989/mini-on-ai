const API_URL = "https://clauseguard-api.kirozdormu.workers.dev";

let userId = null;
let userTier = "free";
let currentAnalysis = null;

// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  await loadUser();
  setupTabs();
  setupAnalyzeTab();
  setupCompareTab();
  setupLibraryTab();
});

async function loadUser() {
  const data = await chrome.storage.local.get(["userId", "seenOnboarding"]);
  userId = data.userId;
  const isFirstTime = !userId;

  if (!userId) {
    // First time — generate UUID and register
    userId = crypto.randomUUID();
    await chrome.storage.local.set({ userId });
    try {
      await apiFetch("/api/auth/register", "POST", { user_id: userId });
    } catch (e) { /* non-fatal */ }
  }

  await refreshUsage();

  // Show onboarding tooltip on first launch
  if (isFirstTime && !data.seenOnboarding) {
    showOnboarding();
    await chrome.storage.local.set({ seenOnboarding: true });
  }
}

function showOnboarding() {
  const toast = document.createElement("div");
  toast.style.cssText = `
    position:fixed;bottom:14px;left:14px;right:14px;
    background:linear-gradient(135deg,#1e1b4b,#312e81);
    border:1px solid rgba(99,102,241,0.5);border-radius:10px;
    padding:12px 14px;z-index:999;
    box-shadow:0 8px 24px rgba(0,0,0,0.4);
    animation:slideUp 0.3s ease;
  `;
  toast.innerHTML = `
    <style>@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}</style>
    <div style="font-weight:700;font-size:13px;color:#e2e2f0;margin-bottom:5px;">👋 Welcome to ClauseGuard!</div>
    <div style="font-size:11px;color:#a5b4fc;line-height:1.6;margin-bottom:10px;">
      Paste a contract below, upload a PDF, or click <strong style="color:#e2e2f0;">"Analyze current page"</strong> on any contract page. You get <strong style="color:#e2e2f0;">3 free analyses</strong> per month.
    </div>
    <button id="onboardingClose" style="background:#6366f1;border:none;color:white;padding:5px 14px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;">Got it →</button>
  `;
  document.body.appendChild(toast);
  document.getElementById("onboardingClose").addEventListener("click", () => {
    toast.style.animation = "none";
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.2s";
    setTimeout(() => toast.remove(), 200);
  });
  // Auto-dismiss after 8 seconds
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 8000);
}

async function refreshUsage() {
  try {
    const data = await apiFetch(`/api/usage?user_id=${userId}`);
    userTier = data.tier;

    // Update tier badge
    const badge = document.getElementById("tierBadge");
    if (data.tier === "pro") {
      badge.textContent = "Pro";
      badge.classList.add("pro");
    } else {
      badge.textContent = "Free";
    }

    // Update usage text
    const usageText = document.getElementById("usageRow");
    if (data.tier === "pro") {
      usageText.innerHTML = `<span style="color: #6366f1;">✓ Pro — unlimited analyses</span>`;
    } else {
      const remaining = Math.max(0, data.limit - data.usage_this_month);
      if (remaining === 0) {
        usageText.innerHTML = `<span style="color:var(--red);">No free analyses left this month</span>`;
        document.getElementById("upgradeBanner").classList.remove("hidden");
        document.getElementById("analyzeBtn").disabled = true;
        document.getElementById("analyzeCurrentPage").disabled = true;
      } else {
        usageText.innerHTML = `<span style="color:var(--text-muted);">${remaining} free ${remaining === 1 ? "analysis" : "analyses"} remaining this month</span>`;
      }
    }

    // Update Pro gates
    updateProGates(data.tier === "pro");
  } catch (e) {
    console.error("Failed to load usage", e);
  }
}

function updateProGates(isPro) {
  const gates = ["compareGate", "libraryGate"];
  const forms  = ["compareForm", "libraryContent"];
  gates.forEach(id => document.getElementById(id).classList.toggle("hidden", isPro));
  forms.forEach(id => document.getElementById(id).classList.toggle("hidden", !isPro));
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────

function setupTabs() {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => {
        c.classList.remove("active");
        c.classList.add("hidden");
      });
      tab.classList.add("active");
      const target = document.getElementById(`tab-${tab.dataset.tab}`);
      target.classList.remove("hidden");
      target.classList.add("active");

      if (tab.dataset.tab === "library" && userTier === "pro") loadLibrary();
    });
  });
}

// ─── Analyze tab ──────────────────────────────────────────────────────────────

function setupAnalyzeTab() {
  const textarea = document.getElementById("contractText");
  const analyzeBtn = document.getElementById("analyzeBtn");

  // Enable analyze button when text is present
  textarea.addEventListener("input", () => {
    const hasText = textarea.value.trim().length >= 50;
    analyzeBtn.disabled = !hasText || (userTier !== "pro" && document.getElementById("upgradeBanner").classList.contains("hidden") === false);
  });

  analyzeBtn.addEventListener("click", runAnalysis);
  document.getElementById("newAnalysisBtn").addEventListener("click", showInputState);
  document.getElementById("upgradeFromBanner").addEventListener("click", openUpgrade);
  document.getElementById("exportBtn").addEventListener("click", exportReport);

  // Analyze current page
  document.getElementById("analyzeCurrentPage").addEventListener("click", analyzeCurrentPage);

  // PDF upload
  document.getElementById("pdfUpload").addEventListener("change", handlePdfUpload);

  // Google Doc import
  document.getElementById("importGoogleDoc").addEventListener("click", async () => {
    try {
      const response = await chrome.runtime.sendMessage({ action: "extractGoogleDoc" });
      if (response?.text) {
        textarea.value = response.text;
        textarea.dispatchEvent(new Event("input"));
      } else {
        alert(response?.error || "Could not extract text from the Google Doc. Make sure you have a Google Doc open in another tab.");
      }
    } catch (e) {
      alert("Could not connect to Google Doc. Make sure a Google Doc is open.");
    }
  });
}

async function analyzeCurrentPage() {
  const btn = document.getElementById("analyzeCurrentPage");
  btn.disabled = true;
  btn.textContent = "Extracting page text…";

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || tab.url?.startsWith("chrome://") || tab.url?.startsWith("chrome-extension://")) {
      alert("Cannot analyze this type of page. Navigate to a contract or document page first.");
      return;
    }

    // Inject extraction function into the active tab
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        // Remove noise elements
        const noise = ["script", "style", "nav", "header", "footer", "aside",
                       ".nav", ".header", ".footer", ".sidebar", ".menu",
                       ".cookie", ".banner", ".ad", ".popup"];
        const clone = document.body.cloneNode(true);
        noise.forEach(sel => {
          try { clone.querySelectorAll(sel).forEach(el => el.remove()); } catch {}
        });

        // Try semantic containers first
        const candidates = [
          clone.querySelector("article"),
          clone.querySelector("main"),
          clone.querySelector('[role="main"]'),
          clone.querySelector(".contract"),
          clone.querySelector(".document"),
          clone.querySelector(".content"),
        ].filter(Boolean);

        let text = "";
        if (candidates.length > 0) {
          text = candidates[0].innerText || candidates[0].textContent;
        } else {
          text = clone.innerText || clone.textContent;
        }

        return text.replace(/\n{3,}/g, "\n\n").trim().slice(0, 15000);
      },
    });

    const text = results?.[0]?.result?.trim();
    if (!text || text.length < 50) {
      alert("Could not extract enough text from this page. Try copying and pasting the contract text manually.");
      return;
    }

    const textarea = document.getElementById("contractText");
    textarea.value = text;
    textarea.dispatchEvent(new Event("input"));

    // Auto-detect contract type from page URL/title
    const urlLower = tab.url?.toLowerCase() || "";
    const titleLower = tab.title?.toLowerCase() || "";
    const typeSelect = document.getElementById("contractType");
    if (urlLower.includes("nda") || titleLower.includes("non-disclosure") || titleLower.includes("nda")) {
      typeSelect.value = "nda";
    } else if (titleLower.includes("employment") || titleLower.includes("offer letter")) {
      typeSelect.value = "employment";
    } else if (titleLower.includes("freelance") || titleLower.includes("service agreement")) {
      typeSelect.value = "freelance";
    } else if (titleLower.includes("lease") || titleLower.includes("rental")) {
      typeSelect.value = "lease";
    }

    // Auto-run analysis
    runAnalysis();
  } catch (e) {
    console.error("Page extraction failed:", e);
    alert("Could not access this page. Try pasting the contract text manually.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg> Analyze current page`;
  }
}

async function handlePdfUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const textarea = document.getElementById("contractText");
  textarea.value = "Extracting PDF text...";
  textarea.disabled = true;

  try {
    const text = await extractPdfText(file);
    if (text.trim().length < 50) {
      textarea.value = "";
      alert("Could not extract text from this PDF. It may be a scanned image. Please copy and paste the text manually.");
    } else {
      textarea.value = text.slice(0, 15000);
      if (text.length > 15000) {
        textarea.value += "\n\n[Text truncated to 15,000 characters]";
      }
      textarea.dispatchEvent(new Event("input"));
    }
  } catch (e) {
    textarea.value = "";
    alert("PDF extraction failed. Please paste the text manually.");
  } finally {
    textarea.disabled = false;
    event.target.value = ""; // reset file input
  }
}

async function extractPdfText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        if (typeof pdfjsLib === "undefined") {
          throw new Error("pdf.js not loaded");
        }
        // Point worker to bundled file inside the extension
        pdfjsLib.GlobalWorkerOptions.workerSrc = chrome.runtime.getURL("lib/pdf.worker.min.js");

        const typedArray = new Uint8Array(e.target.result);
        const pdf = await pdfjsLib.getDocument({ data: typedArray }).promise;
        const pages = Math.min(pdf.numPages, 100);
        let fullText = "";
        for (let i = 1; i <= pages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          // Join items, preserving line breaks via transform y-position changes
          let lastY = null;
          for (const item of content.items) {
            const y = item.transform?.[5];
            if (lastY !== null && Math.abs(y - lastY) > 5) fullText += "\n";
            fullText += item.str;
            lastY = y;
          }
          fullText += "\n\n";
        }
        resolve(fullText.trim());
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

async function runAnalysis() {
  const text = document.getElementById("contractText").value.trim();
  const type = document.getElementById("contractType").value;

  if (text.length < 50) return;

  showLoadingState();

  try {
    const data = await apiFetch("/api/analyze", "POST", {
      user_id: userId,
      contract_text: text,
      contract_type: type,
    });

    if (data.upgrade_required) {
      showInputState();
      document.getElementById("upgradeBanner").classList.remove("hidden");
      document.getElementById("analyzeBtn").disabled = true;
      return;
    }

    currentAnalysis = data.analysis;
    await refreshUsage();
    showResults(data.analysis, data.usage);
  } catch (e) {
    showInputState();
    const msg = e.message || "";
    if (msg.includes("429") || msg.toLowerCase().includes("rate")) {
      alert("Too many requests. Please wait a moment and try again.");
    } else if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
      alert("Could not connect to ClauseGuard. Check your internet connection and try again.");
    } else if (msg.includes("413") || msg.toLowerCase().includes("too large")) {
      alert("Contract text is too long. Please trim it to under 15,000 characters.");
    } else {
      alert("Analysis failed. Please try again in a moment.");
    }
  }
}

function showInputState() {
  document.getElementById("inputState").classList.remove("hidden");
  document.getElementById("loadingState").classList.add("hidden");
  document.getElementById("resultsState").classList.add("hidden");
}

function showLoadingState() {
  document.getElementById("inputState").classList.add("hidden");
  document.getElementById("loadingState").classList.remove("hidden");
  document.getElementById("resultsState").classList.add("hidden");
}

function showResults(analysis, usage) {
  document.getElementById("inputState").classList.add("hidden");
  document.getElementById("loadingState").classList.add("hidden");
  document.getElementById("resultsState").classList.remove("hidden");

  // Risk badge
  const score = analysis.risk_score || 0;
  const badge = document.getElementById("riskBadge");
  const cls = score <= 3 ? "low" : score <= 6 ? "medium" : score <= 8 ? "high" : "critical";
  badge.className = `risk-badge ${cls}`;
  document.getElementById("riskScore").textContent = score;
  document.getElementById("riskLabel").textContent = analysis.risk_label || "Unknown";

  // Summary
  document.getElementById("summaryBox").textContent = analysis.plain_english_summary || "";

  // Disclaimer
  document.getElementById("disclaimerBox").textContent = analysis.disclaimer || "";

  // Red flags
  const redFlagsList = document.getElementById("redFlagsList");
  const redFlagsSection = document.getElementById("redFlagsSection");
  if (analysis.red_flags?.length) {
    redFlagsList.innerHTML = analysis.red_flags.map(flag => `
      <div class="red-flag ${flag.severity}">
        <div class="red-flag-title">
          ${flag.severity === "danger" ? "🔴" : "🟡"} ${escHtml(flag.title)}
        </div>
        <div class="red-flag-text">${escHtml(flag.explanation)}</div>
      </div>
    `).join("");
    redFlagsSection.classList.remove("hidden");
  } else {
    redFlagsSection.classList.add("hidden");
  }

  // Clauses
  const clausesList = document.getElementById("clausesList");
  clausesList.innerHTML = (analysis.clauses || []).map(clause => `
    <div class="clause-card" data-id="${clause.id}">
      <div class="clause-header">
        <div class="clause-dot ${clause.risk_level}"></div>
        <span class="clause-category">${escHtml(clause.category)}</span>
        <span class="clause-title">${escHtml(clause.title)}</span>
        <span class="clause-chevron">▼</span>
      </div>
      <div class="clause-body">
        ${clause.original_text ? `<div class="clause-quote">"${escHtml(clause.original_text)}"</div>` : ""}
        <div class="clause-explanation">${escHtml(clause.explanation)}</div>
        ${clause.concern ? `<div class="clause-concern">⚠ ${escHtml(clause.concern)}</div>` : ""}
        ${clause.suggested_change ? `
          <div class="clause-suggestion">
            <div class="clause-suggestion-label">✦ Suggested change</div>
            ${escHtml(clause.suggested_change)}
            <br>
            <button class="copy-btn" data-text="${escAttr(clause.suggested_change)}">
              Copy suggestion
            </button>
            ${userTier === "pro" ? `<button class="save-clause-btn" data-category="${escAttr(clause.category)}" data-title="${escAttr(clause.title)}" data-text="${escAttr(clause.suggested_change)}">Save to library</button>` : ""}
          </div>
        ` : ""}
      </div>
    </div>
  `).join("");

  // Clause accordion
  clausesList.querySelectorAll(".clause-card").forEach(card => {
    card.querySelector(".clause-header").addEventListener("click", () => {
      card.classList.toggle("open");
    });
  });

  // Copy buttons
  clausesList.querySelectorAll(".copy-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      navigator.clipboard.writeText(btn.dataset.text).then(() => {
        btn.textContent = "✓ Copied!";
        btn.classList.add("copied");
        setTimeout(() => { btn.textContent = "Copy suggestion"; btn.classList.remove("copied"); }, 2000);
      });
    });
  });

  // Save clause buttons
  clausesList.querySelectorAll(".save-clause-btn").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      try {
        await apiFetch("/api/clauses", "POST", {
          user_id: userId,
          category: btn.dataset.category,
          title: btn.dataset.title,
          clause_text: btn.dataset.text,
        });
        btn.textContent = "✓ Saved";
        btn.style.color = "var(--green)";
      } catch (err) {
        btn.textContent = "Failed";
      }
    });
  });

  // Missing protections
  const missingList = document.getElementById("missingList");
  const missingSection = document.getElementById("missingSection");
  if (analysis.missing_protections?.length) {
    missingList.innerHTML = analysis.missing_protections.map(item => `
      <div class="missing-item">
        <div class="missing-title">+ ${escHtml(item.title)}</div>
        <div class="missing-why">${escHtml(item.why_it_matters)}</div>
        ${item.suggested_clause ? `
          <div class="missing-clause">${escHtml(item.suggested_clause)}
            <br><button class="copy-btn" style="margin-top:6px" data-text="${escAttr(item.suggested_clause)}">Copy clause</button>
          </div>
        ` : ""}
      </div>
    `).join("");
    missingSection.classList.remove("hidden");
    // Copy buttons in missing
    missingList.querySelectorAll(".copy-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        navigator.clipboard.writeText(btn.dataset.text).then(() => {
          btn.textContent = "✓ Copied!";
          setTimeout(() => { btn.textContent = "Copy clause"; }, 2000);
        });
      });
    });
  } else {
    missingSection.classList.add("hidden");
  }

  // Negotiation tips
  const tipsList = document.getElementById("tipsList");
  const tipsSection = document.getElementById("tipsSection");
  if (analysis.negotiation_tips?.length) {
    tipsList.innerHTML = analysis.negotiation_tips.map(tip => `<li>${escHtml(tip)}</li>`).join("");
    tipsSection.classList.remove("hidden");
  } else {
    tipsSection.classList.add("hidden");
  }
}

function exportReport() {
  if (!currentAnalysis) return;

  const html = buildReportHtml(currentAnalysis);
  const win = window.open("", "_blank");
  win.document.write(html);
  win.document.close();
  win.focus();
  setTimeout(() => win.print(), 500);
}

function buildReportHtml(analysis) {
  const score = analysis.risk_score || 0;
  const color = score <= 3 ? "#22c55e" : score <= 6 ? "#f59e0b" : "#ef4444";
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>ClauseGuard Report</title>
  <style>
    body { font-family: -apple-system, sans-serif; color: #1a1a1a; max-width: 800px; margin: 40px auto; padding: 0 20px; }
    h1 { color: #6366f1; } h2 { margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .risk { font-size: 2em; font-weight: 800; color: ${color}; }
    .disclaimer { background: #fffbeb; border: 1px solid #f59e0b; padding: 10px; border-radius: 6px; font-size: 12px; color: #92400e; margin: 20px 0; }
    .clause { border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; margin: 8px 0; }
    .red { border-left: 4px solid #ef4444; } .yellow { border-left: 4px solid #f59e0b; } .green { border-left: 4px solid #22c55e; }
    .flag { background: #fef2f2; padding: 10px; border-radius: 6px; margin: 6px 0; }
    footer { margin-top: 40px; font-size: 11px; color: #9ca3af; border-top: 1px solid #eee; padding-top: 12px; }
  </style></head><body>
  <h1>ClauseGuard Contract Analysis</h1>
  <p>Generated ${new Date().toLocaleDateString()} · <span class="risk">${score}/10</span> ${analysis.risk_label}</p>
  <div class="disclaimer">${analysis.disclaimer}</div>
  <h2>Summary</h2><p>${analysis.plain_english_summary}</p>
  ${analysis.red_flags?.length ? `<h2>Red Flags</h2>${analysis.red_flags.map(f => `<div class="flag"><strong>${f.title}</strong><br>${f.explanation}</div>`).join("")}` : ""}
  <h2>Clause Analysis</h2>
  ${(analysis.clauses || []).map(c => `<div class="clause ${c.risk_level}"><strong>${c.category.toUpperCase()} — ${c.title}</strong><br><em>"${c.original_text}"</em><br>${c.explanation}${c.concern ? `<br><strong>⚠ Concern:</strong> ${c.concern}` : ""}${c.suggested_change ? `<br><strong>Suggested change:</strong> ${c.suggested_change}` : ""}</div>`).join("")}
  ${analysis.missing_protections?.length ? `<h2>Missing Protections</h2>${analysis.missing_protections.map(m => `<div class="clause yellow"><strong>+ ${m.title}</strong><br>${m.why_it_matters}${m.suggested_clause ? `<br><em>Suggested: ${m.suggested_clause}</em>` : ""}</div>`).join("")}` : ""}
  ${analysis.negotiation_tips?.length ? `<h2>Negotiation Tips</h2><ol>${analysis.negotiation_tips.map(t => `<li>${t}</li>`).join("")}</ol>` : ""}
  <footer>Generated by ClauseGuard · Not legal advice · Consult a qualified attorney before signing any contract</footer>
  </body></html>`;
}

// ─── Compare tab ──────────────────────────────────────────────────────────────

function setupCompareTab() {
  document.getElementById("upgradeFromCompare").addEventListener("click", openUpgrade);
  document.getElementById("compareBtn")?.addEventListener("click", runCompare);
}

async function runCompare() {
  const old = document.getElementById("compareOld").value.trim();
  const newV = document.getElementById("compareNew").value.trim();
  if (!old || !newV) { alert("Please paste both contract versions."); return; }

  const btn = document.getElementById("compareBtn");
  btn.textContent = "Comparing...";
  btn.disabled = true;

  try {
    const data = await apiFetch("/api/compare", "POST", {
      user_id: userId,
      contract_text_old: old,
      contract_text_new: newV,
    });

    const resultsDiv = document.getElementById("compareResults");
    resultsDiv.innerHTML = `
      <div style="margin: 12px 0; padding: 10px 12px; background: var(--bg-card); border-radius: var(--radius); font-size: 12px;">
        <strong>Overall:</strong> ${escHtml(data.overall_assessment)}
        <span style="margin-left: 8px; font-size: 11px; color: ${data.risk_change === 'improved' ? 'var(--green)' : data.risk_change === 'worsened' ? 'var(--red)' : 'var(--text-muted)'}">
          ${data.risk_change === 'improved' ? '↓ Risk improved' : data.risk_change === 'worsened' ? '↑ Risk worsened' : '→ Unchanged'}
        </span>
      </div>
      ${(data.changes || []).map(c => `
        <div class="change-item ${c.impact}">
          <div class="change-type">${c.type} · ${c.category}</div>
          <div class="change-title">${escHtml(c.title)}</div>
          <div class="change-explanation">${escHtml(c.explanation)}</div>
        </div>
      `).join("")}
    `;
  } catch (e) {
    alert("Comparison failed. Please try again.");
  } finally {
    btn.textContent = "Compare Versions";
    btn.disabled = false;
  }
}

// ─── Library tab ──────────────────────────────────────────────────────────────

function setupLibraryTab() {
  document.getElementById("upgradeFromLibrary").addEventListener("click", openUpgrade);
}

async function loadLibrary() {
  const container = document.getElementById("clauseLibraryList");
  container.innerHTML = '<p style="color:var(--text-muted);font-size:12px;text-align:center;padding:20px">Loading...</p>';

  try {
    const data = await apiFetch(`/api/clauses?user_id=${userId}`);
    if (!data.clauses?.length) {
      container.innerHTML = '<p style="color:var(--text-muted);font-size:12px;text-align:center;padding:20px">No saved clauses yet. Analyze a contract and save fair clauses to your library.</p>';
      return;
    }
    container.innerHTML = data.clauses.map(clause => `
      <div class="library-item">
        <div class="library-item-header">
          <span class="library-title">${escHtml(clause.title)}</span>
          <span class="library-category">${escHtml(clause.category)}</span>
        </div>
        <div class="library-text">${escHtml(clause.clause_text)}</div>
        <button class="copy-btn" style="margin-top:6px" data-text="${escAttr(clause.clause_text)}">Copy</button>
      </div>
    `).join("");

    container.querySelectorAll(".copy-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        navigator.clipboard.writeText(btn.dataset.text).then(() => {
          btn.textContent = "✓ Copied!";
          setTimeout(() => { btn.textContent = "Copy"; }, 2000);
        });
      });
    });
  } catch (e) {
    container.innerHTML = '<p style="color:var(--red);font-size:12px;text-align:center;padding:20px">Failed to load library.</p>';
  }
}

// ─── Upgrade ──────────────────────────────────────────────────────────────────

function openUpgrade() {
  // Open the options page — the Stripe checkout button lives there
  chrome.tabs.create({ url: chrome.runtime.getURL("options/options.html") });
}

// ─── API helper ───────────────────────────────────────────────────────────────

async function apiFetch(path, method = "GET", body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API_URL}${path}`, opts);
  const data = await res.json();
  if (!res.ok && !data.upgrade_required) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ─── Utils ────────────────────────────────────────────────────────────────────

function escHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escAttr(str) {
  if (!str) return "";
  return String(str).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
