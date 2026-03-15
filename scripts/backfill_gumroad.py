#!/usr/bin/env python3
"""Backfill gumroad_description for all skill products that have it null."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)

import anthropic
from lib.utils import read_json, write_json, log

ROOT = os.path.join(os.path.dirname(__file__), "..")
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
client = anthropic.Anthropic()

catalog = read_json("data/product-catalog.json")
products = catalog.get("products", [])

to_fix = [p for p in products if p.get("category") == "claude-code-skill" and not p.get("gumroad_description")]
print(f"Found {len(to_fix)} products missing gumroad_description")

for p in to_fix:
    pid = p["id"]
    item_count = p.get("item_count", 5)
    format_note = f"{item_count} ready-to-use SKILL.md files • Drop-in `skills/` folder • Installation guide + quick-reference table"

    print(f"  Generating for: {p['title'][:70]}...")
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": f"""Write a compelling Gumroad product page description for this digital product.

Product: {p['title']}
One-liner: {p['description']}
Format: {format_note}

Requirements:
- Open with a hook sentence that names the exact pain this solves (no generic fluff)
- "Who this is for" section: 2-3 specific bullet personas (not vague "anyone who...")
- "What's inside" section: itemized list with value framing, not just counts
- One short closing line + simple CTA ("Download and use it today.")
- Tone: direct, confident, peer-to-peer. Not hype, not corporate.
- Length: 120-200 words total
- Output: plain text only. Use blank lines between sections. Use "—" bullets. No HTML, no markdown, no preamble."""}],
        )
        desc = msg.content[0].text.strip()
        desc = re.sub(r"^```[a-z]*\n?", "", desc)
        desc = re.sub(r"\n?```$", "", desc)
        desc = desc.strip() + "\n\nDiscover more tools like this at mini-on-ai.com"

        p["gumroad_description"] = desc

        meta_path = os.path.join(ROOT, "products", pid, "meta.json")
        if os.path.exists(meta_path):
            meta = json.loads(open(meta_path).read())
            meta["gumroad_description"] = desc
            open(meta_path, "w").write(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
            print(f"    ✓ meta.json updated")

    except Exception as e:
        print(f"    ✗ Failed: {e}")

write_json("data/product-catalog.json", catalog)
print("\nDone. Now rebuilding site pages...")
os.system("python3 scripts/update_site.py --rebuild-all")
