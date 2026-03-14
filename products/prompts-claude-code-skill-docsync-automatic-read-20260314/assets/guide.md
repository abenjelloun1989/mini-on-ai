# Claude Code Skill: DocSync — Automatic README and API Reference Generator

> For backend developers, this skill scans codebases and auto-generates structured README files and API reference docs from functions, routes, and comments so they can ship well-documented libraries without writing a single doc line manually

---

## What This Skill Does

Scans codebases to automatically generate structured README files and API reference documentation from functions, routes, comments, and type signatures — eliminating manual documentation work for backend developers.

**Best for:** Backend Development, API Engineering, Open Source Maintenance, DevOps/Platform Engineering

---

## Use Cases

**A backend developer has built a new Node.js REST API and needs a full README with endpoint references before shipping to npm**
  → `/doc-sync generate full-docs --target ./src --output README.md`

**A Python library maintainer wants to regenerate API reference docs after adding 10 new functions without writing JSDoc or docstrings manually**
  → `/doc-sync refresh-api-ref --lang python --src ./lib --format markdown`

**A team lead wants to audit which exported functions are missing documentation before a release review**
  → `/doc-sync audit-coverage --src ./src --report undocumented-exports.md`

**An open source contributor wants to auto-generate a CHANGELOG-style API diff between two branches to update docs after a refactor**
  → `/doc-sync diff-docs --base main --head feature/refactor --output API_CHANGES.md`

---

## Configuration Steps

### Step 1: Create the skills directory and SKILL.md file

From your project root, run: `mkdir -p skills && touch skills/SKILL.md`. This is where Claude Code will look for specialized skill instructions. Open `skills/SKILL.md` in your editor to begin configuration.

### Step 2: Define the DocSync skill identity and scanning rules in SKILL.md

Paste the following into `skills/SKILL.md`:

```
# DocSync — Auto Documentation Generator

## Purpose
Scan this codebase and generate structured README and API reference documentation from source code, routes, function signatures, and inline comments.

## Scanning Rules
- Parse exported functions, classes, and methods from ./src, ./lib, or ./app directories
- Extract JSDoc, docstrings, or inline comments above each export
- Identify HTTP route definitions (Express, FastAPI, Flask, NestJS patterns)
- Detect TypeScript interfaces and Python type hints as schema sources
- Flag exports with zero documentation coverage

## Output Format
- README.md: Project title, description, installation, usage, environment variables, contributor guide
- API_REFERENCE.md: Grouped by module/route, includes method signature, params, return type, example usage
- Use GitHub-flavored Markdown with anchor links and a generated table of contents
```

### Step 3: Add generation templates and output path configuration

Create a config file at `skills/docsync.config.json` with your project-specific settings:

```json
{
  "source_dirs": ["src", "lib", "app", "routes"],
  "output_dir": "docs",
  "readme_output": "README.md",
  "api_ref_output": "docs/API_REFERENCE.md",
  "languages": ["javascript", "typescript", "python"],
  "frameworks": ["express", "fastapi", "nestjs", "flask"],
  "include_private": false,
  "toc": true,
  "badge_shields": true
}
```

Then add a reference to this config in your SKILL.md: `## Config\nLoad settings from skills/docsync.config.json before scanning.`

### Step 4: Add slash-command triggers to CLAUDE.md at project root

Open or create `CLAUDE.md` at your project root and add:

```
## Custom Commands

/doc-sync [action] — Trigger the DocSync skill from skills/SKILL.md
  Actions: generate, refresh-api-ref, audit-coverage, diff-docs
  Always load skills/docsync.config.json before executing
  Write output files; do not print full docs to terminal unless --preview flag is passed
```

This ensures Claude Code routes `/doc-sync` commands to the right skill and config.

### Step 5: Test the skill with a dry-run audit on your codebase

In your Claude Code session, run: `/doc-sync audit-coverage --src ./src --report docs/coverage-report.md`. Claude will scan exported symbols, flag undocumented ones, and write a coverage report. Review `docs/coverage-report.md` to verify Claude is parsing the right files before running full generation. Adjust `source_dirs` in `skills/docsync.config.json` if any directories are missed.

### Step 6: Run full documentation generation and commit outputs

Once the audit looks correct, run: `/doc-sync generate full-docs --target ./src --output README.md`. Claude will overwrite README.md and create `docs/API_REFERENCE.md`. Add both to version control: `git add README.md docs/API_REFERENCE.md && git commit -m 'docs: auto-generated via DocSync skill'`. Add a `docs/` entry to `.gitignore` only if you want to exclude intermediate files but keep the final outputs tracked.

---

## Ready-to-Use SKILL.md Template

Copy this file to your project's `skills/` directory:

```markdown

```

---

## Adapting for Different Fields

### Backend / API Engineering

Focus scanning on route files and controller layers. In `docsync.config.json`, set `source_dirs` to `['routes', 'controllers', 'handlers']` and enable `frameworks: ['express', 'fastapi']`. The API_REFERENCE.md will organize docs by HTTP method and path, include request/response schemas, and generate curl examples from type hints.

### Open Source Library Maintenance

Enable `badge_shields: true` in config to auto-generate npm/PyPI/license badges in README. Add a `## Contributing` and `## Changelog` section template to SKILL.md. Use `/doc-sync diff-docs` before every release tag to produce a human-readable API change summary for the release notes.

### DevOps / Platform Engineering

Extend SKILL.md scanning rules to include Terraform modules, Helm chart values.yaml, and Dockerfile ARG/ENV declarations. Set `output_dir` to `runbooks/` instead of `docs/`. Use DocSync to auto-generate infrastructure runbooks from IaC comments, making on-call handoffs significantly faster.

### Data Engineering / ML Teams

Configure `languages: ['python']` and add `source_dirs: ['pipelines', 'models', 'transforms']`. Extend SKILL.md to extract dataset schemas from Pydantic models or Pandas DataFrame type hints and document them as data dictionaries. Output a `DATA_DICTIONARY.md` alongside the standard API reference.

---

## Tips for Best Results

- Add JSDoc or docstring stubs (even one-liners like `# Returns filtered user list`) above exported functions before running DocSync — Claude generates dramatically richer docs from even minimal inline hints compared to bare function signatures alone.
- Use `/doc-sync audit-coverage` as a pre-commit hook check by adding it to `.git/hooks/pre-push` with a `--fail-on-undocumented` flag instruction in SKILL.md, so documentation gaps are caught before code reaches main.
- Version your `skills/docsync.config.json` alongside your code so the documentation generation rules evolve with the codebase — when you add a new framework or rename source directories, update the config immediately so the next `/doc-sync generate` run stays accurate.

---

## Common Mistakes to Avoid

- Setting `source_dirs` too broadly (e.g., `['.']`) causes Claude to scan test files, node_modules stubs, and build artifacts, polluting the API reference with internal helpers. Always scope to `src`, `lib`, or specific feature directories and add an `exclude_dirs` list like `['__tests__', 'dist', 'node_modules']` to your config.
- Forgetting to set `include_private: false` results in private/underscore-prefixed functions appearing in public API docs, which confuses library consumers. Double-check this config flag and also add an instruction in SKILL.md: 'Skip any function or method prefixed with _ or marked @internal in its comment.'
- Running `/doc-sync generate` without first doing `/doc-sync audit-coverage` means you ship docs without knowing their completeness — you may publish a README where 40% of functions have no descriptions. Always run the audit first, fix critical gaps, then generate the final output.
