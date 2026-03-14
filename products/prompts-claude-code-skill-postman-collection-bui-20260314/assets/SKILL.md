---
name: postman-builder
title: "Postman Collection Builder"
description: "Converts OpenAPI specs, markdown API docs, or raw endpoint lists into fully structured Postman collections with example payloads, auth configs, and environment variables. Designed for solutions engineers and technical support teams who need to onboard clients or reproduce issues without manual Postman setup."
version: 1.0.0
author: Claude Code
tags: [api, postman, openapi, documentation, testing, collections]
when_to_use: |
  Use this skill when you have an OpenAPI/Swagger spec, markdown API docs, a curl-based endpoint list,
  or any human-readable API reference and need a production-ready Postman collection exported as
  valid Postman Collection v2.1 JSON — complete with environment variables, example request bodies,
  and authentication configuration.
---

# Claude Code Skill: Postman Collection Builder

## Purpose

Transform API documentation or specifications into fully structured, ready-to-run Postman collections.
This skill is built for **solutions engineers** and **technical support teams** who need to:

- Onboard clients to an API without spending hours building collections by hand
- Reproduce customer-reported issues with pre-populated, realistic example payloads
- Share consistent, versioned collections across teams
- Bridge the gap between raw API documentation and working HTTP requests

Accepted input formats:

- **OpenAPI 3.x or Swagger 2.0** (YAML or JSON)
- **Markdown API documentation** (headers, code blocks, parameter tables)
- **Raw endpoint lists** (one per line, with optional HTTP method and description)
- **cURL command snippets** (one or many)
- **Any combination of the above**

---

## How Claude Should Execute This Skill

When this skill is invoked, follow these steps precisely.

### Step 1 — Parse and Inventory the Input

Read all provided input carefully. Build an internal inventory of every endpoint found, including:

- HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
- URL path (note any path parameters such as `{id}` or `:userId`)
- Query parameters and whether they are required or optional
- Request headers (especially `Content-Type`, `Accept`, `Authorization`)
- Request body schema (fields, types, example values)
- Response codes documented (for folder descriptions and notes)
- Any authentication scheme mentioned (Bearer token, API key, Basic, OAuth 2.0, no auth)

If the input is ambiguous or incomplete, make reasonable assumptions and document them in a `_skill_notes` field inside the exported collection's `info` description. Do not ask clarifying questions unless a critical piece of information — such as the base URL — is entirely absent from all input provided.

### Step 2 — Design the Collection Structure

Organize requests into **folders** based on the natural grouping found in the source material. Use these rules:

- Group by resource noun (e.g., `Users`, `Orders`, `Authentication`, `Webhooks`)
- If no grouping is apparent, group by HTTP method family (read operations vs. write operations)
- Place authentication requests (token exchange, login) in a top-level `Auth` folder
- Place health check or utility endpoints in a `Utilities` folder
- Preserve the order of endpoints as they appear in the source when possible
- Each folder should have a `description` summarizing what the resource represents

### Step 3 — Build Each Request Object

For every endpoint identified, construct a Postman request with:

**URL**
- Use `{{baseUrl}}` as the protocol-and-host placeholder
- Replace path parameters with Postman-style double-brace variables: `/users/{{userId}}`
- Add query parameters as individual key-value entries in the `query` array, not appended to the raw URL string

**Headers**
- Include `Content-Type: application/json` for any request with a body
- Include `Accept: application/json` for all requests unless the endpoint explicitly returns another type
- Add `Authorization: Bearer {{accessToken}}` for any endpoint marked as authenticated
- Add API-key headers using `{{apiKey}}` as the value placeholder

**Request Body**
- Use `raw` mode with `json` language for JSON bodies
- Populate example values that are realistic and human-readable:
  - Strings: use descriptive placeholders (`"John Doe"`, `"user@example.com"`, `"active"`)
  - IDs: use `"{{userId}}"` style variable references when the value comes from a prior request
  - Dates: use ISO 8601 format (`"2024-01-15T10:30:00Z"`)
  - Booleans: choose the most commonly expected default
  - Arrays: include one realistic item rather than an empty array
  - Numbers: use plausible values within any documented constraints
- For form-data or urlencoded bodies, use the appropriate Postman mode

**Description**
- Each request must have a `description` field summarizing:
  - What the endpoint does (one sentence)
  - Any required vs. optional parameters
  - Expected success response code
  - Any notable side effects or prerequisites (e.g., "Requires a valid session token from `POST /auth/login`")

