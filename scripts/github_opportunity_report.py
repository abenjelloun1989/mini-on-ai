#!/usr/bin/env python3
"""
github_opportunity_report.py — Daily GitHub trending → market opportunity report.

Fetches the top trending GitHub repos from the past 7 days, runs Claude market
analysis, and delivers a report via Telegram + personal email.

Run: python3 scripts/github_opportunity_report.py
Scheduled: daily at 7:00am via launchd (com.mini-on-ai.github-opportunity.plist)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

import anthropic
from lib.utils import read_json, write_json, log, timestamp, extract_json
from telegram_notify import send_telegram
from email_blast import _brevo, _text_to_html, SENDER_NAME, SENDER_EMAIL

# ── Config ────────────────────────────────────────────────────────────────────

GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN", "")
OWNER_EMAIL     = os.getenv("OWNER_EMAIL", "kirozdormu@gmail.com")
CLAUDE_MODEL    = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
REPO_COUNT      = 25   # repos to fetch
SCORE_THRESHOLD = 60   # minimum score to include in report
HOT_THRESHOLD   = 80   # "hot" badge threshold
TOP_TELEGRAM    = 3    # top N ideas sent via Telegram
RUN_LOG         = "data/github-opportunity-runs.json"

# ── GitHub fetch ──────────────────────────────────────────────────────────────

def fetch_trending_repos(days: int = 7, count: int = REPO_COUNT) -> list[dict]:
    """Fetch repos created in the last N days, sorted by stars."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    url = (
        f"https://api.github.com/search/repositories"
        f"?q=created:>{since}&sort=stars&order=desc&per_page={count}"
    )
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # nosec B310
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API error {e.code}: {e.read().decode()}") from None

    repos = []
    for r in data.get("items", []):
        repos.append({
            "name":        r["full_name"],
            "description": (r.get("description") or "")[:200],
            "stars":       r["stargazers_count"],
            "language":    r.get("language") or "Unknown",
            "topics":      r.get("topics", [])[:8],
            "url":         r["html_url"],
            "created_at":  r["created_at"],
        })
    log("github-scout", f"Fetched {len(repos)} trending repos (last {days} days)")
    return repos


# ── Claude analysis ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a market analyst for mini-on-ai.com, a digital product factory
that sells prompt packs, checklists, mini-guides, and Chrome extensions to freelancers,
developers, and small business owners on Gumroad ($9–$49).

Products take 1–2 hours to generate with AI. The best opportunities are problems that:
- Many freelancers/devs/creators face repeatedly
- Have no good existing prompt pack or guide on Gumroad
- Are directly related to what the trending repo is solving

Product types available:
- prompt-pack: 20–30 ready-to-use AI prompts ($19)
- checklist: 15–20 step action list ($9–$19)
- mini-guide: concise practitioner guide 800–1200 words ($9)
- chrome-extension: browser tool (bigger build, score only if truly obvious gap)"""

def _load_existing_titles() -> list[str]:
    """Return titles of already-published products so Claude can avoid them."""
    catalog_path = ROOT / "data/product-catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text())
        return [p["title"] for p in catalog.get("products", []) if p.get("title")]
    except Exception:
        return []


def analyze_repos(repos: list[dict]) -> list[dict]:
    """Ask Claude to score each repo for product opportunity. Returns sorted list."""
    client = anthropic.Anthropic()

    existing_titles = _load_existing_titles()
    existing_block = ""
    if existing_titles:
        titles_str = "\n".join(f"- {t}" for t in existing_titles)
        existing_block = f"""
IMPORTANT — already published products (do NOT propose anything that covers the same topic):
{titles_str}

Score 0 for any idea that substantially overlaps with the above list.
"""

    repos_json = json.dumps(repos, indent=2)
    prompt = f"""Here are {len(repos)} trending GitHub repos from the past 7 days.
{existing_block}
For each repo, score the digital product opportunity for mini-on-ai.com (0–100).
Only score above 60 if there is a real, specific product gap worth building.

Return a JSON array (no markdown, raw JSON only) with one object per repo:
{{
  "repo": "owner/name",
  "stars": 1234,
  "score": 75,
  "opportunity_type": "prompt-pack",
  "product_title": "Exact product title (max 8 words)",
  "rationale": "2 sentences: why this score, what gap exists",
  "plan_prompt": "A complete, self-contained prompt the developer pastes into Claude Code plan mode. Start with: /plan [full description of what to build, including product type, audience, number of items, key sections, tone, and why it will sell]. Make it actionable and specific."
}}

