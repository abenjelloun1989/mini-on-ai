const API_URL = "https://clauseguard-api.kirozdormu.workers.dev";

let userId = null;
let userTier = "free";
let currentAnalysis = null;

// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  // Dark/light mode toggle — provided by shared.js
  initDarkMode("cg-theme", "darkModeToggle");

  // Full-page mode when opened as a tab
  if (window.outerWidth > 600) {
    document.body.classList.add("full-page");
    const expandBtn = document.getElementById("expandBtn");
    if (expandBtn) expandBtn.style.display = "none";
  }
  document.getElementById("expandBtn")?.addEventListener("click", () => {
    chrome.tabs.create({ url: chrome.runtime.getURL("popup/popup.html") });
  });

  await loadUser();
  _initTabs();
  setupAnalyzeTab();
  setupCompareTab();
  setupLibraryTab();
  setupAccountTab();
  await restoreState(); // restore contract text + results from previous popup session
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
    updateTierBadge(data.tier);

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
  // Hide "Pro" chips on tab labels once the user already has Pro access
  document.querySelectorAll(".tab .pro-chip").forEach(chip => {
    chip.classList.toggle("hidden", isPro);
  });
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────

function _initTabs() {
  // Use shared setupTabs() from shared.js with extension-specific callbacks
  setupTabs((tabName) => {
    if (tabName === "library" && userTier === "pro") loadLibrary();
    if (tabName === "account") loadAccountTab();
  });
}

// ─── Analyze tab ──────────────────────────────────────────────────────────────

