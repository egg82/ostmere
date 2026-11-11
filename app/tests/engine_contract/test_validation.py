"""Invariant 17: every documented invalid rule shape raises InvalidRulesError, every invalid verb InvalidVerbError.
Each invalid case is paired with a valid control so a validator that rejects everything cannot pass."""
from dataclasses import replace

import pytest
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, HANDS, ActionId, Amount, AfterTime, AtLeast, AtMost, CapRaise, CardId, CardShare, DeleteMix, Flow,
    InvalidRulesError, InvalidVerbError, LaneDef, LaneId, LineKey, Mix, Modifier, ModifierKind, Order, Outcome,
    PacingCurve, QueueEntry, SaveMix, SetOrders, SetQueue, SkillDef, SkillId, SourceId, StandingDef, StoreDef,
    StoreValue, SubMix, SwitchMix, TapCard, TimeOrderError, Unlock, UnlockKind, WorkRef, advance, decide,
    flatten_shares, new_save, validate_rules, value, StoreId, CardDef, Rules,
)
from contract_gen import Q, SK, card, card_id, make_rules, mix_id, rules_st, store_id

S0, S1 = store_id(0), store_id(1)
A0, A1, A2 = card_id(0), card_id(1), card_id(2)
RACK = LaneId("rack")
FIRE = ActionId("fire")


def good_rules():
    """Cards c0 and c1 on HANDS (mixable), c2 on the declared lane `rack` (tapped only), one standing action."""
    r = make_rules(
        [StoreDef(S0, 10 * Q, Q), StoreDef(S1, 10 * Q)],
        [card(0, 100, (Flow(S0, 500),), (Flow(S1, 200),)), card(1, 0, (), (Flow(S0, 100),)),
         replace(card(2), lane=RACK)],
        thresholds=(Q, 2 * Q))
    return replace(r, lanes=(LaneDef(RACK),), standing=(StandingDef(FIRE, (Flow(S1, 50),)),))


