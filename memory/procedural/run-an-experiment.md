# Playbook: run an experiment

Reusable procedure. (Procedural memory: how-to knowledge.)

1. Decide the question: does variant B beat variant A on a target metric, measured on the same eval points?
2. `uv run python -m experiments.run_experiment` (baseline vs personalized, NDCG@5 vs true relevance).
3. Read the delta CI. If it includes zero, do not claim a win.
4. Check the guardrails (coverage, diversity, latency). A metric win with a guardrail regression is not a clean win.
5. Remember this is offline. Before claiming online impact, read experiments/ATTRIBUTION.md and pick a causal design (A/B, IPS, interleaving).
6. The run writes a provenance header to runs/. Keep it with any result you report.
