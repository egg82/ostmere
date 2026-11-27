"""When each skill's levels and each store's fills land if the player changes nothing (engine/design/, "Forecast").

A view's next_level_at and fills_at hold under the current segments only: an order that comes on, a tap that ends or
a store that runs dry changes them at the next event. A forecast resolves instant after instant with nobody deciding,
as advance does, so orders, the queue and everything running play out, and records every level-up, every fill (a
store reaching its cap as it stands then, from below) and every emptying up to `until`. That is the save's own future
while nobody decides, so it holds for every later save on the same path: a later forecast handed this one's path
takes the instants it already resolved, and only a decision (or new rules) needs them all again. Past `until`, past
MAX_INSTANTS instants, or once `stop` says so (then `until` is where it stopped), nothing is known, never guessed.
Pure: reads the save, writes nothing."""
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

from .events import Event
from .gates import store_cap
from .handlers import ignore
from .handsfree import hands_after, hands_at_start
from .ids import SkillId, StoreId
from .instant import resolve_instant
from .motion import store_segment
from .phases import at_top, next_level_xp, phase_top
from .prestige import mastered
from .rebuild import rebuild, shift
from .rules import Rules
from .schedule import events
from .segments import reach_time
from .state import Save

MAX_INSTANTS = 400


@dataclass(frozen=True)
class _Landed:
    """What lands while one instant's segments hold, up to the next instant (or the forecast's end): each level-up
    (dropped at the tally when an earlier window listed it), fill, emptying, and skill reaching its phase's top, in the
    order the tally takes them."""

    ups: tuple[tuple[SkillId, int], ...]
    fills: tuple[tuple[StoreId, int], ...]
    empties: tuple[tuple[StoreId, int], ...]
    tops: tuple[tuple[SkillId, int], ...]


@dataclass(frozen=True)
class _Leg:
    save: Save
    """A resolved instant, or the save the forecast began from."""
    arrivals: tuple[Event, ...]
    """The events that arrived at it (none for the start)."""
    landed: _Landed | None
    """What lands from it to the next leg's instant; None on the last leg, whose window ended at `until`, MAX_INSTANTS
    or the stop."""


@dataclass(frozen=True)
class ForecastPath:
    """The instants one forecast resolved, for a later forecast on the same path (forecast's `kept`)."""

    rules: Rules
    stores: tuple[StoreId, ...]
    legs: tuple[_Leg, ...]


@dataclass(frozen=True)
class Forecast:
    until: int
    """Everything that lands by this time is listed; nothing past it is known."""
    level_ups: dict[SkillId, tuple[int, ...]]
    """Skill: when each next level lands, in order."""
    fills: dict[StoreId, tuple[int, ...]]
    """Store: each time it reaches its cap from below, in order."""
    empties: dict[StoreId, tuple[int, ...]]
    """Store: each time it runs down to 0 from above, in order."""
    tops_out: dict[SkillId, int] = field(default_factory=lambda: {})
    """Skill: the instant it reaches its current phase's top (phases.phase_top), for each skill that does by `until`;
    the row's "tops out in". At most one per skill, since only the player's click lifts a top. A skill already at its
    top, a mastered one (prestige.mastered: no click waits at its top), and every skill under rules with no prestige,
    are absent. Its level_ups end at that top: the levels its
    carried XP passes wait for the click and are not level-ups (design/prestige-phases.txt, "PRESTIGE PHASES")."""
    hands_free_at: int | None = None
    """The first instant the player's work stops holding the hands (handsfree.py: no tap the player started runs on
    HANDS and the queue is empty), after the forecast began with it holding them; None when it did not (already free)
    or they are not free by `until`. Unlike the times above it depends on where the forecast begins, since the save does
    not record who started the tap running there."""
    path: ForecastPath | None = field(default=None, compare=False, repr=False)
    """The instants this forecast resolved, to hand a later forecast of the same save as its `kept`."""


def forecast(save: Save, rules: Rules, until: int, stores: tuple[StoreId, ...] = (),
             stop: Callable[[], bool] | None = None, kept: ForecastPath | None = None) -> Forecast:
    """Every level-up, and every fill and emptying of `stores`, by `until` (or as far as MAX_INSTANTS instants reach).
    `stop`, when given, is asked before each instant is resolved; True ends the forecast there. `kept`: an earlier
    forecast's path. The instants of it that follow `save` (a save that path passes through) are taken from it, not
    resolved again, and stop is not asked for them: the answer is the one a forecast without `kept` gives, except that
    it may reach further than that one's stop would have let it."""
    tally = _Tally(save, rules, stores)
    legs: list[_Leg] = []
    s, came, own, n, hands = save, tuple[Event, ...](), None, 0, hands_at_start(save, rules)
    for leg in _following(save, rules, stores, kept):
        if leg.save.time > until:   # a path holds MAX_INSTANTS instants at most, so `n` stays under it here
            break
        landed = own if own is not None else _landed(s, rules, leg.save.time, stores)
        tally.add(landed)
        legs.append(_Leg(s, came, landed))
        hands = hands_after(hands, s, leg.save, list(leg.arrivals), rules)
        s, came, own, n = leg.save, leg.arrivals, leg.landed, n + 1
    while True:
        upcoming = [ev for ev in events(s, rules) if ev.time > s.time]
        nxt = min((ev.time for ev in upcoming), default=None)
        end = until if nxt is None else min(until, nxt)
        landed = _landed(s, rules, end, stores)
        tally.add(landed)
        if nxt is None or nxt > until or n >= MAX_INSTANTS or (stop is not None and stop()):
            legs.append(_Leg(s, came, None))
            return tally.forecast(end, hands.free_at, ForecastPath(rules, stores, tuple(legs)))
        legs.append(_Leg(s, came, landed))
        arrivals = tuple(ev for ev in upcoming if ev.time == nxt)   # one instant, as api._advance resolves it
        after = resolve_instant(rebuild(shift(s, rules, nxt), rules), rules, list(arrivals), False, ignore)
        s, came, n, hands = after, arrivals, n + 1, hands_after(hands, s, after, list(arrivals), rules)


