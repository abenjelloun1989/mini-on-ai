# /ship

Before starting, ask the user: "What stale values should I grep for? (e.g. old prices, outdated URLs, renamed features)"

Wait for their answer, then run this checklist in order:

## 1. Stale Value Grep
For each value the user specified, run:
```
grep -rn "VALUE" . --include="*.html" --include="*.md" --include="*.json" --include="*.js" --include="*.py" --include="*.css"
```
Report every hit with file:line and context. Flag anything that looks unintentional.

## 2. Security Scan
Check for:
- Exposed secrets: API keys, tokens, passwords hardcoded in source files (grep for patterns like `sk-`, `Bearer `, `password=`, `secret=`, `token=`)
- `.env` files accidentally staged or committed (`git status`, `git log --diff-filter=A -- "*.env"`)
- Unsafe HTML: `innerHTML` assignments with unescaped user input
- Open redirects or unvalidated URLs passed to `chrome.tabs.create` or `fetch`
- CSP issues: inline scripts, `unsafe-inline`, `unsafe-eval` in headers or manifests

## 3. Docs & README Sync
- `git diff --stat HEAD~1` to see what changed in the last commit(s)
- Check if CLAUDE.md, README.md, or any docs file references features, prices, or URLs that no longer match the codebase
- Update any stale lines; note what was changed

## 4. PR Description
Summarize all findings and changes as a ready-to-paste PR description:
- What changed (bullet list)
- Stale values found / fixed
- Security issues found / fixed
- Docs updated
- Open questions or items for the user to review manually
