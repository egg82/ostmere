"""The pacing readout's weekly counting (pacing.py) on made-up days: a week is seven calendar days, the last holds what is left,
and a line is counted but is not a new thing."""
from collections import Counter

from tests.weektwo import pacing


def days(n: int) -> list[Counter[str]]:
    return [Counter(card=1, line=2, chip=d % 2) for d in range(n)]


def test_weeks_sum_seven_days_each_and_the_last_holds_the_rest():
    rows = pacing.week_lines(days(10))[1:]
    assert [r.split()[:2] for r in rows] == [["1", "1-7"], ["2", "8-10"]]
    assert [r.split()[-1] for r in rows] == ["10", "5"], "cards and chips are things, the lines are not"


def test_a_line_is_no_new_thing():
    row = pacing.week_lines([Counter(line=5)])[1]
    assert row.split()[-1] == "0"
