"""Days eight, nine, eleven, twelve and fifteen as the routes play them (daythree/chapter.Later): which content step is which story id, read off a save,
and the chapter's sinks, order cards, shares and each route's split of the town, on the rules day three loads (every
chapter in writing merged). Ids only (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import (
    AfterTime, AnswerId, CardId, OfferId, Order, Rules, Save, StoreId, TapCard, Unlock, UnlockKind, View,
)
from ashfall_app.engine.rates import store_value
from ashfall_app.opening.convert import condition
from tests.daythree import content as c3
from tests.daythree.chapter import Landings, Later, Share
from tests.dayone.policy import Move
from tests.dayone.sinks import Chapter, Trip
from tests.weekone import content as w1
from tests.weektwo import policy as p8
from tests.weektwo.policy import Split, WeekTwoKnobs, card, feature

PALISADE, HIDE_FLAPS = CardId("palisade"), CardId("hide_flaps")
EIGHT = Landings(
    {"B8": ("t_b8",), "U1": ("t_howls",), "U2": ("t_caps",), "SL15": ("t_ash_ground",), "SL16": ("t_cord",),
     "U3": ("t_pack",), "B9": ("t_b9",)}, {}, {}, {})
NINE = Landings(
    {"E1": ("t_ring",), "SL18": ("t_gap_fire",), "SL17": ("t_old_wire",), "E2": ("t_open_side",), "E3": ("t_smoke",),
     "B10": ("t_b10",)}, {}, {}, {})
ELEVEN = Landings(
    {"Z1": ("t_family_joins",), "Z2": ("t_guard_n2", "t_guard_n7"), "SL19": ("t_posts",), "Z3": ("t_count",),
     "B11": ("t_b11",)},
    {"A31": ("keep_vigil",)}, {}, {"O-family": OfferId("o_family"), "O-guard": OfferId("o_guard")})
VIGIL, POSTS = CardId("keep_vigil"), CardId("n6_posts")
TWELVE = Landings(
    {"S1": ("t_s1",), "SL20": ("t_bear_sign",), "S2": ("t_s2",), "B12": ("t_b12",), "SL21": ("t_lamps",),
     "S3": ("t_sitter",), "N14": ("t_night_14",), "S4": ("t_s4",), "B13": ("t_b13",)},
    {"A32": ("sit_last_night",)}, {}, {})
"""B13 too, the next chapter's: a route away over the turn sees S4 and B13 in one visit, and B13's days note is held
to B13's landing."""
FIFTEEN = Landings(
    {"B13": ("t_b13",), "SL22": ("t_sow",), "T1": ("t_frost",), "T2": ("t_deer",), "SL23": ("t_beams",),
     "T3": ("t_walls",), "B14": ("t_b14",)}, {}, {}, {})
LAST_NIGHT, HUNT_BEAR, BEAR_SIGN = CardId("sit_last_night"), CardId("hunt_bear"), StoreId("bear_sign")
CUT_STAKES = CardId("cut_stakes")
ORDER_STORES = ("stakes", "roof_ash", "cord", "pelt", "wind_torn", "stones", "tallow")
"""The stores whose content order cards a route that takes rules sets once offered: the builds', the two chips', the
old man's cord and the lamps'."""
ORDER_STORES_FIFTEEN = ("ashed_ground", "ripe", "rime")
"""Day fifteen's besides (the hall's is on stakes): her sowing, her reaping and her covers."""
ASKS_EIGHT = ((OfferId("o_posts"), AnswerId("o_posts_cord")),)
"""The camp's ask that lands in day eight's stretch (day_nine.toml, "the camp's asks"), as every route answers it."""
ASKS_NINE = tuple((OfferId(o), AnswerId(a)) for o, a in (
    ("o_margin", "o_margin_gap"), ("o_rack", "o_rack_high"), ("o_deep", "o_deep_pace"), ("o_bark", "o_bark_tinder"),
    ("o_footing", "o_footing_hearth"), ("o_fed", "o_fed_pot"), ("o_lookout", "o_lookout_wall"),
    ("o_gate", "o_gate_road"), ("o_skin", "o_skin_flaps")))
