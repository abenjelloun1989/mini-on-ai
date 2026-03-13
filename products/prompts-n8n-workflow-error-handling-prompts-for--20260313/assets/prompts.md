# n8n Workflow Error Handling Prompts for Automation Builders

> n8n automation builders get 20 targeted prompts to systematically diagnose, document, and resolve node failures, retry logic gaps, and silent error conditions in production workflows.

---

## Prompts (20 total)

### 1. Diagnose Silent Node Failure Root Cause

**Use case:** Debugging workflows that complete but produce wrong or empty results

```
I have an n8n workflow named [WORKFLOW NAME] that is failing silently — it completes without errors but produces no output or incorrect output. The workflow does the following: [BRIEF WORKFLOW DESCRIPTION]. The node where I suspect the issue is: [NODE NAME AND TYPE]. Here is the node configuration or any relevant output data: [PASTE NODE CONFIG OR OUTPUT]. Please help me: 1) Identify the most likely root causes for silent failures in this type of node, 2) Provide a step-by-step diagnostic checklist I can follow inside n8n, 3) Suggest specific expressions or test inputs to expose the hidden failure, and 4) Recommend how to add visibility into this node so failures surface immediately in future runs.
```

### 2. Build Robust Retry Logic Strategy

**Use case:** Adding reliable retry logic to API-dependent workflow nodes

```
I am building an n8n workflow that calls an external API: [API NAME OR ENDPOINT]. This API occasionally returns 429 (rate limit), 503 (service unavailable), or timeout errors. My workflow currently has no retry logic. Please provide: 1) A detailed explanation of how to configure n8n's built-in retry-on-fail settings for this node, 2) The recommended retry count and wait time values for this type of API, 3) How to implement exponential backoff using n8n's Wait node or Function node if built-in retry is insufficient, 4) A code snippet (JavaScript) for a Function node that handles retry logic with exponential backoff, and 5) How to distinguish between retryable errors and permanent failures so I don't retry unnecessarily.
```

### 3. Design Error Branch for Any Node

**Use case:** Building dedicated error handling branches for critical workflow nodes

```
I want to add a proper error-handling branch to a specific node in my n8n workflow. The node is: [NODE NAME AND TYPE], and it performs the following action: [DESCRIBE WHAT THE NODE DOES]. When this node fails, I need to: [DESCRIBE DESIRED FAILURE BEHAVIOR, e.g., notify via Slack, log to a database, retry once, stop the workflow]. Please provide: 1) Step-by-step instructions to enable and configure the 'On Error' output on this node type in n8n, 2) A recommended error branch structure with specific nodes to use, 3) The exact n8n expressions to extract error message, error code, and timestamp from the error object, 4) How to include the original input data in the error notification so I can replay the failed item, and 5) A JSON template for a structured error log entry.
```

### 4. Write Error Notification Message Template

**Use case:** Creating professional error alerts with all context needed to act fast

```
I need to create a professional, actionable error notification message for my n8n workflow. This notification will be sent via [CHANNEL: e.g., Slack, Email, PagerDuty] whenever the workflow named [WORKFLOW NAME] fails. The primary audience for this notification is [AUDIENCE: e.g., developers, operations team, business stakeholders]. Please write: 1) A complete notification message template using n8n expression syntax ({{ }}) that includes workflow name, node that failed, error message, timestamp, execution ID, and a link to the execution log, 2) A shorter summary version for SMS or mobile push notifications, 3) Guidance on which error details are most useful for each audience type, 4) Instructions on how to configure this in n8n's Error Trigger node and connect it to [CHANNEL], and 5) A severity classification system (P1/P2/P3) with criteria for each level.
```

### 5. Audit Workflow for Error Handling Gaps

**Use case:** Systematically finding error handling weaknesses before production deployment

