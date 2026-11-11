"""Invariants 43-44 (Order mix, kinds don't shadow; CARDS "Order mix", "Orders", "Greyed mix"): a mix order's mix runs
over the player's while its latch holds and the player's own comes back when it releases; no order ever writes
save.active; a greyed order mix is passed over; a player's switch under an order's mix only sets what comes back;
pauses clear exactly when the running mix changes; tap orders and mix orders never shadow each other; the queue
waits while an order's mix runs."""
from dataclasses import replace

from hypothesis import example, given, strategies as st
from hypothesis.strategies import DrawFn

from ashfall_app.engine import (
    BP, HANDS, ActionId, AfterTime, AtLeast, AtMost, CardDef, CardShare, Flow, Mix, MixId, Order, QueueEntry, SaveMix, Save, SetOrders,
    SetQueue, StandingDef, StoreDef, StoreValue, SwitchMix, TapCard, advance, decide, new_save, next_event, segment, value, view,
    Rules, CardId, Verb,
)
from contract_gen import (
    Q, Scenario, card, card_id, condition_st, few, make_rules, mix_id, mix_st, play, probe_times, rules_st, store_id,
)

S0, S1 = store_id(0), store_id(1)
M0, M1, M2 = mix_id(0), mix_id(1), mix_id(2)
NEVER = AfterTime(10**9)


def _lane_card(s: Save):
    return next(ls.card for ls in s.lanes if ls.lane == HANDS)


def _expected_running(s: Save, greyed: tuple[MixId, ...]) -> tuple[MixId | None, int | None]:
    """Invariant 43's definition, from the save's own latches: the first latched SwitchMix order to a mix that is not
    greyed, else save.active."""
    for i, (o, on) in enumerate(zip(s.orders, s.latches)):
        if on and isinstance(o.then, SwitchMix) and o.then.mix not in greyed:
            return o.then.mix, i
    return s.active, None


# ---- worlds ---------------------------------------------------------------------------------------------------

def _rest_world():
    """s0 (5 items of 10) drains at 1000/s under the player's m1 = {c1}; the order "s0 <= 2 items (release above 4):
    run m0 = {c0}" fills it at 2000/s. m2 = {c2} drains at 500/s, a third mix for the player's switch.
    s0 reaches 2 items at 10800 (latch rises) and passes 4 items at 14401 (latch releases)."""
    rules = make_rules([StoreDef(S0, 10 * Q, 5 * Q)], [
        card(0, 0, (Flow(S0, 2000),), ()), card(1, 0, (), (Flow(S0, 1000),)), card(2, 0, (), (Flow(S0, 500),)),
        card(3, 0, (), (), work_s=50)])
    s = new_save(rules)
    for v in (SaveMix(Mix(M0, (CardShare(card_id(0), BP),))), SaveMix(Mix(M1, (CardShare(card_id(1), BP),))),
              SaveMix(Mix(M2, (CardShare(card_id(2), BP),))), SwitchMix(M1),
              SetOrders((Order(AtMost(StoreValue(S0), 2 * Q, 4 * Q), SwitchMix(M0)),))):
        s = decide(s, rules, 0, v)
    return rules, s


RISE, RELEASE = 10_800, 14_401


def test_a_rule_mix_runs_while_its_condition_holds_and_the_players_mix_comes_back():
    """Invariant 43, "Order mix": before the latch the player's m1 runs; while it holds m0 runs over it (s0 rises) and
    save.active stays m1; at the release the player's m1 runs again (s0 falls) with nothing written to the save."""
    r, s = _rest_world()
    assert s.active == M1 and segment(advance(s, r, RISE - 1), r, S0).rate == -1000
    a = advance(s, r, RISE)
    assert a.latches == (True,) and a.active == M1 and segment(a, r, S0).rate == 2000
    held = advance(s, r, RELEASE - 1)
    assert held.latches == (True,) and segment(held, r, S0).rate == 2000
    b = advance(s, r, RELEASE)
    assert b.latches == (False,) and b.active == M1 and segment(b, r, S0).rate == -1000
    for save, want in ((s, (M1, None, (False,))), (a, (M0, 0, (True,))), (b, (M1, None, (False,)))):
        v = view(save, r)
        assert (v.running_mix, v.mix_order, v.orders_on) == want, save.time


