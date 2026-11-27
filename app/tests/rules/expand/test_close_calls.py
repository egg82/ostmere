"""Close calls (rules/entries/close_call_entries.py): the loader refuses a close call whose person is no notable, whose outcome
or change is unknown, never one for how many there are; the readout (close_calls_readout.py) lists each notable's by
id with its days and its change, and says so when no content has one. Planted on the shipped content, which has none."""
from typing import Any

import pytest

from ashfall_app.rules.entries.close_call_entries import CloseCallEntry
from ashfall_app.rules.checks.run import check_structure
from ashfall_app.rules.schema import Opening
from tests import readout_snapshot as rs
from tests.daytwo.abs_band import Pace, load_pace
from tests.rules.play import close_calls_readout as readout

PACE = Pace(scale=2.0, targets={"B5": 5, "B9": 9})


def person_of(o: Opening) -> str:
    return next(x.id for x in o.lanes if x.ruled and not x.pooled and not x.station)


def planted(o: Opening, calls: list[CloseCallEntry]) -> Opening:
    """`o` with its first person a notable and `calls` its close calls."""
    lanes = [x.model_copy(update={"notable": x.id == person_of(o)}) for x in o.lanes]
    return o.model_copy(update={"lanes": lanes, "close_calls": calls})


def call(o: Opening, **kw: Any) -> CloseCallEntry:
    base: dict[str, Any] = {"id": "cc1", "person": person_of(o), "beat": "B5", "at": o.triggers[0].id, "change": o.triggers[1].id}
    return CloseCallEntry(**{**base, **kw})


def test_the_shipped_content_marks_no_close_call_and_the_readout_says_so(shipped_opening: Opening):
    assert not shipped_opening.close_calls
    assert readout.NONE_MARKED in readout.render(planted(shipped_opening, []), PACE)
    assert "no notable is marked yet" == readout.render(shipped_opening, PACE)


def test_the_committed_readouts_are_the_ones_the_close_calls_write():
    assert rs.stray("closecalls", readout.NAMES) == ([], [])


def test_the_close_calls_readout_is_reported(shipped_opening: Opening):
    rs.check("closecalls", readout.render(shipped_opening, load_pace()))


def test_a_well_formed_close_call_loads_with_any_count(shipped_opening: Opening):
    calls = [call(shipped_opening, id=f"cc{i}") for i in range(7)]
    check_structure(planted(shipped_opening, calls))


@pytest.mark.parametrize("what,update,message", [
    ("a person who is not a notable", {"person": "not_a_lane"}, "is not a notable's lane"),
    ("an unknown outcome", {"at": "no_such_outcome"}, "at no_such_outcome is not a trigger or an answer"),
    ("an unknown change", {"change": "no_such_change"}, "change no_such_change is not a trigger, an answer or a text key"),
])
def test_the_loader_refuses(shipped_opening: Opening, what: str, update: dict[str, str], message: str):
    with pytest.raises(ValueError, match=message):
        check_structure(planted(shipped_opening, [call(shipped_opening, **update)]))


def test_a_notable_that_is_not_a_person_is_refused(shipped_opening: Opening):
    station = next(x for x in shipped_opening.lanes if x.station)
    lanes = [x.model_copy(update={"notable": True}) if x.id == station.id else x for x in shipped_opening.lanes]
    with pytest.raises(ValueError, match="is notable but is not a person"):
        check_structure(shipped_opening.model_copy(update={"lanes": lanes}))


def test_the_readout_lists_each_close_call_with_its_days_and_its_change(shipped_opening: Opening):
    person = call(shipped_opening).person
    calls = [call(shipped_opening, id="late", beat="B9", change=None), call(shipped_opening, id="early"),
             call(shipped_opening, id="odd", beat="B2")]
    text = readout.render(planted(shipped_opening, calls), PACE)
    rows = text.splitlines()
    assert rows[1] == f"{person}: 3 close calls"
    assert rows[2].split() == ["odd", "B2", "unknown", "unknown", "-", shipped_opening.triggers[1].id]
    assert rows[3].split() == ["early", "B5", "5", "10", "-", shipped_opening.triggers[1].id]
    assert rows[4].split() == ["late", "B9", "9", "18", "8", "NO", "CHANGE"]
