"""What a route does in week five's four chapters, as data a chapter fills in when it lands (docs/design/week-five-plan.md,
item 9): a `Week` names one chapter's story ids and the ids each policy acts on, and `later` plays it on from the chapter
before as week four's `weekfour.py` does, by the same `Later` the moves read (daythree/moves.py). The policies:

- chip rules written at a chip's first showing, for a route that takes rules and none for a lazy one;
- the filling card and the week's second trip in the mix at a route's share, a route not named following typical;
- the cast notable's town card in the mix at a route's share once its role is cast, 0 keeping it off the line;
- a two-answer offer answered by route, typical the yes and sharp the other, so both paths are measured;
- both builds' order cards, the arrival offers by the kind's rule where the route set one, the asks;
- the glowing steps tapped the moment they are ready, or queued When ready;
- the new input store made by a route's choice (a keep for the routes named).

Ids come from the chapter (CLAUDE.md, "Never spoil the owner"). A chapter's moves file registers `later`'s result in
tests/weektwo/routes.py DAYS and keys.py MOVES as the earlier weeks' do; nothing here is read by a play until it does."""
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace

from ashfall_app.engine import AnswerId, CardId, ChipId, OfferId, Order, Rules, Save, Unlock, View
from tests.daythree import moves
from tests.daythree.chapter import ChipRule, Keep, Later, Offer, Share
from tests.dayone.player.policy import Move
from tests.dayone.player.sinks import SINKS, Chapter, Trip
from tests.weekfive.reads import cast_lane

TYPICAL = "typical"


def lazy(route: str) -> bool:
    """A route that neither mixes a trip nor queues a comfort (dayone/player/sinks.py SINKS): it writes no rule of its own."""
    knobs = SINKS.get(route, SINKS[TYPICAL])
    return not (knobs.mix_trips or knobs.queue_comforts)


def by_route[T](table: Mapping[str, T], route: str) -> T:
    """The route's entry, or typical's when the route is not named."""
    return table[route] if route in table else table[TYPICAL]


@dataclass(frozen=True)
class RouteShare:
    """A card in the active mix at a share set by route (basis points of the hands' time), from the visit it is shown in."""

    card: CardId
    bp: Mapping[str, int]
    until: Callable[[Save], bool] | None = None
    """Once this holds the card leaves the mix (a finite pool spent), as chapter.Share.until."""


@dataclass(frozen=True)
class CastCard:
    """A town card on the cast lane of `role`, `pattern` as the content writes its id with {lane}, in the mix at a share
    set by route once the cast has happened; a share of 0 keeps it off the line."""

    role: str
    pattern: str
    bp: Mapping[str, int]

    def card_on(self, lane: str) -> CardId:
        return CardId(self.pattern.replace("{lane}", lane))


@dataclass(frozen=True)
class TwoAnswer:
    """An offer with two answers, answered in the visit it shows: typical's, and the others' by route (sharp's the other)."""

    offer: OfferId
    answers: Mapping[str, AnswerId]


@dataclass(frozen=True)
class Week:
    """One chapter's route-facing ids; every field but the story ids is empty until the chapter has it."""

    start: str
    stop: str
    landed: Callable[[Save, Rules], set[str]]
    news: tuple[str, ...]
    chips: tuple[ChipRule, ...] = ()
    shares: tuple[RouteShare, ...] = ()
    casts: tuple[CastCard, ...] = ()
    two_answers: tuple[TwoAnswer, ...] = ()
    order_cards: tuple[tuple[Unlock, Order] | Offer, ...] = ()
    arrivals: tuple[tuple[OfferId, AnswerId], ...] = ()
    asks: tuple[tuple[OfferId, AnswerId], ...] = ()
    trips: tuple[Trip, ...] = ()
    steps: tuple[CardId, ...] = ()
    queued: tuple[CardId, ...] = ()
    keeps: tuple[tuple[Keep, frozenset[str]], ...] = ()
    """The input store's keep and the routes that make it; a route not named never does."""


def cast_move(casts: tuple[CastCard, ...], route: str) -> Callable[[View, Save, Rules], Move | None]:
    """The first cast card not yet in the mix, put in at the route's share once its role is cast (chapter.Share's move)."""
    def move(v: View, save: Save, rules: Rules) -> Move | None:
        for c in casts:
            lane, bp = cast_lane(save, rules, c.role), by_route(c.bp, route)
            if lane is not None and bp > 0:
                stub = replace(_BARE, shares=(Share(c.card_on(lane), bp),))
                if (found := moves.share(v, save, stub)) is not None:
                    return found
        return None
    return move


def _no_story(save: Save, rules: Rules) -> set[str]:
    return set()


_BARE = Later(start="", stop="", sinks=Chapter(), steps=(), order_cards=(), keeps=(), landed=_no_story, news=())
"""A chapter that does nothing, the base a share is read through."""


def first_move(*each: Callable[[View, Save, Rules], Move | None] | None) -> Callable[[View, Save, Rules], Move | None]:
    """The first of `each` that has a move: the chapters' own moves, the earlier week's before this one's."""
    found = [f for f in each if f is not None]
    def move(v: View, save: Save, rules: Rules) -> Move | None:
        return next((m for f in found if (m := f(v, save, rules)) is not None), None)
    return move


def later(prev: Later, week: Week, route: str) -> Later:
    """`week` as `route` plays it, on from `prev`'s sinks, rules, shares and moves, which it keeps."""
    answers = [(t.offer, by_route(t.answers, route)) for t in week.two_answers]
    return replace(
        prev, start=week.start, stop=week.stop, landed=week.landed, news=week.news,
        sinks=Chapter(trips=(*prev.sinks.trips, *week.trips), comforts=prev.sinks.comforts,
                      arrivals=(*prev.sinks.arrivals, *week.arrivals), first=prev.sinks.first),
        steps=week.steps, queued=week.queued,
        order_cards=(*prev.order_cards, *week.order_cards),
        keeps=(*prev.keeps, *(k for k, routes in week.keeps if route in routes)),
        answers=(*prev.answers, *answers, *week.asks),
        shares=(*prev.shares, *(Share(s.card, bp, s.until) for s in week.shares if (bp := by_route(s.bp, route)) > 0)),
        chip_rules=(*prev.chip_rules, *(() if lazy(route) else week.chips)),
        own=first_move(prev.own, cast_move(week.casts, route) if week.casts else None))


def chip_cure(chip: str, cure: str) -> ChipRule:
    return ChipRule(ChipId(chip), CardId(cure))
