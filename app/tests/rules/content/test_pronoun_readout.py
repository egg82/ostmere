"""The pronouns readout (tests/rules/play/pronouns_readout.py) flags a line whose he/she has no one in the line to point
at, and none whose line holds a person's slot, a name or a word for a person; it reports and fails nothing."""
from ashfall_app.rules.schema import Opening
from tests import readout_snapshot as rs
from tests.rules.play import pronouns_readout as readout


def with_lines(o: Opening, lines: dict[str, str]) -> Opening:
    kind = next(iter(o.line_kinds.values()))
    return o.model_copy(update={"text": {**o.text, **lines}, "line_kinds": {**o.line_kinds, **{k: kind for k in lines}}})


def test_the_committed_readout_is_the_one_it_writes():
    assert rs.stray("pronouns", readout.NAMES) == ([], [])


def test_the_pronouns_readout_is_reported():
    rs.check("pronouns", readout.readouts()["pronouns"])


def test_a_pronoun_with_no_one_in_its_line_is_flagged_and_one_with_someone_is_not(shipped_opening: Opening):
    lane = next(x for x in shipped_opening.lanes if x.name_key)
    name = shipped_opening.text[lane.name_key or ""]
    o = with_lines(shipped_opening, {
        "zz_alone": "by dark he is not back.",
        "zz_slot": f"{{{lane.id}}} ties a cloth to every stake she set.",
        "zz_name": f"{name.lower()} looks up. she says nothing.",
        "zz_word": "the man sits. he says nothing.",
        "zz_none": "the fire burns down.",
    })
    flagged = dict(readout.unanchored(o))
    assert flagged.get("zz_alone") == ["he"]
    assert not {"zz_slot", "zz_name", "zz_word", "zz_none"} & set(flagged)
    assert "zz_alone" in readout.render(o)
