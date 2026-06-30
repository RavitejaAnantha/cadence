"""Recommenders: a popularity baseline and a personalized scorer.

The personalized score is a transparent weighted sum of three terms:
    score = w_genre * genre_affinity + w_energy * energy_fit + w_popularity * popularity

Deterministic. Ties break by track_id so ordering is stable across machines.
The model is trivial on purpose. The workflow around it is the subject.
"""

from __future__ import annotations

from dataclasses import dataclass

from .catalog import Track
from .rationale import explain
from .users import Context, User, target_energy


@dataclass(frozen=True)
class RecommenderConfig:
    w_genre: float = 0.50
    w_energy: float = 0.35
    w_popularity: float = 0.15


DEFAULT_CONFIG = RecommenderConfig()


@dataclass(frozen=True)
class Recommendation:
    track: Track
    score: float
    rationale: str


def _energy_match(track: Track, context: Context) -> float:
    """1.0 when track energy equals the context target, decaying linearly to 0.0."""
    return 1.0 - abs(track.energy - target_energy(context))


def score_track(track: Track, user: User, context: Context, config: RecommenderConfig = DEFAULT_CONFIG) -> float:
    genre = config.w_genre * user.genre_affinity.get(track.genre, 0.0)
    energy = config.w_energy * _energy_match(track, context)
    pop = config.w_popularity * track.popularity
    return genre + energy + pop


def recommend_personalized(
    user: User, context: Context, catalog: list[Track], k: int = 5, config: RecommenderConfig = DEFAULT_CONFIG
) -> list[Recommendation]:
    scored = [(score_track(t, user, context, config), t) for t in catalog]
    scored.sort(key=lambda st: (-st[0], st[1].track_id))
    return [
        Recommendation(track=t, score=round(s, 4), rationale=explain(t, user, context, config))
        for s, t in scored[:k]
    ]


def recommend_popularity(
    user: User, context: Context, catalog: list[Track], k: int = 5, config: RecommenderConfig = DEFAULT_CONFIG
) -> list[Recommendation]:
    """Baseline: ignores the user and context, ranks by global popularity."""
    ordered = sorted(catalog, key=lambda t: (-t.popularity, t.track_id))
    return [
        Recommendation(track=t, score=round(t.popularity, 4), rationale=f"popular track (popularity {t.popularity})")
        for t in ordered[:k]
    ]


def recommend_diverse(
    user: User, context: Context, catalog: list[Track], k: int = 5, config: RecommenderConfig = DEFAULT_CONFIG
) -> list[Recommendation]:
    """Personalized scores, re-ranked greedily to spread genres across the list (MMR-style).

    Each already-picked genre adds a penalty, so the list does not collapse onto one genre.
    This addresses the low intra-list diversity of the plain personalized variant.
    """
    scored = sorted(
        ((score_track(t, user, context, config), t) for t in catalog),
        key=lambda st: (-st[0], st[1].track_id),
    )
    base = {t.track_id: s for s, t in scored}
    pool = [t for _, t in scored]
    chosen: list[Track] = []
    genre_counts: dict = {}
    penalty_weight = 0.5
    while pool and len(chosen) < k:
        best = None
        best_val = None
        for t in pool:
            val = base[t.track_id] - penalty_weight * genre_counts.get(t.genre, 0)
            if best_val is None or val > best_val or (val == best_val and t.track_id < best.track_id):
                best, best_val = t, val
        chosen.append(best)
        genre_counts[best.genre] = genre_counts.get(best.genre, 0) + 1
        pool.remove(best)
    return [
        Recommendation(track=t, score=round(base[t.track_id], 4), rationale=explain(t, user, context, config))
        for t in chosen
    ]


VARIANTS = {
    "personalized": recommend_personalized,
    "baseline": recommend_popularity,
    "diverse": recommend_diverse,
}


def recommend(
    variant: str, user: User, context: Context, catalog: list[Track], k: int = 5, config: RecommenderConfig = DEFAULT_CONFIG
) -> list[Recommendation]:
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; expected one of {sorted(VARIANTS)}")
    return VARIANTS[variant](user, context, catalog, k=k, config=config)
