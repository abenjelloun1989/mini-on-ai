/**
 * InvoiceGuard — Popup Dashboard
 *
 * Shows invoice list, summary, detail view, and reminder generation.
 */

const API_BASE = "https://invoiceguard-api.kirozdormu.workers.dev";

let userId = null;
let allInvoices = [];
let currentFilter = "all";
let currentInvoice = null;

// ─── Init ────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  const { userId: uid } = await chrome.storage.local.get("userId");
  userId = uid;

  if (!userId) {
    document.getElementById("loading").textContent = "Extension not registered. Please reinstall.";
    return;
  }

  // Load user info
  loadUser();

  // Load invoices
  loadInvoices();

  // Filter tabs
  document.querySelectorAll(".filter-tab").forEach(tab => {
    tab.addEventListener("click", (e) => {
      currentFilter = e.target.dataset.filter;
      document.querySelectorAll(".filter-tab").forEach(t => t.classList.remove("active"));
      e.target.classList.add("active");
      renderInvoices();
    });
  });

  // Settings button
  document.getElementById("settingsBtn").addEventListener("click", () => {
    chrome.runtime.openOptionsPage();
  });

  // Detail panel back
  document.getElementById("detailBack").addEventListener("click", hideDetail);

  // Mark paid
  document.getElementById("markPaidBtn").addEventListener("click", markPaid);

  // Delete
  document.getElementById("deleteBtn").addEventListener("click", deleteInvoice);

  // Reminder tone buttons
  document.querySelectorAll(".btn-tone").forEach(btn => {
    btn.addEventListener("click", (e) => generateReminder(e.currentTarget.dataset.tone));
  });

  // Upgrade
  document.getElementById("upgradeBtn")?.addEventListener("click", upgrade);
});

// ─── Data Loading ────────────────────────────────────────────────────────────

async function loadUser() {
  try {
    const res = await fetch(`${API_BASE}/api/usage?user_id=${userId}`);
    if (!res.ok) return;
    const data = await res.json();

    const badge = document.getElementById("tierBadge");
    if (data.tier === "pro") {
      badge.textContent = "Pro";
      badge.classList.add("tier-badge--pro");
    } else {
      badge.textContent = "Free";
    }
  } catch (e) {
    console.error("Load user error:", e);
  }
}

async function loadInvoices() {
  const loading = document.getElementById("loading");
  try {
    const res = await fetch(`${API_BASE}/api/invoices?user_id=${userId}`);
    if (!res.ok) {
      loading.textContent = "Failed to load invoices.";
      return;
    }

    const data = await res.json();
    allInvoices = data.invoices || [];

    // Update summary
    const summary = data.summary || {};
    document.getElementById("totalOutstanding").textContent = formatAmount(summary.total_outstanding_cents || 0);
    document.getElementById("overdueCount").textContent = summary.overdue || 0;
    document.getElementById("activeCount").textContent = summary.active || 0;

    // Show upgrade banner if at limit
    const activeCount = summary.active || 0;
    const { tier } = await chrome.storage.local.get("tier");
    if (tier !== "pro" && activeCount >= 5) {
      document.getElementById("upgradeBanner").style.display = "block";
    }

    loading.style.display = "none";
    renderInvoices();
  } catch (e) {
    console.error("Load invoices error:", e);
    loading.textContent = "Network error. Please try again.";
  }
}

// ─── Rendering ───────────────────────────────────────────────────────────────

