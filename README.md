# Cadence

Cadence is a small audiobook recommender, the kind of thing Audible does, and a worked example
of how to build a data product carefully, so you can trust it and change it without breaking it.

If you have ever opened an audiobook app and seen a "for your commute" row or a "bedtime" shelf,
that is the kind of thing this does. You give it a person and the situation they are in, and it
returns a short ranked list of audiobooks, each with a one-line reason.

## The use case, in plain terms

An audiobook app has to pick a few titles for you right now. The choice depends on two things:
who you are (the genres you tend to like) and the situation you are in (a workout wants a
gripping, fast-paced listen, bedtime wants a calm one). Cadence is a tiny version of that
picker. For example:

```
uv run cadence recommend --user u1 --situation commute
```

returns five titles, best first, each with a plain reason like "fantasy is a top genre for you,
and the intensity fits a commute."

## What this repo is actually about

The title-picking logic is deliberately simple. It is not the point. The point is the
engineering workflow around a system like this, the part that is usually missing:

- Reproducibility: run it twice, on any machine, and get the same result, with a record of how
  it was produced.
- Verification: a check that the code does what we said it should, not just that it runs.
- Measurement: a way to tell whether a change actually makes the recommendations better,
  reported as an honest range instead of a single flattering number.
- Documentation that keeps itself current: the docs update automatically when the code changes,
  so they do not drift out of date.

A recommender is a good example because a change is easy to make and hard to judge. Anyone can
tweak the ranking. Knowing whether the tweak helped, and being able to prove it, is the real
work, and it is the same work for almost any data product.

## How the recommender decides (kept simple)

Every title gets a score built from three things:

1. Genre match: how much this listener tends to like this title's genre.
2. Intensity fit: how well the title's intensity (how gripping or fast paced it is) matches the
   situation. A workout wants high intensity, bedtime wants low.
3. Popularity: how popular the title is in general.

The final score is a weighted sum of those three, and titles are ranked by it. There are three
versions you can run:

- `personalized`: the scorer above (the default).
- `baseline`: ignores the person and ranks by popularity only, as a simple comparison point.
- `diverse`: the personalized list, re-ranked so it does not collapse onto a single genre.

Nothing here is trained. The weights are set by hand on purpose, so you can read the code and
predict the output. The one place anything is fit to data is the optional experiment in
`experiments/feature_selection_loop.py`.

## How we know a change is an improvement (the important part)

This is where most of the value sits. The repo includes a small experiment that asks one
question: does a new version rank titles better than the old one?

Because this is a self-contained example, it uses made-up data with a known right answer for
what each person would enjoy. It scores each ranking against that answer using NDCG, a standard
score for ranked lists where putting the best items at the top scores higher and 1.0 is a
perfect ranking. It never reports a single number. It reports a range (a 95 percent confidence
interval), so you can see how much the result could move.

It is also honest about a trap. Doing well on this offline test is not proof that the change
would help real listeners. Real usage data is biased by what people were already shown, so a
model can look good on past logs for the wrong reasons. The file `experiments/ATTRIBUTION.md`
explains this and what you would do to make a real claim, such as an A/B test. Showing that
limit plainly is part of the point.

```
uv run python -m experiments.run_experiment
```

prints the comparison, the ranges, and a few guardrail numbers, for example whether the list is
still varied or is recommending the same five titles to everyone.

## How the code keeps itself honest

- A check runs every time you commit: it runs the tests, confirms the code matches what it was
  meant to do, and blocks the commit if anything fails.
- The same checks run again on every pull request.
- After a change is merged, an automated routine reviews what changed and updates the
  documentation, so the docs stay in step with the code instead of rotting.

## Run it yourself

```
uv sync --extra dev                                     # set up the pinned environment
uv run cadence recommend --user u1 --situation commute  # see a recommendation
uv run cadence recommend --user u1 --situation bedtime   # same person, calmer titles
uv run python -m experiments.run_experiment             # measure one version against another
uv run pytest -q                                        # run the tests
bash scripts/install_hooks.sh                           # turn on the pre-commit check
```

## What is in each folder

```
cadence/        the recommender, the command-line tool, and the run record
experiments/    the measurement code, the made-up data, and ATTRIBUTION.md
tools/          the documentation generator, the intent check, and the changelog
hooks/          the pre-commit check (install with scripts/install_hooks.sh)
memory/         plain-text notes the project keeps between work sessions
docs/           a tutorial, a how-to guide, a reference, and an explanation
tests/          the tests
```

## Honest limits

The data is made up, the recommender is simple, and everything runs offline with no external
calls. The numbers describe the made-up data and show how the workflow behaves, not how any
real product would perform. More detail is in `docs/limitations.md`.