def test_the_band_repeats_without_the_players_mix_ever_being_written():
    """Invariant 43: over several cycles of the band, every resolved save keeps active == m1, and s0 moves at m0's rate
    exactly while the latch holds and at m1's otherwise."""
    r, s = _rest_world()
    cur = s
    cycles = 0
    for _ in range(12):
        e = next_event(cur, r)
        if e is None:
            break
        nxt = advance(cur, r, e.time)
        cycles += nxt.latches != cur.latches
        cur = nxt
        assert cur.active == M1
        assert segment(cur, r, S0).rate == (2000 if cur.latches[0] else -1000), cur.time
    assert cycles >= 4


def test_a_players_switch_under_a_rule_mix_only_sets_what_comes_back():
    """"Order mix": a player's SwitchMix while m0 runs for the order sets save.active to m2 and nothing else (s0 still
    rises at m0's rate); m2, not m1, comes back at the release."""
    r, s = _rest_world()
    a = advance(s, r, 11_000)
    b = decide(a, r, 11_000, SwitchMix(M2))
    assert b == replace(a, active=M2)
    assert view(b, r).running_mix == M0 and segment(b, r, S0).rate == 2000
    c = advance(b, r, RELEASE)
    assert c.active == M2 and view(c, r).running_mix == M2 and segment(c, r, S0).rate == -500


def test_removing_the_controlling_rule_returns_to_the_players_mix():
    """"Order mix": SetOrders that drops the latched mix order pops its mix at once: the player's m1 runs."""
    r, s = _rest_world()
    a = decide(advance(s, r, 11_000), r, 11_000, SetOrders(()))
    v = view(a, r)
    assert a.active == M1 and (v.running_mix, v.mix_order, v.orders_on) == (M1, None, ())
    assert segment(a, r, S0).rate == -1000


def test_the_queue_waits_while_a_rule_mix_runs():
    """"Order mix", "Queue mix": an order's mix runs over the queue's. A queued switch set while m0 runs for the order
    waits, and at the release its m2 runs; save.active stays m1 throughout."""
    r, s = _rest_world()
    a = decide(advance(s, r, 11_000), r, 11_000, SetQueue((QueueEntry(SwitchMix(M2), NEVER),)))
    assert a.active == M1 and view(a, r).running_mix == M0 and segment(a, r, S0).rate == 2000
    b = advance(a, r, RELEASE)
    assert b.active == M1 and view(b, r).running_mix == M2 and segment(b, r, S0).rate == -500
    assert view(advance(b, r, RELEASE + 50_000), r).running_mix == M2


def test_a_queued_tap_waits_while_a_rule_mix_runs_and_starts_at_the_release():
    """"Orders" (the queue waits, also while an order's mix runs): the head taps c3, but m0 runs for the order, so the
    hands stay free until the latch releases; then the tap starts."""
    r, s = _rest_world()
    a = decide(advance(s, r, 11_000), r, 11_000, SetQueue((QueueEntry(TapCard(card_id(3)), NEVER),)))
    assert _lane_card(a) is None
    assert _lane_card(advance(a, r, RELEASE - 1)) is None
    assert _lane_card(advance(a, r, RELEASE)) == card_id(3)


def test_the_queues_mix_runs_over_the_players_and_gives_it_back_at_the_pop():
    """"Queue mix": with no order latched the controlling entry's mix runs over save.active, which it never writes; at
    the entry's pop the player's own mix runs again."""
    r, s = _rest_world()
    a = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(M2), AfterTime(5000)),)))
    assert a.active == M1 and segment(a, r, S0).rate == -500 and view(a, r).running_mix == M2
    b = advance(a, r, 5000)
    assert b.queue == () and b.active == M1 and view(b, r).running_mix == M1


def _greyed_world():
    """_rest_world's three mixes plus m3 = {c0 50%, g 50%}, g capped at one completion; the player taps g at 0 and it
    completes at 100, greying m3. No orders yet."""
    m3 = mix_id(3)
    g = CardDef(card_id(4), 100, cap=1)
    rules = make_rules([StoreDef(S0, 10 * Q, 5 * Q)], [
        card(0, 0, (Flow(S0, 2000),), ()), card(1, 0, (), (Flow(S0, 1000),)), card(2, 0, (), (Flow(S0, 500),)), g])
    s = new_save(rules)
    for v in (SaveMix(Mix(M0, (CardShare(card_id(0), BP),))), SaveMix(Mix(M1, (CardShare(card_id(1), BP),))),
              SaveMix(Mix(m3, (CardShare(card_id(0), 5000), CardShare(g.id, 5000)))), SwitchMix(M1), TapCard(g.id)):
        s = decide(s, rules, 0, v)
    a = advance(s, rules, 100)
    assert view(a, rules).greyed_mixes == (m3,)  # the world's premise: m3 is greyed from 100
    return rules, a, m3


