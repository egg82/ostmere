"""`[journal_habits]` loaded and range checked (opening/setting_entries.py; docs/design/journal.md, "The habits as
data"): each refusal is the shipped opening's table edited, beside the unedited control that loads."""
from pathlib import Path

import pytest

from ashfall_app.opening.schema import OPENING, load_opening

TABLE = "[journal_habits]\n"

PLANTS = (
    ("a fade that never fades", ("routine = { base = 0.8, fade = 0.5 }", "routine = { base = 0.8, fade = 1 }"),
     "journal_habits.routine.fade"),
    ("a base over one", ("crowd = { base = 0.5,", "crowd = { base = 1.5,"), "journal_habits.crowd.base"),
    ("a worry that presses by nothing", ("press = 0.3", "press = 0"), "journal_habits.worry.press"),
    ("a floor of one", ("floor = 0.15", "floor = 1"), "journal_habits.floor"),
    ("a halflife of nothing", ("\nhalflife = 12", "\nhalflife = 0"), "journal_habits.halflife"),
    ("a rate over one", ("late_rate = 0.15", "late_rate = 1.5"), "journal_habits.late_rate"),
    ("a correction the same day", ("correct_after_days = 2", "correct_after_days = 0"), "journal_habits.correct_after_days"),
    ("a busy day under its budget", ("busy_ratio = 2", "busy_ratio = 0.5"), "journal_habits.busy_ratio"),
    ("a budget that grows", ("lines_floor = 1", "lines_floor = 9"), "lines_floor is over lines_start"),
    ("a knob that is not one", (TABLE, TABLE + "stamina = 3\n"), "journal_habits.stamina"),
)


def edited(tmp_path: Path, old: str, new: str) -> Path:
    text = OPENING.read_text()
    assert text.count(old) == 1, f"anchor is not unique: {old!r}"
    path = tmp_path / OPENING.name
    path.write_text(text.replace(old, new))
    return path


def test_the_shipped_table_loads():
    h = load_opening(OPENING, ()).journal_habits
    assert h.lines_floor <= h.lines_start and 0 < h.routine.fade < 1


@pytest.mark.parametrize("edit,named", [(e, n) for _, e, n in PLANTS], ids=[d for d, _, _ in PLANTS])
def test_each_planted_value_out_of_range_fails_the_load_naming_its_field(tmp_path: Path, edit: tuple[str, str], named: str):
    with pytest.raises(ValueError) as e:
        load_opening(edited(tmp_path, *edit), ())
    assert named in str(e.value), str(e.value)


def test_an_opening_without_the_table_fails_the_load(tmp_path: Path):
    text = OPENING.read_text()
    start = text.index(TABLE)
    end = text.index("\n\n", start)
    path = tmp_path / OPENING.name
    path.write_text(text[:start] + text[end:])
    with pytest.raises(ValueError, match="journal_habits"):
        load_opening(path, ())
