"""When the hands come free of the player's work, as a forecast sees it (engine/design/, "Forecast", "Hands free").

The player's work holds the hands while the queue holds an entry (a goal stint's included) or HANDS runs a tap the
player started: by their own TapCard or by a queue entry. A tap an order or an outcome started, the mix and Rest are
what runs by itself. The save does not record who started the tap HANDS runs, so the one running where a forecast
begins is the player's unless an order that is on taps that card (plan.lane_order); a tap starting inside the forecast
is the queue's when an entry taps its card and no order that is on does, since evaluation applies an order's tap
before the queue's."""
from dataclasses import dataclass

from ..core.events import Event, EventKind
from ..core.ids import HANDS, CardId
from ..orders.lanes import TapCard
from ..orders.plan import lane_order
from ..core.rules import Rules
from ..core.state import Save


@dataclass(frozen=True)
class Hands:
    """`armed`: the player's work held the hands where the forecast began, so a free moment can follow. `tapped`: the
    tap HANDS runs at the state last seen is the player's. `free_at`: the first instant the hands came free."""

    armed: bool
    tapped: bool
    free_at: int | None = None


def hands_at_start(save: Save, rules: Rules) -> Hands:
    tapped = _card(save) is not None and lane_order(save, rules, HANDS) is None
    return Hands(armed=bool(save.queue) or tapped, tapped=tapped)


def hands_after(h: Hands, before: Save, after: Save, arrivals: list[Event], rules: Rules) -> Hands:
    """`h` carried over one resolved instant, from `before` to `after`, whose arrivals were `arrivals`."""
    if not h.armed or h.free_at is not None:
        return h
    card = _card(after)
    if card is None:
        tapped = False
    elif card != _card(before) or any(ev.kind is EventKind.TAP_DONE and ev.subject == HANDS for ev in arrivals):
        queued = any(q.verb == TapCard(card) for q in (*before.queue, *after.queue))
        tapped = queued and lane_order(after, rules, HANDS) is None
    else:
        tapped = h.tapped
    if after.queue or tapped:
        return Hands(True, tapped)
    return Hands(True, False, after.time)


def _card(save: Save) -> CardId | None:
    return next(ls.card for ls in save.lanes if ls.lane == HANDS)
