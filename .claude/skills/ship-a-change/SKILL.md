---
name: ship-a-change
description: The standard flow for shipping a change to this repo. Always sync main first, then branch, define the intent as an executable check, implement, verify, and open a PR. Use whenever asked to add a feature, fix a bug, or change behavior.
---

# Ship a change

Run this end to end for any change. Do not commit on a red gate.

1. Sync first, every time. Before starting new work (especially right after raising a previous
   PR), get onto a clean, current, green main:
   - `git checkout main`
   - `git pull --ff-only origin main`. If it will not fast-forward, rebase or resolve the
     conflicts by hand. Never force.
   - Confirm main is green before building: `uv run python -m tools.intent_check` and `uv run pytest -q`.
   - Only start the new work once main is synced and the gate passes.
2. Branch off main: `git checkout -b <slug>`.
3. State the intent in one line, and add it to `tools/intent_check.py` as an executable check. Define "done" before writing code.
4. Implement the smallest change that satisfies the intent.
5. Verify:
   - `uv run python -m tools.intent_check`
   - `uv run pytest -q`
6. Commit. The pre-commit hook re-runs the gate (style, intent, tests) and blocks a red commit.
7. Push the branch and open a PR. CI runs the same gate.

Documentation is not your job here. After the PR merges, the post-merge routine reviews the
change and updates the API reference, the affected prose docs, and the changelog (see
.claude/skills/update-docs-after-merge and .github/workflows/docs.yml).

After the work lands, record a durable learning in memory/: a dated note in episodic, and
promote anything lasting to semantic. For experiments specifically, do not open a PR
automatically. Report the result and ask first; if the answer is yes, run this flow.

Conventions: no em-dashes, deterministic, synthetic data only, a confidence interval on every
estimate. The full rules are in CLAUDE.md.
