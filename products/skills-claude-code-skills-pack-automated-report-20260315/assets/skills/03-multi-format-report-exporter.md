---
name: multi-format-report-exporter
trigger: /export-report
description: >
  Generates a complete export pipeline that renders a finished report into one
  or more target formats from a single shared data payload. Supports PDF
  (print-ready via Puppeteer/WeasyPrint), CSV (raw tabular data), and Slack
  Block Kit messages. Use this skill when a report is ready and needs to be
  distributed in multiple formats without duplicating rendering logic.
tags: [reporting, export, pdf, csv, slack, automation]
pack: Claude Code Skills Pack — Automated Report Generation
---

# Skill: Multi-Format Report Exporter

## Purpose

Produce a clean, production-ready export pipeline that accepts a single
normalized report payload and fans it out to one or more output formats:

- **PDF** — print-ready, styled document using an HTML template rendered via
  Puppeteer (Node) or WeasyPrint (Python)
- **CSV** — flat tabular export of raw data rows with headers, suitable for
  spreadsheet ingestion
- **Slack Block Kit** — structured message blocks with summary stats, a data
  table excerpt, and a download link section

The pipeline must be format-agnostic at the data layer — the same payload
drives all renderers.

---

## When to Use This Skill

- A report template already exists and data has been populated into it
- The report needs to reach multiple audiences in different formats
- You want to avoid per-format data transformation logic scattered across files
- You are building or extending a scheduled report distribution system

---

## Execution Instructions

Follow these steps in order when `/export-report` is invoked.

### Step 1 — Parse the Command Arguments

Extract arguments from the invocation:

- `--formats` — comma-separated list: `pdf`, `csv`, `slack` (required; at least one)
- `--report` — path to the report data file or inline payload identifier (required)
- `--output-dir` — directory for file outputs (default: `./exports`)
- `--slack-channel` — Slack channel ID or name (required only when `slack` is a target format)
- `--title` — human-readable report title used in headers and filenames
- `--date` — report date string, ISO 8601 preferred (default: today)

If `--formats` is missing or empty, halt and return an error message listing
required arguments.

### Step 2 — Inspect the Report Payload

Read the report data file or object. Validate that it contains:

1. A `metadata` block with at least `title`, `date`, and `generated_by`
2. A `summary` block with key-value stats (used in PDF header and Slack summary)
3. A `rows` array of uniform objects representing tabular data
4. An optional `sections` array for multi-section PDF layouts

If any required block is missing, output a clear error and stop. Do not
silently skip formats.

### Step 3 — Generate the Shared Data Adapter

Create a single adapter module (`reportAdapter.js` or `report_adapter.py`)
that:

- Accepts the raw report payload
- Exposes typed accessors: `getMetadata()`, `getSummaryStats()`, `getRows()`,
  `getSections()`
- Normalizes date formats to ISO 8601
- Truncates or paginates large `rows` arrays for Slack (max 10 rows in preview)

All renderers must import from this adapter. No renderer should parse the raw
payload directly.

### Step 4 — Generate Each Requested Renderer

Generate only the renderers that match the `--formats` argument.

#### PDF Renderer

- Use an HTML template with inline CSS (no external stylesheets, for portability)
- Include: report title, date, generated-by line, summary stats table,
  full data table, page numbers in footer
- Use Puppeteer (Node) or WeasyPrint (Python) based on the project stack
- Output filename: `{title}-{date}.pdf` in `--output-dir`
- Ensure tables do not break across pages (`page-break-inside: avoid` on rows)

#### CSV Renderer

- Extract headers from the keys of the first row object
- Write a header row followed by data rows, all comma-separated
- Escape values containing commas, quotes, or newlines per RFC 4180
- Output filename: `{title}-{date}.csv` in `--output-dir`
- Include a metadata comment block at the top (lines prefixed with `#`) with
  title, date, and row count

#### Slack Renderer

