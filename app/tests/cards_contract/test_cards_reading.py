"""Invariants 4 and 31: every reading function leaves the save equal to a copy taken before, the new card reads among
them (work.blocker, tappable, ready, tap_seconds, completions, effective_cap, is_completed, greyed, starved,
explain_work and view)."""
import copy

import pytest
from hypothesis import given

from ashfall_app.engine import (
    FlowKind, RateRef, Rules, Save, advance, explain, explain_work, level, next_event, segment, value, view, xp,
)
from ashfall_app.engine import work as engine_work
from cards_gen import Scenario, few, play, scenario_st, span
from cards_world import rich_rules, rich_saves


def read_everything(s: Save, r: Rules) -> None:
    for sd in r.stores:
        value(s, r, sd.id, s.time + span(r, 5000))
        segment(s, r, sd.id)
        engine_work.starved(s, r, sd.id)
    for sk in r.skills:
        xp(s, r, sk.id, s.time + 100)
        level(s, r, sk.id, s.time + 100)
    next_event(s, r)
    for c in r.cards:
        explain_work(s, r, c.id)
        explain(s, r, RateRef(c.id, FlowKind.XP))
        for f in c.makes + c.costs:
            explain(s, r, RateRef(c.id, FlowKind.MAKE if f in c.makes else FlowKind.COST, f.store))
        engine_work.blocker(s, r, c.id)
        engine_work.tappable(s, r, c.id)
        engine_work.ready(s, r, c.id)
        engine_work.tap_seconds(s, r, c.id)
        engine_work.completions(s, r, c.id)
        engine_work.effective_cap(s, r, c.id)
        engine_work.is_completed(s, r, c.id)
    for m in s.mixes:
        engine_work.greyed(s, r, m.id)
    view(s, r)


@pytest.mark.parametrize("s", rich_saves(), ids=lambda s: f"t{s.time}")
def test_reading_a_rich_run_writes_nothing(s: Save):
    """Invariants 4, 31 over saves holding every kind of card state, one test per save of the run so that each stays
    under the per-test time ceiling (reading everything costs about 0.1 s a save; the run's eleven saves, one test,
    were about 1 s)."""
    before = copy.deepcopy(s)
    read_everything(s, rich_rules())
    assert s == before


@few(8)
@given(sc=scenario_st())
def test_reading_a_random_save_writes_nothing(sc: Scenario):
    """Invariants 4, 31 over random card worlds, and reading gives the same answer twice."""
    s = play(sc)
    r = sc.rules
    before = copy.deepcopy(s)
    read_everything(s, r)
    assert s == before
    assert view(s, r) == view(before, r)
    assert advance(s, r, s.time + 100) == advance(before, r, s.time + 100)
