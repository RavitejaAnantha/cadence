"""Baseline vs personalized experiment with bootstrap CIs, guardrails, and an honest
offline-vs-confounded comparison.

Run:
    uv run python -m experiments.run_experiment

Synthetic data only. The headline result (personalized beats baseline on NDCG vs true
relevance) is a measurement claim, not a causal one. See experiments/ATTRIBUTION.md.
"""

from __future__ import annotations

import time

from cadence.catalog import build_catalog
from cadence.provenance import run_header, write_run_header
from cadence.recommender import DEFAULT_CONFIG, recommend
from cadence.users import ACTIVITIES, Context, build_users
from experiments.bootstrap import clustered_bootstrap_ci, paired_delta_ci
from experiments.data import generate_logs, relevance_map
from experiments.metrics import catalog_coverage, intra_list_diversity, ndcg_at_k, recall_at_k

K = 5
SEED = 0


def ndcg_by_user(variant, users, catalog):
    """Per-user NDCG@K against true relevance, plus guardrail metrics for this variant."""
    by_user = {}
    recommended = set()
    diversity_lists = []
    latencies = []
    for u in users:
        vals = []
        for a in ACTIVITIES:
            ctx = Context(a)
            rel = relevance_map(u, ctx, catalog)
            t0 = time.perf_counter()
            recs = recommend(variant, u, ctx, catalog, k=K, config=DEFAULT_CONFIG)
            latencies.append((time.perf_counter() - t0) * 1000)
            ranked = [r.track.track_id for r in recs]
            vals.append(ndcg_at_k(ranked, rel, K))
            recommended.update(ranked)
            diversity_lists.append([r.track.genre for r in recs])
        by_user[u.user_id] = vals
    guardrails = {
        "coverage": catalog_coverage(recommended, len(catalog)),
        "diversity": intra_list_diversity(diversity_lists),
        "latency_ms_p50": sorted(latencies)[len(latencies) // 2],
    }
    return by_user, guardrails


def click_recall_by_user(variant, users, catalog, logs):
    """Per-user recall@K of LOGGED CLICKS. This is the confounded, production-style metric."""
    topk = {}
    for u in users:
        for a in ACTIVITIES:
            recs = recommend(variant, u, Context(a), catalog, k=K, config=DEFAULT_CONFIG)
            topk[(u.user_id, a)] = [r.track.track_id for r in recs]
    by_user = {u.user_id: [] for u in users}
    for s in logs:
        r = recall_at_k(topk[(s.user_id, s.activity)], s.clicks, K)
        if r is not None:
            by_user[s.user_id].append(r)
    return {uid: vals for uid, vals in by_user.items() if vals}


def _fmt(ci):
    point, lo, hi = ci
    return f"{point:.3f} [{lo:.3f}, {hi:.3f}]"


def main():
    catalog = build_catalog(seed=SEED)
    users = build_users(seed=SEED)
    logs = generate_logs(users, catalog, n_sessions=400, seed=SEED)

    base_ndcg, base_g = ndcg_by_user("baseline", users, catalog)
    pers_ndcg, pers_g = ndcg_by_user("personalized", users, catalog)
    base_cr = click_recall_by_user("baseline", users, catalog, logs)
    pers_cr = click_recall_by_user("personalized", users, catalog, logs)

    b_n = clustered_bootstrap_ci(base_ndcg, seed=SEED)
    p_n = clustered_bootstrap_ci(pers_ndcg, seed=SEED)
    d_n = paired_delta_ci(base_ndcg, pers_ndcg, seed=SEED)
    b_c = clustered_bootstrap_ci(base_cr, seed=SEED)
    p_c = clustered_bootstrap_ci(pers_cr, seed=SEED)

    header = run_header(seed=SEED, config=DEFAULT_CONFIG)
    repro = header["reproducible"]

    rows = [
        ("NDCG@5 vs true relevance", _fmt(b_n), _fmt(p_n), _fmt(d_n)),
        ("Recall@5 of logged clicks (confounded)", _fmt(b_c), _fmt(p_c), "see note"),
        ("Coverage (guardrail)", f"{base_g['coverage']:.3f}", f"{pers_g['coverage']:.3f}", "-"),
        ("Diversity (guardrail)", f"{base_g['diversity']:.3f}", f"{pers_g['diversity']:.3f}", "-"),
        ("Latency p50 ms (guardrail)", f"{base_g['latency_ms_p50']:.3f}", f"{pers_g['latency_ms_p50']:.3f}", "-"),
    ]

    ndcg_sep = d_n[1] > 0 or d_n[2] < 0
    verdict_lines = [
        f"NDCG@5: personalized minus baseline = {_fmt(d_n)} (paired clustered bootstrap, {len(base_ndcg)} user clusters).",
        ("  CI excludes zero: personalized improves ranking against the known utility."
         if ndcg_sep else
         "  CI includes zero: not separated. Do not claim a win."),
        f"Confounded click-recall: baseline {b_c[0]:.3f} vs personalized {p_c[0]:.3f}. "
        "The popularity baseline is flattered because logged clicks are popularity and position biased.",
        "Offline NDCG is a measurement claim, not a causal one. See experiments/ATTRIBUTION.md.",
    ]

    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()
        console.print(Panel.fit(
            f"experiment=baseline_vs_personalized  k={K}  n_log_sessions={len(logs)}\n"
            f"seed={repro['seed']}  config={repro['config_hash']}  git={repro['git_sha'][:12]}  "
            f"py={repro['versions']['python']}  numpy={repro['versions']['numpy']}",
            title="provenance", border_style="dim"))
        table = Table(show_header=True, header_style="bold")
        for col in ("metric", "baseline (95% CI)", "personalized (95% CI)", "delta (95% CI)"):
            table.add_column(col, overflow="fold")
        for r in rows:
            table.add_row(*r)
        console.print(table)
        for line in verdict_lines:
            console.print(line)
    except Exception:
        print(f"[provenance] seed={repro['seed']} config={repro['config_hash']} git={repro['git_sha'][:12]}")
        for r in rows:
            print(f"{r[0]:<42} | base {r[1]:<26} | pers {r[2]:<26} | delta {r[3]}")
        for line in verdict_lines:
            print(line)

    path = write_run_header(f"runs/experiment-{repro['config_hash']}.json", header)
    print(f"\nprovenance written: {path}")


if __name__ == "__main__":
    main()
