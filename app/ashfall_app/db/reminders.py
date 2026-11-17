"""Devices with reminders on (reminders/), read and written in the caller's transaction. Whether a device is due is
`reminders.due`'s; this module finds the candidates, claims one so a send happens once, and prunes."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import CTE, Connection, Row, and_, delete, insert, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .tables import reminder_devices as rd


@dataclass(frozen=True)
class DeviceRecord:
    id: int
    account_id: int
    endpoint: str
    p256dh: str
    auth: str
    after_hours: int
    tz: str
    send_from_hour: int
    send_until_hour: int
    visited_at: datetime
    last_sent_at: datetime | None


@dataclass(frozen=True)
class NewDevice:
    """after_hours None: the absence reminder off, so `hands_free` must be on; the send hours are then kept as the row
    has them (a new row takes these)."""

    account_id: int
    endpoint: str
    p256dh: str
    auth: str
    after_hours: int | None
    tz: str
    send_from_hour: int
    send_until_hour: int
    hands_free: bool = False


def insert_device(conn: Connection, now: datetime, new: NewDevice) -> int:
    """A device whose visit is `now`; its endpoint is unique."""
    return int(conn.execute(insert(rd).values(
        account_id=new.account_id, endpoint=new.endpoint, p256dh=new.p256dh, auth=new.auth,
        after_hours=new.after_hours, tz=new.tz, send_from_hour=new.send_from_hour, send_until_hour=new.send_until_hour,
        hands_free=new.hands_free, visited_at=now, created_at=now).returning(rd.c.id)).scalar_one())


@dataclass(frozen=True)
class Window:
    """What the player picked for a device: the absence in hours and the hours a reminder may arrive in."""

    after_hours: int
    send_from_hour: int
    send_until_hour: int


@dataclass(frozen=True)
class Choice:
    """What the player turned on for a device: the absence reminder with its window (None: off), and the hands-free
    notice. A row always has one of them on."""

    window: Window | None
    hands_free: bool


VISIT_EVERY = timedelta(minutes=10)
"""A visit is stamped at most this often: the stamp rides a statement the request runs anyway, but each one is a write."""


def visit(account_id: int, now: datetime) -> CTE:
    """Stamps the account's devices visited at `now`, those last stamped over VISIT_EVERY ago: a data-modifying CTE
    for a statement the open and advance requests already run, so a visit costs no round trip of its own."""
    return update(rd).where(rd.c.account_id == account_id, rd.c.visited_at < now - VISIT_EVERY
                            ).values(visited_at=now).returning(rd.c.id).cte("visited")


_CHOICE = (rd.c.after_hours, rd.c.send_from_hour, rd.c.send_until_hour, rd.c.hands_free)


def _choice(row: Row[Any]) -> Choice:
    window = None if row.after_hours is None else Window(row.after_hours, row.send_from_hour, row.send_until_hour)
    return Choice(window, row.hands_free)


def keep_device(conn: Connection, now: datetime, new: NewDevice) -> Choice:
    """The device with the player's pick, visited `now`, whoever held its endpoint before (a browser has one
    subscription, and it follows the browser's session)."""
    hours: dict[str, object] = dict(send_from_hour=new.send_from_hour, send_until_hour=new.send_until_hour)
    values: dict[str, object] = dict(account_id=new.account_id, p256dh=new.p256dh, auth=new.auth, tz=new.tz,
                                     after_hours=new.after_hours, hands_free=new.hands_free, visited_at=now)
    q = pg_insert(rd).values(endpoint=new.endpoint, created_at=now, **values, **hours).on_conflict_do_update(
        index_elements=[rd.c.endpoint], set_=values if new.after_hours is None else values | hours)
    return _choice(conn.execute(q.returning(*_CHOICE)).one())


def refresh_device(conn: Connection, now: datetime, account_id: int, endpoint: str, keys: tuple[str, str],
                   tz: str) -> Choice | None:
    """A device already on gets fresh keys and zone, is visited `now` and follows the browser to `account_id`; its
    pick, or None when no row holds the endpoint."""
    q = update(rd).where(rd.c.endpoint == endpoint).values(
        account_id=account_id, p256dh=keys[0], auth=keys[1], tz=tz, visited_at=now).returning(*_CHOICE)
    row = conn.execute(q).first()
    return None if row is None else _choice(row)


def delete_endpoint(conn: Connection, account_id: int, endpoint: str) -> bool:
    """Turns the account's device off; False when the account holds no such endpoint."""
    return conn.execute(delete(rd).where(rd.c.account_id == account_id, rd.c.endpoint == endpoint)).rowcount > 0


def unsent(conn: Connection) -> list[DeviceRecord]:
    """Devices with the absence reminder on that have had none since their last visit: the candidates `due` judges."""
    q = select(rd).where(rd.c.after_hours.is_not(None), or_(rd.c.last_sent_at.is_(None), rd.c.last_sent_at < rd.c.visited_at)
                         ).order_by(rd.c.id)
    return [DeviceRecord(
        id=r.id, account_id=r.account_id, endpoint=r.endpoint, p256dh=r.p256dh, auth=r.auth,
        after_hours=r.after_hours, tz=r.tz, send_from_hour=r.send_from_hour, send_until_hour=r.send_until_hour,
        visited_at=r.visited_at, last_sent_at=r.last_sent_at) for r in conn.execute(q)]


def claim(conn: Connection, device_id: int, visited_at: datetime, now: datetime) -> bool:
    """Marks the device's reminder sent for the visit `visited_at`; True only for the caller that did. Another job's
    claim, or a visit since `visited_at`, leaves nothing to mark. Commit before sending, so a crash loses a reminder
    and never doubles one."""
    won = conn.execute(update(rd).where(and_(
        rd.c.id == device_id, rd.c.visited_at == visited_at,
        or_(rd.c.last_sent_at.is_(None), rd.c.last_sent_at < rd.c.visited_at))
    ).values(last_sent_at=now).returning(rd.c.id)).first()
    return won is not None


def delete_device(conn: Connection, device_id: int) -> None:
    conn.execute(delete(rd).where(rd.c.id == device_id))


def delete_unvisited_before(conn: Connection, before: datetime, limit: int) -> int:
    """Deletes up to `limit` of the devices last visited before `before`; how many went."""
    doomed = (select(rd.c.id).where(rd.c.visited_at < before).order_by(rd.c.visited_at)
              .limit(limit).with_for_update(skip_locked=True))
    return conn.execute(delete(rd).where(rd.c.id.in_(doomed))).rowcount


@dataclass(frozen=True)
class Target:
    """A device a notification goes to."""

    id: int
    endpoint: str
    p256dh: str
    auth: str


def notice_targets(conn: Connection, account_id: int) -> list[Target]:
    """The account's devices that take the hands-free notice."""
    q = select(rd.c.id, rd.c.endpoint, rd.c.p256dh, rd.c.auth).where(rd.c.account_id == account_id, rd.c.hands_free
                                                                     ).order_by(rd.c.id)
    return [Target(r.id, r.endpoint, r.p256dh, r.auth) for r in conn.execute(q)]
