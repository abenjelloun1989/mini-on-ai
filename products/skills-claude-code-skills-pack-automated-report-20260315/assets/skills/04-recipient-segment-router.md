---
name: recipient-segment-router
trigger: /segment-recipients
description: >
  Builds recipient segmentation logic that maps report variants, data scopes,
  and delivery channels to the correct audience groups based on role, team, or
  subscription rules. Use this skill when you need to define, generate, or
  update the routing layer that decides who receives which version of a report,
  through which channel, and with what data scope applied.
when_to_use: >
  Invoke this skill whenever a report has multiple audiences with different
  data access levels, delivery preferences, or format requirements. Ideal for
  weekly/monthly recurring reports sent to mixed audiences (executives, team
  leads, individual contributors, external stakeholders) where a single
  report variant would be inappropriate or a security/privacy risk.
---

# Skill: Recipient Segment Router

## Purpose

Generate production-ready recipient segmentation logic for automated report
distribution. This skill produces a routing configuration (YAML or JSON),
a resolver module (Python), and a validation report confirming that every
defined recipient maps to exactly one segment with no gaps or conflicts.

---

## Inputs Expected from the User

Before executing, confirm you have the following. If any are missing, ask
the user to supply them before proceeding.

1. **Report name** — the report this segmentation applies to
2. **Recipient list or source** — a raw list, CSV, directory path, or
   description of where recipients live (e.g., "pull from `teams.yaml`")
3. **Segmentation dimensions** — the rules that define groups, such as:
   - Role (e.g., `executive`, `team_lead`, `analyst`, `external`)
   - Team or department (e.g., `engineering`, `finance`, `marketing`)
   - Subscription tier or opt-in flags
   - Data scope restrictions (e.g., `org-wide`, `team-only`, `own-data`)
4. **Delivery channels per segment** — e.g., Slack DM, email, PDF attachment,
   CSV download link, dashboard link
5. **Report variants per segment** — which template or filter each segment
   receives (references the `parameterized-report-template` skill outputs
   if used in this pack)
6. **Conflict resolution rule** — what to do when a recipient matches
   multiple segments (e.g., `most_restrictive`, `highest_priority`, `all`)

---

## Execution Steps

### Step 1 — Parse and Normalize Recipients

- Load the recipient list from the provided source.
- Normalize fields: deduplicate, standardize role labels to lowercase snake_case,
  flag any recipients with missing role or team attributes.
- Output a normalized recipient table as an in-memory structure. Do not write
  to disk yet.

### Step 2 — Define Segment Rules

- For each segment dimension provided, generate a named segment block with:
  - `segment_id` (snake_case, unique)
  - `match_criteria` (field + operator + value, e.g., `role == "executive"`)
  - `data_scope` (what data filter applies)
  - `report_variant` (template ID or filter key)
  - `delivery_channels` (ordered list)
  - `priority` (integer, used for conflict resolution)
- If the user has not specified all segments, infer reasonable defaults based
  on the role/team dimensions provided and flag them clearly as `[INFERRED]`
  so the user can confirm or override.

### Step 3 — Build the Routing Configuration File

Generate a `recipient_segments.yaml` file with the structure:

  report_name: <report_name>
  conflict_resolution: <rule>
  segments:
    - segment_id: ...
      match_criteria: ...
      data_scope: ...
      report_variant: ...
      delivery_channels: [...]
      priority: <int>

Place this file at `reports/config/recipient_segments.yaml` unless the user
specifies a different path.

### Step 4 — Generate the Resolver Module

Create `reports/routing/segment_resolver.py` with:

- A `SegmentResolver` class that:
  - Loads `recipient_segments.yaml` on init
  - Exposes `resolve(recipient: dict) -> list[SegmentMatch]` method
  - Applies conflict resolution logic
  - Returns a list of `SegmentMatch` objects, each containing:
    `segment_id`, `data_scope`, `report_variant`, `delivery_channels`
- A `resolve_all(recipients: list[dict]) -> dict[str, list[SegmentMatch]]`
  convenience method that returns a mapping of recipient identifier to matches
- Type hints on all public methods
- Inline docstrings explaining match logic and conflict resolution behavior

### Step 5 — Run Validation

