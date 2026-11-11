"""Installed rules (engine DESIGN.txt, part "TOWNSFOLK, INSTALLED RULES AND OFFERS": "Installed rule", "Installs land
once", "A finished one-off rule stays"; invariants 59 and 60; api CONTRACT.txt, "A LANE RUN BY RULES"). Outcome.orders
lands after `raises` and before `queues` and `starts`: each RuleInstall(c, first) is Order(AfterTime(0), TapCard(c)),
the first=True ones as one block at the top, the rest appended, each skipped when an equal order is already held,
every new latch true. Afterwards it is an ordinary rule: removed, it never comes back from the same install."""
from ashfall_app.engine import (
    AfterTime, CardDef, CardId, Order, OrderState, Outcome, RuleChange, RuleInstall, SetOrders, TapCard, TriggerDef,
    TriggerId, Unlock, UnlockKind, advance, advance_logged, decide, new_save, view,
)
from cards_world import done
from town_world import H, NEVER, T1, T2, TC, TOWN, always, running, started, town

GO, GO2 = TriggerId("go"), TriggerId("go2")
T3, T4 = CardId("t3"), CardId("t4")
MORE_TOWN = (CardDef(T3, 100, lane=TOWN), CardDef(T4, 100, lane=TOWN))
BEFORE = (Order(NEVER, TapCard(H)), always(T2))
"""What the player had set before the install: a waiting hands rule and the town's always rule."""


def go(outcome: Outcome, at: int = 10, trigger: TriggerId = GO) -> TriggerDef:
    return TriggerDef(trigger, AfterTime(at), outcome)


def installs(*found: RuleInstall) -> Outcome:
    return Outcome(orders=found)


def test_a_plain_install_is_appended_as_the_lanes_always_rule_with_its_latch_on():
    """Installed rule: RuleInstall(t1) gives Order(AfterTime(0), TapCard(t1)) after the orders already held, latch
    True, nothing marking it as installed."""
    r = town(triggers=(go(installs(RuleInstall(T1))),))
    s = advance(started(r, SetOrders(BEFORE)), r, 10)
    assert s.orders == BEFORE + (Order(AfterTime(0), TapCard(T1)),)
    assert s.latches == (False, True, True)


def test_first_installs_go_to_the_top_as_one_block_in_tuple_order():
    """Invariant 59: installs a(first), b, c(first), d over `before` give [a, c] + before + [b, d]; two first=True
    installs keep their tuple order (the first of them at index 0)."""
    r = town(cards=MORE_TOWN, triggers=(go(installs(RuleInstall(T1, first=True), RuleInstall(TC),
                                                    RuleInstall(T3, first=True), RuleInstall(T4))),))
    s = advance(started(r, SetOrders(BEFORE)), r, 10)
    assert s.orders == (always(T1), always(T3)) + BEFORE + (always(TC), always(T4))
    assert s.latches == (True, True, False, True, True, True)


def test_an_install_already_held_changes_nothing_and_is_not_moved():
    """Each install, in tuple order: if save.orders already holds an equal order, nothing (a first=True install of an
    order held lower down does not move it to the top)."""
    r = town(triggers=(go(installs(RuleInstall(T2, first=True), RuleInstall(T1))),))
    s = advance(started(r, SetOrders(BEFORE)), r, 10)
    assert s.orders == BEFORE + (always(T1),)


def test_an_install_is_setorders_with_that_list_at_that_instant():
    """Invariant 59: the result equals the same save given SetOrders with F + before + L at T (here the outcome has no
    other parts, so the whole saves are equal: latches, lanes and cards too)."""
    out = installs(RuleInstall(T1, first=True), RuleInstall(TC))
    r1, r0 = town(triggers=(go(out),)), town(triggers=(go(Outcome()),))
    s1 = advance(started(r1, SetOrders(BEFORE)), r1, 10)
    s0 = decide(advance(started(r0, SetOrders(BEFORE)), r0, 10), r0, 10, SetOrders((always(T1),) + BEFORE + (always(TC),)))
    assert s1 == s0


