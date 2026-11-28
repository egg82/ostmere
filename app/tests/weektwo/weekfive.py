"""Week five's chapters as the routes play them (daythree/chapter.Later), played on from week four's end by the same
players (tests/weekfive/policy.py `later`): which content step is which story id, read off a save, and what each
chapter's Week names for the policies. Ids only (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import AnswerId, CardId, OfferId, StoreId
from tests.daythree import content as c3
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


THIRTY_ONE = Landings(
    {"Y8": ("t_y8",), "Y9": ("t_y9",), "SL40": ("t_scrape",), "Y10": ("t_y10",), "SL41": ("t_bear_sign_2",),
     "Y11": ("t_y11",), "B24": ("t_b24",)},
    {"A43": ("wake_ward",)}, {}, {"O-burners": OfferId("o_burners")})
WAKE_WARD = CardId("wake_ward")
BURNERS = {"typical": AnswerId("o_burners_food"), "sharp": AnswerId("o_burners_build")}
"""Where the burners work first, as each route answers (a route not named follows typical): both answers measured. The
whenever player's kind rule, set in week three, answers it."""
JOBS = ("j_post_roof", "j_drag_elk", "j_new_pins")
JOB_NO = {"sharp": "j_drag_elk"}
"""Lucy's jobs from B23, each answered yes when it shows, but for the one each route here declines. A yes shows the job
without queuing it (D-176), so a route taps it once it is ready."""


def jobs(route: str) -> tuple[tuple[OfferId, AnswerId], ...]:
    no = JOB_NO.get(route)
    return tuple((OfferId(j), AnswerId(f"{j}_{'no' if j == no else 'yes'}")) for j in JOBS)


def week_thirty_one(route: str) -> Week:
    """Day thirty-one's ids for `route`: the latch's order card is on stakes, which every route since day eight takes."""
    return Week(
        start="B23", stop="B24", landed=THIRTY_ONE.of,
        news=("Y8", "Y9", "O-burners", "SL40", "Y10", "SL41", "Y11", "A43", "B24"),
        order_cards=c3.order_cards(c3.opening3(), ("post_stores",)),
        arrivals=((OfferId("o_burners"), BURNERS.get(route, BURNERS["typical"])),),
        asks=jobs(route),
        steps=(CardId("post_roof"), CardId("drag_elk"), CardId("new_pins"), WAKE_WARD), queued=(WAKE_WARD,))


def day_thirty_one(route: str) -> Later:
    """B23's visit to B24's, week five's third: day thirty's moves carried on, the latch and the house by their order
    cards, O-burners by the route's answer (or the kind's rule), Lucy's jobs answered when they show and tapped once
    ready, and A43 queued When ready once shown, or tapped when ready."""
    return later(day_thirty(route), week_thirty_one(route), route)


THIRTY_THREE = Landings(
    {"Y12": ("t_y12",), "Y13": ("t_y13",), "B25": ("t_b25",), "Y14": ("t_y14",), "Y15": ("t_y15",)},
    {"A44": ("open_ward",)}, {}, {})
OPEN_WARD, HILL_STAKES = CardId("open_ward"), CardId("hill_stakes")
LAST_JOB = "j_hill_stakes"
LAST_JOB_NO = {"sharp": LAST_JOB}
"""Lucy's last job, from B24, answered yes when it shows but on the route here that declines it: both answers measured."""


def week_thirty_three(route: str) -> Week:
    """Day thirty-three's ids for `route`: B24's visit to Y15's, night 35 on the calendar."""
    no = LAST_JOB_NO.get(route) == LAST_JOB
    return Week(
        start="B24", stop="Y15", landed=THIRTY_THREE.of, news=("Y12", "Y13", "A44", "B25", "Y14", "Y15"),
        asks=((OfferId(LAST_JOB), AnswerId(f"{LAST_JOB}_{'no' if no else 'yes'}")),),
        steps=(HILL_STAKES, OPEN_WARD), queued=(OPEN_WARD,))


def day_thirty_three(route: str) -> Later:
    """B24's visit to Y15's, week five's last: day thirty-one's moves carried on, Lucy's last job answered when it shows
    and tapped once ready, and A44 queued When ready once shown, or tapped when ready."""
    return later(day_thirty_one(route), week_thirty_three(route), route)
