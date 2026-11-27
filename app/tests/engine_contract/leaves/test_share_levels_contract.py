"""Invariants 162-166 (SHARE LEVELS): a level given as basis points of the watched store's cap is read against the cap
at the instant the condition is read. The store's whole items k are compared with the exact share x = b * C / BP of
the cap's whole items C: an at_most holds while k <= x and lets go once k >= its release's x; an at_least holds once
k >= x and lets go once k <= its release's x. A release read on the wrong side of the value is read as the value.
Expected values here come from that statement, in whole items and exact fractions."""
from fractions import Fraction

import pytest
from hypothesis import given, settings, strategies as st

from ashfall_app.engine import (
    BP, AtLeast, AtMost, CardCount, CardShare, ChipDef, ChipId, Flow, InvalidRulesError, InvalidVerbError, Latch, Mix,
    Modifier, ModifierKind, Order, Outcome, QueueEntry, Rules, Save, SaveMix, SetOrders, SetQueue, SkillLevel, SourceId,
    SkillId, StoreCap, StoreDef, StoreValue, SwitchMix, TriggerDef, TriggerId, AfterTime, advance, advance_logged, decide, decode,
    encode, new_save, validate_rules,
)
from contract_gen import Q, card, card_id, make_rules, mix_id, store_id
from leaves_world import kills

S0 = store_id(0)
FILL, DRAIN = mix_id(0), mix_id(1)
H = 3600
QUARTER, HALF, FULL = BP // 4, BP // 2, BP


def _rules(cap: int, initial: int, *, raise_at: int | None = None, fill: int = 2000, drain: int = 1000) -> Rules:
    """S0 with `cap` and `initial` (quantities); FILL = {c0 making `fill`/h}, DRAIN = {c1 costing `drain`/h}. With
    `raise_at`, a trigger doubles S0's cap at that second."""
    rules = make_rules([StoreDef(S0, cap, initial)], [card(0, 0, (Flow(S0, fill),), ()), card(1, 0, (), (Flow(S0, drain),))])
    if raise_at is None:
        return rules
    double = Modifier(StoreCap(S0), ModifierKind.MUL_BP, 2 * BP, SourceId("raise"))
    return Rules(rules.stores, rules.skills, rules.standing, rules.curve, rules.max_firings_per_instant,
                 cards=rules.cards, triggers=(TriggerDef(TriggerId("raise"), AfterTime(raise_at), Outcome(modifiers=(double,))),))


def _world(rules: Rules, order: Order, player: str) -> Save:
    s = new_save(rules)
    for v in (SaveMix(Mix(FILL, (CardShare(card_id(0), BP),))), SaveMix(Mix(DRAIN, (CardShare(card_id(1), BP),))),
              SwitchMix(mix_id(1) if player == "drain" else mix_id(0)), SetOrders((order,))):
        s = decide(s, rules, 0, v)
    return s


def _changes(rules: Rules, s: Save, until: int) -> list[tuple[int, bool, int]]:
    """(time, on, amount of S0) for each latch change of the save's one order up to `until`."""
    return [(c.time, c.on, c.level) for c in advance_logged(s, rules, until).rule_changes if c.level is not None]


def _latch(cap: int, store: int, cond: AtLeast | AtMost) -> Latch:
    """The latch SetOrders gives a new order on S0 at `store` of `cap` (latched afresh from its value alone)."""
    rules = _rules(cap, store)
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(FILL, (CardShare(card_id(0), BP),))))
    return decide(s, rules, 0, SetOrders((Order(cond, SwitchMix(FILL)),))).latches[0]


def _down_to(value_bp: int, release_bp: int) -> AtMost:
    return AtMost(StoreValue(S0), value_bp, release_bp, value_of_cap=True, release_of_cap=True)


def _up_to(value_bp: int, release_bp: int) -> AtLeast:
    return AtLeast(StoreValue(S0), value_bp, release_bp, value_of_cap=True, release_of_cap=True)


# ---- invariant 163: the same share across a cap rise -------------------------------------------------------------

