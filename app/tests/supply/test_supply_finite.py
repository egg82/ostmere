"""The finite-supply check (rules/checks/world/finite_checks.py, issue #438) on the fixture outpost (chapter.py): the outpost's
store is made by a card that stops on the town's store, which an uncapped gatherer makes, so no progress gate reading
the outpost's store is flagged. The control makes the town's store a finite pool instead, and the same gates are."""
from dataclasses import replace

import pytest

from ashfall_app.engine import QUANTITY_SCALE as Q, Amount, AfterTime, Outcome, Rules, TriggerDef, TriggerId
from ashfall_app.rules.checks.world.finite_checks import check_finite_supply
from tests.supply.chapter import GATHER, HAUL, HOLD_A, HOLD_B, KEEP, POST, RAID, TOWN, TRIP, TWIN, rules, without

PER = Q
READ = frozenset({POST})
"""The outpost's store as a tally the stocked trigger reads (chapter.py)."""


def pooled(r: Rules, pool: int) -> Rules:
    """The town's store a finite pool: its gatherer gone, a trigger landing `pool` items once, and the draws on the
    outpost's store that no cap bounds gone, so only the supply is in question."""
    gone = without(r, GATHER, TRIP, TWIN, HOLD_A, HOLD_B)
    fill = TriggerDef(TriggerId("fill"), AfterTime(0), Outcome(stores=(Amount(TOWN, pool * PER),)))
    standing = tuple(a for a in r.standing if a.id not in (KEEP, RAID))
    return replace(gone, standing=standing, triggers=(*gone.triggers, fill))


def test_the_outpost_made_by_an_uncapped_maker_flags_no_gate_reading_it() -> None:
    check_finite_supply(rules(), READ)


@pytest.mark.parametrize("flag", ["upkeep", "fight"])
def test_each_standing_action_alone_passes_too(flag: str) -> None:
    check_finite_supply(rules(**{flag: False}), READ)


def test_the_stage_gate_and_the_stock_gate_pass_with_a_pool_that_covers_them() -> None:
    """Control for the planted case: 5 items in the town's store make 10 in the outpost's, the 3 stages and the 6 the
    stock gate reads."""
    check_finite_supply(pooled(rules(), 5), READ)


def test_a_gate_on_a_store_whose_only_maker_is_a_finite_pool_is_flagged() -> None:
    with pytest.raises(ValueError, match="store (town|post): finite: supplies"):
        check_finite_supply(pooled(rules(), 4), READ)


def test_the_stage_count_alone_is_flagged_on_a_finite_pool_too() -> None:
    """One item in the town's store lands 2 in the outpost's: the build's 3 stages cannot all be paid."""
    r = pooled(rules(), 1)
    noread = replace(r, triggers=tuple(t for t in r.triggers if str(t.id) != "stocked"))
    with pytest.raises(ValueError, match="store (town|post): finite: supplies"):
        check_finite_supply(noread)


def test_the_filler_is_the_outposts_only_maker() -> None:
    """Without the filler nothing makes the outpost's store, so the control above is not passing for want of a maker."""
    with pytest.raises(ValueError, match="store post: finite"):
        check_finite_supply(without(rules(), HAUL, TWIN), READ)
