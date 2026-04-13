/**
 * InvoiceGuard — Gmail Content Script
 *
 * Injects a "Track Invoice" button into Gmail email views.
 * When clicked, extracts email text and sends to API for AI parsing.
 * Shows a slide-out panel with editable fields for confirmation.
 */

const API_BASE = "https://invoiceguard-api.mini-on-ai.workers.dev";

let currentOverlay = null;
let userId = null;

// ─── Init ────────────────────────────────────────────────────────────────────

async function init() {
  // Get user ID from background
  const response = await chrome.runtime.sendMessage({ type: "GET_USER_ID" });
  userId = response?.userId;

  if (!userId) {
    console.warn("[InvoiceGuard] No user ID found. Extension not registered.");
    return;
  }

  // Wait for Gmail to fully load, then observe
  if (document.readyState === "complete") {
    startObserver();
  } else {
    window.addEventListener("load", startObserver);
  }
}

// ─── DOM Observer ────────────────────────────────────────────────────────────

function startObserver() {
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
        tryInjectButton();
      }
    }
  });

  observer.observe(document.body, { childList: true, subtree: true });

  // Also try immediately
  tryInjectButton();
}

/**
 * Look for an open email and inject the Track Invoice button.
 * Gmail renders email actions in a toolbar area — we find it and append our button.
 */
function tryInjectButton() {
  // Skip if overlay is open
  if (currentOverlay) return;

  // Find email action bar (the row with reply/forward/etc buttons)
  // Gmail uses role="listitem" for individual emails in a thread
  // The action bar is typically in elements with [data-tooltip] buttons
  const emailHeaders = document.querySelectorAll("div.ha > div.hP"); // Subject line container
  if (emailHeaders.length === 0) return;

  // Check if we already injected
  if (document.querySelector(".ig-track-btn")) return;

  // Find the toolbar area near the top of the email
  // Gmail's email toolbar contains buttons like archive, delete, etc.
  const toolbars = document.querySelectorAll("div[role='toolbar']");
  if (toolbars.length === 0) return;

  // Use the last toolbar (usually the one in the email view)
  const toolbar = toolbars[toolbars.length - 1];

  // Don't inject if already there
  if (toolbar.querySelector(".ig-track-btn")) return;

  const btn = document.createElement("button");
  btn.className = "ig-track-btn";
  btn.innerHTML = "📋 Track Invoice";
  btn.addEventListener("click", onTrackClick);
  toolbar.appendChild(btn);
}

// ─── Track Button Click ──────────────────────────────────────────────────────

