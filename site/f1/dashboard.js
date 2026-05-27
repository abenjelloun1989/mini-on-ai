const F1_API = 'https://f1-api.kirozdormu.workers.dev';
const token = new URLSearchParams(location.search).get('token');

// ── Boot ─────────────────────────────────────────────────────────────────────
if (!token) {
  document.getElementById('auth-error').style.display = 'block';
} else {
  init();
}

async function init() {
  try {
    await Promise.all([
      loadStats(),
      loadInsights(),
    ]);
    // Load other tabs lazily when clicked
    if (new URLSearchParams(location.search).get('welcome') === '1') {
      document.getElementById('welcome-banner').style.display = 'block';
    }
  } catch (e) {
    showError('Failed to load dashboard: ' + e.message);
  }
}

// ── API helpers ───────────────────────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const sep = path.includes('?') ? '&' : '?';
  const res = await fetch(`${F1_API}${path}${sep}token=${token}`, opts);
  // Capture the deployed commit SHA from the response header on every call
  // so the dashboard can show which build is running.
  const commit = res.headers.get('X-F1-Commit');
  if (commit) renderCommitBadge(commit);
  if (res.status === 401) {
    document.getElementById('auth-error').style.display = 'block';
    throw new Error('Unauthorized');
  }
  return res.json();
}

let _commitRendered = false;
function renderCommitBadge(commit) {
  if (_commitRendered || !commit || commit === 'dev') return;
  _commitRendered = true;
  const short = commit.length > 7 ? commit.slice(0, 7) : commit;
  const url = 'https://github.com/mini-on-ai/f1/commit/' + encodeURIComponent(commit);
  function makeLink() {
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.title = 'Verify the deployed Worker against the open-source repo';
    a.style.cssText = 'color:var(--text-muted);text-decoration:none;';
    a.textContent = 'build ' + short + ' ↗';
    return a;
  }
  const top = document.getElementById('commit-hash');
  const foot = document.getElementById('footer-commit');
  if (top)  { top.textContent = '';  top.appendChild(makeLink()); }
  if (foot) { foot.textContent = ''; foot.appendChild(makeLink()); }
}

// ── Stats ────────────────────────────────────────────────────────────────────
async function loadStats() {
  const data = await apiFetch('/api/stats');
  if (data.error) return showError(data.error);

  const acc = data.account || {};
  document.getElementById('account-tier-label').textContent =
    `${acc.email || ''} · ${acc.tier || ''} plan` + (acc.has_anthropic_key ? '' : ' · ⚠️ No Anthropic key set');

  if (!acc.has_anthropic_key) {
    document.getElementById('byok-section').style.display = 'block';
  }

  setVal('stat-today-usd', fmtUsd(data.today?.usd));
  setVal('stat-today-calls', `${(data.today?.calls || 0).toLocaleString()} calls`);
  setVal('stat-week-usd', fmtUsd(data.week?.usd));
  setVal('stat-week-calls', `${(data.week?.calls || 0).toLocaleString()} calls`);
  setVal('stat-month-usd', fmtUsd(data.month?.usd));
  setVal('stat-month-calls', `${(data.month?.calls || 0).toLocaleString()} calls`);
  setVal('stat-month-tokens', fmtTokens(data.month?.tokens || 0));

  // Model breakdown bars
  const models = data.by_model || [];
  if (models.length > 0) {
    const total = models.reduce((s, m) => s + (m.usd || 0), 0);
    const breakdown = document.getElementById('model-breakdown');
    const card = document.createElement('div');
    card.className = 'card';
    card.style.marginTop = '0';
    models.forEach(m => {
      const row = document.createElement('div');
      row.className = 'model-row';
      const labelDiv = document.createElement('div');
      labelDiv.className = 'model-bar-label';
      const nameSpan = document.createElement('span');
      nameSpan.style.color = 'var(--text)';
      nameSpan.textContent = m.model || 'unknown';
      const detailSpan = document.createElement('span');
      detailSpan.textContent = fmtUsd(m.usd) + ' · ' + (m.calls || 0).toLocaleString() + ' calls';
      labelDiv.append(nameSpan, detailSpan);
      const trackDiv = document.createElement('div');
      trackDiv.className = 'model-bar-track';
      const fillDiv = document.createElement('div');
      fillDiv.className = 'model-bar-fill';
      fillDiv.style.width = (total > 0 ? (m.usd / total * 100).toFixed(1) : 0) + '%';
      trackDiv.appendChild(fillDiv);
      row.append(labelDiv, trackDiv);
      card.appendChild(row);
    });
    breakdown.textContent = '';
    breakdown.appendChild(card);
  }
}

