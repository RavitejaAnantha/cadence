#!/usr/bin/env bash
# Runs the read-only example commands in order.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
export PATH="$HOME/.local/bin:$PATH"
hr() { printf '\n========== %s ==========\n' "$1"; }

hr "1. recommend (personalized)"
uv run cadence recommend --user u1 --activity workout

hr "2. recommend (focus changes the ranking)"
uv run cadence recommend --user u1 --activity focus

hr "3. intent check (does the code do what we said)"
uv run python -m tools.intent_check

hr "4. doc-vs-code consistency"
uv run python -m tools.make_docs && uv run python -m tools.doc_consistency

hr "5. tests"
uv run pytest -q

hr "6. experiment harness (then read experiments/ATTRIBUTION.md)"
uv run python -m experiments.run_experiment

hr "done"
