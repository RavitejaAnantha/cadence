"""Synthetic music catalog. Deterministic, seeded, offline. No real catalog data.

Every field is generated from a seeded RNG, so the same seed produces the same catalog
on any machine. This is what makes the rest of the pipeline bit-reproducible.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

GENRES = ("pop", "rock", "hiphop", "electronic", "jazz", "classical", "folk", "metal")

# Loose genre -> baseline energy so the examples are legible.
_GENRE_BASE_ENERGY = {
    "metal": 0.90,
    "electronic": 0.80,
    "hiphop": 0.70,
    "pop": 0.65,
    "rock": 0.60,
    "folk": 0.40,
    "jazz": 0.35,
    "classical": 0.25,
}

_ADJ = ("Neon", "Velvet", "Paper", "Golden", "Silent", "Electric", "Midnight", "Crimson", "Hollow", "Northern")
_NOUN = ("Tide", "Engine", "Garden", "Signal", "Avenue", "Ember", "Circuit", "Harbor", "Mirror", "Echo")
_ARTISTS = ("The Foxgloves", "Marble Sky", "K. Rivera", "Lownote", "Aria Vance", "Pixel Choir", "Sundial", "Cassette Kids", "Mero", "Two Rivers")


@dataclass(frozen=True)
class Track:
    track_id: str
    title: str
    artist: str
    genre: str
    energy: float       # 0..1
    tempo_bpm: int      # roughly 60..180
    popularity: float   # 0..1, a synthetic global-popularity prior
    year: int


def build_catalog(seed: int = 0, n: int = 40) -> list[Track]:
    """Return a deterministic synthetic catalog of n tracks.

    Same seed gives the same catalog, so any downstream metric is reproducible.
    """
    rng = random.Random(seed)
    tracks: list[Track] = []
    for i in range(n):
        genre = GENRES[i % len(GENRES)]
        title = f"{rng.choice(_ADJ)} {rng.choice(_NOUN)}"
        artist = rng.choice(_ARTISTS)
        base = _GENRE_BASE_ENERGY[genre]
        energy = min(1.0, max(0.0, base + rng.uniform(-0.15, 0.15)))
        tempo = int(60 + energy * 110 + rng.uniform(-10, 10))
        popularity = round(rng.random(), 3)
        year = rng.randint(1975, 2025)
        tracks.append(
            Track(
                track_id=f"t{i:03d}",
                title=title,
                artist=artist,
                genre=genre,
                energy=round(energy, 3),
                tempo_bpm=tempo,
                popularity=popularity,
                year=year,
            )
        )
    return tracks
