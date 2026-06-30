# CLAUDE.md - Cadence

Steering file for agents and humans working in this repo. Read first. Kept short on purpose.

## What this is
Cadence is a small, reproducible recommendation service. The recommender is deliberately simple.
The work that matters is the engineering workflow around it: provenance, verification, and an
experiment harness with honest causal attribution.

## Conventions (hard)
1. No em-dashes anywhere, code or prose. Use commas, periods, parentheses. The pre-commit hook enforces this.
2. Avoid filler words like "leverage", "robust", "ensure", "comprehensive". Write plainly.
3. Deterministic where possible. Seed every synthetic generator. The pipeline makes no network or model calls and is bit-reproducible. Keep it that way.
4. Never report a point estimate without a confidence interval. Use the clustered bootstrap in experiments/bootstrap.py.
5. Verify before commit. The pre-commit hook runs the em-dash check, the intent check, and the tests. Do not bypass it.
6. Docs are reconciled by the post-merge routine, not by the author. Do not hand-edit docs/reference.md; the routine regenerates it and updates the prose docs after merge.
7. Synthetic sample data only. The catalog, users, and logs are generated from seeds. Do not commit real catalog or user data.

## Architecture
- `cadence/`: the recommender (catalog, users, recommender, rationale), the CLI, and provenance.
- `experiments/`: the eval harness (data with baked-in confounders, metrics, bootstrap, run_experiment) and ATTRIBUTION.md.
- `tools/`: make_docs (reference generation), doc_consistency (doc-vs-code gate), intent_check (code matches intent), changelog (provenance trail).
- `hooks/pre-commit`: the enforcement gate, installed via scripts/install_hooks.sh (git core.hooksPath).
- `memory/`: episodic (per-session decisions), semantic (durable facts), procedural (playbooks).
- `docs/`: tutorial, how-to, reference, and explanation (Diataxis).
- `.claude/skills/`: the ship-a-change flow an agent follows for any update.
- `.github/workflows/`: a correctness gate on pull requests, and a post-merge routine that reviews the merged change and updates the docs.

## Loops
- Inner loop: build a feature, run it, verify (tests + intent check), fix, repeat. The verifiers are the stop condition.
- Outer loop: after shipping, write a durable lesson to memory/ and refine a playbook. The next session reads memory/ first. See docs/explanation-inner-outer-loop.md.

## Memory
Three plain-file stores you can read with cat:
- `memory/episodic/<date>-session.md`: what happened in a session and why.
- `memory/semantic.md`: durable facts and conventions.
- `memory/procedural/*.md`: reusable playbooks.
The taxonomy follows Tulving (episodic vs semantic) and CoALA's mapping onto agents. See REFERENCES.md.

## No model or network calls
Cadence is deterministic and offline by design, so the pipeline is bit-reproducible and runs in
CI without credentials. Do not add a network or model dependency without a strong reason; it
breaks reproducibility and offline use.

## The flow (after each change)
1. Branch. 2. Add the intent check. 3. Implement. 4. `uv run python -m tools.intent_check`. 5. `uv run pytest`.
6. Commit (the hook re-runs the gate). 7. Push and open a PR. Docs are updated after merge by the routine.

## Commands
```
uv sync --extra dev
uv run cadence recommend --user u1 --activity workout
uv run python -m experiments.run_experiment
uv run python -m tools.intent_check
uv run pytest -q
bash scripts/install_hooks.sh
```
