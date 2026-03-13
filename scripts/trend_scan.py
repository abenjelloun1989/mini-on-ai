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
from lib.utils import read_json, write_json, timestamp, log, extract_json, log_token_usage
from lib.trend_sources import get_google_trends_rising

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


SKILL_SEED_TOPICS = [
    "code review and pull request automation",
    "deployment and CI/CD pipelines",
    "documentation generation from code",
    "API design and testing workflows",
    "data analysis and reporting pipelines",
    "content creation and publishing automation",
    "project management and sprint planning",
    "database migration and schema management",
    "security auditing and dependency checks",
    "onboarding new team members to codebases",
    "refactoring and technical debt reduction",
    "customer support ticket triage and response",
    "social media scheduling and analytics",
    "design system and component library maintenance",
]


def _trend_scan_skills(count: int = 5) -> list:
    """Generate Claude Code skill guide ideas based on high-demand workflows."""
    import random
    topic = random.choice(SKILL_SEED_TOPICS)
    log("trend-scan", f"Generating {count} Claude Code skill ideas (topic: {topic})...")

    backlog = read_json("data/idea-backlog.json")
    existing_titles = [i["title"] for i in backlog.get("ideas", [])]
    avoid_block = ""
    if existing_titles:
        avoid_list = "\n".join(f"- {t}" for t in existing_titles[-20:])
        avoid_block = f"\n\nDo NOT suggest any of these already-existing ideas:\n{avoid_list}"

    message = client.messages.create(
        model=MODEL,
        max_tokens=1536,
        messages=[{
            "role": "user",
            "content": f"""Generate {count} Claude Code skill guide product ideas for the topic: "{topic}".

Claude Code skills are SKILL.md files that give Claude Code specialized capabilities for specific
workflows. Each guide teaches practitioners how to build and configure one skill.

Rules:
- Each skill must solve a real, recurring developer or professional workflow problem
- Skills should work across different roles (devs, marketers, ops, designers, etc.)
- Title format: "Claude Code Skill: [Skill Name] — [What It Does]"
  e.g., "Claude Code Skill: PR Reviewer — Automated Code Review and Feedback"
- Description: exact role + exact benefit from this skill
- Tags: include "claude-code", "skills" + 2-3 domain-specific tags{avoid_block}

Return ONLY a valid JSON array:
[
  {{
    "title": "Claude Code Skill: Name — What It Does",
    "description": "For [role], this skill [does what] so they can [benefit]",
    "category": "claude-code-skill",
    "tags": ["claude-code", "skills", "tag3", "tag4"]
  }}
]""",
        }],
    )

    log_token_usage("trend-scan", message.usage, MODEL)
    ideas_raw = extract_json(message.content[0].text.strip(), array=True)
    log("trend-scan", f"Generated {len(ideas_raw)} skill ideas")

    backlog = read_json("data/idea-backlog.json")
    new_ideas = []
    for i, idea in enumerate(ideas_raw):
        new_idea = {
            "id": f"idea-{int(time.time())}-skill-{i}",
            "title": idea["title"],
            "description": idea["description"],
            "category": "claude-code-skill",
            "tags": idea.get("tags", ["claude-code", "skills"]),
            "score": None, "rationale": None, "selected": False,
            "status": None, "product_id": None,
            "generated_at": timestamp(),
            "source": "trend-scan-skills",
        }
        new_ideas.append(new_idea)
        time.sleep(0.001)

    backlog["ideas"].extend(new_ideas)
    write_json("data/idea-backlog.json", backlog)
    log("trend-scan", f"Added {len(new_ideas)} skill ideas to backlog.")
    return new_ideas


