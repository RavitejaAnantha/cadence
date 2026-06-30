# Adoption: rolling this workflow out to a team, and measuring whether it helped

Cadence is as much a workflow as it is a recommender. This note is about getting that workflow
adopted by a team, and measuring the impact honestly.

## The core lever: make the right way the enforced way
The mistake is to introduce a workflow as a document people are asked to follow. Documents decay.
The lever that works is to encode the workflow into the repo so adoption is the default:
- A short CLAUDE.md that travels with the clone (conventions, architecture, commands).
- A pre-commit gate wired through `git config core.hooksPath hooks`, so the gate is shared, not re-created in each developer's private `.git/hooks`. Clone, run `scripts/install_hooks.sh` once, and the gate is on for everyone.
- Reusable playbooks and memory as plain files in the repo, so a new engineer (or a new agent session) reads the same context everyone else does.

The same idea scales to larger systems: version-controlled skills and hooks that are load-bearing
enforcement (a hook that blocks direct commits to a protected branch, a check that refuses
em-dashes), plus server-side branch protection. The workflow is enforced by the tooling, so it
does not quietly erode.

## A rollout sequence that works
1. Pick one painful, high-frequency task, not the whole workflow. Docs drifting from code is a good first target: the pain is constant and the fix (a doc-vs-code gate) is cheap.
2. Ship the tool for that one task and show the time it saves on real work.
3. Let it spread by pull, not mandate. People adopt a gate that catches their own mistakes.
4. Only then add the next piece (intent checks, the experiment harness, memory).

## What tends to succeed
- Deterministic gates people trust (tests, doc-vs-code consistency). Trust comes from the gate being right every time, which is why the verifiers are deterministic and not a model judge.
- Plain-file memory and playbooks people can read and edit, not a black box.
- Opt-in first, default-on once it has earned trust.

## What resists
- Skepticism about generated code. Mitigation: the verifier is the product. Nothing merges that the tests, intent checks, and review do not pass. The pitch is not "trust the model", it is "trust the gate".
- Review burden. More generated code means more to review. Mitigation: keep humans on judgment, push mechanical checks into hooks, and treat a large unreviewable diff as a process smell.
- Cost anxiety. Mitigation: show cost telemetry, explore with a cheap model and judge with an expensive one, and put a budget on loops.
- The plausible-but-wrong failure mode. A model can produce confident, incorrect work. Mitigation: verifiers the model does not control (pytest, a doc-vs-code diff, a held-out metric), and a human gate on anything irreversible.

## Measuring adoption impact as an experiment
Adoption is itself a measurement problem, and it deserves the same rigor as the recommender
experiment in this repo.

Metrics:
- Primary: cycle time (PR opened to merged), PR throughput per engineer-week, defect or rework rate (reverts and follow-up fix commits per merged PR), doc coverage (the doc-vs-code gate pass rate).
- Adoption rate: the fraction of PRs that actually ran the workflow.
- Guardrails: defect rate must not rise, review load must not explode, on-call pages must not increase. A throughput win that raises defects is not a win.

Design, and why the naive version is wrong:
- You cannot cleanly randomize engineers to "tool" vs "no tool". It is hard to enforce, and the two groups contaminate each other.
- A naive pre-versus-post comparison is confounded. Prefer a staggered rollout across teams that adopt at different times, analyzed as a difference-in-differences, or at least a pre/post with a comparison group that has not adopted yet.
- Report effect sizes with confidence intervals, not a single percentage.

Confounders to name out loud:
- Ticket difficulty. Hard tickets take longer regardless, and the mix shifts over time.
- Engineer experience and seniority.
- Selection bias. Eager early adopters are often already the faster engineers.
- Hawthorne effect. People who know they are measured change behavior.
- Secular trends. The codebase matures and CI gets faster on its own.

## The stance
Most published productivity numbers for engineering tooling are confounded and over-claimed. The
credible move is to measure adoption like an experiment, name the confounders, prefer staggered
difference-in-differences over pre/post, guard against defect and review-load regressions, and
report effects with confidence intervals. The same rigor the recommender harness applies to a
ranking change is the rigor an adoption claim deserves.