def test_a_greyed_rule_mix_falls_through_to_the_next_mix_rule():
    """"Greyed mix", invariant 43: the first order is latched but names greyed m3, so it is passed over and the next
    latched mix order's m0 runs; save.active is untouched."""
    r, a, m3 = _greyed_world()
    b = decide(a, r, 100, SetOrders((Order(AfterTime(0), SwitchMix(m3)), Order(AfterTime(0), SwitchMix(M0)))))
    assert b.active == M1 and segment(b, r, S0).rate == 2000
    v = view(b, r)
    assert (v.running_mix, v.mix_order, v.orders_on) == (M0, 1, (True, True))


def test_a_greyed_rule_mix_alone_falls_through_to_the_players_mix():
    """"Greyed mix": the only latched mix order names greyed m3: the player's m1 runs."""
    r, a, m3 = _greyed_world()
    b = decide(a, r, 100, SetOrders((Order(AfterTime(0), SwitchMix(m3)),)))
    assert b.active == M1 and segment(b, r, S0).rate == -1000
    v = view(b, r)
    assert (v.running_mix, v.mix_order, v.orders_on) == (M1, None, (True,))


def test_a_saved_mix_that_ungreys_runs_again_at_once_while_its_latch_holds():
    """"Greyed mix": SaveMix replacing greyed m3 with {c0 50%} un-greys it, and since its order is latched (and first)
    it runs at that instant, over the m0 that ran in its place."""
    r, a, m3 = _greyed_world()
    b = decide(a, r, 100, SetOrders((Order(AfterTime(0), SwitchMix(m3)), Order(AfterTime(0), SwitchMix(M0)))))
    c = decide(b, r, 100, SaveMix(Mix(m3, (CardShare(card_id(0), 5000),))))
    assert c.active == M1 and segment(c, r, S0).rate == 1000
    v = view(c, r)
    assert v.greyed_mixes == () and (v.running_mix, v.mix_order) == (m3, 0)


def test_a_rule_mix_that_greys_while_running_falls_through_at_that_instant():
    """Invariants 43, 39: m3 = {c0 50%, g 50%} runs for a latched order; g (cap 1, 100 s) completes in it at 200 and
    m3 greys, so from that instant the player's m1 runs (s0 falls at c1's rate) rather than a greyed mix running
    nothing; save.active was never written."""
    m3 = mix_id(3)
    g = CardDef(card_id(4), 100, cap=1)
    r = make_rules([StoreDef(S0, 10 * Q, 5 * Q)], [card(0, 0, (Flow(S0, 2000),), ()), card(1, 0, (), (Flow(S0, 1000),)), g])
    s = new_save(r)
    for v in (SaveMix(Mix(M1, (CardShare(card_id(1), BP),))),
              SaveMix(Mix(m3, (CardShare(card_id(0), 5000), CardShare(g.id, 5000)))), SwitchMix(M1),
              SetOrders((Order(AfterTime(0), SwitchMix(m3)),))):
        s = decide(s, r, 0, v)
    before = advance(s, r, 199)
    assert before.active == M1 and segment(before, r, S0).rate == 1000
    a = advance(s, r, 200)
    assert a.active == M1 and segment(a, r, S0).rate == -1000
    v = view(a, r)
    assert v.greyed_mixes == (m3,) and (v.running_mix, v.mix_order) == (M1, None)


