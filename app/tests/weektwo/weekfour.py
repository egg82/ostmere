"""Week four's chapters as the routes play them (daythree/chapter.Later), played on from week three's end by the same
players as weeks two and three (content.py): which content step is which story id, read off a save, and what each
chapter adds to the policies. Ids only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Callable

from ashfall_app.engine import AnswerId, CardId, ChipId, OfferId, Rules, Save, StoreId, TapCard, View, units
from ashfall_app.engine.rates import store_value
from ashfall_app.engine.work import completions
from tests.daythree.chapter import ChipRule, Landings, Later, Share
from tests.dayone.policy import Move, lane_free
from tests.dayone.sinks import Chapter
from tests.weektwo import content as w2

TWENTY_TWO = Landings(
    {"I1": ("t_i1",), "B18": ("t_b18",), "SL29": ("t_fish",), "I2": ("t_film",), "I3": ("t_bowl",), "I4": ("t_pace",),
     "SL30": ("t_singing",), "B19": ("t_b19",)}, {}, {}, {})
WALK, FOG_FISH = CardId("walk_ashwood"), CardId("fog_fish")
WALK_SHARE = {"typical": 3000, "sharp": 4000}
"""The hands' share of the walk a route sets from the visit it is shown in, T13's (a route not named follows typical);
the town's twin on one lane is the route's split (content.py)."""
FISH_SHARE = 1000
"""The hands' share a route gives the fish once shown (SL29); the pool is finite, so its share yields once it is spent
(decisions.md, "A mix keeps going without a dry store")."""
WASH = ChipRule(ChipId("ashed"), CardId("n3_wash_meat"))
"""The rule a route that takes rules writes on the film's chip, which has no order card (D-155): the cure on her lane,
from the visit the chip is first seen."""


def day_twenty_two(route: str) -> Later:
    """T13's visit to B19's, week four's first: day nineteen's sinks, rules, split and shares carried on, the walk in the
    hands' mix from the visit it is shown in and on one lane once the town can walk it (B18), the fish at a share once
    shown, and the chip's rule written once the chip is seen."""
    nineteen = w2.day_nineteen(route)
    return Later(
        start="T13", stop="B19",
        sinks=nineteen.sinks,
        steps=(), order_cards=nineteen.order_cards, keeps=nineteen.keeps,
        landed=TWENTY_TWO.of, news=("I1", "B18", "SL29", "I2", "I3", "I4", "SL30", "B19"),
        answers=nineteen.answers,
        shares=(*nineteen.shares, Share(WALK, WALK_SHARE.get(route, WALK_SHARE["typical"])), Share(FOG_FISH, FISH_SHARE)),
        cures=nineteen.cures, own=nineteen.own, chip_rules=(WASH,))


TWENTY_THREE = Landings(
    {"SL31": ("t_named",), "I6": ("t_cache",), "SL32": ("t_stir",), "I7": ("t_post_ring",), "SL33": ("t_rooting",),
     "B20": ("t_b20",)},
    {"A39": ("go_wallow",)}, {}, {"I5": OfferId("o_fiddle"), "O-fiddle": OfferId("o_fiddle"), "O-book": OfferId("o_book")})
"""I5 is its offer's showing (the offer carries the beat's lines)."""
GO_WALLOW, BIND_BOOK = CardId("go_wallow"), CardId("bind_book")
FIDDLE = {"typical": AnswerId("o_fiddle_food"), "sharp": AnswerId("o_fiddle_build")}
"""Where the man and his wife work first, as each route answers (a route not named follows typical): both answers
measured. The whenever player's kind rule, set in week three, answers it."""
BOOK = {"typical": AnswerId("o_book_make"), "sharp": AnswerId("o_book_later")}
"""O-book as each route answers it in the visit it shows: sharp says not now, then makes the book later (BOOK_LATER_H),
so both paths are measured (week-four-plan item 7)."""
BOOK_LATER_H = 30
"""The B19 clock's hour from which a route that said not now taps the book: about two of sharp's visits after the ask."""
JOBS = ("j_drag_marks", "j_show_fish")
JOB_NO = {"sharp": "j_show_fish"}
"""Lucy's jobs, each answered yes when it shows, but for the one each route here declines."""


def book_later(then: Callable[[View, Save, Rules], Move | None] | None) -> Callable[[View, Save, Rules], Move | None]:
    """The book tapped by hand, once shown, unmade and its hour come, with the hands free; else `then`'s move."""
    def moves(v: View, save: Save, rules: Rules) -> Move | None:
        shown = next((c for c in v.cards if c.card == BIND_BOOK), None)
        if (shown is not None and shown.blocker is None and completions(save, rules, BIND_BOOK) == 0
                and BIND_BOOK not in queued(save) and lane_free(v, "hands")
                and store_value(save, StoreId("sorrel_clock")) >= units(BOOK_LATER_H)):
            return "tap", (TapCard(BIND_BOOK),)
        return then(v, save, rules) if then is not None else None
    return moves


def queued(save: Save) -> set[CardId]:
    return {e.verb.card for e in save.queue if isinstance(e.verb, TapCard)}


def day_twenty_three(route: str) -> Later:
    """B19's visit to B20's: day twenty-two's sinks, rules, split and shares carried on, O-fiddle by the route's answer
    (or the kind's rule), the post by its order card, O-book and Lucy's jobs answered when they show (sharp's not now
    made good later), and A39 queued When ready once shown."""
    twentytwo = day_twenty_two(route)
    fiddle = (OfferId("o_fiddle"), FIDDLE.get(route, FIDDLE["typical"]))
    no = JOB_NO.get(route)
    asks = ((OfferId("o_book"), BOOK.get(route, BOOK["typical"])),
            *((OfferId(j), AnswerId(f"{j}_{'no' if j == no else 'yes'}")) for j in JOBS))
    return Later(
        start="B19", stop="B20",
        sinks=Chapter(trips=twentytwo.sinks.trips, comforts=twentytwo.sinks.comforts,
                      arrivals=(*twentytwo.sinks.arrivals, fiddle)),
        steps=(GO_WALLOW,), order_cards=(*twentytwo.order_cards, *w2.order_cards(stores=("charwood",))),
        keeps=twentytwo.keeps, landed=TWENTY_THREE.of,
        news=("SL31", "I5", "O-fiddle", "I6", "O-book", "SL32", "I7", "SL33", "A39", "B20"),
        answers=(*twentytwo.answers, *asks), shares=twentytwo.shares, cures=twentytwo.cures,
        own=book_later(twentytwo.own), queued=(GO_WALLOW,), chip_rules=twentytwo.chip_rules)