Repos to analyze:
{repos_json}"""

    log("github-scout", "Running Claude market analysis...")
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    ideas = extract_json(raw, array=True)
    if not isinstance(ideas, list):
        raise RuntimeError(f"Claude returned unexpected format: {raw[:200]}")

    # Filter and sort
    ideas = [i for i in ideas if isinstance(i.get("score"), int) and i["score"] >= SCORE_THRESHOLD]
    ideas.sort(key=lambda x: x["score"], reverse=True)
    log("github-scout", f"Analysis complete — {len(ideas)} opportunities scored ≥{SCORE_THRESHOLD}")
    return ideas


# ── Email report ──────────────────────────────────────────────────────────────

def build_email_html(ideas: list[dict], repos_count: int, run_date: str) -> str:
    """Build a rich HTML email report."""
    hot = [i for i in ideas if i["score"] >= HOT_THRESHOLD]
    rest = [i for i in ideas if i["score"] < HOT_THRESHOLD]
    top_score = ideas[0]["score"] if ideas else 0

    def idea_block(idea: dict, hot: bool = False) -> str:
        badge = "🔥 " if hot else ""
        type_label = idea.get("opportunity_type", "product").upper()
        return f"""
        <div style="border:1px solid {'#f59e0b' if hot else '#e5e7eb'};border-radius:10px;padding:20px;margin-bottom:16px;background:{'#fffbeb' if hot else '#f9fafb'};">
          <p style="margin:0 0 6px;font-size:18px;font-weight:700;color:#111827;">
            {badge}[{idea['score']}/100] {idea.get('product_title','?')}
          </p>
          <p style="margin:0 0 8px;font-size:12px;color:#6b7280;">
            📦 {type_label} &nbsp;·&nbsp;
            🔗 <a href="https://github.com/{idea.get('repo','')}" style="color:#6366f1;">github.com/{idea.get('repo','')}</a>
            &nbsp;·&nbsp; ⭐ {idea.get('stars',0):,} stars this week
          </p>
          <p style="margin:0 0 12px;font-size:14px;color:#374151;line-height:1.6;">{idea.get('rationale','')}</p>
          <div style="background:#1e1e2e;border-radius:6px;padding:14px;font-family:monospace;font-size:13px;color:#e2e8f0;white-space:pre-wrap;">{idea.get('plan_prompt','')}</div>
        </div>"""

    hot_blocks = "".join(idea_block(i, hot=True) for i in hot) if hot else \
        "<p style='color:#6b7280;'>No high-scoring opportunities today.</p>"
    rest_blocks = "".join(idea_block(i) for i in rest) if rest else ""
    rest_section = f"""
      <h2 style="font-size:16px;font-weight:700;color:#374151;margin:32px 0 12px;">📉 Other ideas ({len(rest)})</h2>
      {rest_blocks}""" if rest else ""

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 16px;">
    <tr><td align="center">
      <table width="640" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;padding:40px;max-width:640px;">
        <tr><td>
          <p style="margin:0 0 4px;font-size:20px;font-weight:800;color:#6366f1;">mini-on-ai · GitHub Scout</p>
          <p style="margin:0 0 28px;font-size:13px;color:#9ca3af;">{run_date}</p>

          <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin-bottom:28px;">
            <p style="margin:0;font-size:14px;color:#166534;">
              📊 <strong>{repos_count} repos analyzed</strong> &nbsp;·&nbsp;
              <strong>{len(ideas)} opportunities found</strong> &nbsp;·&nbsp;
              Top score: <strong>{top_score}/100</strong>
            </p>
          </div>

          <h2 style="font-size:18px;font-weight:700;color:#111827;margin:0 0 16px;">🔥 High-opportunity ideas ({len(hot)})</h2>
          {hot_blocks}
          {rest_section}

          <hr style="border:none;border-top:1px solid #e5e7eb;margin:32px 0;">
          <p style="margin:0;font-size:12px;color:#9ca3af;">
            Daily GitHub Opportunity Scout · <a href="https://mini-on-ai.com" style="color:#6366f1;">mini-on-ai.com</a>
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""


def send_email_report(ideas: list[dict], repos_count: int) -> bool:
    """Send personal transactional email (not subscriber blast)."""
    if not os.getenv("BREVO_API_KEY"):
        log("github-scout", "BREVO_API_KEY not set — skipping email")
        return False

    run_date = datetime.now().strftime("%A, %B %-d, %Y")
    top_score = ideas[0]["score"] if ideas else 0
    subject = f"🔍 GitHub Scout — {run_date} — {len(ideas)} ideas, top {top_score}/100"
    html = build_email_html(ideas, repos_count, run_date)

    try:
        _brevo("POST", "/smtp/email", {
            "sender":      {"name": SENDER_NAME, "email": SENDER_EMAIL},
            "to":          [{"email": OWNER_EMAIL, "name": "Mini-on-AI"}],
            "subject":     subject,
            "htmlContent": html,
        })
        log("github-scout", f"Email sent to {OWNER_EMAIL}")
        return True
    except Exception as e:
        log("github-scout", f"Email failed: {e}")
        return False


# ── Telegram summary (numbered list + build buttons) ─────────────────────────

def _tg_escape(text: str) -> str:
    """Escape special HTML chars for Telegram HTML mode."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def save_latest_opportunities(ideas: list[dict]) -> None:
    """Persist the current ranked list so the bot can reference it by index."""
    indexed = [{"index": i + 1, **idea} for i, idea in enumerate(ideas)]
    write_json("data/github-scout-latest.json", indexed)
    log("github-scout", f"Saved {len(indexed)} opportunities to data/github-scout-latest.json")


