"""The worth measure on a fixture world, two skills and the cards that train them (tests/worth/probe.py): the controls
that show it tells setups apart, and the first build's measure beside it on the same mix.

Skill a's goal takes 1 h on its card alone, skill b's 2 h, so the best setup splits a third and two thirds and lands
both at 3 h, the time one card after the other would take."""
from ashfall_app.engine import (
    BP, CardDef, CardId, PacingCurve, Rules, Save, SkillDef, SkillId, Unlock, UnlockKind, new_save, view,
)
from tests.worth import goaltime as gt
from tests.worth import probe as pr
from tests.worth import summary as sm

H = 3600
A, B = SkillId("a"), SkillId("b")
LEVEL_XP = 3600 * 1000 * 100
RATE = LEVEL_XP // H
"""Card a's rate: a level an hour (XP per second in quantity units, engine/units.py)."""


def world(fast_b: bool = False) -> tuple[Rules, Save]:
    cards = [CardDef(CardId("ca"), 60, skill=A, xp_per_hour=RATE), CardDef(CardId("cb"), 60, skill=B, xp_per_hour=RATE // 2),
             CardDef(CardId("rest"), 60), CardDef(CardId("cb_fast"), 60, skill=B, xp_per_hour=RATE * 2)]
    shown = ["ca", "cb", "rest", *(["cb_fast"] if fast_b else [])]
    r = Rules(stores=(), skills=(SkillDef(A), SkillDef(B)), standing=(), curve=PacingCurve((LEVEL_XP, 10 * LEVEL_XP)),
              max_firings_per_instant=100, lanes=(), cards=tuple(cards), chips=(), triggers=(),
              opening=(Unlock(UnlockKind.SKILL, A), Unlock(UnlockKind.SKILL, B),
                       *(Unlock(UnlockKind.CARD, CardId(c)) for c in shown)))
    return r, new_save(r)


def worth_of(shares: gt.Shares, fast_b: bool = False) -> float:
    r, s = world(fast_b)
    b = gt.board(s, view(s, r), r)
    goals = pr.served(b, shares)
    best = pr.score(b, goals, pr.probe(r, shares, goals))
    assert best is not None
    return sm.fraction(best, pr.score(b, goals, shares))


def test_the_board_reads_each_goal_and_its_time_alone() -> None:
    r, s = world()
    b = gt.board(s, view(s, r), r)
    assert {(g.skill, g.card, round(g.alone_s)) for g in b.goals} == {("a", "ca", H), ("b", "cb", 2 * H)}


def test_the_best_setup_lands_the_set_when_one_card_after_another_would() -> None:
    r, s = world()
    b = gt.board(s, view(s, r), r)
    goals = pr.served(b, (("ca", 5000), ("cb", 5000)))
    probe = pr.probe(r, (("ca", 5000), ("cb", 5000)), goals)
    assert probe == (("ca", 3333), ("cb", 6667))
    assert abs((pr.score(b, goals, probe) or 0) - 3 * H) < 5


def test_control_a_split_in_proportion_is_worth_nothing_to_change() -> None:
    assert worth_of((("ca", 3333), ("cb", 6667))) < 0.001


def test_control_the_first_builds_measure_read_that_same_split_far_behind() -> None:
    """Worth at the nearest single goal: the split lands a's goal at 3 h, a's card alone at 1 h."""
    r, s = world()
    b = gt.board(s, view(s, r), r)
    split = (("ca", 3333), ("cb", 6667))
    nearest = min(b.goals, key=lambda g: g.alone_s)
    kept = nearest.xp_left / gt.rates(b, split)[nearest.skill]
    assert sm.fraction(nearest.alone_s, kept) > 0.6


def test_control_a_mix_that_starves_a_goal_is_worth_a_lot_to_change() -> None:
    assert worth_of((("ca", 9000), ("cb", 1000))) > 0.7


def test_upkeep_cards_keep_their_share_and_the_rest_is_split() -> None:
    r, s = world()
    b = gt.board(s, view(s, r), r)
    own = (("ca", 4000), ("cb", 4000), ("rest", 2000))
    probe = pr.probe(r, own, pr.served(b, own))
    assert dict(probe)["rest"] == 2000 and sum(bp for _, bp in probe) == BP


def test_a_new_card_that_does_old_work_better_makes_a_change_worth_making() -> None:
    split = (("ca", 3333), ("cb", 6667))
    assert worth_of(split) < 0.001 < 0.25 < worth_of(split, fast_b=True)


def test_a_setup_that_leaves_a_goal_unserved_never_lands_the_set() -> None:
    r, s = world()
    b = gt.board(s, view(s, r), r)
    goals = pr.served(b, (("ca", 5000), ("cb", 5000)))
    assert pr.score(b, goals, (("ca", BP),)) is None
    assert sm.fraction(H, None) == 1.0
