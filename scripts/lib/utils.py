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


def product_id(title: str) -> str:
    date = datetime.now().strftime("%Y%m%d")
    slug = slugify(title)[:40]
    return f"prompts-{slug}-{date}"


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(stage: str, message: str) -> None:
    print(f"[{stage}] {message}", flush=True)


def extract_json(text: str, array: bool = True):
    """Extract first JSON array or object from a string."""
    pattern = r"\[[\s\S]*\]" if array else r"\{[\s\S]*\}"
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"No JSON {'array' if array else 'object'} found in response")
    return json.loads(match.group(0))
