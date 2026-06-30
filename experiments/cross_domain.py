"""Synthetic cross-domain signals for a listener, layered on top of Audible history.

These stand in for other Amazon-ecosystem sources: Amazon shopping, Prime Video, and One
Medical. All synthetic. The point is to use mutual information to see which cross-domain signals
add non-overlapping information about what someone wants to listen to, and which just duplicate
the Audible history we already have. The health signal is included on purpose, to make a point
about both genuine lift and the ethics of using sensitive data.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from cadence.catalog import GENRES
from cadence.users import User


@dataclass(frozen=True)
class CrossDomainProfile:
    user_id: str
    prime_video_genre: dict    # genre -> taste 0..1, nearly equal to Audible taste (redundant by design)
    short_session_need: float  # 0..1, a One Medical signal: some listeners need shorter sessions


def build_profiles(users: list[User], seed: int = 0) -> dict:
    """Deterministic cross-domain profiles, one per listener."""
    rng = random.Random(5000 + seed)
    profiles = {}
    for u in users:
        # Prime Video genre taste closely mirrors Audible taste, so it is a near-duplicate signal.
        prime = {g: min(1.0, max(0.0, u.genre_affinity[g] + rng.uniform(-0.05, 0.05))) for g in GENRES}
        # One Medical signal, generated independently of listening taste.
        short_need = round(rng.random(), 3)
        profiles[u.user_id] = CrossDomainProfile(user_id=u.user_id, prime_video_genre=prime, short_session_need=short_need)
    return profiles


def amazon_purchase_signal(user_id: str, book_id: str) -> float:
    """A deterministic Amazon shopping signal with no real listening signal (pure noise)."""
    h = hashlib.md5(f"amz|{user_id}|{book_id}".encode()).hexdigest()[:8]
    return int(h, 16) / 0xFFFFFFFF
