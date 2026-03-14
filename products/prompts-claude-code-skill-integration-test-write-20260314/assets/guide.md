# Claude Code Skill: Integration Test Writer — Auto-Generate API Integration Tests from Endpoint Definitions

> For QA engineers and full-stack developers, this skill reads endpoint definitions, request/response schemas, and example payloads to generate structured integration test suites so they can achieve consistent API coverage without writing boilerplate test code from scratch.

---

## What This Skill Does

Reads API endpoint definitions, request/response schemas, and example payloads to auto-generate structured integration test suites with full coverage of happy paths, edge cases, and error scenarios.

**Best for:** QA Engineering, Full-Stack Development, Backend Development

---

## Use Cases

**A new REST API module has been built and needs integration tests before merging to main**
  → `/integration-test-writer generate tests for src/api/routes/payments.ts using the OpenAPI spec at docs/openapi.yaml`

**A QA engineer needs to retroactively add test coverage to undocumented legacy endpoints**
  → `/integration-test-writer reverse-engineer tests from src/controllers/UserController.js and write output to tests/integration/users.test.ts`

**A developer adds a new endpoint and wants tests generated from the request/response Zod or JSON schema definitions**
  → `/integration-test-writer scaffold tests for the POST /orders endpoint using src/schemas/order.schema.ts and sample payloads in fixtures/orders/`

**Team wants to ensure all error codes and edge cases (401, 404, 422, 500) are covered across an entire API surface**
  → `/integration-test-writer audit-coverage for all routes in src/api/ and generate missing edge-case tests into tests/integration/`

---

## Configuration Steps

### Step 1: Create the skills directory and SKILL.md file

From your project root, run: `mkdir -p skills && touch skills/integration-test-writer.md`. This registers the skill with Claude Code so it can be invoked via slash command.

### Step 2: Populate SKILL.md with context, rules, and output format

Open `skills/integration-test-writer.md` and define: (1) the skill's purpose, (2) which files to read (e.g. OpenAPI specs, schema files, fixture payloads), (3) the test framework to use (e.g. Jest + Supertest, Vitest, Pytest + httpx), (4) output file naming convention (e.g. `tests/integration/{resource}.test.ts`), and (5) required test categories: happy path, auth failure, validation errors, not-found, and server error simulation.

### Step 3: Add fixture and schema discovery instructions to the skill

Inside `skills/integration-test-writer.md`, instruct Claude to look for source files in this priority order: `docs/openapi.yaml` or `docs/openapi.json` → `src/schemas/` → `src/routes/` or `src/controllers/` → `fixtures/` or `__fixtures__/`. Add a line: 'If no spec file is found, infer request/response shape from the route handler source code directly.'

### Step 4: Install required testing dependencies

For Node.js projects run: `npm install --save-dev jest supertest @types/supertest ts-jest`. For Python projects run: `pip install pytest httpx pytest-asyncio`. Add a `jest.config.ts` or `pytest.ini` if one does not exist, and ensure `testMatch` or `testpaths` includes `tests/integration/`.

### Step 5: Create a sample fixture to validate skill output

Add a minimal fixture at `fixtures/sample-endpoint.json` containing one valid request body and one intentionally invalid body. Then invoke the skill: `claude /integration-test-writer generate tests for GET /health and POST /users using fixtures/sample-endpoint.json` and verify the output file appears at `tests/integration/users.test.ts` with grouped describe blocks.

### Step 6: Commit and document the skill for your team

Run `git add skills/integration-test-writer.md` and commit. Update your project README with a section: 'Integration Test Generation — run `/integration-test-writer generate tests for <endpoint> using <spec-file>` to auto-scaffold tests. Output lands in `tests/integration/`.' This ensures consistent team adoption.

---

## Ready-to-Use SKILL.md Template

Copy this file to your project's `skills/` directory:

```markdown

```

---

## Adapting for Different Fields

### QA Engineering

Focus the SKILL.md on generating tests that map to test case IDs and acceptance criteria from Jira or TestRail. Add instructions to include comments like `// TC-1042: POST /users returns 422 when email is missing` and group tests by severity (P0 smoke, P1 regression) using describe block labels.

### Full-Stack Development

Configure the skill to generate both frontend API client mock tests and backend integration tests simultaneously. Instruct Claude to read the same OpenAPI spec to produce a `tests/integration/api.test.ts` for Supertest and a `src/api/__mocks__/` folder for MSW handlers used in component tests.

### Backend / Platform Engineering

Extend the skill to generate contract tests using Pact or Dredd alongside standard integration tests. Add a rule: 'For each endpoint, also output a Pact consumer contract file to `tests/contracts/{consumer}-{provider}.pact.json` derived from the request/response schema.'

### DevOps / CI Engineering

Adapt the skill to produce tests that are CI-pipeline-aware: include environment variable placeholders like `process.env.API_BASE_URL`, generate a `tests/integration/setup.ts` that reads from `.env.test`, and output a GitHub Actions job snippet to `docs/ci-integration-tests.yml` showing how to run the generated suite in a containerized environment.

---

## Tips for Best Results

- Always point the skill at the most authoritative source of truth first — an OpenAPI or AsyncAPI spec produces far more accurate tests than inferring from route handler code. If your project lacks a spec, use this skill as a forcing function to create one.
- Use the `fixtures/` folder aggressively. The more real-world example payloads you provide (valid, boundary-value, and malformed), the richer the generated edge-case tests will be. Name fixture files descriptively: `fixtures/users/create-missing-email.json` rather than `fixture2.json`.
- After generating tests, always run them immediately with `npx jest tests/integration/ --verbose` and feed any failures back to Claude with context. Say: 'This test failed with: [error]. Adjust the generated test to match the actual API behavior.' This creates a tight feedback loop that improves accuracy fast.

---

## Common Mistakes to Avoid

- Pointing the skill at a stale or partial OpenAPI spec and accepting the output as complete. Always verify the spec matches the actual deployed routes by cross-referencing with the router file (`src/routes/index.ts`) before generating — otherwise tests will assert against endpoints that no longer exist or miss newly added ones.
- Generating all tests into a single flat file instead of organizing by resource. This makes the suite hard to maintain. Explicitly tell Claude in your SKILL.md: 'Create one test file per resource (e.g. `users.test.ts`, `orders.test.ts`) inside `tests/integration/`, never a single monolithic file.'
- Forgetting to include auth setup in the generated tests, causing every authenticated endpoint test to return 401 and appear broken. Add a rule to your SKILL.md: 'Always generate a `beforeAll` block that obtains a test JWT via `POST /auth/token` using credentials from `process.env.TEST_USER` and `process.env.TEST_PASSWORD`, and attach it to subsequent requests.'
