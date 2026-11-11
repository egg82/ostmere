"""Retired chores (engine DESIGN.txt, "Installed rule", "Retired chores", invariants 142-147; week-three plan, items 3
and 5). Written blind from that part and the public interface; the `kills` marker names the rows of MUTANTS_leaves.txt
each test must turn red for. retire_world's turn at 100 names c1 and r1 (the cures) while both are mid-task; c2 and r2
(same lanes, same store) and the mix and queue entry stand beside them. The loader's half is test_retire_loader_contract."""
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    HANDS, QUANTITY_SCALE as Q, AfterTime, AnswerDef, AnswerId, CardId, InvalidRulesError, Join, MixId, OfferDef, OfferId,
    Outcome, TriggerDef, TriggerId,
    Rules, Save, SetOrders, advance, advance_logged, decide, decide_logged, decode, encode, rebase, rebase_logged,
    rules_digest, validate_rules, value,
)
from leaves_world import ended_changes, expected_ends, kills, logged_end
from retire_world import C1, C2, OA, OB, OC, OD, OE, OF, ORDERS, LR, R1, R2, T0, TURN, rules, scene, turn
from town_mix_world import card_view, lane_card

PIN = "2d062104336566b55da08cf2329c283d724501c545ddc56c060279838b1d73aa"
"""rules_digest(rules(None)) as the engine computed it before this part: rules with no retire_orders keep it."""


def worlds() -> tuple[Rules, Rules, Save, Save]:
    """The rules with the turn and the control without any, each saved at TURN - 1."""
    r, c = rules(), rules(None)
    return r, c, advance(scene(r), r, TURN - 1), advance(scene(c), c, TURN - 1)


def completions(s: Save, r: Rules, card: CardId, t: int) -> int:
    return card_view(s, r, card, t)[0].completions


# ---- 142: retire --------------------------------------------------------------------------------------------------

@kills(21, 22)
def test_a_turn_removes_exactly_the_orders_tapping_the_named_cards_with_their_latches():
    """Invariant 142: of oa, ob, oc, od, oe the turn takes oa (c1) and oc (r1); ob (c2, the same lane and store), od
    (r2, the same lane) and oe (a mix order) stay in their order with the latches they had."""
    r, c, s, sc = worlds()
    assert s.orders == ORDERS and all(s.latches[:5]) and not s.latches[5]   # the premise: six orders, the named ones on, the last one off
    after, ctl = advance(s, r, TURN), advance(sc, c, TURN)
    kept = [i for i, o in enumerate(ORDERS) if o in (OB, OD, OE, OF)]
    assert (after.orders, after.latches) == (tuple(ORDERS[i] for i in kept), tuple(s.latches[i] for i in kept))
    assert ctl.orders == ORDERS   # the control: nothing else removes them


@kills(23)
def test_the_queue_the_mixes_and_the_unlocks_are_as_the_same_instant_leaves_them_without_the_part():
    """Invariant 142: nothing but orders changes: the queue entry tapping c1 stays, as do the saved mix and the unlock
    set, equal to those of the world with no turn; the unlock set is one a join at 50 filled (Unlock(JOINED, lr)), as
    this world's opening None leaves it empty otherwise."""
    joiner = TriggerDef(TriggerId("joiner"), AfterTime(50), Outcome(joins=(Join(LR, MixId("town:t"), R2),)))
    r, c = (replace(w, triggers=(joiner, *w.triggers)) for w in (rules(), rules(None)))
    for w in (r, c):
        validate_rules(w)
    s, sc = advance(scene(r), r, TURN - 1), advance(scene(c), c, TURN - 1)
    after, ctl = advance(s, r, TURN), advance(sc, c, TURN)
    assert after.queue == s.queue != () and after.mixes == ctl.mixes != ()
    assert after.unlocked == ctl.unlocked != ()


# ---- 143: logged --------------------------------------------------------------------------------------------------

@kills(24)
def test_each_removed_order_is_logged_once_as_ended_season_with_the_level_of_the_store_it_read():
    """Invariant 143: the span holding TURN reports RuleChange(TURN, o, False, level, Ended.SEASON) for oa (a time
    order: level None) and oc (it reads t0: 100 items at 100)."""
    r, _, s, _ = worlds()
    step = advance_logged(s, r, TURN)
    assert value(step.save, r, T0, TURN) == 100 * Q
    assert ended_changes(step.rule_changes) == expected_ends(
        logged_end(TURN, OA, None, "SEASON"), logged_end(TURN, OC, 100 * Q, "SEASON"))
    assert not ended_changes(advance_logged(step.save, r, 500).rule_changes)   # logged at the instant, not again


