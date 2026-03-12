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


SEED_ROTATION = [
    "solo freelancers and consultants",
    "content creators and YouTubers",
    "job seekers and career changers",
    "startup founders and entrepreneurs",
    "remote team managers",
    "real estate agents",
    "teachers and course creators",
    "health and wellness coaches",
    "legal and finance professionals",
    "software developers and engineers",
    "social media managers",
    "small business owners",
    "copywriters and marketers",
    "UX designers and product managers",
    "sales reps and account managers",
]


def trend_scan(seed: str = "", count: int = 10) -> list:
    import random

    # Pick a seed: user-supplied, or rotate through diverse topics
    active_seed = seed or random.choice(SEED_ROTATION)
    log("trend-scan", f"Generating {count} ideas (focus: {active_seed})...")

    # Pull titles already in backlog to avoid duplicates
    backlog = read_json("data/idea-backlog.json")
    existing_titles = [i["title"] for i in backlog.get("ideas", [])]
    avoid_block = ""
    if existing_titles:
        avoid_list = "\n".join(f"- {t}" for t in existing_titles[-30:])
        avoid_block = f"\n\nDo NOT suggest any of these already-existing ideas:\n{avoid_list}"

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""Generate {count} highly specific, niche prompt pack ideas for digital download.

Target audience for this batch: {active_seed}

Rules:
- Each pack must solve one specific, painful daily workflow problem
- Title must be concrete (e.g. "Cold Email Sequences for SaaS Trials" not "Email Prompts")
- Avoid generic topics like "productivity", "writing", "ChatGPT tips" — go niche
- Each idea must be genuinely different (different audience segment, different use case)
- Think: what does this person struggle with every week that AI could help with?{avoid_block}

Return ONLY a valid JSON array, no other text. Schema:
[
  {{
    "title": "Specific pack title (5-9 words)",
    "description": "One sentence: exact audience + exact benefit they get",
    "tags": ["tag1", "tag2", "tag3"]
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
