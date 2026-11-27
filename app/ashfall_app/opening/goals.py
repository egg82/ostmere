"""What each story beat waits on, so the page can mark it (docs/decisions.md, "Progress is stated, never hinted"): read
off the content's rules once, at load, the loader's own triggers (offers, notes) included. tests/goals holds that every
story beat met in play had what it waited on marked before it."""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from ..engine import AfterTime, AtLeast, AtMost, CardCount, Outcome, Rules, Running, SkillLevel, StoreValue, TriggerDef
from .makers import card_made, made_by

if TYPE_CHECKING:
    from .entries import StandingEntry
    from .schema import Opening

GoalKind = Literal["store", "card", "level", "clock", "fight"]


@dataclass(frozen=True)
class GoalDef:
    kind: GoalKind
    """What a story beat waits on. store: a store's amount; card: a card's completions, or the card running (target
    0); level: a skill's level; clock: a wait nothing the player does shortens; fight: a card's fight lost that many
    times (its lost tally, which no screen draws as a store: the card carries it)."""
    subject: str | None
    """The store, card or skill; the fight's card; None for a clock."""
    target: int
    """Quantity units (store, fight), completions (card), a level (level); 0 for a clock or a card running."""
    makers: tuple[str, ...] = ()
    """A store's: the cards that make it (makers.made_by). It shows once its store is unlocked or one is in play."""
    fed_by: tuple[str, ...] = ()
    """A clock's: the stores whose running dry pauses it (the other costs of the standing actions that move it)."""
    count: str | None = None
    """A clock on a store authored `stated`: the store whose amount the wait line states against `target`."""
    tally: str | None = None
    """A fight's: the lost tally store the card's fight adds to."""


def goal_defs(o: "Opening", rules: Rules) -> dict[str, GoalDef]:
    """Trigger id to what it waits on, for each story beat of `rules` (the content's) the page can show."""
    out: dict[str, GoalDef] = {}
    clocks = _clocks(o)
    stated = frozenset(s.id for s in o.stores if s.stated)
    camp = None if o.camp is None else o.camp.store
    fights = {c.fight.lost: c.id for c in o.cards if c.fight is not None}
    for t in rules.triggers:
        goal = _goal(o, t, clocks, camp, fights, stated) if story(t.outcome) else None
        if goal is not None:
            out[str(t.id)] = goal
    return out


def story(out: Outcome) -> bool:
    """A story beat: it unlocks something, someone joins or leaves, or it tells lines with no find or effect on them.
    A find (a store with its lines), an effect, a Camp level are progress the player sees where it lands."""
    moves = out.unlocks or out.joins or out.leaves or out.casts
    return bool(moves) or (bool(out.lines) and not out.stores and not out.modifiers)


def _clocks(o: "Opening") -> frozenset[str]:
    """Stores no card fills, and hidden ones but a tally the cards add to: what moves them is time (a standing action)
    or what comes by itself (a fight's tally), not work."""
    return frozenset(s.id for s in o.stores if not card_made(o, s.id) or (s.hidden and not s.tally))


def _fed_by(o: "Opening", store: str) -> tuple[str, ...]:
    """The other stores the standing actions moving `store` cost, a fight's losses included: a standing action stops
    while one of them is dry."""
    moving = [a for a in o.standing if store in moved_by(a)]
    return tuple(dict.fromkeys(s for a in moving for s in _costs(a) if s != store))


def moved_by(a: "StandingEntry") -> set[str]:
    """The stores a standing action's lines move: its flows, and its fight's tallies, wounds and losses."""
    f = a.fight
    fight: set[str] = set() if f is None else {f.lost, *([] if f.fought is None else [f.fought]),
                                     *(x.store for x in (*f.loses, *f.wounds))}
    return {x.store for x in (*a.makes, *a.costs)} | fight


def _costs(a: "StandingEntry") -> list[str]:
    return [x.store for x in a.costs] + ([] if a.fight is None else [x.store for x in a.fight.loses])


def _goal(o: "Opening", t: TriggerDef, clocks: frozenset[str], camp: str | None,
          fights: dict[str, str], stated: frozenset[str]) -> GoalDef | None:
    """None for an unlock (it waits on what gives it), a lane's rules (the lesson on screen is the step), and the Camp's
    store (its bar states its levels). `fights`: each card fight's lost tally store to its card; `stated`: the hidden
    stores whose amount a clock on them states."""
    w = t.when
    if isinstance(w, AfterTime):
        return GoalDef("clock", None, 0)
    s = w.subject
    if isinstance(s, CardCount) and isinstance(w, AtLeast):
        return GoalDef("card", str(s.card), w.value)
    if isinstance(s, Running) and isinstance(w, AtLeast):
        return GoalDef("card", str(s.runner), 0)
    if isinstance(s, SkillLevel) and isinstance(w, AtLeast):
        return GoalDef("level", str(s.skill), w.value)
    if not isinstance(s, StoreValue) or s.store == camp:
        return None
    if isinstance(w, AtLeast) and str(s.store) in fights:
        return GoalDef("fight", fights[str(s.store)], w.value, tally=str(s.store))
    if isinstance(w, AtMost) or s.store in clocks:
        store = str(s.store)
        if isinstance(w, AtLeast) and store in stated:
            return GoalDef("clock", None, w.value, fed_by=_fed_by(o, store), count=store)
        return GoalDef("clock", None, 0, fed_by=_fed_by(o, store))
    return GoalDef("store", str(s.store), w.value, tuple(made_by(o, str(s.store))))
