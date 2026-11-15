"""Rule guards, shape and validation (docs/design/rule-guards.md, "Contract (blind)", statements 1 to 4; "The saved
shape"; "What a rule is", its limits). The old text is fixtures/pre_guards.json, written by the engine before Order had
`unless` or `or_else`, from ORDERS played by `play`; it is never rewritten. Each refusal has an accepted rule beside it,
so a refusal for some other reason cannot pass."""
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, AnswerDef, AnswerId, AnswerOffer, AtLeast, AtMost, Condition, InvalidVerbError, LaneId, LaneRules, OfferDef, OfferId,
    Order, Outcome, Rules, Save, SetOrders, SkillLevel, StoreValue, SwitchMix, TapCard, advance, advance_logged,
    decide, decode, encode, verb_from_json, verb_to_json,
)
from contract_gen import SK, few
from guards_world import (
    kills,
    ALWAYS, J, K, K2, K3, K4, KL, RM, RM2, T, W, Q, at_least, at_most, block_from, guarded, guarded_latch, order,
    rules, start, with_else,
)
import town_mix_world as town

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pre_guards.json"
ORDERS = (
    Order(at_least(10, 9), TapCard(K)),
    Order(at_most(5, 6, W), SwitchMix(RM)),
    Order(AtLeast(StoreValue(T), BP, BP, value_of_cap=True, release_of_cap=True), SwitchMix(RM2)),
    Order(ALWAYS, TapCard(K2)),
)
PLAYS = (0, 4, 9, 13, 25, 40)


def play(r: Rules) -> dict[int, Save]:
    s = start(r, ORDERS)
    return {t: advance(s, r, t) for t in PLAYS}


def _old() -> dict[str, object]:
    return json.loads(FIXTURE.read_text())


def _old_json(key: str) -> Any:
    return json.loads(FIXTURE.read_text())[key]


def _rules() -> Rules:
    return rules(t0=8, t_rate=1, w_rate=1)


# ---- statement 1: no guard and no fallback is today's text ------------------------------------------------------------

@kills(18, 19)
def test_a_save_without_guards_encodes_to_its_old_text_with_bool_latches():
    """Statement 1: a save holding only orders with empty `unless` and `or_else` encodes to the text it had before the
    fields existed, and its latches are bare bools."""
    r = _rules()
    s = play(r)[4]
    assert encode(s, r) == _old()["save"]
    assert decode(str(_old()["save"]), r) == s
    assert s.latches and all(type(x) is bool for x in s.latches)


@kills(18)
def test_an_order_given_empty_lists_is_the_order_without_them_and_keeps_the_old_text():
    """Statement 1: Order(when, then, unless=(), or_else=()) is today's Order(when, then); set through SetOrders, the
    save encodes to the old text and the logged SetOrders to its old JSON."""
    explicit = tuple(order(o.when, o.then, unless=(), or_else=()) for o in ORDERS)
    assert explicit == ORDERS
    r = _rules()
    s = advance(start(r, explicit), r, 4)
    assert encode(s, r) == _old()["save"]
    assert verb_to_json(SetOrders(explicit)) == _old()["set_orders"]


@kills(18)
def test_a_logged_set_orders_without_guards_keeps_its_old_json():
    """Statement 1, as a logged SetOrders."""
    assert verb_to_json(SetOrders(ORDERS)) == _old()["set_orders"]
    assert verb_from_json(_old_json("set_orders")) == SetOrders(ORDERS)


# ---- statement 4: an engine call with no guard returns what it returned before ------------------------------------------

@kills(18, 19)
def test_saves_without_guards_follow_the_old_path():
    """Statement 4 (beside the existing suites, which are the statement): the world played from 0 to 40 with guard-free
    orders, mixes, taps and a share level reaches the saves, and emits the lines, the engine gave before guards."""
    r = _rules()
    got = {str(t): hashlib.sha256(encode(s, r).encode()).hexdigest() for t, s in play(r).items()}
    assert got == _old()["trajectory"]
    assert len(advance_logged(play(r)[0], r, max(PLAYS)).lines) == _old()["lines"]
    assert int(str(_old()["lines"])) > 0   # the lines compared are not an empty list


# ---- statement 2: guards and fallbacks round-trip ---------------------------------------------------------------------

def _guard(kind: bool, v: int, gap: int, share: bool) -> AtLeast | AtMost:
    if share:
        return AtLeast(StoreValue(T), v * 500, max(0, v - gap) * 500, value_of_cap=True, release_of_cap=True)
    return at_least(v, max(0, v - gap)) if kind else at_most(v, v + gap)


_GUARD = st.builds(_guard, st.booleans(), st.integers(1, 20), st.integers(0, 3), st.booleans())


