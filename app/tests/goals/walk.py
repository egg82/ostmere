"""Every story beat met in a played route, and whether the screen showed what it waited on before it was met
(docs/decisions.md, "Progress is stated, never hinted"). Walks the moments the player saw (a player's history); for
each trigger that fires between two moments, reads the earlier one. Beats are named by trigger id only (CLAUDE.md,
"Never spoil the owner").

A beat is a trigger whose outcome is story (opening/goals.py, `story`). Shown means View.goals (api/goals.py) marked
the store, card or skill it waits on, or, for a wait on the clock, served the wait line with a time no later than the
beat (or stopped, naming the dry store) and naming every store whose running dry pauses that clock. Not beats here: a
beat on an unlock (it lands with what gives it), on a lane's rules (the lesson is the step), on the Camp's store (its
bar).

A beat nothing could show at the moment before (not pending then, a clock with no time and no dry store stopping it,
a card or skill not on screen) is judged by the step that starts it: an open trigger giving an unlock it lacks (one it
requires, the standing action that moves a store it reads, the card or skill it reads), itself judged the same way at
that moment, stated when any such step is shown. A beat met with no game time passing came of the player's move at
that moment and waits on nothing: stated. A beat whose only unmet conditions at the moment before are unlocks given by
the next completion of a card the player tapped, landing by the moment after, lands with that card, as a beat on an
unlock lands with what gives it: stated (`tapped` names the card). A beat with no open step that starts it is unjudged
(`stated` None), and the caller holds those by id."""
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache

from ashfall_app.api import goal_models as g
from ashfall_app.api.goals import goals, stopped
from ashfall_app.engine import (
    ActionId, AfterTime, AtLeast, CardCount, CardId, CardView, LaneRules, Pending, Rules, RunBy, Running, Save, SkillLevel,
    StoreValue, TapCard, TriggerDef, Unlock, Unlocked, UnlockKind, Verb, View, pending,
)
from ashfall_app.engine.conditions import is_true
from ashfall_app.engine.work import completions
from ashfall_app.opening.goals import GoalDef, goal_defs, moved_by, story
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening

Served = Callable[[Save, Rules, View, Mapping[str, GoalDef]], list[g.Goal]]


@dataclass(frozen=True)
class Met:
    trigger: str
    at: int
    """The moment after it fired (game seconds)."""
    before: int
    """The moment before it fired: `at` when it came of the player's move at that moment."""
    stated: bool | None
    """None: no open step starts it, so not judged (module docstring)."""
    tapped: str | None = None
    """The card whose tapped completion it landed with (module docstring)."""


@dataclass(frozen=True)
class Tap:
    """A player's tap: when, the card, and the save it was made on."""
    at: int
    card: CardId
    on: Save


def taps(decisions: Sequence[tuple[int, object, Verb]], undecided: Sequence[Save]) -> list[Tap]:
    """The taps among a player's decisions, `undecided[i]` being the save decision i was made on."""
    return [Tap(at, v.card, undecided[i]) for i, (at, _, v) in enumerate(decisions) if isinstance(v, TapCard)]


@dataclass(frozen=True)
class _Moment:
    """The moment before a beat, as the walk reads it."""
    save: Save
    view: View
    rules: Rules
    by: int
    """The beat's time: the moment after."""
    shown: list[g.Goal]
    pend: dict[str, Pending]
    unlocked: set[str]


@dataclass(frozen=True)
class _Starts:
    """What gives each unlock, and which standing actions move each store: the steps that start a beat."""
    givers: dict[Unlock, list[TriggerDef]]
    movers: dict[str, set[Unlock]]


@cache
def content() -> Opening:
    return load_opening(chapters=CHAPTERS + IN_WRITING)


def served_nothing(save: Save, rules: Rules, v: View, defs: Mapping[str, GoalDef]) -> list[g.Goal]:
    """A page that states no goal: the guard's control."""
    return []


def walk(history: Sequence[tuple[Save, View]], rules: Rules, served: Served = goals,
         tapped: Sequence[Tap] = ()) -> list[Met]:
    """Each gate met over `history`, in the order met; `tapped` the player's taps over it."""
    o = content()
    camp = None if o.camp is None else o.camp.store
    gd = goal_defs(o, rules)
    starts = _starts(o, rules)
    out: list[Met] = []
    for (a, va), (b, _) in zip(history, history[1:]):
        fired = [i for i, (x, y) in enumerate(zip(a.fired, b.fired)) if y and not x]
        gates = [rules.triggers[i] for i in fired if _gate(rules.triggers[i], camp, gd)]
        if not gates:
            continue
        pend = {str(p.trigger): p for p in pending(a, rules)}
        m = _Moment(a, va, rules, b.time, served(a, rules, va, gd), pend, {str(u.id) for u in va.unlocked})
        for t in gates:
            card = None if b.time == a.time else _landed_with(t, m, tapped)
            stated = True if b.time == a.time or card else _stated(t, m, gd, starts, set())
            out.append(Met(t.id, b.time, a.time, stated, card))
    return out


