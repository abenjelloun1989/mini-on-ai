#!/usr/bin/env python3
"""
run_pipeline.py
Orchestrates the full factory pipeline end-to-end.

Usage:
  python3 scripts/run_pipeline.py
  python3 scripts/run_pipeline.py --seed "marketing"
  python3 scripts/run_pipeline.py --skip-scan   (use existing backlog)

Stages:
  1. trend_scan    — generate ideas
  2. idea_rank     — score and select best idea
  2.5 approval     — wait for Telegram Go / No Go
  3. generate      — create product content
  4. package       — zip product assets
  5. update_site   — add to showcase
  6. git commit    — push to GitHub
  7. telegram      — send report
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, write_json, timestamp, log, ROOT
from trend_scan import trend_scan
from idea_rank import idea_rank
from generate_product import generate_product
from package_product import package_product
from update_site import update_site
from telegram_notify import telegram_report, send_approval_request

APPROVAL_TIMEOUT_HOURS = 48


def request_approval(idea: dict) -> bool:
    """Send idea to Telegram for approval. Blocks until Go/No Go or timeout."""
    state = {
        "status": "pending",
        "idea": idea,
        "requested_at": timestamp(),
        "decided_at": None,
    }
    write_json("data/approval-state.json", state)

    try:
        send_approval_request(idea)
    except Exception as e:
        log("pipeline", f"Warning: could not send approval request: {e}")

    log("pipeline", f"Waiting for approval (timeout: {APPROVAL_TIMEOUT_HOURS}h)...")
    deadline = time.time() + APPROVAL_TIMEOUT_HOURS * 3600

    while time.time() < deadline:
        try:
            current = read_json("data/approval-state.json")
        except Exception:
            time.sleep(5)
            continue

        status = current.get("status")
        if status == "approved":
            log("pipeline", "Approval received: Go")
            return True
        if status == "rejected":
            log("pipeline", "Approval received: No Go")
            return False

        time.sleep(5)

    log("pipeline", "Approval timed out")
    write_json("data/approval-state.json", {**state, "status": "timeout"})
    return False


def run_pipeline(seed: str = "", skip_scan: bool = False):
    start_time = time.time()

    run = {
        "id": f"run-{int(time.time())}",
        "started_at": timestamp(),
        "status": "running",
        "failed_stage": None,
        "error": None,
        "product": None,
        "duration_seconds": None,
    }

    pipeline_log = read_json("data/pipeline-log.json")

    def fail(stage: str, error: str):
        run["status"] = "failed"
        run["failed_stage"] = stage
        run["error"] = error
        run["duration_seconds"] = round(time.time() - start_time)
        pipeline_log["runs"].append(run)
        write_json("data/pipeline-log.json", pipeline_log)
        try:
            telegram_report()
        except Exception as e:
            log("telegram", f"Warning: notification failed: {e}")
        sys.exit(1)

    # Stage 1: Trend scan — only if available idea pool is low
    if not skip_scan:
        log("pipeline", "--- Stage: trend-scan ---")
        try:
            backlog = read_json("data/idea-backlog.json")
            available = [
                i for i in backlog.get("ideas", [])
                if i.get("status") not in ("produced", "rejected")
            ]
            if len(available) < 5 or seed:
                log("pipeline", f"Available ideas: {len(available)} — scanning for more...")
                trend_scan(seed=seed, count=10)
            else:
                log("pipeline", f"Available ideas: {len(available)} — skipping scan (pool sufficient)")
        except Exception as e:
            fail("trend-scan", str(e))
    else:
        log("pipeline", "Skipping trend-scan (--skip-scan)")

    # Stage 2: Idea rank
    log("pipeline", "--- Stage: idea-rank ---")
    try:
        selected = idea_rank()
        if not selected:
            fail("idea-rank", "No ideas available to rank")
    except Exception as e:
        fail("idea-rank", str(e))

    # Stage 2.5: Approval gate
    log("pipeline", "--- Stage: approval ---")
    approved = request_approval(selected)
    if not approved:
        # Mark idea as rejected so it won't be selected again
        try:
            backlog = read_json("data/idea-backlog.json")
            for idea in backlog.get("ideas", []):
                if idea.get("selected") and idea.get("title") == selected.get("title"):
                    idea["selected"] = False
                    idea["status"] = "rejected"
            write_json("data/idea-backlog.json", backlog)
        except Exception as e:
            log("pipeline", f"Warning: could not update backlog: {e}")

        # Pause the daemon — don't propose the next idea until user sends /resume
        try:
            import json as _json
            (ROOT / "data/daemon-state.json").write_text(_json.dumps({"paused": True}))
            log("pipeline", "Daemon paused after rejection. Waiting for /resume.")
        except Exception as e:
            log("pipeline", f"Warning: could not pause daemon: {e}")

        fail("approval", "Idea rejected")

    # Stage 3: Generate product
    log("pipeline", "--- Stage: generate-product ---")
    try:
        meta = generate_product()
    except Exception as e:
        fail("generate-product", str(e))

    # Stage 4: Package product
    log("pipeline", "--- Stage: package-product ---")
    try:
        meta = package_product()
    except Exception as e:
        fail("package-product", str(e))

    # Stage 5: Update site
    log("pipeline", "--- Stage: update-site ---")
    try:
        meta = update_site()
    except Exception as e:
        fail("update-site", str(e))

    # Success
    duration = round(time.time() - start_time)
    run["status"] = "success"
    run["product"] = {
        "id": meta["id"],
        "title": meta["title"],
        "description": meta["description"],
    }
    run["duration_seconds"] = duration

    pipeline_log["runs"].append(run)
    write_json("data/pipeline-log.json", pipeline_log)

    log("pipeline", f"--- Pipeline complete in {duration}s ---")
    log("pipeline", f"Product: {meta['title']}")

    import os
    site_url = os.getenv("SITE_URL", "file://./site")
    log("pipeline", f"Site: {site_url}/products/{meta['id']}.html")

    # Stage 6: Git commit + push (site + data + product assets)
    log("pipeline", "--- Stage: git-commit ---")
    try:
        subprocess.run(
            ["git", "add", "site/", "data/", f"products/{meta['id']}/"],
            cwd=str(ROOT), check=True, capture_output=True
        )
        # Only commit if there are staged changes
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(ROOT), capture_output=True
        )
        if diff.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"product: {meta['title']}"],
                cwd=str(ROOT), check=True, capture_output=True
            )
            log("pipeline", "Git commit created")
        else:
            log("pipeline", "No staged changes to commit")

        # Always push to keep remote in sync
        push = subprocess.run(
            ["git", "push"],
            cwd=str(ROOT), capture_output=True, text=True
        )
        if push.returncode == 0:
            log("pipeline", "Pushed to remote — GitHub Pages deploy triggered")
        else:
            log("pipeline", f"Git push failed: {push.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        log("pipeline", f"Git stage error: {e.stderr.decode().strip() if e.stderr else str(e)}")

    # Stage 7: Telegram report
    log("pipeline", "--- Stage: telegram-report ---")
    try:
        telegram_report()
    except Exception as e:
        log("telegram", f"Warning: notification failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Run the full product factory pipeline")
    parser.add_argument("--seed", default="", help="Keyword to seed the trend scan")
    parser.add_argument("--skip-scan", action="store_true", help="Skip trend scan, use existing backlog")
    args = parser.parse_args()

    run_pipeline(seed=args.seed, skip_scan=args.skip_scan)


if __name__ == "__main__":
    main()