// ── Insights ─────────────────────────────────────────────────────────────────
async function loadInsights() {
  const data = await apiFetch('/api/insights');
  document.getElementById('insights-loading').style.display = 'none';
  if (data.error) return showError(data.error);

  const list = document.getElementById('insights-list');
  list.textContent = '';
  const insights = data.insights || [];
  if (!insights.length) {
    const p = document.createElement('p');
    p.className = 'loading';
    p.textContent = 'No insights yet — make some API calls first.';
    list.appendChild(p);
  } else {
    insights.forEach(ins => {
      const card = document.createElement('div');
      card.className = 'insight-card';
      const header = document.createElement('div');
      header.className = 'ins-header';
      const h4 = document.createElement('h4');
      h4.textContent = ins.title;
      header.appendChild(h4);
      if (ins.estimated_savings_usd > 0.001) {
        const badge = document.createElement('span');
        badge.className = 'savings-badge';
        badge.textContent = '≈ save $' + ins.estimated_savings_usd.toFixed(4);
        header.appendChild(badge);
      }
      const p = document.createElement('p');
      p.textContent = ins.finding;
      card.append(header, p);
      list.appendChild(card);
    });
  }
}

// ── Keys ─────────────────────────────────────────────────────────────────────
async function loadKeys() {
  document.getElementById('keys-loading').textContent = 'Loading…';
  const data = await apiFetch('/api/keys');
  document.getElementById('keys-loading').style.display = 'none';
  if (data.error) return;
  const tbody = document.getElementById('keys-body');
  tbody.textContent = '';
  (data.keys || []).forEach(k => {
    const tr = document.createElement('tr');
    const tdId = document.createElement('td'); tdId.className = 'mono'; tdId.textContent = k.id;
    const tdLabel = document.createElement('td'); tdLabel.textContent = k.label || '—';
    const tdStatus = document.createElement('td');
    const statusSpan = document.createElement('span');
    statusSpan.className = k.active ? 'tag-active' : 'tag-revoked';
    statusSpan.textContent = k.active ? 'active' : 'revoked';
    tdStatus.appendChild(statusSpan);
    const tdDate = document.createElement('td'); tdDate.textContent = fmtDate(k.created_at);
    tr.append(tdId, tdLabel, tdStatus, tdDate);
    tbody.appendChild(tr);
  });
  document.getElementById('keys-table').style.display = 'table';
}