```
I want to perform a comprehensive error handling audit of my n8n workflow. Here is a description of my workflow's structure and nodes: [PASTE WORKFLOW DESCRIPTION OR NODE LIST]. Please act as a senior automation engineer and: 1) Identify every node type in my workflow that is a high-risk failure point and explain why, 2) List specific error handling gaps — nodes that have no error branch, no retry logic, or no data validation, 3) Rank the gaps by risk level (high/medium/low) with justification, 4) Provide a prioritized remediation plan with specific actions for each gap, 5) Suggest a minimum viable error handling standard I should apply to every production n8n workflow going forward, and 6) Provide a reusable audit checklist I can use for all future workflows.
```

### 6. Handle Partial Batch Failure Gracefully

**Use case:** Managing workflows where only some batch items fail during processing

```
My n8n workflow processes items in batches. Sometimes a subset of items fail while others succeed. The workflow processes [DESCRIBE WHAT IS BEING PROCESSED, e.g., 'customer records from a CSV']. The node that processes each item is: [NODE NAME AND TYPE]. I need a strategy to handle partial failures without losing successful results or silently skipping failed items. Please provide: 1) How to configure the 'Continue on Fail' setting correctly for batch processing in n8n, 2) An approach to separate successful items from failed items after batch processing using n8n expressions, 3) A Function node JavaScript snippet that categorizes items into success and failure arrays, 4) How to write failed items to a [STORAGE: e.g., Google Sheet, Airtable, database table] for later review and replay, 5) How to send a batch summary notification showing X succeeded and Y failed, and 6) A strategy for replaying only the failed items without re-running the entire workflow.
```

### 7. Create Dead Letter Queue Pattern

**Use case:** Building a system to capture, store, and replay all failed workflow items

```
I want to implement a dead letter queue (DLQ) pattern in my n8n workflow to capture and store all failed items for later inspection and replay. My workflow processes [DESCRIBE DATA BEING PROCESSED] and currently loses failed items permanently. Please provide: 1) A complete architecture diagram description for a DLQ pattern using n8n nodes, 2) Step-by-step instructions to route failed items to a [STORAGE DESTINATION: e.g., Airtable base, PostgreSQL table, Google Sheet] including the exact node configuration, 3) The recommended data schema for the DLQ storage including fields for error details, original payload, timestamp, retry count, and status, 4) A companion 'DLQ Replay' sub-workflow design that reads from the DLQ, re-processes items, and updates their status, 5) How to add a maximum retry limit to prevent infinite replay loops, and 6) A monitoring query or filter to identify items stuck in the DLQ for more than [TIME PERIOD].
```

### 8. Debug n8n Expression Evaluation Errors

**Use case:** Fixing broken n8n expressions that return errors or unexpected null values

```
I have an n8n workflow where a node is throwing an expression evaluation error or returning undefined/null when I expect valid data. The failing expression is: [PASTE YOUR EXPRESSION]. The node where this expression is used is: [NODE NAME AND TYPE]. The input data coming into this node looks like: [PASTE SAMPLE INPUT JSON]. The error message I see is: [PASTE ERROR MESSAGE IF AVAILABLE]. Please: 1) Analyze my expression and identify exactly why it is failing or returning unexpected results, 2) Provide the corrected expression with a detailed explanation of what was wrong, 3) Explain the n8n expression evaluation context — how $json, $item, $node, and $input work and when to use each, 4) Show me how to safely access nested data with null-safety to prevent future undefined errors, 5) Provide 3 alternative ways to write this expression with trade-offs for each, and 6) List the top 5 most common n8n expression mistakes and how to avoid them.
```

### 9. Document Workflow Error Handling Architecture

**Use case:** Creating professional documentation for workflow error handling systems

```
I need to create comprehensive documentation for the error handling architecture of my n8n workflow named [WORKFLOW NAME]. This documentation will be read by [AUDIENCE: e.g., new team members, external auditors, DevOps engineers]. The workflow does the following: [DESCRIBE WORKFLOW PURPOSE AND MAIN STEPS]. Please generate: 1) A structured documentation template with sections covering: overview, error handling strategy, node-level error configurations, notification routing, escalation procedures, and known failure modes, 2) A table listing each critical node, its failure modes, handling strategy, and recovery steps, 3) A runbook section with step-by-step troubleshooting procedures for the 5 most likely failure scenarios, 4) A glossary of n8n-specific error handling terms for non-technical readers, 5) Mermaid diagram syntax for a flowchart showing the error handling flow, and 6) A changelog template to track error handling updates over time.
```