def _bad_rules():
    g = good_rules()
    a0 = g.cards[0]

    def with_card(c: CardDef):
        return replace(g, cards=(c,) + g.cards[1:])

    return {
        "duplicate store id": replace(g, stores=g.stores + (g.stores[0],)),
        "duplicate card id": replace(g, cards=g.cards + (g.cards[0],)),
        "card id clashes with a standing action": replace(g, standing=(StandingDef(ActionId(A0)),)),
        "duplicate skill id": replace(g, skills=g.skills + (SkillDef(SK),)),
        "card trains unknown skill": with_card(replace(a0, skill=SkillId("nope"))),
        "card has xp but no skill": with_card(replace(a0, skill=None)),
        "make of unknown store": with_card(replace(a0, makes=(Flow(StoreId("zz"), 5),))),
        "cost of unknown store": with_card(replace(a0, costs=(Flow(StoreId("zz"), 5),))),
        "cap zero": replace(g, stores=(StoreDef(S0, 0, 0), g.stores[1])),
        "cap negative": replace(g, stores=(StoreDef(S0, -5, 0), g.stores[1])),
        "initial above cap": replace(g, stores=(StoreDef(S0, Q, Q + 1), g.stores[1])),
        "initial negative": replace(g, stores=(StoreDef(S0, Q, -1), g.stores[1])),
        "negative make rate": with_card(replace(a0, makes=(Flow(S0, -1),))),
        "negative cost rate": with_card(replace(a0, costs=(Flow(S1, -1),))),
        "makes and costs one store": with_card(replace(a0, costs=(Flow(S0, 5),))),
        "standing action makes and costs one store": replace(g, standing=(StandingDef(FIRE, (Flow(S1, 50),), (Flow(S1, 20),)),)),
        "store twice in makes": with_card(replace(a0, makes=(Flow(S0, 5), Flow(S0, 6)))),
        "store twice in costs": with_card(replace(a0, costs=(Flow(S1, 5), Flow(S1, 6)))),
        # the card rules (DESIGN.txt, "Validation of cards")
        "work_s zero": with_card(replace(a0, work_s=0)),
        "card cap zero": with_card(replace(a0, cap=0)),
        "card on an undeclared lane": with_card(replace(a0, lane=LaneId("nope"))),
        "declared lane named HANDS": replace(g, lanes=g.lanes + (LaneDef(HANDS),)),
        "input of an unknown store": with_card(replace(a0, inputs=(Amount(StoreId("zz"), Q),))),
        "input of zero": with_card(replace(a0, inputs=(Amount(S1, 0),))),
        "outcome store of zero": with_card(replace(a0, outcome=Outcome(stores=(Amount(S0, 0),)))),
        "input on a store the card makes": with_card(replace(a0, inputs=(Amount(S0, Q),))),
        "outcome store on a store the card costs": with_card(replace(a0, outcome=Outcome(stores=(Amount(S1, Q),)))),
        "input on a store the card costs": with_card(replace(a0, inputs=(Amount(S1, Q),))),
        "outcome store on a store the card makes": with_card(replace(a0, outcome=Outcome(stores=(Amount(S0, Q),)))),
        "store twice in inputs": with_card(replace(a0, makes=(), costs=(), inputs=(Amount(S0, Q), Amount(S0, 2 * Q)))),
        "store twice in outcome stores": with_card(
            replace(a0, makes=(), costs=(), outcome=Outcome(stores=(Amount(S0, Q), Amount(S0, 2 * Q))))),
        "input and outcome store on one store": with_card(
            replace(a0, makes=(), costs=(), inputs=(Amount(S0, Q),), outcome=Outcome(stores=(Amount(S0, Q),)))),
        "uncapped card with a discrete outcome": with_card(
            replace(a0, outcome=Outcome(unlocks=(Unlock(UnlockKind.CARD, A1),)))),
        "uncapped card with finished": with_card(replace(a0, finished=Outcome(stores=(Amount(S0, Q),)))),
        "uncapped card with two lines": with_card(replace(a0, lines=(LineKey("x"), LineKey("y")))),
        "capped card with the wrong number of lines": with_card(replace(a0, cap=3, lines=(LineKey("x"), LineKey("y")))),
        "cap raise of an uncapped card": with_card(
            replace(a0, cap=1, outcome=Outcome(raises=(CapRaise(A1, 1),)))),
        "cap raise by zero": with_card(replace(a0, cap=1, outcome=Outcome(raises=(CapRaise(A0, 0),)))),
        "outcome starts an unknown card": with_card(replace(a0, cap=1, outcome=Outcome(starts=(CardId("zz"),)))),
        "outcome taps a HANDS card from a HANDS completion": with_card(
            replace(a0, cap=1, outcome=Outcome(starts=(A1,)))),
        "thresholds not increasing": replace(g, curve=PacingCurve((Q, Q))),
        "thresholds decreasing": replace(g, curve=PacingCurve((2 * Q, Q))),
        "first threshold zero": replace(g, curve=PacingCurve((0, Q))),
        "firing cap below 1": replace(g, max_firings_per_instant=0),
    }


def test_the_valid_control_passes():
    """Invariant 17 (validation): the baseline rules the invalid cases are derived from are accepted, and so are
    the look-alikes of the card shapes above that are legal: a capped card with one line per completion, an unlock,
    a finished outcome and a raise of a capped card, a HANDS completion that taps a card on another lane, an input
    and an outcome store on two stores the card does not otherwise use (each store appears once across a card's makes,
    costs, inputs and outcome stores)."""
    g = good_rules()
    validate_rules(g)
    capped = replace(g.cards[0], cap=2, lines=(LineKey("x"), LineKey("y")), makes=(), costs=(),
                     inputs=(Amount(S1, Q),),
                     outcome=Outcome(unlocks=(Unlock(UnlockKind.CARD, A1),), raises=(CapRaise(A1, 1),),
                                     starts=(A2,), stores=(Amount(S0, Q),)),
                     finished=Outcome(lines=(LineKey("fin"),)))
    validate_rules(replace(g, cards=(capped, replace(g.cards[1], cap=1)) + g.cards[2:]))


@pytest.mark.parametrize("name", sorted(_bad_rules()))
def test_each_invalid_rule_shape_is_rejected(name: str):
    """Invariant 17 (validation): each documented invalid rule shape raises InvalidRulesError."""
    with pytest.raises(InvalidRulesError):
        validate_rules(_bad_rules()[name])


@given(rules_st())
def test_generated_valid_rules_are_accepted(rules: Rules):
    """Invariant 17 (validation): rules built from the documented constraints are never rejected."""
    validate_rules(rules)


