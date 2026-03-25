"""
claude_cli.py — Wrapper for `claude -p` CLI calls using Claude Pro subscription.

Instead of paying per-token via the Anthropic API, expensive Sonnet calls run
through the `claude` CLI which charges the flat-rate Pro/Max subscription.

Usage:
    from lib.claude_cli import claude_call

    text, usage = claude_call(prompt)
    text, usage = claude_call(prompt, tools=["WebSearch"])
    text, usage = claude_call(prompt, model="haiku", system="You are...")
"""

import glob
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Binary discovery
# ---------------------------------------------------------------------------

def _find_claude_bin() -> str:
    """
    Locate the `claude` CLI binary.
    Checks versioned install paths first (picks latest), then falls back to PATH.
    """
    base = Path.home() / "Library" / "Application Support" / "Claude" / "claude-code"
    if base.exists():
        # Find all versioned installs, pick the most recently modified
        pattern = str(base / "*" / "claude.app" / "Contents" / "MacOS" / "claude")
        candidates = glob.glob(pattern)
        if candidates:
            # Sort by modification time descending → pick newest version
            candidates.sort(key=lambda p: Path(p).stat().st_mtime, reverse=True)
            return candidates[0]

    # Fallback: try PATH
    result = subprocess.run(["which", "claude"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    raise FileNotFoundError(
        "claude CLI not found. Install from https://claude.ai/claude-code "
        "or ensure it is in PATH."
    )


# Cache the binary path so we only discover it once per process
_CLAUDE_BIN: Optional[str] = None


def _get_bin() -> str:
    global _CLAUDE_BIN
    if _CLAUDE_BIN is None:
        _CLAUDE_BIN = _find_claude_bin()
    return _CLAUDE_BIN


# ---------------------------------------------------------------------------
# Main call
# ---------------------------------------------------------------------------

def claude_call(
    prompt: str,
    *,
    system: Optional[str] = None,
    tools: Optional[List[str]] = None,
    model: Optional[str] = None,
    timeout: int = 300,
    cwd: Optional[str] = None,
) -> Tuple[str, dict]:
    """
    Run `claude -p <prompt>` and return (result_text, usage_dict).

    Args:
        prompt:  The user prompt to send.
        system:  Optional system prompt (passed via --system-prompt).
        tools:   List of allowed tools, e.g. ["WebSearch"]. Defaults to none.
        model:   Model alias, e.g. "haiku", "sonnet". Defaults to claude default.
        timeout: Subprocess timeout in seconds (default 300 = 5 minutes).
        cwd:     Working directory for subprocess.

    Returns:
        (result_text, usage)
        - result_text: the final text response from Claude
        - usage: dict with keys like "input_tokens", "output_tokens" (may be empty)

    Raises:
        RuntimeError: if the CLI exits non-zero or output cannot be parsed.
    """
    bin_path = _get_bin()

    cmd = [
        bin_path,
        "-p", prompt,
        "--output-format", "json",
        "--setting-sources", "user",   # skip project CLAUDE.md → saves ~23k tokens
    ]

    if tools:
        cmd += ["--allowedTools", ",".join(tools)]
    else:
        cmd += ["--tools", ""]         # explicitly disable all tools

    if model:
        cmd += ["--model", model]

    if system:
        cmd += ["--system-prompt", system]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude CLI timed out after {timeout}s")

    if result.returncode != 0:
        stderr = result.stderr.strip()[:500]
        raise RuntimeError(f"claude CLI exited {result.returncode}: {stderr}")

    stdout = result.stdout.strip()
    if not stdout:
        raise RuntimeError("claude CLI returned empty output")

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"claude CLI output is not valid JSON: {e}\nRaw: {stdout[:300]}")

    text = data.get("result", "")
    usage = data.get("usage", {})

    return text, usage


# ---------------------------------------------------------------------------
# Convenience: call and return text only (drops usage)
# ---------------------------------------------------------------------------

def claude_text(prompt: str, **kwargs) -> str:
    """Like claude_call() but returns only the text string."""
    text, _ = claude_call(prompt, **kwargs)
    return text


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Discovering claude binary...")
    try:
        bin_path = _get_bin()
        print(f"Found: {bin_path}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("Running test call...")
    try:
        text, usage = claude_call(
            'Return exactly this JSON: {"ok": true}',
            model="haiku",
        )
        print(f"Result: {text}")
        print(f"Usage: {usage}")
        print("✅ claude_cli works!")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
