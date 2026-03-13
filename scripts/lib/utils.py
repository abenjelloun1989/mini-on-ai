"""
Shared utilities for pipeline scripts
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Project root = two levels up from scripts/lib/
ROOT = Path(__file__).parent.parent.parent.resolve()


def read_json(rel_path: str) -> dict:
    full = ROOT / rel_path
    with open(full, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(rel_path: str, data) -> None:
    full = ROOT / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def ensure_dir(rel_path: str) -> None:
    (ROOT / rel_path).mkdir(parents=True, exist_ok=True)


def write_file(rel_path: str, content: str) -> None:
    full = ROOT / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def read_file(rel_path: str) -> str:
    with open(ROOT / rel_path, "r", encoding="utf-8") as f:
        return f.read()


def file_exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = text.strip()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


def product_id(title: str, category: str = "prompt-packs") -> str:
    prefix_map = {
        "prompt-packs": "prompts",
        "checklist": "checklist",
        "swipe-file": "swipe",
        "mini-guide": "guide",
        "n8n-template": "n8n",
    }
    prefix = prefix_map.get(category, "prompts")
    date = datetime.now().strftime("%Y%m%d")
    slug = slugify(title)[:40]
    return f"{prefix}-{slug}-{date}"


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(stage: str, message: str) -> None:
    print(f"[{stage}] {message}", flush=True)


def extract_json(text: str, array: bool = True):
    """Extract first JSON array or object from a string.
    Falls back to repairing truncated arrays if strict parse fails.
    """
    pattern = r"\[[\s\S]*\]" if array else r"\{[\s\S]*\}"
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"No JSON {'array' if array else 'object'} found in response")
    raw = match.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        if array:
            return _repair_json_array(raw)
        raise


def _repair_json_array(raw: str) -> list:
    """Recover a truncated JSON array by keeping only complete items."""
    depth = 0
    in_string = False
    escape_next = False
    last_complete = 1  # position just after opening '['

    for i, ch in enumerate(raw):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in ("{", "["):
            depth += 1
        elif ch in ("}", "]"):
            depth -= 1
            if depth == 1 and ch == "}":
                last_complete = i + 1  # end of a complete top-level object

    truncated = raw[:last_complete].rstrip().rstrip(",") + "]"
    try:
        result = json.loads(truncated)
        if isinstance(result, list) and result:
            return result
    except json.JSONDecodeError:
        pass
    raise ValueError("Could not repair truncated JSON array")