async function onTrackClick(e) {
  const btn = e.currentTarget;
  btn.className = "ig-track-btn ig-track-btn--loading";
  btn.innerHTML = "⏳ Extracting...";

  try {
    // Extract email data from the DOM
    const emailData = extractEmailFromDOM();

    if (!emailData.body || emailData.body.length < 10) {
      btn.className = "ig-track-btn";
      btn.innerHTML = "📋 Track Invoice";
      alert("Could not extract email content. Please try opening the email fully.");
      return;
    }

    // Call parse API
    const res = await fetch(`${API_BASE}/api/parse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        email_text: emailData.body,
        email_subject: emailData.subject,
        sender_email: emailData.senderEmail,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: "Parse failed" }));
      throw new Error(err.error || "Parse failed");
    }

    const parsed = await res.json();

    // Show overlay with pre-filled fields
    showOverlay(parsed, emailData);

    btn.className = "ig-track-btn ig-track-btn--done";
    btn.innerHTML = "✓ Tracked";
  } catch (err) {
    console.error("[InvoiceGuard] Parse error:", err);
    btn.className = "ig-track-btn";
    btn.innerHTML = "📋 Track Invoice";

    // Show overlay with empty fields for manual entry
    showOverlay({}, extractEmailFromDOM());
  }
}

// ─── Email DOM Extraction ────────────────────────────────────────────────────

function extractEmailFromDOM() {
  const result = { subject: "", senderEmail: "", senderName: "", body: "", date: "" };

  // Subject: Gmail uses h2.hP or div.hP for the subject
  const subjectEl = document.querySelector("h2.hP") || document.querySelector("div.hP");
  if (subjectEl) result.subject = subjectEl.textContent.trim();

  // Sender: look for the email address in the sender span
  // Gmail shows sender info in elements with class "gD" (sender name) and email in "go" or data-hovercard-id
  const senderEl = document.querySelector("span.gD[email]") || document.querySelector("span.go");
  if (senderEl) {
    result.senderEmail = senderEl.getAttribute("email") || "";
    result.senderName = senderEl.getAttribute("name") || senderEl.textContent.trim();
  }

  // Also try data-hovercard-id which contains the email
  if (!result.senderEmail) {
    const hovercard = document.querySelector("[data-hovercard-id]");
    if (hovercard) result.senderEmail = hovercard.getAttribute("data-hovercard-id");
  }

  // Date: typically in a span with title containing the full date
  const dateEl = document.querySelector("span.g3");
  if (dateEl) result.date = dateEl.getAttribute("title") || dateEl.textContent.trim();

  // Body: get the email body text
  // Gmail renders email body in div.a3s (message body container)
  const bodyEls = document.querySelectorAll("div.a3s.aiL, div.a3s");
  const bodyParts = [];
  bodyEls.forEach((el) => {
    bodyParts.push(el.innerText);
  });
  result.body = bodyParts.join("\n\n").trim();

  // Fallback: try broader selector
  if (!result.body) {
    const msgBody = document.querySelector("div[data-message-id] div.ii");
    if (msgBody) result.body = msgBody.innerText.trim();
  }

  return result;
}

// ─── Extraction Overlay ──────────────────────────────────────────────────────

function showOverlay(parsed, emailData) {
  // Remove existing overlay
  closeOverlay();

  const overlay = document.createElement("div");
  overlay.className = "ig-overlay";

  const confidence = parsed.confidence || "low";

  overlay.innerHTML = `
    <div class="ig-overlay-header">
      <h3>📋 Track Invoice</h3>
      <button class="ig-overlay-close" id="igClose">×</button>
    </div>
    <div class="ig-overlay-body">
      <div class="ig-status ig-status--success" style="display:${parsed.client_name ? 'block' : 'none'}">
        AI extracted fields below <span class="ig-confidence ig-confidence--${confidence}">${confidence}</span>
      </div>

      <div class="ig-field">
        <label>Client name</label>
        <input type="text" id="igClientName" value="${escHtml(parsed.client_name || emailData.senderName || '')}" placeholder="Acme Corp">
      </div>
      <div class="ig-field">
        <label>Client email</label>
        <input type="email" id="igClientEmail" value="${escHtml(parsed.client_email || emailData.senderEmail || '')}" placeholder="client@example.com">
      </div>
      <div class="ig-field">
        <label>Amount</label>
        <div style="display:flex;gap:8px">
          <input type="number" id="igAmount" value="${parsed.amount_cents ? (parsed.amount_cents / 100).toFixed(2) : ''}" placeholder="1500.00" step="0.01" style="flex:1">
          <select id="igCurrency" style="width:80px">
            ${["USD","EUR","GBP","CAD","AUD"].map(c => `<option value="${c}" ${c === (parsed.currency || "USD") ? "selected" : ""}>${c}</option>`).join("")}
          </select>
        </div>
      </div>
      <div class="ig-field">
        <label>Invoice date</label>
        <input type="date" id="igInvoiceDate" value="${escHtml(parsed.invoice_date || '')}">
      </div>
      <div class="ig-field">
        <label>Due date</label>
        <input type="date" id="igDueDate" value="${escHtml(parsed.due_date || '')}">
      </div>
      <div class="ig-field">
        <label>Notes (optional)</label>
        <input type="text" id="igNotes" value="" placeholder="Project name, PO number, etc.">
      </div>
    </div>
    <div class="ig-overlay-footer">
      <button class="ig-btn-save" id="igSave">Save & Track</button>
      <button class="ig-btn-cancel" id="igCancel">Cancel</button>
    </div>
  `;

  document.body.appendChild(overlay);
  currentOverlay = overlay;

  // Event listeners
  overlay.querySelector("#igClose").addEventListener("click", closeOverlay);
  overlay.querySelector("#igCancel").addEventListener("click", closeOverlay);
  overlay.querySelector("#igSave").addEventListener("click", () => saveInvoice(emailData));
}

async function saveInvoice(emailData) {
  const saveBtn = document.querySelector("#igSave");
  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";
  }

  const clientName = document.querySelector("#igClientName")?.value.trim();
  const amountStr = document.querySelector("#igAmount")?.value;
  const amount = parseFloat(amountStr);

  if (!clientName) {
    showOverlayError("Client name is required.");
    if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = "Save & Track"; }
    return;
  }
  if (!amountStr || isNaN(amount) || amount <= 0) {
    showOverlayError("Please enter a valid amount.");
    if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = "Save & Track"; }
    return;
  }

  const payload = {
    user_id: userId,
    client_name: clientName,
    client_email: document.querySelector("#igClientEmail")?.value.trim() || null,
    amount_cents: Math.round(amount * 100),
    currency: document.querySelector("#igCurrency")?.value || "USD",
    invoice_date: document.querySelector("#igInvoiceDate")?.value || null,
    due_date: document.querySelector("#igDueDate")?.value || null,
    email_subject: emailData.subject || null,
    email_snippet: (emailData.body || "").slice(0, 200) || null,
    notes: document.querySelector("#igNotes")?.value.trim() || null,
  };

  try {
    const res = await fetch(`${API_BASE}/api/invoices`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      showOverlayError(data.error || "Failed to save invoice.");
      if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = "Save & Track"; }
      return;
    }

    // Success — show confirmation briefly then close
    showOverlaySuccess("Invoice tracked! Check your dashboard.");
    chrome.runtime.sendMessage({ type: "REFRESH_BADGE" });

    setTimeout(closeOverlay, 1500);
  } catch (err) {
    console.error("[InvoiceGuard] Save error:", err);
    showOverlayError("Network error. Please try again.");
    if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = "Save & Track"; }
  }
}

function closeOverlay() {
  if (currentOverlay) {
    currentOverlay.remove();
    currentOverlay = null;
  }

  // Reset button
  const btn = document.querySelector(".ig-track-btn--done");
  if (btn) {
    btn.className = "ig-track-btn";
    btn.innerHTML = "📋 Track Invoice";
  }
}

function showOverlayError(msg) {
  const body = currentOverlay?.querySelector(".ig-overlay-body");
  if (!body) return;
  const existing = body.querySelector(".ig-status--error");
  if (existing) existing.remove();
  const el = document.createElement("div");
  el.className = "ig-status ig-status--error";
  el.textContent = msg;
  body.insertBefore(el, body.firstChild);
}

function showOverlaySuccess(msg) {
  const body = currentOverlay?.querySelector(".ig-overlay-body");
  if (!body) return;
  body.innerHTML = `<div class="ig-status ig-status--success" style="margin-top:40%;text-align:center;font-size:16px">✓ ${escHtml(msg)}</div>`;
}

function escHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// ─── Start ───────────────────────────────────────────────────────────────────

init();
