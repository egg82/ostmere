"""The journal's subjects as the loader checks them (rules/checks/world/subject_checks.py; docs/design/journal.md, "The content's
side"), on fixtures/subjects.toml merged onto the opening alone. Each refusal is the fixture edited to break it, beside
the control that loads; each names its ids and fields, never text."""
from pathlib import Path

import pytest

from ashfall_app.rules.schema import CHAPTERS, IN_WRITING, OPENING, Opening, load_opening
from ashfall_app.rules.checks.world.subject_checks import AWAITING_SLOTS, CATCHUP_KINDS, check_subjects

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "subjects.toml"
STORM_FIRST = 'first = { keys = ["t_day_storm"] }\n'
DIG_PAIR = 'misremember = { keys = ["t_j_dig_wrong"] }\ncorrection = { keys = ["t_j_dig_right"] }\n'
PAIR = DIG_PAIR.replace("t_j_dig_wrong", "t_j_storm").replace("t_j_dig_right", "t_j_storm")


def subject(sid: str) -> str:
    return f'id = "{sid}"\n'


PLANTS = (
    ("a subject with no first slot", "subject t_s_hunger: has no first slot",
     (('first = { keys = ["t_j_hungry"] }\n', ''),)),
    ("a beat with no catchup", "subject t_s_storm: is a beat and has no catchup slot",
     (('catchup = { keys = ["t_j_storm"] }\n', ''),)),
    ("a person with no catchup", "subject t_s_q1_went: is a person and has no catchup slot",
     (('catchup = { keys = ["t_j_q1_went"] }\n', ''),)),
    ("a routine with no catchup", "subject t_s_dig: is a routine and has no catchup slot",
     (('catchup = { keys = ["t_j_dig_short"] }\n', ''),)),
    ("a crowd with no mention bands", "subject t_s_came: is a crowd and has no mention bands",
     (('mention = [{ at_least = 1, keys = ["t_j_came_one"] }, { at_least = 2, keys = ["t_j_came_some"] }]\n', ''),)),
    ("a crowd's bands not starting at one", "subject t_s_came mention: bands start at one person and rise",
     (('{ at_least = 1, keys = ["t_j_came_one"] }', '{ at_least = 3, keys = ["t_j_came_one"] }'),)),
    ("a misremembering with no correction", "subject t_s_dig: has one of misremember and correction",
     (('correction = { keys = ["t_j_dig_right"] }\n', ''),)),
    ("a correction with no misremembering", "subject t_s_dig: has one of misremember and correction",
     (('misremember = { keys = ["t_j_dig_wrong"] }\n', ''),)),
    ("a beat misremembered", "subject t_s_storm: is a beat, and only a routine is misremembered",
     ((STORM_FIRST, STORM_FIRST + PAIR),)),
    ("a person misremembered", "subject t_s_q1_came: is a person, and only a routine is misremembered",
     (('first = { keys = ["t_j_q1_came"] }\n', 'first = { keys = ["t_j_q1_came"] }\n' + PAIR),)),
    ("a worry misremembered", "subject t_s_hunger: is a worry, and only a routine is misremembered",
     (('first = { keys = ["t_j_hungry"] }\n', 'first = { keys = ["t_j_hungry"] }\n' + PAIR),)),
    ("a source that is no trigger", "subject t_s_hunger: its source, trigger t_nowhere, is not a cause",
     (('id = "t_hunger" }', 'id = "t_nowhere" }'),)),
    ("a trigger source that writes no line", "subject t_s_hunger: its source, trigger t_quiet, is not a cause",
     (('id = "t_hunger" }', 'id = "t_quiet" }'),)),
    ("a card source that writes no line", "subject t_s_dig: its source, card t_rest, is not a cause",
     (('id = "t_dig" }', 'id = "t_rest" }'),)),
    ("a person subject for a mention person", "subject t_s_q1_came: its source, lane t_q2 joined, is not a cause",
     (('id = "t_q1", way = "joined"', 'id = "t_q2", way = "joined"'),)),
    ("a crowd for a way no mention person moves", "subject t_s_came: its source, mentions left, is not a cause",
     (('source_kind = "mentions", way = "joined"', 'source_kind = "mentions", way = "left"'),)),
    ("a trigger source with a way", "subject t_s_storm: a trigger source names an id",
     (('id = "t_storm" }', 'id = "t_storm", way = "joined" }'),)),
    ("a lane source with no way", "subject t_s_q1_came: a lane source names an id and a way",
     (('id = "t_q1", way = "joined" }', 'id = "t_q1" }'),)),
    ("a mentions source with an id", "subject t_s_came: a mentions source names a way and no id",
     (('source_kind = "mentions", way', 'source_kind = "mentions", id = "t_q2", way'),)),
    ("a beat fed by a lane", "subject t_s_storm: only a person feeds from a lane's coming or going",
     (('kind = "beat"\nsource = { source_kind = "trigger", id = "t_storm" }',
       'kind = "beat"\nsource = { source_kind = "lane", id = "t_q1", way = "joined" }'),)),
    ("a crowd fed by a trigger", "subject t_s_came: only a person feeds from a lane's coming or going",
     (('source_kind = "mentions", way = "joined"', 'source_kind = "trigger", id = "t_hunger"'),)),
    ("two subjects fed by one cause", "subject t_s_hunger: feeds from trigger t_storm, as subject t_s_storm does",
     (('id = "t_hunger" }', 'id = "t_storm" }'),)),
    ("a line person's leaving with no person subject",
     "trigger t_q1_goes: left t_q1, a line person, and no person subject feeds from it",
     (('[[subjects]]\nid = "t_s_q1_went"\nkind = "person"\n'
       'source = { source_kind = "lane", id = "t_q1", way = "left" }\n'
       'first = { keys = ["t_j_q1_went"] }\ncatchup = { keys = ["t_j_q1_went"] }\n', ''),)),
    ("a first key with no text", "subject t_s_hunger: first key 't_j_nowhere' is not in text",
     (('keys = ["t_j_hungry"]', 'keys = ["t_j_nowhere"]'),)),
    ("a repeat key with no text", "subject t_s_dig: repeat key 't_j_nowhere' is not in text",
     (('"t_j_dig_more"', '"t_j_nowhere"'),)),
    ("a late key with no text", "subject t_s_dig: late key 't_j_nowhere' is not in text",
     (('keys = ["t_j_dig_late"]', 'keys = ["t_j_nowhere"]'),)),
    ("a correction key with no text", "subject t_s_dig: correction key 't_j_nowhere' is not in text",
     (('keys = ["t_j_dig_right"]', 'keys = ["t_j_nowhere"]'),)),
    ("a mention key with no text", "subject t_s_came mention: key 't_j_nowhere' is not in text",
     (('keys = ["t_j_came_some"]', 'keys = ["t_j_nowhere"]'),)),
    ("a slot sketch that is a path", "subject t_s_dig first: sketch 'a/b'",
     (('sketch = "t_spade"', 'sketch = "a/b"'),)),
    ("two subjects with one id", "subject: duplicate id t_s_storm",
     ((subject("t_s_hunger"), subject("t_s_storm")),)),
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


def test_the_control_loads_one_subject_of_each_kind():
    o = load_with(FIXTURE)
    kinds = {s.id: s.kind for s in o.subjects if s.id.startswith("t_s_")}
    assert sorted(kinds.values()) == ["beat", "crowd", "person", "person", "routine", "worry"]
    assert not AWAITING_SLOTS & set(kinds)


@pytest.mark.parametrize("edits,named", [(e, n) for _, n, e in PLANTS], ids=[d for d, _, _ in PLANTS])
def test_each_planted_fault_fails_the_load_naming_its_ids(tmp_path: Path, edits: tuple[tuple[str, str], ...], named: str):
    with pytest.raises(ValueError) as e:
        load_with(edited(tmp_path, *edits))
    assert named in str(e.value), str(e.value)


def awaiting_faults(o: Opening, held: frozenset[str]) -> list[str]:
    """Where the held set and the subjects still missing a first or catch-up slot differ: each held subject that has
    both now (stale) or is gone, and each one missing a slot that is not held."""
    missing = {s.id for s in o.subjects if s.first is None or (s.kind in CATCHUP_KINDS and s.catchup is None)}
    return sorted([f"stale: {i}" for i in held - missing] + [f"not held: {i}" for i in missing - held])


def test_the_subjects_awaiting_their_slots_are_exactly_those_still_missing_one():
    o = load_opening(OPENING, CHAPTERS + IN_WRITING)
    assert o.subjects, "the shipped content declares subjects"
    assert awaiting_faults(o, AWAITING_SLOTS) == []


def test_a_held_subject_with_its_slots_reads_stale_and_one_missing_a_slot_reads_not_held():
    o = load_with(FIXTURE)
    storm = next(s for s in o.subjects if s.id == "t_s_storm")
    missing = storm.model_copy(update={"id": "t_s_bare", "catchup": None})
    bare = o.model_copy(update={"subjects": [*o.subjects, missing]})
    assert awaiting_faults(bare, frozenset({"t_s_bare", "t_s_storm"})) == ["stale: t_s_storm"]
    assert awaiting_faults(bare, frozenset()) == ["not held: t_s_bare"]


def test_a_subject_sourced_from_a_fight_only_card_is_refused_and_a_card_with_its_own_line_is_not():
    o = load_opening(OPENING, CHAPTERS + IN_WRITING)
    hunt = next(c for c in o.cards if c.fight is not None and not (c.line_keys or c.outcome.line_keys
                                                                    or c.finished.line_keys))
    assert hunt.fight is not None and (hunt.fight.won_line_keys or hunt.fight.lost_line_keys)
    base = next(s for s in o.subjects if s.source.source_kind == "card")
    fed = base.model_copy(update={"id": "t_s_hunt", "source": base.source.model_copy(update={"id": hunt.id})})
    with pytest.raises(ValueError, match=f"subject t_s_hunt: its source, card {hunt.id}, is not a cause the content writes a kept line"):
        check_subjects(o.model_copy(update={"subjects": [*o.subjects, fed]}))
    own = hunt.model_copy(update={"outcome": hunt.outcome.model_copy(update={"line_keys": [*base_keys(o)]})})
    cards = [own if c.id == hunt.id else c for c in o.cards]
    check_subjects(o.model_copy(update={"subjects": [*o.subjects, fed], "cards": cards}))


def base_keys(o: Opening) -> list[str]:
    return [next(iter(o.text))]
