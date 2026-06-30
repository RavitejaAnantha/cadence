"""Synthetic logged interactions with confounders baked in on purpose.

The logging policy exposes titles by POPULARITY, and click probability is discounted by
POSITION. So the logs are confounded: popular and top-placed titles get clicked more
regardless of true relevance. We also record an exposure propensity per shown title so that
off-policy estimators (IPS, doubly-robust) are possible later.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from cadence.catalog import Book
from cadence.users import Context, User, target_intensity

_SITUATIONS = ("commute", "bedtime", "road_trip", "workout", "focus")


def true_relevance(user: User, context: Context, book: Book) -> float:
    """Ground-truth utility in [0,1]. Uses ONLY genre affinity and intensity fit.

    Popularity is deliberately excluded from true relevance. It is only an exposure confounder
    in the logs. This is the crux of the offline-vs-causal discussion.
    """
    aff = user.genre_affinity.get(book.genre, 0.0)
    intensity_fit = 1.0 - abs(book.intensity - target_intensity(context))
    return max(0.0, min(1.0, 0.6 * aff + 0.4 * intensity_fit))


def relevance_map(user: User, context: Context, catalog: list[Book]) -> dict:
    return {b.book_id: true_relevance(user, context, b) for b in catalog}


def _position_discount(position: int) -> float:
    """Position bias: a title shown lower on the list gets fewer clicks."""
    return 1.0 / (1.0 + position)


@dataclass(frozen=True)
class LoggedSession:
    session_id: int
    user_id: str
    situation: str
    shown: tuple   # tuple of (book_id, position, exposure_prob)
    clicks: tuple  # tuple of clicked book_ids


def _weighted_sample_without_replacement(items, weights, k, rng):
    items = list(items)
    weights = list(weights)
    chosen = []
    for _ in range(min(k, len(items))):
        total = sum(weights)
        if total <= 0:
            break
        r = rng.uniform(0, total)
        upto = 0.0
        for idx, w in enumerate(weights):
            upto += w
            if upto >= r:
                chosen.append(items.pop(idx))
                weights.pop(idx)
                break
    return chosen


def generate_logs(users: list[User], catalog: list[Book], n_sessions: int = 400, list_len: int = 10, seed: int = 0) -> list[LoggedSession]:
    """Generate logs under a popularity-biased policy with position-biased clicks. Deterministic."""
    rng = random.Random(7000 + seed)
    sessions: list[LoggedSession] = []
    for sid in range(n_sessions):
        user = rng.choice(users)
        situation = rng.choice(_SITUATIONS)
        context = Context(situation)
        weights = [b.popularity + 0.01 for b in catalog]  # exposure proportional to popularity
        shown_books = _weighted_sample_without_replacement(catalog, weights, list_len, rng)
        shown = []
        clicks = []
        for pos, b in enumerate(shown_books):
            shown.append((b.book_id, pos, round(b.popularity + 0.01, 4)))
            p_click = true_relevance(user, context, b) * _position_discount(pos)
            if rng.random() < p_click:
                clicks.append(b.book_id)
        sessions.append(LoggedSession(sid, user.user_id, situation, tuple(shown), tuple(clicks)))
    return sessions
