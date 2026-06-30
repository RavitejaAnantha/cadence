"""Cross-domain feature selection: which other-domain signals actually add information?

We layer signals from other Amazon-ecosystem sources on top of Audible history:
- Prime Video genre taste, which closely mirrors Audible taste, so it is likely redundant
- an Amazon shopping signal, which is unrelated, so it is likely noise
- a One Medical signal (some listeners need shorter sessions), generated independently of taste

We then define an enriched ground truth where a listener's real preference also depends on the
health signal: someone who needs shorter sessions genuinely prefers shorter titles, an axis the
base recommender ignores. mRMR then shows which cross-domain signals carry non-overlapping
information about that enriched preference, and which only duplicate Audible history or add noise.
We use the conservative mRMR variant (maximum redundancy against the kept set), because a
cross-domain signal can be a near-duplicate of a single source.

Synthetic. The health result is deliberate, to make two points at once: a cross-domain signal
can carry real, non-redundant lift, and using a medical signal for a product recommendation is
a consent and governance decision, not just a modeling one. See the note at the end of output.

Run: uv run python -m experiments.cross_domain_loop
"""

from __future__ import annotations

import numpy as np

from cadence.catalog import build_catalog
from cadence.users import SITUATIONS, Context, build_users, target_intensity
from experiments.bootstrap import clustered_bootstrap_ci, paired_delta_ci
from experiments.cross_domain import amazon_purchase_signal, build_profiles
from experiments.feature_selection_loop import mutual_info  # reuse the MI estimator
from experiments.metrics import ndcg_at_k

K = 5
MIN_GAIN = 0.04
TRAIN_SEED = 0
TEST_SEED = 1
HEALTH_WEIGHT = 0.35  # how much the health signal shifts true preference in the enriched target

NAMES = ["genre_affinity", "intensity_fit", "popularity", "prime_video_match", "amazon_signal", "medical_short_fit"]
DOMAIN = {
    "genre_affinity": "Audible",
    "intensity_fit": "Audible",
    "popularity": "Audible",
    "prime_video_match": "Prime Video",
    "amazon_signal": "Amazon shop",
    "medical_short_fit": "One Medical",
}


def _length_norm(book) -> float:
    return min(1.0, book.length_hours / 30.0)


def enriched_relevance(user, profile, ctx, book) -> float:
    """True preference = Audible taste (genre + intensity) plus a health-driven preference for
    shorter titles. The length axis is one the base recommender does not use."""
    aff = user.genre_affinity.get(book.genre, 0.0)
    intensity_fit = 1.0 - abs(book.intensity - target_intensity(ctx))
    short_fit = profile.short_session_need * (1.0 - _length_norm(book))
    return max(0.0, min(1.0, 0.5 * aff + 0.3 * intensity_fit + HEALTH_WEIGHT * short_fit))


def features(user, profile, ctx, book) -> dict:
    return {
        "genre_affinity": user.genre_affinity.get(book.genre, 0.0),
        "intensity_fit": 1.0 - abs(book.intensity - target_intensity(ctx)),
        "popularity": book.popularity,
        "prime_video_match": profile.prime_video_genre.get(book.genre, 0.0),
        "amazon_signal": amazon_purchase_signal(user.user_id, book.book_id),
        "medical_short_fit": profile.short_session_need * (1.0 - _length_norm(book)),
    }


def build_dataset(seed):
    catalog = build_catalog(seed=seed)
    users = build_users(seed=seed)
    profiles = build_profiles(users, seed=seed)
    rows, y, points = [], [], {}
    for u in users:
        prof = profiles[u.user_id]
        for s in SITUATIONS:
            ctx = Context(s)
            for b in catalog:
                f = features(u, prof, ctx, b)
                rows.append([f[n] for n in NAMES])
                y.append(enriched_relevance(u, prof, ctx, b))
                points.setdefault((u.user_id, s), []).append((b.book_id, len(rows) - 1))
    return np.asarray(rows, float), np.asarray(y, float), points


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


def main():
    Xtr, ytr, ptr = build_dataset(TRAIN_SEED)
    Xte, yte, pte = build_dataset(TEST_SEED)

    relevance = {n: mutual_info(Xtr[:, i], ytr) for i, n in enumerate(NAMES)}
    red = {}
    for i, a in enumerate(NAMES):
        for j, b in enumerate(NAMES):
            if i < j:
                red[(a, b)] = red[(b, a)] = mutual_info(Xtr[:, i], Xtr[:, j])

    print("relevance, MI(signal, enriched true preference), by source domain:")
    for n in sorted(NAMES, key=lambda k: -relevance[k]):
        print(f"  {n:20s} [{DOMAIN[n]:11s}] {relevance[n]:.4f}")

    selected, remaining = [], list(NAMES)
    print("\nmRMR loop across domains (max-redundancy variant, keep informative non-duplicates):")
    while remaining:
        def mrmr(f):
            r = max([red[(f, s)] for s in selected]) if selected else 0.0
            return relevance[f] - r
        best = max(remaining, key=mrmr)
        s = mrmr(best)
        if selected and s < MIN_GAIN:
            print(f"  stop: best remaining ({best}, {DOMAIN[best]}) adds only {s:.4f} (< {MIN_GAIN})")
            break
        selected.append(best)
        remaining.remove(best)
        print(f"  + {best:20s} [{DOMAIN[best]:11s}] mRMR={s:.4f}")

    audible_only = [n for n in selected if DOMAIN[n] == "Audible"] or ["genre_affinity"]
    cols_a, coef_a = fit(audible_only, Xtr, ytr)
    cols_s, coef_s = fit(selected, Xtr, ytr)
    a_te = ndcg_by_user(cols_a, coef_a, Xte, yte, pte)
    s_te = ndcg_by_user(cols_s, coef_s, Xte, yte, pte)
    ap, al, ah = clustered_bootstrap_ci(a_te, seed=TEST_SEED)
    sp, sl, sh = clustered_bootstrap_ci(s_te, seed=TEST_SEED)
    delta = paired_delta_ci(a_te, s_te, seed=TEST_SEED)

    kept_cross = [n for n in selected if DOMAIN[n] != "Audible"]
    dropped = [n for n in NAMES if n not in selected]
    print(f"\nkept cross-domain signals: {kept_cross or 'none'}")
    print(f"dropped (redundant or noise): {dropped}")
    print("\nheld-out NDCG@5 on a fresh seed:")
    print(f"  Audible signals only:               {ap:.4f} [{al:.4f}, {ah:.4f}]")
    print(f"  Audible plus kept cross-domain:     {sp:.4f} [{sl:.4f}, {sh:.4f}]")
    print(f"  delta (cross-domain minus Audible): {delta[0]:.4f} [{delta[1]:.4f}, {delta[2]:.4f}] "
          + ("(CI excludes zero)" if delta[1] > 0 or delta[2] < 0 else "(CI includes zero)"))
    print("\nread: Prime Video taste mirrors Audible history, so mRMR drops it as redundant. The")
    print("Amazon shopping signal is noise. The One Medical signal is on an axis the base model")
    print("ignores (title length), so it carries non-overlapping information and is kept.")
    print("\nNote: the health signal helping does not mean you should use it. Using One Medical data")
    print("for an Audible recommendation is a consent and governance decision, not a modeling one.")
    print("The loop tells you the signal exists; whether you are allowed to use it is a separate choice.")


if __name__ == "__main__":
    main()
