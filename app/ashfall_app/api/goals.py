"""View.goals: what the open story beats wait on, read off the engine's pending triggers and the content's goals
(opening/goals.py; CONTRACT.txt, "Goals")."""
from collections.abc import Mapping

from .. import engine as e
from ..opening.goals import GoalDef
from . import convert
from . import goal_models as g

_PAUSED = 2**62
"""Sorts a clock with no time (a store it waits on is dry) after every clock with one."""


def goals(save: e.Save, rules: e.Rules, v: e.View, defs: Mapping[str, GoalDef]) -> list[g.Goal]:
    """Every store, card and skill an open story beat waits on that is in play, at its lowest target, in content order;
    a require on an unlock waits on what the earliest trigger giving it waits on. Then the soonest clock with a time,
    else one stopped on a dry store it waits on, with the unlocked stores that keep each clock landing then moving.
    Open: unfired, with each require held or given by an unfired trigger (engine pending)."""
    pend = {str(p.trigger): p for p in e.pending(save, rules, defs.keys())}
    givers = _givers(rules, pend)
    in_play = {str(c.card) for c in v.cards} | {str(u.id) for u in v.unlocked if u.kind is e.UnlockKind.STORE}
    skills = {str(b.skill) for b in v.skills}
    shown = {str(u.id) for u in v.unlocked if u.kind is e.UnlockKind.STORE}
    work: dict[tuple[str, str | None], GoalDef] = {}
    clocks: list[tuple[int, GoalDef]] = []
    for t in rules.triggers:
        p = pend.get(t.id)
        if p is None:
            continue
        for d, at in _parts(t, p, givers, defs):
            if d.kind == "clock":
                clocks += [(at, d)] if at is not None else [(_PAUSED, d)] if stopped(save, rules, d) else []
            elif _shown(d, in_play, skills):
                held = work.get((d.kind, d.subject))
                work[(d.kind, d.subject)] = d if held is None or d.target < held.target else held
    out = [_goal(save, rules, d) for d in work.values()]
    if not clocks:
        return out
    at = min(x[0] for x in clocks)
    fed = dict.fromkeys(s for t, d in clocks if t == at for s in d.fed_by if s in shown)
    return out + [g.Goal(kind=g.GoalKind.CLOCK, store=None, card=None, skill=None, target=0, value=None,
                         at=None if at == _PAUSED else at, feeds=list(fed))]


def stopped(save: e.Save, rules: e.Rules, d: GoalDef) -> bool:
    """A clock with no time is stopped, not unstarted, when a store that keeps it moving is dry."""
    return any(e.segment(save, rules, e.StoreId(s)).start_value == 0 for s in d.fed_by)


def _parts(t: e.TriggerDef, p: e.Pending, givers: Mapping[e.Unlock, list[e.Pending]],
           defs: Mapping[str, GoalDef]) -> list[tuple[GoalDef, int | None]]:
    """The beat's own condition, and for a require on an unlock it lacks, what the earliest open trigger giving that
    unlock waits on (one step: the giver's own condition)."""
    own = defs.get(t.id)
    out: list[tuple[GoalDef, int | None]] = [] if own is None else [(own, p.at)]
    if p.held:
        return out
    for c in t.requires:
        if not isinstance(c, e.AtLeast) or not isinstance(c.subject, e.Unlocked):
            continue
        given = givers.get(c.subject.unlock)
        if given:
            q = min(given, key=lambda x: x.at if x.at is not None else 2**62)
            d = defs.get(q.trigger)
            out += [] if d is None else [(d, q.at)]
    return out


def _givers(rules: e.Rules, pend: Mapping[str, e.Pending]) -> dict[e.Unlock, list[e.Pending]]:
    """Each unlock to the open triggers giving it, in `pend`'s order (min keeps the first of equal times)."""
    out: dict[e.Unlock, list[e.Pending]] = {}
    for t in rules.triggers:
        if (p := pend.get(t.id)) is not None:
            for u in t.outcome.unlocks:
                out.setdefault(u, []).append(p)
    return out


def _shown(d: GoalDef, in_play: set[str], skills: set[str]) -> bool:
    """`in_play`: the cards in play and the unlocked stores."""
    if d.kind == "card":
        return d.subject in in_play
    if d.kind == "level":
        return d.subject in skills
    return d.subject in in_play or bool(in_play.intersection(d.makers))


def _goal(save: e.Save, rules: e.Rules, d: GoalDef) -> g.Goal:
    if d.kind == "store" and d.subject is not None:
        seg = convert.segment(e.segment(save, rules, e.StoreId(d.subject)))
        return g.Goal(kind=g.GoalKind.STORE, store=d.subject, card=None, skill=None, target=d.target, value=seg, at=None,
                      feeds=[])
    if d.kind == "level":
        return g.Goal(kind=g.GoalKind.LEVEL, store=None, card=None, skill=d.subject, target=d.target, value=None, at=None,
                      feeds=[])
    return g.Goal(kind=g.GoalKind.CARD, store=None, card=d.subject, skill=None, target=d.target, value=None, at=None,
                  feeds=[])
