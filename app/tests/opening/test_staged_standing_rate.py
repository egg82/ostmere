"""Each finished stage of a staged card adds an entry on a standing's make rate (week-three-plan item 9), on
fixtures/stagedrate.toml merged onto the opening alone: the standing takes the outcome modifier as a target, explain()
lists one sourced entry per stage and the summed rate, the standing stops where its season pool ends with the entries
kept, and runs at the same rate once the next turn refills it. Nothing in the loader or the engine needed to change;
the season check passes with the standing on its own pool."""
from pathlib import Path

import pytest

from ashfall_app.engine import (
    ActionId, CardId, FlowKind, ModifierKind, RateRef, Rules, Save, StoreId, TapCard, advance, decide, explain,
    new_save, value,
)
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "stagedrate.toml"
FORGE, STOCK, POOL = ActionId("t_forge"), StoreId("t_stock"), StoreId("t_pool")
MAKE = RateRef(FORGE, FlowKind.MAKE, STOCK)
STAGES_DONE_BY, TURN_1, POOL_EMPTY, TURN_2 = 200, 3600, 3600 + 4 * 3600, 36_000


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def staged(rules: Rules, stages: int = 3) -> Save:
    """The save once `stages` stages are tapped and finished, one after the other."""
    s = advance(new_save(rules), rules, 0)
    for n in range(stages):
        s = advance(decide(s, rules, n * 60, TapCard(CardId("t_stage"))), rules, (n + 1) * 60)
    return s


def rate(s: Save, rules: Rules) -> int:
    return explain(s, rules, MAKE).per_hour


def test_three_stages_show_three_sourced_entries_and_the_summed_rate():
    rules = to_rules(load_with(FIXTURE))
    s = advance(staged(rules), rules, TURN_1)
    e = explain(s, rules, MAKE)
    assert [(m.kind, m.amount_bp, str(m.source)) for m in e.adds] == [(ModifierKind.ADD_BP, 2000, "t_stage")] * 3
    assert rate(s, rules) == e.base_per_hour * 16 // 10 and e.muls == ()


def test_fewer_stages_show_fewer_entries():
    rules = to_rules(load_with(FIXTURE))
    s = advance(staged(rules, 2), rules, TURN_1)
    e = explain(s, rules, MAKE)
    assert len(e.adds) == 2 and rate(s, rules) == e.base_per_hour * 14 // 10


def test_the_standing_stops_at_its_pools_end_keeps_its_entries_and_resumes_at_the_same_rate():
    rules = to_rules(load_with(FIXTURE))
    s = staged(rules)
    running = rate(advance(s, rules, TURN_1), rules)
    dry = advance(s, rules, POOL_EMPTY + 100)
    assert value(dry, rules, POOL, POOL_EMPTY + 100) == 0
    assert value(dry, rules, STOCK, POOL_EMPTY + 3600) == value(dry, rules, STOCK, POOL_EMPTY + 100), "stopped"
    assert len(explain(dry, rules, MAKE).adds) == 3, "the entries are kept"
    refilled = advance(s, rules, TURN_2 + 1)
    assert rate(refilled, rules) == running and len(explain(refilled, rules, MAKE).adds) == 3
    assert value(refilled, rules, STOCK, TURN_2 + 3600) > value(refilled, rules, STOCK, TURN_2 + 1)


def test_a_modifier_aimed_at_a_standing_nothing_declares_fails_the_loader(tmp_path: Path):
    text = FIXTURE.read_text()
    assert text.count('id = "t_forge", flow') == 1
    path = tmp_path / FIXTURE.name
    path.write_text(text.replace('id = "t_forge", flow', 'id = "t_missing", flow'))
    with pytest.raises(ValueError, match="t_missing"):
        load_with(path)


def test_the_season_check_ran_on_the_fixture_and_refuses_a_turn_that_raises_the_standing(tmp_path: Path):
    text = FIXTURE.read_text()
    old = 'outcome = { stores = [{ store = "t_pool", items = 4 }] }'
    assert text.count(old) == 1
    raise_rate = ('outcome = { stores = [{ store = "t_pool", items = 4 }], modifiers = [{ target = "rate", id = "t_forge", '
                  'flow = "make", store = "t_stock", kind = "add_bp", amount_bp = 2000, source = "t_turn_2" }] }')
    path = tmp_path / FIXTURE.name
    path.write_text(text.replace(old, raise_rate))
    with pytest.raises(ValueError, match="never moves a rate"):
        load_with(path)
