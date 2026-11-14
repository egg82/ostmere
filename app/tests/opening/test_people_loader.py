"""How people's coming and going is written (opening/people.py, people_checks.py), on fixtures/people.toml merged onto
the opening alone: a `line` person's joining writes the story line its outcome authors; two `mention` people joining
together, and one of them leaving, each write a mention line with no text, at the second it happened, served with the
lane and the way. The loader refuses a person with no `told`, `told` on a lane that is not a person, a `line` person
joined or left by an outcome with no story line of its own (none at all, or only a find), a mention with no bands to
word it, and bands that leave a count without one. Each refusal is the fixture edited, beside the control that loads."""
from pathlib import Path

import pytest

from ashfall_app.api.line_causes import line_infos
from ashfall_app.api.line_models import Mention
from ashfall_app.engine import advance_logged, new_save
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "people.toml"
COMES = 'outcome = { line_keys = ["t_l_comes"], unlocks'
NO_LINE = 'outcome = { unlocks'

PLANTS = (
    ("a person with no told", "lane t_q1: is a person with no `told`",
     (('ruled = true\ntold = "line"\n', 'ruled = true\n'),)),
    ("told on a lane that is not a person", "lane t_post: is told but is not a ruled lane",
     (('label_key = "t_l_post"\n', 'label_key = "t_l_post"\ntold = "line"\n'),)),
    ("a line person's joining with no line", "trigger t_q1_comes: joined t_q1, a line person, and writes no story line",
     ((COMES, NO_LINE),)),
    ("a line person's joining with only a find", "trigger t_q1_comes: joined t_q1, a line person, and writes no story line",
     (('t_l_comes = "story"', 't_l_comes = "find"'),)),
    ("a line person's leaving with no line", "trigger t_q3_goes: left t_q3, a line person, and writes no story line",
     (('label_key = "t_l_q3"\nruled = true\ntold = "mention"', 'label_key = "t_l_q3"\nruled = true\ntold = "line"'),
      ('card = "t_q3_work" }] }', 'card = "t_q3_work", counted = true }] }'))),
    ("a mention with no bands", "lane t_q2: is a mention, and the content has no [people] bands to word it",
     (('[[people.came]]\nat_least = 1\nkeys = ["t_came_one"]\n\n[[people.came]]\nat_least = 2\n'
       'keys = ["t_came_some_a", "t_came_some_b"]\n\n[[people.went]]\nat_least = 1\nkeys = ["t_went_one"]\n', ''),)),
    ("bands not starting at one", "people came: bands start at one person and rise",
     (('at_least = 1\nkeys = ["t_came_one"]', 'at_least = 3\nkeys = ["t_came_one"]'),)),
    ("a band key with no text", "people went: key 't_went_none' is not in text",
     (('keys = ["t_went_one"]', 'keys = ["t_went_none"]'),)),
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


def test_a_mention_persons_moves_write_a_mention_line_each_and_a_line_persons_writes_its_own():
    o = load_with(FIXTURE)
    outcome = {t.id: t.outcome for t in o.triggers}
    assert outcome["t_q1_comes"].line_keys == ["t_l_comes"]
    assert outcome["t_pair_comes"].line_keys == ["people.joined.t_q2", "people.joined.t_q3"]
    assert outcome["t_q3_goes"].line_keys == ["people.left.t_q3"]
    assert {o.line_kinds[k] for k in ("people.joined.t_q2", "people.left.t_q3")} == {"story"}
    assert o.text["people.joined.t_q2"] == ""


def test_the_mention_lines_land_in_the_log_at_the_second_of_the_move():
    r = to_rules(load_with(FIXTURE))
    lines = [(x.time, str(x.key)) for x in advance_logged(new_save(r), r, 6000).lines if str(x.key).startswith(("people.", "t_l_"))]
    assert lines == [(100, "t_l_comes"), (200, "people.joined.t_q2"), (200, "people.joined.t_q3"), (5000, "people.left.t_q3")]


def test_the_served_lines_say_which_tell_a_person_and_which_are_mentions():
    infos = {i.key: i for i in line_infos(load_with(FIXTURE))}
    assert infos["t_l_comes"].person and infos["t_l_comes"].mention is None
    assert infos["people.joined.t_q3"].mention == Mention(lane="t_q3", way="joined") and not infos["people.joined.t_q3"].person
    assert infos["people.left.t_q3"].mention == Mention(lane="t_q3", way="left")
    assert not any(i.person or i.mention for k, i in infos.items() if not k.startswith(("t_l_", "people.")))


def test_a_counted_join_needs_no_line_of_its_own(tmp_path: Path):
    """The person came earlier and was told then: the join only moves them into the town's mix."""
    load_with(edited(tmp_path, (COMES, NO_LINE), ('card = "t_q1_work" }] }', 'card = "t_q1_work", counted = true }] }')))


@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p[0])
def test_each_plant_is_refused_with_its_message(tmp_path: Path, plant: tuple[str, str, tuple[tuple[str, str], ...]]):
    _, message, edits = plant
    with pytest.raises(ValueError) as caught:
        load_with(edited(tmp_path, *edits))
    assert str(caught.value).startswith(message)
