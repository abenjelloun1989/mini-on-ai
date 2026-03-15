---
name: delivery-audit-logger
trigger: /log-report-delivery
version: 1.0.0
description: >
  Instruments a delivery audit logging layer that records every report dispatch
  event — recipient, format, timestamp, status, and error detail — to a
  structured log store. Use this skill whenever you need full traceability of
  report delivery activity, SLA compliance monitoring, or a reliable audit trail
  for debugging failed or delayed dispatches.
when_to_use: >
  Invoke after wiring up any report distribution step (email, Slack, PDF export,
  CSV drop) to ensure every delivery attempt is captured. Also use to retrofit
  audit logging onto an existing report pipeline that currently has no delivery
  visibility.
tags: [reporting, audit, logging, observability, sla, delivery]
---

# Skill: Delivery Audit Logger

## Purpose

Create or extend a structured audit logging layer that captures every report
delivery event with enough detail to answer: *Who received what, when, in what
format, did it succeed, and if not — why?*

The output is a production-ready logging module wired into the existing report
dispatch flow, writing structured records to a configurable log store.

---

## Execution Instructions

Follow these steps in order. Do not skip steps or combine them unless explicitly
instructed.

### Step 1 — Discover the Existing Delivery Surface

1. Scan the codebase for report dispatch callsites:
   - Search for send/deliver/export function calls related to reports
   - Identify email clients, Slack SDK calls, file-write operations, and HTTP
     delivery endpoints
   - Note the language, framework, and any existing logging infrastructure
     (Winston, Pino, Python logging, structlog, etc.)
2. Check whether a log store already exists (database table, log file, external
   service like Datadog, Splunk, or CloudWatch).
3. Record your findings in a short discovery summary before writing any code.

### Step 2 — Define the Audit Log Schema

Every audit record MUST include these fields:

| Field | Type | Required | Description |
|---|---|---|---|
| event_id | UUID v4 | Yes | Unique identifier for this delivery event |
| report_id | string | Yes | Identifier of the report being delivered |
| report_name | string | Yes | Human-readable report name |
| recipient_id | string | Yes | Stable identifier for the recipient (email, user ID, channel ID) |
| recipient_type | enum | Yes | One of: `email`, `slack_channel`, `slack_user`, `webhook`, `filesystem` |
| format | enum | Yes | One of: `pdf`, `csv`, `json`, `xlsx`, `html`, `text` |
| dispatched_at | ISO 8601 | Yes | Timestamp of dispatch attempt (UTC) |
| delivered_at | ISO 8601 | No | Timestamp of confirmed delivery (if available) |
| status | enum | Yes | One of: `success`, `failed`, `pending`, `retrying` |
| attempt_number | integer | Yes | Starts at 1; increments on retry |
| error_code | string | No | Machine-readable error code on failure |
| error_detail | string | No | Human-readable error message on failure |
| delivery_channel | string | Yes | The delivery method used (e.g., `sendgrid`, `slack_api`, `s3`, `smtp`) |
| file_size_bytes | integer | No | Size of the delivered artifact if applicable |
| triggered_by | string | Yes | `schedule`, `manual`, `api`, or the user/job ID that triggered it |
| metadata | object | No | Arbitrary key-value pairs for pipeline-specific context |

Do not omit required fields. Do not rename fields.

### Step 3 — Build the Audit Logger Module

Create a self-contained logger module with these responsibilities:

1. **`logDeliveryAttempt(params)`** — Call this immediately before dispatch.
   Writes a `pending` record and returns the `event_id`.

2. **`logDeliverySuccess(eventId, deliveredAt, fileSizeBytes?)`** — Call this
   on confirmed delivery. Updates the record to `success`.

3. **`logDeliveryFailure(eventId, errorCode, errorDetail, willRetry)`** — Call
   this on any dispatch error. Updates status to `failed` or `retrying`.

4. **`getDeliveryHistory(reportId?, recipientId?, fromDate?, toDate?)`** —
   Returns paginated audit records matching the given filters. Used for SLA
   dashboards and debugging.

Design constraints:
- The logger MUST NOT throw exceptions that interrupt the delivery flow. Wrap
  all I/O in try/catch and emit a `logger_error` to stderr if the audit write
  itself fails.
- All timestamps MUST be UTC ISO 8601 strings.
- Log records MUST be written atomically where the target store supports it.
- The module MUST be injected with its storage adapter — do not hardcode the
  store.

