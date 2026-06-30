# Tutorial: your first recommendation

Diataxis quadrant: tutorial (learning-oriented). Goal: from clone to first output in under three minutes.

1. Install the pinned environment:
   ```
   uv sync --extra dev
   ```
2. Ask for a recommendation:
   ```
   uv run cadence recommend --user u1 --activity workout
   ```
   You see a provenance header (seed, config hash, git SHA, versions) and a ranked table of
   five tracks, each with a one-line rationale that mirrors its score.
3. Change the context and watch the ranking move:
   ```
   uv run cadence recommend --user u1 --activity focus
   ```
   Lower-energy tracks rise, because the focus activity has a lower target energy.
4. See the machine-readable form:
   ```
   uv run cadence recommend --user u1 --activity workout --json
   ```

That is the whole recommender. The rest of the repo is the workflow around it: verification,
provenance, and the experiment harness.