@st.composite
def _guarded_orders(draw: st.DrawFn) -> tuple[Order, ...]:
    out: list[Order] = []
    for verb in draw(st.lists(st.sampled_from([TapCard(K), TapCard(K2), SwitchMix(RM), SwitchMix(RM2)]),
                              min_size=1, max_size=4)):
        when: Condition = draw(st.sampled_from([ALWAYS, at_least(12, 10, W), at_most(30, 31)]))
        guards = draw(st.lists(_GUARD, max_size=3, unique=True))
        out.append(guarded(when, verb, *guards) if guards else Order(when, verb))
    return tuple(out)


@kills(19, 20)
@few(10)
@given(orders=_guarded_orders(), t=st.integers(0, 60))
def test_a_save_holding_guards_round_trips_and_each_latch_has_its_rules_form(orders: tuple[Order, ...], t: int):
    """Statement 2: decode(encode(s)) == s for saves holding guards, advanced while their latches move; "The saved
    shape": a rule with guards holds a GuardedLatch with one bool per guard, a rule with none a bare bool."""
    r = rules(t0=5, t_rate=1, w_rate=1)
    s = advance(start(r, orders), r, t)
    assert decode(encode(s, r), r) == s
    for o, latch in zip(orders, s.latches, strict=True):
        n = len(getattr(o, "unless"))
        if n:
            assert type(latch).__name__ == "GuardedLatch" and len(getattr(latch, "unless")) == n
        else:
            assert type(latch) is bool


@kills(20)
@few(10)
@given(orders=_guarded_orders())
def test_a_logged_set_orders_holding_guards_round_trips(orders: tuple[Order, ...]):
    """Statement 2, as a logged SetOrders."""
    v = SetOrders(orders)
    assert verb_from_json(verb_to_json(v)) == v


@kills(20)
def test_a_save_and_a_logged_set_orders_holding_fallbacks_round_trip():
    """Statement 2 for `or_else` (lands with the "or else" build step; gaps.txt): fallbacks beside guards."""
    orders = (with_else(ALWAYS, TapCard(K), (TapCard(K2), TapCard(K3)), block_from(10)),
              with_else(at_least(12, 10, W), SwitchMix(RM), (SwitchMix(RM2),)))
    r = rules(t0=5, t_rate=1, w_rate=1)
    s = advance(start(r, orders), r, 20)
    assert decode(encode(s, r), r) == s
    assert verb_from_json(verb_to_json(SetOrders(orders))) == SetOrders(orders)


@kills(1, 8)
def test_a_guarded_rules_latch_reads_its_when_and_its_guards_in_list_order():
    """Statement 2 / "The saved shape": GuardedLatch(when, unless), one bool per guard in list order. T is 5 at 0:
    "5 or more" holds, "20 or more" does not."""
    r = rules(t0=5)
    s = start(r, (guarded(ALWAYS, TapCard(K), at_least(5, 4), at_least(20, 19)),
                  guarded(ALWAYS, TapCard(K2), at_least(20, 19), at_least(5, 4))))
    assert s.latches == (guarded_latch(True, (True, False)), guarded_latch(True, (False, True)))


# ---- statement 3: what SetOrders refuses --------------------------------------------------------------------------------

def _set(orders: tuple[Order, ...], r: Rules | None = None) -> Save:
    r = r or rules(t0=5)
    return start(r, orders)


G1, G2, G3, G4 = at_least(10, 9), at_least(20, 19), at_most(2, 3), at_most(1, 2, W)


@kills(21, 22)
def test_four_guards_are_refused_and_three_are_not():
    """Statement 3: four guards; "at most 3 guards"."""
    _set((guarded(ALWAYS, TapCard(K), G1, G2, G3),))
    with pytest.raises(InvalidVerbError):
        _set((guarded(ALWAYS, TapCard(K), G1, G2, G3, G4),))


@kills(21)
def test_a_guard_listed_twice_is_refused():
    """Statement 3: a guard listed twice; the same two guards on two rules are fine."""
    _set((guarded(ALWAYS, TapCard(K), G1), guarded(ALWAYS, TapCard(K2), G1)))
    with pytest.raises(InvalidVerbError):
        _set((guarded(ALWAYS, TapCard(K), G1, G2, G1),))