def _pause_world():
    """s1 is a clock, made by a standing action at 500 a second outside every mix; the order "s1 <= 0 (release above
    499999): run m0" holds from 0 and releases at 1000. m0 = {c1 50% (costs s0 1000), c3 50% (makes s0 50)}: s0
    (95000) empties at 100, pausing c1, whose share goes to c3, so s0 refills at 100/s, to 90000 at 1000, far below an
    hour of c1's cost. The player's mix is m1 = {c1}; m2 = {c3} is a third mix."""
    rules = make_rules([StoreDef(S0, 10 * Q, 95_000), StoreDef(S1, 10 * Q, 0)], [
        card(1, 0, (), (Flow(S0, 2000),)), card(3, 0, (Flow(S0, 100),), ())])
    rules = replace(rules, standing=(StandingDef(ActionId("clock"), makes=(Flow(S1, 500),)),))
    s = new_save(rules)
    m0 = Mix(M0, (CardShare(card_id(1), 5000), CardShare(card_id(3), 5000)))
    for v in (SaveMix(m0), SaveMix(Mix(M1, (CardShare(card_id(1), BP),))), SaveMix(Mix(M2, (CardShare(card_id(3), BP),))),
              SwitchMix(M1), SetOrders((Order(AtMost(StoreValue(S1), 0, 499_999), SwitchMix(M0)),))):
        s = decide(s, rules, 0, v)
    return rules, s


def test_pauses_clear_when_the_rule_mix_releases():
    """"Running dry", "Order mix": c1 pauses on s0 at 100 under the order's m0. At 1000 the latch releases and the
    player's m1 comes back: the running mix changed, so the pause clears and c1 draws s0 (still above 0) again."""
    r, s = _pause_world()
    a = advance(s, r, 999)
    assert a.latches == (True,) and [p.runner for p in a.pauses] == [card_id(1)]
    b = advance(s, r, 1000)
    assert b.latches == (False,) and b.pauses == () and value(b, r, S0, 1000) == 90_000
    assert segment(b, r, S0).rate == -2000
    assert b.active == M1 and view(b, r).running_mix == M1


def test_a_switch_that_leaves_the_running_mix_unchanged_clears_no_pause():
    """Invariant 43: while m0 runs for the order a player's switch to m2 changes only save.active: c1's pause stays and
    every segment is as it was."""
    r, s = _pause_world()
    a = advance(s, r, 500)
    assert a.pauses != ()
    b = decide(a, r, 500, SwitchMix(M2))
    assert b == replace(a, active=M2)


def test_split_holds_across_a_rule_mix_rising_and_releasing():
    """Invariant 1 (split) while an order's mix runs: chained advances through the latch's rise and release, and
    through a pause under the order's mix and its clearing, equal one direct advance."""
    for r, s, cuts in ((*_rest_world(), (RISE - 1, RISE, RISE + 1, 12_000, RELEASE - 1, RELEASE, RELEASE + 1, 40_000)),
                       (*_pause_world(), (99, 100, 101, 999, 1000, 1001, 1011, 1012, 1013, 5000))):
        chained = s
        for t in cuts:
            chained = advance(chained, r, t)
            assert chained == advance(s, r, t), t


# ---- properties over generated worlds ---------------------------------------------------------------------------

@st.composite
def mix_order_scenario_st(draw: DrawFn) -> Scenario:
    """Random rules and 2-3 mixes; the player switches to m0; then SetOrders with 0-3 random mix orders and one
    AfterTime order to another mix (so a mix order is latched at some point), in a random position; then perhaps a
    player's switch. No queue, so every write of save.active is the player's."""
    rules = draw(rules_st(1000))
    n_mix = draw(st.integers(2, 3))
    mixes = [draw(mix_st(rules, i)) for i in range(n_mix)]
    ids = [mix_id(i) for i in range(n_mix)]
    orders = [Order(draw(condition_st(rules)), SwitchMix(draw(st.sampled_from(ids))))
              for _ in range(draw(st.integers(0, 3)))]
    forced = Order(AfterTime(draw(st.integers(0, 20_000))), SwitchMix(draw(st.sampled_from(ids[1:]))))
    orders.insert(draw(st.integers(0, len(orders))), forced)
    steps: list[tuple[int, Verb]] = [(0, SaveMix(m)) for m in mixes]
    steps.append((0, SwitchMix(M0)))
    steps.append((draw(st.integers(0, 3000)), SetOrders(tuple(orders))))
    if draw(st.booleans()):
        steps.append((draw(st.integers(0, 30_000)), SwitchMix(draw(st.sampled_from(ids)))))
    offsets = tuple(draw(st.lists(st.integers(0, 60_000), min_size=1, max_size=3)))
    return Scenario(rules, (), tuple(steps), SwitchMix(M0), offsets)