// ── Usage ─────────────────────────────────────────────────────────────────────
async function loadUsage() {
  document.getElementById('usage-loading').textContent = 'Loading…';
  const data = await apiFetch('/api/usage?limit=100');
  document.getElementById('usage-loading').style.display = 'none';
  if (data.error) return;
  const tbody = document.getElementById('usage-body');
  tbody.textContent = '';
  (data.events || []).forEach(e => {
    const tr = document.createElement('tr');
    const cells = [
      { text: fmtDate(e.ts) },
      { text: e.model || '—', cls: 'mono', style: 'max-width:200px;overflow:hidden;text-overflow:ellipsis;' },
      { text: (e.input_tokens || 0).toLocaleString() },
      { text: (e.output_tokens || 0).toLocaleString() },
      { text: '$' + (e.usd_cost || 0).toFixed(5) },
      { text: String(e.status_code), style: 'color:' + (e.status_code < 300 ? 'var(--green)' : 'var(--red)') + ';' },
      { text: e.latency_ms ? e.latency_ms + 'ms' : '—' },
    ];
    cells.forEach(({ text, cls, style }) => {
      const td = document.createElement('td');
      if (cls) td.className = cls;
      if (style) td.style.cssText = style;
      td.textContent = text;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  document.getElementById('usage-table').style.display = 'table';
}

// ── Audit log ─────────────────────────────────────────────────────────────────
async function loadAuditLog() {
  document.getElementById('audit-loading').textContent = 'Loading…';
  const data = await apiFetch('/api/key-access-log');
  document.getElementById('audit-loading').style.display = 'none';
  if (data.error) return;
  const tbody = document.getElementById('audit-body');
  tbody.textContent = '';
  (data.log || []).forEach(e => {
    const tr = document.createElement('tr');
    const tdTs = document.createElement('td'); tdTs.textContent = fmtDate(e.ts);
    const tdReason = document.createElement('td'); tdReason.textContent = e.reason || '—';
    const tdHash = document.createElement('td'); tdHash.className = 'mono'; tdHash.style.fontSize = '11px'; tdHash.textContent = e.ip_hash || '—';
    tr.append(tdTs, tdReason, tdHash);
    tbody.appendChild(tr);
  });
  document.getElementById('audit-table').style.display = 'table';
}

// ── BYOK: upload Anthropic key ────────────────────────────────────────────────
async function uploadAnthropicKey() {
  const key = document.getElementById('anthropic-key-input').value.trim();
  const errEl = document.getElementById('byok-error');
  errEl.style.display = 'none';
  if (!key.startsWith('sk-ant-')) {
    errEl.textContent = 'Invalid key — must start with sk-ant-';
    errEl.style.display = 'block';
    return;
  }
  try {
    const data = await apiFetch('/api/set-anthropic-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ anthropic_key: key }),
    });
    if (data.ok) {
      document.getElementById('byok-section').style.display = 'none';
      document.getElementById('anthropic-key-input').value = '';
      showSuccess('Anthropic key saved and encrypted ✓');
      loadStats();
    } else {
      errEl.textContent = data.error || 'Failed to save key.';
      errEl.style.display = 'block';
    }
  } catch (e) {
    errEl.textContent = 'Network error. Please try again.';
    errEl.style.display = 'block';
  }
}

// ── Billing portal ────────────────────────────────────────────────────────────
async function openPortal() {
  const data = await apiFetch('/api/portal', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
  if (data.portal_url) window.location.href = data.portal_url;
}

// ── Settings ─────────────────────────────────────────────────────────────────
async function saveCutoverDate() {
  const d = document.getElementById('cutover-date-input').value;
  if (!d) return;
  await apiFetch('/api/cutover-date', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cutover_date: d }),
  });
  showSuccess('Cutover date saved. Reload insights to see the updated comparison.');
}

async function savePromptOptin(val) {
  const data = await apiFetch('/api/prompt-optin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt_optin: val ? 1 : 0 }),
  });
  if (data && data.ok) {
    showSuccess(val
      ? 'Prompt prefix storage enabled (takes effect on next call).'
      : 'Prompt prefix storage disabled.');
  }
}

// ── Spend alerts ────────────────────────────────────────────────────────────
async function loadAlerts() {
  const data = await apiFetch('/api/alerts');
  if (!data) return;
  const budgetInput = document.getElementById('alert-budget-input');
  const emailInput = document.getElementById('alert-email-input');
  const webhookInput = document.getElementById('alert-webhook-input');
  const hint = document.getElementById('alert-suggested-hint');
  const status = document.getElementById('alert-status');

  if (data.alert_budget_usd != null) budgetInput.value = data.alert_budget_usd;
  else budgetInput.placeholder = String(data.suggested_budget_usd ?? 50);
  if (data.alert_email) emailInput.value = data.alert_email;
  if (data.account_email) emailInput.placeholder = data.account_email;
  if (data.alert_webhook_url) webhookInput.value = data.alert_webhook_url;

  if (hint) {
    const spent = Number(data.spent_last_30d_usd || 0);
    if (spent > 0) {
      hint.textContent = `Suggested: $${data.suggested_budget_usd} (1.5× your last 30d spend of $${spent.toFixed(2)})`;
    } else {
      hint.textContent = `Suggested: $${data.suggested_budget_usd} (no usage history yet)`;
    }
  }

  if (status) {
    if (data.alert_budget_usd == null) {
      status.textContent = 'Alerts off — set a budget to enable.';
    } else {
      const lastFired = data.alert_fired_at
        ? `last fired ${new Date(data.alert_fired_at).toLocaleString()}`
        : 'never fired';
      status.textContent = `Budget $${data.alert_budget_usd} · ${lastFired}.`;
    }
  }
}