def trend_scan(seed: str = "", count: int = 10) -> list:
    import random

    # If the category focus is claude-code-skill, use the specialist scanner
    category_focus = os.environ.get("PIPELINE_CATEGORY_FOCUS", "").strip()
    if category_focus == "claude-code-skill":
        return _trend_scan_skills(count=min(count, 5))

    # Pick a seed: user-supplied, or rotate through diverse topics
    active_seed = seed or random.choice(SEED_ROTATION)
    log("trend-scan", f"Generating {count} ideas (focus: {active_seed})...")

    # Fetch real trend signals from Google Trends
    log("trend-scan", "Fetching live trend signals from Google Trends...")
    trend_signals = get_google_trends_rising(max_terms=20)
    if trend_signals:
        log("trend-scan", f"Got {len(trend_signals)} rising queries")
        trends_block = "\n\nCurrently rising search trends (use these as inspiration for real demand):\n" + \
            "\n".join(f"- {t}" for t in trend_signals)
    else:
        log("trend-scan", "No trend signals available — generating from seed only")
        trends_block = ""

    # Pull titles already in backlog to avoid duplicates
    backlog = read_json("data/idea-backlog.json")
    existing_titles = [i["title"] for i in backlog.get("ideas", [])]
    avoid_block = ""
    if existing_titles:
        avoid_list = "\n".join(f"- {t}" for t in existing_titles[-30:])
        avoid_block = f"\n\nDo NOT suggest any of these already-existing ideas:\n{avoid_list}"

    message = client.messages.create(
        model=MODEL,
        max_tokens=1536,
        messages=[
            {
                "role": "user",
                "content": f"""Generate {count} highly specific, niche digital product ideas for download.

Target audience for this batch: {active_seed}{trends_block}

Rules:
- Each product must solve one specific, painful daily workflow problem that the target audience faces
- Title must be concrete and operational (e.g. "Client Onboarding Checklist for Freelance Designers" not "Onboarding Tips")
- Where the trend signals above are relevant to the target audience, use them to inspire ideas grounded in real demand
- Avoid generic topics like "productivity", "writing", "ChatGPT tips" — go niche
- Each idea must be genuinely different (different sub-audience or use case)
- Think: what does this person struggle with every week in their actual work?{avoid_block}

AVOID these over-used angles (already too many of these):
- Do NOT suggest ideas primarily about writing emails or email subject lines
- Do NOT suggest generic "AI prompt packs" — the content must be a real operational artifact, not meta-instructions about using AI
- Do NOT suggest "ChatGPT prompts for X" or "AI prompts for Y" framing — focus on the work output, not the AI tool
- Avoid ideas that are just templates for sending messages (cold outreach, DMs, follow-ups) unless the audience genuinely needs a full library

Instead, focus on the operational work itself:
- Analysis frameworks, audit checklists, decision trees
- Client-facing deliverables: proposals, briefs, reports, SOPs
- Research and planning tools: swipe files of real examples, reference guides
- Process automation: specific tool integrations (Notion + Zapier, Typeform + Slack, etc.)
- Domain-specific workflows: pricing calculators (as guides), project scoping, onboarding flows, retrospectives

Product categories — assign the BEST fit:
- "prompt-packs"  → 20 AI prompts for a specific operational workflow (only when prompts are genuinely the best format)
- "checklist"     → step-by-step checklist for a repeatable process (use for audits, launches, onboarding, reviews)
- "swipe-file"    → library of real copy-ready examples (proposals, scripts, pricing tiers, case study structures)
- "mini-guide"    → concise practitioner guide for one specific skill or framework (600-900 words, actionable)
- "n8n-template"  → automation workflow connecting SPECIFIC named tools (e.g. "Typeform → Notion → Slack")

REQUIRED category distribution for this batch of {count} ideas — these are hard counts, not suggestions:
- Exactly 4 × "prompt-packs"
- Exactly 2 × "checklist"
- Exactly 2 × "swipe-file"
- Exactly 1 × "mini-guide"
- Exactly 1 × "n8n-template"
You MUST output exactly these counts. Count your assignments before returning.

Return ONLY a valid JSON array, no other text. Schema:
[
  {{
    "title": "Specific title (5-9 words)",
    "description": "One sentence: exact audience + exact benefit they get",
    "category": "checklist",
    "tags": ["tag1", "tag2", "tag3"]
  }}
]""",
            }
        ],
    )

    log_token_usage("trend-scan", message.usage, MODEL)
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
            "category": idea.get("category", "prompt-packs"),
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
