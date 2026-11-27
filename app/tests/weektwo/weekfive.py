"""Week five's chapters as the routes play them (daythree/chapter.Later), played on from week four's end by the same
players (tests/weekfive/policy.py `later`): which content step is which story id, read off a save, and what each
chapter's Week names for the policies. Ids only (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import AnswerId, CardId, OfferId, StoreId
from tests.daythree.chapter import Keep, Landings, Later
from tests.weekfive.policy import CastCard, RouteShare, TwoAnswer, Week, chip_cure, later
from tests.dayone.player.sinks import SINKS
from tests.weektwo import weekfour as w4

TWENTY_NINE = Landings(
    {"Y1": ("t_y1",), "SL37": ("t_fiddle_plays",), "Y2": ("t_post_prints",), "Y3": ("t_pin",), "B22": ("t_b22",)},
    {"A41": ("first_run",)}, {}, {"O-first-run": OfferId("o_first_run")})
FIRST_RUN, RUN_CART, WALK_HILL = CardId("first_run"), CardId("run_cart"), CardId("walk_hill")
FIRST_RUN_OFFER = OfferId("o_first_run")
FIRST_RUN_ANSWERS = {"typical": AnswerId("o_first_run_yes"), "sharp": AnswerId("o_first_run_other")}
"""O-first-run as each route answers it in the visit it shows (a route not named follows typical): both answers measured."""
CART_SHARE = {"typical": 1500, "sharp": 2000}
HILL_SHARE = {"typical": 1000, "sharp": 1500}
"""The hands' shares of the cart and the hill's walk a route sets from B22 (week-five-numbers.md, "The arithmetic"; a
route not named follows typical)."""
ROOFS = chip_cure("ash_laden", "n2_clear_roofs")
"""The rule a route that takes rules writes on the roofs' chip, whose order card is not offered again (D-203)."""
WEEK_TWENTY_NINE = Week(
    start="I13", stop="B22", landed=TWENTY_NINE.of, news=("Y1", "SL37", "Y2", "Y3", "O-first-run", "A41", "B22"),
    chips=(ROOFS,),
    shares=(RouteShare(RUN_CART, CART_SHARE), RouteShare(WALK_HILL, HILL_SHARE)),
    two_answers=(TwoAnswer(FIRST_RUN_OFFER, FIRST_RUN_ANSWERS),),
    steps=(FIRST_RUN,))


def day_twenty_nine(route: str) -> Later:
    """I13's visit to B22's, week five's first: day twenty-seven's sinks, rules, split and shares carried on, the roofs'
    rule written once the chip is seen, O-first-run answered by the route, the run tapped once shown, and the cart and
    the hill's walk in the hands' mix from B22."""
    return later(w4.day_twenty_seven(route), WEEK_TWENTY_NINE, route)


THIRTY = Landings(
    {"Y4": ("t_y4",), "SL38": ("t_line_walked",), "Y5": ("t_moths",), "Y6": ("t_pack_yard",), "SL39": ("t_elk_words",),
     "Y7": ("t_hair_warm",), "B23": ("t_b23",)},
    {"A42": ("call_pack",)}, {}, {})
CALL_PACK, COMB_PELTS = CardId("call_pack"), CardId("comb_pelts")
NET_MOTHS, DUST_LINE, WARD_GATE, JUMP_PACK = CardId("net_moths"), CardId("dust_line"), CardId("ward_gate"), CardId("jump_pack")
TRACK = CastCard("tracker", "{lane}_track", {"typical": 3000, "sharp": 5000})
"""The tracker's share of their own time on the line once cast; the rest stays on their old work (the week's people
decision; a route not named follows typical)."""
MOTHS_SHARE = {"typical": 500, "sharp": 800}
DUST_SHARE = {"typical": 500, "sharp": 800}
WARD_SHARE = {"typical": 1000, "sharp": 1000}
JUMP_SHARE = {"typical": 500, "sharp": 500}
"""The hands' shares of the moths, the dust, the ward and the jump from the visit each is shown (a route not named
follows typical); the moths' share yields once their pool is netted out (D-125)."""
HAIR = Keep(COMB_PELTS, StoreId("hair"), 3)
"""Hair combed by hand while under A42's three: every route makes the new input store."""
TRACK_CHIP = chip_cure("drifted", "clear_track")
"""The rule a route that takes rules writes on the track's chip, which has no order card (D-155)."""
WEEK_THIRTY = Week(
    start="B22", stop="B23", landed=THIRTY.of, news=("Y4", "SL38", "Y5", "Y6", "SL39", "Y7", "A42", "B23"),
    chips=(TRACK_CHIP,),
    shares=(RouteShare(NET_MOTHS, MOTHS_SHARE), RouteShare(DUST_LINE, DUST_SHARE), RouteShare(WARD_GATE, WARD_SHARE),
            RouteShare(JUMP_PACK, JUMP_SHARE)),
    casts=(TRACK,),
    steps=(CALL_PACK,), queued=(CALL_PACK,),
    keeps=((HAIR, frozenset(SINKS)),))


def day_thirty(route: str) -> Later:
    """B22's visit to B23's, week five's second: day twenty-nine's moves carried on, the track's rule written once its
    chip is seen, the tracker on the line at the route's share, hair combed while short of three, the moths, the dust,
    the ward and the jump in the hands' mix once shown, and A42 queued When ready once shown, or tapped when ready."""
    return later(day_twenty_nine(route), WEEK_THIRTY, route)