Execute a dry-run validation pass over the normalized recipient list:

- Every recipient must match at least one segment → flag unmatched as `UNROUTED`
- No recipient should produce ambiguous results unless `conflict_resolution`
  is set to `all` → flag conflicts as `CONFLICT`
- Channel references must be from the allowed set:
  `[email, slack_dm, slack_channel, pdf, csv, dashboard_link]`
- Report variants referenced must exist in `reports/templates/` (check file
  presence; warn if missing but do not block generation)

Output a `routing_validation_report.md` at `reports/logs/` with:
- Summary counts: total recipients, routed, unrouted, conflicts
- A table of any flagged recipients with their issue type and suggested fix
- A confirmation line per segment showing how many recipients it matched

### Step 6 — Summarize and Hand Off

Print a concise summary to the user covering:
- Files created and their paths
- Segment count and recipient coverage percentage
- Any `[INFERRED]` segments that need user confirmation
- Any unrouted or conflicted recipients requiring action
- Next-step suggestion (e.g., "Run `/schedule-reports` to attach this routing
  config to your delivery schedule")

---

## Constraints and Quality Rules

- **No PII in logs**: recipient email addresses or names must be masked in
  `routing_validation_report.md` (show only recipient ID or index)
- **Deterministic output**: given the same inputs, the resolver must produce
  identical segment assignments every run
- **Segment IDs are stable**: once generated, do not rename segment IDs across
  runs; additions are additive only, to avoid breaking downstream references
- **Conflict resolution must be explicit**: never silently drop a recipient
  from delivery — always route to the most restrictive match if unspecified
- **YAML over JSON** for the config file unless the user's project already
  uses JSON configs (check for `package.json` or `.json` config files in root)
- **Python 3.10+** for the resolver module; use `match` statements for
  conflict resolution logic where appropriate
- **No hardcoded credentials or channel webhook URLs** in generated files;
  reference environment variables or a secrets config instead

---

## Output Files Summary

  reports/
    config/
      recipient_segments.yaml       ← Segment routing configuration
    routing/
      segment_resolver.py           ← Python resolver class and methods
    logs/
      routing_validation_report.md  ← Dry-run validation results

---

## Usage Examples

### Example 1 — Role-Based Segmentation for a Weekly Metrics Report

  /segment-recipients \
    report="Weekly Growth Metrics" \
    recipients="data/recipients.csv" \
    segments="executive=org-wide+PDF+email, team_lead=team-only+CSV+slack_dm, analyst=own-data+CSV+slack_dm" \
    conflict_resolution="most_restrictive"

Claude will parse `recipients.csv`, create three segments mapped to role values
in the CSV, assign data scopes and delivery channels, generate the YAML config
and Python resolver, and validate full recipient coverage.

---

### Example 2 — Subscription-Based Segmentation with External Recipients

  /segment-recipients \
    report="Monthly Partner Digest" \
    recipients="crm/contacts.yaml" \
    segments="internal_exec=full_data+PDF, internal_team=summary+CSV, external_partner=redacted+PDF+email" \
    conflict_resolution="highest_priority"

Claude will create a three-tier segment structure distinguishing internal from
external recipients, apply a `redacted` data scope to external partners to
restrict sensitive fields, and flag any contacts in `crm/contacts.yaml`
missing a `type` field as `UNROUTED` in the validation report.

---

### Example 3 — Updating Existing Segments to Add a New Team

  /segment-recipients \
    report="Ops Weekly Scorecard" \
    existing_config="reports/config/recipient_segments.yaml" \
    add_segment="data_engineering=team-only+CSV+slack_channel:#data-alerts" \
    new_recipients="ops_team_additions.csv"

Claude will load the existing config, append the new segment without modifying
existing segment IDs, merge the new recipient list, re-run validation against
the full combined recipient set, and output an updated YAML config and
refreshed validation report showing delta coverage.

---

## Related Skills in This Pack

- `parameterized-report-template` — defines the report variants referenced
  by `report_variant` in segment configs
- `report-scheduler` — consumes `recipient_segments.yaml` to attach routing
  rules to scheduled delivery jobs
- `delivery-audit-logger` — reads `SegmentMatch` outputs at send time to
  record which segment each delivery was attributed to