#!/usr/bin/env python3
"""
sync_shared.py — Copy _shared/ files into each extension's popup/ directory.

Run this before packaging any extension:
    python3 scripts/sync_shared.py

The script:
  1. Copies _shared/utils.js  → {ext}/popup/shared.js
  2. Copies _shared/base.css  → {ext}/popup/shared.css
  3. Copies _shared/icons.svg → {ext}/popup/icons.svg
  4. Skips files that haven't changed (hash comparison)
  4. Runs `node --check {ext}/popup/popup.js` after each copy
  5. Exits with code 1 if any check fails
"""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SHARED = ROOT / "_shared"
EXTENSIONS = ["clauseguard", "invoiceguard", "jobguard"]

# (source filename in _shared/, destination filename in {ext}/popup/)
SYNC_MAP = [
    ("utils.js",  "shared.js"),
    ("base.css",  "shared.css"),
    ("icons.svg", "icons.svg"),
]

# JS files to syntax-check after syncing each extension
JS_TO_CHECK = ["popup/popup.js", "popup/fullpage.js", "options/options.js"]


def file_hash(path: Path) -> str:
    """Return MD5 hex digest of a file, or empty string if it doesn't exist."""
    if not path.exists():
        return ""
    return hashlib.md5(path.read_bytes()).hexdigest()


def node_check(path: Path):
    """Run `node --check` on a JS file. Returns error message or None if OK."""
    if not path.exists():
        return None  # optional files (e.g. fullpage.js only in jobguard)
    result = subprocess.run(
        ["node", "--check", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return result.stderr.strip()
    return None


def main() -> int:
    errors = []
    changed = []
    unchanged = []

    # Verify _shared/ source files exist
    for src_name, _ in SYNC_MAP:
        src = SHARED / src_name
        if not src.exists():
            errors.append(f"MISSING source file: {src}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    for ext in EXTENSIONS:
        ext_dir = ROOT / ext
        popup_dir = ext_dir / "popup"

        if not popup_dir.exists():
            errors.append(f"MISSING popup dir: {popup_dir}")
            continue

        print(f"\n── {ext} ──")

        # Copy shared files
        for src_name, dst_name in SYNC_MAP:
            src = SHARED / src_name
            dst = popup_dir / dst_name
            before = file_hash(dst)
            shutil.copy2(src, dst)
            after = file_hash(dst)
            rel = dst.relative_to(ROOT)
            if before != after:
                print(f"  updated   {rel}")
                changed.append(str(rel))
            else:
                print(f"  unchanged {rel}")
                unchanged.append(str(rel))

        # Syntax-check JS files
        for js_rel in JS_TO_CHECK:
            js_path = ext_dir / js_rel
            err = node_check(js_path)
            rel = js_path.relative_to(ROOT)
            if err:
                print(f"  SYNTAX ERR {rel}")
                errors.append(f"Syntax error in {rel}:\n    {err}")
            else:
                if js_path.exists():
                    print(f"  syntax OK  {rel}")

    print()
    if changed:
        print(f"Updated {len(changed)} file(s).")
    if not changed and not errors:
        print("Everything up to date.")

    if errors:
        print("\nFAILURES:")
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
