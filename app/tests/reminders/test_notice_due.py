"""`notice_due` (reminders/due.py): a hands-free notice is due once its instant has passed unseen, and goes once."""
from datetime import UTC, datetime, timedelta

from hypothesis import given
from hypothesis import strategies as st

from ashfall_app.reminders.due import notice_due

START = datetime(2026, 11, 3, 12, tzinfo=UTC)
AT = 4000
WALL = START + timedelta(seconds=AT)


def test_due_once_its_wall_time_has_passed_and_the_save_was_written_before_it():
    assert notice_due(AT, WALL, AT - 1, None, WALL)
    assert not notice_due(AT, WALL, AT - 1, None, WALL - timedelta(seconds=1))


def test_not_due_when_the_save_was_written_at_or_after_it():
    assert not notice_due(AT, WALL, AT, None, WALL + timedelta(hours=1))
    assert not notice_due(AT, WALL, AT + 60, None, WALL + timedelta(hours=1))


def test_not_due_without_a_kept_instant_or_once_sent_for_it():
    assert not notice_due(None, None, 0, None, WALL)
    assert not notice_due(AT, WALL, 0, AT, WALL)
    assert notice_due(AT, WALL, 0, AT - 100, WALL), "a notice sent for an earlier instant does not cover this one"


@given(st.lists(st.tuples(st.integers(0, 3), st.integers(0, 20_000)), min_size=1, max_size=30))
def test_the_job_asking_again_and_again_sends_at_most_once_per_instant(runs: list[tuple[int, int]]):
    """Runs of the job, each at a later wall time, over a save whose kept instant a new forecast may change (one of a
    few); a run that finds it due claims it, as the job does. While the kept instant stays the same, it is sent for
    once."""
    sent: int | None = None
    sends: list[int] = []
    now = START
    for pick, step in runs:
        at = AT + 1000 * pick
        now += timedelta(seconds=step)
        if notice_due(at, START + timedelta(seconds=at), 0, sent, now):
            sends.append(at)
            sent = at
    assert all(a != b for a, b in zip(sends, sends[1:]))
