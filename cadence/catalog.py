"""Synthetic audiobook catalog. Deterministic, seeded, offline. No real catalog data.

Every field is generated from a seeded RNG, so the same seed produces the same catalog on any
machine. That is what keeps the rest of the pipeline reproducible.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

GENRES = ("mystery", "scifi", "fantasy", "romance", "business", "selfhelp", "history", "biography")

# Loose genre -> baseline intensity (how gripping or fast paced a title tends to be), 0 to 1.
_GENRE_BASE_INTENSITY = {
    "mystery": 0.80,
    "scifi": 0.70,
    "fantasy": 0.65,
    "romance": 0.55,
    "business": 0.45,
    "history": 0.40,
    "biography": 0.40,
    "selfhelp": 0.35,
}

# Loose genre -> typical length in hours.
_GENRE_BASE_LENGTH = {
    "fantasy": 22,
    "history": 18,
    "scifi": 16,
    "biography": 14,
    "mystery": 11,
    "romance": 9,
    "business": 7,
    "selfhelp": 6,
}

_ADJ = ("Silent", "Hidden", "Last", "Burning", "Quiet", "Broken", "Distant", "Golden", "Hollow", "Northern")
_NOUN = ("Garden", "Empire", "Promise", "Witness", "Horizon", "Inheritance", "Tide", "Archive", "Reckoning", "Echo")
_AUTHORS = ("J. R. Calder", "Mara Esposito", "D. Whitfield", "Priya Nair", "Tom Beckett", "Lena Hart", "O. Adeyemi", "S. Kowalski", "R. Mendez", "Anya Sorin")


@dataclass(frozen=True)
class Book:
    book_id: str
    title: str
    author: str
    genre: str
    intensity: float     # 0 to 1, how gripping or fast paced
    length_hours: float
    popularity: float    # 0 to 1, a synthetic global-popularity prior
    year: int


def build_catalog(seed: int = 0, n: int = 40) -> list[Book]:
    """Return a deterministic synthetic catalog of n audiobooks.

    Same seed gives the same catalog, so any downstream metric is reproducible.
    """
    rng = random.Random(seed)
    books: list[Book] = []
    for i in range(n):
        genre = GENRES[i % len(GENRES)]
        title = f"The {rng.choice(_ADJ)} {rng.choice(_NOUN)}"
        author = rng.choice(_AUTHORS)
        intensity = min(1.0, max(0.0, _GENRE_BASE_INTENSITY[genre] + rng.uniform(-0.15, 0.15)))
        length = round(max(2.0, _GENRE_BASE_LENGTH[genre] + rng.uniform(-3, 3)), 1)
        popularity = round(rng.random(), 3)
        year = rng.randint(1995, 2025)
        books.append(
            Book(
                book_id=f"b{i:03d}",
                title=title,
                author=author,
                genre=genre,
                intensity=round(intensity, 3),
                length_hours=length,
                popularity=popularity,
                year=year,
            )
        )
    return books
