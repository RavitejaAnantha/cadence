"""Clustered bootstrap confidence intervals.

Two disciplines carried over from prior research work: never report a point estimate
without a CI, and resample the CLUSTER (here, the user) rather than the individual
row, because eval points from the same user are correlated. A row-level bootstrap would
report falsely tight intervals.
"""

from __future__ import annotations

import numpy as np


def clustered_bootstrap_ci(values_by_cluster, n_resamples: int = 2000, alpha: float = 0.05, seed: int = 0):
    """Return (point, lo, hi) for the grand mean, resampling clusters with replacement.

    values_by_cluster maps a cluster id to a list of per-point metric values.
    """
    rng = np.random.default_rng(seed)
    clusters = list(values_by_cluster.keys())
    cluster_vals = [np.asarray(values_by_cluster[c], dtype=float) for c in clusters]
    all_vals = np.concatenate(cluster_vals) if cluster_vals else np.array([])
    point = float(all_vals.mean()) if all_vals.size else 0.0
    if len(clusters) < 2 or all_vals.size == 0:
        return point, point, point
    n = len(clusters)
    means = np.empty(n_resamples)
    for b in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        means[b] = np.concatenate([cluster_vals[i] for i in idx]).mean()
    return point, float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def paired_delta_ci(values_a_by_cluster, values_b_by_cluster, n_resamples: int = 2000, alpha: float = 0.05, seed: int = 0):
    """Return (point, lo, hi) for mean(B) - mean(A), paired by cluster.

    The same cluster resample is applied to both arms, which is the honest way to compare
    two policies measured on the SAME eval points. A CI that excludes zero is the bar for
    claiming one beat the other.
    """
    rng = np.random.default_rng(seed)
    clusters = list(values_a_by_cluster.keys())
    a = [np.asarray(values_a_by_cluster[c], dtype=float) for c in clusters]
    b = [np.asarray(values_b_by_cluster[c], dtype=float) for c in clusters]
    point = float(np.concatenate(b).mean() - np.concatenate(a).mean())
    if len(clusters) < 2:
        return point, point, point
    n = len(clusters)
    deltas = np.empty(n_resamples)
    for j in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        deltas[j] = np.concatenate([b[i] for i in idx]).mean() - np.concatenate([a[i] for i in idx]).mean()
    return point, float(np.quantile(deltas, alpha / 2)), float(np.quantile(deltas, 1 - alpha / 2))
