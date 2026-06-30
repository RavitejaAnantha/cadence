"""Human-readable rationale for one recommendation.

The text mirrors the score components exactly. There is no hidden logic. If you can read
the rationale, you can predict the score, and vice versa. That is the point.
"""

from __future__ import annotations

from .catalog import Track
from .users import Context, User, target_energy


def explain(track: Track, user: User, context: Context, config) -> str:
    tgt = target_energy(context)
    aff = user.genre_affinity.get(track.genre, 0.0)
    energy_fit = 1.0 - abs(track.energy - tgt)
    parts = []
    if aff >= 0.7:
        parts.append(f"{track.genre} is a top genre for you (affinity {aff})")
    elif aff >= 0.3:
        parts.append(f"{track.genre} is a moderate match (affinity {aff})")
    else:
        parts.append(f"{track.genre} is off your usual taste (affinity {aff})")
    parts.append(f"energy {track.energy} vs {context.activity} target {tgt} (fit {energy_fit:.2f})")
    parts.append(f"popularity {track.popularity}")
    return "; ".join(parts)
