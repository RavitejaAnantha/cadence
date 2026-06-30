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
    usr, ctx = get_user(u, "u1"), Context("workout")
    a = recommend("personalized", usr, ctx, c, k=5)
    b = recommend("personalized", usr, ctx, c, k=5)
    assert [r.track.track_id for r in a] == [r.track.track_id for r in b]


def test_respects_k():
    c, u = _setup()
    assert len(recommend("personalized", get_user(u, "u1"), Context("focus"), c, k=3)) == 3


def test_no_duplicates():
    c, u = _setup()
    ids = [r.track.track_id for r in recommend("personalized", get_user(u, "u2"), Context("party"), c, k=10)]
    assert len(ids) == len(set(ids))


def test_sorted_descending():
    c, u = _setup()
    recs = recommend("personalized", get_user(u, "u1"), Context("workout"), c, k=8)
    scores = [r.score for r in recs]
    assert scores == sorted(scores, reverse=True)


def test_baseline_ignores_user_and_context():
    c, u = _setup()
    a = recommend("baseline", get_user(u, "u1"), Context("workout"), c, k=5)
    b = recommend("baseline", get_user(u, "u2"), Context("chill"), c, k=5)
    assert [r.track.track_id for r in a] == [r.track.track_id for r in b]


def test_unknown_variant_raises():
    c, u = _setup()
    with pytest.raises(ValueError):
        recommend("nope", get_user(u, "u1"), Context("workout"), c)