def send_telegram_summary(ideas: list[dict], repos_count: int) -> bool:
    """
    Send a compact numbered list with inline 🔨 #N build buttons.
    Full details go to email; this message is the quick decision surface.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_OWNER_ID") or os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log("github-scout", "Telegram credentials not set — skipping summary")
        return False

    date_str = datetime.now().strftime("%d %b %Y")
    top_score = ideas[0]["score"] if ideas else 0

    lines = [
        f"🔍 <b>GitHub Scout — {date_str}</b>",
        f"📊 {repos_count} repos · {len(ideas)} opportunities · top {top_score}/100\n",
    ]
    for i, idea in enumerate(ideas, 1):
        hot = "🔥" if idea["score"] >= HOT_THRESHOLD else "📦"
        title = _tg_escape(idea.get("product_title", "?"))[:45]
        otype = _tg_escape(idea.get("opportunity_type", ""))
        lines.append(f"{i}. {hot} [{idea['score']}] {title} <i>({otype})</i>")

    lines.append("\n<i>Full report → email · Tap a number to build 👇</i>")
    text = "\n".join(lines)

    # Inline keyboard: 3 build buttons per row
    all_btns = [{"text": f"🔨 #{i}", "callback_data": f"scout:build:{i}"}
                for i in range(1, len(ideas) + 1)]
    keyboard = [all_btns[j:j + 3] for j in range(0, len(all_btns), 3)]

    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": keyboard},
    }).encode("utf-8")

    import urllib.request as _req
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    request = _req.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with _req.urlopen(request, timeout=15) as resp:  # nosec B310
            ok = resp.status == 200
        log("github-scout", f"Telegram summary sent ({len(ideas)} opportunities)")
        return ok
    except Exception as e:
        log("github-scout", f"Telegram summary failed: {e}")
        return False


# ── Run log ───────────────────────────────────────────────────────────────────

def log_run(repos_count: int, ideas: list[dict]) -> None:
    try:
        runs = read_json(RUN_LOG) if Path(ROOT / RUN_LOG).exists() else []
    except Exception:
        runs = []
    runs.append({
        "run_at":       timestamp(),
        "repos_fetched": repos_count,
        "ideas_found":  len(ideas),
        "top_score":    ideas[0]["score"] if ideas else 0,
        "ideas":        ideas,
    })
    write_json(RUN_LOG, runs)


# ── Dry run ───────────────────────────────────────────────────────────────────

def dry_run():
    """Fetch repos + run analysis, then print full output without sending anything."""
    log("github-scout", "[DRY RUN] Starting...")
    repos = fetch_trending_repos()
    if not repos:
        print("No repos fetched.")
        return

    ideas = analyze_repos(repos)
    date_str = datetime.now().strftime("%A, %B %-d, %Y")

    print("\n" + "="*70)
    print(f"  GITHUB OPPORTUNITY SCOUT — DRY RUN — {date_str}")
    print(f"  {len(repos)} repos scanned · {len(ideas)} opportunities ≥{SCORE_THRESHOLD}")
    print("="*70)

    if not ideas:
        print(f"\n  No opportunities found ≥{SCORE_THRESHOLD} today.\n")
        return

    for idea in ideas:
        hot = " 🔥 HOT" if idea["score"] >= HOT_THRESHOLD else ""
        print(f"\n{'─'*70}")
        print(f"  [{idea['score']}/100]{hot}  {idea.get('product_title','?')}")
        print(f"  Type: {idea.get('opportunity_type','?').upper()}  ·  "
              f"github.com/{idea.get('repo','')}  ·  ⭐ {idea.get('stars',0):,}")
        print(f"\n  {idea.get('rationale','')}")
        print(f"\n  📋 PLAN PROMPT:")
        print(f"  {idea.get('plan_prompt','')}")

    print(f"\n{'='*70}")
    print(f"  [DRY RUN] No email or Telegram sent.\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print report without sending")
    parser.add_argument("--skip-email", action="store_true", help="Skip email (re-send Telegram only)")
    args = parser.parse_args()

    if args.dry_run:
        dry_run()
        return

    log("github-scout", "Starting daily GitHub opportunity scan...")
    start = time.time()

    repos = fetch_trending_repos()
    if not repos:
        log("github-scout", "No repos fetched — aborting")
        return

    ideas = analyze_repos(repos)

    if not ideas:
        log("github-scout", f"No opportunities ≥{SCORE_THRESHOLD} today out of {len(repos)} repos scanned.")
        log_run(len(repos), [])
        return

    save_latest_opportunities(ideas)
    if not args.skip_email:
        send_email_report(ideas, len(repos))
    else:
        log("github-scout", "Skipping email (--skip-email)")
    send_telegram_summary(ideas, len(repos))
    log_run(len(repos), ideas)

    elapsed = round(time.time() - start, 1)
    log("github-scout", f"Done in {elapsed}s — {len(ideas)} opportunities delivered")


if __name__ == "__main__":
    main()