"""Day nine's asks, as every route answers them: one a return from E2 (content/team/week-two.md, "The asks")."""
ARRIVAL_ELEVEN = (OfferId("o_family"), AnswerId("o_family_room"))
"""The family's offer as a route that lets newcomers stay answers it; the kind's rule takes the role of the first."""
GUARD = (OfferId("o_guard"), AnswerId("o_guard_n7"))
"""Who stands the gap, as every route answers it, in the visit it shows."""
ASKS_ELEVEN = tuple((OfferId(o), AnswerId(a)) for o, a in (("o_door", "o_door_gate"), ("o_pot", "o_pot_hang"),
                                                          ("o_ditch", "o_ditch_dig")))
"""Day eleven's asks while the hut goes up, as every route answers them: the door to the gate, the pot hung, the ditch
dug."""
ASKS_TWELVE = tuple((OfferId(o), AnswerId(a)) for o, a in (
    ("o_spoil", "o_spoil_ring"), ("o_cradle", "o_cradle_fire"), ("o_shaft", "o_shaft_bind"),
    ("o_cold_air", "o_cold_air_meat"), ("o_lean_to", "o_lean_to_wood"), ("o_lye", "o_lye_bedding"),
    ("o_wet", "o_wet_drain"), ("o_crows", "o_crows_be"), ("o_sag", "o_sag_prop")))
"""Day twelve's asks while the cellar goes down, as every route answers them (content/team/week-two.md, "The asks (day
twelve)")."""
ASKS_FIFTEEN = ((OfferId("o_sun_rack"), AnswerId("o_sun_rack_sun")), (OfferId("o_door_ice"), AnswerId("o_door_ice_shave")))
"""Day fifteen's two asks, as every route answers them."""
PULL_BEAMS, HUNT_DEER = CardId("pull_beams"), CardId("hunt_deer")
BEAMS = {"typical": 1500, "sharp": 3000}
"""The hands' share of pulling beams a route adds once shown (S4's visit); a route not named follows typical. The ruin's
pool is finite, so its share yields once it is spent (decisions.md, "A mix keeps going without a dry store")."""
DEER_SHARE = 1000
"""The hands' share a route gives the deer hunt once shown (T2); its pool is finite too."""
STEW_BARLEY = Trip(CardId("barley_stew"), StoreId("barley"), share_bp=1000)
"""The pot in the mix on full barley, as fungus's."""
BEAR_SHARE = 1500
"""The hands' share a route that hunts the bear gives it once shown (12b), as the wolf hunt's."""
POSTS_RULE = (Unlock(UnlockKind.CARD, POSTS), Order(AfterTime(0), TapCard(POSTS)))
"""His posts on his lane are built by a rule of the player's (a capped card is never a share), as her bed was."""
STEW_FUNGUS = Trip(CardId("fungus_stew"), StoreId("fungus"), share_bp=1000)
"""The pot in the mix on full fungus (8a)."""

TYPICAL = WeekTwoKnobs(
    splits=(
        Split("n2", (("n2_forage", 5000), ("n2_stakes", 5000)), card("palisade")),
        Split("n3", (("n3_forage", 5000), ("n3_pick", 5000)), feature("drift")),
        Split("n3", (("n3_forage", 4000), ("n3_pick", 4000), ("n3_ash_ground", 2000)), card("n3_ash_ground")),
        Split("n2", (("n2_forage", 2500), ("n2_stakes", 5000), ("n2_watch", 2500)), Unlock(UnlockKind.ACTION, "pack")),
        Split("n2", (("n2_stakes", 5000), ("n2_watch", 5000)), Unlock(UnlockKind.ACTION, "e2_strip")),
        Split("n2", (("n2_forage", 5000), ("n2_watch", 5000)), feature("ring_closed")),
        Split("n2", (("n2_stakes", 5000), ("n2_watch", 5000)), card("make_hut")),
        Split("n2", (("n2_forage", 5000), ("n2_watch", 5000)), feature("family_joined")),
    ))
