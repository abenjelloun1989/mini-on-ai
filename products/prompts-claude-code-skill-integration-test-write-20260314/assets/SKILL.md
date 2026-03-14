---
name: integration-test-writer
title: Integration Test Writer
description: Reads API endpoint definitions, request/response schemas, and example payloads to auto-generate structured integration test suites with full coverage of happy paths, edge cases, and error scenarios. Designed for QA engineers and full-stack developers who want consistent API coverage without writing boilerplate test code from scratch.
version: 1.0.0
author: Claude Code
tags: [testing, api, integration, qa, automation]
---

# Integration Test Writer

## Purpose

This skill generates comprehensive integration test suites from API endpoint definitions, request/response schemas, and example payloads. It produces ready-to-run test files covering happy paths, edge cases, authentication scenarios, and error conditions — eliminating the need to write repetitive boilerplate test code by hand.

## When to Use This Skill

Invoke this skill when you need to:

- Generate integration tests for one or more REST or GraphQL API endpoints
- Achieve consistent test coverage across a new or existing API surface
- Onboard a new endpoint into an existing test suite quickly
- Audit coverage gaps in a current integration test file
- Scaffold tests from an OpenAPI/Swagger spec, Postman collection, or inline endpoint definition

Do **not** use this skill for unit tests, end-to-end UI tests, or load/performance testing. Those concerns are out of scope.

---

## How to Execute This Skill

When this skill is invoked, follow these steps in order. Do not skip steps or assume information that has not been provided.

### Step 1 — Gather Source Material

Identify and read the endpoint definitions available in the current project. Check for the following sources in priority order:

1. An OpenAPI/Swagger spec file (`openapi.yaml`, `openapi.json`, `swagger.yaml`, `swagger.json`)
2. A Postman collection (`*.postman_collection.json`)
3. Route definition files (e.g., Express router files, FastAPI route decorators, Rails routes, Django URL patterns)
4. A dedicated API documentation file (`API.md`, `docs/api.md`, `docs/endpoints.md`)
5. Inline schema or payload examples provided directly in the slash-command invocation

If no source material is found, **stop and ask the user** to provide one of the above before proceeding.

### Step 2 — Detect Project Context

Scan the project to determine:

- **Language**: TypeScript, JavaScript, Python, Go, Java, Ruby, etc.
- **Test framework already in use**: Jest, Vitest, Pytest, Go test, RSpec, JUnit, Mocha, etc. Match the existing framework if one is present. If none is detected, default to the most idiomatic framework for the detected language.
- **HTTP client convention**: Check for existing test files to detect whether the project uses `supertest`, `httpx`, `requests`, `net/http/httptest`, `RestAssured`, or similar. Mirror that pattern.
- **Base URL / test environment config**: Look for `.env.test`, `jest.config.*`, `pytest.ini`, `conftest.py`, or similar config files that declare a `BASE_URL` or `TEST_HOST`. Use those values; do not hardcode production URLs.
- **Authentication pattern**: Detect Bearer token, API key header, cookie session, OAuth, or no auth. Infer from existing test fixtures or the spec.

### Step 3 — Parse Endpoints

For each endpoint to be tested, extract:

