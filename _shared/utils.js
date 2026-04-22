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
function initDarkMode(storageKey, toggleId) {
  const toggle = document.getElementById(toggleId);
  const stored = localStorage.getItem(storageKey);
  if (stored === "light") {
    document.body.classList.add("light-mode");
  }
  if (toggle) {
    toggle.addEventListener("click", () => {
      const isLight = document.body.classList.toggle("light-mode");
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