"""The town's split, moment by moment (week-two-numbers.md, "The bigger thing in each typical visit"). Her lane stays on
its rules: she is the town's forager, and the track's roots need her (moving her to stakes starves roots, and the
hands' roots rule then taps every few seconds). Once the pack has come in round the open side (E2) his foraging goes to
the watch; once the ring is closed his stakes go back to foraging, until the hut is asked for (B10's offer answered by
the hands) and done (Z1)."""
SHARP = WeekTwoKnobs(
    splits=(
        Split("n2", (("n2_stakes", 10000),), card("palisade")),
        Split("n3", (("n3_forage", 5000), ("n3_pick", 5000)), feature("drift")),
        Split("n3", (("n3_forage", 4000), ("n3_pick", 4000), ("n3_ash_ground", 2000)), card("n3_ash_ground")),
        Split("n2", (("n2_forage", 10000),), feature("ring_closed")),
        Split("n2", (("n2_stakes", 10000),), card("make_hut")),
        Split("n2", (("n2_watch", 10000),), feature("family_joined")),
    ))
KNOBS = {"sharp": SHARP}
"""Each route's split; a route not named follows typical."""
HANDS = {"typical": (1500, 0), "sharp": (3000, 0)}
"""The hands' shares of cut_stakes and twist_cord a route adds at G2's visit; a route not named follows typical."""


def order_cards(rules_cards: tuple[tuple[Unlock, Order], ...] = (),
                stores: tuple[str, ...] = ORDER_STORES) -> tuple[tuple[Unlock, Order], ...]:
    """`rules_cards`, and the content's order cards on `stores`, each as the page fills it in, offered after its
    unlock."""
    op = c3.opening3()
    cards = {c.id for c in op.cards}
    out = list(rules_cards)
    for oc in op.order_cards:
        if oc.store in stores and oc.tap_card is not None and oc.offered_after is not None:
            after = Unlock(UnlockKind(oc.offered_after.unlock_kind), oc.offered_after.id)
            out.append((after, Order(condition(oc.when, cards), TapCard(CardId(oc.tap_card)))))
    return tuple(out)


def own(knobs: WeekTwoKnobs):
    def moves(v: View, save: Save, rules: Rules) -> Move | None:
        return p8.move(v, save, rules, knobs)
    return moves


def day_eight(route: str) -> Later:
    stakes, cord = HANDS.get(route, HANDS["typical"])
    return Later(
        start="G2", stop="B9",
        sinks=Chapter(trips=(w1.STONE_DAMP, w1.TRACK_STONES, STEW_FUNGUS),
                      comforts=(*c3.COMFORTS, w1.WOODSHED, w1.HEARTH_STONES, w1.SPEAR, w1.BEDDING),
                      arrivals=w1.ANSWERS),
        steps=(), order_cards=order_cards((*c3.order_cards(c3.opening3()), w1.BED_RULE)), keeps=c3.keeps(),
        landed=EIGHT.of, news=("B8", "U1", "U2", "SL15", "SL16", "U3", "B9"), answers=ASKS_EIGHT,
        shares=(Share(w1.HUNT, 1500), Share(CardId("cut_stakes"), stakes),
                *((Share(CardId("twist_cord"), cord),) if cord else ())),
        cures=w1.day_six().cures, own=own(KNOBS.get(route, TYPICAL)))