- HTTP method (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
- Path including any path parameters (e.g., `/users/{id}`)
- Required and optional query parameters
- Request headers (especially `Content-Type`, `Authorization`, `Accept`)
- Request body schema and example payloads (required fields, optional fields, data types, constraints)
- Expected response schemas for each status code documented
- Any documented error responses (`400`, `401`, `403`, `404`, `409`, `422`, `500`, etc.)

### Step 4 — Generate Test Cases

For each endpoint, generate the following categories of tests. Label each test with a clear, descriptive name that reads like a sentence.

#### Happy Path Tests
- Valid request with all required fields → assert expected `2xx` status and response body shape
- Valid request with all optional fields included
- Valid request with only required fields (no optional fields)
- Paginated endpoints: first page, last page, middle page

#### Validation & Edge Case Tests
- Missing required field → assert `400` or `422`
- Invalid data type for a field (e.g., string where integer expected) → assert `400` or `422`
- Field value at boundary (max length string, zero, negative number, empty array)
- Field value exceeding boundary (string over max length, number over max value)
- Extra unexpected fields in the request body (assert the API ignores or rejects them per spec)
- Empty request body when body is required

#### Authentication & Authorization Tests
- Request with valid credentials → assert `2xx`
- Request with missing auth header/token → assert `401`
- Request with malformed or expired token → assert `401`
- Request with valid token but insufficient permissions → assert `403` (only if roles/scopes are defined in the spec)

#### Error Scenario Tests
- Resource not found (invalid ID) → assert `404`
- Conflict on duplicate creation → assert `409` (only where applicable per spec)
- Method not allowed on a path → assert `405`
- Unsupported `Content-Type` header → assert `415` (only where applicable)

#### Data Integrity Tests (when the spec or schema implies state)
- After a `POST` creates a resource, a subsequent `GET` returns it
- After a `DELETE`, a subsequent `GET` returns `404`
- After a `PUT`/`PATCH`, a subsequent `GET` reflects the updated values

Do not fabricate test cases for scenarios the spec does not document or imply. If a scenario is ambiguous, add a `TODO` comment in the test noting the assumption.

### Step 5 — Apply Project Conventions

Before writing the output file:

- Match the indentation, quote style, and import ordering found in existing test files
- Use the same test lifecycle hooks (`beforeAll`, `afterAll`, `setUp`, `tearDown`, etc.) already present in the project
- Reuse any existing helper utilities (`createTestUser`, `getAuthToken`, `seedDatabase`, etc.) found in `test/`, `tests/`, `spec/`, or `__tests__/` directories
- Place the generated file in the same directory as existing integration test files, following the naming convention already in use (e.g., `users.integration.test.ts`, `test_users_api.py`, `users_spec.rb`)
- If no convention is detectable, use the pattern `[resource].integration.test.[ext]`

### Step 6 — Write the Output File

Write the complete, immediately runnable test file. The file must:

- Import all required dependencies at the top
- Include a single top-level `describe` / test suite block named after the API resource or endpoint group
- Nest sub-blocks by category (Happy Path, Validation, Auth, Errors, Data Integrity)
- Contain no placeholder values such as `YOUR_TOKEN_HERE` or `FILL_ME_IN` — use environment variables, fixture helpers, or generated test data instead
- Include a comment block at the top of the file listing the source it was generated from and the date

After writing the file, print a short summary table listing:

| Endpoint | Method | Tests Generated | Categories Covered |
|---|---|---|---|

### Step 7 — Report Coverage Gaps

After generating the file, explicitly state any scenarios that could **not** be covered due to missing information in the source material. Format these as a bulleted list:

- What is missing
- Why it matters
- What the user should provide to fill the gap

---

## Constraints and Rules

- **Never** hardcode real credentials, PII, or production URLs in test files
- **Never** modify existing test files unless the user explicitly asks you to merge into them
- **Always** use environment variables for base URLs, secrets, and API keys
- **Always** generate tests that are independent and can run in any order unless the spec explicitly requires ordered state (in which case, note this with a comment)
- **Always** assert both the HTTP status code **and** the response body structure, not just the status code
- If the user provides a specific endpoint path in the invocation (e.g., `/api/v1/orders`), scope generation to that endpoint only
- If the user asks to generate tests for an entire spec file, process all endpoints but group them into separate `describe` blocks per resource tag or path prefix
- Do not generate tests for deprecated endpoints unless explicitly asked

---

## Output Format

The primary output is a single test file written to disk. Additionally, print to the terminal:

1. The full path of the file written
2. The summary table (Step 6)
3. The coverage gap report (Step 7)

If multiple files are generated (one per resource), list all paths written.

---

## Examples

### Example 1 — Generate tests for a single endpoint from an OpenAPI spec

/integration-test-writer generate tests for POST /api/v1/users from openapi.yaml

Claude will:
- Read `openapi.yaml` and locate the `POST /api/v1/users` operation
- Detect the project language and test framework
- Generate a test file at the appropriate path (e.g., `tests/integration/users.integration.test.ts`)
- Cover: valid user creation, missing required fields, duplicate email conflict, unauthenticated request, field validation errors

---

### Example 2 — Generate a full test suite from a Postman collection

/integration-test-writer generate full integration test suite from payments.postman_collection.json using pytest

Claude will:
- Parse all requests in the Postman collection
- Group them by folder/resource into `describe`-equivalent blocks in Pytest
- Generate one test file per resource group (e.g., `tests/integration/test_charges_api.py`, `tests/integration/test_refunds_api.py`)
- Use `httpx` or `requests` depending on what is already present in the project
- Report any requests in the collection that lacked example responses and could not have assertions generated

---

### Example 3 — Extend an existing test file with missing edge cases

/integration-test-writer audit and add missing edge cases to tests/integration/orders.test.ts

Claude will:
- Read the existing `orders.test.ts` file and the relevant route/schema definitions
- Identify which test categories (validation, auth, error scenarios) are absent or incomplete
- Append the missing test cases to the existing file in the matching style
- Print a before/after coverage comparison

---

## Reference: Test Framework Defaults by Language

If no existing test framework is detected, use these defaults:

| Language | Default Framework | Default HTTP Client |
|---|---|---|
| TypeScript / JavaScript | Jest | supertest |
| Python | Pytest | httpx |
| Go | `testing` + `net/http/httptest` | standard library |
| Ruby | RSpec | rack-test / Faraday |
| Java | JUnit 5 | RestAssured |
| PHP | PHPUnit | Guzzle |
| Rust | `#[cfg(test)]` + `reqwest` | reqwest |