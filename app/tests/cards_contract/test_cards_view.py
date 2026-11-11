"""The card panel (view.py; "Card panel", "Read model", invariant 31): View.cards holds the unlocked cards not completed
in rules order and View.completed the rest; lanes show HANDS always and another once a card on it is unlocked; a card's
blocker is its first unmet precondition (the rest of the current completion's inputs, in declaration order, then
requires) with ready_at off the current segments, the time the card is ready; needs are one whole completion's, each store once at the larger
quantity; tap_s is the rest of the current completion at the current speed."""
from ashfall_app.engine import (
    BP, HANDS, ActionId, AfterTime, Amount, AtLeast, Blocker, CardDef, CardId, CompletedCard, Flow, FlowKind, LaneBar,
    LaneSpeed, Need, Outcome, RateRef, StandingDef, StoreDef, StoreId, StoreValue, TriggerDef, TriggerId, Unlock,
    UnlockKind, WorkRef, advance, new_save, segment, view,
)
from ashfall_app.engine import work as engine_work
from cards_world import K, Q, RACK, add, card_view, mul, rules, tap, val, view_of, with_mix

X, Z = StoreId("x"), StoreId("z")
C, C2, D, CP, CH, RK = (CardId(n) for n in ("c", "c2", "d", "cp", "ch", "rk"))
GEN = ActionId("gen")
OPEN = [Unlock(UnlockKind.STORE, X), Unlock(UnlockKind.SKILL, K), Unlock(UnlockKind.ACTION, GEN)] + [
    Unlock(UnlockKind.CARD, c) for c in (C, C2, CP, CH)]


def world(opening: list[Unlock] | None = OPEN, x0: int = 0, gen: int = 36_000):
    """gen fills x at an item per 100 s. c needs an item of x and requires two; c2 needs x then z (z locked); d is
    locked; cp is a one-off; ch needs an item of x; rk is a rack card, locked unless the opening names it."""
    return rules([StoreDef(X, 100 * Q, x0), StoreDef(Z, 100 * Q, 0)],
                 standing=[StandingDef(GEN, makes=(Flow(X, gen),))],
                 cards=[CardDef(C, 100, inputs=(Amount(X, Q),), requires=(AtLeast(StoreValue(X), 2 * Q, 2 * Q),)),
                        CardDef(C2, 100, inputs=(Amount(X, Q), Amount(Z, Q))),
                        CardDef(D, 100), CardDef(CP, 50, cap=1), CardDef(CH, 100, inputs=(Amount(X, Q),)),
                        CardDef(RK, 100, lane=RACK)],
                 lanes=[RACK], opening=opening)


def test_the_panel_holds_unlocked_cards_not_completed_in_rules_order():
    """View.cards / View.completed: locked d and rk appear in neither; cp moves to the Completed tab once it reaches
    its cap; the order is rules.cards order."""
    r = world()
    s = new_save(r)
    assert [cv.card for cv in view(s, r).cards] == [C, C2, CP, CH]
    a = advance(tap(s, r, 0, CP), r, 50)
    v = view(a, r)
    assert [cv.card for cv in v.cards] == [C, C2, CH]
    assert v.completed == (CompletedCard(CP, 1),)


def test_a_lane_shows_once_a_card_on_it_is_unlocked():
    """View.lanes: HANDS always; the rack only once a card on it is unlocked, free ones listed with card None."""
    hidden, shown = world(), world(OPEN + [Unlock(UnlockKind.CARD, RK)])
    assert view(new_save(hidden), hidden).lanes == (LaneBar(HANDS, None, None, None),)
    assert view(new_save(shown), shown).lanes == (LaneBar(HANDS, None, None, None), LaneBar(RACK, None, None, None))


def test_the_blocker_is_inputs_first_then_requires_with_ready_at_off_the_segments():
    """cards.Blocker: c's input (an item of x) is checked before its requires (two items); each ready_at is when the
    card is ready under the current segments (x rising an item per 100 s: its input at 100, its requires at 200)."""
    r = world()
    s = new_save(r)
    first = Blocker(AtLeast(StoreValue(X), Q, Q), 200)
    assert engine_work.blocker(s, r, C) == first
    cv = card_view(s, r, C)
    assert cv is not None and cv.blocker == first
    a = advance(s, r, 100)
    assert engine_work.blocker(a, r, C) == Blocker(AtLeast(StoreValue(X), 2 * Q, 2 * Q), 200)
    b = advance(a, r, 200)
    assert engine_work.blocker(b, r, C) is None and engine_work.ready(b, r, C)
    assert view_of(b, r, C).blocker is None


