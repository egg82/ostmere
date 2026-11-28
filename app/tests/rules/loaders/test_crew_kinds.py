"""Crews take town cards by kind (rules/expand/town.py `kinds`, rules/groups.py check_crew_work), on
fixtures/crew_kinds.toml merged onto the opening alone. Each refusal is the fixture edited, beside the control that loads."""
from pathlib import Path

import pytest

from ashfall_app.rules.schema import OPENING, Opening, load_opening

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "crew_kinds.toml"
PLANTS = (
    ("a crew listed in a card's lanes", "town card {lane}_a: lists crews t_crew in lanes",
     (('lanes = ["t_m2"]\nkinds = ["t_k"]', 'lanes = ["t_m2", "t_crew"]\nkinds = ["t_k"]'),)),
    ("a card a crew member does, with no kinds", "town card {lane}_c: is done by a crew member and has no `kinds`",
     (('kinds = ["t_other"]\npresentation', 'presentation'),)),
    ("a kind on a person", "lane t_m2: kind is only on a pooled lane",
     (('id = "t_m2"\nlabel_key = "t_l_m2"\nruled = true\n', 'id = "t_m2"\nlabel_key = "t_l_m2"\nruled = true\nkind = "t_k"\n'),)),
)


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return path


def card_ids(o: Opening) -> set[str]:
    return {c.id for c in o.cards}


def test_a_crew_takes_every_card_of_its_kind():
    ids = card_ids(load_opening(OPENING, (FIXTURE,)))
    assert {"t_crew_a", "t_crew_b"} <= ids
    assert "t_crew_c" not in ids and "t_crew_d" not in ids


def test_a_member_who_cannot_do_a_job_does_not_remove_it_from_the_crew():
    """t_m1 is the crew's one member and cannot do t_a (it is not on t_a's lanes); the crew still holds it."""
    o = load_opening(OPENING, (FIXTURE,))
    a = next(tc for tc in o.town_cards if tc.id == "{lane}_a")
    assert "t_m1" not in a.lanes and "t_crew_a" in card_ids(o) and "t_m1_a" not in card_ids(o)


@pytest.mark.parametrize(("message", "edits"), [(m, e) for _, m, e in PLANTS], ids=[n for n, _, _ in PLANTS])
def test_the_loader_refuses(tmp_path: Path, message: str, edits: tuple[tuple[str, str], ...]):
    with pytest.raises(ValueError, match=message.replace("{", r"\{").replace("}", r"\}")):
        load_opening(OPENING, (edited(tmp_path, *edits),))


def test_a_card_marked_not_crew_work_loads_and_reaches_no_crew(tmp_path: Path):
    """The control for the no-kinds refusal: `kinds = []` loads, and t_d is on its people only."""
    ids = card_ids(load_opening(OPENING, (edited(tmp_path),)))
    assert {"t_m1_d", "t_m2_d"} <= ids and "t_crew_d" not in ids