### 10. Validate Input Data Before Processing

**Use case:** Preventing downstream failures by validating data at workflow entry points

```
I want to add robust input data validation to my n8n workflow before data reaches any processing nodes. My workflow receives input data from: [DATA SOURCE: e.g., webhook, form submission, scheduled trigger, API]. The data I expect to receive looks like this: [DESCRIBE OR PASTE EXPECTED DATA STRUCTURE]. Critical fields that must be present and valid are: [LIST REQUIRED FIELDS AND THEIR EXPECTED TYPES/FORMATS]. Please provide: 1) A complete Function node JavaScript code snippet that validates all required fields, checks data types, and validates formats (email, phone, date, URL, etc.), 2) How to use n8n's IF node to route valid and invalid data to separate branches, 3) A structured validation error response format that identifies which fields failed and why, 4) How to send invalid data to a [NOTIFICATION METHOD] with details about what was wrong, 5) Strategies to sanitize and normalize data (trim whitespace, standardize dates) before validation, and 6) How to log validation failures for later analysis.
```

### 11. Handle API Rate Limit Errors Intelligently

**Use case:** Gracefully managing API rate limits to prevent workflow failures

```
My n8n workflow is hitting rate limits on [API NAME]. The API returns the following when rate limited: [DESCRIBE THE RATE LIMIT RESPONSE, e.g., HTTP 429 with Retry-After header]. My workflow currently makes approximately [NUMBER] API calls per [TIME PERIOD]. Please provide: 1) A strategy to detect rate limit responses specifically in n8n HTTP Request or [SPECIFIC NODE] nodes, 2) How to read and use the Retry-After header or X-RateLimit-Reset value to wait the correct amount of time, 3) A Function node code snippet that implements intelligent rate limit handling with dynamic wait times, 4) How to throttle my workflow proactively to avoid hitting rate limits in the first place, using n8n's Wait node or batch size settings, 5) How to implement a token bucket or request queue pattern using n8n sub-workflows, 6) Monitoring recommendations to track API usage and predict when limits will be hit, and 7) How to configure alerts when rate limit errors exceed a threshold.
```

### 12. Set Up Global Error Workflow in n8n

**Use case:** Building a centralized error handling system for all n8n workflows

```
I want to set up a global error handling workflow in n8n that catches failures from all other workflows in my instance. Please provide: 1) Step-by-step instructions to create and configure an Error Trigger node as the entry point for a global error workflow, 2) How to connect this error workflow to multiple source workflows in n8n settings, 3) The complete data structure of the error object that the Error Trigger receives — all available fields and what they contain, 4) A recommended global error workflow structure with nodes for: logging errors to [DATABASE/SHEET], sending notifications via [CHANNEL], categorizing error severity, and updating a status dashboard, 5) How to prevent error notification storms when a workflow fails repeatedly in a short period (rate limiting notifications), 6) How to create different notification routing rules based on workflow name, error type, or time of day, and 7) A recommended folder and naming convention for organizing error handling workflows in n8n.
```

### 13. Recover from Webhook Delivery Failures

**Use case:** Preventing data loss when webhook-triggered workflows fail mid-processing

```
My n8n workflow is triggered by incoming webhooks from [EXTERNAL SYSTEM: e.g., Stripe, GitHub, Shopify]. Sometimes the workflow fails after receiving the webhook, causing the event data to be lost permanently since the external system does not retry. I need a strategy to ensure no webhook events are ever lost. Please provide: 1) A 'webhook buffer' architecture where incoming webhooks are immediately stored before any processing begins, using [STORAGE: e.g., n8n's own database, external store], 2) Step-by-step instructions to split the workflow into a 'receive and store' phase and a separate 'process' phase, 3) How to immediately return a 200 OK response to the webhook sender while processing asynchronously, 4) A replay mechanism to reprocess stored webhook events that failed during the processing phase, 5) How to implement idempotency to prevent duplicate processing when replaying events, 6) How to handle webhook signature verification in the receive phase, and 7) Monitoring recommendations to detect and alert on unprocessed webhook backlogs.
```