@pytest.mark.parametrize("bad", [
    AtLeast(LaneRules(LaneId("l")), 1, 1),
    AtLeast(SkillLevel(SK), 5000, 5000, value_of_cap=True, release_of_cap=True),
    AtLeast(StoreValue(T), 2 * BP, BP, value_of_cap=True, release_of_cap=True),
    AtLeast(StoreValue(T), 5 * Q, 6 * Q),
    AtLeast(StoreValue(T), 5000, 6000, value_of_cap=True, release_of_cap=True),
], ids=["lane rules", "share of a skill", "share over BP", "release over value", "share release over value"])
@kills(21)
def test_a_guard_refused_as_a_when_is_refused(bad: AtLeast):
    """Statement 3: a guard SetOrders would refuse as a `when` ("a guard passes every check a when passes"). The same
    condition is refused as a when first (the premise), and a good guard in its place is accepted."""
    with pytest.raises(InvalidVerbError):
        _set((Order(bad, TapCard(K)),))
    _set((guarded(ALWAYS, TapCard(K), G1),))
    with pytest.raises(InvalidVerbError):
        _set((guarded(ALWAYS, TapCard(K), bad),))


@kills(27)
def test_four_actions_are_refused_and_three_are_not():
    """Statement 3 (with "or else"): four actions; "at most 3 actions"."""
    _set((with_else(ALWAYS, TapCard(K), (TapCard(K2), TapCard(K3))),))
    with pytest.raises(InvalidVerbError):
        _set((with_else(ALWAYS, TapCard(K), (TapCard(K2), TapCard(K3), TapCard(K4))),))


@kills(27)
def test_an_action_listed_twice_is_refused():
    """Statement 3 (with "or else"): an action listed twice, `then` included."""
    with pytest.raises(InvalidVerbError):
        _set((with_else(ALWAYS, TapCard(K), (TapCard(K2), TapCard(K))),))
    with pytest.raises(InvalidVerbError):
        _set((with_else(ALWAYS, TapCard(K), (TapCard(K2), TapCard(K2))),))


@kills(27)
def test_a_tap_and_a_mix_in_one_rule_are_refused():
    """Statement 3 (with "or else"): every action is the same kind of verb."""
    _set((with_else(ALWAYS, SwitchMix(RM), (SwitchMix(RM2),)),))
    with pytest.raises(InvalidVerbError):
        _set((with_else(ALWAYS, TapCard(K), (SwitchMix(RM),)),))
    with pytest.raises(InvalidVerbError):
        _set((with_else(ALWAYS, SwitchMix(RM), (TapCard(K),)),))


@kills(27)
def test_taps_on_two_lanes_are_refused():
    """Statement 3 (with "or else"): every listed tap is of a card on one lane (J is on L2, KL on L)."""
    _set((with_else(ALWAYS, TapCard(K), (TapCard(KL),)),))
    with pytest.raises(InvalidVerbError):
        _set((with_else(ALWAYS, TapCard(K), (TapCard(J),)),))


@kills(27)
def test_mixes_of_two_layers_are_refused():
    """Statement 3 (with "or else"): every listed mix is of one layer, hands or town."""
    r = town.world((town.joiner("j", town.LA, town.TM, town.A1),))
    s = town.start(r, *town.hands_mixes())
    decide(s, r, 0, SetOrders((with_else(town.ALWAYS, SwitchMix(town.HM1), (SwitchMix(town.HM2),)),)))
    with pytest.raises(InvalidVerbError):
        decide(s, r, 0, SetOrders((with_else(town.ALWAYS, SwitchMix(town.HM1), (SwitchMix(town.TM),)),)))


@kills(27)
def test_or_else_on_a_rule_answering_an_offer_is_refused():
    """Statement 3 (with "or else"): a rule whose `then` answers an offer takes no `or_else`; the same rule without it,
    and with a guard, is accepted."""
    of, a1, a2 = OfferId("of"), AnswerId("a1"), AnswerId("a2")
    r = rules(t0=5, offers=(OfferDef(of, (AnswerDef(a1, Outcome()), AnswerDef(a2, Outcome()))),))
    _set((Order(ALWAYS, AnswerOffer(of, a1)),), r)
    _set((guarded(ALWAYS, AnswerOffer(of, a1), G1),), r)
    with pytest.raises(InvalidVerbError):
        _set((with_else(ALWAYS, AnswerOffer(of, a1), (AnswerOffer(of, a2),)),), r)


@kills(22)
def test_the_page_shaped_guards_are_accepted_on_taps_and_mixes():
    """Statement 3's must-allow side: three distinct guards (amount, share, at-most, another store) on a tap rule and a
    mix rule are accepted, and set the rule's latch to a GuardedLatch."""
    full = AtLeast(StoreValue(T), BP, BP, value_of_cap=True, release_of_cap=True)
    s = _set((guarded(ALWAYS, TapCard(K), G1, full, G4), guarded(at_most(3, 4), SwitchMix(RM), G2, G3)))
    assert [len(getattr(latch, "unless")) for latch in s.latches] == [3, 2]