**Tests (Pre-population)**
- Add a `Tests` script to every response that:
  - Asserts the expected success status code with `pm.test`
  - Parses the response body and saves important identifiers to collection variables
    (e.g., `pm.collectionVariables.set("userId", pm.response.json().data.id)`)
  - This enables chaining requests together in sequence during a demo or debugging session

### Step 4 — Build the Environment Template

Create a **separate JSON file** for a Postman environment named `{CollectionName} — Environment.json` containing:

| Variable | Initial Value | Notes |
|---|---|---|
| `baseUrl` | `https://api.example.com` | Replace with actual base URL |
| `accessToken` | `` | Populated by Auth request test script |
| `apiKey` | `` | Filled in manually by user |
| Any path/query params discovered | `` | One variable per unique parameter name |

Mark `accessToken` and `apiKey` as **secret** type (`"type": "secret"`) in the environment JSON.
All other variables use `"type": "default"`.

### Step 5 — Assemble and Output the Final Collection

Produce valid **Postman Collection Format v2.1** JSON. The root structure must be:

```
{
  "info": { "name", "description", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "item": [ ...folders and requests... ],
  "variable": [ ...collection-level variables if any... ],
  "auth": { ...top-level auth if uniform across all endpoints... },
  "event": [ ...collection-level pre-request scripts if needed... ]
}
```

**Output format:**

Deliver two artifacts in your response:

1. **`{CollectionName}.postman_collection.json`** — The full collection, pretty-printed with 2-space indentation
2. **`{CollectionName}.postman_environment.json`** — The environment template

Present each file in its own fenced code block labeled with the filename.

After the code blocks, provide a **Usage Guide** section in plain Markdown that explains:
- How to import both files into Postman (drag-and-drop or File > Import)
- Which variables to fill in before running
- The recommended request execution order (especially if requests must be chained)
- Any assumptions made during generation

---

## Constraints and Rules

- **Always** produce valid JSON that can be imported into Postman Desktop or Postman Web without modification
- **Never** include real credentials, real tokens, or real personal data in example values
- **Always** use collection variables (`{{variableName}}`) rather than hardcoding values into URLs or bodies
- **Always** add a test script to capture IDs and tokens from responses — this is what makes the collection actually useful in demos
- **Do not** add endpoints that were not present in the source input unless filling an obvious structural gap (e.g., a DELETE endpoint when only GET/POST/PUT were documented — note this as an assumption)
- **Do not** omit any endpoint from the source input — completeness is required
- If authentication type is ambiguous, default to Bearer token with `{{accessToken}}`
- If the base URL cannot be determined, use `https://api.example.com` and flag it prominently in the collection description and the Usage Guide

---

## Usage Examples

### Example 1 — OpenAPI Spec File

```
/postman-builder Convert the attached openapi.yaml into a Postman collection for our client onboarding package. The API uses Bearer token auth.
```

Claude will parse the YAML, group endpoints by tag or path prefix, generate example payloads from the spec schemas, configure Bearer auth at the collection level, and output both the collection JSON and the environment JSON along with import instructions.

---

### Example 2 — Markdown API Documentation

```
/postman-builder Here is our internal API documentation in markdown. Build a Postman collection I can share with the support team to reproduce issues. [paste markdown content]
```

Claude will extract every endpoint described in the markdown (including those in code blocks and tables), build realistic example payloads, add chaining test scripts so IDs flow between requests, and flag any ambiguities in the Usage Guide.

---

### Example 3 — Raw Endpoint List

```
/postman-builder Convert these endpoints into a Postman collection with environment variables. We use an x-api-key header for auth.

GET    /v1/customers
POST   /v1/customers
GET    /v1/customers/:id
PATCH  /v1/customers/:id
DELETE /v1/customers/:id
GET    /v1/customers/:id/subscriptions
POST   /v1/subscriptions
POST   /v1/auth/token
```

Claude will organize the endpoints into `Auth`, `Customers`, and `Subscriptions` folders, add an `x-api-key: {{apiKey}}` header to all requests, build sensible example bodies for the POST and PATCH endpoints, write test scripts that capture the customer ID from create responses and pass it into subsequent requests, and produce both output files.

---

## Notes for Maintainers

- This skill targets **Postman Collection Format v2.1** specifically. Do not use the legacy v1 format.
- The Postman schema reference URL is: `https://schema.getpostman.com/json/collection/v2.1.0/collection.json`
- Environment file format follows the Postman environment schema: each variable is an object with `key`, `value`, `type`, and `enabled` fields
- When updating this skill, test output by importing generated JSON into Postman Desktop and verifying zero import errors before releasing