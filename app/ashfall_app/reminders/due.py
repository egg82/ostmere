"""Whether a device is due its reminder now. Pure: everything it reads is an argument."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def local_hour(now: datetime, tz: str) -> int | None:
    """The hour of day at `now` in zone `tz`; None for a name that is not a zone (it never matches the window)."""
    try:
        return now.astimezone(ZoneInfo(tz)).hour
    except (ZoneInfoNotFoundError, ValueError):
        return None


def in_window(hour: int, from_hour: int, until_hour: int) -> bool:
    """Whether `hour` falls from `from_hour` up to `until_hour`. A window may wrap past midnight (22 until 7);
    equal ends mean any hour."""
    if from_hour == until_hour:
        return True
    if from_hour < until_hour:
        return from_hour <= hour < until_hour
    return hour >= from_hour or hour < until_hour


def due(visited_at: datetime, after: timedelta, last_sent_at: datetime | None, now: datetime, tz: str,
        from_hour: int, until_hour: int) -> bool:
    """True when the player has been away `after`, no reminder has gone since that visit, and the device's local hour
    is inside the player's window. A visit after the last send re-arms it; nothing else does, so one absence sends at
    most one reminder."""
    if last_sent_at is not None and last_sent_at >= visited_at:
        return False
    if now < visited_at + after:
        return False
    hour = local_hour(now, tz)
    return hour is not None and in_window(hour, from_hour, until_hour)
