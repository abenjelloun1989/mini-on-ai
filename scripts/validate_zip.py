#!/usr/bin/env python3
"""
validate_zip.py — Validate a built extension zip before CWS upload.

Usage:
    python3 scripts/validate_zip.py clauseguard
    python3 scripts/validate_zip.py invoiceguard
    python3 scripts/validate_zip.py jobguard
    python3 scripts/validate_zip.py          # validates all three

Exits with code 0 if all pass, code 1 if any validation fails.
"""

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent

REQUIRED_FILES = {
    "clauseguard": [
        "manifest.json",
        "background/service-worker.js",
        "popup/popup.html",
        "popup/popup.js",
        "popup/popup.css",
        "popup/shared.js",
        "popup/shared.css",
        "options/options.html",
        "options/options.js",
        "content/extract.js",
        "lib/pdf.min.js",
        "lib/pdf.worker.min.js",
    ],
    "invoiceguard": [
        "manifest.json",
        "background/service-worker.js",
        "popup/popup.html",
        "popup/popup.js",
        "popup/popup.css",
        "popup/shared.js",
        "popup/shared.css",
        "options/options.html",
        "options/options.js",
        "content/gmail.js",
        "content/gmail.css",
    ],
    "jobguard": [
        "manifest.json",
        "background/service-worker.js",
        "popup/popup.html",
        "popup/popup.js",
        "popup/popup.css",
        "popup/fullpage.html",
        "popup/fullpage.js",
        "popup/shared.js",
        "popup/shared.css",
        "options/options.html",
        "options/options.js",
    ],
}

FORBIDDEN_PATTERNS = [
    ".DS_Store",
    "node_modules",
    ".env",
    "store-assets",
    "worker/",
    ".git",
]

ICON_SIZES = ["16", "48", "128"]


def validate(ext_name: str) -> list[str]:
    """Return list of error strings (empty = pass)."""
    errors: list[str] = []
    store_dir = ROOT / ext_name / "store-assets"

    # Find the zip — take the latest one if multiple
    zips = sorted(store_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not zips:
        return [f"No zip found in {store_dir}"]
    zip_path = zips[0]
    print(f"  Checking {zip_path.relative_to(ROOT)}")

    try:
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())

            # Check required files
            required = REQUIRED_FILES.get(ext_name, [])
            for req in required:
                if req not in names:
                    errors.append(f"MISSING required file: {req}")

            # Check forbidden patterns
            for name in names:
                for forbidden in FORBIDDEN_PATTERNS:
                    if forbidden in name:
                        errors.append(f"FORBIDDEN entry in zip: {name}")
                        break

            # Check icon files exist (at least one naming convention)
            for size in ICON_SIZES:
                has_icon = (
                    f"icons/icon{size}.png" in names
                    or f"icons/icon-{size}.png" in names
                )
                if not has_icon:
                    errors.append(f"MISSING icon: icons/icon{size}.png (or icon-{size}.png)")

    except zipfile.BadZipFile:
        errors.append(f"BAD ZIP FILE: {zip_path}")

    return errors


def main() -> int:
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(REQUIRED_FILES.keys())
    all_errors: dict[str, list[str]] = {}

    for ext in targets:
        if ext not in REQUIRED_FILES:
            print(f"Unknown extension: {ext}. Choose from: {list(REQUIRED_FILES.keys())}")
            return 1
        print(f"\n── {ext} ──")
        errs = validate(ext)
        all_errors[ext] = errs
        if errs:
            for e in errs:
                print(f"  ERROR: {e}")
        else:
            print("  PASS")

    print()
    total_errors = sum(len(v) for v in all_errors.values())
    if total_errors:
        print(f"{total_errors} validation error(s). Fix before uploading to CWS.")
        return 1

    print("All zips validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
