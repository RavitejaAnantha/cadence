"""Recommenders: a popularity baseline and a personalized scorer.

The personalized score is a transparent weighted sum:
    score = w_genre * genre_affinity + w_intensity * intensity_fit
            + w_popularity * popularity + w_length * length_fit

Deterministic. Ties break by book_id so ordering is stable across machines. The model is
trivial on purpose. The workflow around it is the subject.
"""

from __future__ import annotations

from dataclasses import dataclass

from .catalog import Book
from .rationale import explain
from .users import Context, User, target_intensity, target_length


@dataclass(frozen=True)
class RecommenderConfig:
    w_genre: float = 0.50
    w_intensity: float = 0.35
    w_popularity: float = 0.15
    w_length: float = 0.0  # off by default; a length-fit term (see _length_match)


DEFAULT_CONFIG = RecommenderConfig()


@dataclass(frozen=True)
class Recommendation:
    book: Book
    score: float
    rationale: str


def _intensity_match(book: Book, context: Context) -> float:
    """1.0 when book intensity equals the context target, decaying linearly to 0.0."""
    return 1.0 - abs(book.intensity - target_intensity(context))


def _length_match(book: Book, context: Context) -> float:
    """1.0 when book length matches the situation's target length, decaying linearly to 0.0.

    A commute wants a short title, a road trip wants a long one. Length is normalized so 1.0 is
    about 30 hours.
    """
    length_norm = min(1.0, book.length_hours / 30.0)
    return 1.0 - abs(length_norm - target_length(context))


def score_book(book: Book, user: User, context: Context, config: RecommenderConfig = DEFAULT_CONFIG) -> float:
    genre = config.w_genre * user.genre_affinity.get(book.genre, 0.0)
    intensity = config.w_intensity * _intensity_match(book, context)
    pop = config.w_popularity * book.popularity
    length = config.w_length * _length_match(book, context)
    return genre + intensity + pop + length


def recommend_personalized(
    user: User, context: Context, catalog: list[Book], k: int = 5, config: RecommenderConfig = DEFAULT_CONFIG
) -> list[Recommendation]:
    scored = [(score_book(b, user, context, config), b) for b in catalog]
    scored.sort(key=lambda sb: (-sb[0], sb[1].book_id))
    return [
        Recommendation(book=b, score=round(s, 4), rationale=explain(b, user, context, config))
        for s, b in scored[:k]
    ]


def recommend_popularity(
    user: User, context: Context, catalog: list[Book], k: int = 5, config: RecommenderConfig = DEFAULT_CONFIG
) -> list[Recommendation]:
    """Baseline: ignores the user and context, ranks by global popularity."""
    ordered = sorted(catalog, key=lambda b: (-b.popularity, b.book_id))
    return [
        Recommendation(book=b, score=round(b.popularity, 4), rationale=f"popular title (popularity {b.popularity})")
        for b in ordered[:k]
    ]


def recommend_diverse(
    user: User, context: Context, catalog: list[Book], k: int = 5, config: RecommenderConfig = DEFAULT_CONFIG
) -> list[Recommendation]:
    """Personalized scores, re-ranked greedily to spread genres across the list (MMR-style).

    Each already-picked genre adds a penalty, so the list does not collapse onto one genre.
    This addresses the low intra-list diversity of the plain personalized variant.
    """
    scored = sorted(
        ((score_book(b, user, context, config), b) for b in catalog),
        key=lambda sb: (-sb[0], sb[1].book_id),
    )
    base = {b.book_id: s for s, b in scored}
    pool = [b for _, b in scored]
    chosen: list[Book] = []
    genre_counts: dict = {}
    penalty_weight = 0.5
    while pool and len(chosen) < k:
        best = None
        best_val = None
        for b in pool:
            val = base[b.book_id] - penalty_weight * genre_counts.get(b.genre, 0)
            if best_val is None or val > best_val or (val == best_val and b.book_id < best.book_id):
                best, best_val = b, val
        chosen.append(best)
        genre_counts[best.genre] = genre_counts.get(best.genre, 0) + 1
        pool.remove(best)
    return [
        Recommendation(book=b, score=round(base[b.book_id], 4), rationale=explain(b, user, context, config))
        for b in chosen
    ]


VARIANTS = {
    "personalized": recommend_personalized,
    "baseline": recommend_popularity,
    "diverse": recommend_diverse,
}


def recommend(
    variant: str, user: User, context: Context, catalog: list[Book], k: int = 5, config: RecommenderConfig = DEFAULT_CONFIG
) -> list[Recommendation]:
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; expected one of {sorted(VARIANTS)}")
    return VARIANTS[variant](user, context, catalog, k=k, config=config)
