# Explanation: the inner loop and the outer loop

Diataxis quadrant: explanation (understanding-oriented).

## Inner loop (within a task)
The agent executes one feature: reason about the change, edit code, run the verifiers (tests,
intent check, doc consistency), read the result, fix, and repeat until the verifiers pass. The
verifiers are the stop condition. This is the tight code-test-fix cycle that loop engineering
refers to (Anthropic's Claude Code best practices, and Boris Cherny's "I write loops" framing).
In Cadence the inner loop is concrete: the pre-commit gate is the verifier, and a red gate
blocks the commit.

## Outer loop (across tasks)
After a feature ships, the agent reflects: what was learned, what should change next time. That
learning is written to memory/ (a durable lesson to semantic.md, a refined step in a procedural
playbook). The next session reads memory/ first, so the system improves its own prompts and
playbooks over time without any weight update. The research idea behind this is reflective
optimization (Reflexion, arXiv:2303.11366; Self-Refine, arXiv:2303.17651; and, for programmatic
prompt optimization, DSPy, arXiv:2310.03714).

Honest caveat: reflective outer loops are an established research idea, not a settled,
universally deployed production standard. Cadence implements the simplest honest version: plain
memory files a human can read and a future agent reads first.

## Why separate them
The inner loop optimizes for getting one task correct, fast, with a verifier. The outer loop
optimizes the process itself. Conflating them is how you get an agent that solves today's task
and forgets the lesson tomorrow. Keeping memory in plain files, not buried inside a model, is
what makes the outer loop inspectable and reviewable.

## Where this scales
In a larger system the same shape runs for real: an episodic-to-semantic dual memory feeds a
co-scientist loop, and a multiple-testing-corrected promotion gate decides what is allowed to
graduate. Cadence is the legible, offline version of that idea.
