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


TWENTY_FIVE = Landings(
    {"I8": ("t_bowl_set",), "SL34": ("t_second_wake",), "SL35": ("t_sister_road",), "I10": ("t_thanks",), "B21": ("t_b21",)},
    {}, {}, {"I9": OfferId("o_walkers"), "O-walkers": OfferId("o_walkers"), "O-widowers": OfferId("o_widowers")})
"""I9 is its offer's showing (the offer carries the beat's lines)."""
HUNT_BOAR, POST_DOOR = CardId("hunt_boar"), CardId("post_door")
BOAR_SHARE = {"typical": 2000, "sharp": 2500}
"""The hands' share of the boar hunt a route sets once shown (I8): the pooled fight in the mix by the route's choice
(week-four-plan item 7; a route not named follows typical)."""
WALKERS = {"typical": AnswerId("o_walkers_food"), "sharp": AnswerId("o_walkers_build")}
WIDOWERS = {"typical": AnswerId("o_widowers_build"), "sharp": AnswerId("o_widowers_food")}
"""Where each group works first, as each route answers (a route not named follows typical): both answers measured on
each offer. The whenever player's kind rule, set in week three, answers them."""
LATER_JOBS = ("j_midden", "j_leaning_wall", "j_steam_hole")
LATER_JOB_NO = {"sharp": "j_leaning_wall"}
"""Lucy's jobs from B20, each answered yes when it shows, but for the one each route here declines."""


def day_twenty_five(route: str) -> Later:
    """B20's visit to B21's: day twenty-three's sinks, rules, split and shares carried on, the boar hunt at the route's
    share once shown, the walkers and widowers by the route's answers (or the kind's rule), Lucy's jobs answered when
    they show, and the post's door tapped once ready."""
    twentythree = day_twenty_three(route)
    groups = ((OfferId("o_walkers"), WALKERS.get(route, WALKERS["typical"])),
              (OfferId("o_widowers"), WIDOWERS.get(route, WIDOWERS["typical"])))
    no = LATER_JOB_NO.get(route)
    jobs = tuple((OfferId(j), AnswerId(f"{j}_{'no' if j == no else 'yes'}")) for j in LATER_JOBS)
    return Later(
        start="B20", stop="B21",
        sinks=Chapter(trips=twentythree.sinks.trips, comforts=twentythree.sinks.comforts,
                      arrivals=(*twentythree.sinks.arrivals, *groups)),
        steps=(POST_DOOR,), order_cards=twentythree.order_cards, keeps=twentythree.keeps, landed=TWENTY_FIVE.of,
        news=("I8", "I9", "O-walkers", "SL34", "SL35", "I10", "O-widowers", "B21"),
        answers=(*twentythree.answers, *jobs),
        shares=(*twentythree.shares, Share(HUNT_BOAR, BOAR_SHARE.get(route, BOAR_SHARE["typical"]))),
        cures=twentythree.cures, own=twentythree.own, chip_rules=twentythree.chip_rules)


TWENTY_SEVEN = Landings(
    {"I11": ("t_board",), "SL36": ("t_hands",), "I12": ("t_names_given",), "I13": ("t_i13",)},
    {"A40": ("sit_names",)}, {}, {})
SIT_NAMES, FAR_SNARES = CardId("sit_names"), CardId("far_snares")
LAST_JOB = "j_far_snares"
LAST_JOB_NO = {"sharp": LAST_JOB}
"""Lucy's last job, answered yes when it shows, but by the route here that declines it, so both answers are measured.
Its yes shows the job without queuing it (D-176), so a route taps it once it is ready."""


def day_twenty_seven(route: str) -> Later:
    """B21's visit to I13's, week four's last: day twenty-five's sinks, rules, split and shares carried on, Lucy's last
    job answered when it shows and tapped once ready, and A40 queued When ready once shown."""
    twentyfive = day_twenty_five(route)
    job = (OfferId(LAST_JOB), AnswerId(f"{LAST_JOB}_{'no' if LAST_JOB_NO.get(route) == LAST_JOB else 'yes'}"))
    return Later(
        start="B21", stop="I13",
        sinks=twentyfive.sinks, steps=(FAR_SNARES,), order_cards=twentyfive.order_cards, keeps=twentyfive.keeps,
        landed=TWENTY_SEVEN.of, news=("I11", "SL36", "I12", "A40", "I13"),
        answers=(*twentyfive.answers, job), shares=twentyfive.shares, cures=twentyfive.cures, own=twentyfive.own,
        queued=(SIT_NAMES,), chip_rules=twentyfive.chip_rules)
