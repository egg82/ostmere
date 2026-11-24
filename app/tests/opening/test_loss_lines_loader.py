"""The loader's loss lines (api/CONTRACT.txt, "LOSS LINES"): a fight card's loss_pool, loss_notes, on_loss_key and
loss_after, on fixtures/loss_lines.toml merged onto the opening alone. Each refusal is the fixture edited to break it,
beside the control that loads."""
from pathlib import Path

import pytest

from ashfall_app.opening.entries import UnlockEntry
from ashfall_app.opening.loss_checks import check_loss_order
from ashfall_app.opening.schema import OPENING, Opening, load_opening

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "loss_lines.toml"
TEXT = FIXTURE.read_text()
POOL_FIGHT = 'lost = "t_lost_pool", loss_pool'
FIELDS = ('loss_pool = ["t_l_pool_1", "t_l_pool_2"], loss_notes = ["t_n_pool_1", "t_n_pool_2", "t_n_pool_3"], '
          'on_loss_key = "t_on_loss", loss_after = "t_kept"')
TOWN = '''[[lanes]]
id = "t_helper"
label_key = "t_c_plain"
ruled = true
told = "line"

'''


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = TEXT
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def load(path: Path) -> Opening:
    return load_opening(OPENING, (path,))


def test_the_fixture_loads_with_the_fields_on_the_pooled_card_alone():
    o = load(FIXTURE)
    pool = next(c.fight for c in o.cards if c.id == "t_pool")
    plain = next(c.fight for c in o.cards if c.id == "t_plain")
    assert pool is not None and plain is not None
    assert (pool.loss_pool, pool.loss_notes, pool.on_loss_key, pool.loss_after) == (
        ["t_l_pool_1", "t_l_pool_2"], ["t_n_pool_1", "t_n_pool_2", "t_n_pool_3"], "t_on_loss", "t_kept")
    assert (plain.loss_pool, plain.loss_notes, plain.on_loss_key, plain.loss_after) == (None, None, None, None)


@pytest.mark.parametrize("where,edits", [
    ("action t_raid", (('fights_per_hour = 2,', f'fights_per_hour = 2, {FIELDS},'),)),
    ("card t_pool", (('[[cards]]\nid = "t_pool"', TOWN + '[[cards]]\nid = "t_pool"\nlane = "t_helper"'),
                     ('only_player = "self"\n', ''))),
    ("card t_pool", (('[[cards]]\nid = "t_pool"', TOWN + '[[cards]]\nid = "t_twin"\nlane = "t_helper"\n'
                      'presentation = "action"\nlabel_key = "t_c_pool"\nwork_s = 60\ntwin_of = "t_pool"\n\n'
                      '[[cards]]\nid = "t_pool"'),)),
    ("card t_pool", (('only_player = "self"', 'only_player = "fight"'),)),
    ("card t_pool", (('only_player = "self"\n', ''),)),
    ("card t_pool", ((', loss_after = "t_kept"', ''),)),
    ("card t_pool", ((POOL_FIGHT, 'lost = "t_lost_pool", wounds = [{ store = "stones", items = 1 }], loss_pool'),)),
    ("card t_pool", ((POOL_FIGHT, 'lost = "t_lost_pool", loses = [{ store = "stones", items = 1 }], loss_pool'),)),
    ("card t_pool", ((POOL_FIGHT, 'lost = "t_lost_pool", lost_line_keys = ["t_l_plain_1"], loss_pool'),)),
    ("card t_pool", (('"t_n_pool_2", "t_n_pool_3"]', '"t_n_pool_2", "t_n_pool_2"]'),)),
    ("card t_pool", (('loss_pool = ["t_l_pool_1", "t_l_pool_2"]', 'loss_pool = []'),)),
    ("card t_pool", (('loss_after = "t_kept"', 'loss_after = "t_nothing"'),)),
    ("card t_pool", (('{ unlock_kind = "action", id = "t_raid" }] }',
                      '{ unlock_kind = "action", id = "t_raid" }, { unlock_kind = "card", id = "t_pool" }] }'),)),
    ("card t_pool", (('on_loss_key = "t_on_loss"', 'on_loss_key = "t_no_text"'),)),
    ("line t_l_pool_2", (('t_l_pool_2 = "fight"\n', ''),)),
], ids=["standing", "town lane", "town twin", "only_player fight", "only_player absent", "three of four", "wound",
        "loses", "lost_line_keys", "note twice", "empty pool", "no feature", "opened early", "key not in text",
        "pool line kind"])
def test_a_planted_refusal_fails_naming_the_id(tmp_path: Path, where: str, edits: tuple[tuple[str, str], ...]):
    with pytest.raises(ValueError, match=f"^{where}: "):
        load(edited(tmp_path, *edits))


def test_a_pooled_card_in_the_start_is_refused():
    o = load(FIXTURE)
    check_loss_order(o)
    started = o.model_copy(update={"start": [*o.start, UnlockEntry(unlock_kind="card", id="t_pool")]})
    with pytest.raises(ValueError, match="^card t_pool: "):
        check_loss_order(started)
