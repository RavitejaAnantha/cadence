---
name: ship-a-change
description: The standard flow for shipping a change to this repo. Branch, define the intent as an executable check, implement, verify, and open a PR. Use whenever asked to add a feature, fix a bug, or change behavior.
---

# Ship a change

When asked to make an update, run this flow end to end. Do not commit on a red gate.

1. Branch off main: `git checkout -b <slug>`.
2. State the intent in one line, and add it to `tools/intent_check.py` as an executable check. Define "done" before writing code.
3. Implement the smallest change that satisfies the intent.
4. Verify:
   - `uv run python -m tools.intent_check`
   - `uv run pytest -q`
5. Commit. The pre-commit hook re-runs the gate (style, intent, tests) and blocks a red commit.
6. Push the branch and open a PR. CI runs the same gate.

Documentation is not your job here. After the PR merges, the post-merge routine reviews the
change and updates the API reference, the affected prose docs, and the changelog (see
.claude/skills/update-docs-after-merge and .github/workflows/docs.yml).

Conventions: no em-dashes, deterministic, synthetic data only, a confidence interval on every
estimate. The full rules are in CLAUDE.md.
