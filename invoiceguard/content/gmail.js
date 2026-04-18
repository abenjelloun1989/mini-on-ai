/**
 * InvoiceGuard — Gmail Content Script
 *
 * Injects a "Track Invoice" button when an email is open.
 * Uses URL change detection + MutationObserver for reliability.
 */

const API_BASE = "https://invoiceguard-api.kirozdormu.workers.dev";

let currentOverlay = null;
let userId = null;
let lastUrl = location.href;
let injecting = false;

// ─── Init ────────────────────────────────────────────────────────────────────

async function init() {
  const response = await chrome.runtime.sendMessage({ type: "GET_USER_ID" });
  userId = response?.userId;
  if (!userId) return;

  // Ensure user is registered (handles case where service worker registration failed)
  try {
    await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
  } catch (_) { /* silent — will retry on next load */ }


  // Watch URL changes (Gmail is a SPA)
  new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      scheduleInject();
    }
  }).observe(document.body, { childList: true, subtree: true });

  // Also observe DOM changes to detect email load
  new MutationObserver(scheduleInject)
    .observe(document.body, { childList: true, subtree: true });

  scheduleInject();
}

let injectTimer = null;
function scheduleInject() {
  clearTimeout(injectTimer);
  injectTimer = setTimeout(tryInjectButton, 600);
}

// ─── Button Injection ────────────────────────────────────────────────────────

function tryInjectButton() {
  if (injecting) return;

  // Only inject when an email is open (URL contains # fragment)
  if (!location.href.includes('#')) return;

  // Don't inject if already present
  if (document.querySelector('.ig-track-btn')) return;

  // Don't inject if overlay is open
  if (currentOverlay) return;

  // Find the email body — most reliable signal that an email is loaded
  const emailBody = document.querySelector('div.a3s.aiL') ||
                    document.querySelector('div.a3s') ||
                    document.querySelector('div[data-message-id]');

  if (!emailBody) return;

  // Find a good place to inject the button
  // Strategy: try multiple known Gmail toolbar/action locations
  const anchor = findInjectionPoint();
  if (!anchor) return;

  injecting = true;

  const btn = document.createElement('button');
  btn.className = 'ig-track-btn';
  btn.innerHTML = '📋 Track Invoice';
  btn.addEventListener('click', onTrackClick);

  anchor.appendChild(btn);
  injecting = false;
}

function findInjectionPoint() {
  // Option 1: reply action buttons area (div.ade contains the reply/forward buttons)
  const ade = document.querySelectorAll('div.ade');
  if (ade.length > 0) return ade[ade.length - 1];

  // Option 2: the email action toolbar with aria buttons
  const toolbars = document.querySelectorAll('div[role="toolbar"]');
  if (toolbars.length > 0) return toolbars[toolbars.length - 1];

  // Option 3: the message header actions area
  const headerActions = document.querySelector('div.hq');
  if (headerActions) return headerActions;

  // Option 4: inject after the email header div
  const emailHeader = document.querySelector('div.ha');
  if (emailHeader) return emailHeader;

  // Option 5: inject a floating button directly
  return null;
}

// ─── Fallback: Floating button ───────────────────────────────────────────────
// If we can't find a toolbar, inject a floating button on the page

