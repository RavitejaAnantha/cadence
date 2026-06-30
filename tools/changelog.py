"""Append a provenance entry to CHANGELOG.md: intent -> design -> tests -> docs -> commit.

This is the human-readable provenance trail. One entry per feature, written before the
commit, so the reasoning that produced a change is captured next to the change itself.
It is the local, plain-file equivalent of what a doc/release skill (GStack /document-release)
would automate against the diff.

Run:
    uv run python -m tools.changelog \
        --intent "..." --design "..." --tests "..." --docs "..."
"""

from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CHANGELOG = Path("CHANGELOG.md")


def _git_sha() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else "pending"
    except Exception:
        return "pending"


def entry(intent: str, design: str, tests: str, docs: str, when: str | None = None, sha: str | None = None) -> str:
    when = when or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sha = sha or _git_sha()
    return (
        f"## {when}  (commit {sha})\n"
        f"- intent: {intent}\n"
        f"- design: {design}\n"
        f"- tests: {tests}\n"
        f"- docs: {docs}\n\n"
    )


def append(text: str) -> None:
    header = "# Changelog\n\nProvenance trail: every feature records intent, design, tests, docs, and the commit.\n\n"
    if not CHANGELOG.exists():
        CHANGELOG.write_text(header)
    CHANGELOG.write_text(CHANGELOG.read_text() + text)


def main() -> int:
    p = argparse.ArgumentParser(description="Append a provenance changelog entry.")
    p.add_argument("--intent", required=True)
    p.add_argument("--design", required=True)
    p.add_argument("--tests", required=True)
    p.add_argument("--docs", required=True)
    p.add_argument("--when", default=None, help="override date (for reproducible runs)")
    args = p.parse_args()
    text = entry(args.intent, args.design, args.tests, args.docs, when=args.when)
    append(text)
    print(f"appended changelog entry to {CHANGELOG}")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
