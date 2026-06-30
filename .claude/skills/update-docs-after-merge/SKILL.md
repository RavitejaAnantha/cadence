---
name: update-docs-after-merge
description: Post-merge documentation routine. Review the change that just landed on main, update the API reference and any affected prose docs and the changelog, then commit and push. Run by the docs GitHub Actions workflow.
---

# Update docs after merge

You are running in CI right after a change merged to main. Update the documentation to match
what changed, then commit and push. Change documentation only, never code or tests.

1. Regenerate the API reference: `uv run python -m tools.make_docs`.
2. Read what just merged: `git show --stat HEAD` and `git diff HEAD~1 HEAD`.
3. If public behavior changed (a new variant, a CLI flag, a metric), update the affected prose:
   README.md (usage), the relevant file under docs/, and add a CHANGELOG.md entry with intent,
   design, tests, and docs lines.
4. Keep the house style: no em-dashes, no filler words, synthetic data only, plain voice.
5. Verify the reference matches the code: `uv run python -m tools.doc_consistency`.
6. Commit and push with a skip-ci marker so this routine does not retrigger:
   `git commit -am "docs: update after merge [skip ci]"` then `git push`.
