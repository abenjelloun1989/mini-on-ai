import { corsJson, parseJson, requireUser, currentMonth } from "./index.js";

const FREE_INVOICE_LIMIT = 5;
const RATE_LIMIT_PER_MINUTE = 10;

// -----------------------------------------------------------------------------
// POST /api/invoices — create (track) a new invoice
// -----------------------------------------------------------------------------

export async function handleCreateInvoice(request, env) {
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, client_name, client_email, amount_cents, currency, invoice_date, due_date, email_subject, email_snippet, notes } = body;

  let user = await requireUser(env, user_id);
  if (!user) {
    await env.DB.prepare("INSERT OR IGNORE INTO users (id, tier) VALUES (?, 'free')").bind(user_id).run();
    user = await requireUser(env, user_id);
  }
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  // Rate limiting
  const minuteKey = `ratelimit:${user.id}:${Math.floor(Date.now() / 60000)}`;
  const rlRaw = await env.KV.get(minuteKey);
  const rlCount = rlRaw ? parseInt(rlRaw) : 0;
  if (rlCount >= RATE_LIMIT_PER_MINUTE) {
    return corsJson(env, { error: "Too many requests. Please wait a moment." }, 429);
  }
  await env.KV.put(minuteKey, String(rlCount + 1), { expirationTtl: 120 });

  // Free tier: count active invoices
  if (user.tier === "free") {
    const active = await env.DB.prepare(
      "SELECT COUNT(*) as cnt FROM invoices WHERE user_id = ? AND status IN ('sent', 'overdue')"
    ).bind(user.id).first();

    if ((active?.cnt || 0) >= FREE_INVOICE_LIMIT) {
      return corsJson(env, {
        error: `Free plan allows tracking up to ${FREE_INVOICE_LIMIT} active invoices. Upgrade to Pro for unlimited tracking.`,
        upgrade: true,
      }, 403);
    }
  }

  // Validate required fields
  if (!client_name || !amount_cents) {
    return corsJson(env, { error: "Missing required fields: client_name, amount_cents" }, 400);
  }

  if (typeof amount_cents !== "number" || amount_cents <= 0) {
    return corsJson(env, { error: "amount_cents must be a positive number" }, 400);
  }

  const id = crypto.randomUUID();
  const now = new Date().toISOString();

  await env.DB.prepare(`
    INSERT INTO invoices (id, user_id, client_name, client_email, amount_cents, currency, invoice_date, due_date, status, email_subject, email_snippet, notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sent', ?, ?, ?, ?, ?)
  `).bind(
    id,
    user.id,
    client_name,
    client_email || null,
    amount_cents,
    currency || "USD",
    invoice_date || null,
    due_date || null,
    email_subject || null,
    email_snippet || null,
    notes || null,
    now,
    now,
  ).run();

  // Track usage
  const month = currentMonth();
  await env.DB.prepare(`
    INSERT INTO usage_tracking (user_id, month, invoice_count) VALUES (?, ?, 1)
    ON CONFLICT(user_id, month) DO UPDATE SET invoice_count = invoice_count + 1
  `).bind(user.id, month).run();

  return corsJson(env, {
    id,
    client_name,
    amount_cents,
    currency: currency || "USD",
    due_date: due_date || null,
    status: "sent",
    created_at: now,
  }, 201);
}

// -----------------------------------------------------------------------------
// GET /api/invoices?user_id=...&status=...
// -----------------------------------------------------------------------------