function setupAnalyzeTab() {
  const textarea = document.getElementById("contractText");
  const analyzeBtn = document.getElementById("analyzeBtn");

  // Enable analyze button + update char count + persist on input
  textarea.addEventListener("input", () => {
    const len = textarea.value.trim().length;
    const hasText = len >= 50;
    analyzeBtn.disabled = !hasText || (userTier !== "pro" && document.getElementById("upgradeBanner").classList.contains("hidden") === false);
    const counter = document.getElementById("charCount");
    if (counter) {
      counter.textContent = `${len.toLocaleString()} / 15,000`;
      counter.className = `char-count ${len >= 50 ? "ready" : len > 0 ? "typing" : ""}`;
    }
    scheduleStateSave();
  });

  // Ctrl+Enter / Cmd+Enter to submit
  textarea.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !analyzeBtn.disabled) {
      e.preventDefault();
      runAnalysis();
    }
  });

  analyzeBtn.addEventListener("click", runAnalysis);
  document.getElementById("newAnalysisBtn").addEventListener("click", showInputState);
  document.getElementById("upgradeFromBanner").addEventListener("click", openUpgrade);
  document.getElementById("exportBtn").addEventListener("click", exportReport);

  // Analyze current page
  document.getElementById("analyzeCurrentPage").addEventListener("click", analyzeCurrentPage);

  // PDF upload (button)
  document.getElementById("pdfUpload").addEventListener("change", handlePdfUpload);

  // Drag-and-drop PDF onto textarea
  textarea.addEventListener("dragover", (e) => {
    e.preventDefault();
    textarea.classList.add("drag-over");
  });
  textarea.addEventListener("dragleave", () => {
    textarea.classList.remove("drag-over");
  });
  textarea.addEventListener("drop", async (e) => {
    e.preventDefault();
    textarea.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (!file) return;
    if (file.type === "application/pdf") {
      await handlePdfUpload({ target: { files: [file] } });
    } else {
      alert("Only PDF files are supported via drag-and-drop. Paste text directly for other formats.");
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

function isFullPage() {
  return document.body.classList.contains("full-page");
}

// ─── State persistence (survives popup close/reopen within session) ───────────

let _saveTimer = null;

function scheduleStateSave() {
  clearTimeout(_saveTimer);
  _saveTimer = setTimeout(persistState, 400);
}

async function persistState() {
  try {
    const textarea  = document.getElementById("contractText");
    const typeSelect = document.getElementById("contractType");
    const isResults  = !document.getElementById("resultsState").classList.contains("hidden");
    await chrome.storage.session.set({
      contractText:  textarea?.value  || "",
      contractType:  typeSelect?.value || "general",
      currentView:   isResults ? "results" : "input",
      savedAnalysis: isResults ? currentAnalysis : null,
    });
  } catch (e) {
    // Non-fatal — session storage may be unavailable
  }
}

async function restoreState() {
  try {
    const saved = await chrome.storage.session.get([
      "contractText", "contractType", "currentView", "savedAnalysis",
    ]);
    if (saved.contractText) {
      const textarea = document.getElementById("contractText");
      textarea.value = saved.contractText;
      textarea.dispatchEvent(new Event("input")); // re-enable analyze button
    }
    if (saved.contractType) {
      document.getElementById("contractType").value = saved.contractType;
    }
    if (saved.currentView === "results" && saved.savedAnalysis) {
      currentAnalysis = saved.savedAnalysis;
      showResults(saved.savedAnalysis);
    }
  } catch (e) {
    console.warn("State restore failed:", e);
  }
}

function showInputState() {
  document.getElementById("inputState").classList.remove("hidden");
  document.getElementById("loadingState").classList.add("hidden");
  document.getElementById("resultsState").classList.add("hidden");
  persistState(); // save "input" view so reopen lands here
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
      copyText(btn, btn.dataset.text, "Copy suggestion");
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
      btn.addEventListener("click", () => copyText(btn, btn.dataset.text, "Copy clause"));
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

  // Persist so reopening the popup restores this result
  persistState();
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

    const changes = data.changes || [];
    const favorable = changes.filter(c => c.impact === "favorable").length;
    const unfavorable = changes.filter(c => c.impact === "unfavorable").length;
    const changeSummary = changes.length === 0
      ? "No changes detected"
      : `${changes.length} change${changes.length !== 1 ? "s" : ""} — ${favorable} favorable, ${unfavorable} unfavorable`;

    const resultsDiv = document.getElementById("compareResults");
    resultsDiv.innerHTML = `
      <div style="margin: 12px 0; padding: 10px 12px; background: var(--bg-card); border-radius: var(--radius); font-size: 12px;">
        <div style="margin-bottom:6px;font-size:11px;color:var(--text-muted);font-weight:600;letter-spacing:0.5px;text-transform:uppercase;">${escHtml(changeSummary)}</div>
        <strong>Overall:</strong> ${escHtml(data.overall_assessment)}
        <span style="margin-left: 8px; font-size: 11px; color: ${data.risk_change === 'improved' ? 'var(--green)' : data.risk_change === 'worsened' ? 'var(--red)' : 'var(--text-muted)'}">
          ${data.risk_change === 'improved' ? '↓ Risk improved' : data.risk_change === 'worsened' ? '↑ Risk worsened' : '→ Unchanged'}
        </span>
      </div>
      ${changes.length === 0
        ? `<p style="color:var(--text-muted);font-size:12px;text-align:center;padding:16px 0;">No significant changes detected between the two versions.</p>`
        : changes.map(c => `
          <div class="change-item ${escHtml(c.impact)}">
            <div class="change-type">${escHtml(c.type)} · ${escHtml(c.category)}</div>
            <div class="change-title">${escHtml(c.title)}</div>
            <div class="change-explanation">${escHtml(c.explanation)}</div>
          </div>
        `).join("")
      }
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
      // Hide export button when empty
      const exportLibBtn = document.getElementById("exportLibraryBtn");
      if (exportLibBtn) exportLibBtn.classList.add("hidden");
      return;
    }

    // Show export button when there are clauses
    const exportLibBtn = document.getElementById("exportLibraryBtn");
    if (exportLibBtn) {
      exportLibBtn.classList.remove("hidden");
      exportLibBtn.onclick = () => exportLibrary(data.clauses);
    }

    container.innerHTML = data.clauses.map(clause => `
      <div class="library-item" data-clause-id="${escAttr(clause.id)}">
        <div class="library-item-header">
          <span class="library-title">${escHtml(clause.title)}</span>
          <span class="library-category">${escHtml(clause.category)}</span>
          <button class="library-delete-btn" data-id="${escAttr(clause.id)}" title="Delete clause">✕</button>
        </div>
        <div class="library-text">${escHtml(clause.clause_text)}</div>
        ${clause.notes ? `<div class="library-notes">${escHtml(clause.notes)}</div>` : ""}
        <button class="copy-btn" style="margin-top:6px" data-text="${escAttr(clause.clause_text)}">Copy</button>
      </div>
    `).join("");

    container.querySelectorAll(".copy-btn").forEach(btn => {
      btn.addEventListener("click", () => copyText(btn, btn.dataset.text, "Copy"));
    });

    container.querySelectorAll(".library-delete-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const clauseId = btn.dataset.id;
        btn.textContent = "…";
        btn.disabled = true;
        try {
          await apiFetch(`/api/clauses/${clauseId}?user_id=${userId}`, "DELETE");
          // Remove the card from the DOM
          const card = container.querySelector(`[data-clause-id="${clauseId}"]`);
          if (card) card.remove();
          // If library is now empty, reload to show empty state
          if (!container.querySelector(".library-item")) loadLibrary();
        } catch (e) {
          btn.textContent = "✕";
          btn.disabled = false;
          alert("Could not delete clause. Please try again.");
        }
      });
    });
  } catch (e) {
    container.innerHTML = `
      <div style="text-align:center;padding:20px;">
        <p style="color:var(--red);font-size:12px;margin-bottom:8px;">Failed to load library.</p>
        <button class="btn-text" id="retryLibraryBtn" style="font-size:12px;">Try again</button>
      </div>`;
    document.getElementById("retryLibraryBtn").addEventListener("click", loadLibrary);
  }
}

function exportLibrary(clauses) {
  const lines = clauses.map((c, i) => [
    `${i + 1}. ${c.title.toUpperCase()} [${c.category}]`,
    c.clause_text,
    c.notes ? `Note: ${c.notes}` : "",
    "",
  ].filter(Boolean).join("\n")).join("\n---\n\n");

  const content = `CLAUSEGUARD — CLAUSE LIBRARY EXPORT\nExported ${new Date().toLocaleDateString()}\n${"=".repeat(50)}\n\n${lines}`;
  const blob = new Blob([content], { type: "text/plain" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href     = url;
  a.download = `clauseguard-library-${new Date().toISOString().slice(0, 10)}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

// ─── Account tab ──────────────────────────────────────────────────────────────

function setupAccountTab() {
  const redeemBtn = document.getElementById("ltdRedeemBtn");
  const codeInput = document.getElementById("ltdCodeInput");

  redeemBtn.addEventListener("click", redeemLtdCode);
  codeInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") redeemLtdCode();
  });
  // Auto-uppercase as user types
  codeInput.addEventListener("input", () => {
    const pos = codeInput.selectionStart;
    codeInput.value = codeInput.value.toUpperCase();
    codeInput.setSelectionRange(pos, pos);
  });
}

async function loadAccountTab() {
  const planBox = document.getElementById("accountPlanBox");
  const ltdSection = document.getElementById("ltdSection");

  planBox.innerHTML = '<div style="color:var(--text-muted);font-size:12px;text-align:center">Loading…</div>';

  try {
    const data = await apiFetch(`/api/subscription?user_id=${userId}`);
    const isPro = data.tier === "pro";
    const isLtd = data.pro_source === "ltd";
    const hasStripe = !!data.has_subscription;

    // Fetch usage count to show in Pro plan box
    let usageThisMonth = 0;
    try {
      const usageData = await apiFetch(`/api/usage?user_id=${userId}`);
      usageThisMonth = usageData.usage_this_month || 0;
    } catch (_) {}

    if (isPro && isLtd) {
      planBox.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
          <span style="font-size:22px;">⚡</span>
          <div>
            <div style="font-weight:700;font-size:14px;color:var(--text);">Pro Lifetime</div>
            <div style="font-size:11px;color:var(--text-muted);">Paid once · unlimited analyses · forever</div>
          </div>
          <span style="margin-left:auto;background:#1e3a1e;color:var(--green);font-size:10px;font-weight:700;padding:3px 8px;border-radius:20px;white-space:nowrap;">Active</span>
        </div>
        <div style="font-size:12px;color:var(--text-muted);">✓ Unlimited contract analyses<br>✓ Contract comparison<br>✓ PDF export<br>✓ Clause library<br>✓ All future Pro features</div>
        <div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--border);font-size:11px;color:var(--text-muted);">
          This month: <strong style="color:var(--text);">${usageThisMonth} analys${usageThisMonth === 1 ? "is" : "es"}</strong>
        </div>
      `;
      // Hide LTD section — already redeemed
      ltdSection.style.display = "none";
    } else if (isPro && hasStripe) {
      planBox.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
          <span style="font-size:22px;">✦</span>
          <div>
            <div style="font-weight:700;font-size:14px;color:var(--text);">Pro Plan</div>
            <div style="font-size:11px;color:var(--text-muted);">$7/month · unlimited analyses</div>
          </div>
          <span style="margin-left:auto;background:#1e3a1e;color:var(--green);font-size:10px;font-weight:700;padding:3px 8px;border-radius:20px;white-space:nowrap;">Active</span>
        </div>
        <div style="margin-bottom:8px;font-size:11px;color:var(--text-muted);">
          This month: <strong style="color:var(--text);">${usageThisMonth} analys${usageThisMonth === 1 ? "is" : "es"}</strong>
        </div>
        <button id="manageBillingBtn" class="btn-primary" style="width:100%;font-size:12px;">Manage subscription →</button>
      `;
      document.getElementById("manageBillingBtn").addEventListener("click", async () => {
        const btn = document.getElementById("manageBillingBtn");
        btn.textContent = "Opening…";
        btn.disabled = true;
        try {
          const portal = await apiFetch("/api/portal", "POST", { user_id: userId });
          if (portal.portal_url) chrome.tabs.create({ url: portal.portal_url });
          else throw new Error("no url");
        } catch {
          btn.textContent = "Could not open portal — try again";
          btn.disabled = false;
        }
      });
      // Hide LTD section for active Stripe subscribers
      ltdSection.style.display = "none";
    } else {
      // Free user
      planBox.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
          <img src="../icons/icon48.png" width="24" height="24" style="border-radius:4px;flex-shrink:0;" alt="">
          <div>
            <div style="font-weight:700;font-size:14px;color:var(--text);">Free Plan</div>
            <div style="font-size:11px;color:var(--text-muted);">3 analyses per month</div>
          </div>
        </div>
        <button id="upgradeFromAccount" class="btn-primary" style="width:100%;font-size:12px;">Upgrade to Pro — $7/month</button>
      `;
      document.getElementById("upgradeFromAccount").addEventListener("click", openUpgrade);
      ltdSection.style.display = "";
    }
  } catch (e) {
    planBox.innerHTML = '<div style="color:var(--text-muted);font-size:12px;text-align:center">Could not load plan info.</div>';
  }
}

async function redeemLtdCode() {
  const input = document.getElementById("ltdCodeInput");
  const btn   = document.getElementById("ltdRedeemBtn");
  const status = document.getElementById("ltdStatus");

  const code = input.value.trim().toUpperCase();
  if (!code) {
    setLtdStatus("error", "Please enter a code.");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Redeeming…";
  status.textContent = "";

  try {
    const data = await apiFetch("/api/redeem-ltd", "POST", { user_id: userId, code });

    if (data.success) {
      // Update local tier immediately
      userTier = "pro";

      // Update the header badge
      const badge = document.getElementById("tierBadge");
      badge.textContent = "Pro";
      badge.classList.add("pro");

      setLtdStatus("success", "✓ Code redeemed! Your account is now Pro lifetime. Enjoy unlimited analyses.");
      input.value = "";
      input.disabled = true;
      btn.style.display = "none";

      // Refresh usage display and pro gates immediately (no popup restart needed)
      await refreshUsage();
      updateProGates(true);

      // Refresh the plan box to show lifetime state
      await loadAccountTab();
    } else {
      setLtdStatus("error", data.error || "Redemption failed. Please try again.");
      btn.disabled = false;
      btn.textContent = "Redeem";
    }
  } catch (e) {
    const msg = e.message || "";
    if (msg.includes("already been redeemed")) {
      setLtdStatus("error", "This code has already been redeemed by another account.");
    } else if (msg.includes("Invalid code")) {
      setLtdStatus("error", "Code not found. Check for typos and try again.");
    } else {
      setLtdStatus("error", "Could not connect. Check your internet and try again.");
    }
    btn.disabled = false;
    btn.textContent = "Redeem";
  }
}

function setLtdStatus(type, message) {
  const el = document.getElementById("ltdStatus");
  el.textContent = message;
  el.style.color = type === "success" ? "var(--green)" : "var(--red)";
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

// ─── Shared utils (copyText, escHtml, escAttr) provided by shared.js ─────────
