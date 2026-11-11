"""A person leaves the town, part one: what the leave changes and what it leaves alone (engine DESIGN.txt, "LEAVES",
invariants 148-152; week-three plan, items 4 and 5). Written blind from that part and the public interface; the `kills`
marker names the rows of MUTANTS_leaves.txt each test must turn red for. The world is leaves_world's: la leaves at 40 with
its ac tap (started at 20, due at 70) under way; every expectation is exact, or an equality with the same world where
nobody leaves."""
import pytest

from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, AfterTime, AtLeast, CardId, CardShare, EngineError, FlowKind, InvalidVerbError, Mix, MixId, Order, Outcome, RateRef,
    Rules, RunKind, Save, SaveMix, SetOrders, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked, advance,
    advance_logged, decide, decide_logged, explain, value, view,
)
from leaves_world import (
    A1, A2, AC, AD, AC_DONE, AD_DONE, AFTER_MIXES, B1, B2, H1, HM, HS, KEEP, LA, LA_CARDS, LB, LEAVE_AT, MIX_HANDS,
    MIX_SOLO_B, MIX_TOWN, MIX_SOLO_A, ORDER_AC, ORDER_AD, ORDER_BC, STOP, TM, TM2, TOWN_RULE, U, V, W, X, Y, Z, Z2,
    before_and_after, ended_changes, expected_ends, kills, logged_end, rules, scene,
)
from town_mix_world import lane_card, stored

T = LEAVE_AT
LATER = (T, T + 1, 70, 71, 120, 500)


def control() -> tuple[Rules, Save]:
    """The same world where nobody leaves, at T - 1."""
    c = rules(None)
    return c, advance(scene(c), c, T - 1)


def mixes_by_id(s: Save) -> dict[MixId, Mix]:
    return {m.id: m for m in s.mixes}


# ---- 148: others untouched ----------------------------------------------------------------------------------------

@kills(2, 8, 10)
def test_every_other_person_and_store_runs_as_if_nobody_had_left_and_the_leavers_stores_stop():
    """Invariant 148: lb's stores and the hands' and the standing's follow the world where nobody leaves, exactly; la's
    own stop where they were (12 items of x, 0 of w) while the control's go on, and no one else gains what they lose."""
    r, s, _ = before_and_after()
    c, sc = control()
    for t in LATER:
        for store in (V, U, HS, Z2):
            assert stored(s, r, store, t) == stored(sc, c, store, t), (store, t)
        assert [lane_card(advance(s, r, t), LB)] == [lane_card(advance(sc, c, t), LB)], t
    assert stored(sc, c, V, 500) > stored(sc, c, V, T) and stored(sc, c, X, 500) > 12 * Q   # the control runs on
    assert (stored(s, r, X, T), stored(s, r, X, 500)) == (12 * Q, 12 * Q)
    assert stored(s, r, W, 500) == stored(s, r, W, T)


@kills(1, 2, 8)
def test_the_leavers_shares_leave_every_saved_mix_and_nothing_else_in_a_mix_changes():
    """Invariant 148 and CHOICES step 4: the town mix keeps lb's two shares, in order; the hands' mix
    is as it was; nobody's share moved to another."""
    _, s, after = before_and_after()
    assert mixes_by_id(s) == {TM: MIX_TOWN, HM: MIX_HANDS}   # the premise: the save held la's shares
    assert mixes_by_id(after) == AFTER_MIXES


@kills(1, 17)
def test_a_mix_left_with_no_component_stays_empty_and_the_other_persons_mix_is_untouched():
    """CHOICES step 4: la alone in the town mix, lb alone in town:two. The first stays as an empty mix, the second is as it was."""
    _, s, after = before_and_after(solo=True)
    assert mixes_by_id(s) == {TM: MIX_SOLO_A, TM2: MIX_SOLO_B, HM: MIX_HANDS}
    assert mixes_by_id(after) == {TM: Mix(TM, ()), TM2: MIX_SOLO_B, HM: MIX_HANDS}
    assert view(after, rules(T, solo=True)).greyed_mixes == (HM,)


@kills(2, 8, 20)
@pytest.mark.parametrize("ref", [
    RateRef(B1, FlowKind.MAKE, V), RateRef(B2, FlowKind.MAKE, U), RateRef(H1, FlowKind.MAKE, HS),
    RateRef(KEEP, FlowKind.MAKE, Z2),
], ids=["b1", "b2", "h1", "keep"])
def test_every_explanation_off_the_leavers_lane_is_the_same_just_after_as_just_before(ref: RateRef):
    """Invariant 148: nothing on these rules is shared with la, so the Explanation of each line off its lane is equal
    across the leave (its share, modifiers, run and rate)."""
    r, s, after = before_and_after()
    assert explain(after, r, ref) == explain(s, r, ref)
    assert explain(after, r, ref).base_per_hour > 0   # a real line, not a zero compared with a zero


