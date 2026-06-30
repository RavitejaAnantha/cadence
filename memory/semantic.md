# Semantic memory: durable facts and conventions

Decontextualized knowledge about Cadence that holds across sessions. (Tulving: semantic memory.)

- The recommender is trivial on purpose. The repo's value is the workflow around it.
- `true_relevance` uses genre affinity and energy fit only. Popularity is a confounder, never a relevance signal.
- The pipeline is bit-reproducible: every synthetic generator is seeded, and provenance records seed, git SHA, config hash, and versions.
- Offline NDCG is a measurement claim, not a causal one. A causal claim needs an A/B test, or an off-policy estimator using the recorded propensities. See experiments/ATTRIBUTION.md.
- Confidence intervals are mandatory and clustered by user, because eval points from one user are correlated.
- Verification is enforced by the pre-commit hook, not left to discipline.
- Conventions: no em-dashes, no AI-isms, synthetic data only.
- This repo makes no model calls. It is offline and deterministic by design.
