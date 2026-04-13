const API_BASE = "https://invoiceguard-api.kirozdormu.workers.dev";

let userId = null;

document.addEventListener("DOMContentLoaded", async () => {
  const { userId: uid } = await chrome.storage.local.get("userId");
  userId = uid;

  if (!userId) return;

  document.getElementById("supportId").textContent = userId.slice(0, 8);
  document.getElementById("supportId").addEventListener("click", async () => {
    await navigator.clipboard.writeText(userId);
    document.getElementById("supportId").textContent = "Copied!";
    setTimeout(() => {
      document.getElementById("supportId").textContent = userId.slice(0, 8);
    }, 2000);
  });

  // Load account data
  const [usageRes, subRes] = await Promise.all([
    fetch(`${API_BASE}/api/usage?user_id=${userId}`).catch(() => null),
    fetch(`${API_BASE}/api/subscription?user_id=${userId}`).catch(() => null),
  ]);

  if (usageRes?.ok) {
    const usage = await usageRes.json();
    document.getElementById("activeDisplay").textContent = `${usage.active_invoices || 0}${usage.tier === "free" ? " / 5" : ""}`;
  }

  if (subRes?.ok) {
    const sub = await subRes.json();
    const tierEl = document.getElementById("tierDisplay");

    if (sub.tier === "pro") {
      tierEl.textContent = "Pro";
      tierEl.classList.add("row-value--pro");
      document.getElementById("subFree").style.display = "none";
      document.getElementById("subPro").style.display = "block";
      await chrome.storage.local.set({ tier: "pro" });
    } else {
      tierEl.textContent = "Free";
      tierEl.classList.add("row-value--free");
    }

    if (sub.email) {
      document.getElementById("emailDisplay").textContent = sub.email;
    }
  }

  // Upgrade
  document.getElementById("upgradeBtn").addEventListener("click", async () => {
    try {
      const res = await fetch(`${API_BASE}/api/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      const data = await res.json();
      if (data.checkout_url) window.open(data.checkout_url);
    } catch (e) {
      alert("Error starting checkout.");
    }
  });

  // Cancel / manage
  document.getElementById("cancelBtn").addEventListener("click", async () => {
    try {
      const res = await fetch(`${API_BASE}/api/portal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      const data = await res.json();
      if (data.portal_url) window.open(data.portal_url);
    } catch (e) {
      alert("Error opening billing portal.");
    }
  });

  // Export CSV
  document.getElementById("exportBtn").addEventListener("click", async () => {
    try {
      const res = await fetch(`${API_BASE}/api/invoices?user_id=${userId}`);
      if (!res.ok) { alert("Failed to load invoices."); return; }

      const data = await res.json();
      const invoices = data.invoices || [];

      if (invoices.length === 0) { alert("No invoices to export."); return; }

      const headers = ["Client", "Email", "Amount", "Currency", "Status", "Invoice Date", "Due Date", "Reminders Sent", "Last Reminder", "Notes", "Created"];
      const rows = invoices.map(i => [
        i.client_name,
        i.client_email || "",
        (i.amount_cents / 100).toFixed(2),
        i.currency,
        i.status,
        i.invoice_date || "",
        i.due_date || "",
        i.reminders_sent || 0,
        i.last_reminder_at || "",
        (i.notes || "").replace(/"/g, '""'),
        i.created_at,
      ]);

      const csv = [headers, ...rows].map(row =>
        row.map(cell => `"${cell}"`).join(",")
      ).join("\n");

      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `invoiceguard-export-${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("Export failed.");
    }
  });
});