def _landed_with(t: TriggerDef, m: _Moment, tapped: Sequence[Tap]) -> str | None:
    """The card a player tapped whose next completion, by the moment after, gives every unlock the beat still lacks,
    every other condition of it already met at the moment before (module docstring)."""
    unmet = [c for c in (t.when, *t.requires) if not is_true(m.save, m.rules, c)]
    if not unmet or not all(isinstance(c, AtLeast) and isinstance(c.subject, Unlocked) for c in unmet):
        return None
    lacks = {c.subject.unlock for c in unmet if isinstance(c, AtLeast) and isinstance(c.subject, Unlocked)}
    defs = {d.id: d for d in m.rules.cards}
    for c in m.view.cards:
        if (c.by is RunBy.TAP and c.completes_at is not None and m.save.time < c.completes_at <= m.by
                and lacks <= _gives(c, defs[c.card].outcome.unlocks, defs[c.card].finished.unlocks)
                and any(x.card == c.card and x.at <= m.save.time
                        and completions(x.on, m.rules, c.card) == c.completions for x in tapped)):
            return str(c.card)
    return None


def _gives(c: CardView, outcome: tuple[Unlock, ...], finished: tuple[Unlock, ...]) -> set[Unlock]:
    """What the card's next completion unlocks: its outcome's, and its finished outcome's when that reaches the cap."""
    return {*outcome, *(finished if c.cap is not None and c.completions + 1 >= c.cap else ())}


def _gate(t: TriggerDef, camp: str | None, gd: Mapping[str, GoalDef]) -> bool:
    """A story beat the player meets that waits on something of its own (module docstring)."""
    w = t.when
    if not story(t.outcome) or t.id in gd or isinstance(w, AfterTime):
        return story(t.outcome)
    s = w.subject
    return not (isinstance(s, (Unlocked, LaneRules)) or (isinstance(s, StoreValue) and s.store == camp))


def _stated(t: TriggerDef, m: _Moment, gd: Mapping[str, GoalDef], starts: _Starts, seen: set[str]) -> bool | None:
    """Its own wait shown, or else the step that starts it (module docstring)."""
    p, d = m.pend.get(t.id), gd.get(t.id)
    if p is not None and d is not None and not _unseen(d, p.at, m):
        return _shown(d, m.by, p.at, m.shown, m.unlocked)
    steps = [s for s in _steps(t, m.save, starts) if s.id in m.pend and s.id not in seen]
    seen |= {s.id for s in steps}
    verdicts = [_stated(s, m, gd, starts, seen) for s in steps]
    return True if True in verdicts else False if False in verdicts else None


def _steps(t: TriggerDef, save: Save, starts: _Starts) -> list[TriggerDef]:
    """The triggers giving an unlock `t` lacks at `save`."""
    lacks = _needs(t, starts) - set(save.unlocked)
    return list({s.id: s for u in lacks for s in starts.givers.get(u, [])}.values())


def _needs(t: TriggerDef, starts: _Starts) -> set[Unlock]:
    """The unlocks its conditions read: an unlock required, the standing actions moving a store, a card, a skill."""
    out: set[Unlock] = set()
    for c in (t.when, *t.requires):
        s = None if isinstance(c, AfterTime) else c.subject
        if isinstance(s, Unlocked):
            out.add(s.unlock)
        elif isinstance(s, StoreValue):
            out |= starts.movers.get(str(s.store), set())
        elif isinstance(s, CardCount):
            out.add(Unlock(UnlockKind.CARD, s.card))
        elif isinstance(s, Running):
            out |= {Unlock(UnlockKind.CARD, CardId(s.runner)), Unlock(UnlockKind.ACTION, ActionId(s.runner))}
        elif isinstance(s, SkillLevel):
            out.add(Unlock(UnlockKind.SKILL, s.skill))
    return out


def _starts(o: Opening, rules: Rules) -> _Starts:
    givers: dict[Unlock, list[TriggerDef]] = {}
    for t in rules.triggers:
        for u in t.outcome.unlocks:
            givers.setdefault(u, []).append(t)
    movers: dict[str, set[Unlock]] = {}
    for a in o.standing:
        for s in moved_by(a):
            movers.setdefault(s, set()).add(Unlock(UnlockKind.ACTION, ActionId(a.id)))
    return _Starts(givers, movers)


def _unseen(d: GoalDef, at: int | None, m: _Moment) -> bool:
    """Nothing could have shown its own wait at this moment (module docstring)."""
    if d.kind == "clock":
        return at is None and not stopped(m.save, m.rules, d)
    if d.kind == "card":
        return d.subject not in {str(c.card) for c in m.view.cards}
    return d.kind == "level" and d.subject not in {str(b.skill) for b in m.view.skills}


def _shown(d: GoalDef, by: int, at: int | None, shown: list[g.Goal], unlocked: set[str]) -> bool:
    """A clock: the wait line's time is no later than the beat, and when it is this clock's own time (or the clock is
    stopped) it names every unlocked store that keeps the clock moving. Else the store, card or skill is marked."""
    if d.kind == "clock":
        feeds = set(d.fed_by) & unlocked
        return any(x.kind == g.GoalKind.CLOCK and (
            (x.at is not None and x.at <= by and (x.at != at or feeds <= set(x.feeds)))
            or (x.at is None and at is None and feeds <= set(x.feeds))) for x in shown)
    return any((x.store, x.card, x.skill)[("store", "card", "level").index(d.kind)] == d.subject
               for x in shown if x.kind != g.GoalKind.CLOCK)


def misses(met: Sequence[Met]) -> list[str]:
    """`trigger at <hours>h` for each gate met with nothing on screen stating it before."""
    return [f"{m.trigger} at {m.at / 3600:.2f}h" for m in met if m.stated is False]


def unjudged(met: Sequence[Met]) -> set[str]:
    """The gates met with no open step starting them (module docstring)."""
    return {m.trigger for m in met if m.stated is None}
