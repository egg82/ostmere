"""Day three's content as the simulator reads it: the rules with the chapters in writing (IN_WRITING, day_three.toml)
merged after the shipped ones, as tests/opening/test_day_two.py loads them; which content step is which of day three's
story ids, read off a save; and the chapter as the routes play it (chapter.Later). Ids only (CLAUDE.md, "Never spoil
the owner")."""
from functools import cache

from ashfall_app.engine import (
    AnswerId, AtLeast, CardId, OfferId, Order, QUANTITY_SCALE, Rules, StoreId, StoreValue, TapCard, Unlock, UnlockKind, ceil_div,
)
from ashfall_app.opening.convert import condition
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, OPENING, Opening, load_opening, to_rules
from tests.daythree.chapter import Keep, Landings, Later
from tests.dayone.sinks import Chapter, Trip

TRIGGERED = {"K2": ("t_stream",), "K3": ("t_night_3",), "K5": ("t_joins",),
             "SL1": ("t_morning_4",), "SL3": ("t_watch_lit",), "SL4": ("t_scrap_ask",)}
"""Story ids that land when one of these triggers fires."""
STEPS = {"A22": ("walk_edge",), "K1": ("walk_edge",), "K4": ("track_end",), "A23": ("make_bay", "n2_build_bay"),
         "A20": ("bank_hearth",),
         "B5": ("bank_hearth",)}
"""Story ids that land at the first completion of one of these cards (A23: whoever builds the bay)."""
STAGES = {"SL2": ("larder_floor", 3), "SL5": ("rack_roof", 2)}
"""Story ids that land at a comfort's nth completion."""
OFFERS = {"O-stay": OfferId("o_stay"), "SL6": OfferId("o_bank")}
"""Story ids that land when the offer shows."""
STORY = ("B4", "K1", "K2", "K3", "K4", "K5", "B5")
"""Day three's beats in their authored order (beats.yaml, day_three:)."""
SIDE = ("SL1", "SL2", "SL3", "SL4", "SL5", "SL6")
TRACK, DAMP_WOOD = CardId("field_track"), StoreId("damp_wood")
DRYING = CardId("lay_to_dry")
TRACK_DAMP = Trip(TRACK, DAMP_WOOD, reserve_for=(DRYING,))
"""The track in the mix on damp wood, with a reserve of the store kept for the drying wall, which takes it on its own
lane: drunk dry, the wall stops and dry wood runs short under a tap that takes it."""
COMFORTS = tuple(CardId(c) for c in ("larder_floor", "rack_roof", "watch_fire", "clay_hearth", "wood_stack",
                                          "pot_shelf"))
"""The comforts, queued When ready a stage at a time (the hearth's courses among them: each waits on the last cure)."""
ANSWERS = ((OfferId("o_stay"), AnswerId("o_stay_room")), (OfferId("o_bank"), AnswerId("o_bank_hers")))
ORDER_STORES = ("clay",)
"""Stores whose order card a route that takes rules sets once offered."""
KEPT = (("stew", "stew", 9), ("dig_clay", "clay", 0))
"""Tapped by hand while low, each up to the larger of its floor and the most any card or trigger of the content asks of
the store (need): stew, which the town eats from K5 and no gate reads, to a floor of 9 items, the level the routes were
paced on; and clay (a route without its order card digs by hand), to its need."""


@cache
def opening3() -> Opening:
    return load_opening(OPENING, (*CHAPTERS, *IN_WRITING))


@cache
def rules3() -> Rules:
    """One Rules object for every day-three run: the engine caches by the rules' identity."""
    return to_rules(opening3())


def need(rules: Rules, store: StoreId) -> int:
    """The most of `store`, in items, that one card takes as an input or one trigger waits for."""
    asked = [a.quantity for c in rules.cards for a in c.inputs if a.store == store]
    asked += [t.when.value for t in rules.triggers
              if isinstance(t.when, AtLeast) and t.when.subject == StoreValue(store)]
    return ceil_div(max(asked, default=0), QUANTITY_SCALE)


LANDINGS = Landings(TRIGGERED, STEPS, STAGES, OFFERS)


def keeps() -> tuple[Keep, ...]:
    return tuple(Keep(CardId(card), StoreId(store), max(floor, need(rules3(), StoreId(store)))) for card, store, floor in KEPT)


def order_cards(op: Opening) -> tuple[tuple[Unlock, Order], ...]:
    """The chapter's order cards that tap a card once offered, as the page fills them in (opening/convert.py)."""
    cards = {c.id for c in op.cards}
    out: list[tuple[Unlock, Order]] = []
    for oc in op.order_cards:
        if oc.store in ORDER_STORES and oc.tap_card is not None and oc.offered_after is not None:
            after = Unlock(UnlockKind(oc.offered_after.unlock_kind), oc.offered_after.id)
            out.append((after, Order(condition(oc.when, cards), TapCard(CardId(oc.tap_card)))))
    return tuple(out)


@cache
def day_three() -> Later:
    return Later(
        start="B4", stop="B5",
        sinks=Chapter(trips=(TRACK_DAMP,), comforts=COMFORTS, arrivals=ANSWERS,
                      first=(CardId("clay_hearth"),)),
        steps=(CardId("walk_edge"), CardId("track_end"), CardId("bank_hearth")),
        order_cards=order_cards(opening3()),
        keeps=keeps(),
        landed=LANDINGS.of, news=(*STORY, *SIDE))

