"""A season's turn as content (week-two-plan item 6), on fixtures/season.toml merged onto the opening alone: the
standing action the turn opens stops at the next turn's instant exactly, and the loader refuses a card or standing
action a turn opens without a pool that turn fills, or a turn aimed at a rate. Each refusal is the fixture edited,
beside a control that loads."""
from pathlib import Path

import pytest

from ashfall_app.engine import Rules, StoreId, advance, new_save, units, value
from ashfall_app.opening import checks
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules
from tests.opening.season_plants import PLANTS, Plant

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "season.toml"
TURN_1, TURN_2 = 36_000, 50_400
POOL = StoreId("t_pool")


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def load_with(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def skipped(o: Opening) -> None:
    """Stands in for the season check, so a plant is shown to break nothing else."""


def pool_at(r: Rules, t: int) -> int:
    return value(advance(new_save(r), r, t), r, POOL, t)


def test_the_standing_action_stops_at_the_next_turns_instant_exactly():
    r = to_rules(load_with(FIXTURE))
    assert pool_at(r, TURN_1 - 1) == 0
    assert pool_at(r, TURN_1) == units(4)
    assert 0 < pool_at(r, TURN_2 - 1) <= units(1)
    assert pool_at(r, TURN_2) == 0 == pool_at(r, TURN_2 + 3600)


@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p.name)
def test_each_planted_fixture_is_valid_rules_and_breaks_only_its_check(tmp_path: Path, plant: Plant, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(checks, "check_season_turns", skipped)
    to_rules(load_with(edited(tmp_path, *plant.edits)))


@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p.name)
def test_each_planted_fixture_fails_the_check_naming_the_id(tmp_path: Path, plant: Plant):
    with pytest.raises(ValueError, match=plant.failing_id):
        load_with(edited(tmp_path, *plant.edits))


@pytest.mark.parametrize("plant", PLANTS[:2], ids=lambda p: p.name)
def test_the_same_shape_unmarked_is_no_season_and_loads(tmp_path: Path, plant: Plant):
    """The marker is what makes a turn a season: an arrival or a story step opens cards without a pool."""
    marked = (("season = true\nwhen = { test = \"after_time\", value = 36000 }", "when = { test = \"after_time\", value = 36000 }"),)
    load_with(edited(tmp_path, *plant.edits, *marked))