def _world():
    r = good_rules()
    s = new_save(r)
    for v in (SaveMix(Mix(mix_id(0), (CardShare(A0, 5000), CardShare(A1, 5000)))),
              SaveMix(Mix(mix_id(1), (SubMix(mix_id(0), 5000),))),
              SwitchMix(mix_id(0))):
        s = decide(s, r, 0, v)
    return r, s


def _bad_verbs():
    m = mix_id
    return {
        "share sum above 100%": SaveMix(Mix(m(5), (CardShare(A0, 6000), CardShare(A1, 5000)))),
        "share above 100%": SaveMix(Mix(m(5), (CardShare(A0, BP + 1),))),
        "negative share": SaveMix(Mix(m(5), (CardShare(A0, -1),))),
        "unknown card": SaveMix(Mix(m(5), (CardShare(card_id(9), 100),))),
        "card on another lane": SaveMix(Mix(m(5), (CardShare(A2, 100),))),
        "standing action as a card": SaveMix(Mix(m(5), (CardShare(CardId(FIRE), 100),))),
        "unknown sub-mix": SaveMix(Mix(m(5), (SubMix(m(9), 100),))),
        "self-nesting cycle": SaveMix(Mix(m(5), (SubMix(m(5), 100),))),
        "cycle through a saved mix": SaveMix(Mix(m(0), (SubMix(m(1), 100),))),
        "switch to an unsaved mix": SwitchMix(m(9)),
        "tap of an unknown card": TapCard(CardId("zz")),
        "delete an unsaved mix": DeleteMix(m(9)),
        "delete a mix nested in another": DeleteMix(m(0)),
        "AtLeast release above value": SetOrders((Order(AtLeast(StoreValue(S0), Q, Q + 1), SwitchMix(m(0))),)),
        "AtMost release below value": SetOrders((Order(AtMost(StoreValue(S0), Q, Q - 1), SwitchMix(m(0))),)),
        "order names an unsaved mix": SetOrders((Order(AfterTime(5), SwitchMix(m(9))),)),
        "queue release on the wrong side": SetQueue((QueueEntry(SwitchMix(m(0)), AtLeast(StoreValue(S0), Q, Q + 1)),)),
        "queue names an unsaved mix": SetQueue((QueueEntry(SwitchMix(m(9)), AfterTime(5)),)),
    }


def test_valid_verb_controls_are_accepted():
    """Invariant 17 (validation): valid look-alikes of the invalid verbs are accepted (shares exactly 100%,
    release == value, an empty queue)."""
    r, s = _world()
    for v in (SaveMix(Mix(mix_id(5), (CardShare(A0, 5000), CardShare(A1, 5000)))),
              SetOrders((Order(AtLeast(StoreValue(S0), Q, Q), SwitchMix(mix_id(0))),)),
              SetOrders((Order(AtMost(StoreValue(S0), Q, Q + 5), SwitchMix(mix_id(1))),)),
              SetQueue(()), SwitchMix(mix_id(1))):
        decide(s, r, 5, v)


@pytest.mark.parametrize("name", sorted(_bad_verbs()))
def test_each_invalid_verb_is_rejected(name: str):
    """Invariant 17 (validation): each documented invalid verb raises InvalidVerbError."""
    r, s = _world()
    with pytest.raises(InvalidVerbError):
        decide(s, r, 5, _bad_verbs()[name])


def test_a_negative_multiplier_is_refused_where_the_stack_starts():
    """Invariant 17 (validation), Modifier: a MUL_BP factor is >= 0 (zero stops a line), so new_save refuses a starting
    stack holding a negative one."""
    r = good_rules()
    new_save(r, (Modifier(WorkRef(A0), ModifierKind.MUL_BP, 0, SourceId("s")),))
    with pytest.raises(InvalidVerbError):
        new_save(r, (Modifier(WorkRef(A0), ModifierKind.MUL_BP, -1, SourceId("s")),))


def _plan_world():
    """The world plus mixes m2 and m3, named by an order and by a queue entry (neither fires: their conditions are
    far off)."""
    r, s = _world()
    for v in (SaveMix(Mix(mix_id(2), (CardShare(A0, 100),))), SaveMix(Mix(mix_id(3), (CardShare(A1, 100),))),
              SetOrders((Order(AfterTime(10**9), SwitchMix(mix_id(2))),)),
              SetQueue((QueueEntry(SwitchMix(mix_id(3)), AfterTime(10**9)),))):
        s = decide(s, r, 0, v)
    return r, s


