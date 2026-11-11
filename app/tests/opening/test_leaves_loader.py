"""People leaving as content (engine DESIGN.txt, "LEAVES", "Content"), on fixtures/leaves.toml merged onto the opening
alone: the first person leaves with the standing action they brought, and the loader refuses a leave anywhere but a
trigger's or an answer's outcome, of a lane that is not ruled, twice, beside a join of the same lane, or stopping
something that is not a standing action. Each refusal is the fixture edited, beside the control that loads."""
from pathlib import Path

import pytest

from ashfall_app.engine import LaneId, Unlock, UnlockKind, advance, new_save, view
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "leaves.toml"
LEAVES = 'leaves = [{ lane = "t_p1", stops = ["t_tend"] }]'

PLANTS = (
    ("a lane that is not ruled", "trigger t_depart: leaves hands, which is not a ruled lane",
     ((LEAVES, 'leaves = [{ lane = "hands" }]'),)),
    ("a lane left twice", "trigger t_depart: leaves t_p1, which another outcome already leaves",
     ((LEAVES, 'leaves = [{ lane = "t_p1", stops = ["t_tend"] }, { lane = "t_p1" }]'),)),
    ("a lane joined by the outcome that leaves it", "trigger t_depart: joins t_p2 in the outcome that leaves it",
     ((LEAVES, 'leaves = [{ lane = "t_p2" }], joins = [{ lane = "t_p2", mix = "town:main" }]'),)),
    ("a stop that is not a standing action", "trigger t_depart: leaves t_p1, stopping t_p1_work, which is not a "
     "standing action", ((LEAVES, 'leaves = [{ lane = "t_p1", stops = ["t_p1_work"] }]'),)),
    ("a card's outcome", "card t_once: only a trigger's or an answer's outcome has a person leave",
     (('[[triggers]]\nid = "t_arrive"', '[[cards]]\nid = "t_once"\nlane = "t_p2"\npresentation = "action"\n'
       'label_key = "t_c_work"\nwork_s = 60\ncap = 1\noutcome = { leaves = [{ lane = "t_p2" }] }\n\n'
       '[[triggers]]\nid = "t_arrive"'),)),
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


def test_the_first_person_leaves_with_the_standing_action_they_brought():
    r = to_rules(load_with(FIXTURE))
    s = advance(new_save(r), r, 5000)
    assert Unlock(UnlockKind.LEFT, LaneId("t_p1")) in s.unlocked
    v = view(s, r)
    assert "t_p1" not in [b.lane for b in v.lanes] and "t_p2" in [b.lane for b in v.lanes]
    assert "t_tend" not in [b.action for b in v.standing]
    assert "t_tend" in [b.action for b in view(advance(new_save(r), r, 4999), r).standing]


@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p[0])
def test_each_plant_is_refused_with_its_message(tmp_path: Path, plant: tuple[str, str, tuple[tuple[str, str], ...]]):
    _, message, edits = plant
    with pytest.raises(ValueError) as caught:
        load_with(edited(tmp_path, *edits))
    assert str(caught.value).startswith(message)