# ---- 149: no mix greys --------------------------------------------------------------------------------------------

@kills(1)
def test_no_mix_greys_because_of_the_leave_and_a_mix_greyed_before_stays_greyed():
    """Invariant 149: hm greys at 30 (hc done) and stays so; the town mix is never greyed, and keeps running."""
    r, s, _ = before_and_after()
    assert view(s, r).greyed_mixes == (HM,) and view(s, r).running_town_mix == TM   # the premise
    for t in LATER:
        v = view(advance(s, r, t), r)
        assert v.greyed_mixes == (HM,), t
        assert v.running_town_mix == TM, t


@kills(1, 17)
def test_a_mix_left_empty_is_not_greyed_either():
    r, s, _ = before_and_after(solo=True)
    for t in LATER:
        assert view(advance(s, r, t), r).greyed_mixes == (HM,), t


# ---- 150: orders gone and logged ----------------------------------------------------------------------------------

@kills(4, 8)
def test_the_orders_on_the_lane_are_gone_the_rest_keep_their_order_and_latches_and_none_comes_back():
    """Invariant 150: save.orders holds no tap of a card on la from T on; the town rule and lb's order stay in their
    order with the latches they had."""
    r, s, after = before_and_after()
    assert s.orders == (TOWN_RULE, ORDER_AC, ORDER_AD, ORDER_BC)
    assert (after.orders, after.latches) == ((TOWN_RULE, ORDER_BC), (s.latches[0], s.latches[3]))
    for t in (70, 120, 500):
        assert advance(s, r, t).orders == (TOWN_RULE, ORDER_BC), t


@kills(4, 6, 8)
def test_each_removed_order_is_logged_once_as_ended_left_with_the_level_of_the_store_it_read():
    """Invariant 150 and "Logged": the span holding T reports exactly RuleChange(T, o, False, level, Ended.LEFT) for
    the two orders of la: the time one has level None, the store one reads (y) has its amount at T (2 items)."""
    r, s, _ = before_and_after()
    step = advance_logged(s, r, T)
    assert value(step.save, r, Y, T) == 2 * Q
    assert ended_changes(step.rule_changes) == expected_ends(
        logged_end(T, ORDER_AC, None, "LEFT"), logged_end(T, ORDER_AD, 2 * Q, "LEFT"))
    assert not ended_changes(advance_logged(step.save, r, 500).rule_changes)


@kills(33)
def test_a_player_removing_an_order_is_not_logged_as_ended():
    """Invariant 143 (the rule log): a SetOrders that drops lb's order reports nothing ended."""
    r, s, _ = before_and_after()
    step = advance_logged(s, r, T)
    dropped = decide_logged(step.save, r, T + 5, SetOrders((TOWN_RULE,)))
    assert dropped.save.orders == (TOWN_RULE,) and not ended_changes(dropped.rule_changes)


# ---- 151: pays nothing mid-task -----------------------------------------------------------------------------------

