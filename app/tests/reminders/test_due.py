"""`due` (reminders/due.py): the window, the wait, and one reminder per absence."""
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from hypothesis import given, settings
from hypothesis import strategies as st

from ashfall_app.reminders.due import due as judge

T0 = datetime(2026, 11, 3, 12, tzinfo=UTC)   # noon in UTC; a Tuesday
DAY = timedelta(days=1)


def due(visited_at: datetime, after: timedelta, last_sent_at: datetime | None, now: datetime, tz: str,
        window: tuple[int, int] = (9, 21)) -> bool:
    return judge(visited_at, after, last_sent_at, now, tz, window[0], window[1])


def test_due_once_the_wait_has_passed_in_daylight():
    assert due(T0 - DAY, DAY, None, T0, "UTC")


def test_not_due_before_the_wait_is_over():
    assert not due(T0 - DAY + timedelta(minutes=1), DAY, None, T0, "UTC")


def test_not_due_once_a_reminder_went_for_this_visit():
    assert not due(T0 - DAY, DAY, T0 - timedelta(hours=1), T0, "UTC")


def test_due_again_after_a_visit_that_followed_the_last_send():
    assert due(T0 - DAY, DAY, T0 - 3 * DAY, T0, "UTC")


def test_the_window_is_the_devices_local_time():
    at = datetime(2026, 11, 3, 8, 59, tzinfo=UTC)
    assert not due(at - 3 * DAY, DAY, None, at, "UTC")
    assert due(at - 3 * DAY, DAY, None, at, "Asia/Kolkata")   # 14:29 there
    assert not due(at - 3 * DAY, DAY, None, at, "America/New_York")   # 03:59 there


def test_the_window_opens_at_nine_and_closes_at_nine_in_the_evening():
    def at(hour: int, minute: int) -> bool:
        now = datetime(2026, 11, 3, hour, minute, tzinfo=UTC)
        return due(now - 3 * DAY, DAY, None, now, "UTC")
    assert [at(8, 59), at(9, 0), at(20, 59), at(21, 0)] == [False, True, True, False]


def test_a_window_that_wraps_past_midnight_holds_the_night_and_not_the_day():
    def at(hour: int) -> bool:
        now = datetime(2026, 11, 3, hour, 30, tzinfo=UTC)
        return due(now - 3 * DAY, DAY, None, now, "UTC", (22, 7))
    assert [at(21), at(22), at(23), at(0), at(6), at(7), at(12)] == [False, True, True, True, True, False, False]


def test_equal_ends_mean_any_hour():
    for hour in range(24):
        now = datetime(2026, 11, 3, hour, tzinfo=UTC)
        assert due(now - 3 * DAY, DAY, None, now, "UTC", (5, 5))


def test_a_name_that_is_not_a_zone_is_never_due():
    assert not due(T0 - 3 * DAY, DAY, None, T0, "Not/AZone")
    assert not due(T0 - 3 * DAY, DAY, None, T0, "")


def test_ticking_every_five_minutes_through_three_days_sends_exactly_once():
    visited, last_sent, sends = T0, None, 0
    for step in range(3 * 24 * 12):
        now = visited + timedelta(minutes=5 * step)
        if due(visited, DAY, last_sent, now, "UTC"):
            last_sent, sends = now, sends + 1
    assert sends == 1


timelines = st.lists(st.tuples(st.sampled_from("vt"), st.integers(0, 24 * 60)), min_size=1, max_size=60)


hours = st.integers(0, 23)
zones = st.sampled_from(["UTC", "America/New_York", "Asia/Kolkata"])


@given(minutes=st.integers(0, 3 * 24 * 60), tz=zones, from_hour=hours, until_hour=hours)
@settings(max_examples=500, deadline=None)
def test_a_send_lands_only_inside_the_window_and_equal_ends_never_block(minutes: int, tz: str, from_hour: int, until_hour: int):
    """Any window, wrapped or not: with the wait long past, `due` is true exactly when the device's local hour is one
    of the hours counted forward from `from_hour` for the window's length (a full day when the ends are equal)."""
    now = T0 + timedelta(minutes=minutes)
    length = (until_hour - from_hour) % 24 or 24
    inside = {(from_hour + i) % 24 for i in range(length)}
    assert due(now - 30 * DAY, DAY, None, now, tz, (from_hour, until_hour)) == (now.astimezone(ZoneInfo(tz)).hour in inside)


@given(events=timelines, after_hours=st.integers(1, 168), tz=zones, from_hour=hours, until_hour=hours)
@settings(max_examples=300, deadline=None)
def test_a_visit_is_reminded_at_most_once_however_often_the_job_runs(
        events: list[tuple[str, int]], after_hours: int, tz: str, from_hour: int, until_hour: int):
    """Events are visits ('v') and job ticks ('t'), each a few minutes after the last. A tick sends when `due` says so
    and then records the send, as the job's claim does. Between two visits that happens at most once."""
    now, visited, last_sent = T0, T0, None
    sent_since_visit, most = 0, 0
    for kind, gap in events:
        now += timedelta(minutes=gap)
        if kind == "v":
            visited, sent_since_visit = now, 0
        elif due(visited, timedelta(hours=after_hours), last_sent, now, tz, (from_hour, until_hour)):
            last_sent, sent_since_visit = now, sent_since_visit + 1
        most = max(most, sent_since_visit)
    assert most <= 1