def _following(save: Save, rules: Rules, stores: tuple[StoreId, ...], kept: ForecastPath | None) -> Iterator[_Leg]:
    """The legs of `kept` after `save`, when `save` is on that path: the last leg at or before save.time, shifted to
    save.time, is `save`, and a leg follows it (a last leg's next instant was never resolved, so it vouches for no
    stretch after it)."""
    if kept is None or kept.rules is not rules or kept.stores != stores:
        return
    i = next((i for i in range(len(kept.legs) - 1, -1, -1) if kept.legs[i].save.time <= save.time), None)
    if i is None or i == len(kept.legs) - 1:
        return
    at = kept.legs[i].save
    if (at if at.time == save.time else shift(at, rules, save.time)) == save:
        yield from kept.legs[i + 1:]


class _Tally:
    """A forecast's lists, taking each window's _Landed in order."""

    def __init__(self, save: Save, rules: Rules, stores: tuple[StoreId, ...]) -> None:
        self._ups: dict[SkillId, list[int]] = {k.skill: [] for k in save.skills}
        self._fills: dict[StoreId, list[int]] = {st: [] for st in stores}
        self._empties: dict[StoreId, list[int]] = {st: [] for st in stores}
        self._tops = _topping(save, rules)
        self._topped: dict[SkillId, int] = {}

    def add(self, landed: _Landed) -> None:
        for k, at in landed.ups:
            if not self._ups[k] or at > self._ups[k][-1]:
                self._ups[k].append(at)
        for st, at in landed.fills:
            self._fills[st].append(at)
        for st, at in landed.empties:
            self._empties[st].append(at)
        for k, at in landed.tops:
            if k in self._tops:
                self._topped[k] = at

    def forecast(self, until: int, hands_free_at: int | None, path: ForecastPath) -> Forecast:
        return Forecast(until, _kept(self._ups), _kept(self._fills), _kept(self._empties), self._topped, hands_free_at,
                        path)


def _topping(save: Save, rules: Rules) -> dict[SkillId, int]:
    """Each skill below its phase's top and not mastered, with that top; none with rules.prestige None. Fixed for
    the forecast: a phase moves only at a click, a decision."""
    p = rules.prestige
    if p is None:
        return {}
    tops = {k.skill: phase_top(rules.curve, p, k.phase.phase) for k in save.skills}
    return {k: top for k, top in tops.items() if not at_top(save, rules, k) and not mastered(save, rules, k)}


def _kept[K](found: dict[K, list[int]]) -> dict[K, tuple[int, ...]]:
    return {k: tuple(v) for k, v in found.items() if v}


def _landed(s: Save, rules: Rules, end: int, stores: tuple[StoreId, ...]) -> _Landed:
    """What lands from s.time to `end`, while the segments hold: each level-up (phases.next_level_xp, so none past a
    phase's top), each of `stores` reaching its cap or 0, and each skill's XP reaching its phase's top (the tally keeps
    only the skills the forecast's start had below it)."""
    ups: list[tuple[SkillId, int]] = []
    for k in s.skills:
        x = next_level_xp(rules.curve, rules.prestige, k.phase.phase, k.xp.start_value)
        while x is not None and (at := reach_time(k.xp, x)) is not None and at <= end:
            ups.append((k.skill, at))
            x = next_level_xp(rules.curve, rules.prestige, k.phase.phase, x)
    fills: list[tuple[StoreId, int]] = []
    empties: list[tuple[StoreId, int]] = []
    for st in stores:
        cap = store_cap(s, rules, st)
        seg = store_segment(s, rules, st)
        at = reach_time(seg, cap) if seg.start_value < cap else None
        if at is not None and at <= end:
            fills.append((st, at))
        out = reach_time(seg, 0) if seg.start_value > 0 else None
        if out is not None and out <= end:
            empties.append((st, out))
    return _Landed(tuple(ups), tuple(fills), tuple(empties), _tops_in(s, rules, end))


def _tops_in(s: Save, rules: Rules, end: int) -> tuple[tuple[SkillId, int], ...]:
    """Each skill's XP reaching its phase's top from s.time to `end`, while the segments hold."""
    p = rules.prestige
    if p is None:
        return ()
    found: list[tuple[SkillId, int]] = []
    for k in s.skills:
        top = phase_top(rules.curve, p, k.phase.phase)
        if k.xp.start_value >= top:
            continue
        at = reach_time(k.xp, top)
        if at is not None and at <= end:
            found.append((k.skill, at))
    return tuple(found)