### 14. Implement Circuit Breaker Pattern

**Use case:** Protecting workflows from cascading failures caused by unreliable external services

```
I want to implement a circuit breaker pattern in my n8n workflow that calls [EXTERNAL SERVICE NAME]. This service sometimes goes down or becomes slow, causing my workflow to hang or accumulate failures. A circuit breaker should stop calling the service temporarily when it detects repeated failures. Please provide: 1) A plain-language explanation of the circuit breaker pattern and why it is valuable for n8n workflows, 2) A practical circuit breaker implementation using n8n nodes — describe the architecture using available n8n node types, 3) How to use an external state store ([STORAGE: e.g., Redis, Airtable, Google Sheet]) to track the circuit state (closed/open/half-open), 4) A Function node JavaScript snippet that checks circuit state, records failures, and triggers state transitions, 5) How to configure the failure threshold (e.g., 5 failures in 10 minutes) and cooldown period before attempting recovery, 6) How to notify the operations team when the circuit opens and when it closes, and 7) How to test the circuit breaker without taking down the real service.
```

### 15. Trace and Log Workflow Execution Path

**Use case:** Adding execution tracing to reconstruct any workflow run for debugging

```
I need to add comprehensive execution tracing and logging to my n8n workflow named [WORKFLOW NAME] so I can reconstruct exactly what happened during any execution — both successful and failed. The workflow does the following: [DESCRIBE WORKFLOW PURPOSE AND MAIN STEPS]. Please provide: 1) A logging strategy that captures: execution start, each major step completion, data transformations, external API calls, decision branch taken, and execution end, 2) A JavaScript Function node code snippet that generates a structured log entry with: timestamp, execution ID, step name, status, duration, input summary, and output summary, 3) How to send all log entries to [LOG DESTINATION: e.g., Datadog, a database table, a Google Sheet, Logtail], 4) How to assign and propagate a unique correlation ID throughout the entire workflow execution, 5) How to differentiate between INFO, WARNING, and ERROR level log entries and filter them appropriately, 6) A log schema design that makes querying and troubleshooting efficient, and 7) Performance considerations to ensure logging does not significantly slow down the workflow.
```

### 16. Handle Database Connection and Query Failures

**Use case:** Making database-dependent workflow nodes resilient to connection and query failures

```
My n8n workflow connects to a [DATABASE TYPE: e.g., PostgreSQL, MySQL, MongoDB] database and runs queries as part of its main processing. Database errors are causing my workflow to fail without proper handling. The types of database operations I perform are: [LIST OPERATIONS: e.g., insert records, read customer data, update status]. Please provide: 1) A categorized list of common database errors for [DATABASE TYPE] and which ones are transient (safe to retry) vs permanent (require human intervention), 2) How to configure n8n's database node with optimal connection settings and timeout values for production use, 3) Error handling strategies specific to database operations: unique constraint violations, connection timeouts, deadlocks, and empty result sets, 4) A Function node snippet that wraps database operations with error categorization logic, 5) How to implement connection pooling considerations in n8n's database node, 6) A strategy for handling empty query results gracefully — distinguishing between 'no results found' (expected) and a query failure (unexpected), and 7) How to alert the team when database errors exceed a normal threshold.
```

### 17. Create Workflow Health Check System

**Use case:** Building automated monitoring to detect unhealthy production workflows proactively

