"""A person leaves the town, part two: once and for good, and the codec and validation (engine DESIGN.txt, "LEAVES",
invariants 153 and 155). Written blind from that part and the public interface; the `kills` marker names the rows of
MUTANTS_leaves.txt each test must turn red for. ld never joins: a lane with LEFT held is gone, joined or not."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    HANDS, ActionId, AfterTime, CardShare, AnswerDef, AnswerId, InvalidRulesError, LaneId, OfferDef, OfferId, Outcome,
    RuleInstall, Rules, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, advance, decode, encode, rules_digest, validate_rules,
    view,
)
from leaves_world import (
    AD, D1, DC, LA, LD, LEAVE_AT, S, before_and_after, join, kills, leave, leave_trigger, left, outcome, rules, scene,
)
from town_mix_world import lane_card, stored

LATE = TriggerDef(TriggerId("late"), AfterTime(200), Outcome(joins=(join(LD, D1),), orders=(RuleInstall(DC),)))
"""At 200: a join of ld, and an install of its capped card's always rule."""
PIN = "85277cdc413e3d7756de8539ac6f3247f716a920af194a92a4656b56d05349ba"
"""rules_digest(rules(None)) as the engine computed it before this part: rules with no leave keep it."""


def ld_world(leaves: bool) -> Rules:
    return rules(None, extra=((leave_trigger(100, LD, ()),) if leaves else ()) + (LATE,))


# ---- 153: once and for good ---------------------------------------------------------------------------------------

@kills(9, 15)
def test_left_is_held_from_the_moment_for_good_and_only_where_a_leave_lands():
    """Invariant 153: Unlock(LEFT, ld) is absent at 99, held once from 100 to 500; the world with no leave never holds
    it."""
    r, c = ld_world(True), ld_world(False)
    for t in (99, 100, 101, 200, 201, 500):
        held = advance(scene(r), r, t).unlocked
        assert held.count(left(LD)) == (1 if t >= 100 else 0), t
        assert left(LD) not in advance(scene(c), c, t).unlocked


@kills(15)
def test_a_join_and_an_install_on_a_left_lane_change_nothing_where_they_would_have_acted():
    """Invariant 153, CHOICES "Nothing lands on a left lane": at 200 ld's join and its card's install, after the leave
    at 100, add no JOINED, no share, no order and no work; the control (no leave) joins, runs d1 and taps dc."""
    r, c = ld_world(True), ld_world(False)
    ac = advance(scene(c), c, 210)
    assert TapCard(DC) in [o.then for o in ac.orders]   # the control installs it
    assert Unlock(UnlockKind.JOINED, LD) in ac.unlocked and lane_card(ac, LD) == DC and stored(scene(c), c, S, 300) > 0
    for t in (200, 210, 300, 500):
        a = advance(scene(r), r, t)
        assert Unlock(UnlockKind.JOINED, LD) not in a.unlocked
        assert D1 not in {x.card for m in a.mixes for x in m.components if isinstance(x, CardShare)} and TapCard(DC) not in [o.then for o in a.orders]
        assert lane_card(a, LD) is None and stored(scene(r), r, S, t) == 0
        assert LD not in {b.lane for b in view(a, r).lanes}


# ---- 155: codec and validation ------------------------------------------------------------------------------------

@kills(16)
def test_a_save_holding_left_round_trips_through_the_codec():
    r, _, after = before_and_after()
    s = advance(after, r, 500)
    assert left(LA) in s.unlocked and decode(encode(s, r), r) == s


@kills(18)
def test_rules_with_no_leave_keep_their_digest_and_a_leave_changes_it():
    assert rules_digest(rules(LEAVE_AT)) != PIN
    assert rules_digest(rules(None)) == PIN


def bad(kind: str) -> Rules:
    """rules(None) with one thing wrong, each a refusal of invariant 155 (built without validate_rules)."""
    r = rules(None)
    two = TriggerDef(TriggerId("again"), AfterTime(90), outcome(leaves=(leave(LA, ()),)))
    wrong = {
        "undeclared lane": outcome(leaves=(leave(LaneId("nobody"), ()),)),
        "lane not ruled": outcome(leaves=(leave(HANDS, ()),)),
        "undeclared stop": outcome(leaves=(leave(LA, (ActionId("nothing"),)),)),
        "twice in one outcome": outcome(leaves=(leave(LA, ()), leave(LA, ()))),
        "left in unlocks": Outcome(unlocks=(left(LA),)),
    }
    if kind in wrong:
        return replace(r, triggers=r.triggers + (TriggerDef(TriggerId("bad"), AfterTime(50), wrong[kind]),))
    if kind == "twice in two triggers":
        return replace(r, triggers=r.triggers + (leave_trigger(), two))
    if kind == "in a card":
        return replace(r, cards=tuple(replace(c, outcome=outcome(leaves=(leave(),))) if c.id == AD else c for c in r.cards))
    if kind == "left in opening":
        return replace(r, opening=(left(LA),))
    raise AssertionError(kind)


@kills(19)
@pytest.mark.parametrize("kind", ["undeclared lane", "lane not ruled", "undeclared stop", "twice in one outcome",
                                  "twice in two triggers", "in a card", "left in unlocks", "left in opening"])
def test_rules_with_a_leave_that_is_not_declared_once_in_a_trigger_or_an_answer_are_refused(kind: str):
    with pytest.raises(InvalidRulesError):
        validate_rules(bad(kind))


def test_a_leave_in_an_answers_outcome_is_allowed():
    r = rules(None)
    offer = OfferDef(OfferId("o"), (AnswerDef(AnswerId("yes"), outcome(leaves=(leave(),))), AnswerDef(AnswerId("no"))))
    validate_rules(replace(r, offers=(offer,)))