def _players_mix(sc: Scenario) -> MixId:
    return [v.mix for _, v in sc.steps if isinstance(v, SwitchMix)][-1]


@few(12)
@given(sc=mix_order_scenario_st())
def test_running_mix_is_the_first_latched_live_mix_order_else_the_players(sc: Scenario):
    """Invariant 43: at every probe time view.running_mix and mix_order are the first latched SwitchMix order to a mix
    not greyed, else save.active (None); orders_on are the latches."""
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets):
        a = advance(s, sc.rules, t)
        v = view(a, sc.rules)
        assert v.orders_on == a.latches
        assert (v.running_mix, v.mix_order) == _expected_running(a, v.greyed_mixes), t


@few(12)
@given(sc=mix_order_scenario_st())
def test_no_evaluation_changes_the_players_mix(sc: Scenario):
    """Invariant 43: with no queue, save.active is the player's last switch through SetOrders and every later
    evaluation (latches rising and releasing at every probe time), and a fresh SetOrders leaves it too."""
    s = play(sc)
    mine = _players_mix(sc)
    assert s.active == mine
    for t in probe_times(s, sc.rules, sc.offsets, events=6):
        a = advance(s, sc.rules, t)
        assert a.active == mine, t
        assert decide(a, sc.rules, t, SetOrders(tuple(reversed(a.orders)))).active == mine, t


@few(12)
@given(sc=mix_order_scenario_st())
def test_while_no_mix_order_is_latched_segments_equal_the_save_without_them(sc: Scenario):
    """Invariant 43: until a mix order is latched, every store segment equals that of the same save with its SwitchMix
    orders removed, event by event."""
    s = play(sc)
    stripped = decide(s, sc.rules, s.time, SetOrders(tuple(o for o in s.orders if not isinstance(o.then, SwitchMix))))
    cur = s
    for _ in range(6):
        if any(on and isinstance(o.then, SwitchMix) for o, on in zip(cur.orders, cur.latches)):
            break
        other = advance(stripped, sc.rules, cur.time)
        for sd in sc.rules.stores:
            assert segment(cur, sc.rules, sd.id) == segment(other, sc.rules, sd.id), (cur.time, sd.id)
        e = next_event(cur, sc.rules)
        if e is None:
            break
        cur = advance(s, sc.rules, e.time)


@few(12)
@given(sc=mix_order_scenario_st())
def test_a_switch_under_a_running_order_mix_changes_only_the_players_mix(sc: Scenario):
    """Invariant 43: wherever an order's mix runs, a player's switch to any saved mix returns the save with only
    save.active replaced."""
    s = play(sc)
    for t in probe_times(s, sc.rules, sc.offsets, events=6):
        a = advance(s, sc.rules, t)
        if _expected_running(a, view(a, sc.rules).greyed_mixes)[1] is None:
            continue
        for m in a.mixes:
            assert decide(a, sc.rules, t, SwitchMix(m.id)) == replace(a, active=m.id), (t, m.id)


@few(10)
@given(sc=mix_order_scenario_st(), cuts=st.lists(st.integers(0, 30_000), min_size=2, max_size=8))
def test_split_holds_with_mix_orders(sc: Scenario, cuts: list[int]):
    """Invariant 1 (split) over worlds whose order mixes rise and release: chained advances equal one direct advance."""
    s = play(sc)
    chained = s
    for c in sorted(cuts):
        chained = advance(chained, sc.rules, s.time + c)
        assert chained == advance(s, sc.rules, s.time + c), c


@st.composite
def kinds_st(draw: DrawFn):
    """Random rules and mixes with the player on m0 after a random wait, and orders mixing both kinds: a latched mix
    order and a latched tap order (in either sequence) among 0-3 random orders of either kind."""
    rules = draw(rules_st(1000))
    n_mix = draw(st.integers(2, 3))
    mixes = [draw(mix_st(rules, i)) for i in range(n_mix)]
    ids = [mix_id(i) for i in range(n_mix)]
    cards = [c.id for c in rules.cards]

    def verb():
        if draw(st.booleans()):
            return SwitchMix(draw(st.sampled_from(ids)))
        return TapCard(draw(st.sampled_from(cards)))

    orders = [Order(draw(condition_st(rules)), verb()) for _ in range(draw(st.integers(0, 3)))]
    pair = [Order(AfterTime(0), SwitchMix(draw(st.sampled_from(ids[1:])))),
            Order(AfterTime(0), TapCard(draw(st.sampled_from(cards))))]
    if draw(st.booleans()):
        pair.reverse()
    at = draw(st.integers(0, len(orders)))
    orders[at:at] = pair
    wait = draw(st.integers(0, 20_000))
    tapped = next(o.then.card for o in pair if isinstance(o.then, TapCard))
    return rules, mixes, tuple(orders), wait, tapped


