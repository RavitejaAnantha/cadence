# Tutorial: your first recommendation

Diataxis quadrant: tutorial (learning-oriented). Goal: from clone to first output in under three minutes.

1. Install the pinned environment:
   ```
   uv sync --extra dev
   ```
2. Ask for a recommendation:
   ```
   uv run cadence recommend --user u1 --situation commute
   ```
   You see a provenance header (seed, config hash, git SHA, versions) and a ranked table of
   five audiobooks, each with a one-line reason that mirrors its score.
3. Change the situation and watch the ranking move:
   ```
   uv run cadence recommend --user u1 --situation bedtime
   ```
   Calmer, lower-intensity titles rise, because the bedtime situation has a lower target intensity.
4. See the machine-readable form:
   ```
   uv run cadence recommend --user u1 --situation commute --json
   ```

That is the whole recommender. The rest of the repo is the workflow around it: verification,
provenance, and the experiment harness.
