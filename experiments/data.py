"""Synthetic logged interactions with confounders baked in on purpose.

The logging policy exposes tracks by POPULARITY, and click probability is discounted by
POSITION. So the logs are confounded: popular and top-placed tracks get clicked more
regardless of true relevance. This is what makes ATTRIBUTION.md concrete instead of
hand-waved. We also record an exposure propensity per shown track so that off-policy
estimators (IPS, doubly-robust) are possible later.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from cadence.catalog import Track
from cadence.users import Context, User, target_energy

_ACTIVITIES = ("workout", "focus", "chill", "party", "commute")


def true_relevance(user: User, context: Context, track: Track) -> float:
    """Ground-truth utility in [0,1]. Uses ONLY genre affinity and energy fit.

    Popularity is deliberately excluded from true relevance. It is only an exposure
    confounder in the logs. This is the crux of the offline-vs-causal discussion.
    """
    aff = user.genre_affinity.get(track.genre, 0.0)
    energy_fit = 1.0 - abs(track.energy - target_energy(context))
    return max(0.0, min(1.0, 0.6 * aff + 0.4 * energy_fit))


def relevance_map(user: User, context: Context, catalog: list[Track]) -> dict:
    return {t.track_id: true_relevance(user, context, t) for t in catalog}


def _position_discount(position: int) -> float:
    """Position bias: a track shown lower on the list gets fewer clicks."""
    return 1.0 / (1.0 + position)


@dataclass(frozen=True)
class LoggedSession:
    session_id: int
    user_id: str
    activity: str
    shown: tuple   # tuple of (track_id, position, exposure_prob)
    clicks: tuple  # tuple of clicked track_ids


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


def generate_logs(users: list[User], catalog: list[Track], n_sessions: int = 400, list_len: int = 10, seed: int = 0) -> list[LoggedSession]:
    """Generate logs under a popularity-biased policy with position-biased clicks. Deterministic."""
    rng = random.Random(7000 + seed)
    sessions: list[LoggedSession] = []
    for sid in range(n_sessions):
        user = rng.choice(users)
        activity = rng.choice(_ACTIVITIES)
        context = Context(activity)
        weights = [t.popularity + 0.01 for t in catalog]  # exposure proportional to popularity
        shown_tracks = _weighted_sample_without_replacement(catalog, weights, list_len, rng)
        shown = []
        clicks = []
        for pos, t in enumerate(shown_tracks):
            shown.append((t.track_id, pos, round(t.popularity + 0.01, 4)))
            p_click = true_relevance(user, context, t) * _position_discount(pos)
            if rng.random() < p_click:
                clicks.append(t.track_id)
        sessions.append(LoggedSession(sid, user.user_id, activity, tuple(shown), tuple(clicks)))
    return sessions
