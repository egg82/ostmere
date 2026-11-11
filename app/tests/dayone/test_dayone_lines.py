"""No line is logged twice in a day-one save unless a repeat task wrote it (repeats.py), on every route a run plays."""
import pytest

from ashfall_app.engine import Line, LineKey
from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.player import DayOnePlayer
from tests.dayone.repeats import repeated
from tests.dayone.routes import plays
from tests.opening.playthrough import opening_rules


@pytest.mark.playthrough
@pytest.mark.timeout(PLAY_TIMEOUT_S)
@pytest.mark.parametrize("day_route", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_no_line_repeats_in_a_save(day_route: DayOnePlayer):
    assert repeated(day_route.rules, day_route.lines) == []


def test_only_a_repeat_tasks_lines_may_repeat():
    rules = opening_rules()
    task = next(c.id for c in rules.cards if c.cap is None)
    once = next(c.id for c in rules.cards if c.cap is not None)
    key = LineKey("k")
    assert repeated(rules, [Line(0, 0, key, task), Line(1, 0, key, task)]) == []
    for second in (None, once):
        assert repeated(rules, [Line(0, 0, key, task), Line(1, 0, key, second)]) != []
    assert repeated(rules, [Line(0, 0, key), Line(1, 0, LineKey("other"))]) == []
