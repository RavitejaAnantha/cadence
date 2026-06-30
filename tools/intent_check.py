"""Intent check: does the code do what we said it should?

Each intent is a one-line contract plus an executable check. This is how we verify that
generated code matches stated intent, not just that it imports and runs. One of the intents
is statistical (personalized beats baseline with a CI that excludes zero), which is the kind
of property a unit test alone would not assert.

Run: uv run python -m tools.intent_check
"""

from __future__ import annotations

import sys
from dataclasses import replace

from cadence.catalog import build_catalog
from cadence.provenance import run_header
from cadence.recommender import DEFAULT_CONFIG, recommend
from cadence.users import Context, build_users, get_user
from experiments.bootstrap import paired_delta_ci
from experiments.data import true_relevance

K = 5


def _recs(variant, seed=0, user="u1", activity="workout", k=K):
    catalog = build_catalog(seed=seed)
    users = build_users(seed=seed)
    return recommend(variant, get_user(users, user), Context(activity), catalog, k=k)


def check_determinism():
    a = [r.track.track_id for r in _recs("personalized")]
    b = [r.track.track_id for r in _recs("personalized")]
    return a == b, f"two runs identical: {a == b}"


def check_k():
    recs = _recs("personalized", k=7)
    return len(recs) <= 7, f"returned {len(recs)} items for k=7"


def check_no_dupes():
    ids = [r.track.track_id for r in _recs("personalized", k=10)]
    return len(ids) == len(set(ids)), f"{len(ids)} items, {len(set(ids))} distinct"


def check_personalized_wins():
    from experiments.run_experiment import ndcg_by_user

    catalog = build_catalog(seed=0)
    users = build_users(seed=0)
    base, _ = ndcg_by_user("baseline", users, catalog)
    pers, _ = ndcg_by_user("personalized", users, catalog)
    point, lo, hi = paired_delta_ci(base, pers, seed=0)
    return lo > 0, f"NDCG delta {point:.3f} CI [{lo:.3f}, {hi:.3f}]"


def check_pop_not_in_truth():
    catalog = build_catalog(seed=0)
    users = build_users(seed=0)
    u, ctx, t = users[0], Context("workout"), catalog[0]
    r1 = true_relevance(u, ctx, t)
    r2 = true_relevance(u, ctx, replace(t, popularity=(t.popularity + 0.5) % 1.0))
    return abs(r1 - r2) < 1e-12, f"relevance moved {abs(r1 - r2):.2e} when popularity changed"


def check_provenance_fields():
    h = run_header(seed=0, config=DEFAULT_CONFIG, frozen_time="2026-01-01T00:00:00+00:00")
    repro = h.get("reproducible", {})
    ok = all(key in repro for key in ("seed", "git_sha", "config_hash", "versions"))
    return ok, f"reproducible keys: {sorted(repro)}"


INTENTS = [
    ("Recommendations are deterministic for a fixed seed", check_determinism),
    ("recommend() never returns more than k items", check_k),
    ("recommend() never returns duplicate tracks", check_no_dupes),
    ("Personalized beats baseline on NDCG vs true relevance, CI excludes zero", check_personalized_wins),
    ("Popularity is excluded from true relevance (confounder only)", check_pop_not_in_truth),
    ("Provenance header carries seed, git_sha, config_hash, versions", check_provenance_fields),
]


def main() -> int:
    ok_all = True
    print("intent check: does the code do what we said?\n")
    for text, fn in INTENTS:
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001 - report any failure, do not crash the gate
            ok, detail = False, f"raised {type(e).__name__}: {e}"
        ok_all = ok_all and ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {text}")
        print(f"         {detail}")
    print("\nALL INTENTS PASS" if ok_all else "\nSOME INTENTS FAILED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
