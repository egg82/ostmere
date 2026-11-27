"""What a rule's mix made while the rule was on (contract/rule-runs.txt, "RULE RUNS", "Made"): the engine reports the levels of the
stores its mix makes when the rule comes on and lets go, and the saves layer turns the pair into `made`, as it does for
an ended goal stint (test_stint_made)."""
from ashfall_app import engine as e
from ashfall_app.engine import BP, AtLeast, CardId, CardShare, Mix, MixId, Order, SaveMix, SetOrders, StoreValue, SwitchMix, TapCard
from ashfall_app.engine.core.units import units
from ashfall_app.saves.ruleruns import RuleRun, merged
from tests.goals.test_goal_rows import LOG, PLANK, running, world

BAND = AtLeast(StoreValue(LOG), units(45), units(40))
"""Felling takes the log store from 40 to 45 in an hour and 40; the band is then on until sawing brings it back to 40."""


def _played(then: e.OrderVerb) -> tuple[RuleRun, tuple[e.RuleChange, ...]]:
    """The entry of a rule `BAND` -> `then` after its band came on and let go, read in steps as a page would, and the
    changes it saw. A second rule on the same band sets the saw mix, which is what brings the band back down."""
    r, s = world(logs=40)
    s = e.decide(running(r, s, {"fell": BP}), r, s.time, SaveMix(Mix(MixId("saw"), (CardShare(CardId("saw"), BP),))))
    s = e.decide(s, r, s.time, SetOrders(tuple(dict.fromkeys((Order(BAND, then), Order(BAND, SwitchMix(MixId("saw"))))))))
    runs: tuple[RuleRun, ...] = ()
    seen: tuple[e.RuleChange, ...] = ()
    for _ in range(40):
        step = e.advance_logged(s, r, s.time + 600)
        runs, seen, s = merged(runs, step.rule_changes, s.orders), seen + step.rule_changes, step.save
        if any(not c.on for c in step.rule_changes):
            break
    run = next(r for r in runs if r.order.then == then)
    assert run.on_at is not None and run.off_at is not None and run.off_at > run.on_at, "control: on, then off"
    return run, seen


def test_a_rule_that_switches_a_mix_lists_what_the_mix_made_between_its_start_and_its_let_go() -> None:
    run, seen = _played(SwitchMix(MixId("saw")))
    assert [c.on for c in seen if c.order.then == SwitchMix(MixId("saw"))] == [True, False] \
        and all(c.levels for c in seen), "control: both ends reported levels"
    assert run.ended is None and run.on_levels == ()
    [(store, gained)] = run.made
    assert run.on_at is not None and run.off_at is not None
    assert store == PLANK and gained == units(6) * (run.off_at - run.on_at) // 3600, "saw makes 6 an hour"


def test_a_rule_with_no_mix_change_lists_nothing() -> None:
    run, seen = _played(TapCard(CardId("nap")))
    taps = [c for c in seen if c.order.then == TapCard(CardId("nap"))]
    assert [c.on for c in taps] == [True, False] and all(c.levels == () for c in taps)
    assert run.made == ()


def test_a_rule_back_on_lists_nothing_until_it_lets_go_again() -> None:
    run, _ = _played(SwitchMix(MixId("saw")))
    order = run.order
    assert run.off_at is not None
    again = merged((run,), (e.RuleChange(run.off_at + 60, order, True, None, None, ((PLANK, 0),)),), (order,))
    assert again[0].made == () and again[0].starts == run.starts + 1


def test_a_rule_whose_mix_gained_less_than_an_item_lists_nothing() -> None:
    order = Order(BAND, SwitchMix(MixId("saw")))
    on, off = ((PLANK, 0),), ((PLANK, e.QUANTITY_SCALE - 1),)
    [run] = merged((), (e.RuleChange(10, order, True, None, None, on), e.RuleChange(20, order, False, None, None, off)), (order,))
    assert (run.off_at, run.made) == (20, ()), "no zero-gain entry"
    [whole] = merged((), (e.RuleChange(10, order, True, None, None, on), e.RuleChange(20, order, False, None, None, ((PLANK, e.QUANTITY_SCALE),))), (order,))
    assert whole.made == ((PLANK, e.QUANTITY_SCALE),), "control: a whole item is listed"
