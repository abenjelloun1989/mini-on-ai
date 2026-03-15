---
name: environment-setup-guide
trigger: /gen-env-setup
description: >
  Inspects configuration files, scripts, and tooling across the repository to
  generate a comprehensive, step-by-step local environment setup guide for new
  engineers. Covers prerequisites, installation, configuration, secrets
  management, and verification steps. Use this skill whenever a new hire needs
  to get a working local dev environment from scratch, or when the setup
  process has changed and documentation needs to be refreshed.
tags: [onboarding, documentation, devex, environment]
---

# Skill: Environment Setup Guide (`/gen-env-setup`)

## Purpose

Generate a clear, accurate, step-by-step local environment setup guide by
inspecting the actual repository artifacts — not by guessing or using generic
templates. The output must reflect the real state of the codebase so a new
engineer can follow it without asking for help.

---

## Execution Instructions

When `/gen-env-setup` is triggered, follow these steps in order.

### Step 1 — Discover Configuration Artifacts

Scan the repository root and common subdirectories for the following files.
Read every file found before writing any output.

**Package and dependency manifests:**
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- `requirements.txt`, `Pipfile`, `pyproject.toml`, `poetry.lock`, `setup.py`
- `Gemfile`, `Gemfile.lock`
- `go.mod`, `go.sum`
- `Cargo.toml`, `Cargo.lock`
- `build.gradle`, `pom.xml`, `build.sbt`
- `mix.exs`, `composer.json`

**Runtime and tooling version files:**
- `.nvmrc`, `.node-version`, `.tool-versions`, `.ruby-version`, `.python-version`
- `Dockerfile`, `docker-compose.yml`, `docker-compose*.yml`
- `.devcontainer/devcontainer.json`
- `.mise.toml`, `.rtx.toml`

**Environment and secrets templates:**
- `.env.example`, `.env.sample`, `.env.template`, `.env.local.example`
- Any `*.example` or `*.sample` files at the root level

**Scripts directory:**
- `Makefile`, `Justfile`
- `scripts/`, `bin/`, `.github/workflows/` (CI config reveals required steps)
- `bootstrap`, `setup`, `install`, `dev` scripts (any extension)

**Infrastructure and service dependencies:**
- `docker-compose.yml` service definitions (databases, caches, queues)
- `terraform/`, `infra/` for cloud resource hints
- `k8s/` or `helm/` for local cluster requirements

**Editor and linting config (optional tooling hints):**
- `.editorconfig`, `.eslintrc*`, `.prettierrc*`, `pyproject.toml` tool sections

---

### Step 2 — Extract Key Setup Facts

From the files discovered, extract and record:

1. **Runtime versions** — exact versions required (Node 20.x, Python 3.11, Ruby 3.2, etc.)
2. **Package manager** — npm vs yarn vs pnpm, pip vs poetry vs pipenv, etc.
3. **System prerequisites** — compilers, CLI tools (aws-cli, terraform, kubectl), databases
4. **Service dependencies** — which databases, caches, or message brokers must be running
5. **Environment variables** — every key in `.env.example`; flag which are required vs optional
6. **Secret sources** — any references to Vault, AWS SSM, 1Password, Doppler, etc.
7. **Database setup** — migration commands, seed data commands
8. **Build steps** — asset compilation, code generation, proto compilation
9. **Verification commands** — test commands, health check endpoints, smoke test scripts
10. **OS-specific notes** — any `darwin`/`linux`/`windows` conditionals in scripts

---

### Step 3 — Resolve Ambiguities

Before writing the guide:

- If a `.env.example` variable has no comment explaining its value, note it as
  "⚠️ Ask your team lead for this value" rather than leaving it blank.
- If conflicting Node/Python versions appear across files, flag the conflict
  explicitly and recommend the most specific source (e.g., `.nvmrc` over
  `package.json` engines field).
- If a setup script exists (`scripts/setup.sh`, `make setup`, etc.), treat it
  as authoritative and document what it does step by step — do not just say
  "run `make setup`" without explaining what that does.
- If Docker Compose is available, offer it as an alternative path to manual
  installation where applicable.

