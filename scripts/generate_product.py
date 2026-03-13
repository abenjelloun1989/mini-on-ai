#!/usr/bin/env python3
"""
generate_product.py
Generates a digital product for the selected idea.

Supported categories:
  prompt-packs  — 25 AI prompts in JSON + Markdown
  checklist     — actionable checklist in JSON + Markdown
  swipe-file    — curated copy examples in JSON + Markdown
  mini-guide    — focused how-to guide in Markdown
  n8n-template  — importable n8n automation workflow JSON + README

Usage: python3 scripts/generate_product.py
"""

import json
import re
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

VALID_CATEGORIES = {"prompt-packs", "checklist", "swipe-file", "mini-guide", "n8n-template"}


def generate_product() -> dict:
    backlog = read_json("data/idea-backlog.json")
    idea = next((i for i in backlog["ideas"] if i.get("selected")), None)

    if not idea:
        raise RuntimeError("No selected idea found. Run idea_rank first.")

    category = idea.get("category", "prompt-packs")
    if category not in VALID_CATEGORIES:
        log("generate-product", f"Unknown category '{category}', defaulting to prompt-packs")
        category = "prompt-packs"

    log("generate-product", f"Generating {category} for: \"{idea['title']}\"")

    pid = product_id(idea["title"], category)
    assets_dir = f"products/{pid}/assets"
    ensure_dir(assets_dir)

    if category == "prompt-packs":
        meta = _gen_prompt_pack(idea, pid, assets_dir)
    elif category == "checklist":
        meta = _gen_checklist(idea, pid, assets_dir)
    elif category == "swipe-file":
        meta = _gen_swipe_file(idea, pid, assets_dir)
    elif category == "mini-guide":
        meta = _gen_mini_guide(idea, pid, assets_dir)
    elif category == "n8n-template":
        meta = _gen_n8n_template(idea, pid, assets_dir)

    # Generate rich Gumroad description and store in meta
    try:
        meta["gumroad_description"] = _gen_gumroad_description(idea, meta)
    except Exception as e:
        log("generate-product", f"Warning: could not generate Gumroad description: {e}")
        meta["gumroad_description"] = None

    write_file(f"products/{pid}/meta.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    idea["status"] = "produced"
    idea["product_id"] = pid
    write_json("data/idea-backlog.json", backlog)

    log("generate-product", f"Product created at products/{pid}/")
    return meta


# ── Prompt Pack ──────────────────────────────────────────────────────────────

def _gen_prompt_pack(idea: dict, pid: str, assets_dir: str) -> dict:
    message = client.messages.create(
        model=MODEL,
        max_tokens=8096,
        messages=[{
            "role": "user",
            "content": f"""Create a professional prompt pack titled "{idea['title']}".

Target audience and purpose: {idea['description']}

Generate exactly 20 high-quality, immediately usable prompts. Each prompt should:
- Be complete and self-contained (works without additional context)
- Include clear placeholders like [PRODUCT NAME] or [TARGET AUDIENCE] where customization is needed
- Be specific enough to produce consistent, high-quality results
- Cover different angles, use cases, and scenarios within the theme
- Be written for use with any modern AI assistant (ChatGPT, Claude, Gemini, and others)

Return ONLY a valid JSON array, no other text. Schema:
[
  {{
    "id": 1,
    "title": "Short descriptive title (max 8 words)",
    "prompt": "The full prompt text ready to use",
    "use_case": "When to use this (max 12 words)"
  }}
]""",
        }],
    )

    if message.stop_reason == "max_tokens":
        log("generate-product", "Warning: response truncated at max_tokens — attempting JSON repair")
    prompts = extract_json(message.content[0].text.strip(), array=True)
    log("generate-product", f"Generated {len(prompts)} prompts")

    write_file(f"{assets_dir}/prompts.json", json.dumps(prompts, indent=2, ensure_ascii=False) + "\n")
    write_file(f"{assets_dir}/prompts.md", _prompts_md(idea, prompts))
    write_file(f"{assets_dir}/README.md", _prompts_readme(idea, len(prompts)))

    return {
        "id": pid, "title": idea["title"], "description": idea["description"],
        "category": "prompt-packs", "tags": idea.get("tags", []),
        "item_count": len(prompts), "prompt_count": len(prompts),
        "created_at": timestamp(), "status": "generated",
        "package_path": None, "site_path": None, "thumbnail": None, "price": None, "gumroad_product_id": None, "gumroad_url": None,
    }


def _prompts_md(idea, prompts):
    lines = [f"# {idea['title']}", "", f"> {idea['description']}", "", "---", "",
             f"## Prompts ({len(prompts)} total)", ""]
    for p in prompts:
        lines += [f"### {p['id']}. {p['title']}", "", f"**Use case:** {p['use_case']}", "",
                  "```", p["prompt"], "```", ""]
    return "\n".join(lines)


def _prompts_readme(idea, count):
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


# ── Checklist ────────────────────────────────────────────────────────────────

def _gen_checklist(idea: dict, pid: str, assets_dir: str) -> dict:
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Create a professional actionable checklist titled "{idea['title']}".

Target audience and purpose: {idea['description']}

Generate 15-20 checklist items. Each item should:
- Be a concrete, actionable step (starts with a verb)
- Include a brief explanation of why it matters or what to check for
- Be ordered logically (preparation → execution → review)
- Be specific enough to be immediately useful

Return ONLY a valid JSON array, no other text. Schema:
[
  {{
    "id": 1,
    "item": "Actionable step text",
    "why": "Why this matters or what to look for",
    "section": "Section name (e.g. Preparation, Execution, Review)"
  }}
]""",
        }],
    )

    if message.stop_reason == "max_tokens":
        log("generate-product", "Warning: response truncated at max_tokens — attempting JSON repair")
    items = extract_json(message.content[0].text.strip(), array=True)
    log("generate-product", f"Generated {len(items)} checklist items")

    write_file(f"{assets_dir}/checklist.json", json.dumps(items, indent=2, ensure_ascii=False) + "\n")
    write_file(f"{assets_dir}/checklist.md", _checklist_md(idea, items))
    write_file(f"{assets_dir}/README.md", _checklist_readme(idea, len(items)))

    return {
        "id": pid, "title": idea["title"], "description": idea["description"],
        "category": "checklist", "tags": idea.get("tags", []),
        "item_count": len(items),
        "created_at": timestamp(), "status": "generated",
        "package_path": None, "site_path": None, "thumbnail": None, "price": None, "gumroad_product_id": None, "gumroad_url": None,
    }


def _checklist_md(idea, items):
    lines = [f"# {idea['title']}", "", f"> {idea['description']}", "", "---", ""]
    current_section = None
    for item in items:
        section = item.get("section", "")
        if section and section != current_section:
            lines += [f"## {section}", ""]
            current_section = section
        lines += [
            f"- [ ] **{item['item']}**",
            f"  *{item['why']}*",
            "",
        ]
    return "\n".join(lines)


def _checklist_readme(idea, count):
    return f"""# {idea['title']}

{idea['description']}

## What's included

- **{count} actionable checklist items**
- Organized by phase for easy use
- Each item includes context explaining why it matters
- Markdown format — use in any app or print it

## How to use

1. Open `checklist.md`
2. Work through each section in order
3. Check off items as you complete them
4. Use `checklist.json` to import into your own tools

## Files

- `checklist.md` — Formatted checklist ready to use
- `checklist.json` — Structured data for import or automation
- `README.md` — This file
"""


# ── Swipe File ───────────────────────────────────────────────────────────────

def _gen_swipe_file(idea: dict, pid: str, assets_dir: str) -> dict:
    message = client.messages.create(
        model=MODEL,
        max_tokens=6144,
        messages=[{
            "role": "user",
            "content": f"""Create a professional swipe file titled "{idea['title']}".

Target audience and purpose: {idea['description']}

Generate 20-25 real-world, copy-ready examples. Each example should:
- Be immediately usable — copy, paste, adapt
- Be specific and concrete (not a template with too many blanks)
- Include a brief note on when or how to use it
- Cover varied scenarios, tones, or situations within the theme

Return ONLY a valid JSON array, no other text. Schema:
[
  {{
    "id": 1,
    "title": "Short label for this example",
    "example": "The full copy-ready text",
    "notes": "When to use this / what makes it work"
  }}
]""",
        }],
    )

    if message.stop_reason == "max_tokens":
        log("generate-product", "Warning: response truncated at max_tokens — attempting JSON repair")
    examples = extract_json(message.content[0].text.strip(), array=True)
    log("generate-product", f"Generated {len(examples)} swipe file examples")

    write_file(f"{assets_dir}/swipe-file.json", json.dumps(examples, indent=2, ensure_ascii=False) + "\n")
    write_file(f"{assets_dir}/swipe-file.md", _swipe_md(idea, examples))
    write_file(f"{assets_dir}/README.md", _swipe_readme(idea, len(examples)))

    return {
        "id": pid, "title": idea["title"], "description": idea["description"],
        "category": "swipe-file", "tags": idea.get("tags", []),
        "item_count": len(examples),
        "created_at": timestamp(), "status": "generated",
        "package_path": None, "site_path": None, "thumbnail": None, "price": None, "gumroad_product_id": None, "gumroad_url": None,
    }


def _swipe_md(idea, examples):
    lines = [f"# {idea['title']}", "", f"> {idea['description']}", "", "---", ""]
    for ex in examples:
        lines += [
            f"### {ex['id']}. {ex['title']}",
            "",
            ex["example"],
            "",
            f"*{ex['notes']}*",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def _swipe_readme(idea, count):
    return f"""# {idea['title']}

{idea['description']}

## What's included

- **{count} copy-ready examples**
- Each example is immediately usable — copy, adapt, send
- Notes on when and how to use each one
- Markdown and JSON formats included

## How to use

1. Open `swipe-file.md` to browse all examples
2. Find the one that fits your situation
3. Copy and adapt for your context
4. Use `swipe-file.json` to import into your own tools

## Files

- `swipe-file.md` — All examples in readable format
- `swipe-file.json` — Structured data
- `README.md` — This file
"""


# ── Mini Guide ───────────────────────────────────────────────────────────────

def _gen_mini_guide(idea: dict, pid: str, assets_dir: str) -> dict:
    message = client.messages.create(
        model=MODEL,
        max_tokens=6144,
        messages=[{
            "role": "user",
            "content": f"""Create a concise, practical mini-guide titled "{idea['title']}".

Target audience and purpose: {idea['description']}

Write a focused, immediately actionable guide. Structure:
- Brief intro (2-3 sentences: who this is for and what they'll get)
- 4-6 sections, each covering one key concept or step
- Each section: short explanation + 2-3 concrete tips or examples
- Quick-reference summary at the end (key takeaways as bullet points)

Rules:
- Write for practitioners, not beginners — skip basics
- Be specific: real examples, real numbers, real scenarios
- Total length: 600-900 words
- Format in clean Markdown

Return ONLY the guide in Markdown, starting with the title as an H1.""",
        }],
    )

    guide_md = message.content[0].text.strip()
    log("generate-product", f"Generated mini-guide ({len(guide_md)} chars)")

    write_file(f"{assets_dir}/guide.md", guide_md)
    write_file(f"{assets_dir}/README.md", _guide_readme(idea))

    return {
        "id": pid, "title": idea["title"], "description": idea["description"],
        "category": "mini-guide", "tags": idea.get("tags", []),
        "item_count": 1,
        "created_at": timestamp(), "status": "generated",
        "package_path": None, "site_path": None, "thumbnail": None, "price": None, "gumroad_product_id": None, "gumroad_url": None,
    }


def _guide_readme(idea):
    return f"""# {idea['title']}

{idea['description']}

## What's included

- Concise, practitioner-focused guide
- Concrete tips, examples, and frameworks
- Quick-reference summary of key takeaways
- Markdown format — readable anywhere

## How to use

1. Open `guide.md`
2. Read through once for the full picture
3. Use the summary at the end as a quick reference

## Files

- `guide.md` — The complete guide
- `README.md` — This file
"""


# ── n8n Template ─────────────────────────────────────────────────────────────

def _gen_n8n_template(idea: dict, pid: str, assets_dir: str) -> dict:
    message = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": f"""Create a complete, importable n8n workflow template for: "{idea['title']}".

Purpose: {idea['description']}

Generate a realistic n8n workflow JSON. Requirements:
- Use common n8n node types (Webhook, Schedule Trigger, HTTP Request, Set, IF, Code, Email, Slack, Google Sheets, Telegram, etc.)
- Include 4-10 nodes connected logically to accomplish the automation
- Each node must have: id (short unique string), name, type (e.g. "n8n-nodes-base.webhook"), typeVersion (use 1 or 2), position ([x,y] with 200px spacing), parameters (realistic for that node type)
- Connections must reference node names correctly
- workflow "active" should be false
- Include placeholder values for credentials/API keys (e.g. "YOUR_API_KEY", "your-email@example.com")

Return a JSON object with two keys:
1. "workflow": the complete n8n workflow JSON (importable)
2. "setup_steps": array of strings describing setup steps (credentials to configure, values to replace)

Format:
{{
  "workflow": {{ "name": "...", "nodes": [...], "connections": {{...}}, "active": false, "settings": {{}} }},
  "setup_steps": ["Step 1: ...", "Step 2: ..."]
}}

Return ONLY valid JSON, no other text.""",
        }],
    )

    if message.stop_reason == "max_tokens":
        raise RuntimeError(
            "n8n workflow response truncated at max_tokens — skipping this product. "
            "Try an idea with fewer nodes or simpler logic."
        )

    raw = message.content[0].text.strip()
    data = extract_json(raw, array=False)

    workflow = data.get("workflow", {})
    setup_steps = data.get("setup_steps", [])
    node_count = len(workflow.get("nodes", []))
    log("generate-product", f"Generated n8n workflow with {node_count} nodes")

    write_file(f"{assets_dir}/workflow.json", json.dumps(workflow, indent=2, ensure_ascii=False) + "\n")
    write_file(f"{assets_dir}/README.md", _n8n_readme(idea, setup_steps, node_count))

    return {
        "id": pid, "title": idea["title"], "description": idea["description"],
        "category": "n8n-template", "tags": idea.get("tags", []),
        "item_count": node_count,
        "created_at": timestamp(), "status": "generated",
        "package_path": None, "site_path": None, "thumbnail": None, "price": None, "gumroad_product_id": None, "gumroad_url": None,
    }


def _n8n_readme(idea: dict, setup_steps: list, node_count: int) -> str:
    steps_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(setup_steps)) if setup_steps else "1. Configure credentials in n8n\n2. Activate the workflow"
    return f"""# {idea['title']}

{idea['description']}

## What's included

- Ready-to-import n8n workflow (`workflow.json`)
- {node_count} connected nodes
- Setup instructions for credentials and configuration

## How to import

1. Open your n8n instance
2. Go to **Workflows** → **Import from file**
3. Select `workflow.json`
4. Follow the setup steps below

## Setup

{steps_md}

## Requirements

- n8n (self-hosted or n8n.cloud)
- Relevant credentials configured in n8n (see setup steps above)

## Files

- `workflow.json` — Importable n8n workflow
- `README.md` — This file
"""


# ── Gumroad Description ──────────────────────────────────────────────────────

def _gen_gumroad_description(idea: dict, meta: dict) -> str:
    """Generate a rich, persuasive Gumroad product description (HTML)."""
    category = meta.get("category", "prompt-packs")
    item_count = meta.get("item_count", 0)

    format_note = {
        "prompt-packs": f"{item_count} prompts • Markdown + JSON • Works with ChatGPT, Claude, Gemini",
        "checklist":    f"{item_count} checklist items • Markdown + JSON • Context for each step",
        "swipe-file":   f"{item_count} copy-ready examples • Markdown + JSON • Usage notes included",
        "mini-guide":   f"~800-word focused guide • Markdown • Quick-reference summary",
        "n8n-template": f"{item_count}-node n8n workflow • Importable JSON • Setup guide included",
    }.get(category, f"{item_count} items included")

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Write a compelling Gumroad product page description for this digital product.

Product: {idea['title']}
One-liner: {idea['description']}
Format: {format_note}

Requirements:
- Open with a BOLD hook sentence that names the exact pain this solves (no generic fluff)
- "Who this is for" section: 2-3 specific bullet personas (not vague "anyone who...")
- "What's inside" section: itemized list with value framing, not just counts
- One short closing line + simple CTA ("Download and use it today.")
- Tone: direct, confident, peer-to-peer. Not hype, not corporate.
- Length: 120-200 words total
- Output: valid HTML only (p, strong, h3, ul, li tags). No markdown. No preamble.

Start with: <p><strong>[hook sentence]</strong></p>""",
        }],
    )

    desc = message.content[0].text.strip()
    # Strip markdown code fences if the model wrapped the HTML anyway
    desc = re.sub(r"^```[a-z]*\n?", "", desc)
    desc = re.sub(r"\n?```$", "", desc)
    desc = desc.strip()
    desc += '\n\n<p>Discover more tools like this at <a href="https://mini-on-ai.com">mini-on-ai.com</a>.</p>'
    log("generate-product", "Generated Gumroad description")
    return desc


def main():
    generate_product()


if __name__ == "__main__":
    main()