def _can_run(s: Save, rules: Rules, c: CardId) -> bool:
    """A tap of c can start and run at s.time: no Pause on it and every store it costs above 0 (DESIGN.txt, "Inputs
    against a dry store": a tap on a dry cost store pauses at once and ends, as a player's own tap would)."""
    costs = next(cd.costs for cd in rules.cards if cd.id == c)
    return (all(p.runner != c for p in s.pauses)
            and all(segment(s, rules, f.store).start_value > 0 for f in costs if f.per_hour > 0))


_PAUSED_TAP = (
    make_rules([StoreDef(S0, 6000 * Q, 0)], [card(2, 0, (Flow(S0, 237),), ()), card(3, 0, (), (Flow(S0, 97),))]),
    [Mix(M0, (CardShare(card_id(2), 252), CardShare(card_id(3), 4988))), Mix(M1, (CardShare(card_id(2), 2858),))],
    (Order(AfterTime(0), SwitchMix(M1)), Order(AfterTime(0), TapCard(card_id(3)))), 522, card_id(3))
"""c3 is paused on s0 under the player's m0 (s0 is below an hour of its cost); the mix order's m1 does not run c3, so
m1 taking over clears the pause and the tap order can act."""


@few(12)
@given(world=kinds_st())
@example(world=_PAUSED_TAP)
def test_kinds_dont_shadow(world: tuple[Rules, list[Mix], tuple[Order, ...], int, CardId]):
    """Invariant 44: setting orders of both kinds starts exactly the taps the tap orders alone start under the mix the
    mix orders run, and runs exactly the mix the mix orders alone run. The taps are compared under that mix, set by the
    player's switch, because a running-mix change clears every pause ("Order mix") and a paused card is unready, so a
    mix order can make a tap order able to act exactly as the player's own switch would."""
    rules, mixes, orders, wait, tapped = world
    s = new_save(rules)
    for m in mixes:
        s = decide(s, rules, 0, SaveMix(m))
    s = advance(decide(s, rules, 0, SwitchMix(M0)), rules, wait)
    both = decide(s, rules, wait, SetOrders(orders))
    mixed = decide(s, rules, wait, SetOrders(tuple(o for o in orders if isinstance(o.then, SwitchMix))))
    runs = view(mixed, rules).running_mix
    under = s if runs is None or runs == s.active else decide(s, rules, wait, SwitchMix(runs))
    taps = decide(under, rules, wait, SetOrders(tuple(o for o in orders if isinstance(o.then, TapCard))))
    assert both.lanes == taps.lanes
    if _can_run(under, rules, tapped):
        assert _lane_card(both) is not None  # the latched tap order acts: the hands were free
    assert view(both, rules).running_mix == view(mixed, rules).running_mix
    v = view(both, rules)
    assert (v.running_mix, v.mix_order) == _expected_running(both, v.greyed_mixes)


# ---- a "Run when..." rule: the band of one item ---------------------------------------------------------------------

def _store_band_world(rule: AtMost | AtLeast, init: int, fill: int, drain: int, cap_items: int, rule_fills: bool) -> tuple[Rules, Save]:
    """One store; m0 = {c0} makes it at `fill` per second, m1 = {c1} drains it at `drain`. The player runs m1 (rule
    fills) or m0 (rule drains); the one order applies `rule` and switches to the other. Every rate is a whole number
    of quantity units per second (full share), so a segment's rate is the exact net rate."""
    r = make_rules([StoreDef(S0, cap_items * Q, init)], [card(0, 0, (Flow(S0, fill),), ()), card(1, 0, (), (Flow(S0, drain),))])
    mine, theirs = (M1, M0) if rule_fills else (M0, M1)
    s = new_save(r)
    for v in (SaveMix(Mix(M0, (CardShare(card_id(0), BP),))), SaveMix(Mix(M1, (CardShare(card_id(1), BP),))),
              SwitchMix(mine), SetOrders((Order(rule, SwitchMix(theirs)),))):
        s = decide(s, r, 0, v)
    return r, s


