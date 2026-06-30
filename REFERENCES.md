# References

The practices this repo's workflow is built on, with sources and a tag on each: (Established) for
a documented practice or peer-reviewed result, (Emerging) for recent or not-yet-standard ideas.

## 1. Agentic coding loops, inner vs outer loop
The inner loop (a tight code, test, fix cycle the agent runs autonomously) and the outer loop
(research, plan, execute, review, ship, with humans gating stages) is the durable structure.
Splitting the agent that writes code from the one that checks it is the load-bearing idea.
- Anthropic, "Claude Code: Best practices for agentic coding," 2025-04-18 (Established). https://www.anthropic.com/engineering/claude-code-best-practices
- The New Stack, "The Anthropic leader who built Claude Code now just writes loops," June 2026 (Emerging, secondary reporting). https://thenewstack.io/loop-engineering/

## 2. CLAUDE.md / steering files
A project-level context file auto-loaded into the agent, encoding conventions and constraints.
Good ones are short (Anthropic suggests roughly 200 lines or fewer) and prefer verifiable rules
tied to a real mistake over vague platitudes. The pattern was popularized by Andrej Karpathy.
- Anthropic best practices (above), which describes CLAUDE.md's role (Established).
- "Karpathy's CLAUDE.md, Annotated," mcp.directory, 2026 (Emerging, secondary). https://mcp.directory/blog/karpathy-claude-md-annotated-2026
- Note: a canonical primary URL for Karpathy's original post is hard to pin down; the attribution is consistent across secondary sources.

## 3. Hooks as deterministic enforcement
Hooks are shell commands that fire at fixed points in the tool lifecycle and run every time,
regardless of how the model is prompted. PreToolUse can block or modify a tool call, PostToolUse
runs quality gates (format, lint, validator feedback). The pre-commit gate here is the local analogue.
- Claude Code Docs, "Automate actions with hooks" (Established). https://code.claude.com/docs/en/hooks-guide

## 4. Skills as reusable primitives
A Skill is a directory with a SKILL.md plus optional scripts that packages a capability the agent
invokes when relevant. Skills are composable and portable. Introduced by Anthropic in late 2025.
- Anthropic, "Equipping agents for the real world with Agent Skills," 2025 (Established, young). https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

## 5. Agent memory: episodic, semantic, procedural
The episodic vs semantic distinction is from Tulving (1972): episodic is time and place stamped
experience, semantic is decontextualized facts. Procedural is skills and how-to knowledge. The
CoALA framework maps these onto language agents. Generative Agents stores a timestamped
observation stream and periodically distills reflections (episodic to semantic).
- Tulving, E. (1972), "Episodic and Semantic Memory," in Organization of Memory (Established).
- Sumers, Yao, Narasimhan, Griffiths, "Cognitive Architectures for Language Agents" (CoALA), arXiv:2309.02427 (Established as research). https://arxiv.org/abs/2309.02427
- Park et al., "Generative Agents," arXiv:2304.03442 (Established as research). https://arxiv.org/abs/2304.03442
- Note: MemGPT/Letta is commonly cited as arXiv:2310.08560; confirm the id before relying on it.

## 6. Diataxis documentation
Diataxis (by Daniele Procida) organizes docs by user need into four modes: tutorials (learning),
how-to (task), reference (information), explanation (understanding). The docs/ tree follows it.
- Diataxis site: https://diataxis.fr/ (Established). Author's repo: https://github.com/evildmp/diataxis-documentation-framework

## 7. Reflective / outer-loop optimization
Techniques that use past-run outcomes to improve future behavior without weight updates.
Reflexion stores verbal reflections on failures as memory. Self-Refine iterates generate,
critique, revise. DSPy compiles and optimizes prompts against a metric. The shared idea is well
studied in research but is not a settled, universal production standard for engineering agents.
- Shinn et al., "Reflexion," arXiv:2303.11366 (Established as research). https://arxiv.org/abs/2303.11366
- Madaan et al., "Self-Refine," arXiv:2303.17651 (Established as research). https://arxiv.org/abs/2303.17651
- Khattab et al., "DSPy," arXiv:2310.03714 (Established as research). https://arxiv.org/abs/2310.03714

## 8. GStack (third-party tool)
GStack is a third-party, reportedly MIT-licensed Claude Code skill pack by Garry Tan, described
by its repo as roughly 23 opinionated tools that act as a virtual engineering team. It is recent
(reported launch around March 2026) and popular, so Emerging rather than established. The local
tools here are dependency-light equivalents of a few of its commands.

| GStack command | What it does (reported) | Pillar |
|---|---|---|
| /office-hours | forcing questions to pressure-test scope before code | planning |
| /review | staff-engineer review for bugs that still pass CI | verification |
| /qa | opens a browser, tests changed routes, fixes and re-verifies | verification |
| /document-release | cross-references the diff against docs and updates them | provenance, docs |
| /document-generate | generates missing docs using Diataxis | provenance, docs |
| /retro | engineering retrospective from commit history | memory, learning |
| /learn | cross-session project memory | memory, learning |

- Repo: https://github.com/garrytan/gstack . Coverage: https://www.sitepoint.com/gstack-garry-tan-claude-code/
- Note: command details are drawn from the repo documentation and secondary coverage; treat the license and exact command names as reported, and do not confuse this with the unrelated "Gstack command-line tool" at docs.gstack.io. Productivity figures in promotional material are not independent benchmarks.
