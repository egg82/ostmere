"""The loss lines on the wire (api/CONTRACT.txt, "LOSS LINES"): a pooled card's three fields on CardInfo.fight, null on
every other fight; a fold note's count and the pencil hand on a served day; the fields named in openapi.json."""
import json
from pathlib import Path

import pytest

from ashfall_app.api.service import Game
from ashfall_app.opening.schema import OPENING, load_opening
from ashfall_app.saves.journal import ComposedDay, Note
from ashfall_app.saves.ruleset import ruleset

FIXTURE = Path(__file__).resolve().parent / "opening" / "fixtures" / "loss_lines.toml"
SPEC = Path(__file__).resolve().parents[1] / "client" / "generated" / "openapi.json"


@pytest.fixture(scope="module")
def game() -> Game:
    o = load_opening(OPENING, (FIXTURE,))
    return Game(o, ruleset(o, "t", 1))


def test_the_pooled_card_serves_its_fields_and_every_other_fight_null(game: Game):
    content = game.content()
    fights = {c.card: c.fight for c in content.card_infos if c.fight is not None}
    pool, plain = fights["t_pool"], fights["t_plain"]
    assert (pool.loss_pool, pool.loss_notes, pool.on_loss_key, pool.lost_line_keys) == (
        ["t_l_pool_1", "t_l_pool_2", "t_l_pool_3", "t_l_pool_4", "t_l_pool_5", "t_l_pool_6"], ["t_n_pool_1", "t_n_pool_2", "t_n_pool_3"], "t_on_loss", [])
    assert (plain.loss_pool, plain.loss_notes, plain.on_loss_key) == (None, None, None)
    raids = [a.fight for a in content.standing_infos if a.fight is not None]
    assert raids and all((f.loss_pool, f.loss_notes, f.on_loss_key) == (None, None, None) for f in raids)


def test_a_served_day_carries_the_fold_count_in_pencil(game: Game):
    day = ComposedDay(3, (Note("t_pool", "loss", "t_n_pool_2"), Note("t_pool", "fold", "ui.journal.fold", 4)), None)
    (served,) = game.journal_days((day,))
    assert [(n.subject, n.slot.value, n.key, n.hand.value, n.sketch, n.count) for n in served.day_notes] == [
        ("t_pool", "loss", "t_n_pool_2", "pencil", None, None), ("t_pool", "fold", "ui.journal.fold", "pencil", None, 4)]


def test_openapi_names_the_fields():
    schemas = json.loads(SPEC.read_text())["components"]["schemas"]
    assert {"loss_pool", "loss_notes", "on_loss_key"} <= set(schemas["FightInfo"]["properties"])
    assert "count" in schemas["DayNote"]["properties"]
    assert {"loss", "fold"} <= set(schemas["Slot"]["enum"])
