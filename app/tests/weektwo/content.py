"""Days eight, nine, eleven, twelve, fifteen, sixteen, eighteen and nineteen as the routes play them (daythree/chapter.Later): which content step is which story id, read off a save,
and the chapter's sinks, order cards, shares and each route's split of the town, on the rules day three loads (every
chapter in writing merged). Ids only (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import (
    BP, AfterTime, AnswerId, CardId, OfferId, Order, Rules, Save, StoreId, TapCard, Unlock, UnlockKind,
    View,
)
from ashfall_app.engine.rates import store_value
from tests.daythree import content as c3
from tests.daythree.chapter import Landings, Later, Share
from tests.dayone.policy import Move
from tests.dayone.sinks import Chapter, Trip
from tests.weekone import content as w1
from tests.weektwo import policy as p8
from tests.weektwo.policy import Split, WeekTwoKnobs, answer, card, feature

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
"""B13 too, the next chapter's: a route away over the turn sees S4 and B13 in one visit."""
FIFTEEN = Landings(
    {"B13": ("t_b13",), "SL22": ("t_sow",), "T1": ("t_frost",), "T2": ("t_deer",), "SL23": ("t_beams",),
     "T3": ("t_walls",), "B14": ("t_b14",)}, {}, {}, {})
SIXTEEN = Landings(
    {"T4": ("t_rows_black",), "SL24": ("t_road_marked",), "SL25": ("t_hall_hearth",), "T5": ("t_rime_ring",),
     "T6": ("t_covers_torn",), "SL26": ("t_sun_back",), "B15": ("t_b15",)},
    {"A36": ("mark_road", "n2_mark_road"), "A35": ("try_stone",)}, {}, {"O-road": OfferId("o_road")})
EIGHTEEN = Landings(
    {"SL27": ("t_first_working",), "T8": ("t_pot_out",), "arr15": ("t_starer",), "B16": ("t_b16",)}, {}, {},
    {"T7": OfferId("o_choir"), "O-choir": OfferId("o_choir"), "T9": OfferId("o_cutter"), "O-cutter": OfferId("o_cutter")})
"""T7 and T9 are their offers' showing (each offer carries its beat's lines); arr15 the fifteenth arrival."""
NINETEEN = Landings(
    {"T10": ("t_far_hills",), "T11": ("t_cut_night",), "SL28": ("t_cloth",), "B17": ("t_b17",), "T12": ("t_lamp_out",),
     "T13": ("t_t13",)},
    {"A38": ("sit_road_end",)}, {}, {"O-sun": OfferId("o_last_sun")})
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
ORDER_STORES_SIXTEEN = ("cleared",)
"""Day sixteen's: the road's. The working's rule on the frost is on rime, so day fifteen's set it once offered."""
ROAD = {"typical": AnswerId("o_road_you"), "sharp": AnswerId("o_road_n2")}
"""Who walks the old road, as each route answers it (a route not named follows typical): both answers measured."""
JOBS = ("j_steps", "j_smoke_hole", "j_wedged", "j_snares", "j_ridge", "j_tally")
JOB_NO = {"sharp": "j_ridge"}
"""Lucy's jobs, each answered yes when it shows, but for the one each route here declines, so both answers are
measured (week-three-plan item 6)."""
TRY_STONE, SHOVEL_ROAD = CardId("try_stone"), CardId("shovel_road")
SHOVEL = {"typical": 1000, "sharp": 2000}
"""The hands' share of shovelling the road a route adds once shown (SL24); a route not named follows typical."""
PULL_BEAMS, HUNT_DEER = CardId("pull_beams"), CardId("hunt_deer")
CORDWOOD = CardId("stack_cordwood")
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
POT_FUNGUS = (Unlock(UnlockKind.CARD, CardId("pot_fungus_stew")),
              Order(AfterTime(0), TapCard(CardId("pot_fungus_stew")), or_else=(TapCard(CardId("pot_stew")),)))
"""The pot the route cooks for on the fire once there is a second kind, the first kind its fallback, so the camp eats
whichever is stocked with no visit (#473)."""
POT_BARLEY = (Unlock(UnlockKind.CARD, CardId("pot_barley_stew")),
              Order(AfterTime(0), TapCard(CardId("pot_barley_stew")),
                    or_else=(TapCard(CardId("pot_fungus_stew")), TapCard(CardId("pot_stew")))))
"""The barley pot on, as the route cooks it on full barley (day fifteen), the others its fallbacks."""

