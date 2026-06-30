"""Synthetic listeners and contexts. Deterministic, seeded, offline. No real user data.

A listener has a genre affinity map and a baseline intensity taste. A context is the listening
situation, which implies a target intensity and a target title length.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .catalog import GENRES

SITUATIONS = ("commute", "bedtime", "road_trip", "workout", "focus")

# Each situation implies a target intensity (how gripping the listener wants the title to be).
SITUATION_TARGET_INTENSITY = {
    "workout": 0.85,
    "road_trip": 0.70,
    "commute": 0.60,
    "focus": 0.45,
    "bedtime": 0.20,
}

# Each situation also implies a target title length, normalized 0..1 where 1.0 is about 30 hours.
# A commute wants something short, a road trip wants something long.
SITUATION_TARGET_LENGTH = {
    "commute": 0.20,
    "bedtime": 0.35,
    "workout": 0.40,
    "focus": 0.45,
    "road_trip": 0.85,
}


@dataclass(frozen=True)
class Context:
    situation: str

    def __post_init__(self) -> None:
        if self.situation not in SITUATIONS:
            raise ValueError(f"unknown situation {self.situation!r}; expected one of {SITUATIONS}")


@dataclass(frozen=True)
class User:
    user_id: str
    genre_affinity: dict   # genre -> 0 to 1
    intensity_pref: float  # 0 to 1, the listener's baseline intensity taste


def target_intensity(context: Context) -> float:
    return SITUATION_TARGET_INTENSITY[context.situation]


def target_length(context: Context) -> float:
    return SITUATION_TARGET_LENGTH[context.situation]


def build_users(seed: int = 0, n: int = 8) -> list[User]:
    """Return n deterministic synthetic listeners. Each gets two high-affinity top genres."""
    rng = random.Random(1000 + seed)
    users: list[User] = []
    for i in range(n):
        affinity = {g: round(rng.uniform(0.0, 0.3), 3) for g in GENRES}
        for g in rng.sample(GENRES, 2):
            affinity[g] = round(rng.uniform(0.7, 1.0), 3)
        users.append(User(user_id=f"u{i + 1}", genre_affinity=affinity, intensity_pref=round(rng.random(), 3)))
    return users


def get_user(users: list[User], user_id: str) -> User:
    for u in users:
        if u.user_id == user_id:
            return u
    raise KeyError(f"no such user {user_id!r}; have {[u.user_id for u in users]}")
