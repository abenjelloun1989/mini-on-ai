---
name: mock-server
title: "Mock Server Scaffolder — Generate Instant API Mocks from Specs or Curl Examples"
description: >
  Generates fully functional mock server configurations (MSW, json-server, or
  Express stubs) from OpenAPI specs or raw curl examples. Use this skill when
  frontend developers or QA engineers need to unblock UI development or test
  automation without waiting for live backend endpoints to be production-ready.
triggers:
  - /mock-server
tags:
  - frontend
  - testing
  - api
  - mocking
  - openapi
  - msw
  - json-server
  - express
---

# Mock Server Scaffolder

## Purpose

Generate fully functional mock server configurations from OpenAPI specs or raw curl examples so frontend developers and QA engineers can unblock UI development and testing without waiting for backend endpoints to be production-ready.

Supported output targets:

| Target | Best For |
|---|---|
| **MSW** (Mock Service Worker) | Browser-based React/Vue/Angular apps, Storybook, Vitest/Jest |
| **json-server** | Quick REST CRUD mocks with zero custom logic |
| **Express stubs** | Node.js environments, custom logic, middleware needs |

---

## When to Use This Skill

- A backend endpoint is not yet built or is unstable
- You need repeatable, deterministic API responses for UI component development
- You are writing frontend integration tests or E2E tests that must not hit real APIs
- You want to simulate error states, edge cases, or paginated responses
- You are demoing a feature before backend is complete

---

## How Claude Should Execute This Skill

When this skill is invoked, follow these steps precisely:

### Step 1 — Identify the Input Source

Determine what the user has provided:

- **OpenAPI/Swagger spec** (YAML or JSON, inline or file path)
- **One or more curl examples** (raw curl commands with headers and bodies)
- **Both** (use spec as the source of truth, curl examples to fill in missing response bodies)
- **Neither** — if no input is provided, ask the user to supply one before proceeding

### Step 2 — Identify the Target Framework

Check if the user specified a framework (`msw`, `json-server`, or `express`). If not specified, apply this default logic:

- If a `package.json` is present in the project, scan it for existing dependencies:
  - Found `msw` → use **MSW**
  - Found `json-server` → use **json-server**
  - Found `express` → use **Express stubs**
- If no clear signal, **default to MSW** as it is the most broadly applicable for modern frontend projects
- If the environment appears to be a pure Node.js/server project with no frontend framework, **default to Express stubs**

Always tell the user which target was selected and why before generating code.

### Step 3 — Parse the Input

**From OpenAPI spec:**
- Extract every path and HTTP method combination
- For each operation, read the `responses` block and extract example values or schema shapes
- If `examples` are defined, use them verbatim as response bodies
- If only a `schema` is defined, generate realistic placeholder data that matches the schema types and field names (use sensible fake values — not `string`, `0`, `true`, but `"jane.doe@example.com"`, `42`, `true`)
- Preserve response status codes exactly as defined in the spec
- Note any `requestBody` schemas so stub handlers can validate or echo back fields if needed

**From curl examples:**
- Parse the HTTP method, URL path, headers, and request body
- Infer the response body from context clues in the curl command or any inline comments the user provides
- If no response body is evident, generate a plausible response based on the endpoint path and method semantics (e.g., a `POST /users` likely returns a created user object with an `id`)
- Identify base URL or path prefix patterns across multiple curl examples

### Step 4 — Generate the Mock Configuration

Produce clean, runnable output for the selected target. Follow the format rules below.

---

## Output Format Rules by Target

### MSW (Mock Service Worker)

- Output a single `handlers.ts` (or `handlers.js` if no TypeScript signals detected) file
- Import from `msw` using the correct v2 API (`http` and `HttpResponse`)
- Group handlers by resource/domain using inline comments
- Export a named `handlers` array
- Include a `src/mocks/browser.ts` setup file if one does not already exist in the project
- Include a `src/mocks/server.ts` Node.js test server setup file for Jest/Vitest usage
- Add a brief comment at the top of each file explaining how to activate it

Example handler structure:

```ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  // Users
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: '1', name: 'Jane Doe', email: 'jane.doe@example.com' }
    ])
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: '2', ...body }, { status: 201 })
  }),
]
```

### json-server

- Output a `db.json` file containing realistic seed data for every resource
- Output a `routes.json` file if any path rewriting is needed (e.g., `/api/users` → `/users`)
- Output a `package.json` script suggestion as a comment block at the top of `db.json`
- If custom response logic is needed (delays, status codes, non-CRUD behavior), output a `server.js` middleware file alongside `db.json`

