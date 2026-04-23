"""
Security assertions — run before and after fixes to verify remediation.
These are fast, import-free checks that don't require a test framework.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"

failures = []

def check(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))
        failures.append(name)

print("=== Security Assertions ===\n")

# ── B324: MD5 should use usedforsecurity=False ────────────────────────────────
sync_shared = (SCRIPTS / "sync_shared.py").read_text()
check(
    "B324: hashlib.md5 uses usedforsecurity=False",
    "usedforsecurity=False" in sync_shared,
    "sync_shared.py uses hashlib.md5() without usedforsecurity=False"
)

# ── Real bug: no file:// fallback URLs ───────────────────────────────────────
for script in SCRIPTS.glob("*.py"):
    if script.name == "test_security.py": continue  # skip self
    text = script.read_text()
    matches = [(i+1, l.strip()) for i, l in enumerate(text.splitlines())
               if 'file://' in l and not l.strip().startswith('#')]
    check(
        f"No file:// URL in {script.name}",
        len(matches) == 0,
        f"lines {[m[0] for m in matches]}: {[m[1] for m in matches]}"
    )

# ── Secrets: no hardcoded tokens/keys in scripts ─────────────────────────────
SECRET_PATTERN = re.compile(
    r'(sk-[A-Za-z0-9]{20,}|'
    r'AAAA[A-Za-z0-9_-]{20,}|'  # Telegram bot tokens start with digits:AAAA...
    r'ghp_[A-Za-z0-9]{36,}|'   # GitHub personal access tokens
    r'xoxb-[0-9]+-[A-Za-z0-9]+)'  # Slack bot tokens
)
for script in list(SCRIPTS.glob("*.py")) + list((ROOT / "clauseguard/worker").glob("*.js")):
    text = script.read_text()
    hits = SECRET_PATTERN.findall(text)
    check(
        f"No hardcoded secrets in {script.name}",
        len(hits) == 0,
        f"potential secrets: {hits[:3]}"
    )

# ── B310: all urlopen calls use Request objects (not raw strings) ─────────────
RAW_URLOPEN = re.compile(r'urlopen\s*\(\s*["\']', re.MULTILINE)
for script in SCRIPTS.glob("*.py"):
    if script.name == "test_security.py": continue  # skip self
    text = script.read_text()
    hits = RAW_URLOPEN.findall(text)
    check(
        f"No raw string passed to urlopen in {script.name}",
        len(hits) == 0,
        f"{len(hits)} raw string urlopen call(s)"
    )

print(f"\n{'='*40}")
if failures:
    print(f"FAILED: {len(failures)} check(s) failed")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
