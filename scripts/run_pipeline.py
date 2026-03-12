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
  3. generate      — create product content
  4. package       — zip product assets
  5. update_site   — add to showcase
  6. telegram      — send report
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from lib.utils import read_json, write_json, timestamp, log
from trend_scan import trend_scan
from idea_rank import idea_rank
from generate_product import generate_product
from package_product import package_product
from update_site import update_site
from telegram_notify import telegram_report


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

    # Stage 1: Trend scan
    if not skip_scan:
        log("pipeline", "--- Stage: trend-scan ---")
        try:
            trend_scan(seed=seed, count=10)
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

    # Stage 6: Telegram report
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