def test_an_install_sees_the_outcomes_unlocks_and_acts_at_once():
    """It lands after `raises` (so after the unlocks), and orders evaluate after the outcome: tc, locked until this
    outcome unlocks it, starts at 10; without the unlock the install still lands (a locked card may be named) and the
    town keeps its own task."""
    unlock = (Unlock(UnlockKind.CARD, TC),)
    waiting = SetOrders((Order(NEVER, TapCard(H)),))
    r = town(triggers=(go(Outcome(unlocks=unlock, orders=(RuleInstall(TC, first=True),))),))
    s = advance(started(r, waiting), r, 10)
    assert s.orders[0] == always(TC) and running(s, TOWN) == TC
    r = town(triggers=(go(installs(RuleInstall(TC, first=True))),))
    s = advance(started(r, waiting), r, 10)
    assert s.orders[0] == always(TC) and running(s, TOWN) is None


def test_an_install_lands_before_the_outcomes_starts():
    """Field order, then evaluation: an outcome installing always(t1) and starting t2 on the free town lane runs t2
    (the start takes the lane before orders evaluate); t1 takes over at t2's landing."""
    r = town(triggers=(go(Outcome(starts=(T2,), orders=(RuleInstall(T1),))),))
    s = advance(new_save(r), r, 10)
    assert s.orders == (always(T1),) and running(s, TOWN) == T2
    s = advance(s, r, 110)
    assert done(s, r, T2) == 1 and running(s, TOWN) == T1


def test_an_install_is_reported_as_coming_on():
    """Installed rule: "it is reported as coming on" (Rule changes), at the install's instant, reading no store."""
    r = town(triggers=(go(installs(RuleInstall(T1))),))
    step = advance_logged(new_save(r), r, 50)
    assert RuleChange(10, always(T1), True, None) in step.rule_changes


def test_a_removed_installed_rule_never_comes_back_from_the_same_install():
    """Invariant 60 and "Installs land once": removed by SetOrders at 20, the rule is not back at any later instant,
    though the trigger's condition (AfterTime) stays true and the town lands every 100 s."""
    r = town(triggers=(go(installs(RuleInstall(T1))),))
    s = advance(new_save(r), r, 10)
    assert s.orders == (always(T1),)
    s = decide(s, r, 20, SetOrders(()))
    for t in (100, 110, 1000, 50_000):
        s = advance(s, r, t)
        assert s.orders == (), t


def test_another_trigger_installing_an_equal_order_adds_it_again():
    """Invariant 60, the parenthesis: a different trigger (go2 at 100) installing the same order puts it back after
    the player removed the first install's."""
    r = town(triggers=(go(installs(RuleInstall(T1))), go(installs(RuleInstall(T1)), at=100, trigger=GO2)))
    s = decide(advance(new_save(r), r, 10), r, 20, SetOrders(()))
    assert advance(s, r, 99).orders == ()
    assert advance(s, r, 100).orders == (always(T1),)


def test_an_edited_installed_rule_is_the_players_rule():
    """Afterwards nothing tells an installed order from one the player set: SetOrders moves and edits it like any
    other, and its latch is kept when it is kept (Rule changes)."""
    r = town(triggers=(go(installs(RuleInstall(T1))),))
    s = advance(started(r, SetOrders(BEFORE)), r, 10)
    s = decide(s, r, 20, SetOrders((always(T1),) + BEFORE))
    assert s.orders == (always(T1),) + BEFORE and s.latches == (True, False, True)


def test_a_finished_one_off_rule_stays_passed_over():
    """"A finished one-off rule stays in the order list, PASSED_OVER (its card completed); the player removes it.
    Nothing removes an order by itself": tc installed at the top at 10 waits for t2's landing at 100, completes at
    200, and its rule stays while the town goes back to t2."""
    unlock = (Unlock(UnlockKind.CARD, TC),)
    r = town(triggers=(go(Outcome(unlocks=unlock, orders=(RuleInstall(TC, first=True),))),))
    s = advance(started(r, SetOrders((always(T2),))), r, 10)
    assert running(s, TOWN) == T2
    s = advance(s, r, 100)
    assert running(s, TOWN) == TC
    assert running(advance(s, r, 200), TOWN) == T2
    s = advance(s, r, 5000)
    assert done(s, r, TC) == 1 and s.orders == (always(TC), always(T2))
    assert view(s, r).order_states == (OrderState.PASSED_OVER, OrderState.ON) and running(s, TOWN) == T2