F, H = "g_field_", "g_hearth_"
N5, N7, N4, N6 = {F + "forage": BP}, {F + "pick": BP}, {H + "watch": BP}, {H + "watch": BP}
"""Each person's own split before the crews, as the routes played it (a crew's split at a moment is the mean of its
members' here, so each card keeps its person-time): her forager's, her picker's, the two watchers'."""
N2_FORAGE_WATCH = {F + "forage": BP // 2, F + "watch": BP // 2}
N2_WATCH, N2_WATCH_ROAD = {F + "watch": BP}, {F + "watch": BP // 2, F + "clear_road": BP // 2}
ROAD_FIELD, ROAD_HEARTH = {F + "clear_road": BP}, {H + "clear_road": BP}
REAP_FIELD, REAP_HEARTH = {F + "reap": BP}, {H + "reap": BP}
REAP_FORAGE_FIELD, REAP_FORAGE_HEARTH = {F + "reap": BP // 2, F + "forage": BP // 2}, {H + "reap": BP // 2, H + "forage": BP // 2}
WALK_FORAGE_TYPICAL, WALK_FORAGE_SHARP = ({F + "walk_ashwood": 2500, F + "forage": 7500},
                                          {F + "walk_ashwood": BP // 2, F + "forage": BP // 2})
"""The newcomers' own splits as each answer and the open road left them: whole on the card the answer joined them with,
the reaping and foraging halves from the road's opening, the Ashwood walk's share beside the roots."""


def crew(*members: dict[str, int]) -> tuple[tuple[str, int], ...]:
    """A crew's split: the mean of its members' shares, each card floored and the remainder on the last card."""
    total: dict[str, int] = {}
    for m in members:
        assert sum(m.values()) == BP, m
        for card_id, bp in m.items():
            total[card_id] = total.get(card_id, 0) + bp
    shares = {c: t // len(members) for c, t in total.items()}
    shares[list(shares)[-1]] += BP - sum(shares.values())
    return tuple(shares.items())


TYPICAL = WeekTwoKnobs(
    splits=(
        Split("n2", (("n2_forage", 5000), ("n2_stakes", 5000)), card("palisade")),
        Split("n3", (("n3_forage", 5000), ("n3_pick", 5000)), feature("drift")),
        Split("n3", (("n3_forage", 4000), ("n3_pick", 4000), ("n3_ash_ground", 2000)), card("n3_ash_ground")),
        Split("n2", (("n2_forage", 2500), ("n2_stakes", 5000), ("n2_watch", 2500)), Unlock(UnlockKind.ACTION, "pack")),
        Split("n2", (("n2_stakes", 5000), ("n2_watch", 5000)), Unlock(UnlockKind.ACTION, "e2_strip")),
        Split("n2", (("n2_forage", 5000), ("n2_watch", 5000)), feature("ring_closed")),
        Split("n2", (("n2_stakes", 5000), ("n2_watch", 5000)), card("make_hut")),
        Split("g_field", crew(N2_FORAGE_WATCH, N5, N7), feature("family_joined")),
        Split("g_hearth", crew(N4, N6), feature("family_joined")),
        Split("g_field", crew(N2_WATCH_ROAD, N5, N7), feature("road_marked")),
        Split("g_field", crew(N2_WATCH_ROAD, N5, N7, ROAD_FIELD), answer("o_choir_road")),
        Split("g_hearth", crew(N4, N6, ROAD_HEARTH, ROAD_HEARTH), answer("o_choir_road")),
        Split("g_field", crew(N2_WATCH_ROAD, N5, N7, ROAD_FIELD, REAP_FIELD), answer("o_cutter_beds")),
        Split("g_hearth", crew(N4, N6, ROAD_HEARTH, ROAD_HEARTH, ROAD_HEARTH), answer("o_cutter_beds")),
        Split("g_field", crew(N2_FORAGE_WATCH, N5, N7, REAP_FORAGE_FIELD, REAP_FIELD), feature("r2_open")),
        Split("g_hearth", crew(N4, N6, REAP_FORAGE_HEARTH, REAP_FORAGE_HEARTH), feature("r2_open")),
        Split("g_field", crew(N2_FORAGE_WATCH, N5, N7, WALK_FORAGE_TYPICAL, REAP_FIELD), feature("ashwood")),
        Split("n13", (("n13_walk_ashwood", 5000), ("n13_forage", 5000)), feature("sorrel_named")),
        Split("g_road", (("g_road_fog_fish", 5000), ("g_road_fungus_stew", 5000)), answer("o_fiddle_food")),
        Split("g_road", (("g_road_fog_fish", 1667), ("g_road_fungus_stew", 8333)), answer("o_walkers_food")),
        Split("g_road", (("g_road_fog_fish", 1111), ("g_road_fungus_stew", 5556), ("g_road_stakes", 3333)), answer("o_widowers_build")),
    ))
"""The town's split, moment by moment (week-two-numbers.md, "The bigger thing in each typical visit"). Her lane stays on
its rules: she is the town's forager, and the track's roots need her (moving her to stakes starves roots, and the
hands' roots rule then taps every few seconds). Once the pack has come in round the open side (E2) his foraging goes to
the watch; once the ring is closed his stakes go back to foraging, until the hut is asked for (B10's offer answered by
the hands) and done (Z1). A group's split at each moment is the mean, over its members then, of the shares each had
on their own split before groups (so each card keeps its person-time; n7's was all picking). The two early companions
are in the crews from the family's day: n2 with the field crew, n4 at the watch with the hearth crew."""
SHARP = WeekTwoKnobs(
    splits=(
        Split("n2", (("n2_stakes", 10000),), card("palisade")),
        Split("n3", (("n3_forage", 5000), ("n3_pick", 5000)), feature("drift")),
        Split("n3", (("n3_forage", 4000), ("n3_pick", 4000), ("n3_ash_ground", 2000)), card("n3_ash_ground")),
        Split("n2", (("n2_forage", 10000),), feature("ring_closed")),
        Split("n2", (("n2_stakes", 10000),), card("make_hut")),
        Split("g_field", crew(N2_WATCH, N5, N7), feature("family_joined")),
        Split("g_hearth", crew(N4, N6), feature("family_joined")),
        Split("g_field", crew(N2_WATCH_ROAD, N5, N7), feature("road_marked")),
        Split("g_field", crew(N2_WATCH_ROAD, N5, N7, REAP_FIELD), answer("o_choir_beds")),
        Split("g_hearth", crew(N4, N6, REAP_HEARTH, REAP_HEARTH), answer("o_choir_beds")),
        Split("g_field", crew(N2_WATCH_ROAD, N5, N7, REAP_FIELD, ROAD_FIELD), answer("o_cutter_road")),
        Split("g_hearth", crew(N4, N6, REAP_HEARTH, REAP_HEARTH, ROAD_HEARTH), answer("o_cutter_road")),
        Split("g_field", crew(N2_WATCH, N5, N7, REAP_FIELD, REAP_FORAGE_FIELD), feature("r2_open")),
        Split("g_hearth", crew(N4, N6, REAP_HEARTH, REAP_HEARTH), feature("r2_open")),
        Split("g_field", crew(N2_WATCH, N5, N7, REAP_FIELD, WALK_FORAGE_SHARP), feature("ashwood")),
        Split("n13", (("n13_walk_ashwood", 5000), ("n13_fog_fish", 5000)), feature("sorrel_named")),
        Split("g_road", (("g_road_clear_road", 5000), ("g_road_stakes", 5000)), answer("o_fiddle_build")),
        Split("g_road", (("g_road_clear_road", 8333), ("g_road_stakes", 1667)), answer("o_walkers_build")),
        Split("g_road", (("g_road_clear_road", 5556), ("g_road_stakes", 1111), ("g_road_fungus_stew", 3333)), answer("o_widowers_food")),
    ))
"""Once the road is over the top (B17) both routes take the lanes they had clearing it to the beds and the roots; once
the town can walk the Ashwood (B18) one of them walks beside the roots, the beds being over. Crew shares as typical's."""
KNOBS = {"sharp": SHARP}
"""Each route's split; a route not named follows typical."""
HANDS = {"typical": (1500, 0), "sharp": (3000, 0)}
"""The hands' shares of cut_stakes and twist_cord a route adds at G2's visit; a route not named follows typical."""


def order_cards(rules_cards: tuple[tuple[Unlock, Order], ...] = (),
                stores: tuple[str, ...] = ORDER_STORES) -> tuple[tuple[Unlock, Order], ...]:
    """`rules_cards`, and the content's order cards on `stores`, each as the page fills it in, offered after its
    unlock."""
    return (*rules_cards, *c3.order_cards(c3.opening3(), stores))


def cordwood_rule() -> tuple[tuple[Unlock, Order], ...]:
    """Damp wood's sink's order card (day_fifteen.toml, stack_cordwood), offered once woodcutting's first top opens it.
    Of damp wood's order cards only this one: n1_cut's is her first rule, taught on day two."""
    return tuple(x for x in c3.order_cards(c3.opening3(), ("damp_wood",)) if x[1].then == TapCard(CORDWOOD))


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
        steps=(), order_cards=order_cards((*c3.order_cards(c3.opening3()), w1.BED_RULE, POT_FUNGUS)), keeps=c3.keeps(),
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
        steps=(VIGIL,), order_cards=(*nine.order_cards, POSTS_RULE, *order_cards(stores=("smoked",))), keeps=nine.keeps,
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
        steps=(), order_cards=(*order_cards(twelve.order_cards, ORDER_STORES_FIFTEEN), *cordwood_rule(), POT_BARLEY), keeps=twelve.keeps,
        landed=FIFTEEN.of, news=("B13", "SL22", "T1", "T3", "T2", "SL23", "B14"),
        answers=(*twelve.answers, *ASKS_FIFTEEN),
        shares=(*twelve.shares, Share(PULL_BEAMS, BEAMS.get(route, BEAMS["typical"])), Share(HUNT_DEER, DEER_SHARE)),
        cures=twelve.cures, own=twelve.own)


def asks_sixteen(route: str) -> tuple[tuple[OfferId, AnswerId], ...]:
    """O-road as the route answers it, then Lucy's jobs: yes but for the route's one no."""
    no = JOB_NO.get(route)
    return ((OfferId("o_road"), ROAD.get(route, ROAD["typical"])),
            *((OfferId(j), AnswerId(f"{j}_{'no' if j == no else 'yes'}")) for j in JOBS))


def day_sixteen(route: str) -> Later:
    """B14 to B15's visit: day fifteen's sinks, rules and split carried on, the road by its order card and half of his
    lane on clearing its bed once found, the hands shovelling it at a share, the working's rule beside the covers' once
    offered, O-road and the jobs answered when they show, and the field stone tapped the moment it is ready."""
    fifteen = day_fifteen(route)
    return Later(
        start="B14", stop="B15",
        sinks=fifteen.sinks,
        steps=(TRY_STONE,), order_cards=(*fifteen.order_cards, *order_cards(stores=ORDER_STORES_SIXTEEN)),
        keeps=fifteen.keeps,
        landed=SIXTEEN.of, news=("O-road", "A36", "T4", "SL24", "SL25", "T5", "T6", "SL26", "A35", "B15"),
        answers=(*fifteen.answers, *asks_sixteen(route)),
        shares=(*fifteen.shares, Share(SHOVEL_ROAD, SHOVEL.get(route, SHOVEL["typical"]))),
        cures=fifteen.cures, own=fifteen.own)


CHOIR = {"typical": AnswerId("o_choir_road"), "sharp": AnswerId("o_choir_beds")}
CUTTER = {"typical": AnswerId("o_cutter_beds"), "sharp": AnswerId("o_cutter_road")}
"""Where the newcomers go first, as each route answers (a route not named follows typical): both answers of each
measured. The whenever player sets the kind's rule from its first answer, which answers the second."""


def day_eighteen(route: str) -> Later:
    """B15 to B16's visit: day sixteen's sinks, rules, split and shares carried on, and the two arrival offers answered
    when they show; the newcomers' shares are their joins'."""
    sixteen = day_sixteen(route)
    arrivals = ((OfferId("o_choir"), CHOIR.get(route, CHOIR["typical"])),
                (OfferId("o_cutter"), CUTTER.get(route, CUTTER["typical"])))
    return Later(
        start="B15", stop="B16",
        sinks=Chapter(trips=sixteen.sinks.trips, comforts=sixteen.sinks.comforts,
                      arrivals=(*sixteen.sinks.arrivals, *arrivals)),
        steps=(), order_cards=sixteen.order_cards, keeps=sixteen.keeps,
        landed=EIGHTEEN.of, news=("SL27", "T7", "O-choir", "T8", "T9", "O-cutter", "arr15", "B16"),
        answers=sixteen.answers, shares=sixteen.shares, cures=sixteen.cures, own=sixteen.own)


OVER, ROAD_CLOTHS, SIT_ROAD_END = CardId("cut_over"), CardId("road_cloths"), CardId("sit_road_end")
CLOTHS_RULE = (Unlock(UnlockKind.CARD, ROAD_CLOTHS), Order(AfterTime(0), TapCard(ROAD_CLOTHS)))
"""Her cloth on her lane is tied by a rule of the player's once shown (a capped card is never a share), as his posts were."""
LAST_SUN = {"typical": AnswerId("o_last_sun_light"), "sharp": AnswerId("o_last_sun_cellar")}
"""Lucy's question for the season's last days, as each route answers it in the visit it shows (a route not named follows
typical): both answers measured."""


def day_nineteen(route: str) -> Later:
    """B16 to T13's visit, the end of week three: day eighteen's sinks, rules, split and shares carried on (the road over
    the top is its order card's, on cleared), her cloth by a rule once shown, and night 21's step queued When ready once
    it shows. The hands keep their share of shovelling: taking it out once the road is over set the trips' retune
    fighting the shares at two visits, minutes of play each."""
    eighteen = day_eighteen(route)
    last_sun = (OfferId("o_last_sun"), LAST_SUN.get(route, LAST_SUN["typical"]))
    return Later(
        start="B16", stop="T13",
        sinks=eighteen.sinks,
        steps=(SIT_ROAD_END,), order_cards=(*eighteen.order_cards, CLOTHS_RULE), keeps=eighteen.keeps,
        landed=NINETEEN.of, news=("T10", "T11", "SL28", "B17", "T12", "O-sun", "A38", "T13"),
        answers=(*eighteen.answers, last_sun), shares=eighteen.shares, cures=eighteen.cures, own=eighteen.own, queued=(SIT_ROAD_END,))