function renderInvoices() {
  const list = document.getElementById("invoiceList");
  const empty = document.getElementById("emptyState");

  // Clear existing rows (keep loading and empty)
  list.querySelectorAll(".invoice-row").forEach(r => r.remove());

  const filtered = currentFilter === "all"
    ? allInvoices
    : allInvoices.filter(i => i.status === currentFilter);

  if (filtered.length === 0) {
    empty.style.display = "block";
    if (currentFilter !== "all") {
      empty.querySelector("p").textContent = `No ${currentFilter} invoices.`;
    }
    return;
  }

  empty.style.display = "none";

  filtered.forEach(inv => {
    const row = document.createElement("div");
    row.className = "invoice-row";
    row.dataset.id = inv.id;

    const isOverdue = inv.status === "overdue";
    const amountClass = isOverdue ? " invoice-amount--overdue" : "";

    row.innerHTML = `
      <div class="invoice-status invoice-status--${inv.status}"></div>
      <div class="invoice-info">
        <div class="invoice-client">${escHtml(inv.client_name)}</div>
        <div class="invoice-meta">${inv.due_date ? `Due ${inv.due_date}` : "No due date"} · ${inv.status}</div>
      </div>
      <div class="invoice-amount${amountClass}">${formatAmount(inv.amount_cents, inv.currency)}</div>
    `;

    row.addEventListener("click", () => showDetail(inv));
    list.appendChild(row);
  });
}

// ─── Detail Panel ────────────────────────────────────────────────────────────

function showDetail(inv) {
  currentInvoice = inv;
  const panel = document.getElementById("detailPanel");
  const body = document.getElementById("detailBody");

  const daysOverdue = inv.due_date && inv.status === "overdue"
    ? Math.max(0, Math.floor((Date.now() - new Date(inv.due_date).getTime()) / 86400000))
    : 0;

  body.innerHTML = `
    <div class="detail-field">
      <div class="detail-field-value detail-field-value--large ${inv.status === 'overdue' ? 'detail-field-value--danger' : ''}">${formatAmount(inv.amount_cents, inv.currency)}</div>
      <div class="detail-field-value" style="margin-top:2px">${escHtml(inv.client_name)}${inv.client_email ? ` <span style="color:var(--text-muted);font-size:11px">${escHtml(inv.client_email)}</span>` : ""}</div>
    </div>
    <div class="detail-fields-grid">
      <div class="detail-field">
        <div class="detail-field-label">Status</div>
        <div class="detail-field-value ${inv.status === 'overdue' ? 'detail-field-value--danger' : inv.status === 'paid' ? 'detail-field-value--success' : ''}">${inv.status.toUpperCase()}${daysOverdue > 0 ? ` · ${daysOverdue}d` : ""}</div>
      </div>
      <div class="detail-field">
        <div class="detail-field-label">Reminders</div>
        <div class="detail-field-value">${inv.reminders_sent || 0} sent</div>
      </div>
      <div class="detail-field">
        <div class="detail-field-label">Invoice date</div>
        <div class="detail-field-value">${inv.invoice_date || "—"}</div>
      </div>
      <div class="detail-field">
        <div class="detail-field-label">Due date</div>
        <div class="detail-field-value">${inv.due_date || "—"}</div>
      </div>
    </div>
    ${inv.notes ? `<div class="detail-field"><div class="detail-field-label">Notes</div><div class="detail-field-value">${escHtml(inv.notes)}</div></div>` : ""}
    ${inv.email_subject ? `<div class="detail-field" style="color:var(--text-muted);font-size:11px">${escHtml(inv.email_subject)}</div>` : ""}
  `;

  // Reset reminder result
  document.getElementById("remindResult").style.display = "none";

  // Show/hide mark paid based on status
  document.getElementById("markPaidBtn").style.display = (inv.status === "paid" || inv.status === "cancelled") ? "none" : "inline-flex";

  panel.style.display = "block";
  panel.scrollTop = 0;
}

function hideDetail() {
  document.getElementById("detailPanel").style.display = "none";
  currentInvoice = null;
}

// ─── Actions ─────────────────────────────────────────────────────────────────