### Step 4 — Implement Storage Adapters

Provide at least the adapter(s) that match the discovered infrastructure. If
none exists, default to the **structured file adapter**.

**Structured File Adapter** (default fallback)
- Writes newline-delimited JSON (NDJSON) to a configurable file path
- Rotates logs daily by default using date-suffix filenames
- File path defaults to `./logs/report-delivery-audit.ndjson`

**Database Adapter** (if a DB is present)
- Writes to a `report_delivery_audit` table
- Include the DDL migration to create the table
- Use parameterized queries only — no string interpolation

**External Service Adapter** (if Datadog, Splunk, CloudWatch, etc. detected)
- Use the service's structured logging SDK
- Tag all events with `source:report-delivery-audit`

### Step 5 — Instrument the Delivery Callsites

For each dispatch callsite identified in Step 1:

1. Import the audit logger module
2. Call `logDeliveryAttempt` before the dispatch call, capturing `event_id`
3. Call `logDeliverySuccess` or `logDeliveryFailure` inside the response handler
4. Preserve all existing error handling — do not replace it, only augment it
5. Add a code comment: `// AUDIT: delivery logged via delivery-audit-logger`

### Step 6 — Add SLA Helper Utilities

Create a lightweight `slaMonitor` utility with:

- **`getFailureRate(reportId, windowHours)`** — Returns the failure percentage
  for a report over the given time window
- **`getLateDeliveries(scheduledTime, toleranceMinutes)`** — Returns deliveries
  where `dispatched_at` exceeded `scheduledTime + toleranceMinutes`
- **`getPendingStuck(thresholdMinutes)`** — Returns records stuck in `pending`
  longer than the threshold (default: 30 minutes)

### Step 7 — Output a Verification Checklist

After generating all files, output a markdown checklist the developer can use
to verify the integration is working:

- [ ] Audit table/file created and writable
- [ ] `logDeliveryAttempt` called before every dispatch
- [ ] `logDeliverySuccess` / `logDeliveryFailure` called in all code paths
- [ ] No audit I/O error causes a delivery failure
- [ ] Sample log record matches schema exactly
- [ ] `getDeliveryHistory` returns filterable results
- [ ] SLA helpers return correct counts on test data

---

## Output Format Rules

- Generate separate files: `auditLogger.js` (or `.ts`, `.py` etc.), storage
  adapter file(s), SLA monitor file, and the DB migration if applicable
- Use the language and style conventions found in the existing codebase
- All functions must include JSDoc / docstring comments
- Include a `README-audit-logger.md` explaining configuration and usage
- Do not generate test files unless explicitly requested

## Quality Constraints

- Zero hardcoded credentials or file paths — all configurable via environment
  variables or constructor injection
- Logger module must be stateless and safe to instantiate multiple times
- All enum fields must be validated at runtime with a clear error on invalid value
- Code must be lintable with no warnings under the project's existing linter

---

## Usage Examples

### Example 1 — Retrofit audit logging onto an existing email report pipeline

/log-report-delivery

Context: We have a Node.js service in ./src/reports/emailDispatcher.js that
sends weekly PDF reports via SendGrid. No audit logging exists today. We want
every send attempt recorded to a Postgres database so we can track delivery SLA.

### Example 2 — Add audit logging to a Slack digest and CSV file drop

/log-report-delivery

Context: Python 3.11 project. Reports are sent to Slack channels via
slack_sdk and CSV files are written to an S3 bucket. We already use structlog.
Log to both structlog (for live streaming) and a SQLite file for historical
query. Include SLA helpers.

### Example 3 — Audit logger for a multi-channel report with retry logic

/log-report-delivery

Context: TypeScript monorepo, ./packages/report-runner. Reports are dispatched
via email, Slack, and webhook simultaneously. The dispatcher already has retry
logic with exponential backoff. Log each attempt number separately and flag
any report that fails all 3 retries for a given recipient.

---

## Notes for Claude

- Always complete Step 1 discovery before writing any code. Assumptions about
  the stack that turn out wrong waste more time than the discovery takes.
- If the user has not specified a log store, default to the file adapter and
  note that it can be swapped for a DB or external service adapter later.
- If the project already has a logging library, wrap it rather than introducing
  a new dependency.
- When instrumenting callsites, never silently swallow delivery errors to make
  room for audit calls — the audit layer is additive only.