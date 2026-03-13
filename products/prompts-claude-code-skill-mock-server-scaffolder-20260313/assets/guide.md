# Claude Code Skill: Mock Server Scaffolder — Generate Instant API Mocks from Specs or Curl Examples

> For frontend developers and QA engineers, this skill generates fully functional mock server configurations from OpenAPI specs or raw curl examples so they can unblock UI development and testing without waiting for backend endpoints to be production-ready.

---

## What This Skill Does

Generates fully functional mock server configurations (MSW, json-server, or Express stubs) from OpenAPI specs or raw curl examples so frontend developers and QA engineers can unblock development without waiting for live backend endpoints.

**Best for:** Frontend Development, QA Engineering, API Integration

---

## Use Cases

**Frontend developer needs to build a dashboard UI before the backend REST API is ready**
  → `/mock-server generate from openapi.yaml --target msw --output src/mocks`

**QA engineer wants to simulate specific edge-case API responses (rate limits, 500 errors, empty states) for automated test coverage**
  → `/mock-server add-scenario error-states --status 429,503 --endpoint /api/orders`

**Developer has curl examples from API docs and needs runnable stubs immediately without writing boilerplate**
  → `/mock-server from-curl 'curl -X POST https://api.example.com/users -d {"name":"Alice"}' --target json-server`

**Team wants a shareable mock server that runs in CI for integration tests without any real backend dependency**
  → `/mock-server scaffold --target express --add-docker --output mock-server/`

---

## Configuration Steps

### Step 1: Create the skills directory and SKILL.md file

From your project root, run: `mkdir -p skills && touch skills/mock-server.md`. This is where Claude Code will discover and load the skill definition.

### Step 2: Populate SKILL.md with the mock server prompt and rules

Open `skills/mock-server.md` and paste the skill definition block. Include: (a) the skill's purpose and supported targets (MSW, json-server, Express), (b) parsing rules for OpenAPI YAML/JSON and raw curl strings, (c) output file structure conventions (e.g., `src/mocks/handlers.js` for MSW, `db.json` + `routes.json` for json-server), and (d) scenario scaffolding rules for success, empty, error, and delay variants.

### Step 3: Add input examples and output templates inside the SKILL.md

Inside the skill file, add a `## Examples` section with at least one OpenAPI snippet and one curl example paired with their expected generated output. For MSW, show a `rest.get('/api/users', ...)` handler block. For json-server, show a `db.json` with seed data. These few-shot examples dramatically improve Claude's output consistency.

### Step 4: Install mock server dependencies in your project

Run the appropriate install command based on your target: MSW: `npm install msw --save-dev && npx msw init public/`. json-server: `npm install json-server --save-dev`. Express stubs: `npm install express cors --save-dev`. Add a start script to `package.json`: `"mock": "json-server --watch mock-server/db.json --port 3001"` or equivalent.

### Step 5: Configure output directories and gitignore rules

Create the target output folder: `mkdir -p src/mocks` (MSW) or `mkdir -p mock-server` (json-server/Express). Add generated seed data files to `.gitignore` if they contain sensitive example payloads: echo 'mock-server/db.json' >> .gitignore. Commit the SKILL.md and handler scaffolds but treat large seed fixtures as ephemeral.

### Step 6: Validate the skill by running a generation command and testing the mock

Trigger the skill with: `/mock-server generate from openapi.yaml --target msw --output src/mocks`. Then start your dev server and confirm the mock intercepts requests by opening the browser network tab or running: `curl http://localhost:3001/api/users`. Iterate on the SKILL.md examples section if the output needs formatting adjustments.

---

## Ready-to-Use SKILL.md Template

Copy this file to your project's `skills/` directory:

```markdown

```

---

## Adapting for Different Fields

### Frontend Development

Target MSW (Mock Service Worker) as the default output so mocks run in the browser's service worker layer without a separate server process. Include realistic seed data with 5-10 records per collection, and scaffold delay simulation (`ctx.delay(800)`) to mimic real network latency during UI development.

### QA Engineering

Prioritize scenario-based generation: for every endpoint, produce separate handler variants for success (200), validation error (422), server error (500), unauthorized (401), and empty-state (200 with empty array). Output an Express server with a `/control` endpoint that lets tests switch active scenarios programmatically via HTTP, enabling headless automation without restarts.

### API Integration / Backend Teams

Generate a contract-first json-server setup that exactly mirrors the OpenAPI spec's schema shapes using JSON Schema Faker for synthetic data. Add a `routes.json` file that maps REST conventions and include a `Dockerfile` so the mock can run as a sidecar in Docker Compose alongside other services during local integration testing.

### Design / Prototyping

Generate a minimal json-server instance with human-readable, visually rich seed data (real names, product titles, image placeholder URLs from picsum.photos) rather than UUIDs and lorem text. Include a one-command startup script (`npm run mock`) so designers using tools like Framer or Storybook can wire live data without any Node.js expertise.

---

## Tips for Best Results

- Always include a `## Seed Data Rules` section in your SKILL.md that instructs Claude to generate realistic domain-specific data (e.g., e-commerce product names, not 'item1', 'item2') — this prevents placeholder data leaking into demos and screenshots.
- Add a `--watch` flag convention to your skill so Claude generates a file-watching setup by default; json-server supports this natively and it means your mock auto-reloads when you hand-edit `db.json` to tweak a test scenario mid-session.
- Store your OpenAPI spec path as a default in the SKILL.md frontmatter (e.g., `default_spec: ./docs/openapi.yaml`) so developers can run `/mock-server generate` with zero arguments and get a working output immediately, reducing adoption friction.

---

## Common Mistakes to Avoid

- Generating mocks without matching the exact response envelope your frontend expects (e.g., `{ data: [], meta: {} }` vs a bare array `[]`) — fix this by adding a `## Response Envelope` section to your SKILL.md that documents your API's wrapper structure so Claude wraps all generated handlers consistently.
- Forgetting to scope MSW handlers to only intercept in development/test environments, causing mocks to accidentally run in staging builds — fix by instructing the skill to wrap handler registration in `if (process.env.NODE_ENV !== 'production')` guards and adding that rule explicitly to the SKILL.md output template.
- Treating generated mock files as source-of-truth and manually editing them, then re-running the skill and losing changes — fix by establishing a `src/mocks/overrides/` directory convention in your SKILL.md where hand-crafted handlers live separately and are merged with generated ones at runtime, so regeneration never overwrites custom work.