- Build a Block Kit payload (JSON) with these block sections in order:
  1. `header` block — report title
  2. `section` block — date and generated-by as context
  3. `section` block — summary stats formatted as a two-column `fields` list
     (max 10 fields per Slack limit)
  4. `divider` block
  5. `section` block — data preview table as a Markdown code block (max 10 rows)
  6. `actions` block — buttons for "Download PDF" and "Download CSV" if those
     formats were also generated (use placeholder URLs if paths are local)
  7. `context` block — row count and truncation notice if applicable
- Post via `chat.postMessage` using the Slack Web API client
- Log the `ts` (timestamp) of the sent message for audit purposes

### Step 5 — Generate the Orchestrator

Create a single entry-point script (`exportReport.js` or `export_report.py`)
that:

1. Loads and validates the report payload
2. Instantiates the adapter
3. Runs each requested renderer in parallel where possible
4. Collects results: `{ format, status, outputPath, error }`
5. Prints a final summary table to stdout
6. Exits with code `0` if all requested formats succeeded, `1` if any failed

### Step 6 — Output the File Manifest

After generating all files, print a manifest listing every file created,
its purpose, and any configuration the user must supply (API tokens, output
paths, etc.).

---

## Constraints and Quality Rules

- **Single payload, multiple renderers** — never duplicate data transformation
  logic across renderer files
- **No runtime format detection** — format selection happens at invocation
  time; renderers do not check `--formats` internally
- **Graceful partial failure** — if one renderer fails, others must still run
  and complete; report all failures at the end
- **No hardcoded credentials** — all API tokens and webhook URLs must be read
  from environment variables
- **RFC 4180 compliance** — CSV output must be valid per spec; test edge cases
  (empty cells, quoted strings, special characters)
- **Slack Block Kit limits** — respect the 50-block-per-message and 10-field
  limits; never exceed them silently
- **Filename sanitization** — strip special characters from titles before
  using them in filenames
- **Idempotent output** — re-running with the same arguments overwrites
  existing output files cleanly without error

---

## Output Format

Generated files should follow this structure:

  exports/
    {title}-{date}.pdf
    {title}-{date}.csv
  src/
    reportAdapter.js         # or report_adapter.py
    renderers/
      pdfRenderer.js         # or pdf_renderer.py
      csvRenderer.js         # or csv_renderer.py
      slackRenderer.js       # or slack_renderer.py
    exportReport.js          # or export_report.py (orchestrator)

---

## Usage Examples

### Example 1 — All three formats

  /export-report --formats pdf,csv,slack --report ./data/weekly-kpis.json --title "Weekly KPIs" --date 2025-01-27 --slack-channel C08XXXXXXX

Generates the PDF, CSV, and Slack Block Kit renderer. Posts the Slack message
to channel C08XXXXXXX. Creates `Weekly-KPIs-2025-01-27.pdf` and
`Weekly-KPIs-2025-01-27.csv` in `./exports`.

### Example 2 — CSV and Slack only, custom output directory

  /export-report --formats csv,slack --report ./data/monthly-revenue.json --output-dir ./dist/reports --title "Monthly Revenue" --slack-channel C09XXXXXXX

Skips PDF renderer entirely. Generates only the CSV renderer and Slack
renderer. Outputs CSV to `./dist/reports/Monthly-Revenue-{today}.csv`.

### Example 3 — PDF only for print distribution

  /export-report --formats pdf --report ./data/exec-summary.json --title "Executive Summary" --date 2025-01-27 --output-dir ./print-ready

Generates only the PDF renderer and orchestrator. No Slack or CSV code is
produced. Useful for board-level print distributions where raw data export
is not appropriate.

---

## Environment Variables Required

  SLACK_BOT_TOKEN        # Slack Bot OAuth token (xoxb-...)
  SLACK_SIGNING_SECRET   # For request verification if using a web endpoint
  EXPORT_OUTPUT_DIR      # Optional override for --output-dir default

---

## Notes for Claude

- If the project already has a PDF or CSV utility, inspect it before
  generating a new one and extend it rather than duplicate.
- If the stack is ambiguous, ask whether the project is Node or Python before
  generating any code.
- Always generate the adapter module first; renderers depend on it.
- If `--slack-channel` is omitted and `slack` is in `--formats`, ask for it
  before proceeding — do not generate a placeholder.