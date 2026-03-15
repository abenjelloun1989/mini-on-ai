---
name: post-release-summary
trigger: /post-release-summary
description: >
  Generates a structured internal post-release summary report after a version
  ships. Covers what was delivered, known issues discovered post-deploy, rollback
  procedures, and follow-up action items for engineering and stakeholder teams.
  Use this immediately after a release goes live to align the team and close the
  communication loop.
tags: [release, documentation, devops, internal, post-mortem]
---

# Skill: Post-Release Summary

## Purpose

After a release ships, engineers and stakeholders need a single, authoritative
document that answers: What went out? Did anything break? How do we roll back if
needed? What still needs attention? This skill produces that document quickly and
consistently by pulling from git history, existing notes, and project context.

## When to Use

- Immediately after a production release completes
- After a hotfix or patch deployment
- When handing off release ownership to another team or time zone
- Before a post-release retrospective meeting
- When leadership or stakeholders ask for a release debrief

---

## How to Execute This Skill

Follow these steps in order. Ask clarifying questions if required inputs are
missing before proceeding.

### Step 1 — Gather Release Context

Collect the following information. If not provided in the command invocation,
ask the user or infer from available project files:

- **Version number** — e.g., `v2.4.1`
- **Release date and time** — include timezone if available
- **Target environment** — production, staging, canary, etc.
- **Release lead or engineer name** (optional but recommended)
- **Deployment method** — CI/CD pipeline, manual deploy, blue/green, canary, etc.

If a version is not specified, check `package.json`, `pyproject.toml`,
`Cargo.toml`, `CHANGELOG.md`, or the most recent git tag to infer it.

### Step 2 — Analyze What Shipped

Run or simulate the following to extract delivered changes:

1. Identify commits since the previous release tag:
   `git log <previous-tag>..<current-tag> --oneline --no-merges`
2. If a CHANGELOG.md exists, extract the section matching this version.
3. Group changes into categories:
   - **Features** — new user-facing or API functionality
   - **Bug Fixes** — resolved defects
   - **Performance Improvements** — speed or resource optimizations
   - **Security Patches** — CVE fixes, auth changes, dependency updates
   - **Infrastructure / DevOps** — deployment, config, or pipeline changes
   - **Breaking Changes** — anything requiring migration or consumer updates
   - **Dependencies Updated** — library upgrades with notable impact

### Step 3 — Document Known Issues

Check the following sources for post-release issues:

- Any issues or notes the user provides directly
- Recent git commits after the release tag (hotfix indicators)
- TODO/FIXME comments added near release time
- Open issues or PR descriptions referencing the release version

For each known issue, document:
- **Description** of the problem
- **Severity** — Critical / High / Medium / Low
- **Affected scope** — which users, services, or features are impacted
- **Current status** — monitoring, investigating, fix in progress, resolved
- **Owner** — who is responsible for resolution

If no known issues exist, state explicitly: "No known issues at time of
publication."

### Step 4 — Write Rollback Procedures

Provide clear, actionable rollback steps tailored to the project type and
deployment method. Include:

1. **Trigger condition** — when should rollback be initiated?
2. **Step-by-step rollback commands or procedure**
3. **Data migration reversal** — if database migrations ran, note how to reverse
4. **Expected rollback duration** — estimate time to complete
5. **Verification steps** — how to confirm rollback succeeded
6. **Escalation contact** — who to notify if rollback fails

If deployment method is unknown, provide a generic git-based rollback template
and note that it should be adapted to the team's actual deployment tooling.

### Step 5 — Define Follow-Up Action Items

List concrete next steps. Categorize by team:

- **Engineering** — tech debt, follow-up fixes, monitoring tasks
- **QA / Testing** — regression areas to watch, test coverage gaps
- **DevOps / Infrastructure** — cleanup tasks, config updates, alert tuning
- **Product / Stakeholders** — announcements, customer communications, metrics to track
- **Documentation** — docs that need updating as a result of this release

Each action item should have: description, owner (role or name), and due date
or timeframe if known.

### Step 6 — Assemble the Report

Compile all sections into the final structured document (see Output Format
below). Write in clear, professional prose suitable for both technical and
non-technical readers. Avoid jargon without explanation.

---

## Output Format

Produce a Markdown document with the following structure. Do not omit sections —
if a section has no content, write "None at this time" or an appropriate null
statement.