def test_inputs_block_in_declaration_order_and_a_store_nothing_makes_has_no_ready_at():
    """cards.Blocker: with x and z both short, c2's blocker is x (declared first); once x is there, z, which nothing
    makes: ready_at None, from the first blocker on."""
    r = world()
    s = new_save(r)
    assert engine_work.blocker(s, r, C2) == Blocker(AtLeast(StoreValue(X), Q, Q), None)
    assert engine_work.blocker(advance(s, r, 100), r, C2) == Blocker(AtLeast(StoreValue(Z), Q, Q), None)


def test_a_half_done_card_needs_only_the_rest_of_its_input():
    """cards.Blocker ("REJECTED": a tap of a half-done card would demand more than it will use): the mix ran ch to half
    a bar, so a tap needs half an item of x; with exactly that it is ready, with one unit less it is blocked on half an
    item. needs still lists the whole item one completion takes: the card's cost, constant while the bar runs."""
    for x0, ready in ((Q, True), (Q - 1, False)):
        r = world(x0=x0, gen=0)
        a = advance(with_mix(new_save(r), r, 0, {CH: BP}), r, 50)
        assert (engine_work.blocker(a, r, CH) is None) is ready, x0
        if not ready:
            assert engine_work.blocker(a, r, CH) == Blocker(AtLeast(StoreValue(X), Q // 2, Q // 2), None)
        cv = card_view(a, r, CH)
        assert cv is not None and cv.needs == (Need(X, Q, segment(a, r, X)),)


def test_needs_list_one_completion_under_the_modifiers_aimed_at_the_input():
    """CardView.needs: ch takes an item of x; once a trigger lands x2 on that cost line, it needs two items, before
    and halfway through a bar alike."""
    doubled = mul(RateRef(CH, FlowKind.COST, X), 20_000, "t")
    raise_cost = TriggerDef(TriggerId("t"), AfterTime(10), Outcome(modifiers=(doubled,)))
    r = rules([StoreDef(X, 100 * Q, 10 * Q)], cards=[CardDef(CH, 100, inputs=(Amount(X, Q),))], triggers=[raise_cost])
    s = new_save(r)
    assert view_of(s, r, CH).needs[0].quantity == Q
    a = advance(s, r, 10)
    assert view_of(a, r, CH).needs[0].quantity == 2 * Q
    half = advance(with_mix(a, r, 10, {CH: BP}), r, 60)
    assert view_of(half, r, CH).needs[0].quantity == 2 * Q


def test_a_need_is_one_whole_completion_and_readiness_asks_for_the_rest_rounded_up():
    """cards.Blocker, "Rate form"; view.Need: a card's need is what one whole completion takes under the modifiers aimed
    at its line, the same however far the bar has run. Readiness asks only for the rest of the current completion,
    prorated to the work left and rounded up as a cost is. An input of 7 units doubled is 14; the mix ran the card to a
    bar of 665_000 of 1_000_000, so the rest is 14 * 0.335 = 4.69 units, which needs 5; undoubled it is 2.345, which
    needs 3. A store holding the rest but less than the whole is ready; one unit short of the rest is blocked on it."""
    line = RateRef(CH, FlowKind.COST, X)
    for mods, whole, rest, drawn in (((), 7, 3, 5), ((mul(line, 2 * BP, "twice"),), 14, 5, 10)):
        for stock, ready in ((rest - 1, False), (rest, True)):
            # by 133 s the work is 665_000 and has drawn its share of the whole, rounded up (4.655 -> 5, 9.31 -> 10),
            # so the store reads `stock`
            r = rules([StoreDef(X, 100 * Q, drawn + stock)], cards=[CardDef(CH, 100, inputs=(Amount(X, 7),))])
            s = with_mix(new_save(r, mods), r, 0, {CH: BP // 2})
            assert view_of(s, r, CH).needs == (Need(X, whole, segment(s, r, X)),)
            a = advance(s, r, 133)
            assert val(a, r, X) == stock
            cv = card_view(a, r, CH)
            assert cv is not None and cv.needs == (Need(X, whole, segment(a, r, X)),)
            assert (cv.blocker is None) is ready and engine_work.ready(a, r, CH) is ready
            if not ready:
                assert cv.blocker is not None and cv.blocker.condition == AtLeast(StoreValue(X), rest, rest)


def test_needs_follow_the_order_the_inputs_are_declared_in():
    """CardView.needs: inputs in declaration order, then requires (not sorted by store)."""
    r = rules([StoreDef(X, 100 * Q, 0), StoreDef(Z, 100 * Q, 0)],
              cards=[CardDef(C, 100, inputs=(Amount(Z, Q), Amount(X, 2 * Q)))])
    s = new_save(r)
    cv = card_view(s, r, C)
    assert cv is not None and [(n.store, n.quantity) for n in cv.needs] == [(Z, Q), (X, 2 * Q)]


def test_needs_keep_the_larger_quantity_whichever_side_it_is_on():
    """CardView.needs: one entry per store at the larger quantity. Here the input (3 items) is larger than the requires
    (1 item), where in the world above it is the other way round."""
    r = rules([StoreDef(X, 100 * Q, 0)], cards=[CardDef(C, 100, inputs=(Amount(X, 3 * Q),),
                                                        requires=(AtLeast(StoreValue(X), Q, Q),))])
    s = new_save(r)
    cv = card_view(s, r, C)
    assert cv is not None and cv.needs == (Need(X, 3 * Q, segment(s, r, X)),)


def test_needs_list_each_store_once_at_the_larger_quantity_locked_stores_included():
    """CardView.needs: inputs then requires, one entry per store at the larger quantity (c: max(1, 2) items of x), each
    with the store's own segment, a locked store (z) included."""
    r = world()
    s = new_save(r)
    c, c2 = card_view(s, r, C), card_view(s, r, C2)
    assert c is not None and c.needs == (Need(X, 2 * Q, segment(s, r, X)),)
    assert c2 is not None and c2.needs == (Need(X, Q, segment(s, r, X)), Need(Z, Q, segment(s, r, Z)))
    assert Z not in [ln.store for ln in view(s, r).ledger]


def test_tap_s_is_the_rest_of_the_current_completion_at_the_current_speed():
    """CardView.tap_s / work.tap_seconds: a whole completion (100 s) from an empty bar, half from a half bar, doubled by
    tired hands; None when the speed is 0."""
    r = world(x0=10 * Q, gen=0)
    fresh = new_save(r)
    assert view_of(fresh, r, CH).tap_s == 100 and engine_work.tap_seconds(fresh, r, CH) == 100
    half = advance(with_mix(fresh, r, 0, {CH: BP}), r, 50)
    assert view_of(half, r, CH).tap_s == 50
    tired = new_save(r, (mul(LaneSpeed(HANDS), 5000, "tired"),))
    assert view_of(tired, r, CH).tap_s == 200
    stopped = new_save(r, (add(WorkRef(CH), -BP, "stop"),))
    assert view_of(stopped, r, CH).tap_s is None and engine_work.tap_seconds(stopped, r, CH) is None


def test_tappable_and_ready_read_the_lane_the_lock_and_the_cap():
    """work.tappable: known, unlocked, not completed, its lane free; work.ready: tappable and no blocker."""
    r = world(x0=10 * Q)
    s = new_save(r)
    assert engine_work.tappable(s, r, CH) and engine_work.ready(s, r, CH)
    assert not engine_work.tappable(s, r, D)
    busy = tap(s, r, 0, CP)
    assert not engine_work.tappable(busy, r, CH) and not engine_work.ready(busy, r, CH)
    assert engine_work.blocker(busy, r, CH) is None  # the lane is never a blocker
    after = advance(busy, r, 50)
    assert not engine_work.tappable(after, r, CP) and engine_work.is_completed(after, r, CP)
    assert engine_work.completions(after, r, CP) == 1 and engine_work.effective_cap(after, r, CP) == 1


def test_with_no_opening_the_view_reports_every_card_unlocked():
    """View.unlocked with rules.opening None: the effective set, so every card (and standing action) is listed."""
    r = world(opening=None)
    got = view(new_save(r), r).unlocked
    for c in (C, C2, D, CP, CH, RK):
        assert Unlock(UnlockKind.CARD, c) in got
    assert Unlock(UnlockKind.ACTION, GEN) in got
