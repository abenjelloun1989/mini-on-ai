const API_URL = "https://clauseguard-api.kirozdormu.workers.dev";

document.addEventListener("DOMContentLoaded", async () => {
  const { userId } = await chrome.storage.local.get("userId");

  // Show support ID
  if (userId) {
    document.getElementById("userIdDisplay").textContent = userId;
    document.getElementById("copyIdBtn").addEventListener("click", () => {
      navigator.clipboard.writeText(userId).then(() => {
        const btn = document.getElementById("copyIdBtn");
        btn.textContent = "Copied!";
        setTimeout(() => { btn.textContent = "Copy"; }, 2000);
      });
    });
  }

  if (!userId) {
    document.getElementById("planBadge").textContent = "—";
    document.getElementById("subStatus").textContent = "Not registered";
    return;
  }

  try {
    // Load usage + subscription in parallel
    const [usageRes, subRes] = await Promise.all([
      fetch(`${API_URL}/api/usage?user_id=${userId}`),
      fetch(`${API_URL}/api/subscription?user_id=${userId}`),
    ]);
    const usage = await usageRes.json();
    const sub = await subRes.json();

    const isPro = usage.tier === "pro";

    // Plan badge
    document.getElementById("planBadge").innerHTML = isPro
      ? '<span class="tier-badge tier-pro">✦ Pro</span>'
      : '<span class="tier-badge tier-free">Free</span>';

    // Email (if available)
    if (sub.email) {
      document.getElementById("emailStat").style.display = "flex";
      document.getElementById("emailValue").textContent = sub.email;
    }

    // Subscription status
    const subStatusEl = document.getElementById("subStatus");
    if (isPro && sub.has_subscription) {
      subStatusEl.innerHTML = '<span class="status-dot active"></span>Active';
    } else if (isPro && !sub.has_subscription) {
      subStatusEl.innerHTML = '<span class="status-dot active"></span>Active (lifetime)';
    } else {
      subStatusEl.innerHTML = '<span class="status-dot inactive"></span>Free plan';
    }

    // Usage count
    const count = usage.usage_this_month ?? 0;
    const limit = usage.limit ?? 3;
    document.getElementById("usageStat").textContent = isPro
      ? `${count} (unlimited)`
      : `${count} / ${limit}`;

    // Usage bar
    if (isPro) {
      document.getElementById("usageBar").style.display = "none";
    } else {
      const pct = Math.min(100, Math.round((count / limit) * 100));
      const fill = document.getElementById("usageBarFill");
      fill.style.width = `${pct}%`;
      if (pct >= 67) fill.classList.add("warn");
      document.getElementById("usageBarLabel").textContent = `${count} / ${limit} used`;
    }

    // Show/hide upgrade vs manage
    if (isPro) {
      document.getElementById("upgradeCard").classList.add("hidden");
      document.getElementById("manageSection").classList.remove("hidden");
    }

  } catch (e) {
    console.error("Failed to load account data", e);
    document.getElementById("planBadge").textContent = "Error loading";
    document.getElementById("subStatus").textContent = "Could not connect";
  }

  // Upgrade button
  document.getElementById("upgradeBtn")?.addEventListener("click", async () => {
    const btn = document.getElementById("upgradeBtn");
    btn.textContent = "Opening checkout…";
    btn.disabled = true;
    try {
      const res = await fetch(`${API_URL}/api/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert(data.error || "Could not open checkout. Please try again.");
        btn.textContent = "Upgrade to Pro →";
        btn.disabled = false;
      }
    } catch (e) {
      alert("Could not connect to payment server. Check your connection and try again.");
      btn.textContent = "Upgrade to Pro →";
      btn.disabled = false;
    }
  });

  // Manage subscription (portal)
  document.getElementById("manageBtn")?.addEventListener("click", async () => {
    const btn = document.getElementById("manageBtn");
    btn.textContent = "Opening…";
    btn.disabled = true;
    try {
      const res = await fetch(`${API_URL}/api/portal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      const data = await res.json();
      if (data.portal_url) {
        window.open(data.portal_url, "_blank");
      } else {
        alert("Could not open billing portal. Please try again.");
      }
    } catch (e) {
      alert("Could not connect. Please try again.");
    } finally {
      btn.textContent = "⚙ Manage subscription →";
      btn.disabled = false;
    }
  });

  // Cancel = same as manage portal
  document.getElementById("cancelBtn")?.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to cancel your Pro subscription? You'll keep access until the end of your billing period.")) return;
    document.getElementById("manageBtn").click();
  });
});