---

POST-RELEASE SUMMARY
Version: [version]
Release Date: [date and time with timezone]
Environment: [environment]
Prepared By: [name or "Engineering Team"]
Report Generated: [current date]

---

EXECUTIVE SUMMARY

Two to four sentence overview of what shipped, whether the release went smoothly,
and the most important follow-up items. Written for a non-technical audience.

---

1. WHAT SHIPPED

1.1 Features
- Bulleted list

1.2 Bug Fixes
- Bulleted list

1.3 Performance Improvements
- Bulleted list

1.4 Security Patches
- Bulleted list

1.5 Breaking Changes
- Bulleted list with migration notes if applicable

1.6 Infrastructure Changes
- Bulleted list

1.7 Dependencies Updated
- Bulleted list

---

2. RELEASE METRICS

- Deployment method:
- Deployment duration:
- Commits included:
- Files changed:
- Contributors:
- Rollback performed: Yes / No

---

3. KNOWN ISSUES

For each issue:
  Issue: [title]
  Severity: [Critical / High / Medium / Low]
  Description: [details]
  Affected Scope: [who or what is impacted]
  Status: [current state]
  Owner: [name or role]

---

4. ROLLBACK PROCEDURE

4.1 Trigger Conditions
[When to initiate rollback]

4.2 Rollback Steps
[Numbered steps]

4.3 Data Reversal Notes
[Migration rollback details]

4.4 Estimated Duration
[Time estimate]

4.5 Verification
[How to confirm success]

4.6 Escalation
[Who to contact]

---

5. FOLLOW-UP ACTION ITEMS

Engineering:
[ ] [description] — Owner: [name/role] — Due: [date/timeframe]

QA / Testing:
[ ] [description] — Owner: [name/role] — Due: [date/timeframe]

DevOps / Infrastructure:
[ ] [description] — Owner: [name/role] — Due: [date/timeframe]

Product / Stakeholders:
[ ] [description] — Owner: [name/role] — Due: [date/timeframe]

Documentation:
[ ] [description] — Owner: [name/role] — Due: [date/timeframe]

---

6. NOTES AND OBSERVATIONS

Free-form section for anything that doesn't fit above — lessons learned,
observations about the release process, suggestions for improvement.

---

## Constraints and Quality Rules

- **Accuracy over speed** — never fabricate commit messages, issue details, or
  metrics. If data is unavailable, say so explicitly.
- **No vague language** — replace "some issues" with specifics, replace "soon"
  with timeframes.
- **Severity must be justified** — if you assign Critical or High to an issue,
  include a one-line rationale.
- **Rollback steps must be executable** — write commands the reader can copy and
  run, not abstract descriptions.
- **Keep action items actionable** — each item must have a clear verb, owner
  role, and timeframe. Avoid items like "investigate further" without context.
- **Tone** — professional and factual. This is an internal record, not marketing
  copy. Do not inflate the success of a release.
- **Length** — comprehensive but not padded. Omit empty categories rather than
  writing "N/A" repeatedly unless structure requires it.

---

## Usage Examples

### Example 1 — Basic invocation after tagging a release

/post-release-summary v3.1.0 deployed to production on 2024-11-14 at 18:30 UTC

Claude will inspect the git log since the previous tag, extract grouped changes,
generate rollback steps based on detected tooling, and produce the full report.

---

### Example 2 — Release with a known post-deploy issue

/post-release-summary v2.8.3 — prod deploy complete but seeing elevated 503s on
the payments service. Severity high. Sofia is investigating. Deployed via GitHub
Actions blue/green. Previous tag v2.8.2.

Claude will include the 503 issue in Section 3 with High severity, set status to
"Investigating," assign owner to Sofia, and flag a follow-up action item for
Engineering to resolve and verify the payments service stability.

---

### Example 3 — Hotfix summary with rollback already performed

/post-release-summary v4.0.1 hotfix — we had to roll back v4.0.0 due to a
critical auth regression. v4.0.1 patches it. Rollback of v4.0.0 took 12 minutes.
Release lead: Marcus. Prod deploy finished 09:15 EST.

Claude will set "Rollback performed: Yes" in metrics, document the auth
regression in Known Issues as Critical/Resolved, reference the v4.0.0 rollback
duration in the rollback section, and include a QA action item to expand auth
regression test coverage before the next major release.