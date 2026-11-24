"""Week four's chapters as the routes play them (daythree/chapter.Later), played on from week three's end by the same
players as weeks two and three (content.py): which content step is which story id, read off a save, and what each
chapter adds to the policies. Ids only (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import CardId, ChipId
from tests.daythree.chapter import ChipRule, Landings, Later, Share
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
