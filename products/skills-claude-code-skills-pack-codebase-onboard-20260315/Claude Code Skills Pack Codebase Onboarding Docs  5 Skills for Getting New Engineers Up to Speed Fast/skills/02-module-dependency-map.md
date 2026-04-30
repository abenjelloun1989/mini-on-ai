---
name: module-dependency-map
trigger: /map-dependencies
description: >
  Scans the codebase to map and document inter-module and inter-service
  dependencies. Produces a visual-ready dependency graph (Mermaid diagram)
  alongside written explanations of coupling points, critical paths, and
  dependency health signals. Use this skill when onboarding new engineers,
  planning a refactor, or auditing architectural drift.
tags: [onboarding, architecture, dependencies, documentation]
---

# Skill: Module Dependency Map

## Purpose

Generate a comprehensive, human-readable dependency map of this codebase.
The output gives new engineers a mental model of how modules, packages, and
services relate to one another — what calls what, what owns what, and where
the riskiest coupling lives.

---

## When to Use

- A new hire needs to understand the system before making their first PR
- An engineering lead wants to audit coupling before a major refactor
- A staff engineer needs to document architectural boundaries for an ADR
- The team suspects circular dependencies or hidden critical paths

---

## Execution Instructions

Follow these steps in order. Do not skip steps.

### Step 1 — Discover the Module Structure

1. List all top-level directories and identify which represent distinct
   modules, packages, services, or layers (e.g., `src/`, `packages/`,
   `services/`, `apps/`, `libs/`).
2. Read `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
   `pom.xml`, or equivalent manifest files to identify declared
   dependencies between internal packages.
3. Note the language(s) and module system in use (Node ESM/CJS, Python
   packages, Go modules, etc.). This determines how imports are resolved.

### Step 2 — Trace Import and Call Relationships

1. For each module identified in Step 1, scan its entry point files and
   key source files for import/require/use statements that reference
   other internal modules.
2. Build a directed edge list: `ModuleA → ModuleB` means A imports or
   calls B.
3. Flag any **bidirectional dependencies** (A → B and B → A) as
   potential circular coupling issues.
4. Identify **shared utilities or core libraries** that are imported by
   five or more other modules — these are high-leverage, high-risk nodes.
5. If external services are referenced (databases, third-party APIs,
   message queues), include them as leaf nodes labeled `[external]`.

### Step 3 — Identify Critical Paths

1. A **critical path** is any chain of dependencies that, if broken,
   would cascade failures across multiple modules.
2. Look for modules with high **in-degree** (many modules depend on them)
   — these are critical nodes.
3. Look for long dependency chains (depth > 4 hops) that indicate tight
   coupling.
4. Note any modules that sit between two otherwise-disconnected clusters
   (bridge nodes).

### Step 4 — Render the Dependency Graph

Produce a Mermaid `graph TD` diagram following these rules:

- Each node label uses the module's short name (e.g., `auth`, `db`,
  `api-gateway`).
- Use `-->` for standard dependencies.
- Use `-.->` for optional or runtime-only dependencies.
- Use `==>` for critical path edges.
- Group related modules inside `subgraph` blocks named after their
  layer or domain (e.g., `subgraph Services`, `subgraph Shared Libs`).
- External dependencies get a node styled with `:::external` and a
  class definition `classDef external fill:#f5f5f5,stroke:#999`.
- High-risk nodes (high in-degree or bridge nodes) get `:::critical`
  styling: `classDef critical fill:#ffe0e0,stroke:#cc0000`.

### Step 5 — Write the Dependency Narrative

After the diagram, write four named sections:

**Module Inventory**
A table with columns: Module Name | Type | Responsibility (one line) |
Owned By (team or person, if discoverable).

**Coupling Analysis**
Prose paragraphs (one per significant coupling concern). Describe what
is coupled, why it matters, and what the risk is. Be specific — name
the files or functions involved when possible.

**Critical Paths**
A numbered list of critical paths. Each entry states: the path as a
chain (A → B → C), why it is critical, and what would break if the
middle node failed.

**Dependency Health Signals**
A short bullet list of observations about dependency hygiene:
circular deps found, god modules, missing abstraction layers, or a
clean bill of health. Each bullet ends with a recommended action or
"No action needed."

### Step 6 — Output Formatting Rules

- Open with a one-paragraph executive summary (3–5 sentences) suitable
  for a staff engineer or engineering manager who will not read the full
  document.
- The Mermaid diagram must be in a fenced code block labeled `mermaid`.
- All section headers use `##` (H2).
- The Module Inventory table must be valid Markdown table syntax.
- Total document length: aim for 400–800 words of prose, plus the
  diagram. Do not pad with filler.
- If the codebase is very large (>50 modules), focus on the top two
  layers of the dependency hierarchy and note that deeper layers are
  omitted for clarity.

---

## Constraints and Quality Rules

- **Never fabricate module relationships.** Only document dependencies
  you can trace to actual import statements, manifest declarations, or
  explicit function calls found in the codebase.
- If a module's internal structure is opaque (e.g., a compiled binary
  or an unreadable config), note it as `[opaque]` in the diagram and
  explain the limitation in the narrative.
- Do not include test files or dev tooling in the primary graph unless
  they introduce production coupling (e.g., a shared test fixture
  library imported by app code).
- Flag — but do not automatically fix — any circular dependencies.
  Fixing them is an architectural decision, not a documentation task.
- Use language-neutral terminology in the narrative. Avoid jargon that
  only makes sense in one ecosystem (e.g., "barrel file" without
  explanation).

---

## Usage Examples

**Example 1 — Default full-codebase scan**

/map-dependencies

Scans the entire repository. Produces the full Mermaid graph and
narrative document covering all discovered modules.

---

**Example 2 — Scope to a single domain or subdirectory**

/map-dependencies src/payments

Limits the scan to the `src/payments` directory and its dependencies.
The graph will show internal payments modules plus any external modules
they import. Useful when onboarding an engineer to a specific domain.

---

**Example 3 — Focus on a specific module's dependents**

/map-dependencies --focus auth-service

Produces a graph centered on `auth-service`, showing both what it
depends on (outgoing edges) and every module that depends on it
(incoming edges). Includes a callout section titled "Impact of
auth-service Changes" listing all upstream consumers.

---

## Output Template Reference

The final document should follow this structure:

1. Executive Summary (paragraph)
2. Dependency Graph (Mermaid code block)
3. Module Inventory (table)
4. Coupling Analysis (prose)
5. Critical Paths (numbered list)
6. Dependency Health Signals (bullets)