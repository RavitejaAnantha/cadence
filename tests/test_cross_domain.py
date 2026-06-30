from cadence.catalog import GENRES
from cadence.users import build_users
from experiments.cross_domain import amazon_purchase_signal, build_profiles


def test_profiles_deterministic():
    users = build_users(seed=0)
    assert build_profiles(users, seed=0) == build_profiles(users, seed=0)


def test_amazon_signal_deterministic_and_in_range():
    a = amazon_purchase_signal("u1", "b001")
    b = amazon_purchase_signal("u1", "b001")
    assert a == b and 0.0 <= a <= 1.0


def test_profile_covers_all_genres():
    users = build_users(seed=0)
    prof = build_profiles(users, seed=0)["u1"]
    assert set(prof.prime_video_genre) == set(GENRES)
    assert 0.0 <= prof.short_session_need <= 1.0
