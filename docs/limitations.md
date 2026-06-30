# Limitations

## Cost
Cadence makes no model calls, so it costs nothing to run. That is a deliberate choice for a
reproducible offline pipeline, and also a limit: it does not exercise the cost surface of a real
agent loop. The cost discipline that applies at scale is to explore with a cheap model and judge
with an expensive one, put a budget on every loop, and show per-call cost telemetry. Confirm the
current price ratio before quoting it; as of 2026 the Opus-to-Haiku ratio is closer to 5x than
the older 15x.

## Latency
Offline and deterministic, so latency here is microseconds. Real agent loops are dominated by
model latency and tool round-trips. The mitigation is the same as for cost: keep the expensive
model off the hot path, parallelize independent calls, and cache.

## Verification has limits
A verifier can only check what you can express. Tests and the intent check catch contract
violations and regressions. They do not catch a wrong objective. If `true_relevance` encodes the
wrong utility, every check still passes and the system is confidently wrong. This is why the
objective and the eval get more scrutiny than the model.

## Offline eval is not causal proof
The headline NDCG result is a measurement on synthetic data. It is not evidence of online impact.
See experiments/ATTRIBUTION.md for the confounders (exposure bias, position bias, feedback loops)
and the designs that would earn a causal claim (A/B, IPS, interleaving).

## Reproducibility has a boundary
This pipeline is bit-reproducible because it makes no model calls. Model-in-the-loop systems are
not bit-reproducible even at temperature 0, because sampling is not seedable through the API. The
honest move there is to pin what you can (model id, temperature, prompt version, data snapshot)
and report a variance band over repeated runs for what you cannot.

## When not to use an agent
- When the task is irreversible and unverifiable (no cheap check exists). Keep a human in the loop.
- When a deterministic tool already solves it (a formatter, a linter, a SQL query). Use the tool.
- When the cost of a wrong-but-plausible answer is high and you cannot gate it.
- When the real work is deciding what to build, not building it.

## This repo's scope
The catalog, users, and logs are synthetic. The recommender is simple. The numbers describe
synthetic data and illustrate the workflow, not a real product.
