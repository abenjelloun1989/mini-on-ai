---
name: gen-data-contract
trigger: /gen-data-contract
description: >
  Generates a formal data contract definition for a dataset, including schema
  specification, field-level expectations, ownership metadata, and SLA
  commitments. Use this skill whenever you need to establish a shared agreement
  between data producers and consumers about the structure, quality, and
  availability of a dataset.
tags: [data-quality, contracts, schema, validation, sla]
version: 1.0.0
---

# Skill: gen-data-contract

## Purpose

Produce a complete, versioned data contract document for a given dataset. The
contract serves as the authoritative reference for schema structure, field-level
quality rules, ownership, and SLA commitments — making implicit agreements
explicit before they become production incidents.

Use this skill when:
- Onboarding a new data source into a pipeline
- Formalizing expectations between a data producer (e.g., application team) and a data consumer (e.g., analytics team)
- Establishing a baseline before writing validation checks or anomaly detection rules
- Documenting changes to an existing dataset as part of a schema migration

---

## Inputs

Claude will collect the following information before generating the contract.
If the user provides a file, table DDL, sample rows, or a description, extract
what you can. Prompt only for what is genuinely missing.

| Input | Required | Notes |
|---|---|---|
| Dataset name | Yes | e.g., `orders`, `user_events`, `inventory_snapshot` |
| Source system or platform | Yes | e.g., Postgres, Snowflake, Kafka topic, S3 path |
| Schema / field list | Yes | DDL, JSON schema, CSV header, or prose description |
| Owner team or contact | Yes | Team name and/or email |
| Consumer(s) | Recommended | Who reads this data and for what purpose |
| Update frequency | Recommended | e.g., real-time, hourly, daily at 06:00 UTC |
| SLA requirements | Recommended | Freshness window, uptime, acceptable latency |
| Known business rules | Optional | e.g., `order_total` must equal sum of line items |
| Environment | Optional | prod / staging / dev — defaults to prod |

If the user runs `/gen-data-contract` with no arguments, ask a short series of
clarifying questions (one message, bulleted) before generating.

---

## Execution Steps

Follow these steps in order. Do not skip steps.

**Step 1 — Parse inputs**
Extract all available information from the user's message, attached files, or
visible file context. Identify which required inputs are missing.

**Step 2 — Clarify gaps (if needed)**
If any required input is missing, ask for it in a single, concise message.
List missing items as bullets. Do not generate the contract until required
inputs are satisfied.

**Step 3 — Infer field metadata**
For each field in the schema:
- Infer the logical data type (string, integer, float, boolean, timestamp, date, uuid, enum)
- Determine nullable vs. required status based on context clues or ask if ambiguous
- Assign a semantic category: identifier, measure, dimension, timestamp, flag, foreign_key
- Draft a plain-English description (1 sentence) if not provided

**Step 4 — Draft field-level expectations**
For each field, generate at least one quality rule. Use the format:
`[rule_type]: [condition]`

Common rule types: `not_null`, `unique`, `accepted_values`, `min_value`,
`max_value`, `regex_match`, `referential_integrity`, `row_count_range`,
`freshness_threshold`.

**Step 5 — Define SLA commitments**
Translate the stated or inferred update frequency into concrete SLA terms:
- Freshness: maximum acceptable age of latest record at query time
- Availability: expected uptime percentage (default 99.5% if not specified)
- Incident response: how quickly data issues should be escalated (default P2 = 4 hrs)

**Step 6 — Assemble and output the contract**
Render the complete contract using the Output Format defined below.

**Step 7 — Suggest next steps**
After the contract, append a short "Next Steps" section (3–5 bullet points)
recommending related actions such as running `/gen-validation-checks` or
scheduling freshness monitoring.

---

## Output Format

Render the data contract as a YAML document inside a fenced code block.
Follow the structure below exactly. Do not omit top-level keys even if values
are null or TBD.

