#!/usr/bin/env python3
"""
check_syntax.py — Syntax-check all extension JS files using `node --check`.

Run before packaging any extension:
    python3 scripts/check_syntax.py

Exits with code 0 if all files pass, code 1 if any fail.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXTENSIONS = ["clauseguard", "invoiceguard", "jobguard"]

JS_PATTERNS = [
    "popup/popup.js",
    "popup/shared.js",
    "popup/fullpage.js",
    "background/service-worker.js",
    "options/options.js",
]

# Directories to skip (worker source, node_modules, etc.)
SKIP_DIRS = {"node_modules", "worker", "store-assets", "_shared"}


def main() -> int:
    errors = []
    checked = 0

    for ext in EXTENSIONS:
        ext_dir = ROOT / ext
        print(f"\n── {ext} ──")
        for pattern in JS_PATTERNS:
            path = ext_dir / pattern
            if not path.exists():
                continue
            # Skip forbidden dirs
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            result = subprocess.run(
                ["node", "--check", str(path)],
                capture_output=True,
                text=True,
            )
            rel = path.relative_to(ROOT)
            if result.returncode != 0:
                print(f"  FAIL  {rel}")
                errors.append(f"{rel}:\n    {result.stderr.strip()}")
            else:
                print(f"  OK    {rel}")
                checked += 1

    print(f"\nChecked {checked} file(s).")
    if errors:
        print(f"\n{len(errors)} FAILURE(S):")
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print("All syntax checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
