"""The saved ends week two's chapters play on from (ends.py) are today's: where a chapter's directory is present, it holds
every end the chain needs of that chapter and nothing else; each chapter played on from the saved end before it ends where its own saved end says
(week one's ends are checked against week one's play in `playthrough-week-one-saved`, tests/weekone_saved); each saved
rebased save was written from today's play and code. A stale end fails, naming the command that rewrites them; the
controls show the comparisons see a changed play."""
import copy
from pathlib import Path

import pytest

from tools import chapter_saves
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weektwo import ends, keys, rebased
from tests.weektwo.routes import CHAPTERS, SAVED, laters, saved_end

CHECKED = [(chapter, name) for chapter, names in SAVED.items() if chapter != "week1" for name in names]


def wanted(chapter: str) -> set[Path]:
    """Every file `chapter`'s directory holds: one reading to a file, numbered from its first heavy step with no gap."""
    found = {ends.player_path(chapter, n) for n in SAVED.get(chapter, ())} | {ends.manifest(chapter)}
    found |= {ends.rebased_path(c) for c in rebased.OLD if c == chapter}
    found |= {ends.readings_path(chapter, i) for i in range(len(ends.saved_readings(chapter)))}
    return found


@pytest.mark.playthrough
def test_the_saved_ends_are_every_end_the_chain_needs():
    assert sum(len(wanted(c)) for c in keys.ORDER) > len(SAVED)
    for chapter in keys.ORDER:
        if ends.available(chapter):
            assert set(ends.golden(chapter).iterdir()) == wanted(chapter), (chapter, ends.REWRITE)


def test_every_saved_file_is_written_by_a_part():
    """chapter_saves --write PART writes each file; a file in no part would exist only in a full local write."""
    in_parts = [c for chapters in chapter_saves.REBASED.values() for c in chapters]
    assert sorted(in_parts) == sorted(rebased.OLD), "each rebased save in exactly one part"
    assert {n for names in SAVED.values() for n in names} <= chapter_saves.ROUTES | chapter_saves.LINKED
    assert set(chapter_saves.READINGS) <= chapter_saves.ALL and set(chapter_saves.REBASED) <= chapter_saves.ALL
    assert {c for c in rebased.OLD} <= {c for c, names in SAVED.items() if "typical" in names}, \
        "a rebased part reads typical's saved end at its chapter"


def test_a_linked_routes_links_write_each_of_its_saved_ends_once_in_order():
    """The links run from the route's first saved end with no gap and the last open, so a chapter added to SAVED is
    written by the last link; each link after the first reads the end the link before wrote last."""
    assert chapter_saves.LINKED and not chapter_saves.LINKED & chapter_saves.ROUTES
    for route in chapter_saves.LINKED:
        links = [link for link in chapter_saves.LINKS.values() if link.route == route]
        written = [c for link in links for c in chapter_saves.link_chapters(link.part)]
        assert written == [c for c, names in SAVED.items() if route in names], route
        assert [link.after for link in links] == ["", *(link.part for link in links[:-1])], route


def test_each_chapters_readings_run_from_its_first_heavy_step_with_no_gap_and_the_last_open():
    spans: dict[str, list[tuple[int, int | None]]] = {}
    for part in chapter_saves.READINGS.values():
        for chapter, first, after in part:
            spans.setdefault(chapter, []).append((first, after))
    assert set(spans) == set(CHAPTERS)
    for chapter, found in spans.items():
        found.sort()
        assert found[0][0] == 0 and found[-1][1] is None, chapter
        assert all(after == nxt for (_, after), (nxt, _) in zip(found, found[1:])), (chapter, found)


def test_missing_saves_are_not_used_and_under_the_require_variable_fail(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ASHFALL_SAVES_ROOT", str(tmp_path))
    monkeypatch.delenv(ends.REQUIRE, raising=False)
    assert not ends.available("eight")
    monkeypatch.setenv(ends.REQUIRE, "1")
    with pytest.raises(AssertionError, match="no saved ends for eight"):
        ends.available("eight")


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
@pytest.mark.parametrize("chapter_end", CHECKED, indirect=True, ids=[f"{c}-{n}" for c, n in CHECKED])
def test_a_chapter_played_on_from_the_saved_end_before_it_ends_at_its_own(
        chapter_end: tuple[str, DayTwoPlayer, DayTwoPlayer]):
    label, p, saved = chapter_end
    assert ends.differs(p, saved) == [], f"the saved end of {label} is stale: {ends.REWRITE}"


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
@pytest.mark.parametrize("rebased_inputs", list(rebased.OLD), indirect=True)
def test_a_saved_rebased_save_was_written_from_todays_play_and_code(rebased_inputs: tuple[str, str]):
    stamped, now = rebased_inputs
    assert stamped == now, f"a saved rebased save is stale: {ends.REWRITE}"


@pytest.fixture(scope="module")
def two_loads() -> tuple[DayTwoPlayer, DayTwoPlayer]:
    """Typical's week one, loaded twice: two equal plays that share no object but their rules."""
    if ends.available("week1"):
        return (ends.load("week1", "typical", laters("week1", "typical")),
                ends.load("week1", "typical", laters("week1", "typical")))
    a = saved_end("week1", "typical")
    return a, copy.deepcopy(a, {id(a.rules): a.rules})


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_a_changed_play_is_named_and_a_chapter_list_is_not(two_loads: tuple[DayTwoPlayer, DayTwoPlayer]):
    a, b = two_loads
    assert ends.differs(a, b) == []
    b.laters = ()
    assert ends.differs(a, b) == []
    beat = next(iter(b.landed_at))
    b.landed_at = {**b.landed_at, beat: b.landed_at[beat] + 1}
    vars(b)["_rng"].random()   # the play's own draw, as one more glance would advance it
    assert ends.differs(a, b) == ["_rng", "landed_at"]


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
def test_the_rebased_inputs_see_one_decision_more_or_less(two_loads: tuple[DayTwoPlayer, DayTwoPlayer]):
    p, _ = two_loads
    last = p.decisions[-1][0]
    assert rebased.inputs(p, last, None) != rebased.inputs(p, last - 1, None)
    assert rebased.inputs(p, last, None) == rebased.inputs(p, last, None)
    assert len({rebased.inputs(p, last, start) for start in ("a", "b", None)}) == 3, "a different checkpoint is stale"
