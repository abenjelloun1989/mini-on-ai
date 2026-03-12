#!/usr/bin/env python3
"""
idea_rank.py
Scores unscored ideas and marks the best one as selected.

Usage: python3 scripts/idea_rank.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import json
import os
import anthropic
from lib.utils import read_json, write_json, log, extract_json

client = anthropic.Anthropic()
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")


def idea_rank():
    backlog = read_json("data/idea-backlog.json")
    unscored = [i for i in backlog["ideas"] if i.get("score") is None and not i.get("selected")]

    # Score any unscored ideas (skip API call if all already scored)
    if unscored:
        log("idea-rank", f"Scoring {len(unscored)} ideas...")

        ideas_for_prompt = [
            {"id": i["id"], "title": i["title"], "description": i["description"],
             "category": i.get("category", "prompt-packs")}
            for i in unscored
        ]

        message = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""Score each of these digital product ideas for a free download catalog.

Categories:
- prompt-packs: AI prompt collections
- checklist: actionable step-by-step checklists
- swipe-file: curated copy examples (hooks, scripts, subject lines)
- mini-guide: focused how-to guides

Ideas to score:
{json.dumps(ideas_for_prompt, indent=2)}

Score each idea on:
- demand (0-40): how large and urgent the audience need is
- uniqueness (0-30): differentiation from what's freely available online
- generability (0-30): how well AI can produce high-quality, consistent content for this category

Return ONLY a valid JSON array, no other text. Schema:
[
  {{
    "id": "idea-id",
    "score": 85,
    "rationale": "One sentence explaining the score"
  }}
]

Sort by score descending.""",
                }
            ],
        )

        raw = message.content[0].text.strip()
        scores = extract_json(raw, array=True)

        score_map = {s["id"]: s for s in scores}
        for idea in backlog["ideas"]:
            if idea["id"] in score_map:
                idea["score"] = score_map[idea["id"]]["score"]
                idea["rationale"] = score_map[idea["id"]]["rationale"]
    else:
        log("idea-rank", "All ideas already scored — skipping API call")

    # Clear previous selection
    for idea in backlog["ideas"]:
        idea["selected"] = False

    # Select highest-scoring idea that hasn't been produced or rejected
    candidates = [
        i for i in backlog["ideas"]
        if i.get("score") is not None
        and i.get("status") not in ("produced", "rejected")
    ]
    candidates.sort(key=lambda x: x["score"], reverse=True)

    if not candidates:
        log("idea-rank", "No available ideas. Run trend_scan to add more.")
        backlog["ideas"].sort(key=lambda x: 1 if x.get("status") == "rejected" else 0)
        write_json("data/idea-backlog.json", backlog)
        return None

    candidates[0]["selected"] = True
    selected = candidates[0]
    log("idea-rank", f"Selected: \"{selected['title']}\" (score: {selected['score']})")
    log("idea-rank", f"Rationale: {selected['rationale']}")

    # Keep rejected ideas at the bottom
    backlog["ideas"].sort(key=lambda x: 1 if x.get("status") == "rejected" else 0)

    write_json("data/idea-backlog.json", backlog)
    return selected


def main():
    result = idea_rank()
    if not result:
        sys.exit(1)


if __name__ == "__main__":
    main()
