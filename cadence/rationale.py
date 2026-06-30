"""Human-readable rationale for one recommendation.

The text mirrors the score components exactly. There is no hidden logic. If you can read the
rationale, you can predict the score, and the other way round. That is the point.
"""

from __future__ import annotations

from .catalog import Book
from .users import Context, User, target_intensity


def explain(book: Book, user: User, context: Context, config) -> str:
    tgt = target_intensity(context)
    aff = user.genre_affinity.get(book.genre, 0.0)
    intensity_fit = 1.0 - abs(book.intensity - tgt)
    parts = []
    if aff >= 0.7:
        parts.append(f"{book.genre} is a top genre for you (affinity {aff})")
    elif aff >= 0.3:
        parts.append(f"{book.genre} is a moderate match (affinity {aff})")
    else:
        parts.append(f"{book.genre} is off your usual taste (affinity {aff})")
    parts.append(f"intensity {book.intensity} vs {context.situation} target {tgt} (fit {intensity_fit:.2f})")
    parts.append(f"popularity {book.popularity}")
    return "; ".join(parts)
