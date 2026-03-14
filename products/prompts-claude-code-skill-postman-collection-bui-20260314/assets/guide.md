# Claude Code Skill: Postman Collection Builder — Convert API Docs or Specs into Ready-to-Run Postman Collections

> For solutions engineers and technical support teams, this skill transforms OpenAPI specs, markdown API documentation, or raw endpoint lists into fully structured Postman collections with example payloads and environment variables so they can onboard clients and reproduce issues faster without manual collection setup.

---

## What This Skill Does

Converts OpenAPI specs, markdown API docs, or raw endpoint lists into fully structured Postman collections with example payloads, auth configs, and environment variables.

**Best for:** Solutions Engineering, Technical Support, Developer Relations, API Integration

---

## Use Cases

**A client onboarding call is tomorrow and you need a working Postman collection from their OpenAPI 3.0 spec so the team can demo live API calls without manual setup**
  → `/postman-builder generate a full Postman collection from ./docs/openapi.yaml with sandbox environment variables and example payloads for every endpoint`

**A support ticket reports a broken webhook flow and you need to reproduce it quickly by importing endpoints from a markdown README into Postman with the exact headers and body the client is using**
  → `/postman-builder build a Postman collection from ./docs/README.md focusing on the /webhooks endpoints with the reported auth headers and error-case example bodies`

**You have a raw list of REST endpoints copied from internal wiki and need them organized into a Postman collection with folders by resource, pre-request scripts, and a dev/prod environment file**
  → `/postman-builder convert this endpoint list into a Postman collection with folders grouped by resource type and generate both dev and prod environment JSON files`

**A new solutions engineer needs to run a full API smoke test against a prospect's environment and requires a ready-to-import collection with parameterized base URLs and API keys as variables**
  → `/postman-builder create a smoke-test Postman collection from ./specs/partner-api.json with all auth tokens and base URLs as environment variables named for easy handoff`

---

## Configuration Steps

### Step 1: Create the skills directory and SKILL.md file

From your project root, run: `mkdir -p skills && touch skills/postman-builder.md`. This is where Claude Code will look for skill instructions when you invoke `/postman-builder`.

### Step 2: Populate the SKILL.md with collection-building instructions

Open `skills/postman-builder.md` and paste the full skill prompt. The prompt should instruct Claude to: parse the input source (OpenAPI YAML/JSON, markdown, or plain text), extract all endpoints with methods/paths/params/bodies, generate a valid Postman Collection v2.1 JSON structure, create an environment JSON file with variables like `{{base_url}}`, `{{api_key}}`, `{{version}}`, group requests into folders by resource or tag, and write output files to `./postman/` with names like `collection.json` and `environment-dev.json`.

### Step 3: Add example source files for testing the skill

Place a sample spec or doc in your project: `cp your-api-spec.yaml ./docs/openapi.yaml`. If you don't have one, create `./docs/sample-endpoints.md` with a short markdown list of endpoints. These serve as test inputs to verify the skill output is valid before client use. Run `ls ./docs/` to confirm files are present.

### Step 4: Configure output directory and validate JSON output

Run `mkdir -p postman` to ensure the output directory exists. After invoking the skill, validate the generated collection with: `npx @stoplight/spectral-cli lint ./postman/collection.json` or import directly into Postman desktop and use Collection > Run to confirm all requests populate correctly. For CI pipelines, add `newman run ./postman/collection.json -e ./postman/environment-dev.json` to your test script.

### Step 5: Add a .claudeignore or context note for sensitive specs

If your API specs contain internal auth secrets or PII schemas, add sensitive file patterns to `.claudeignore` or prepend a note in your skill invocation: 'strip all real credentials and replace with placeholder variable names'. Also add `postman/` to `.gitignore` if collections will contain environment-specific details: `echo 'postman/environment-prod.json' >> .gitignore`.

---

## Ready-to-Use SKILL.md Template

Copy this file to your project's `skills/` directory:

```markdown

```

---

## Adapting for Different Fields

### Solutions Engineering

Focus the skill prompt on generating client-ready collections with clean naming, onboarding comments inside each request description field, and a dedicated 'Quick Start' folder with the 3-5 most critical flows a new client would run first. Include a pre-request script that auto-refreshes OAuth tokens.

### Technical Support

Adapt the skill to produce debug-oriented collections that include error-case example bodies (4xx/5xx payloads), request logging via Postman test scripts that print response codes to the console, and folders named after common support ticket categories like 'Auth Issues', 'Rate Limiting', and 'Webhook Failures'.

### Developer Relations

Configure the skill to output collections optimized for public sharing: include rich markdown descriptions in every request, add 'Try It' example values that work against a public sandbox, generate a README.md alongside the collection explaining import steps, and structure folders to mirror the official API documentation sections.

### API Integration / Partnerships

Tune the skill to produce multi-environment collections (dev, staging, prod) with a single environment switch variable, add partner-specific auth header patterns, and generate a separate 'Integration Checklist' folder with requests that validate the partner has correctly configured webhooks, scopes, and callback URLs.

---

## Tips for Best Results

- Always specify the Postman Collection schema version in your skill prompt (target v2.1 — `https://schema.getpostman.com/json/collection/v2.1.0/collection.json`) because v2.0 and v2.1 are not interchangeable and Postman's import will silently mishandle variables in older formats.
- Instruct Claude to use `{{double_curly_braces}}` consistently for ALL values that vary by environment — including paths like `/v{{api_version}}/users` — so the collection works immediately after importing the companion environment file without any manual find-and-replace.
- After generation, run a quick smoke test with Newman before handing off to clients: `npx newman run ./postman/collection.json -e ./postman/environment-dev.json --reporters cli,json --reporter-json-export ./postman/results.json`. This catches broken JSON structure or missing variable references before the client sees them.

---

## Common Mistakes to Avoid

- Hardcoding real API keys or base URLs directly in the collection JSON instead of using environment variables — avoid this by explicitly instructing Claude in the skill prompt: 'replace all credential values and hostnames with named environment variables and list every variable in the companion environment file with a placeholder value like REPLACE_ME'.
- Generating a flat collection with no folder structure when the source spec has 30+ endpoints — the resulting collection is unusable in Postman's sidebar. Fix this by specifying in your prompt: 'group all requests into folders using the OpenAPI tags field or the first path segment as the folder name, and nest sub-resources as sub-folders'.
- Forgetting to include Content-Type headers and example request bodies for POST/PUT/PATCH endpoints — Claude will sometimes omit bodies if the spec's `requestBody` schema is complex. Prevent this by adding to your skill prompt: 'for every non-GET endpoint, generate a realistic example request body using the schema definitions and set the Content-Type header explicitly'.
