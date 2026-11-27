"""Week five's chapters as the routes play them (daythree/chapter.Later), played on from week four's end by the same
players (tests/weekfive/policy.py `later`): which content step is which story id, read off a save, and what each
chapter's Week names for the policies. Ids only (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import AnswerId, CardId, OfferId
from tests.daythree.chapter import Landings, Later
from tests.weekfive.policy import RouteShare, TwoAnswer, Week, chip_cure, later
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