async function markPaid() {
  if (!currentInvoice) return;
  const btn = document.getElementById("markPaidBtn");
  btn.textContent = "Saving...";

  try {
    const res = await fetch(`${API_BASE}/api/invoices/${currentInvoice.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, status: "paid" }),
    });

    if (res.ok) {
      currentInvoice.status = "paid";
      // Refresh list
      await loadInvoices();
      hideDetail();
      chrome.runtime.sendMessage({ type: "REFRESH_BADGE" });
    }
  } catch (e) {
    console.error("Mark paid error:", e);
  }
  btn.textContent = "✓ Paid";
}

async function deleteInvoice() {
  if (!currentInvoice) return;
  if (!confirm(`Delete invoice from ${currentInvoice.client_name}?`)) return;

  try {
    await fetch(`${API_BASE}/api/invoices/${currentInvoice.id}?user_id=${userId}`, {
      method: "DELETE",
    });
    await loadInvoices();
    hideDetail();
    chrome.runtime.sendMessage({ type: "REFRESH_BADGE" });
  } catch (e) {
    console.error("Delete error:", e);
  }
}

async function generateReminder(tone) {
  if (!currentInvoice) return;

  const resultEl = document.getElementById("remindResult");
  resultEl.style.display = "block";
  resultEl.innerHTML = '<div style="text-align:center;padding:12px;color:var(--text-muted)">Generating reminder...</div>';

  try {
    const res = await fetch(`${API_BASE}/api/remind`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        invoice_id: currentInvoice.id,
        tone,
      }),
    });

    const rawText = await res.text();

    if (!res.ok) {
      let err = {};
      try { err = JSON.parse(rawText); } catch {}
      resultEl.innerHTML = `<div style="color:var(--danger)">${escHtml(err.error || "Failed to generate reminder.")}</div>`;
      return;
    }

    let data;
    try { data = JSON.parse(rawText); } catch {
      resultEl.innerHTML = `<div style="color:var(--danger)">Bad response from server.</div>`;
      return;
    }

    resultEl.innerHTML = `
      <div class="remind-subject">${escHtml(data.subject)}</div>
      <div class="remind-body">${escHtml(data.body)}</div>
      <div class="remind-actions">
        <button class="btn-send-reminder" id="sendReminderBtn">Open in Gmail</button>
        <button class="btn-copy-reminder" id="copyReminderBtn">📋 Copy</button>
      </div>
      ${data.is_template ? '<div style="font-size:10px;color:var(--text-muted);margin-top:8px">Basic template — upgrade to Pro for AI-personalized reminders</div>' : ''}
    `;
    resultEl.scrollIntoView({ behavior: "smooth", block: "nearest" });

    // Open in Gmail compose
    document.getElementById("sendReminderBtn").addEventListener("click", () => {
      const mailto = `https://mail.google.com/mail/?view=cm&to=${encodeURIComponent(currentInvoice.client_email || "")}&su=${encodeURIComponent(data.subject)}&body=${encodeURIComponent(data.body)}`;
      chrome.tabs.create({ url: mailto });
    });

    // Copy to clipboard
    document.getElementById("copyReminderBtn").addEventListener("click", async () => {
      await navigator.clipboard.writeText(`Subject: ${data.subject}\n\n${data.body}`);
      document.getElementById("copyReminderBtn").textContent = "✓ Copied!";
      setTimeout(() => {
        const btn = document.getElementById("copyReminderBtn");
        if (btn) btn.textContent = "📋 Copy";
      }, 2000);
    });

    // Update reminder count locally
    if (!data.is_template) {
      currentInvoice.reminders_sent = (currentInvoice.reminders_sent || 0) + 1;
    }
  } catch (e) {
    console.error("Remind error:", e);
    resultEl.innerHTML = '<div style="color:var(--danger)">Network error. Please try again.</div>';
  }
}

async function upgrade() {
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

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatAmount(cents, currency = "USD") {
  const symbols = { USD: "$", EUR: "€", GBP: "£", CAD: "CA$", AUD: "A$" };
  const symbol = symbols[currency] || `${currency} `;
  return `${symbol}${(cents / 100).toFixed(2)}`;
}

function escHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