export async function handleListInvoices(request, env) {
  const url = new URL(request.url);
  const userId = url.searchParams.get("user_id");
  const statusFilter = url.searchParams.get("status"); // sent, overdue, paid, cancelled

  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  let query = "SELECT * FROM invoices WHERE user_id = ?";
  const binds = [user.id];

  if (statusFilter) {
    query += " AND status = ?";
    binds.push(statusFilter);
  }

  query += " ORDER BY CASE status WHEN 'overdue' THEN 0 WHEN 'sent' THEN 1 WHEN 'paid' THEN 2 ELSE 3 END, due_date ASC";

  const stmt = env.DB.prepare(query);
  const { results } = await stmt.bind(...binds).all();

  // Auto-mark overdue invoices
  const today = new Date().toISOString().slice(0, 10);
  const updated = [];
  for (const inv of results) {
    if (inv.status === "sent" && inv.due_date && inv.due_date < today) {
      inv.status = "overdue";
      updated.push(inv.id);
    }
  }

  // Batch update overdue status
  if (updated.length > 0) {
    for (const id of updated) {
      await env.DB.prepare(
        "UPDATE invoices SET status = 'overdue', updated_at = datetime('now') WHERE id = ? AND status = 'sent'"
      ).bind(id).run();
    }
  }

  // Compute summary
  const active = results.filter(i => i.status === "sent" || i.status === "overdue");
  const overdue = results.filter(i => i.status === "overdue");
  const totalOutstanding = active.reduce((sum, i) => sum + i.amount_cents, 0);
  const totalOverdue = overdue.reduce((sum, i) => sum + i.amount_cents, 0);

  return corsJson(env, {
    invoices: results,
    summary: {
      total: results.length,
      active: active.length,
      overdue: overdue.length,
      total_outstanding_cents: totalOutstanding,
      total_overdue_cents: totalOverdue,
    },
  });
}

// -----------------------------------------------------------------------------
// PATCH /api/invoices/:id — update invoice status, notes, etc.
// -----------------------------------------------------------------------------

export async function handleUpdateInvoice(request, env, path) {
  const invoiceId = path.split("/").pop();
  const body = await parseJson(request);
  if (body.error) return corsJson(env, body, 400);

  const { user_id, status, notes, due_date, amount_cents, client_name } = body;
  const user = await requireUser(env, user_id);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  // Verify ownership
  const invoice = await env.DB.prepare(
    "SELECT * FROM invoices WHERE id = ? AND user_id = ?"
  ).bind(invoiceId, user.id).first();

  if (!invoice) return corsJson(env, { error: "Invoice not found" }, 404);

  // Build dynamic update
  const updates = [];
  const values = [];

  if (status && ["sent", "overdue", "paid", "cancelled"].includes(status)) {
    updates.push("status = ?");
    values.push(status);
  }
  if (notes !== undefined) {
    updates.push("notes = ?");
    values.push(notes);
  }
  if (due_date !== undefined) {
    updates.push("due_date = ?");
    values.push(due_date);
  }
  if (amount_cents !== undefined) {
    updates.push("amount_cents = ?");
    values.push(amount_cents);
  }
  if (client_name !== undefined) {
    updates.push("client_name = ?");
    values.push(client_name);
  }

  if (updates.length === 0) {
    return corsJson(env, { error: "No fields to update" }, 400);
  }

  updates.push("updated_at = datetime('now')");
  const sql = `UPDATE invoices SET ${updates.join(", ")} WHERE id = ? AND user_id = ?`;
  values.push(invoiceId, user.id);

  await env.DB.prepare(sql).bind(...values).run();

  // Return updated invoice
  const updated = await env.DB.prepare(
    "SELECT * FROM invoices WHERE id = ?"
  ).bind(invoiceId).first();

  return corsJson(env, updated);
}

// -----------------------------------------------------------------------------
// DELETE /api/invoices/:id?user_id=...
// -----------------------------------------------------------------------------

export async function handleDeleteInvoice(request, env, path) {
  const invoiceId = path.split("/").pop();
  const userId = new URL(request.url).searchParams.get("user_id");
  const user = await requireUser(env, userId);
  if (!user) return corsJson(env, { error: "User not found" }, 404);

  await env.DB.prepare(
    "DELETE FROM invoices WHERE id = ? AND user_id = ?"
  ).bind(invoiceId, user.id).run();

  return corsJson(env, { deleted: true });
}
