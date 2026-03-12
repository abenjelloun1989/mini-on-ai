#!/usr/bin/env python3
"""
run_daemon.py
Continuous pipeline daemon — runs the pipeline in a loop, restarting after
each completion (approved + published) or rejection (No Go → picks next idea).

The natural pause in each cycle is the approval gate: the pipeline blocks
waiting for your Telegram Go / No Go before generating anything.

Usage: python3 scripts/run_daemon.py
"""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
PIPELINE_SCRIPT = ROOT / "scripts/run_pipeline.py"
PAUSE_AFTER_SUCCESS = 10       # seconds before starting next cycle
PAUSE_AFTER_FAILURE = 60       # seconds before retrying after error


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"[{ts}] [daemon] {msg}", flush=True)


def run_once() -> int:
    """Run one pipeline cycle. Returns the process exit code."""
    log("Starting pipeline cycle...")
    result = subprocess.run(
        [sys.executable, str(PIPELINE_SCRIPT)],
        cwd=str(ROOT),
    )
    return result.returncode


def main():
    log("Daemon started — running pipeline continuously.")
    log("Pipeline will pause at each cycle waiting for your Telegram approval.")

    while True:
        code = run_once()
        if code == 0:
            log(f"Cycle complete (success). Next cycle in {PAUSE_AFTER_SUCCESS}s.")
            time.sleep(PAUSE_AFTER_SUCCESS)
        else:
            log(f"Cycle ended with exit code {code}. Retrying in {PAUSE_AFTER_FAILURE}s.")
            time.sleep(PAUSE_AFTER_FAILURE)


if __name__ == "__main__":
    main()
