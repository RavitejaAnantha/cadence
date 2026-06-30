"""Doc-vs-code consistency gate.

Checks that docs/reference.md documents exactly the live public API: no symbol the code
exposes is undocumented, and no documented symbol has been removed from the code. Exits 1
on drift so the pre-commit hook blocks a commit whose docs have fallen behind the code.

Run: uv run python -m tools.doc_consistency
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from tools.make_docs import public_api


def symbols_from_api() -> set:
    return {f"{module}.{name}" for module, name, *_ in public_api()}


def symbols_from_doc() -> set:
    path = Path("docs/reference.md")
    if not path.exists():
        return set()
    symbols = set()
    current = None
    for line in path.read_text().splitlines():
        header = re.match(r"## (cadence\.\w+)", line)
        if header:
            current = header.group(1)
            continue
        bullet = re.match(r"- `(\w+)", line)
        if bullet and current:
            symbols.add(f"{current}.{bullet.group(1)}")
    return symbols


def main() -> int:
    api = symbols_from_api()
    doc = symbols_from_doc()
    missing = api - doc
    extra = doc - api
    if not missing and not extra:
        print(f"doc-vs-code: OK ({len(api)} public symbols documented)")
        return 0
    if missing:
        print("MISSING from docs (code exposes, docs do not):")
        for s in sorted(missing):
            print(f"  - {s}")
    if extra:
        print("STALE in docs (docs list, code no longer exposes):")
        for s in sorted(extra):
            print(f"  - {s}")
    print("Fix: uv run python -m tools.make_docs")
    return 1


if __name__ == "__main__":
    sys.exit(main())