function injectFloatingButton() {
  if (document.querySelector('.ig-float-btn')) return;

  const btn = document.createElement('button');
  btn.className = 'ig-float-btn ig-track-btn';
  btn.innerHTML = '📋 Track Invoice';
  btn.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9999;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  `;
  btn.addEventListener('click', onTrackClick);
  document.body.appendChild(btn);
}

// ─── Track Click ─────────────────────────────────────────────────────────────

async function onTrackClick(e) {
  const btn = e.currentTarget;
  btn.classList.add('ig-track-btn--loading');
  btn.innerHTML = '⏳ Extracting...';

  try {
    const emailData = extractEmailFromDOM();

    // Try AI parse if we have body text
    let parsed = {};
    if (emailData.body && emailData.body.length > 20) {
      try {
        const res = await fetch(`${API_BASE}/api/parse`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            email_text: emailData.body,
            email_subject: emailData.subject,
            sender_email: emailData.senderEmail,
          }),
        });
        if (res.ok) parsed = await res.json();
      } catch (_) {
        // Silent — show overlay anyway for manual entry
      }
    }

    showOverlay(parsed, emailData);

    btn.classList.remove('ig-track-btn--loading');
    btn.classList.add('ig-track-btn--done');
    btn.innerHTML = '✓ Tracking...';
  } catch (err) {
    console.error('[InvoiceGuard]', err);
    btn.classList.remove('ig-track-btn--loading');
    btn.innerHTML = '📋 Track Invoice';
    showOverlay({}, extractEmailFromDOM());
  }
}

// ─── DOM Extraction ───────────────────────────────────────────────────────────

function extractEmailFromDOM() {
  const result = { subject: '', senderEmail: '', senderName: '', body: '', date: '' };

  // Subject
  const subjectEl = document.querySelector('h2.hP') ||
                    document.querySelector('[data-legacy-thread-id] h2') ||
                    document.querySelector('.ha h2');
  if (subjectEl) result.subject = subjectEl.textContent.trim();

  // Sender email
  const senderSpan = document.querySelector('span[email]') ||
                     document.querySelector('.gD[email]') ||
                     document.querySelector('[data-hovercard-id]');
  if (senderSpan) {
    result.senderEmail = senderSpan.getAttribute('email') ||
                         senderSpan.getAttribute('data-hovercard-id') || '';
    result.senderName = senderSpan.getAttribute('name') ||
                        senderSpan.textContent.trim();
  }

  // Date
  const dateEl = document.querySelector('.g3') || document.querySelector('[title*="2026"], [title*="2025"]');
  if (dateEl) result.date = dateEl.getAttribute('title') || dateEl.textContent.trim();

  // Email body — try multiple selectors
  const bodySelectors = [
    'div.a3s.aiL',
    'div.a3s',
    'div.ii.gt',
    'div[data-message-id] .ii',
  ];

  for (const sel of bodySelectors) {
    const els = document.querySelectorAll(sel);
    if (els.length > 0) {
      result.body = Array.from(els).map(el => el.innerText).join('\n\n').trim();
      if (result.body.length > 20) break;
    }
  }

  return result;
}

// ─── Overlay ──────────────────────────────────────────────────────────────────

function showOverlay(parsed, emailData) {
  closeOverlay();

  const overlay = document.createElement('div');
  overlay.className = 'ig-overlay';

  const confidence = parsed.confidence || 'low';
  const confidenceVisible = parsed.client_name ? 'block' : 'none';

  overlay.innerHTML = `
    <div class="ig-overlay-header">
      <h3>📋 Track Invoice</h3>
      <button class="ig-overlay-close" id="igClose">×</button>
    </div>
    <div class="ig-overlay-body">
      <div class="ig-status ig-status--success" style="display:${confidenceVisible}">
        Fields extracted <span class="ig-confidence ig-confidence--${confidence}">${confidence} confidence</span>
      </div>
      <div class="ig-status ig-status--success" style="display:${parsed.client_name ? 'none' : 'block'}">
        No invoice data detected — fill in manually
      </div>

      <div class="ig-field">
        <label>Client name</label>
        <input type="text" id="igClientName" value="${esc(parsed.client_name || emailData.senderName || '')}" placeholder="Acme Corp">
      </div>
      <div class="ig-field">
        <label>Client email</label>
        <input type="email" id="igClientEmail" value="${esc(parsed.client_email || emailData.senderEmail || '')}" placeholder="client@example.com">
      </div>
      <div class="ig-field">
        <label>Amount</label>
        <div style="display:flex;gap:8px">
          <input type="number" id="igAmount" value="${parsed.amount_cents ? (parsed.amount_cents / 100).toFixed(2) : ''}" placeholder="1500.00" step="0.01" style="flex:1">
          <select id="igCurrency" style="width:80px">
            ${['USD','EUR','GBP','CAD','AUD'].map(c => `<option value="${c}" ${c === (parsed.currency || 'USD') ? 'selected' : ''}>${c}</option>`).join('')}
          </select>
        </div>
      </div>
      <div class="ig-field">
        <label>Invoice date</label>
        <input type="date" id="igInvoiceDate" value="${esc(parsed.invoice_date || '')}">
      </div>
      <div class="ig-field">
        <label>Due date</label>
        <input type="date" id="igDueDate" value="${esc(parsed.due_date || '')}">
      </div>
      <div class="ig-field">
        <label>Notes (optional)</label>
        <input type="text" id="igNotes" placeholder="Project name, PO number…">
      </div>
    </div>
    <div class="ig-overlay-footer">
      <button class="ig-btn-save" id="igSave">Save & Track</button>
      <button class="ig-btn-cancel" id="igCancel">Cancel</button>
    </div>
  `;

  document.body.appendChild(overlay);
  currentOverlay = overlay;

  overlay.querySelector('#igClose').addEventListener('click', closeOverlay);
  overlay.querySelector('#igCancel').addEventListener('click', closeOverlay);
  const saveBtn = overlay.querySelector('#igSave');
  saveBtn.addEventListener('click', () => saveInvoice(emailData));

  // Ctrl+Enter / Cmd+Enter to save without clicking
  overlay.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !saveBtn.disabled) {
      e.preventDefault();
      saveInvoice(emailData);
    }
    if (e.key === 'Escape') closeOverlay();
  });

  // Focus first input for keyboard UX
  overlay.querySelector('#igClientName')?.focus();
}

async function saveInvoice(emailData) {
  const saveBtn = document.querySelector('#igSave');
  if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = 'Saving…'; }

  const clientName = document.querySelector('#igClientName')?.value.trim();
  const amountStr = document.querySelector('#igAmount')?.value;
  const amount = parseFloat(amountStr);

  if (!clientName) { showOverlayError('Client name is required.'); resetSaveBtn(); return; }
  if (!amountStr || isNaN(amount) || amount <= 0) { showOverlayError('Please enter a valid amount.'); resetSaveBtn(); return; }

  try {
    const res = await fetch(`${API_BASE}/api/invoices`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        client_name: clientName,
        client_email: document.querySelector('#igClientEmail')?.value.trim() || null,
        amount_cents: Math.round(amount * 100),
        currency: document.querySelector('#igCurrency')?.value || 'USD',
        invoice_date: document.querySelector('#igInvoiceDate')?.value || null,
        due_date: document.querySelector('#igDueDate')?.value || null,
        email_subject: emailData.subject || null,
        email_snippet: (emailData.body || '').slice(0, 200) || null,
        notes: document.querySelector('#igNotes')?.value.trim() || null,
      }),
    });

    const data = await res.json();
    if (!res.ok) { showOverlayError(data.error || 'Failed to save.'); resetSaveBtn(); return; }

    showOverlaySuccess('Invoice tracked! Open the extension to view.');
    chrome.runtime.sendMessage({ type: 'REFRESH_BADGE' });
    setTimeout(closeOverlay, 1800);
  } catch (err) {
    showOverlayError('Network error. Please try again.');
    resetSaveBtn();
  }
}

function resetSaveBtn() {
  const btn = document.querySelector('#igSave');
  if (btn) { btn.disabled = false; btn.textContent = 'Save & Track'; }
}

function closeOverlay() {
  currentOverlay?.remove();
  currentOverlay = null;
  document.querySelectorAll('.ig-track-btn--done').forEach(b => {
    b.className = 'ig-track-btn';
    b.innerHTML = '📋 Track Invoice';
  });
}

function showOverlayError(msg) {
  const body = currentOverlay?.querySelector('.ig-overlay-body');
  if (!body) return;
  body.querySelectorAll('.ig-status--error').forEach(e => e.remove());
  const el = document.createElement('div');
  el.className = 'ig-status ig-status--error';
  el.textContent = msg;
  body.insertBefore(el, body.firstChild);
}

function showOverlaySuccess(msg) {
  if (!currentOverlay) return;
  const body = currentOverlay.querySelector('.ig-overlay-body');
  if (body) body.innerHTML = `<div class="ig-status ig-status--success" style="margin-top:50px;text-align:center;font-size:15px">✓ ${esc(msg)}</div>`;
}

function esc(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ─── Start ────────────────────────────────────────────────────────────────────

init().catch(console.error);

// After 2s, if no button was injected, use floating fallback
setTimeout(() => {
  if (!document.querySelector('.ig-track-btn') && location.href.includes('#')) {
    injectFloatingButton();
  }
}, 2000);