def test_a_rule_that_refills_its_store_rises_below_its_value_and_releases_when_the_store_is_full():
    """Invariants 43, 14, the "Run when..." shape: AtMost(s0, 3 items - 1, release = cap - 1) with a SwitchMix to a mix
    that fills s0. The player's m1 drains s0 (10 items, 5 at the start); the latch rises once s0 is below 3 items, m0
    runs and fills s0 to its cap, where it clamps; the cap exceeds the release, so the latch drops at that instant and
    m1 comes back, with save.active m1 throughout; then the band repeats."""
    cap = 10
    r, s = _store_band_world(AtMost(StoreValue(S0), 3 * Q - 1, cap * Q - 1), 5 * Q, 2000, 1000, cap, True)
    assert s.latches == (False,) and view(s, r).running_mix == M1 and segment(s, r, S0).rate == -1000
    cur = s
    flips: list[tuple[int, bool]] = []
    while len(flips) < 4:
        e = next_event(cur, r)
        assert e is not None
        nxt = advance(cur, r, e.time)
        if nxt.latches != cur.latches:
            flips.append((nxt.time, nxt.latches[0]))
            v = view(nxt, r)
            assert v.orders_on == nxt.latches
            if nxt.latches[0]:
                assert value(nxt, r, S0, nxt.time) < 3 * Q  # rose below its value, not before
                assert (v.running_mix, v.mix_order) == (M0, 0) and segment(nxt, r, S0).rate == 2000
            else:
                assert value(nxt, r, S0, nxt.time) == cap * Q  # released at the clamp, full
                assert (v.running_mix, v.mix_order) == (M1, None) and segment(nxt, r, S0).rate == -1000
        assert nxt.active == M1 and nxt.cascade_count == 0
        cur = nxt
    assert [on for _, on in flips] == [True, False, True, False]
    assert all(a < b for (a, _), (b, _) in zip(flips, flips[1:]))


@st.composite
def _band_of_one_st(draw: DrawFn) -> tuple[AtMost | AtLeast, int, int, int, bool]:
    """(rule, init, fill, drain, rule_fills): an AtMost whose mix fills the store (value n items - 1, release one item
    higher) or an AtLeast whose mix drains it (value n items, release one item lower), on a 20-item store."""
    rule_fills = draw(st.booleans())
    n = draw(st.integers(2, 8))
    rule = (AtMost(StoreValue(S0), n * Q - 1, (n + 1) * Q - 1) if rule_fills
            else AtLeast(StoreValue(S0), n * Q, (n - 1) * Q))
    init = draw(st.integers(0, 20 * Q))
    return rule, init, draw(st.integers(200, 5000)), draw(st.integers(200, 5000)), rule_fills


@few(12)
@given(world=_band_of_one_st())
def test_a_band_of_one_item_never_flips_twice_inside_the_band(world: tuple[AtMost | AtLeast, int, int, int, bool]):
    """Invariant 14 for a mix rule (a property over a local strategy: contract_gen's random worlds cannot promise a
    store whose net rate changes sign with the rule's mix): across 20 latch changes, no two share an instant, each gap
    is at least one item of quantity at the net rate in force across it (the store crosses the whole band between
    changes), and the firing cap is never reached."""
    rule, init, fill, drain, rule_fills = world
    r, s = _store_band_world(rule, init, fill, drain, 20, rule_fills)
    cur, last, rate, changes = s, None, 0, 0
    for _ in range(200):
        e = next_event(cur, r)
        assert e is not None
        nxt = advance(cur, r, e.time)
        assert nxt.cascade_count == 0 and nxt.last_cascade is None
        if nxt.latches != cur.latches:
            if last is not None:
                assert nxt.time > last, "two latch changes at one instant"
                assert (nxt.time - last) * abs(rate) >= Q, (last, nxt.time, rate)
            last, rate, changes = nxt.time, segment(nxt, r, S0).rate, changes + 1
            if changes == 20:
                return
        cur = nxt
    raise AssertionError(f"only {changes} latch changes in 200 events")
