# n8n Starter Guide for Zapier Users

If you're coming from Zapier or Make.com and want to start taking client work on n8n, this guide maps what you already know to n8n's concepts and flags the critical differences that will trip you up. Expect a working mental model in one read.

---

## 1. Remap Your Mental Model

Your Zapier "Zap" = n8n **Workflow**. Your Zapier "Step" = n8n **Node**. The trigger-action pattern is identical, but n8n gives you branching, merging, and looping natively — things Zapier charges premium tiers for.

**Key differences to internalize:**
- n8n passes **arrays of items** between nodes, not single records. If your Airtable node returns 50 rows, the next node processes all 50 by default. Zapier loops implicitly; n8n makes data flow explicit.
- There's no "Test & Review" safety net. Use **Ctrl+Enter** to execute a single node mid-build and inspect its output JSON before wiring up the next step.
- Self-hosted means **you manage credentials, uptime, and updates**. For client work, budget time for this or use n8n Cloud.

---

## 2. Understand How Data Flows Between Nodes

This is where most Zapier refugees get stuck. Every node outputs a JSON array under the key `json`. To reference the previous node's output, you use expressions like `{{ $json.email }}` or `{{ $node["Get Contact"].json.email }}`.

**Practical tips:**
- Click the **"Expression"** toggle on any field to switch from static text to dynamic references. The expression editor shows you the live data tree from upstream nodes — use it constantly while building.
- When a node returns multiple items (e.g., 20 Notion pages), downstream nodes run **once per item** automatically. To aggregate them back into one item, use the **Merge** or **Code** node.
- If you see `undefined` in outputs, check whether you're referencing `$json` (current item) vs. `$items()` (all items from a node). This distinction doesn't exist in Zapier.

---

## 3. Master the Four Nodes You'll Use on 80% of Projects

Don't try to learn all 400+ nodes at once. Get fluent in these:

- **HTTP Request** — replaces Zapier's "Webhooks by Zapier." Use it for any API without a native node. Set Auth to "Generic Credential Type," pick OAuth2 or Header Auth, and you can connect virtually anything.
- **Code (JavaScript)** — a fully functional Node.js environment. Use it to transform data, build objects, or do conditional logic that would take 5 Zapier steps. Example: parse a messy webhook payload into clean fields in 8 lines.
- **IF / Switch** — branching logic. IF handles binary yes/no; Switch handles multiple conditions (like a router in Make.com). Wire different actions to each output branch.
- **Schedule Trigger + Set Node combo** — Schedule triggers recurring runs; Set node lets you define static variables at the top of a workflow (like a config block), so client-specific values live in one place.

---

## 4. Handle Errors Like a Professional

Zapier notifies you when a Zap fails. n8n requires you to build error handling yourself, and clients will notice if you don't.

**What to implement before delivering any workflow:**
- Enable **"Continue on Fail"** on nodes that might have transient failures (API rate limits, timeouts). Find it in the node settings panel.
- Add an **Error Trigger** workflow that catches failures from your main workflow and sends a Slack or email alert with the execution ID and error message. Set this up once as a reusable template.
- Turn on **execution logging** (Settings → Save Execution Progress) so you can replay failed runs. Without this, debugging a production failure is nearly blind.

---

## 5. Credentials and Client Handoffs

This is operationally critical and Zapier users consistently underestimate it.

**How to do it cleanly:**
- Store all credentials in **n8n's Credential store** (not hardcoded in nodes). Name them with a convention: `[Client] - [Service]` (e.g., `AcmeCo - Airtable`). This makes multi-client instances manageable.
- On self-hosted setups, use **n8n's environment variables** for secrets that apply globally (API keys for your own services). Never put these in workflow JSON exports — exports include credential IDs but not the secret values themselves, which is safer than it sounds.
- When handing off to a client's own n8n instance, export the workflow JSON and document which credentials need to be recreated. Build a 1-page credential checklist per project.

---

## 6. Before Taking Your First Client Project

Spend one week running these drills on a self-hosted or Cloud trial instance:

1. Build a webhook → transform → HTTP Request workflow end-to-end without using any native integration nodes.
2. Intentionally break a workflow and practice reading the execution log to find the failure.
3. Build the Error Trigger workflow described above and verify the alert fires.

---

## Quick-Reference Summary

- **Zap = Workflow, Step = Node** — trigger-action pattern is the same; execution model is not
- n8n processes **arrays of items**; always inspect node output JSON before wiring the next step
- Use `{{ $json.fieldName }}` for expressions; switch to Expression mode per field, not globally
- **HTTP Request + Code + IF/Switch + Schedule** cover the majority of real-world workflows
- Build error handling (Continue on Fail + Error Trigger workflow) before any client delivery
- Name credentials `[Client] - [Service]`; never hardcode secrets in nodes
- Drill basic builds for one week before charging clients — the failure modes are different from Zapier