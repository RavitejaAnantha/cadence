"""Run provenance: a header stamped onto every run so any output is traceable.

This follows a run-header discipline from prior research work: log the git SHA, seed,
config hash, and package versions for every run. Bit-reproducible fields are kept separate
from environment fields, so it is obvious what does and does not change run to run.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from dataclasses import asdict, is_dataclass
from pathlib import Path


def _git_sha(repo_root: str | None = None) -> str:
    cwd = repo_root or os.getcwd()
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, timeout=5
        )
        if head.returncode != 0 or not head.stdout.strip():
            return "no-commits-yet"
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True, timeout=5
        ).stdout.strip()
        return head.stdout.strip() + ("-dirty" if dirty else "")
    except Exception:
        return "git-unavailable"


def config_hash(config) -> str:
    """Stable 16-char sha256 over a config dict or dataclass. Key order does not matter."""
    if is_dataclass(config):
        config = asdict(config)
    blob = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def _pkg_versions() -> dict:
    versions = {"python": platform.python_version()}
    for mod in ("numpy", "rich"):
        try:
            versions[mod] = getattr(__import__(mod), "__version__", "unknown")
        except Exception:
            versions[mod] = "not-installed"
    return versions


def run_header(seed: int, config, frozen_time: str | None = None) -> dict:
    """Build a provenance header.

    frozen_time (or the CADENCE_FROZEN_TIME env var) makes the header bit-identical, which
    is how the tests assert reproducibility without depending on the wall clock.
    """
    ts = frozen_time or os.environ.get("CADENCE_FROZEN_TIME")
    if ts is None:
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()
    return {
        "tool": "cadence",
        "reproducible": {
            "seed": seed,
            "config_hash": config_hash(config),
            "git_sha": _git_sha(),
            "versions": _pkg_versions(),
        },
        "environment": {
            "utc_time": ts,
            "platform": platform.platform(),
        },
    }


def write_run_header(path: str, header: dict) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(header, indent=2, sort_keys=True))
    return str(p)
