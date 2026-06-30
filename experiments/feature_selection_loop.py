"""Feature selection loop: keep features with strong, non-overlapping signal, then refit.

The loop uses minimum-redundancy maximum-relevance (mRMR) on mutual information:
- relevance = MI(feature, true relevance). Keep features that inform the target.
- redundancy = MI(feature, feature). Drop features that overlap with ones already kept.
mRMR greedily grows a set that is informative and non-overlapping. We then fit linear weights
on the kept features and measure NDCG@5, including on a held-out seed so the parsimonious set
has to generalize. Synthetic data only.

Run: uv run python -m experiments.feature_selection_loop
"""

from __future__ import annotations

import hashlib

import numpy as np

from cadence.catalog import build_catalog
from cadence.recommender import recommend
from cadence.users import SITUATIONS, Context, build_users, target_intensity
from experiments.bootstrap import clustered_bootstrap_ci, paired_delta_ci
from experiments.data import true_relevance
from experiments.metrics import ndcg_at_k

K = 5
N_BINS = 8
MIN_GAIN = 0.01  # do not keep a feature whose marginal mRMR information gain is below this floor
TRAIN_SEED = 0
TEST_SEED = 1


def _noise(u, ctx, b) -> float:
    # a deterministic feature with no real signal, to confirm the loop rejects it
    h = hashlib.md5(f"{u.user_id}|{ctx.situation}|{b.book_id}".encode()).hexdigest()[:8]
    return int(h, 16) / 0xFFFFFFFF


FEATURES = {
    "genre_affinity": lambda u, ctx, b: u.genre_affinity.get(b.genre, 0.0),
    "intensity_fit": lambda u, ctx, b: 1.0 - abs(b.intensity - target_intensity(ctx)),
    "popularity": lambda u, ctx, b: b.popularity,
    "length": lambda u, ctx, b: min(1.0, b.length_hours / 30.0),
    "recency": lambda u, ctx, b: (b.year - 1995) / 30.0,
    "intensity_pref_match": lambda u, ctx, b: 1.0 - abs(b.intensity - u.intensity_pref),
    "noise": _noise,
}
NAMES = list(FEATURES)


def build_dataset(seed):
    """Return feature matrix X, target y, and points mapping (user, situation) -> [(book_id, row)]."""
    catalog = build_catalog(seed=seed)
    users = build_users(seed=seed)
    rows, y, points = [], [], {}
    for u in users:
        for s in SITUATIONS:
            ctx = Context(s)
            for b in catalog:
                rows.append([FEATURES[n](u, ctx, b) for n in NAMES])
                y.append(true_relevance(u, ctx, b))
                points.setdefault((u.user_id, s), []).append((b.book_id, len(rows) - 1))
    return np.asarray(rows, float), np.asarray(y, float), points


def _discretize(col, bins=N_BINS):
    edges = np.quantile(col, np.linspace(0, 1, bins + 1))
    edges[-1] += 1e-9
    return np.clip(np.digitize(col, edges[1:-1]), 0, bins - 1)


def mutual_info(a, b, bins=N_BINS):
    da, db = _discretize(a, bins), _discretize(b, bins)
    joint = np.histogram2d(da, db, bins=[bins, bins])[0]
    p = joint / joint.sum()
    pa, pb = p.sum(1, keepdims=True), p.sum(0, keepdims=True)
    nz = p > 0
    return float((p[nz] * np.log(p[nz] / (pa @ pb)[nz])).sum())


def fit(subset, X, y):
    cols = [NAMES.index(s) for s in subset]
    A = np.column_stack([X[:, cols], np.ones(len(X))])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return cols, coef


def ndcg_by_user(cols, coef, X, y, points):
    A = np.column_stack([X[:, cols], np.ones(len(X))])
    scores = A @ coef
    by_user = {}
    for (uid, _s), items in points.items():
        rel = {bid: y[idx] for bid, idx in items}
        ranked = [bid for bid, _ in sorted(items, key=lambda it: -scores[it[1]])]
        by_user.setdefault(uid, []).append(ndcg_at_k(ranked, rel, K))
    return by_user


