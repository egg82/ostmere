"""SetOrders keeps latches (api/CONTRACT.txt "Rule runs"; DESIGN.txt, "Rule changes"): each new order equal to an old
order (the whole order: its condition with its band, and its verb) keeps that old order's latch, the first equal one's
for every copy; a new or edited order is latched afresh from its threshold alone. So a rule running inside its band
stays on across an edit of another rule or a reorder, and a rule added in the same state starts off."""
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, AfterTime, AtLeast, AtMost, CardShare, Condition, Flow, Mix, MixId, Order, Rules, Save, SaveMix, SetOrders,
    StoreDef, StoreValue, SwitchMix, advance, decide, new_save, value,
)
from contract_gen import Q, card, card_id, make_rules, mix_id, store_id

S0 = store_id(0)
M0, M1, M2 = mix_id(0), mix_id(1), mix_id(2)
NEVER = AfterTime(10**9)
# Every mix makes s0, so the store only rises and any rule's mix keeps it rising: 20, 10 or 5 items an hour.
RULES = make_rules([StoreDef(S0, 60 * Q, 5 * Q)], [
    card(0, 0, (Flow(S0, 20000),), ()), card(1, 0, (Flow(S0, 10000),), ()), card(2, 0, (Flow(S0, 5000),), ())])
RUN = Order(AtMost(StoreValue(S0), 10 * Q, 20 * Q), SwitchMix(M1))   # under 10, until 20
OTHER = Order(NEVER, SwitchMix(M2))
MID_BAND_AT = 3600   # s0 starts at 5 and gains 10 an hour under m1 (RUN's mix, or the player's), so 15 here


def _rules_for(store_at_start: int):
    return make_rules([StoreDef(S0, 60 * Q, store_at_start * Q)], list(RULES.cards))


def _world(old: tuple[Order, ...], start: int = 5, player: MixId = M1) -> tuple[Rules, Save]:
    """The orders set at 0 with s0 at `start` items and `player` the player's mix, advanced to MID_BAND_AT."""
    rules = _rules_for(start)
    s = new_save(rules)
    for i, m in enumerate((M0, M1, M2)):
        s = decide(s, rules, 0, SaveMix(Mix(m, (CardShare(card_id(i), BP),))))
    s = decide(s, rules, 0, SwitchMix(player))
    s = decide(s, rules, 0, SetOrders(old))
    return rules, advance(s, rules, MID_BAND_AT)


def _on_mid_band(old: tuple[Order, ...]) -> tuple[Rules, Save]:
    """RUN's band is 10..20 and s0 reads 15 here; RUN, set at 5, is on."""
    rules, s = _world(old)
    assert 10 * Q < value(s, rules, S0, MID_BAND_AT) < 20 * Q
    assert s.latches[old.index(RUN)] is True
    return rules, s


def _off_mid_band(old: tuple[Order, ...]) -> tuple[Rules, Save]:
    """s0 starts at 12 (never under 10, so RUN never came on) and reads 17 here, inside the band."""
    rules, s = _world(old, start=12, player=M2)
    assert 10 * Q < value(s, rules, S0, MID_BAND_AT) < 20 * Q
    assert s.latches[old.index(RUN)] is False
    return rules, s


def _after(rules: Rules, s: Save, new: tuple[Order, ...]) -> tuple[bool, ...]:
    return decide(s, rules, MID_BAND_AT, SetOrders(new)).latches


def test_a_rule_running_mid_band_stays_on_when_another_rule_is_added():
    rules, s = _on_mid_band((RUN,))
    assert _after(rules, s, (RUN, OTHER)) == (True, False)
    assert _after(rules, s, (OTHER, RUN)) == (False, True)


def test_a_rule_running_mid_band_stays_on_when_another_rule_is_edited():
    rules, s = _on_mid_band((RUN, OTHER))
    assert _after(rules, s, (RUN, Order(AfterTime(10**9 + 1), SwitchMix(M2)))) == (True, False)


def test_a_rule_running_mid_band_stays_on_when_the_list_is_reordered():
    rules, s = _on_mid_band((OTHER, RUN))
    assert _after(rules, s, (RUN, OTHER)) == (True, False)