@kills(33)
def test_a_span_with_no_turn_and_a_players_removal_report_nothing_ended():
    """Invariant 143: the control's whole run, and a SetOrders that drops an order, have every `ended` None; the
    control's spans do report latch changes, so the field is read on real entries."""
    r, c, s, _ = worlds()
    ctl = advance_logged(scene(c), c, 500).rule_changes
    assert ctl and not ended_changes(ctl)
    after = advance(s, r, TURN + 10)
    dropped = decide_logged(after, r, TURN + 20, SetOrders((OB, OD)))
    assert not ended_changes(dropped.rule_changes)


# ---- 144: once, and the player's again ----------------------------------------------------------------------------

@kills(25)
def test_an_equal_order_the_player_sets_after_the_turn_is_kept_by_every_later_advance():
    """Invariant 144: the turn lands once. oa set again at 110 stays at 200 and 500, and c1 runs again."""
    r, _, s, _ = worlds()
    after = advance(s, r, TURN + 10)
    assert OA not in after.orders
    again = decide(after, r, TURN + 10, SetOrders((OA,) + after.orders))   # first: the first true order taps, so oa leads
    for t in (200, 500):
        assert OA in advance(again, r, t).orders, t
    assert completions(again, r, C1, 500) > completions(again, r, C1, 200) > 3


# ---- 145: runs on to its landing ----------------------------------------------------------------------------------

@kills(26, 27)
def test_a_tap_running_at_the_turn_lands_when_it_would_have_and_no_removed_order_starts_it_again():
    """Invariant 145: c1 (due about 115) and r1 (due 121) are running at 99; their completions equal the control's at
    every second to 130, then stay at 3 in the turn's world while the control's go on; the rest of each lane runs."""
    r, c, s, sc = worlds()
    assert lane_card(s, HANDS) == C1 and lane_card(s, LR) == R1   # the premise: both mid-task
    for t in range(TURN, 131):
        for card in (C1, R1):
            assert completions(s, r, card, t) == completions(sc, c, card, t), (card, t)
    for card in (C1, R1):
        assert (completions(s, r, card, 130), completions(s, r, card, 500)) == (3, 3), card
        assert completions(sc, c, card, 500) > 3   # the control keeps tapping
    assert completions(s, r, C2, 500) > 0 and completions(s, r, R2, 500) > 0   # the lanes go to the orders that stay


# ---- 146: validation ----------------------------------------------------------------------------------------------

def refused(kind: str) -> Rules:
    """rules(None) with one thing wrong (built without validate_rules)."""
    r = rules(None)
    base = rules()
    ghost = CardId("ghost")
    if kind == "undeclared card":
        return rules(outcome=turn((ghost,)))
    if kind == "twice":
        return replace(base, triggers=(replace(base.triggers[0], outcome=turn((C1, C1))),))
    if kind == "in a card":
        return replace(r, cards=tuple(replace(x, outcome=turn()) if x.id == C2 else x for x in r.cards))
    offer = OfferDef(OfferId("o"), (AnswerDef(AnswerId("y"), turn()), AnswerDef(AnswerId("n"))))
    return replace(r, offers=(offer,))


@kills(28)
@pytest.mark.parametrize("kind", ["undeclared card", "twice", "in a card", "in an answer"])
def test_a_retirement_naming_an_undeclared_card_or_one_twice_or_outside_a_trigger_is_refused(kind: str):
    """Invariant 146: InvalidRulesError, and for the card problems the message names the card."""
    names = {"undeclared card": "ghost", "twice": "c1"}
    with pytest.raises(InvalidRulesError, match=names.get(kind)):
        validate_rules(refused(kind))


def test_a_retirement_may_name_a_card_on_either_lane():
    validate_rules(rules(outcome=turn((C2, R2))))


# ---- 147: rebase and codec ----------------------------------------------------------------------------------------

def written(at: int = 130) -> str:
    c = rules(None)
    return encode(advance(scene(c), c, at), c)


@kills(29)
def test_a_save_past_the_turn_loads_without_the_named_cards_tap_orders_and_logs_each_as_ended_season():
    """Invariant 147: written under rules with no turn at 130, loaded under rules whose turn is at 100."""
    c, r = rules(None), rules()
    before = decode(written(), c)
    after = rebase(written(), r)
    assert after.time == 130 and before.orders == ORDERS
    assert after.orders == (OB, OD, OE, OF) and decode(encode(after, r), r) == after
    gone = ended_changes(rebase_logged(written(), r).rule_changes)
    assert gone == expected_ends(logged_end(130, OA, None, "SEASON"), logged_end(130, OC, 130 * Q, "SEASON"))
    assert rebase(written(), rules(10**6)).orders == ORDERS   # a turn not yet due removes nothing


@kills(30)
def test_rules_with_no_retire_orders_keep_their_digest_and_a_turn_changes_it():
    assert rules_digest(rules()) != PIN
    assert rules_digest(rules(None)) == PIN
