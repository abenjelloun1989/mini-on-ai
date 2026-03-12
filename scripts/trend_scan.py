#!/usr/bin/env python3
"""
trend_scan.py
Generates prompt pack ideas and appends them to data/idea-backlog.json

Usage: python3 scripts/trend_scan.py [--seed "keyword"] [--count 10]
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import os
import anthropic
from lib.utils import read_json, write_json, timestamp, log, extract_json

client = anthropic.Anthropic()
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")


def trend_scan(seed: str = "", count: int = 10) -> list:
    log("trend-scan", f"Generating {count} prompt pack ideas{f' (seed: {seed})' if seed else ''}...")

    seed_line = f"\nFocus area: {seed}" if seed else ""

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""Generate {count} specific, practical prompt pack ideas for digital creators and professionals.

Each idea should be:
- Focused on a real workflow or pain point that people face daily
- Immediately usable by the target audience
- Described in one clear sentence that names both the audience and the benefit
- Specific (not "prompts for writers" but "30 prompts for writing cold email sequences that get replies")
- Different from each other — cover different audiences and use cases
{seed_line}
Return ONLY a valid JSON array, no other text. Schema:
[
  {{
    "title": "Short pack title (5-8 words)",
    "description": "One sentence: who it's for and what it helps them do",
    "tags": ["tag1", "tag2"]
  }}
]""",
            }
        ],
    )

    raw = message.content[0].text.strip()
    ideas_raw = extract_json(raw, array=True)
    log("trend-scan", f"Generated {len(ideas_raw)} ideas")

    backlog = read_json("data/idea-backlog.json")

    new_ideas = []
    for i, idea in enumerate(ideas_raw):
        new_idea = {
            "id": f"idea-{int(time.time())}-{i}",
            "title": idea["title"],
            "description": idea["description"],
            "category": "prompt-packs",
            "tags": idea.get("tags", []),
            "score": None,
            "rationale": None,
            "selected": False,
            "status": None,
            "product_id": None,
            "generated_at": timestamp(),
            "source": "trend-scan",
        }
        new_ideas.append(new_idea)
        time.sleep(0.001)  # ensure unique ids

    backlog["ideas"].extend(new_ideas)
    write_json("data/idea-backlog.json", backlog)

    log("trend-scan", f"Added {len(new_ideas)} ideas to backlog. Total: {len(backlog['ideas'])}")
    return new_ideas


def main():
    parser = argparse.ArgumentParser(description="Scan for prompt pack ideas")
    parser.add_argument("--seed", default="", help="Focus keyword")
    parser.add_argument("--count", type=int, default=10, help="Number of ideas to generate")
    args = parser.parse_args()

    trend_scan(seed=args.seed, count=args.count)


if __name__ == "__main__":
    main()