```
I want to build an n8n monitoring workflow that acts as a health check system for my other production workflows. This health check workflow should run on a schedule and verify that my critical workflows are operating correctly. My production workflows that need monitoring are: [LIST WORKFLOW NAMES AND WHAT THEY DO]. Please provide: 1) A complete health check workflow architecture that runs every [INTERVAL] and checks each production workflow, 2) Methods to detect the following unhealthy states: workflow has not run in too long, workflow is stuck in running state, workflow error rate is above threshold, workflow is disabled unexpectedly, and data output quality has degraded, 3) How to use n8n's API to query workflow execution history and status programmatically, 4) A health check results data structure and how to store it in [STORAGE: e.g., a dashboard, database, or status page], 5) Alerting logic that only sends notifications when status changes from healthy to unhealthy (and vice versa) to avoid alert fatigue, 6) How to build a simple status dashboard using the health check data, and 7) A weekly health report email template summarizing workflow reliability metrics.
```

### 18. Handle Third-Party Service Outages Gracefully

**Use case:** Keeping workflows operational during third-party service outages

```
My n8n workflow depends on [THIRD-PARTY SERVICE NAME] for a critical step. When this service is down or returns errors, my entire workflow fails. I need a strategy to handle outages gracefully without losing data or requiring manual intervention. Please provide: 1) A decision framework for how to respond to different outage scenarios: brief outage under 5 minutes, extended outage over 1 hour, and partial degradation where the service is slow but responding, 2) How to implement a fallback behavior when [THIRD-PARTY SERVICE NAME] is unavailable — options include: using cached data, skipping the step and flagging for later, using an alternative service [ALTERNATIVE SERVICE IF KNOWN], or queuing the item for retry, 3) A queuing pattern using n8n where failed items are held and automatically retried when the service recovers, 4) How to detect service recovery automatically and trigger reprocessing of queued items, 5) Communication templates for notifying [STAKEHOLDERS] about the outage and the fallback behavior being used, 6) How to track items processed with fallback vs normal processing for reconciliation, and 7) Post-outage reconciliation steps to ensure data integrity.
```

### 19. Analyze and Reduce Workflow Error Rate

**Use case:** Systematically reducing error rates in high-failure production workflows

```
My n8n workflow named [WORKFLOW NAME] has an unacceptably high error rate. Over the past [TIME PERIOD], it has failed approximately [FAILURE COUNT] times out of [TOTAL RUNS] total executions. Here are the most common error messages I see in the execution logs: [PASTE TOP 3-5 ERROR MESSAGES]. The workflow does the following: [DESCRIBE WORKFLOW PURPOSE]. Please: 1) Analyze the error messages I provided and categorize them by likely root cause, 2) Identify whether these errors are systemic (design flaws), environmental (infrastructure issues), or data-driven (bad input data), 3) Provide a prioritized action plan to address each error category with specific n8n configuration changes or code fixes, 4) Recommend leading metrics I should track to measure improvement after changes are made, 5) Suggest a phased testing approach to validate fixes without disrupting production — including how to use n8n's test execution feature, 6) Help me set a realistic target error rate for this type of workflow and the steps to achieve it, and 7) Provide a post-mortem template I can use to document this analysis and the remediation steps taken.
```

### 20. Build Error Handling Runbook for Team

**Use case:** Enabling entire teams to respond to workflow failures independently and effectively

```
I need to create a practical error handling runbook for my team so that any team member — including non-developers — can diagnose and resolve common n8n workflow failures without needing to escalate. Our team includes: [DESCRIBE TEAM: e.g., '3 developers and 2 operations analysts who are not programmers']. Our n8n workflows include: [LIST KEY WORKFLOWS AND WHAT THEY DO]. Common errors we encounter are: [LIST 3-5 RECURRING ERRORS OR FAILURE TYPES]. Please create: 1) A one-page quick reference card for first responders — what to check first when any workflow fails, 2) A decision tree flowchart (described in text/Mermaid) to guide non-technical team members from error symptom to resolution action, 3) Step-by-step resolution procedures for each of the common errors I listed, written for a [LEAST TECHNICAL ROLE] audience, 4) An escalation policy — when to self-resolve vs when to escalate, and who to contact at each escalation level, 5) A post-incident template for documenting what failed, what caused it, how it was resolved, and what was done to prevent recurrence, 6) A glossary of n8n terms and error codes that non-developers will encounter, and 7) A recommended on-call rotation structure and handoff checklist for teams that need 24/7 workflow reliability.
```
