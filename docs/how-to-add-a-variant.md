# How-to: add a recommender variant

Diataxis quadrant: how-to (task-oriented). Goal: add a third ranking strategy and measure it honestly.

1. Write the function in `cadence/recommender.py`, with the same signature as `recommend_personalized`:
   ```
   def recommend_myvariant(user, context, catalog, k=5, config=DEFAULT_CONFIG): ...
   ```
2. Register it:
   ```
   VARIANTS["myvariant"] = recommend_myvariant
   ```
3. Regenerate the reference and check consistency:
   ```
   uv run python -m tools.make_docs
   uv run python -m tools.doc_consistency
   ```
4. Measure it against the baseline. Add it to `experiments/run_experiment.py`, or call
   `ndcg_by_user("myvariant", ...)` directly. Read the delta CI before claiming anything.
5. Add a unit test in `tests/`, and an intent in `tools/intent_check.py` if it has a new contract.
6. Commit. The pre-commit gate runs the whole verification suite.