def day_nine(route: str) -> Later:
    """B9 to B10's visit: day eight's sinks, rules and split carried on (the gap fire is its order card's, in ORDER_STORES)
    and the fourth snare paid the moment it is ready."""
    eight = day_eight(route)
    return Later(
        start="B9", stop="B10",
        sinks=eight.sinks,
        steps=(CardId("set_snare_4"),), order_cards=eight.order_cards, keeps=eight.keeps,
        landed=NINE.of, news=("E1", "SL18", "SL17", "E2", "E3", "B10"), answers=(*eight.answers, *ASKS_NINE),
        shares=eight.shares, cures=eight.cures, own=eight.own)


def day_eleven(route: str) -> Later:
    """B10 to B11's visit: day nine's sinks, rules and split carried on, the family's offer among the arrivals, who
    guards answered when it shows, his posts by a rule, and the vigil queued When ready once it shows (Later.queued)."""
    nine = day_nine(route)
    return Later(
        start="B10", stop="B11",
        sinks=Chapter(trips=nine.sinks.trips, comforts=nine.sinks.comforts, arrivals=(*nine.sinks.arrivals, ARRIVAL_ELEVEN)),
        steps=(VIGIL,), order_cards=(*nine.order_cards, POSTS_RULE), keeps=nine.keeps,
        landed=ELEVEN.of, news=("O-family", "Z1", "O-guard", "Z2", "SL19", "Z3", "A31", "B11"),
        answers=(*nine.answers, *ASKS_ELEVEN, GUARD), shares=nine.shares, cures=nine.cures, own=nine.own, queued=(VIGIL,))


def sign_spent(save: Save) -> bool:
    return store_value(save, BEAR_SIGN) == 0


def cellar_dug(save: Save) -> bool:
    return feature("cellar") in set(save.unlocked)


def day_twelve(route: str) -> Later:
    """B11 to S4's visit: day eleven's sinks, rules and split carried on (the dig and the lamps are their order cards',
    in ORDER_STORES), day twelve's asks, the bear hunted at a share once shown and taken out once its sign is spent, the
    hands' stakes taken out once the cellar is dug (12d: nothing after it takes stakes but the lamps' few), and the last
    night queued When ready once it shows."""
    eleven = day_eleven(route)
    shares = tuple(Share(s.card, s.share_bp, cellar_dug) if s.card == CUT_STAKES else s for s in eleven.shares)
    return Later(
        start="B11", stop="S4",
        sinks=eleven.sinks,
        steps=(LAST_NIGHT,), order_cards=eleven.order_cards, keeps=eleven.keeps,
        landed=TWELVE.of, news=("S1", "SL20", "S2", "B12", "SL21", "S3", "A32", "S4"),
        answers=(*eleven.answers, *ASKS_TWELVE), shares=(*shares, Share(HUNT_BEAR, BEAR_SHARE, sign_spent)),
        cures=eleven.cures, own=eleven.own, queued=(LAST_NIGHT,))


def day_fifteen(route: str) -> Later:
    """S4's visit to B14's: day twelve's sinks, rules and split carried on (the hall is its order card's, on stakes),
    her sowing, reaping and covers by their order cards, beams and the deer hunt in the hands' mix once shown, the pot
    against full barley, and both asks answered when they show."""
    twelve = day_twelve(route)
    return Later(
        start="S4", stop="B14",
        sinks=Chapter(trips=(*twelve.sinks.trips, STEW_BARLEY), comforts=twelve.sinks.comforts,
                      arrivals=twelve.sinks.arrivals),
        steps=(), order_cards=order_cards(twelve.order_cards, ORDER_STORES_FIFTEEN), keeps=twelve.keeps,
        landed=FIFTEEN.of, news=("B13", "SL22", "T1", "T3", "T2", "SL23", "B14"),
        answers=(*twelve.answers, *ASKS_FIFTEEN),
        shares=(*twelve.shares, Share(PULL_BEAMS, BEAMS.get(route, BEAMS["typical"])), Share(HUNT_DEER, DEER_SHARE)),
        cures=twelve.cures, own=twelve.own)
