"""SPENT, the spent set (engine DESIGN.txt, "SPENT", invariant 133 and the plan's "a store whose only maker is spent is
spent"). Written blind from that part; MUTANTS_spent.txt names the wrong implementations each test must turn red for.
Each scenario of spent_world.scenarios() has EAT dry on one store from the first instant of its mix, beside R1: the
test reads whether the store is spent through EAT's Run, so a scenario cannot pass by EAT not being dry at all."""
import pytest

from ashfall_app.engine import FlowKind, RateRef, RunKind, advance, explain
from spent_world import (
    EAT, R1, begin, card_view, gained_of, gains, kills, scenarios, share_of, spent_kind,
    spent_store_of,
)


SCENARIOS = scenarios()


@kills(5, 10, 11, 15, 16, 22)
@pytest.mark.parametrize("name", list(SCENARIOS))
def test_a_store_is_spent_exactly_when_every_maker_of_it_is_stuck_on_a_spent_empty_store(name: str):
    """Invariant 133: EAT is dry on the scenario's store, and its Run is SPENT when the store is spent, PAUSED when
    something in play can still make it; R1 takes EAT's whole share either way (CHOICES "Giver")."""
    sc = SCENARIOS[name]
    s, t = begin(sc), sc.t0 + 50
    cost = explain(advance(s, sc.rules, t), sc.rules, RateRef(EAT, FlowKind.COST, sc.store))
    assert cost.run.store == sc.store, "EAT is dry on the scenario's store in both directions"
    cv = card_view(s, sc.rules, EAT, t)
    if sc.spent:
        assert (cost.run.kind, cv.run, spent_store_of(cv)) == (spent_kind(), spent_kind(), sc.store)
    else:
        assert (cost.run.kind, cv.run, spent_store_of(cv)) == (RunKind.PAUSED, RunKind.PAUSED, None)
    assert (share_of(s, sc.rules, R1, t), gains(s, sc.rules, R1, t)) == (6500, ((EAT, 4000),))
    assert gained_of(cv) == ()