async function saveAlerts() {
  const budgetRaw = document.getElementById('alert-budget-input').value.trim();
  const email = document.getElementById('alert-email-input').value.trim();
  const webhook = document.getElementById('alert-webhook-input').value.trim();
  const body = {
    alert_budget_usd: budgetRaw === '' ? null : Number(budgetRaw),
    alert_email: email || null,
    alert_webhook_url: webhook || null,
  };
  const data = await apiFetch('/api/alerts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (data && data.ok) {
    if (data.alert_budget_usd == null) showSuccess('Alerts turned off.');
    else showSuccess('Alert settings saved.');
    loadAlerts();
  } else if (data && data.error) {
    showError(data.error);
  }
}

async function testAlert() {
  const data = await apiFetch('/api/alerts/test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (data && data.ok) {
    const parts = [];
    parts.push(data.sent.email ? 'email sent ✓' : 'email failed ✗');
    if (data.sent.webhook !== null) parts.push(data.sent.webhook ? 'webhook sent ✓' : 'webhook failed ✗');
    showSuccess('Test alert: ' + parts.join(' · ') + ' — check your inbox (and Slack/Discord if set).');
  } else if (data && data.error) {
    showError(data.error);
  }
}

async function clearAlerts() {
  document.getElementById('alert-budget-input').value = '';
  document.getElementById('alert-webhook-input').value = '';
  await saveAlerts();
}

async function deleteAccount() {
  if (!confirm('Delete your account and ALL data permanently? This cannot be undone.')) return;
  if (!confirm('Are you sure? Keys, usage events, and audit log will be hard-deleted.')) return;
  const data = await apiFetch('/api/account', { method: 'DELETE' });
  if (data.deleted) {
    document.body.innerHTML = '<div style="text-align:center;padding:80px 24px;font-family:Inter,sans-serif;color:#e2e8f0;background:#08080F;min-height:100vh;"><h1 style="color:#6366F1;">Account deleted</h1><p style="color:#64748b;margin-top:12px;">All your data has been removed. Goodbye.</p><a href="/f1" style="color:#6366F1;display:block;margin-top:24px;">← Back to F1</a></div>';
  }
}

// ── Tabs ─────────────────────────────────────────────────────────────────────
const loaded = { insights: true };
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
  if (!loaded[name]) {
    loaded[name] = true;
    if (name === 'keys') loadKeys();
    if (name === 'usage') loadUsage();
    if (name === 'audit') loadAuditLog();
    if (name === 'settings') loadAlerts();
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmtUsd(v) { return v == null ? '—' : '$' + Number(v).toFixed(4); }
function fmtTokens(n) {
  if (n >= 1e9) return (n/1e9).toFixed(1) + 'B';
  if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
  return String(n);
}
function fmtDate(s) {
  if (!s) return '—';
  const d = new Date(s);
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
function setVal(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; }
function showError(msg) {
  const el = document.createElement('div');
  el.className = 'error-msg';
  el.textContent = msg;
  document.querySelector('.dash-main').prepend(el);
}
function showSuccess(msg) {
  const el = document.createElement('div');
  el.style.cssText = 'background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.3);color:#34d399;border-radius:8px;padding:10px 16px;font-size:13px;margin-bottom:16px;';
  el.textContent = msg;
  document.querySelector('.dash-main').prepend(el);
  setTimeout(() => el.remove(), 5000);
}
