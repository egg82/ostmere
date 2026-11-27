"""Controls on the SPENT fixtures themselves (spent_world.py): they run now, before item 1 exists, and stay."""
from ashfall_app.engine import FlowKind, RateRef, RunKind, advance, explain, view
from spent_world import EAT, MK, R1, begin, scenarios, share_of


def test_the_scenarios_cover_both_answers_and_every_named_shape():
    """Spent and not-spent worlds in numbers that make a one-sided mutant visible, built over the shapes of invariant 133."""
    sc = scenarios()
    spent = {n for n, v in sc.items() if v.spent}
    assert len(spent) >= 8 and len(sc) - len(spent) >= 6
    assert {"chain", "cycle", "trigger adds", "locked maker", "completed maker", "retired maker"} <= spent


def test_every_scenario_has_eat_dry_on_its_store_so_none_passes_by_eat_running():
    """EAT is dry on the scenario's store in every world: PAUSED where a maker is in play, SPENT (the same Pause, CHOICES
    "Spent card") where the store is spent, so the dry cases are real."""
    for name, sc in scenarios().items():
        s = begin(sc)
        t = sc.t0 + 50
        e = explain(advance(s, sc.rules, t), sc.rules, RateRef(EAT, FlowKind.COST, sc.store))
        assert (e.run.kind, e.run.store) == (RunKind.SPENT if sc.spent else RunKind.PAUSED, sc.store), name
        assert share_of(s, sc.rules, R1, t) == 6500, name  # R1 alone takes EAT's 4000 (CHOICES "Giver")


def test_the_out_of_play_makers_are_out_of_play():
    """The locked, retired and completed makers really are not cards a player could tap."""
    sc = scenarios()
    for name in ("locked maker", "retired maker"):
        v = view(advance(begin(sc[name]), sc[name].rules, 50), sc[name].rules)
        assert MK not in {c.card for c in v.cards}, name
    v = view(advance(begin(sc["completed maker"]), sc["completed maker"].rules, 52), sc["completed maker"].rules)
    assert MK in {c.card for c in v.completed}
