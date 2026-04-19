const API_BASE = "https://jobguard-api.kirozdormu.workers.dev";

// Register user on first install
chrome.runtime.onInstalled.addListener(async ({ reason }) => {
  if (reason !== "install") return;

  let { userId } = await chrome.storage.local.get("userId");
  if (!userId) {
    userId = crypto.randomUUID();
    await chrome.storage.local.set({ userId });
  }

  try {
    await fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
  } catch (e) {
    console.error("Registration error:", e);
  }
});
