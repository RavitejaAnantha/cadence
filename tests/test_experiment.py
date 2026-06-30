from cadence.catalog import build_catalog
from cadence.users import build_users
from experiments.bootstrap import clustered_bootstrap_ci, paired_delta_ci
from experiments.data import generate_logs
from experiments.run_experiment import ndcg_by_user


def test_personalized_beats_baseline_ci_excludes_zero():
    c, u = build_catalog(seed=0), build_users(seed=0)
    base, _ = ndcg_by_user("baseline", u, c)
    pers, _ = ndcg_by_user("personalized", u, c)
    _, lo, _ = paired_delta_ci(base, pers, seed=0)
    assert lo > 0


def test_bootstrap_reproducible():
    c, u = build_catalog(seed=0), build_users(seed=0)
    pers, _ = ndcg_by_user("personalized", u, c)
    assert clustered_bootstrap_ci(pers, seed=0) == clustered_bootstrap_ci(pers, seed=0)


def test_logs_reproducible():
    c, u = build_catalog(seed=0), build_users(seed=0)
    assert generate_logs(u, c, n_sessions=50, seed=0) == generate_logs(u, c, n_sessions=50, seed=0)


def test_ci_brackets_point_estimate():
    c, u = build_catalog(seed=0), build_users(seed=0)
    pers, _ = ndcg_by_user("personalized", u, c)
    point, lo, hi = clustered_bootstrap_ci(pers, seed=0)
    assert lo <= point <= hi