def completions(save: Save, card: CardId, work_s: int) -> int:
    return next((c.work.start_value // (work_s * BP) for c in save.cards if c.card == card), 0)


@kills(3, 10)
def test_a_tap_under_way_when_the_person_leaves_gives_no_line_no_outcome_and_no_completion():
    """Invariant 151: ac (due at 70) is running at 39. Without the leave it lands at 70 (ac.done) and ad follows at 100;
    with it neither line appears, ac is not completed, and the lane is free from T."""
    r, s, after = before_and_after()
    c, sc = control()
    assert lane_card(s, LA) == AC and lane_card(after, LA) is None   # the premise, and the lane freed
    seen = [(ln.time, ln.key) for ln in advance_logged(sc, c, 500).lines]
    assert (70, AC_DONE) in seen and (100, AD_DONE) in seen   # the control shows the probe can see them
    lines = advance_logged(s, r, 500).lines
    assert not [ln for ln in lines if ln.key in (AC_DONE, AD_DONE) or ln.card in (AC, AD)]
    assert completions(advance(s, r, 500), AC, 50) == 0 == completions(after, AC, 50)


@kills(3)
def test_no_store_moves_by_the_task_after_the_leave_and_what_it_paid_by_its_rate_stays():
    """Invariant 151 and CHOICES step 2: ac pays 5 items of y over its 50 s; 20 s of work are done at T, so y is 2
    items at T and still 2 at 70 and at 500 (the control reaches 5)."""
    r, s, _ = before_and_after()
    c, sc = control()
    assert [stored(s, r, Y, t) for t in (T, 70, 500)] == [2 * Q] * 3
    assert stored(sc, c, Y, 500) == 5 * Q


# ---- 152: out of play ---------------------------------------------------------------------------------------------

@kills(11, 12)
@pytest.mark.parametrize("card", LA_CARDS)
def test_every_card_on_the_lane_is_retired_refused_and_in_no_list_while_its_unlock_stays(card: CardId):
    """Invariant 152 and CHOICES "Out of play": a player's tap raises InvalidVerbError, the card is in neither
    View.cards nor View.completed (nor is its lane in View.lanes), and Unlocked(CARD) of it stays true."""
    r, s, after = before_and_after()
    for t in LATER:
        v = view(advance(s, r, t), r)
        assert card not in {cv.card for cv in v.cards} | {cc.card for cc in v.completed}, t
        assert LA not in {lb.lane for lb in v.lanes} and LB in {lb.lane for lb in v.lanes}
        assert B1 in {cv.card for cv in v.cards}   # control: a card of lb is listed
        assert Unlock(UnlockKind.CARD, card) in v.unlocked
    with pytest.raises(InvalidVerbError):
        decide(after, r, T + 5, TapCard(card))


@kills(11, 12)
def test_a_saved_mix_may_not_take_a_left_card_back_but_may_hold_the_others():
    r, _, after = before_and_after()
    with pytest.raises(EngineError):
        decide(after, r, T + 5, SaveMix(Mix(TM, (CardShare(A1, BP),))))
    ok = decide(after, r, T + 5, SaveMix(Mix(TM, (CardShare(B1, 5000),))))
    assert mixes_by_id(ok)[TM] == Mix(TM, (CardShare(B1, 5000),))


@kills(12)
def test_an_order_tapping_a_left_card_is_accepted_and_passed_over():
    """CHOICES "Nothing lands on a left lane": SetOrders accepts it, and nothing runs on la."""
    r, _, after = before_and_after()
    tap = Order(AfterTime(0), TapCard(AC))
    s = decide(after, r, T + 5, SetOrders(after.orders + (tap,)))
    assert tap in advance(s, r, 300).orders
    assert lane_card(advance(s, r, 300), LA) is None and completions(advance(s, r, 300), AC, 50) == 0


@kills(5, 13)
def test_the_listed_standing_stops_for_good_and_the_unlisted_one_runs_on():
    """Invariant 152: `stop` contributes 0 to every rate, is absent from View.standing and its share in explain is 0,
    while `keep` runs at BP; both stay unlocked. z stands at 40 items from T, z2 reaches 500."""
    r, s, after = before_and_after()
    c, sc = control()
    stop_ref, keep_ref = RateRef(STOP, FlowKind.MAKE, Z), RateRef(KEEP, FlowKind.MAKE, Z2)
    assert explain(sc, c, stop_ref).share_bp == BP and STOP in {b.action for b in view(sc, c).standing}   # control
    for t in LATER:
        a = advance(s, r, t)
        assert explain(a, r, stop_ref).share_bp == 0 and explain(a, r, stop_ref).per_hour == 0
        assert explain(a, r, keep_ref).share_bp == BP
        assert [b.action for b in view(a, r).standing] == [KEEP]
        assert {Unlock(UnlockKind.ACTION, STOP), Unlock(UnlockKind.ACTION, KEEP)} <= set(view(a, r).unlocked)
    assert (stored(s, r, Z, T), stored(s, r, Z, 500), stored(s, r, Z2, 500)) == (40 * Q, 40 * Q, 500 * Q)
    assert all(b.run == RunKind.FULL for b in view(after, r).standing)


@kills(14)
def test_an_order_reading_a_stopped_actions_unlock_still_finds_it_held():
    """Invariant 152: Unlocked(ACTION) of the stopped `stop` stays true where a rule reads it: an order set after the
    leave on that condition is latched on, as it is in the world where nobody left."""
    gate = Order(AtLeast(Unlocked(Unlock(UnlockKind.ACTION, STOP)), 1, 1), TapCard(H1))
    r, _, after = before_and_after()
    c, sc = control()
    for rl, sv in ((c, advance(sc, c, T + 10)), (r, advance(after, r, T + 10))):
        latched = decide(sv, rl, T + 10, SetOrders((*sv.orders, gate)))
        assert dict(zip(latched.orders, latched.latches))[gate]


@kills(15)
def test_a_start_on_the_left_lane_changes_nothing():
    """CHOICES "Nothing lands on a left lane": a trigger at 110 starting a2 taps it where nobody left (control) and
    does nothing where la has gone."""
    start = TriggerDef(TriggerId("start"), AfterTime(110), Outcome(starts=(A2,)))
    c, r = rules(None, extra=(start,)), rules(T, extra=(start,))
    assert lane_card(advance(scene(c), c, 111), LA) == A2   # control
    a = advance(scene(r), r, 300)
    assert lane_card(a, LA) is None and stored(scene(r), r, W, 300) == stored(scene(r), r, W, T)
