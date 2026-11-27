"""A season's chore with no order card (week-four-plan item 4), on fixtures/chorechip.toml merged onto the opening alone:
the chip has two cures, a hands card and a helper's twin, and no `[[order_cards]]` entry, and loads; it reads as a
chore. The plants show the chip and season checks see this fixture: each is the fixture edited, refused by name."""
from pathlib import Path

import pytest

from ashfall_app.engine import CardId, ChipId
from ashfall_app.engine.cure_reading import cures_chip
from ashfall_app.rules.chores import chores
from ashfall_app.rules.expand.convert import build_rules
from ashfall_app.rules.schema import OPENING, Opening, load_opening

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "chorechip.toml"
CHIP = ChipId("t_ashed")

PLANTS = (
    ("a chip with effects and no cost_key", "chip t_ashed: a chip has a cost_key exactly when it has effects",
     (('cost_key = "t_ch_ashed_cost"\n', ""),)),
    ("a chip with effects drawn only after an unlock", "chip t_ashed: has effects and an offered_after",
     (('cost_key = "t_ch_ashed_cost"\n', 'cost_key = "t_ch_ashed_cost"\n'
       'offered_after = { unlock_kind = "card", id = "t_wash" }\n'),)),
    ("a turn opening an action that draws nothing it fills", "t_settle: is opened by the season's turn t_turn",
     (('costs = [{ store = "t_left", items_per_hour = 1 }]\nmakes = [{ store = "t_film"',
       'makes = [{ store = "t_film"'),)),
)


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


def test_a_chore_chip_with_cures_and_no_order_card_loads():
    o = load_with(FIXTURE)
    r = build_rules(o)
    assert not [oc for oc in o.order_cards if oc.chip == CHIP or oc.store == "t_film"]
    assert [c for c in ("t_wash", "t_helper_wash") if cures_chip(r, CardId(c), CHIP)] == ["t_wash", "t_helper_wash"]
    assert CHIP in chores(o, r)


@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p[0])
def test_each_plant_is_refused_with_its_message(tmp_path: Path, plant: tuple[str, str, tuple[tuple[str, str], ...]]):
    _, message, edits = plant
    with pytest.raises(ValueError) as caught:
        load_with(edited(tmp_path, *edits))
    assert str(caught.value).startswith(message)
