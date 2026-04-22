/**
 * mini-on-ai Shared Extension Utilities
 * ──────────────────────────────────────
 * Source of truth: _shared/utils.js
 * Copied into each extension by: scripts/sync_shared.py
 *
 * DO NOT edit the per-extension copies (popup/shared.js).
 * Edit this file and run `python3 scripts/sync_shared.py`.
 */

// ─── HTML Escaping ────────────────────────────────────────────────────────────

/** Escape a value for safe innerHTML insertion. Uses the DOM-based approach
 *  which correctly handles all edge cases (including null/undefined). */
function escHtml(str) {
  if (str === null || str === undefined) return "";
  const d = document.createElement("div");
  d.textContent = String(str);
  return d.innerHTML;
}

/** Escape a value for safe use in HTML attribute values (e.g. data-* attrs). */
function escAttr(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ─── Clipboard ────────────────────────────────────────────────────────────────

/**
 * Write text to clipboard and give visual feedback on the button.
 *
 * @param {HTMLElement} btn        - The button clicked (its label will be swapped)
 * @param {string}      text       - Text to copy
 * @param {string}      [resetLabel] - Label to restore after 2 s (defaults to
 *                                    btn's current textContent at call time)
 */
function copyText(btn, text, resetLabel) {
  const label = resetLabel !== undefined ? resetLabel : btn.textContent;
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = "✓ Copied!";
    btn.classList.add("copied");
    setTimeout(() => {
      if (btn.isConnected) {
        btn.textContent = label;
        btn.classList.remove("copied");
      }
    }, 2000);
  }).catch(() => {
    btn.textContent = "Copy failed";
    setTimeout(() => {
      if (btn.isConnected) btn.textContent = label;
    }, 2000);
  });
}

// ─── Dark Mode ────────────────────────────────────────────────────────────────

/**
 * Apply stored dark/light preference and wire up the toggle button.
 * Call once on DOMContentLoaded, before any rendering, to avoid FOUC.
 * Icon toggling is CSS-driven via body.light-mode .icon-moon / .icon-sun rules.
 *
 * @param {string} storageKey - localStorage key (e.g. "jg-theme", "ig-theme")
 * @param {string} toggleId   - id of the toggle button element
 */
// Light-mode token values — mirrors body.light-mode block in base.css.
// Applied as inline styles on :root so they win over any CSS cascade/cache issue
// in the Chrome extension popup context.
const _LIGHT_VARS = {
  '--bg':             '#f5f6fa',
  '--surface':        '#ffffff',
  '--surface-raised': '#f0f2f8',
  '--surface-hover':  '#eaecf5',
  '--border':         '#dde0ee',
  '--border-subtle':  '#eaecf5',
  '--text':           '#141625',
  '--text-muted':     '#5a6080',
  '--text-disabled':  '#adb5cc',
  '--shadow-sm':      '0 1px 3px rgba(0,0,0,0.08)',
  '--shadow-md':      '0 4px 12px rgba(0,0,0,0.10)',
  '--shadow-lg':      '0 8px 24px rgba(0,0,0,0.12)',
  '--warning':        '#92400e',
  '--success':        '#059669',
  '--danger':         '#b91c1c',
  '--danger-dim':     'rgba(185,28,28,0.10)',
  '--warning-dim':    'rgba(146,64,14,0.10)',
  '--success-dim':    'rgba(5,150,105,0.10)',
  '--neutral-dim':    'rgba(90,96,128,0.08)',
  '--accent-dim':     'rgba(99,102,241,0.10)',
  '--accent-border':  'rgba(99,102,241,0.25)',
};

function _applyTheme(isLight) {
  const root = document.documentElement;
  document.body.classList.toggle("light-mode", isLight);
  if (isLight) {
    Object.entries(_LIGHT_VARS).forEach(([k, v]) => root.style.setProperty(k, v));
    root.style.setProperty('color-scheme', 'light');
  } else {
    Object.keys(_LIGHT_VARS).forEach(k => root.style.removeProperty(k));
    root.style.removeProperty('color-scheme');
  }
}

function initDarkMode(storageKey, toggleId) {
  const stored = localStorage.getItem(storageKey);
  _applyTheme(stored === "light");

  const toggle = document.getElementById(toggleId);
  if (toggle) {
    toggle.addEventListener("click", () => {
      const isLight = !document.body.classList.contains("light-mode");
      _applyTheme(isLight);
      localStorage.setItem(storageKey, isLight ? "light" : "dark");
    });
  }
}

// ─── Tab Navigation ───────────────────────────────────────────────────────────

/**
 * Wire up tab navigation for popups.
 * Expects buttons with [data-tab="name"] and matching #tab-{name} content divs.
 * The first tab must start with class "active"; content divs hidden via style or .hidden.
 *
 * @param {Function} [onSwitch] - Optional callback(tabName) called after switching.
 */
function setupTabs(onSwitch) {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => {
        c.classList.remove("active", "hidden");
        c.style.display = "none";
      });
      tab.classList.add("active");
      const content = document.getElementById(`tab-${tab.dataset.tab}`);
      if (content) {
        content.classList.remove("hidden");
        content.style.display = "block";
        content.classList.add("active");
      }
      if (onSwitch) onSwitch(tab.dataset.tab);
    });
  });
}

// ─── Tier Badge ───────────────────────────────────────────────────────────────

/**
 * Update the #tierBadge element to reflect the current subscription tier.
 *
 * @param {string} tier - "pro" or "free"
 */
function updateTierBadge(tier) {
  const badge = document.getElementById("tierBadge");
  if (!badge) return;
  const isPro = tier === "pro";
  badge.textContent = isPro ? "Pro" : "Free";
  badge.classList.toggle("tier-badge--pro", isPro);
  badge.classList.toggle("tier-badge--free", !isPro);
}

// ─── Upgrade / Stripe ────────────────────────────────────────────────────────

/**
 * Fetch a Stripe checkout URL from the extension API and open it in a new tab.
 *
 * @param {string} apiBase - e.g. "https://jobguard-api.kirozdormu.workers.dev"
 * @param {string} userId  - stored user UUID
 */
async function startUpgrade(apiBase, userId) {
  try {
    const res = await fetch(`${apiBase}/api/subscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
    const data = await res.json();
    if (data.checkout_url) {
      chrome.tabs.create({ url: data.checkout_url });
    } else {
      alert(data.error || "Failed to start checkout. Please try again.");
    }
  } catch {
    alert("Network error. Please check your connection and try again.");
  }
}
