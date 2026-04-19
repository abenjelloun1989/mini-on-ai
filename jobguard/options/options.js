const API_BASE = "https://jobguard-api.kirozdormu.workers.dev";

document.addEventListener("DOMContentLoaded", async () => {
  const { userId } = await chrome.storage.local.get("userId");

  const userIdEl = document.getElementById("userId");
  if (userId) {
    userIdEl.textContent = userId;
  } else {
    userIdEl.textContent = "Not registered";
  }

  // Copy ID
  document.getElementById("copyIdBtn").addEventListener("click", (e) => {
    if (!userId) return;
    navigator.clipboard.writeText(userId).then(() => {
      e.target.textContent = "Copied!";
      setTimeout(() => { e.target.textContent = "Copy ID"; }, 2000);
    }).catch(() => {
      e.target.textContent = "Copy failed";
      setTimeout(() => { e.target.textContent = "Copy ID"; }, 2000);
    });
  });

  // Delete account
  document.getElementById("deleteAccountBtn").addEventListener("click", async () => {
    if (!userId) return;
    if (!confirm("This will permanently delete all your JobGuard data. This cannot be undone. Continue?")) return;

    try {
      await fetch(`${API_BASE}/api/user`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      await chrome.storage.local.clear();
      alert("Your account and all data have been deleted.");
      window.close();
    } catch (e) {
      alert("Failed to delete account. Please try again or contact support.");
    }
  });
});
