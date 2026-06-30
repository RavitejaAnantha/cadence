# Playbook: add a feature

Reusable procedure. (Procedural memory: how-to knowledge.)

1. State the intent in one line. Add it to tools/intent_check.py with an executable check.
2. Implement the smallest change that satisfies the intent.
3. `uv run python -m tools.intent_check` (the new check must pass).
4. `uv run pytest -q` (add a unit or property test if the behavior is new).
5. `uv run python -m tools.make_docs` (regenerate the reference if the public API changed).
6. `uv run python -m tools.changelog --intent ... --design ... --tests ... --docs ...`
7. `git commit` (the pre-commit hook re-runs the whole gate; a red gate blocks the commit).