def test_a_rule_running_mid_band_stays_on_when_another_rule_is_removed():
    rules, s = _on_mid_band((OTHER, RUN))
    assert _after(rules, s, (RUN,)) == (True,)


def test_the_same_rule_added_fresh_in_the_same_state_starts_off():
    rules, s = _world((OTHER,))
    assert value(s, rules, S0, MID_BAND_AT) == 15 * Q
    assert _after(rules, s, (OTHER, RUN)) == (False, False)


def test_an_edited_rule_is_latched_afresh_from_its_threshold():
    rules, s = _on_mid_band((RUN,))
    wider = Order(AtMost(StoreValue(S0), 10 * Q, 25 * Q), RUN.then)     # band edited
    lower = Order(AtMost(StoreValue(S0), 9 * Q, 20 * Q), RUN.then)      # threshold edited
    other_verb = Order(RUN.when, SwitchMix(M0))                          # verb edited
    for edited in (wider, lower, other_verb):
        assert _after(rules, s, (edited,)) == (False,)
    assert _after(rules, s, (RUN, wider, other_verb)) == (True, False, False)


def test_an_edit_to_a_threshold_that_holds_now_is_on_afresh():
    rules, s = _on_mid_band((RUN,))
    held = Order(AtMost(StoreValue(S0), 16 * Q, 20 * Q), RUN.then)   # 15 <= 16
    assert _after(rules, s, (held,)) == (True,)


def test_two_equal_copies_both_take_the_first_equal_old_rules_latch():
    rules, s = _on_mid_band((RUN,))
    assert _after(rules, s, (RUN, OTHER, RUN)) == (True, False, True)
    rules, s = _off_mid_band((RUN,))
    assert _after(rules, s, (RUN, RUN)) == (False, False)


def test_a_rule_that_was_off_mid_band_stays_off():
    rules, s = _off_mid_band((RUN, OTHER))
    assert _after(rules, s, (OTHER, RUN)) == (False, False)
    assert _after(rules, s, (RUN,)) == (False,)


def test_each_rule_keeps_its_own_latch_beside_a_rule_that_is_off():
    rules, s = _on_mid_band((RUN, OTHER))
    assert _after(rules, s, (OTHER, RUN)) == (False, True)


# --- property: a permutation changes no order's latch --------------------------------------------------------

_BANDS = st.tuples(st.integers(1, 30), st.integers(0, 12))
_VERBS = st.sampled_from([SwitchMix(M0), SwitchMix(M1), SwitchMix(M2)])


@st.composite
def _order(draw: st.DrawFn) -> Order:
    kind = draw(st.sampled_from(["most", "least", "time"]))
    v, gap = draw(_BANDS)
    verb = draw(_VERBS)
    cond: Condition
    if kind == "most":
        cond = AtMost(StoreValue(S0), v * Q, (v + gap) * Q)
    elif kind == "least":
        cond = AtLeast(StoreValue(S0), v * Q, max(0, v - gap) * Q)
    else:
        cond = AfterTime(draw(st.integers(0, 3600)))
    return Order(cond, verb)


@given(st.data(), st.lists(_order(), min_size=1, max_size=5), st.integers(0, 40), st.integers(0, 3600))
def test_any_permutation_leaves_every_orders_latch_unchanged(data: st.DataObject, old: list[Order], start: int, t: int):
    rules = _rules_for(start)
    s = new_save(rules)
    for i, m in enumerate((M0, M1, M2)):
        s = decide(s, rules, 0, SaveMix(Mix(m, (CardShare(card_id(i), BP),))))
    s = decide(s, rules, 0, SetOrders(tuple(old)))
    at_t = advance(s, rules, t)
    first: dict[Order, bool] = {}
    for o, latch in zip(old, at_t.latches):
        first.setdefault(o, latch)
    perm = tuple(data.draw(st.permutations(old)))
    after = decide(at_t, rules, t, SetOrders(perm))
    assert after.latches == tuple(first[o] for o in perm)