---

### Step 4 — Write the Guide

Produce a Markdown document with the following structure. Use exactly these
section headings so the document integrates consistently with other onboarding
docs in this pack.

---

#### Output Structure

    # Local Environment Setup Guide
    > Generated from repository inspection on [DATE]. Keep this file updated
    > when setup requirements change.

    ## Prerequisites
    List every tool that must be installed before touching the repo.
    Include minimum version, recommended install method, and a verification
    command for each item.
    | Tool | Version | Install | Verify |
    |------|---------|---------|--------|

    ## Repository Setup
    1. Clone command (with SSH and HTTPS variants if both are plausible)
    2. Navigate to directory
    3. Install runtime version manager steps if .nvmrc / .tool-versions found

    ## Installing Dependencies
    Exact commands with the correct package manager.
    Note if a post-install step (build, compile) runs automatically.

    ## Environment Configuration
    1. Copy the env template: `cp .env.example .env`
    2. Table of all environment variables:
       | Variable | Required | Description | Example Value |
       |----------|----------|-------------|---------------|
    3. Instructions for obtaining secrets (Vault path, SSM path, 1Password
       item name, or "ask your team lead").

    ## Starting Local Services
    - Docker Compose instructions if applicable
    - Manual service start instructions as an alternative
    - Expected output / how to know services are healthy

    ## Database Setup
    Exact migration and seed commands in order.

    ## Running the Application
    The exact command(s) to start the application locally.
    Expected output and the URL/port to open.

    ## Verification Checklist
    A short numbered checklist a new engineer can tick off:
    - [ ] Dependencies installed without errors
    - [ ] All required env vars set
    - [ ] Services running and healthy
    - [ ] Migrations applied
    - [ ] Application starts and home page loads
    - [ ] Test suite passes: `<exact command>`

    ## Common Issues & Fixes
    Populate this from any troubleshooting sections in existing READMEs,
    error handling in setup scripts, or known OS-specific quirks found
    in CI config. Minimum 3 entries if any evidence exists; omit section
    only if no evidence found.

    ## Next Steps
    Link to other onboarding docs in this pack where relevant
    (architecture overview, contributor guide, etc.).

---

### Step 5 — Quality Checks

Before finalizing output, verify:

- [ ] Every command is copy-pasteable (no `<placeholder>` left unexplained)
- [ ] Version numbers are specific, not vague ("Node 20.11.0" not "Node 20+")
- [ ] No step assumes knowledge not covered by an earlier step
- [ ] Docker path and manual path are clearly distinguished if both offered
- [ ] All `.env.example` keys are documented — none silently omitted
- [ ] The verification checklist matches the actual commands documented above

---

## Constraints

- **Do not invent steps** that have no basis in a discovered file. If a step
  is inferred rather than explicit, prefix it with `> ℹ️ Inferred:`.
- **Do not redact secret values** from `.env.example` — those are placeholders
  by design. Only warn when a variable has no example value and no comment.
- **Do not recommend** installing tools globally if the repo pins versions
  locally (e.g., prefer `nvm use` over `npm install -g node`).
- Output must be **plain Markdown**, suitable for saving as `SETUP.md` or
  pasting into Notion/Confluence without reformatting.
- If the repository has **multiple services** (monorepo), generate a top-level
  guide plus a clearly labeled subsection per service — do not collapse them.

---

## Usage Examples

**Basic invocation — generate setup guide for current repo:**

    /gen-env-setup

Claude inspects the repo root, reads all configuration artifacts, and writes
a complete `SETUP.md` to stdout ready to be saved.

---

**Targeting a specific service in a monorepo:**

    /gen-env-setup services/payments-api

Claude scopes discovery to `services/payments-api/` while still reading
root-level `.tool-versions`, `docker-compose.yml`, and shared `scripts/`.

---

**Refreshing an outdated guide after a major dependency upgrade:**

    /gen-env-setup --diff SETUP.md

Claude reads the existing `SETUP.md`, re-inspects the repo, and outputs a new
version with a `<!-- CHANGED -->` marker on every line that differs from the
previous version, making it easy to review what needs updating.