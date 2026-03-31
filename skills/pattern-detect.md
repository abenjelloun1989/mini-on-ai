# Skill: pattern-detect

## Purpose
At the start of a new planning session, scan the repo for repeated manual work patterns and propose converting high-signal ones into skills. Cap at 2 proposals per session to keep it useful without being noisy.

## Trigger
Active when plan mode starts for a **new task** — not a continuation, not a simple question. Skip if the user's request is clearly one-off (typo fix, single question).

## What to execute (in order)

### 1. Git log scan
Run `git log --oneline -80` and look for 3+ commits touching the same area:
- Same command name repeated (e.g., "Fix /blast", "Add /blast", "Debug blast")
- Same script name across multiple fix/debug commits
- Same topic in multiple "Add" commits (e.g., 3+ blog-related commits)

### 2. Command coverage gap
- List all `cmd_*` functions in `scripts/telegram_bot.py`
- List all files in `skills/`
- Flag any command that has no matching skill doc and has been fixed/debugged 2+ times

### 3. next-steps.md persistence check
Read `docs/next-steps.md`. If an item has appeared across multiple sessions (check git log for that file), it's recurring friction worth a skill.

### 4. Threshold
A pattern qualifies if 2+ of the above signals fire for the same area.

## Output format
For each qualifying pattern (max 2), output this block **before the main plan**:

```
🔁 Pattern detected: [area name]
Signals: [list which signals fired]
Proposed skill: skills/[name].md

Stub:
# Skill: [name]
## Trigger
[when to activate]
## Steps
[what Claude should do]

---
Create this skill? (yes / skip)
```

If 0 patterns found, say nothing — do not add noise to the plan.

## Rules
- Max 2 proposals per session. If 3+ qualify, pick the top 2 by signal count.
- Never propose a skill that already exists in `skills/`
- Keep stubs concise — 10-20 lines. The goal is to prompt a decision, not write the full spec.
- If user says "skip", do not re-propose the same pattern in the same session.
- Do not slow down the main plan — run checks quickly (read 2-3 files max), then move on.

## Environment
- `scripts/telegram_bot.py` — source of cmd_* functions
- `skills/` — existing skill files
- `docs/next-steps.md` — recurring items
- `git log --oneline -80` — commit history
