from cadence.catalog import build_catalog
from cadence.recommender import recommend
from cadence.users import Context, build_users, get_user

import pytest


def _setup():
    return build_catalog(seed=0), build_users(seed=0)


def test_catalog_deterministic():
    assert build_catalog(seed=0) == build_catalog(seed=0)


def test_recommend_deterministic():
    c, u = _setup()
    usr, ctx = get_user(u, "u1"), Context("commute")
    a = recommend("personalized", usr, ctx, c, k=5)
    b = recommend("personalized", usr, ctx, c, k=5)
    assert [r.book.book_id for r in a] == [r.book.book_id for r in b]


def test_respects_k():
    c, u = _setup()
    assert len(recommend("personalized", get_user(u, "u1"), Context("focus"), c, k=3)) == 3


def test_no_duplicates():
    c, u = _setup()
    ids = [r.book.book_id for r in recommend("personalized", get_user(u, "u2"), Context("road_trip"), c, k=10)]
    assert len(ids) == len(set(ids))


def test_sorted_descending():
    c, u = _setup()
    recs = recommend("personalized", get_user(u, "u1"), Context("commute"), c, k=8)
    scores = [r.score for r in recs]
    assert scores == sorted(scores, reverse=True)


def test_baseline_ignores_user_and_context():
    c, u = _setup()
    a = recommend("baseline", get_user(u, "u1"), Context("commute"), c, k=5)
    b = recommend("baseline", get_user(u, "u2"), Context("bedtime"), c, k=5)
    assert [r.book.book_id for r in a] == [r.book.book_id for r in b]


def test_unknown_variant_raises():
    c, u = _setup()
    with pytest.raises(ValueError):
        recommend("nope", get_user(u, "u1"), Context("commute"), c)


def test_diverse_spreads_genres():
    c, u = _setup()
    usr, ctx = get_user(u, "u1"), Context("commute")
    pers_genres = {r.book.genre for r in recommend("personalized", usr, ctx, c, k=5)}
    div_genres = {r.book.genre for r in recommend("diverse", usr, ctx, c, k=5)}
    assert len(div_genres) >= len(pers_genres)


def test_diverse_respects_k_and_unique():
    c, u = _setup()
    recs = recommend("diverse", get_user(u, "u1"), Context("road_trip"), c, k=6)
    ids = [r.book.book_id for r in recs]
    assert len(recs) == 6 and len(ids) == len(set(ids))


def test_length_targets_ordered():
    from cadence.users import target_length

    assert target_length(Context("commute")) < target_length(Context("road_trip"))


def test_length_match_prefers_situation_length():
    from cadence.catalog import Book
    from cadence.recommender import _length_match

    short = Book("b1", "Short", "A", "mystery", 0.5, 5.0, 0.5, 2020)
    long_title = Book("b2", "Long", "A", "mystery", 0.5, 28.0, 0.5, 2020)
    commute = Context("commute")
    assert _length_match(short, commute) > _length_match(long_title, commute)
