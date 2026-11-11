"""The saved ends week two's chapters play on from (ends.py) are today's: where present, the directory holds every end the
chain needs and nothing else, on today's rules; each chapter played on from the saved end before it ends where its own saved end says
(week one's ends are checked against week one's play in `playthrough-week-one-saved`, tests/weekone_saved); each saved
rebased save was written from today's play and code. A stale end fails, naming the command that rewrites them; the
controls show the comparisons see a changed play."""
import copy
import json
from pathlib import Path

import pytest

from ashfall_app.engine import rules_digest
from tests.daythree.content import rules3
from tests.daytwo.conftest import PLAY_TIMEOUT_S
from tests.daytwo.player import DayTwoPlayer
from tests.weektwo import ends, rebased
from tests.weektwo.routes import SAVED, laters, saved_end

CHECKED = [(chapter, name) for chapter, names in SAVED.items() if chapter != "week1" for name in names]


@pytest.fixture(scope="module")
def todays_rules() -> str:
    return rules_digest(rules3())


@pytest.mark.playthrough
def test_the_saved_ends_are_every_end_the_chain_needs_on_todays_rules(todays_rules: str):
    wanted = {ends.player_path(c, n) for c, names in SAVED.items() for n in names}
    wanted |= {ends.rebased_path(c) for c in rebased.OLD} | {ends.manifest()}
    assert len(wanted) > len(SAVED)
    if ends.available():
        assert set(ends.golden().iterdir()) == wanted, ends.REWRITE
        assert ends.manifest_rules() == todays_rules, f"the saved ends were written under other rules: {ends.REWRITE}"


@pytest.fixture
def stale_saves(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A saves root whose directory for today's key holds a manifest stamped with other rules."""
    monkeypatch.setenv("ASHFALL_SAVES_ROOT", str(tmp_path))
    (tmp_path / ends.key()).mkdir()
    ends.manifest().write_text(json.dumps({"rules": "0" * 64, "rewrite": ends.REWRITE}))
    return tmp_path


def test_a_stale_stamp_is_not_used_and_under_the_require_variable_fails(
        stale_saves: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(ends.REQUIRE, raising=False)
    assert not ends.available()
    monkeypatch.setenv(ends.REQUIRE, "1")
    with pytest.raises(AssertionError, match="other rules"):
        ends.available()


def test_missing_saves_are_not_used_and_under_the_require_variable_fail(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ASHFALL_SAVES_ROOT", str(tmp_path))
    monkeypatch.delenv(ends.REQUIRE, raising=False)
    assert not ends.available()
    monkeypatch.setenv(ends.REQUIRE, "1")
    with pytest.raises(AssertionError, match="no saved ends"):
        ends.available()


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
    if ends.available():
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
    assert rebased.inputs(p, last) != rebased.inputs(p, last - 1)
    assert rebased.inputs(p, last) == rebased.inputs(p, last)
