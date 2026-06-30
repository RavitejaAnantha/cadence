# Memory

Three plain-file memory stores, readable with cat. No database, no buzzwords. The taxonomy is
the cognitive-science one (Tulving 1972) adapted to agents (CoALA, arXiv:2309.02427). See
REFERENCES.md.

- `episodic/`  : time-stamped records of what happened in a session and why.
- `semantic.md`: durable, decontextualized facts and conventions about the project.
- `procedural/`: reusable playbooks (how to add a feature, how to run an experiment).

The outer loop writes here. The inner loop and every new session read here first. This is the
plain-file version of what /learn and /retro automate in GStack (see REFERENCES.md).
