"""Property-based checks (hypothesis) of the recommender contract over many inputs."""

from hypothesis import given, settings
from hypothesis import strategies as st

from cadence.catalog import build_catalog
from cadence.recommender import recommend
from cadence.users import SITUATIONS, Context, build_users, get_user

CATALOG = build_catalog(seed=0)
USERS = build_users(seed=0)
USER_IDS = [u.user_id for u in USERS]


@settings(max_examples=50, deadline=None)
@given(
    uid=st.sampled_from(USER_IDS),
    situation=st.sampled_from(SITUATIONS),
    k=st.integers(min_value=1, max_value=15),
)
def test_property_returns_k_unique(uid, situation, k):
    recs = recommend("personalized", get_user(USERS, uid), Context(situation), CATALOG, k=k)
    ids = [r.book.book_id for r in recs]
    assert len(recs) == min(k, len(CATALOG))
    assert len(ids) == len(set(ids))


@settings(max_examples=50, deadline=None)
@given(uid=st.sampled_from(USER_IDS), situation=st.sampled_from(SITUATIONS))
def test_property_scores_non_increasing(uid, situation):
    recs = recommend("personalized", get_user(USERS, uid), Context(situation), CATALOG, k=10)
    scores = [r.score for r in recs]
    assert scores == sorted(scores, reverse=True)
