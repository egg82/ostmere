"""A season's second turn (week-five-plan item 1), on fixtures/seasonturn.toml merged onto the opening alone: the third
turn refills a new pool and drains the last season's chip store and its gift pool inside the hour with a one-item pool
and a standing action (week four's thaw), retiring no rule. A rule the player wrote on the chip stays and fires nothing
once the chip cannot show. The order card the earlier turn's retirement ended is served with the unlock that ends it."""
from pathlib import Path

import pytest

from ashfall_app.api.service import Game
from ashfall_app.engine import (
    AtLeast, CardId, ChipId, Order, Rules, SetOrders, StoreId, StoreValue, TapCard, advance, decide, new_save,
    units, value,
)
from ashfall_app.engine.counts import completions
from ashfall_app.engine.gates import shown_chips
from ashfall_app.opening import checks
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules
from ashfall_app.saves.ruleset import ruleset

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "seasonturn.toml"
TURN_2, TURN_3, HOUR = 50_400, 64_800, 3_600
HEAP, GIFT, CHIP, CLEAR = StoreId("t_heap"), StoreId("t_gift"), ChipId("t_heaped"), CardId("t_clear")


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def rules_of(path: Path = FIXTURE) -> Rules:
    return to_rules(load_opening(OPENING, (path,)))


def level(r: Rules, t: int, store: StoreId) -> int:
    return value(advance(new_save(r), r, t), r, store, t)


def test_the_turn_drains_the_chip_store_and_the_gift_pool_inside_the_hour_and_the_chip_never_shows_after():
    r = rules_of()
    before = advance(new_save(r), r, TURN_3 - 1)
    assert CHIP in shown_chips(before, r) and level(r, TURN_3 - 1, HEAP) == level(r, TURN_3 - 1, GIFT) == units(4)
    for t in (TURN_3 + HOUR, TURN_3 + 40 * HOUR):
        assert level(r, t, HEAP) == level(r, t, GIFT) == 0
        assert CHIP not in shown_chips(advance(new_save(r), r, t), r)


def test_a_rule_the_player_wrote_on_the_chip_survives_the_turn_and_fires_nothing_once_it_cannot_show():
    r = rules_of()
    rule = Order(AtLeast(StoreValue(HEAP), units(3), units(1)), TapCard(CLEAR))
    s = decide(advance(new_save(r), r, TURN_2 + 60), r, TURN_2 + 60, SetOrders((rule,)))
    drained = advance(s, r, TURN_3 + HOUR)
    assert advance(s, r, TURN_3 - 1).orders == drained.orders == (rule,)
    ran = completions(drained, r, CLEAR)
    assert advance(s, r, TURN_3 + 40 * HOUR).orders == (rule,)
    assert completions(advance(s, r, TURN_3 + 40 * HOUR), r, CLEAR) == ran


def test_the_turn_retires_no_rule_and_the_earlier_one_did():
    r = rules_of()
    assert [t.outcome.retire_orders for t in r.triggers if t.id in ("t_turn_2", "t_turn_3")] == [(CLEAR,), ()]


def test_the_order_card_is_served_with_the_unlock_that_ends_its_offering():
    o = load_opening(OPENING, (FIXTURE,))
    cards = [c for c in Game(o, ruleset(o, "test", 1)).content().order_cards if c.chip == "t_heaped"]
    assert [(c.offered_until.category, c.offered_until.id) for c in cards if c.offered_until] == [("feature", "t_turned")]
    assert all(c.offered_until is None for c in Game(o, ruleset(o, "test", 1)).content().order_cards if c.chip != "t_heaped")


def test_an_offered_until_naming_an_unknown_unlock_is_refused(tmp_path: Path):
    path = edited(tmp_path, ('offered_until = { unlock_kind = "feature", id = "t_turned" }',
                             'offered_until = { unlock_kind = "feature", id = "t_nope" }'))
    with pytest.raises(ValueError, match="t_nope"):
        load_opening(OPENING, (path,))


def skipped(o: Opening) -> None:
    """Stands in for the season check."""


def test_the_thaw_check_sees_this_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Control: the season check is what refuses a turn that opens the thaw with no pool it fills."""
    path = edited(tmp_path, ('stores = [{ store = "t_pool2", items = 4 }, { store = "t_thaw_left", items = 1 }]',
                             'stores = [{ store = "t_pool2", items = 4 }]'))
    with pytest.raises(ValueError, match="t_thaw"):
        load_opening(OPENING, (path,))
    monkeypatch.setattr(checks, "check_season_turns", skipped)
    load_opening(OPENING, (path,))
