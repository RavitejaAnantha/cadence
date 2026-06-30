# Session log: 2026-06-30 (length-fit experiment)

- Added a length-fit term to the scorer: a per-situation target length (commute short, road trip long) and a `w_length` config weight, defaulting to 0 so existing behavior is unchanged. Added an intent check and two tests.
- Measured it against the base ground truth (NDCG@5 vs true relevance): with `w_length=0.3`, NDCG@5 was 0.9824 [0.9769, 0.9877] versus 0.9878 [0.9809, 0.9926] without it. Delta -0.0054 [-0.0113, 0.0003], CI includes zero.
- Decision: keep `w_length=0`. Length carries no signal in the base preference model (true relevance uses only genre and intensity), so the feature does not help and slightly hurts. Shipped as a dormant, available feature.
- Lesson promoted to semantic memory: a plausible feature is not a useful feature, measure before enabling. Length only carried signal in the cross-domain loop, where a real length preference (the One Medical signal) existed.