@kills(7)
def test_a_share_level_crosses_at_the_same_share_before_and_after_the_cap_rises():
    """"Down to half, until full" refilling S0 (8 of 10, drained at 1/h, refilled at 2/h): before the raise it comes
    on when S0 shows 5 and lets go at 10; the cap doubles at 9h while it refills, and from then on it lets go at 20 and
    comes on when S0 shows 10."""
    rules = _rules(10 * Q, 8 * Q, raise_at=9 * H)
    s = _world(rules, Order(_down_to(HALF, FULL), SwitchMix(FILL)), "drain")
    ch = _changes(rules, s, 40 * H)
    before = [c for c in ch if c[0] < 9 * H]
    after = [c for c in ch if c[0] > 9 * H]
    assert [on for _, on, _ in before[:3]] == [True, False, True]
    assert [lv // Q for _, on, lv in before if on] == [5] * len([c for c in before if c[1]])
    assert [lv for _, on, lv in before if not on] == [10 * Q]
    assert after[0][1] is False and after[0][2] == 20 * Q
    assert after[1][1] is True and after[1][2] // Q == 10


def test_an_amount_level_crosses_at_the_same_number_before_and_after_the_cap_rises():
    """The same world with "under 6, until 10" as amounts: after the cap doubles it still lets go at 10 and comes on
    when S0 shows 5."""
    rules = _rules(10 * Q, 8 * Q, raise_at=9 * H)
    s = _world(rules, Order(AtMost(StoreValue(S0), 6 * Q - 1, 10 * Q - 1), SwitchMix(FILL)), "drain")
    ch = _changes(rules, s, 40 * H)
    assert {lv // Q for _, on, lv in ch if on} == {5}
    assert {lv // Q for _, on, lv in ch if not on} == {10}
    assert any(t > 9 * H for t, _, _ in ch)


# ---- invariant 164: full and empty ---------------------------------------------------------------------------------

@kills(7)
def test_full_is_the_live_cap_and_empty_is_nothing_shown():
    """"Up to full, until empty" draining S0 (filled at 1/h, drained at 2/h, from 0 of 10): it comes on at 10 and lets
    go once S0 shows 0; after the cap doubles at 15h it comes on at 20, not 10."""
    rules = _rules(10 * Q, 0, raise_at=15 * H, fill=1000, drain=2000)
    s = _world(rules, Order(_up_to(FULL, 0), SwitchMix(DRAIN)), "fill")
    ch = _changes(rules, s, 60 * H)
    ons = [(t, lv) for t, on, lv in ch if on]
    offs = [lv for _, on, lv in ch if not on]
    assert ons[0] == (10 * H, 10 * Q)
    assert all(lv // Q == 0 for lv in offs) and offs
    assert [lv for t, lv in ons if t > 15 * H] == [20 * Q]


def test_an_amount_at_the_old_full_no_longer_means_full_after_a_raise():
    """The control for the test above: "10 or more, until under 1" as amounts comes on at 10 after the raise too."""
    rules = _rules(10 * Q, 0, raise_at=15 * H, fill=1000, drain=2000)
    s = _world(rules, Order(AtLeast(StoreValue(S0), 10 * Q, Q), SwitchMix(DRAIN)), "fill")
    ch = _changes(rules, s, 60 * H)
    assert {lv for t, on, lv in ch if on and t > 15 * H} == {10 * Q}


@kills(5)
def test_full_of_a_cap_that_is_not_whole_items_is_its_whole_items():
    """A cap of 10.5 items reads as 10 whole items: "up to full" holds at 10, and not at 9.99."""
    cap = 10 * Q + Q // 2
    assert _latch(cap, 10 * Q, _up_to(FULL, HALF)) is True
    assert _latch(cap, 10 * Q - 1, _up_to(FULL, HALF)) is False


@kills(6)
def test_an_at_most_down_to_empty_holds_only_while_nothing_shows():
    assert _latch(10 * Q, Q - 1, _down_to(0, HALF)) is True
    assert _latch(10 * Q, Q, _down_to(0, HALF)) is False


# ---- the reading, as whole items against the exact share ---------------------------------------------------------

@kills(1, 6, 10)
def test_a_quarter_of_ten_holds_an_at_most_at_two_and_an_at_least_at_three():
    for store, below, above in ((2 * Q, True, False), (3 * Q - 1, True, False), (3 * Q, False, True)):
        assert _latch(10 * Q, store, _down_to(QUARTER, FULL)) is below, store
        assert _latch(10 * Q, store, _up_to(QUARTER, 0)) is above, store


@settings(max_examples=60, deadline=None)
@given(cap_items=st.integers(1, 40), cap_extra=st.integers(0, Q - 1), b=st.integers(0, BP),
       frac=st.fractions(0, 1), at_most=st.booleans())
def test_a_value_level_is_the_shown_amount_against_the_exact_share(cap_items: int, cap_extra: int, b: int,
                                                                 frac: Fraction, at_most: bool):
    """Invariant 162 on the latch SetOrders gives: any cap, any store value, any share."""
    cap = cap_items * Q + cap_extra
    store = int(frac * cap)
    k, x = store // Q, Fraction(b * (cap // Q), BP)
    cond = _down_to(b, BP) if at_most else _up_to(b, 0)
    assert _latch(cap, store, cond) is (k <= x if at_most else k >= x)


def test_an_at_least_until_a_quarter_lets_go_once_two_show():
    """"Up to full, until a quarter" draining from full: a quarter of 10 is 2.5, so it lets go when S0 shows 2."""
    rules = _rules(10 * Q, 10 * Q, fill=1000, drain=2000)
    s = _world(rules, Order(_up_to(FULL, QUARTER), SwitchMix(DRAIN)), "fill")
    offs = [lv for _, on, lv in _changes(rules, s, 30 * H) if not on]
    assert offs and all(lv // Q == 2 for lv in offs)


def test_an_at_most_until_a_quarter_lets_go_once_three_show():
    """"Down to empty, until a quarter" refilling from 0: it lets go when S0 shows 3 (the first whole amount at or
    over 2.5), and comes on again when it shows 0."""
    rules = _rules(10 * Q, Q // 2, fill=2000, drain=1000)
    s = _world(rules, Order(_down_to(0, QUARTER), SwitchMix(FILL)), "drain")
    ch = _changes(rules, s, 30 * H)
    assert ch[0][2] == 3 * Q
    assert [lv // Q for _, on, lv in ch if not on] == [3] * len([c for c in ch if not c[1]])
    assert [lv // Q for _, on, lv in ch if on] == [0] * len([c for c in ch if c[1]])


# ---- invariant 167: a band of one item ----------------------------------------------------------------------------

@kills(2)
def test_two_shares_that_meet_in_whole_items_keep_a_band_of_one_item():
    """A quarter and half of a 4-item cap read 1 and 2: "down to a quarter, until half" comes on when S0 shows 1 and
    lets go at 3, one item past 2; "up to half, until a quarter" comes on at 2 and lets go once S0 shows 0. Each run
    stops at its first change, so a band that is missing flips at most a few times before the check."""
    down = Order(_down_to(QUARTER, HALF), SwitchMix(FILL))
    rules = _rules(4 * Q, Q // 2)
    assert [(on, lv // Q) for _, on, lv in _changes(rules, _world(rules, down, "drain"), 4600)][:1] == [(False, 3)]
    rules = _rules(4 * Q, 3 * Q)
    assert [(on, lv // Q) for _, on, lv in _changes(rules, _world(rules, down, "drain"), 4000)][:1] == [(True, 1)]
    up = Order(_up_to(HALF, QUARTER), SwitchMix(DRAIN))
    rules = _rules(4 * Q, 2 * Q, fill=1000, drain=2000)
    assert [(on, lv // Q) for _, on, lv in _changes(rules, _world(rules, up, "fill"), 2000)][:1] == [(False, 0)]
    rules = _rules(4 * Q, 3 * Q // 2, fill=1000, drain=2000)
    assert [(on, lv // Q) for _, on, lv in _changes(rules, _world(rules, up, "fill"), 1900)][:1] == [(True, 2)]


@kills(3, 4)
def test_the_band_never_reaches_past_full_or_under_nothing_shown():
    """Where a value level is within one item of full or empty there is no room for the band, and the rule is a plain
    threshold rather than one that can never let go: on a 4-item cap "down to three quarters, until full" lets go at
    full, and "up to a quarter, until empty" lets go once S0 shows 0."""
    rules = _rules(4 * Q, 3 * Q)
    ch = _changes(rules, _world(rules, Order(_down_to(3 * QUARTER, FULL), SwitchMix(FILL)), "drain"), 2000)
    assert [(on, lv) for _, on, lv in ch[:1]] == [(False, 4 * Q)]
    rules = _rules(4 * Q, 2 * Q, fill=1000, drain=2000)
    ch = _changes(rules, _world(rules, Order(_up_to(QUARTER, 0), SwitchMix(DRAIN)), "fill"), 2000)
    assert ch and ch[0][1] is False and ch[0][2] // Q == 0


def test_a_release_the_cap_puts_inside_the_value_moves_one_item_past_it():
    """"Under 8 (an amount), until half (a share)" on a 10-item cap: half is 5, inside the value, so the rule lets go
    at 9, one item past where it comes on. After the cap doubles, half is 10 and it lets go at 10."""
    rules = _rules(10 * Q, 9 * Q, raise_at=2 * H)
    cond = AtMost(StoreValue(S0), 8 * Q - 1, HALF, release_of_cap=True)
    s = _world(rules, Order(cond, SwitchMix(FILL)), "drain")
    ch = _changes(rules, s, 13_000)
    before = [lv for t, on, lv in ch if not on and t < 2 * H]
    after = [lv for t, on, lv in ch if not on and t > 2 * H]
    assert before and {lv // Q for lv in before} == {9}
    assert after and {lv // Q for lv in after} == {10}


def test_a_latch_keeps_its_state_through_a_raise_and_the_new_release_decides():
    """"Up to full, until three quarters", on at full (10) when the cap doubles: three quarters of 20 is 15, and S0
    is under it, so it lets go at that instant. "Up to full, until a quarter" in the same place stays on."""
    for release, lets_go in ((3 * QUARTER, True), (QUARTER, False)):
        rules = _rules(10 * Q, 10 * Q, raise_at=H, fill=1000, drain=1)
        s = _world(rules, Order(_up_to(FULL, release), SwitchMix(DRAIN)), "fill")
        assert s.latches == (True,)
        a = advance(s, rules, H)
        assert a.latches == ((not lets_go),), release


# ---- invariant 165: amounts encode as before ----------------------------------------------------------------------

def test_an_amount_condition_writes_no_share_fields_and_a_share_one_round_trips():
    rules = _rules(10 * Q, 5 * Q)
    plain = _world(rules, Order(AtMost(StoreValue(S0), 3 * Q - 1, 8 * Q - 1), SwitchMix(FILL)), "drain")
    text = encode(plain, rules)
    assert "of_cap" not in text and decode(text, rules) == plain
    share = _world(rules, Order(_down_to(QUARTER, FULL), SwitchMix(FILL)), "drain")
    text = encode(share, rules)
    assert "value_of_cap" in text and decode(text, rules) == share
    q = decide(share, rules, 0, SetQueue((QueueEntry(SwitchMix(FILL), _up_to(FULL, FULL)),)))
    assert decode(encode(q, rules), rules) == q


# ---- invariant 166: validation -------------------------------------------------------------------------------------

@pytest.mark.parametrize("cond", [
    AtLeast(SkillLevel(SkillId("k0")), 5000, 5000, value_of_cap=True),
    AtLeast(CardCount(card_id(0)), 1, 1, release_of_cap=True),
    AtMost(StoreValue(S0), BP + 1, BP + 1, value_of_cap=True, release_of_cap=True),
    AtMost(StoreValue(S0), -1, BP, value_of_cap=True, release_of_cap=True),
    AtLeast(StoreValue(S0), BP, -1, value_of_cap=True, release_of_cap=True),
    AtMost(StoreValue(S0), HALF, QUARTER, value_of_cap=True, release_of_cap=True),
    AtLeast(StoreValue(S0), QUARTER, HALF, value_of_cap=True, release_of_cap=True),
])
def test_a_share_level_off_a_store_out_of_range_or_on_the_wrong_side_is_refused(cond: AtLeast | AtMost):
    rules = _rules(10 * Q, 5 * Q)
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(FILL, (CardShare(card_id(0), BP),))))
    with pytest.raises(InvalidVerbError):
        decide(s, rules, 0, SetOrders((Order(cond, SwitchMix(FILL)),)))
    with pytest.raises(InvalidVerbError):
        decide(s, rules, 0, SetQueue((QueueEntry(SwitchMix(FILL), cond),)))


@kills(9)
def test_a_share_level_and_an_amount_level_together_are_not_compared():
    """A mixed band is never refused for its sides: a share and a quantity are on different scales."""
    rules = _rules(10 * Q, 5 * Q)
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(FILL, (CardShare(card_id(0), BP),))))
    for cond in (AtMost(StoreValue(S0), 8 * Q - 1, HALF, release_of_cap=True),
                 AtLeast(StoreValue(S0), FULL, 2 * Q, value_of_cap=True)):
        decide(s, rules, 0, SetOrders((Order(cond, SwitchMix(FILL)),)))


@kills(8)
def test_a_share_level_in_the_rules_is_refused():
    base = _rules(10 * Q, 5 * Q)
    share = _up_to(FULL, FULL)
    chip = Rules(base.stores, base.skills, base.standing, base.curve, cards=base.cards,
                 chips=(ChipDef(ChipId("full"), share),))
    trigger = Rules(base.stores, base.skills, base.standing, base.curve, cards=base.cards,
                    triggers=(TriggerDef(TriggerId("full"), share, Outcome()),))
    for rules in (chip, trigger):
        with pytest.raises(InvalidRulesError):
            validate_rules(rules)
