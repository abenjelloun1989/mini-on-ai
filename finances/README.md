# Finances — Personal Finance PWA

A private, single-user budgeting Progressive Web App built for one job: **log an
expense on your phone in under 10 seconds**. Stats, projections and an AI assistant
are secondary.

- **Frontend** — static HTML + CSS + vanilla JS (no build step, no npm, no framework),
  Chart.js vendored locally. Deploys to **Cloudflare Pages**.
- **Backend** — a single **Cloudflare Worker** (`/api/*`) over **Cloudflare D1** (SQLite).
- **Auth** — **Cloudflare Access** (Zero Trust) protects the whole site; the Worker
  verifies the Access JWT on every request.
- **AI** — Claude (`claude-opus-4-8`) called only from the Worker; the key never
  reaches the browser. The assistant receives **aggregated totals only**, never
  individual transactions.

```
finances/
├── migration.sql        D1 schema
├── worker/              Cloudflare Worker (src/ + wrangler.toml)
└── public/              the PWA (deploy this folder to Pages)
```

---

## 1. Database (D1)

```bash
cd worker
wrangler d1 create finances-db
# → copy the printed database_id into wrangler.toml (replace REPLACE_WITH_YOUR_D1_ID)

# apply the schema to the remote DB
wrangler d1 execute finances-db --remote --file=../migration.sql
```

## 2. Worker config & secrets

Edit `worker/wrangler.toml` `[vars]`:
- `ALLOWED_ORIGIN` — your Pages URL (e.g. `https://finances.pages.dev`), no trailing slash
- `ALLOWED_EMAIL` — the single email allowed by your Access policy
- `CF_ACCESS_AUD` — the **Application Audience (AUD) tag** from the Access app (set in step 4)

Set the secrets (never committed):

```bash
wrangler secret put ANTHROPIC_API_KEY      # sk-ant-...
wrangler secret put CF_ACCESS_TEAM_DOMAIN  # e.g. myteam.cloudflareaccess.com
```

Deploy:

```bash
wrangler deploy
# note the worker URL, e.g. https://finances-worker.<your-subdomain>.workers.dev
```

## 3. Frontend (Cloudflare Pages)

The Worker is on a different origin than Pages, so tell the frontend where the API
lives. Two options:

- **Recommended — same origin via a Pages route/Worker route:** bind the Worker to
  a route on the Pages domain so `/api/*` is same-origin. Then leave the default
  (`API_BASE = ""`).
- **Cross-origin:** add an inline config before the app loads. In `public/index.html`,
  just above `<script type="module" src="js/app.js">`, add:
  ```html
  <script>window.FINANCES_API_BASE = "https://finances-worker.<your-subdomain>.workers.dev";</script>
  ```

Then update CSP in `public/_headers`: replace
`https://finances-worker.YOUR-SUBDOMAIN.workers.dev` in `connect-src` with your real
Worker URL (or remove it if you went same-origin).

Deploy: push this repo to GitHub → Cloudflare **Pages → Create project → connect repo**
→ set the **build output / root directory to `finances/public`**, no build command.

## 4. Cloudflare Access (Zero Trust)

1. Zero Trust dashboard → **Access → Applications → Add an application → Self-hosted**.
2. Application domain = your Pages URL.
3. **Policy:** Action **Allow**, Include → **Emails** → your address.
4. **Login method:** **One-time PIN** (built-in, no code).
5. Open the application's overview and copy the **Application Audience (AUD) Tag** →
   paste into `CF_ACCESS_AUD` in `wrangler.toml`, then `wrangler deploy` again.
6. Your **team domain** (`<team>.cloudflareaccess.com`) is the `CF_ACCESS_TEAM_DOMAIN`
   secret from step 2.

Now every request to the site requires a one-time-PIN login, and the Worker rejects
any request whose Access JWT is missing/invalid/expired or whose email ≠ `ALLOWED_EMAIL`.

## 5. Install on your phone

Open the Pages URL on your phone → log in via the PIN → browser menu →
**"Ajouter à l'écran d'accueil"**. It installs as a standalone PWA and loads offline.

---

## Local development

**Frontend only (visual), no backend needed** — runs against in-memory fixtures:

```bash
cd public
python3 -m http.server 8000
# open http://localhost:8000/?demo=1
```
`?demo=1` flips the app into demo mode (sample budget lines, transactions, config,
and a canned chat reply). `?demo=0` clears it.

**Worker + local D1**, bypassing Access for dev only:

```bash
cd worker
echo 'DEV_BYPASS_AUTH = "1"' > .dev.vars   # local only — never deploy this
wrangler d1 execute finances-db --local --file=../migration.sql
wrangler dev
```
`DEV_BYPASS_AUTH` is honored **only** when present in the environment (i.e. via
`.dev.vars` under `wrangler dev`); it is never set in production, so deployed
requests always go through full JWT verification.

---

## API

All routes require a valid Cloudflare Access JWT (`Cf-Access-Jwt-Assertion`).

| Method | Path | Notes |
|---|---|---|
| GET/POST | `/api/budget-lines` | list / create |
| PUT/DELETE | `/api/budget-lines/:id` | update / delete (409 if it has transactions) |
| GET | `/api/transactions?month=YYYY-MM` | list for a month |
| POST | `/api/transactions` | create |
| PUT/DELETE | `/api/transactions/:id` | update / delete |
| GET/PUT | `/api/config` | wealth + projection config (JSON blob) |
| GET | `/api/stats?month=YYYY-MM` | aggregates: income, expenses, by_budget_line, last_3_months |
| GET/POST/DELETE | `/api/chat` | history (50) / send / clear |

## Privacy

The chat endpoint sends Claude only the `/api/stats` aggregates + the réserves
config — **never** raw transactions. The system prompt instructs the assistant to
redirect transaction-level questions to the Historique tab.

## Replacing the icons

`public/icons/icon-192.png` and `icon-512.png` are auto-generated (navy "€"). Drop
in your own PNGs of the same sizes to rebrand.
