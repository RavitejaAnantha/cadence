#!/usr/bin/env bash
# Point git at the repo's hooks directory, so the gate travels with the repo instead of
# living in each developer's private .git/hooks. This is how a team adopts the workflow by
# default: clone, run this once, and the gate is on for everyone.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath hooks
chmod +x hooks/pre-commit
echo "installed: core.hooksPath -> hooks/  (pre-commit gate active)"