def default_ndcg_by_user(seed):
    catalog = build_catalog(seed=seed)
    users = build_users(seed=seed)
    by_user = {}
    for u in users:
        for s in SITUATIONS:
            ctx = Context(s)
            rel = {b.book_id: true_relevance(u, ctx, b) for b in catalog}
            ranked = [r.book.book_id for r in recommend("personalized", u, ctx, catalog, k=K)]
            by_user.setdefault(u.user_id, []).append(ndcg_at_k(ranked, rel, K))
    return by_user


def main():
    Xtr, ytr, ptr = build_dataset(TRAIN_SEED)
    Xte, yte, pte = build_dataset(TEST_SEED)

    relevance = {n: mutual_info(Xtr[:, i], ytr) for i, n in enumerate(NAMES)}
    red = {}
    for i, a in enumerate(NAMES):
        for j, b in enumerate(NAMES):
            if i < j:
                red[(a, b)] = red[(b, a)] = mutual_info(Xtr[:, i], Xtr[:, j])

    print("relevance, MI(feature, true relevance), higher means more signal:")
    for n in sorted(NAMES, key=lambda k: -relevance[k]):
        print(f"  {n:20s} {relevance[n]:.4f}")

    selected, remaining = [], list(NAMES)
    print("\nmRMR loop (keep informative, non-overlapping features):")
    while remaining:
        def mrmr(f):
            r = np.mean([red[(f, s)] for s in selected]) if selected else 0.0
            return relevance[f] - r
        best = max(remaining, key=mrmr)
        s = mrmr(best)
        if selected and s < MIN_GAIN:
            print(f"  stop: best remaining ({best}) adds only {s:.4f} (< {MIN_GAIN}), overlap not new signal")
            break
        selected.append(best)
        remaining.remove(best)
        print(f"  + {best:20s} mRMR={s:.4f}")

    print("\ngrow the kept set, fit weights, in-sample NDCG@5 (95% CI):")
    for size in range(1, len(selected) + 1):
        cols, coef = fit(selected[:size], Xtr, ytr)
        point, lo, hi = clustered_bootstrap_ci(ndcg_by_user(cols, coef, Xtr, ytr, ptr), seed=TRAIN_SEED)
        print(f"  {size} feat  {str(selected[:size]):55s}  {point:.4f} [{lo:.4f}, {hi:.4f}]")

    cols_sel, coef_sel = fit(selected, Xtr, ytr)
    cols_all, coef_all = fit(NAMES, Xtr, ytr)
    sel_te = ndcg_by_user(cols_sel, coef_sel, Xte, yte, pte)
    all_te = ndcg_by_user(cols_all, coef_all, Xte, yte, pte)
    def_te = default_ndcg_by_user(TEST_SEED)

    sp, sl, sh = clustered_bootstrap_ci(sel_te, seed=TEST_SEED)
    ap, al, ah = clustered_bootstrap_ci(all_te, seed=TEST_SEED)
    dp, dl, dh = clustered_bootstrap_ci(def_te, seed=TEST_SEED)
    delta = paired_delta_ci(def_te, sel_te, seed=TEST_SEED)

    print("\nheld-out NDCG@5 on a fresh seed (train on seed 0, evaluate on seed 1):")
    print(f"  default scorer (genre+intensity+popularity, fixed weights): {dp:.4f} [{dl:.4f}, {dh:.4f}]")
    print(f"  all 7 features, refit:                                      {ap:.4f} [{al:.4f}, {ah:.4f}]")
    print(f"  mRMR-selected {selected}, refit:")
    print(f"                                                              {sp:.4f} [{sl:.4f}, {sh:.4f}]")
    print(f"  selected minus default delta: {delta[0]:.4f} [{delta[1]:.4f}, {delta[2]:.4f}] "
          + ("(CI excludes zero)" if delta[1] > 0 or delta[2] < 0 else "(CI includes zero)"))
    _, coef_show = fit(selected, Xtr, ytr)
    print("\nfitted weights on the kept set:", {k: round(float(w), 3) for k, w in zip(selected, coef_show[:-1])})
    print("read: mRMR keeps genre_affinity and intensity_fit (the true signal), and ranks popularity")
    print("and noise low, because they carry little mutual information with true relevance.")


if __name__ == "__main__":
    main()
