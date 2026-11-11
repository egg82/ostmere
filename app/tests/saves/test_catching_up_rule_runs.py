"""What the rules did lately (saves/ruleruns.py, KEPT records) after a catch-up in slices is what one unbounded advance
leaves: a rule that started early and lets go late is still recorded, with its starts, when more rules are in play
than a save keeps records of."""
import pytest
from sqlalchemy import Engine

from ashfall_app.saves.interface import Played, Ruleset
from ashfall_app.saves.ruleruns import KEPT
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.saves.behind import BUSY_AWAY_S, seed_busy, snapshot
from tests.saves.chunks import every, never


@pytest.fixture
def caught_up(engine: Engine, rs: Ruleset, clock: FakeClock, account: int) -> tuple[int, int, list[Played], Played]:
    """Two busy saves, one caught up in slices and one in a single advance, in setup: their ids, the slices, the whole."""
    sliced_id, whole_id = seed_busy(engine, rs, account, clock()), seed_busy(engine, rs, account, clock())
    clock.tick(BUSY_AWAY_S)
    sliced = PgSaves(engine, rs, clock, stop_for=every(5))
    slices: list[Played] = []
    while not slices or slices[-1].catching_up_to is not None:
        assert len(slices) < 200, "still catching up"
        slices.append(sliced.advance(account, sliced_id))
    return sliced_id, whole_id, slices, PgSaves(engine, rs, clock, stop_for=never).advance(account, whole_id)


def test_rule_runs_past_the_kept_count_after_slices_equal_those_of_one_advance(
        engine: Engine, caught_up: tuple[int, int, list[Played], Played]):
    sliced_id, whole_id, slices, whole = caught_up
    assert len(slices) > 3 and len(whole.save.orders) > KEPT, "the span is not worth slicing, or has too few rules"
    assert len(whole.rule_runs) == KEPT, "more rules ran than are kept: the oldest go"
    assert slices[-1].rule_runs == whole.rule_runs
    assert snapshot(engine, sliced_id) == snapshot(engine, whole_id)
