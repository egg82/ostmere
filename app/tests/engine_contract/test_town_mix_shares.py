"""Invariants 90 and 91 (engine DESIGN.txt, "THE TOWN'S MIX": "Town share", "Rates on a joined lane", "Uncapped only",
"No XP"). A share in a town mix is basis points of one person's own time; a tap on the person's lane yields their
shares; a card on a ruled lane carries no skill and no XP line. Expected numbers come from the documented arithmetic:
a make of one whole item per second at a share of s basis points moves a store by s * Q / BP per second."""
from dataclasses import replace

import pytest
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, CardDef, CardShare, InvalidRulesError, Mix, RunKind, SaveMix, SwitchMix,
    advance, decide, validate_rules, view, xp,
)
from town_mix_world import (
    A1, A2, AC, B1, HM1, K, LA, LB, PER_SECOND, TM, TOWN_RULE, V, W, X, always, card_view, hands_mixes, joiner, orders, start,
    stored, world,
)

BOTH = (joiner("ja", LA, TM, A1), joiner("jb", LB, TM, B1))
"""Both people join at time 0 into the one town mix; the join gives each their card at BP."""


@given(a1=st.integers(0, BP), a2_frac=st.integers(0, BP), b1=st.integers(0, BP), t=st.integers(1, 3000))
def test_each_person_runs_their_shares_of_their_own_time(a1: int, a2_frac: int, b1: int, t: int):
    """Invariant 90: a lane's shares may sum to BP, and the whole to BP times the people present (a1 + b1 may reach
    2 * BP); each card on L runs at its share_bp, so after t seconds its make line holds share * t * Q / BP."""
    a2 = (BP - a1) * a2_frac // BP
    r = world(BOTH)
    s = decide(start(r), r, 0, SaveMix(Mix(TM, (CardShare(A1, a1), CardShare(A2, a2), CardShare(B1, b1)))))
    assert view(s, r).running_town_mix == TM
    for store, share in ((X, a1), (W, a2), (V, b1)):
        assert abs(stored(s, r, store, t) - share * t * Q // BP) <= t
    cv, _ = card_view(s, r, B1, t)
    assert b1 == 0 or cv.share_bp == b1


def test_the_unused_part_of_a_persons_time_idles_and_is_not_moved():
    """Invariant 90: with a1 at 3000 the other 7000 of la's time idles; nothing flows to a2 or to lb's card."""
    r = world(BOTH)
    s = decide(start(r), r, 0, SaveMix(Mix(TM, (CardShare(A1, 3000), CardShare(B1, 1000)))))
    assert abs(stored(s, r, X, 1000) - 300 * Q) <= 1000
    assert abs(stored(s, r, V, 1000) - 100 * Q) <= 1000
    assert stored(s, r, W, 1000) == 0


def test_a_tap_on_a_person_yields_their_shares_and_no_one_elses():
    """Invariant 90: while la taps ac (50 s, the always rule of a capped one-off survives la's join), a1 reads
    YIELDED with its share unchanged and x does not move; b1 on lb runs on; at 50 a1 runs again."""
    r = world((joiner("jb", LB, TM, B1), joiner("ja", LA, TM, A1, at=20)))
    s = start(r, orders(TOWN_RULE, always(AC)))
    assert always(AC) in advance(s, r, 30).orders
    cv, _ = card_view(s, r, A1, 30)
    assert (cv.run, cv.share_bp) == (RunKind.YIELDED, BP)
    assert stored(s, r, X, 30) == 0
    assert abs(stored(s, r, V, 30) - 30 * Q) <= 30
    assert card_view(s, r, A1, 60)[0].run != RunKind.YIELDED
    assert abs(stored(s, r, X, 60) - 10 * Q) <= 10


def test_a_players_edit_of_the_running_town_mix_applies_at_once():
    """"Verbs": a player's SaveMix of the running town mix rebuilds the rates at the edit's instant."""
    r = world((joiner("ja", LA, TM, A1),))
    s = decide(start(r), r, 100, SaveMix(Mix(TM, (CardShare(A1, 5000),))))
    assert abs(stored(s, r, X, 300) - (100 + 100) * Q) <= 300


# ---- invariant 91: never trains ----------------------------------------------------------------------------------

@pytest.mark.parametrize("card", [CardDef(A2, 10, lane=LA, skill=K, xp_per_hour=PER_SECOND),
                                  CardDef(A2, 10, lane=LA, skill=K)])
def test_a_ruled_lane_card_with_a_skill_or_xp_line_is_refused(card: CardDef):
    """Invariant 91 ("No XP"): InvalidRulesError for a ruled-lane card with a skill or an XP line (an XP line with no
    skill is invalid on any lane, so it is no separate case); control: the same card on the hands is valid."""
    base = world()
    others = tuple(c for c in base.cards if c.id != card.id)
    with pytest.raises(InvalidRulesError):
        validate_rules(replace(base, cards=others + (card,)))
    validate_rules(replace(base, cards=others + (replace(card, lane=next(c.lane for c in base.cards if c.id == "h1")),)))


@given(t=st.integers(0, 5000))
def test_a_town_mix_never_changes_a_skills_xp(t: int):
    """Invariant 91: the hands' mix trains k at the same rate whether or not the town's mix runs, a join happened or
    a ruled lane taps."""
    plain = world()
    town = world(BOTH)
    verbs = (*hands_mixes(), SwitchMix(HM1))
    a = decide(start(plain, *verbs), plain, 0, orders(always(A1), always(B1)))
    b = decide(start(town, *verbs), town, 0, orders(TOWN_RULE, always(A1), always(B1)))
    assert view(b, town).running_town_mix == TM
    assert xp(a, plain, K, t) == xp(b, town, K, t)
    assert xp(a, plain, K, 5000) > 0
