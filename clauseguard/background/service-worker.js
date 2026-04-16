const API_URL = "https://clauseguard-api.kirozdormu.workers.dev";

// On install: generate anonymous UUID and register with backend
chrome.runtime.onInstalled.addListener(async () => {
  const { userId } = await chrome.storage.local.get("userId");
  if (!userId) {
    const id = crypto.randomUUID();
    await chrome.storage.local.set({ userId: id });
    try {
      await fetch(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: id }),
      });
    } catch (e) {
      console.error("ClauseGuard: registration failed", e);
    }
  }
});
