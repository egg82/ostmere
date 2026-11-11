"""A played route read as visits for the counters (counters.py): each visit's return (the save the player came back to,
the previous exit run on with nobody deciding), and each decision after the opening's end with the saves around it."""
from dataclasses import replace

from ashfall_app.engine import Rules, Save, advance
from tests.daythree.counters import Step, Visit
from tests.dayone.player import DayOnePlayer, VisitRecord


def steps_of(p: DayOnePlayer) -> list[Step]:
    """Every decision after the opening's end moment, with the save just before it (the one it was made on)."""
    assert p.end_save is not None
    return [Step(at, verb, p.undecided[i], p.decided[i])
            for i, (at, _, verb) in enumerate(p.decisions) if i >= p.opening_decisions]


def visits_of(p: DayOnePlayer, rules: Rules | None = None) -> list[Visit]:
    assert p.end_save is not None
    rules = rules or p.rules
    steps, out, prior = steps_of(p), list[Visit](), p.end_save
    for v in p.visits:
        inside = tuple(s for s in steps if v.start <= s.at <= v.end)
        out.append(Visit(f"V{v.index}", v.gap, _returned(p, rules, prior, v), inside))
        assert v.exit is not None
        prior = v.exit
    return with_returns(out)


def _returned(p: DayOnePlayer, rules: Rules, prior: Save, v: VisitRecord) -> Save:
    """`prior` run on to the visit's start: the save the play began the visit on when it is at that time on the play's
    own rules (invariant 1), else the advance."""
    if rules is p.rules and v.came is not None and v.came.time == v.start:
        return v.came
    return advance(prior, rules, v.start)


def with_returns(found: list[Visit]) -> list[Visit]:
    """Each visit's steps told when the next visit starts, so a decision is read against what that return finds."""
    return [replace(v, steps=tuple(replace(s, return_at=n.returned.time) for s in v.steps)) if n else v
            for v, n in zip(found, [*found[1:], None])]
