#!/usr/bin/env python3
"""
generate_product.py
Generates a prompt pack for the selected idea.

Usage: python3 scripts/generate_product.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

import os
import anthropic
from lib.utils import read_json, write_json, write_file, ensure_dir, product_id, timestamp, log, extract_json

client = anthropic.Anthropic()
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")


def generate_product() -> dict:
    backlog = read_json("data/idea-backlog.json")
    idea = next((i for i in backlog["ideas"] if i.get("selected")), None)

    if not idea:
        raise RuntimeError("No selected idea found. Run idea_rank first.")

    log("generate-product", f"Generating prompt pack for: \"{idea['title']}\"")

    pid = product_id(idea["title"])
    assets_dir = f"products/{pid}/assets"
    ensure_dir(assets_dir)

    message = client.messages.create(
        model=MODEL,
        max_tokens=8096,
        messages=[
            {
                "role": "user",
                "content": f"""Create a professional prompt pack titled "{idea['title']}".

Target audience and purpose: {idea['description']}

Generate exactly 25 high-quality, immediately usable prompts. Each prompt should:
- Be complete and self-contained (works without additional context)
- Include clear placeholders like [PRODUCT NAME] or [TARGET AUDIENCE] where customization is needed
- Be specific enough to produce consistent, high-quality results
- Cover different angles, use cases, and scenarios within the theme
- Be written for use with any modern AI assistant (ChatGPT, Claude, Gemini, and others)

Return ONLY a valid JSON array, no other text. Schema:
[
  {{
    "id": 1,
    "title": "Short descriptive title of this prompt",
    "prompt": "The full prompt text ready to use",
    "use_case": "When and how to use this prompt"
  }}
]""",
            }
        ],
    )

    raw = message.content[0].text.strip()
    prompts = extract_json(raw, array=True)
    log("generate-product", f"Generated {len(prompts)} prompts")

    # Write prompts.json
    write_file(f"{assets_dir}/prompts.json", json.dumps(prompts, indent=2, ensure_ascii=False) + "\n")

    # Write prompts.md
    md = _build_markdown(idea, prompts)
    write_file(f"{assets_dir}/prompts.md", md)

    # Write README.md
    readme = _build_readme(idea, len(prompts))
    write_file(f"{assets_dir}/README.md", readme)

    # Write meta.json
    meta = {
        "id": pid,
        "title": idea["title"],
        "description": idea["description"],
        "category": "prompt-packs",
        "tags": idea.get("tags", []),
        "prompt_count": len(prompts),
        "created_at": timestamp(),
        "status": "generated",
        "package_path": None,
        "site_path": None,
    }
    write_file(f"products/{pid}/meta.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    # Mark idea as produced
    idea["status"] = "produced"
    idea["product_id"] = pid
    write_json("data/idea-backlog.json", backlog)

    log("generate-product", f"Product created at products/{pid}/")
    return meta


def _build_markdown(idea: dict, prompts: list) -> str:
    lines = [
        f"# {idea['title']}",
        "",
        f"> {idea['description']}",
        "",
        "---",
        "",
        f"## Prompts ({len(prompts)} total)",
        "",
    ]
    for p in prompts:
        lines += [
            f"### {p['id']}. {p['title']}",
            "",
            f"**Use case:** {p['use_case']}",
            "",
            "```",
            p["prompt"],
            "```",
            "",
        ]
    return "\n".join(lines)


def _build_readme(idea: dict, count: int) -> str:
    return f"""# {idea['title']}

{idea['description']}

## What's included

- **{count} prompts** ready to use with any AI assistant
- Plain text format — works with ChatGPT, Claude, Gemini, and others
- Organized by use case for easy browsing

## How to use

1. Open `prompts.md` or `prompts.json`
2. Find the prompt that matches your need
3. Copy it into your AI assistant
4. Replace any `[PLACEHOLDER]` text with your specifics
5. Run and iterate

## Files

- `prompts.md` — Human-readable prompt list
- `prompts.json` — Machine-readable structured data
- `README.md` — This file
"""


def main():
    generate_product()


if __name__ == "__main__":
    main()
