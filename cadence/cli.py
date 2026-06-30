"""Cadence CLI.

    cadence recommend --user u1 --activity workout --variant personalized

Prints the provenance header first, then a ranked, explained recommendation table.
"""

from __future__ import annotations

import argparse
import json
import sys

from .catalog import build_catalog
from .provenance import run_header
from .recommender import DEFAULT_CONFIG, VARIANTS, recommend
from .users import ACTIVITIES, Context, build_users, get_user


def _render_rich(header: dict, recs, user_id: str, activity: str, variant: str) -> bool:
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
    except Exception:
        return False
    console = Console()
    repro = header["reproducible"]
    console.print(
        Panel.fit(
            f"[bold]cadence[/bold]  variant=[cyan]{variant}[/cyan]  user=[cyan]{user_id}[/cyan]  activity=[cyan]{activity}[/cyan]\n"
            f"seed={repro['seed']}  config={repro['config_hash']}  git={repro['git_sha'][:12]}  "
            f"py={repro['versions']['python']}  numpy={repro['versions']['numpy']}",
            title="provenance",
            border_style="dim",
        )
    )
    table = Table(show_header=True, header_style="bold")
    for col in ("#", "track", "artist", "genre", "energy", "score", "why"):
        table.add_column(col, overflow="fold")
    for i, r in enumerate(recs, 1):
        table.add_row(
            str(i), r.track.title, r.track.artist, r.track.genre, f"{r.track.energy:.2f}", f"{r.score:.3f}", r.rationale
        )
    console.print(table)
    return True


def _render_plain(header: dict, recs) -> None:
    print(json.dumps(header, indent=2, sort_keys=True))
    for i, r in enumerate(recs, 1):
        print(
            f"{i:>2}. {r.track.title} ({r.track.artist}) [{r.track.genre}] "
            f"energy={r.track.energy:.2f} score={r.score:.3f} :: {r.rationale}"
        )


def cmd_recommend(args) -> int:
    catalog = build_catalog(seed=args.seed)
    users = build_users(seed=args.seed)
    user = get_user(users, args.user)
    context = Context(activity=args.activity)
    recs = recommend(args.variant, user, context, catalog, k=args.k, config=DEFAULT_CONFIG)
    header = run_header(seed=args.seed, config=DEFAULT_CONFIG)
    if args.json:
        out = {
            "header": header,
            "recommendations": [
                {
                    "rank": i + 1,
                    "track_id": r.track.track_id,
                    "title": r.track.title,
                    "score": r.score,
                    "rationale": r.rationale,
                }
                for i, r in enumerate(recs)
            ],
        }
        print(json.dumps(out, indent=2, sort_keys=True))
    elif not _render_rich(header, recs, args.user, args.activity, args.variant):
        _render_plain(header, recs)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cadence", description="Reproducible music recommender.")
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("recommend", help="rank recommendations for a user and activity")
    r.add_argument("--user", default="u1")
    r.add_argument("--activity", default="workout", choices=ACTIVITIES)
    r.add_argument("--variant", default="personalized", choices=sorted(VARIANTS))
    r.add_argument("--k", type=int, default=5)
    r.add_argument("--seed", type=int, default=0)
    r.add_argument("--json", action="store_true", help="machine-readable output")
    r.set_defaults(func=cmd_recommend)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