```yaml
data_contract:
  metadata:
    contract_id: "<dataset_name>-contract-v<version>"
    version: "1.0.0"
    status: "draft"            # draft | active | deprecated
    created_date: "<YYYY-MM-DD>"
    last_updated: "<YYYY-MM-DD>"
    dataset_name: "<name>"
    description: "<one or two sentence description>"
    source_system: "<system or platform>"
    environment: "<prod | staging | dev>"

  ownership:
    producer_team: "<team name>"
    producer_contact: "<email or Slack handle>"
    consumer_teams:
      - name: "<team name>"
        use_case: "<brief description>"
    data_steward: "<name or TBD>"
    escalation_path: "<e.g., #data-incidents Slack channel>"

  schema:
    table_or_topic: "<fully qualified name>"
    fields:
      - name: "<field_name>"
        type: "<logical type>"
        nullable: <true|false>
        semantic_category: "<identifier|measure|dimension|timestamp|flag|foreign_key>"
        description: "<plain-English description>"
        pii: <true|false>
        expectations:
          - "not_null"
          - "<additional rule>"
      # repeat for each field

  quality_rules:
    table_level:
      - rule: "row_count_range"
        min: <integer or null>
        max: <integer or null>
        notes: "<context>"
      - rule: "no_duplicate_primary_key"
        key_fields: ["<field1>", "<field2>"]
    freshness:
      - field: "<timestamp field>"
        max_age: "<e.g., 25 hours>"
        severity: "<warning | critical>"

  sla:
    update_frequency: "<human-readable schedule>"
    freshness_sla: "<maximum acceptable age at query time>"
    availability_sla: "<percentage>"
    incident_response:
      p1_threshold: "<condition that triggers P1>"
      p1_response_time: "<e.g., 1 hour>"
      p2_threshold: "<condition that triggers P2>"
      p2_response_time: "<e.g., 4 hours>"
    change_notification: "<e.g., 5 business days notice for breaking changes>"

  versioning:
    changelog:
      - version: "1.0.0"
        date: "<YYYY-MM-DD>"
        author: "<TBD>"
        summary: "Initial contract definition."
    breaking_change_policy: >
      Any removal or type change to an existing field is a breaking change
      and requires a new major version with 5 business days advance notice
      to all registered consumers.
```

After the YAML block, include a brief **Validation Summary** as a Markdown
table listing each field alongside its rule count and highest-severity
expectation.

---

## Quality Rules

- Every field must have at least one expectation.
- Primary key fields must carry both `not_null` and `unique`.
- Any field named or typed as a timestamp must have a `freshness_threshold` or
  `max_age` rule unless explicitly marked as historical/append-only.
- PII fields must be flagged `pii: true`. Do not invent masking rules unless
  the user provides a masking policy — instead add a TODO comment.
- Do not fabricate business rules. If a business rule is uncertain, mark it
  `severity: warning` and add a `# REVIEW:` comment inline.
- Keep field descriptions factual and free of jargon.
- Version must follow semver. New contracts always start at `1.0.0`.

---

## Constraints

- Output only valid YAML. Run a mental lint pass before responding.
- Do not include placeholder values like `"string"` for the type — use the
  actual inferred or stated type.
- If the schema has more than 30 fields, group fields by logical domain and
  note the grouping in a comment.
- Never expose credentials, connection strings, or raw PII examples even if
  the user pastes them in sample data.
- If sample rows are provided, use them to infer `accepted_values` ranges or
  formats but do not echo raw row data into the contract.

---

## Usage Examples

### Example 1 — Provide a DDL directly

```
/gen-data-contract

Table: analytics.orders (Snowflake, prod)
Owner: Data Platform team — data-platform@company.com
Consumers: Finance (revenue reporting), Growth (funnel analysis)
SLA: refreshed hourly, data must be < 2 hours old at query time

DDL:
CREATE TABLE analytics.orders (
  order_id       VARCHAR(36)    NOT NULL,
  user_id        VARCHAR(36)    NOT NULL,
  created_at     TIMESTAMP_NTZ  NOT NULL,
  status         VARCHAR(20)    NOT NULL,
  order_total    NUMERIC(12,2)  NOT NULL,
  discount_code  VARCHAR(50),
  updated_at     TIMESTAMP_NTZ  NOT NULL
);
```

Claude will generate a complete contract with seven field definitions, infer
`status` as an enum, flag `order_id` as a UUID identifier, set a freshness
SLA of 2 hours on `updated_at`, and prompt for accepted status values.

---

### Example 2 — Minimal invocation with follow-up questions

```
/gen-data-contract  user_events Kafka topic
```

Claude will respond with a single clarifying message asking for the schema
(field list), owner, consumers, and update frequency before generating.

---

### Example 3 — Attach a CSV header for a file-based source

```
/gen-data-contract

Source: S3 daily drop at s3://data-lake/inventory/snapshot=YYYY-MM-DD/
Owner: Supply Chain Analytics — scdata@company.com
Schedule: daily at 03:00 UTC

CSV header:
sku_id,warehouse_id,quantity_on_hand,quantity_reserved,last_counted_at,is_active
```

Claude will infer types from field names and semantic conventions, flag
`last_counted_at` for a freshness rule, mark `is_active` as a boolean flag,
and note that `quantity_on_hand` and `quantity_reserved` should have
`min_value: 0` constraints.

---

## Next Steps (appended to every output)

After generating the contract, always recommend:

- Run `/gen-validation-checks` to turn field expectations into executable dbt tests or Great Expectations suites.
- Run `/gen-anomaly-rules` to add statistical monitoring on numeric measures.
- Run `/gen-freshness-monitor` to implement the SLA freshness check as an automated alert.
- Commit the contract YAML to your data catalog or `contracts/` directory in version control.
- Schedule a 30-minute review with the producer team to confirm business rules before setting status to `active`.