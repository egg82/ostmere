"""The pure parts of a write and a Ruleset: a rebase's lines numbered before a step's, and text keys renamed through
every later rename."""
from ashfall_app import engine as e
from ashfall_app.opening.renames import RenameEntry
from ashfall_app.saves.ruleset import line_renames, retired_lines
from ashfall_app.saves.write import numbered


def line(time: int, seq: int, key: str) -> e.Line:
    return e.Line(time, seq, e.LineKey(key))


def test_a_steps_lines_number_on_after_the_rebases_at_the_same_instant():
    first = (line(5, 0, "r0"), line(5, 1, "r1"))
    then = (line(5, 0, "s0"), line(5, 1, "s1"), line(9, 0, "s2"))
    got = numbered(first, then)
    assert [(ln.time, ln.seq, ln.key) for ln in got] == [
        (5, 0, "r0"), (5, 1, "r1"), (5, 2, "s0"), (5, 3, "s1"), (9, 0, "s2")]
    assert numbered((), then) == then and numbered(first, ()) == first


def entry(kind: str, old: str, new: str | None) -> RenameEntry:
    return RenameEntry.model_validate({"kind": kind, "from": old} | ({} if new is None else {"to": new}))


def test_a_text_key_is_renamed_through_every_later_rename():
    renames = [entry("line", "a", "b"), entry("line", "b", "c"), entry("card", "x", "y"), entry("line", "p", "q")]
    assert line_renames(renames) == {"a": "c", "b": "c", "p": "q"}
    assert line_renames([entry("line", "a", "b"), entry("line", "b", "a")]) == {"a": "a", "b": "b"}   # a cycle ends


def test_a_retired_line_is_retired_and_renames_nothing():
    renames = [entry("line", "a", "b"), entry("line", "gone", None), entry("card", "x", "y")]
    assert retired_lines(renames) == {"gone"} and line_renames(renames) == {"a": "b"}
