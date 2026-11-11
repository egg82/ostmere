"""When each skill's levels and each store's fills land if the player changes nothing (DESIGN.txt, "Forecast").

A view's next_level_at and fills_at hold under the current segments only: an order that comes on, a tap that ends or
a store that runs dry changes them at the next event. A forecast resolves instant after instant with nobody deciding,
as advance does, so orders, the queue and everything running play out, and records every level-up, every fill (a
store reaching its cap as it stands then, from below) and every emptying up to `until`. That is the save's own future
while nobody decides, so it holds for every later save on the same path: a plain advance reuses it, and only a
decision (or new rules) needs a new one. Past `until`, past MAX_INSTANTS instants, or once `stop` says so (then `until`
is where it stopped), nothing is known, never guessed. Pure: reads the save, writes nothing."""
from collections.abc import Callable
from dataclasses import dataclass, field

from .gates import store_cap
from .handlers import ignore
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
    carried XP passes wait for the click and are not level-ups (DESIGN.txt, "PRESTIGE PHASES")."""


def forecast(save: Save, rules: Rules, until: int, stores: tuple[StoreId, ...] = (),
             stop: Callable[[], bool] | None = None) -> Forecast:
    """Every level-up, and every fill and emptying of `stores`, by `until` (or as far as MAX_INSTANTS instants reach).
    `stop`, when given, is asked before each instant is resolved; True ends the forecast there."""
    ups: dict[SkillId, list[int]] = {k.skill: [] for k in save.skills}
    fills: dict[StoreId, list[int]] = {st: [] for st in stores}
    empties: dict[StoreId, list[int]] = {st: [] for st in stores}
    tops, topped = _topping(save, rules), dict[SkillId, int]()
    s, n = save, 0
    while True:
        upcoming = [ev for ev in events(s, rules) if ev.time > s.time]
        nxt = min((ev.time for ev in upcoming), default=None)
        end = until if nxt is None else min(until, nxt)
        _window(s, rules, end, ups, fills, empties)
        _tops_in(s, end, tops, topped)
        if nxt is None or nxt > until or n >= MAX_INSTANTS or (stop is not None and stop()):
            return Forecast(end, _kept(ups), _kept(fills), _kept(empties), topped)
        arrivals = [ev for ev in upcoming if ev.time == nxt]   # one instant, as api._advance resolves it
        s, n = resolve_instant(rebuild(shift(s, rules, nxt), rules), rules, arrivals, False, ignore), n + 1


def _topping(save: Save, rules: Rules) -> dict[SkillId, int]:
    """Each skill below its phase's top and not mastered, with that top; none with rules.prestige None. Fixed for
    the forecast: a phase moves only at a click, a decision."""
    p = rules.prestige
    if p is None:
        return {}
    tops = {k.skill: phase_top(rules.curve, p, k.phase.phase) for k in save.skills}
    return {k: top for k, top in tops.items() if not at_top(save, rules, k) and not mastered(save, rules, k)}


def _tops_in(s: Save, end: int, tops: dict[SkillId, int], topped: dict[SkillId, int]) -> None:
    """Each skill's XP reaching its top (`tops`) from s.time to `end`, while the segments hold, into `topped`."""
    for k in s.skills:
        top = tops.get(k.skill)
        if top is None or k.xp.start_value >= top:
            continue
        at = reach_time(k.xp, top)
        if at is not None and at <= end:
            topped[k.skill] = at


def _kept[K](found: dict[K, list[int]]) -> dict[K, tuple[int, ...]]:
    return {k: tuple(v) for k, v in found.items() if v}


def _window(s: Save, rules: Rules, end: int, ups: dict[SkillId, list[int]], fills: dict[StoreId, list[int]],
            empties: dict[StoreId, list[int]]) -> None:
    """What lands from s.time to `end`, while the segments hold: each level-up (phases.next_level_xp, so none past a
    phase's top), each store reaching its cap or 0."""
    for k in s.skills:
        x = next_level_xp(rules.curve, rules.prestige, k.phase.phase, k.xp.start_value)
        while x is not None and (at := reach_time(k.xp, x)) is not None and at <= end:
            if not ups[k.skill] or at > ups[k.skill][-1]:
                ups[k.skill].append(at)
            x = next_level_xp(rules.curve, rules.prestige, k.phase.phase, x)
    for k in s.stores:
        if k.store in fills:
            cap = store_cap(s, rules, k.store)
            seg = store_segment(s, rules, k.store)
            at = reach_time(seg, cap) if seg.start_value < cap else None
            if at is not None and at <= end:
                fills[k.store].append(at)
            out = reach_time(seg, 0) if seg.start_value > 0 else None
            if out is not None and out <= end:
                empties[k.store].append(out)
