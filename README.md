# Cadence

A small, reproducible recommendation service with the engineering workflow that surrounds it:
provenance, verification, and an experiment harness with honest causal attribution. The
recommender itself is deliberately simple. The workflow is the interesting part.

## Quick start
```
uv sync --extra dev
uv run cadence recommend --user u1 --activity workout
```

## What is here
- A deterministic music recommender and a CLI. Every run prints a provenance header (seed, config hash, git SHA, package versions).
- A verification layer: unit and property tests, an intent check that asserts the code matches its stated contract, and a doc-vs-code consistency gate.
- An experiment harness that compares ranking variants with bootstrap confidence intervals and guardrail metrics, and is explicit about why an offline metric is not a causal claim (see experiments/ATTRIBUTION.md).
- A provenance loop: a generated API reference, a changelog that records intent through to commit, and a pre-commit hook that enforces the whole gate.
- Memory as plain files: episodic, semantic, and procedural (memory/).

## Usage
```
uv run cadence recommend --user u1 --activity workout      # ranked, explained recommendations
uv run cadence recommend --user u1 --activity focus --json # machine-readable output
uv run python -m experiments.run_experiment                # baseline vs personalized, with CIs
uv run python -m tools.intent_check                        # does the code do what we said
uv run pytest -q                                           # tests
bash scripts/install_hooks.sh                              # turn on the pre-commit gate
```

## Data
Cadence ships with a small synthetic catalog, a set of users, and logged interactions, all
generated from fixed seeds so everything runs offline and reproducibly. The logs carry
deliberate confounders (popularity-biased exposure, position-biased clicks) so the experiment
harness can show the gap between an offline metric and a causal claim.

## Workflow automation
- `.claude/skills/ship-a-change/`: the flow an agent follows when asked to make a change (branch, define the intent as a check, implement, verify, document, open a PR).
- `.github/workflows/ci.yml`: the correctness gate (intent check, tests) on every pull request.
- `.github/workflows/docs.yml`: after a change merges to main, a routine reviews the merged diff and updates the API reference, the affected prose docs, and the changelog. With an `ANTHROPIC_API_KEY` secret it uses Claude (the `update-docs-after-merge` skill); without one it regenerates the API reference deterministically.

## Layout
```
cadence/        recommender, CLI, provenance
experiments/    eval harness, synthetic logs with confounders, ATTRIBUTION.md
tools/          make_docs, doc_consistency, intent_check, changelog
hooks/          pre-commit gate (install via scripts/install_hooks.sh)
memory/         episodic / semantic / procedural, plain files
docs/           tutorial, how-to, reference, explanation (Diataxis) + limitations
tests/          unit and property-based tests
```

## Design notes
Cadence makes no network or model calls. It is deterministic and offline so the pipeline is
bit-reproducible and runs in CI without credentials. The conventions, architecture, and the
inner and outer loops are described in CLAUDE.md and docs/explanation-inner-outer-loop.md.
Known limitations are in docs/limitations.md.
