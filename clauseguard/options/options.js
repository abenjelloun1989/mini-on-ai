const API_URL = "https://clauseguard-api.kirozdormu.workers.dev";

document.addEventListener("DOMContentLoaded", async () => {
  const { userId } = await chrome.storage.local.get("userId");
  if (!userId) return;

  try {
    const res = await fetch(`${API_URL}/api/usage?user_id=${userId}`);
    const data = await res.json();

    // Plan badge
    const planBadge = document.getElementById("planBadge");
    if (data.tier === "pro") {
      planBadge.innerHTML = '<span class="tier-badge tier-pro">Pro</span>';
      document.getElementById("upgradeCard").style.display = "none";
      document.getElementById("manageSection").style.display = "block";
      document.getElementById("limitStat").textContent = "Unlimited";
    }

    document.getElementById("usageStat").textContent = data.usage_this_month ?? 0;
    if (data.tier !== "pro") {
      document.getElementById("limitStat").textContent = data.limit ?? 3;
    }
  } catch (e) {
    console.error("Failed to load account data", e);
  }

  document.getElementById("upgradeBtn")?.addEventListener("click", async () => {
    const { userId } = await chrome.storage.local.get("userId");
    const res = await fetch(`${API_URL}/api/subscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
    const data = await res.json();
    if (data.checkout_url) window.open(data.checkout_url, "_blank");
  });

  document.getElementById("manageBtn")?.addEventListener("click", async () => {
    const { userId } = await chrome.storage.local.get("userId");
    const res = await fetch(`${API_URL}/api/portal`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
    const data = await res.json();
    if (data.portal_url) window.open(data.portal_url, "_blank");
  });
});
