"""Ranking metrics and guardrails. Pure functions, easy to unit-test against known cases."""

from __future__ import annotations

import math


def dcg(relevances) -> float:
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances))


def ndcg_at_k(ranked_ids, rel_map, k) -> float:
    """Normalized DCG of a ranking against a relevance map. 0.0 when no relevance exists."""
    gains = [rel_map.get(tid, 0.0) for tid in ranked_ids[:k]]
    ideal = sorted(rel_map.values(), reverse=True)[:k]
    idcg = dcg(ideal)
    return dcg(gains) / idcg if idcg > 0 else 0.0


def recall_at_k(ranked_ids, relevant_ids, k):
    """Recall@k = |top-k intersect relevant| / |relevant|. None when there are no relevant items."""
    relevant = set(relevant_ids)
    if not relevant:
        return None
    return len(set(ranked_ids[:k]) & relevant) / len(relevant)


def catalog_coverage(recommended_ids, catalog_size) -> float:
    """Guardrail: fraction of the catalog that ever gets recommended."""
    return len(set(recommended_ids)) / catalog_size if catalog_size else 0.0


def intra_list_diversity(genre_lists) -> float:
    """Guardrail: average fraction of distinct genres within each recommended list."""
    fracs = [len(set(g)) / len(g) for g in genre_lists if g]
    return sum(fracs) / len(fracs) if fracs else 0.0
