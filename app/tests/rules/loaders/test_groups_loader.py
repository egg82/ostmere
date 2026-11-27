"""Groups as authored (rules/groups.py, engine design/groups.txt, "GROUPS (pooled lanes)", "Content"), on
fixtures/groups.toml merged onto the opening alone: a pooled lane, its member's unmarked join, a mark and an unmarking
load into the engine's fields; an unmarked join or unmarking unlocks the group's cards; the loader refuses what it
refuses beside the control that loads. Each refusal is the fixture edited."""
from pathlib import Path

import pytest

from ashfall_app.engine import CardId, LaneId, Mark, UnlockKind
from ashfall_app.rules.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "groups.toml"
CARD_CAP = ('[[cards]]\nid = "t_capped"\npresentation = "action"\nlabel_key = "t_c_work"\nupside_key = "t_up"\nwork_s = 60\ncap = 1\n'
            'outcome = { marks = [{ lane = "t_m1", own_split = true }] }\n\n[line_kinds]')

PLANTS = (
    ("a pooled lane with a name", "lane t_crew: a pooled lane is ruled and has no name_key, group or told",
     (('pooled = true\n', 'pooled = true\nname_key = "t_l_crew"\n'),)),
    ("a pooled lane with a told", "lane t_crew: a pooled lane is ruled and has no name_key, group or told",
     (('pooled = true\n', 'pooled = true\ntold = "line"\n'),)),
    ("a pooled lane that is not ruled", "lane t_crew: a pooled lane is ruled",
     (('ruled = true\npooled = true\n', 'pooled = true\n'),)),
    ("a group naming a lane that is not pooled", "lane t_m1: group t_m2 is not a pooled lane",
     (('group = "t_crew"', 'group = "t_m2"'),)),
    ("a tie on a lane that is not pooled", "lane t_m2: tied is only on a pooled lane",
     (('id = "t_m2"\nlabel_key = "t_l_m2"\nruled = true\n', 'id = "t_m2"\nlabel_key = "t_l_m2"\nruled = true\ntied = "t_m1"\n'),)),
    ("a tie to a lane that is not there", "lane t_crew: tied t_nobody is not a ruled person's lane",
     (('tied = "t_m1"', 'tied = "t_nobody"'),)),
    ("a tie to a pooled lane", "lane t_crew: tied t_crew is not a ruled person's lane",
     (('tied = "t_m1"', 'tied = "t_crew"'),)),
    ("an unmarked join with no group", "trigger t_m2_comes: joins t_m2 without its own split, and the lane has no group",
     (('counted = true, own_split = true', 'counted = true, own_split = false'),)),
    ("an unmarked join with a card off the group",
     "trigger t_m1_comes: joins t_m1 without its own split, and card t_m1_work is not an uncapped card on its group",
     (('card = "t_crew_work", counted', 'card = "t_m1_work", counted'),)),
    ("a join with no own_split", "own_split",
     (('counted = true, own_split = true', 'counted = true'),)),
    ("an unmarking with no group", "trigger t_m1_back: unmarks t_m2, which has no group",
     (('{ lane = "t_m1", own_split = false }', '{ lane = "t_m2", own_split = false }'),)),
    ("a mark of a lane that is not a person", "trigger t_m1_back: unknown person's lane t_crew",
     (('{ lane = "t_m1", own_split = false }', '{ lane = "t_crew", own_split = false }'),)),
    ("a mark in a card's outcome", "card t_capped: only a trigger's or an answer's outcome marks a person",
     (('[line_kinds]', CARD_CAP),)),
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


def test_the_fields_reach_the_engine():
    rules = to_rules(load_with(FIXTURE))
    lanes = {d.id: d for d in rules.lanes}
    assert lanes[LaneId("t_crew")].pooled and lanes[LaneId("t_m1")].group == LaneId("t_crew")
    assert not lanes[LaneId("t_m2")].pooled and lanes[LaneId("t_m2")].group is None
    outcomes = {str(t.id): t.outcome for t in rules.triggers}
    assert [(j.own_split, j.card) for j in outcomes["t_m1_comes"].joins] == [(False, CardId("t_crew_work"))]
    assert [j.own_split for j in outcomes["t_m2_comes"].joins] == [True]
    assert outcomes["t_m1_apart"].marks == (Mark(LaneId("t_m1"), True, CardId("t_m1_work")),)
    assert outcomes["t_m1_back"].marks == (Mark(LaneId("t_m1"), False),)


def test_handing_a_person_to_their_group_unlocks_the_groups_cards_once():
    cards = {str(t.id): [u.id for u in t.outcome.unlocks if u.kind is UnlockKind.CARD]
             for t in to_rules(load_with(FIXTURE)).triggers}
    assert cards["t_m1_comes"] == ["t_m1_work", "t_crew_work"]
    assert cards["t_m1_back"] == ["t_crew_work"]
    assert cards["t_m2_comes"] == ["t_m2_work"] and cards["t_m1_apart"] == []


def test_a_group_card_an_outcome_names_is_left_to_it(tmp_path: Path):
    named = edited(tmp_path, ('outcome = { marks = [{ lane = "t_m1", own_split = true, card = "t_m1_work" }] }',
                              'outcome = { unlocks = [{ unlock_kind = "card", id = "t_crew_work" }], marks = [{ lane = "t_m1", '
                              'own_split = true, card = "t_m1_work" }] }'))
    cards = {str(t.id): [u.id for u in t.outcome.unlocks if u.kind is UnlockKind.CARD]
             for t in to_rules(load_with(named)).triggers}
    assert cards["t_m1_comes"] == ["t_m1_work"] and cards["t_m1_back"] == []
    assert cards["t_m1_apart"] == ["t_crew_work"]


@pytest.mark.parametrize(("message", "edits"), [(m, e) for _, m, e in PLANTS], ids=[n for n, _, _ in PLANTS])
def test_the_loader_refuses(tmp_path: Path, message: str, edits: tuple[tuple[str, str], ...]):
    with pytest.raises(ValueError, match=message):
        load_with(edited(tmp_path, *edits))