def test_delete_mix_refuses_a_named_mix_and_deletes_a_free_one():
    """Invariants 17, 42 (validation, DeleteMix): a mix named by an order or by a queue entry is refused, a free one
    is gone afterwards and the others keep their order; a mix nested in another is refused until the outer is gone.
    The controls show each refusal is about its own reason."""
    r, s = _plan_world()
    for named in (mix_id(2), mix_id(3)):
        with pytest.raises(InvalidVerbError):
            decide(s, r, 5, DeleteMix(named))
    gone = decide(s, r, 5, DeleteMix(mix_id(1)))  # m1 nests m0, but nothing nests or names m1
    assert [m.id for m in gone.mixes] == [mix_id(0), mix_id(2), mix_id(3)]
    with pytest.raises(InvalidVerbError):
        decide(s, r, 5, DeleteMix(mix_id(0)))  # nested in m1
    assert [m.id for m in decide(gone, r, 5, DeleteMix(mix_id(0))).mixes] == [mix_id(2), mix_id(3)]
    cleared = decide(gone, r, 5, SetOrders(()))  # m2 is no longer named
    assert [m.id for m in decide(cleared, r, 5, DeleteMix(mix_id(2))).mixes] == [mix_id(0), mix_id(3)]


def test_deleting_the_active_mix_leaves_none_active():
    """Invariant 42 (DeleteMix): deleting the active mix leaves no mix active."""
    r = good_rules()
    s = decide(new_save(r), r, 0, SaveMix(Mix(mix_id(0), (CardShare(A0, BP),))))
    s = decide(s, r, 0, SwitchMix(mix_id(0)))
    assert s.active == mix_id(0)
    s = decide(s, r, 7, DeleteMix(mix_id(0)))
    assert s.active is None and s.mixes == ()


def test_flatten_shares_rejects_unknown_ids_and_cycles():
    """Invariant 17 (validation): flatten_shares raises InvalidVerbError on an unknown mix id or a nesting cycle."""
    mixes = (Mix(mix_id(0), (CardShare(A0, 5000), CardShare(A1, 5000))), Mix(mix_id(1), (SubMix(mix_id(0), 5000),)))
    assert flatten_shares(mixes, mix_id(1))  # control: a real mix flattens
    with pytest.raises(InvalidVerbError):
        flatten_shares(mixes, mix_id(9))
    cyc = (Mix(mix_id(0), (SubMix(mix_id(1), 100),)), Mix(mix_id(1), (SubMix(mix_id(0), 100),)))
    with pytest.raises(InvalidVerbError):
        flatten_shares(cyc, mix_id(0))


def test_nested_shares_are_compositional():
    """Invariant 17 (validation, mixes): an inner mix is flattened first (floored, repeats summed), then scaled ONCE
    by the outer share and floored. The example gives three different numbers under the three readings: floor along
    each path (a0 438, a1 427), compositional (439, 428), floor once at the end (440, 429)."""
    mixes = (Mix(mix_id(0), (CardShare(A0, 2941), CardShare(A1, 1842))),
             Mix(mix_id(1), (SubMix(mix_id(0), 2869), SubMix(mix_id(0), 1249), CardShare(A1, 553))),
             Mix(mix_id(2), (SubMix(mix_id(1), 3272), CardShare(A0, 44))))
    assert flatten_shares(mixes, mix_id(0)) == (CardShare(A0, 2941), CardShare(A1, 1842))
    # mix 1: a0 = 2941*2869//BP + 2941*1249//BP = 843 + 367 = 1210 ; a1 = 528 + 230 + 553 = 1311
    assert flatten_shares(mixes, mix_id(1)) == (CardShare(A0, 1210), CardShare(A1, 1311))
    # mix 2: a0 = 1210*3272//BP + 44 = 395 + 44 = 439 (first position) ; a1 = 1311*3272//BP = 428
    assert flatten_shares(mixes, mix_id(2)) == (CardShare(A0, 439), CardShare(A1, 428))


@given(back=st.integers(1, 1000))
def test_time_cannot_run_backwards(back: int):
    """Invariant 17 (validation): a time before save.time raises TimeOrderError from advance, decide and value."""
    r, s = _world()
    s = advance(s, r, 2000)
    for call in (lambda: advance(s, r, s.time - back), lambda: decide(s, r, s.time - back, SwitchMix(mix_id(1))),
                 lambda: value(s, r, S0, s.time - back)):
        with pytest.raises(TimeOrderError):
            call()
