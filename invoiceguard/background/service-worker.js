/**
 * InvoiceGuard — Background Service Worker
 *
 * Responsibilities:
 * 1. Generate UUID on first install
 * 2. Register user with backend
 * 3. Check for overdue invoices periodically (alarm)
 * 4. Badge icon with overdue count
 */

const API_BASE = "https://invoiceguard-api.kirozdormu.workers.dev";

// ─── Install / Startup ───────────────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(async (details) => {
  if (details.reason === "install") {
    const userId = crypto.randomUUID();
    await chrome.storage.local.set({ userId, installedAt: Date.now() });

    // Register with backend
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      const data = await res.json();
      await chrome.storage.local.set({ tier: data.tier || "free" });
    } catch (e) {
      console.error("Registration failed:", e);
    }
  }

  // Set up daily alarm to check overdue invoices
  chrome.alarms.create("checkOverdue", { periodInMinutes: 360 }); // every 6 hours
});

// ─── Alarm: Check overdue invoices ───────────────────────────────────────────

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "checkOverdue") {
    await updateOverdueBadge();
  }
});

async function updateOverdueBadge() {
  try {
    const { userId } = await chrome.storage.local.get("userId");
    if (!userId) return;

    const res = await fetch(`${API_BASE}/api/invoices?user_id=${userId}&status=overdue`);
    if (!res.ok) return;

    const data = await res.json();
    const overdueCount = data.summary?.overdue || 0;

    if (overdueCount > 0) {
      chrome.action.setBadgeText({ text: String(overdueCount) });
      chrome.action.setBadgeBackgroundColor({ color: "#EF4444" });
    } else {
      chrome.action.setBadgeText({ text: "" });
    }
  } catch (e) {
    console.error("Badge update failed:", e);
  }
}

// ─── Message handling from content script / popup ────────────────────────────

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GET_USER_ID") {
    chrome.storage.local.get("userId").then(({ userId }) => {
      sendResponse({ userId });
    });
    return true; // async response
  }

  if (message.type === "REFRESH_BADGE") {
    updateOverdueBadge();
    return false;
  }
});
