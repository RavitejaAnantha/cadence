"""Synthetic users and contexts. Deterministic, seeded, offline. No real user data.

A user has a genre affinity map and a baseline energy taste. A context is just an
activity, which implies a target energy. These are the only signals the recommender uses.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .catalog import GENRES

ACTIVITIES = ("workout", "focus", "chill", "party", "commute")

# Each activity implies a target energy level. This is the context signal.
ACTIVITY_TARGET_ENERGY = {
    "workout": 0.85,
    "party": 0.80,
    "commute": 0.55,
    "focus": 0.35,
    "chill": 0.25,
}


@dataclass(frozen=True)
class Context:
    activity: str

    def __post_init__(self) -> None:
        if self.activity not in ACTIVITIES:
            raise ValueError(f"unknown activity {self.activity!r}; expected one of {ACTIVITIES}")


@dataclass(frozen=True)
class User:
    user_id: str
    genre_affinity: dict  # genre -> 0..1
    energy_pref: float    # 0..1, the user's baseline energy taste


def target_energy(context: Context) -> float:
    return ACTIVITY_TARGET_ENERGY[context.activity]


def build_users(seed: int = 0, n: int = 8) -> list[User]:
    """Return n deterministic synthetic users. Each gets two high-affinity top genres."""
    rng = random.Random(1000 + seed)
    users: list[User] = []
    for i in range(n):
        affinity = {g: round(rng.uniform(0.0, 0.3), 3) for g in GENRES}
        for g in rng.sample(GENRES, 2):
            affinity[g] = round(rng.uniform(0.7, 1.0), 3)
        users.append(User(user_id=f"u{i + 1}", genre_affinity=affinity, energy_pref=round(rng.random(), 3)))
    return users


def get_user(users: list[User], user_id: str) -> User:
    for u in users:
        if u.user_id == user_id:
            return u
    raise KeyError(f"no such user {user_id!r}; have {[u.user_id for u in users]}")