### Express Stubs

- Output a single `mock-server.js` (or `mock-server.ts`) file
- Use only `express` as the dependency (no extra packages unless `cors` is clearly needed)
- Define one route handler per endpoint
- Include a `listen` block at the bottom defaulting to port `3001` with a config comment
- Add middleware for `express.json()` and optional CORS header injection
- Include a startup comment block showing the exact command to run the server

---

## Step 5 — Output File Manifest

After generating all files, output a clear manifest listing:

1. Every file generated and its relative path
2. Install command for any new dependencies needed
3. The exact command to start or activate the mock server
4. Any manual steps required (e.g., adding a `<script>` tag for MSW service worker, running `npx msw init public/`)

Format the manifest as a numbered checklist the user can follow immediately.

---

## Constraints and Quality Rules

- **Never** generate `any` types in TypeScript output — infer proper types from schema or curl data
- **Never** use placeholder strings like `"string"`, `"number"`, `0` for fake data — generate semantically meaningful values
- **Always** match the exact HTTP status codes from the spec; do not default everything to `200`
- **Always** handle at least one error response per endpoint (404 for GET by ID, 422 or 400 for POST/PUT with bad body) unless the spec explicitly defines no error responses
- If the OpenAPI spec contains `$ref` references, resolve them before generating handlers — do not leave unresolved references in output
- If a path has path parameters (e.g., `/users/:id`), use the correct parameter syntax for the target framework (`/users/:id` for Express and json-server, `/users/:id` for MSW `http.get`)
- Keep all generated files self-contained and immediately runnable with no additional configuration beyond the manifest steps
- If generating TypeScript, add a brief `tsconfig` snippet in a comment if the project has no `tsconfig.json`

---

## Step 6 — Optional Enhancements (Offer After Core Output)

After delivering the core mock files, offer the following optional add-ons. Do not generate them automatically — ask the user which they want:

- **Delay simulation** — wrap responses with configurable latency to simulate slow networks
- **Error scenario variants** — a second handler set or feature flag that returns 500/503 responses for chaos testing
- **Pagination support** — generate paginated list responses with `page`, `limit`, `totalCount` envelope
- **Auth stub** — a `/auth/login` endpoint returning a fake JWT and a middleware that validates `Authorization: Bearer` headers
- **Postman collection** — export the same endpoints as a Postman collection JSON for sharing with the team

---

## Usage Examples

### Example 1 — Generate MSW handlers from an OpenAPI spec file

/mock-server openapi: ./api/openapi.yaml target: msw

Claude will read `./api/openapi.yaml`, extract all paths and response schemas, generate `src/mocks/handlers.ts`, `src/mocks/browser.ts`, and `src/mocks/server.ts`, and print the activation checklist.

---

### Example 2 — Generate a json-server mock from curl examples

/mock-server target: json-server curls:
  curl -X GET https://api.example.com/api/products -H "Authorization: Bearer token123"
  curl -X POST https://api.example.com/api/products -H "Content-Type: application/json" -d '{"name":"Widget","price":9.99,"stock":100}'
  curl -X GET https://api.example.com/api/products/42
  curl -X DELETE https://api.example.com/api/products/42

Claude will parse the four curl commands, infer the `products` resource shape, generate `db.json` with seed data, `routes.json` for the `/api` prefix, and print the `json-server` startup command.

---

### Example 3 — Auto-detect framework and generate from inline spec snippet

/mock-server

openapi: "3.0.0"
info:
  title: Orders API
  version: "1.0"
paths:
  /orders:
    get:
      summary: List orders
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id: { type: string }
                    status: { type: string, enum: [pending, shipped, delivered] }
                    total: { type: number }
  /orders/{id}:
    get:
      summary: Get order by ID
      responses:
        "200":
          description: OK
        "404":
          description: Not found

Claude will detect the framework from `package.json` (or default to MSW), generate handlers for `GET /orders` and `GET /orders/:id` including the 404 case, and output the file manifest.

---

## Notes for Claude

- Always confirm the detected or chosen target framework with the user before generating files
- If the input is ambiguous or incomplete, ask one focused clarifying question — do not generate partial output and do not ask multiple questions at once
- When generating fake data, prefer domain-coherent values: an `email` field should look like an email, an `orderId` should look like an order ID, a `createdAt` should be a valid ISO 8601 timestamp
- Treat the skill as a one-shot scaffold — the output should be paste-and-run ready with zero post-processing required from the user