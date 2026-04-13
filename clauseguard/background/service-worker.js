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

// Message router for content script communication
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "extractGoogleDoc") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (!tab || !tab.url?.includes("docs.google.com/document")) {
        sendResponse({ error: "Not a Google Doc" });
        return;
      }
      chrome.tabs.sendMessage(tab.id, { action: "extractText" }, (response) => {
        sendResponse(response || { error: "Could not extract text" });
      });
    });
    return true; // keep channel open for async response
  }
});
