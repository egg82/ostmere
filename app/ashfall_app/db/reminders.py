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
    account_id: int
    endpoint: str
    p256dh: str
    auth: str
    after_hours: int
    tz: str
    send_from_hour: int
    send_until_hour: int


def insert_device(conn: Connection, now: datetime, new: NewDevice) -> int:
    """A device whose visit is `now`; its endpoint is unique."""
    return int(conn.execute(insert(rd).values(
        account_id=new.account_id, endpoint=new.endpoint, p256dh=new.p256dh, auth=new.auth,
        after_hours=new.after_hours, tz=new.tz,
        send_from_hour=new.send_from_hour, send_until_hour=new.send_until_hour, visited_at=now, created_at=now).returning(rd.c.id)).scalar_one())


@dataclass(frozen=True)
class Window:
    """What the player picked for a device: the absence in hours and the hours a reminder may arrive in."""

    after_hours: int
    send_from_hour: int
    send_until_hour: int


VISIT_EVERY = timedelta(minutes=10)
"""A visit is stamped at most this often: the stamp rides a statement the request runs anyway, but each one is a write."""


def visit(account_id: int, now: datetime) -> CTE:
    """Stamps the account's devices visited at `now`, those last stamped over VISIT_EVERY ago: a data-modifying CTE
    for a statement the open and advance requests already run, so a visit costs no round trip of its own."""
    return update(rd).where(rd.c.account_id == account_id, rd.c.visited_at < now - VISIT_EVERY
                            ).values(visited_at=now).returning(rd.c.id).cte("visited")


def _window(row: Row[Any]) -> Window:
    return Window(row.after_hours, row.send_from_hour, row.send_until_hour)


def keep_device(conn: Connection, now: datetime, new: NewDevice) -> Window:
    """The device with the player's pick, visited `now`, whoever held its endpoint before (a browser has one
    subscription, and it follows the browser's session)."""
    values: dict[str, object] = dict(account_id=new.account_id, p256dh=new.p256dh, auth=new.auth, tz=new.tz, after_hours=new.after_hours,
                  send_from_hour=new.send_from_hour, send_until_hour=new.send_until_hour, visited_at=now)
    q = pg_insert(rd).values(endpoint=new.endpoint, created_at=now, **values).on_conflict_do_update(
        index_elements=[rd.c.endpoint], set_=values)
    return _window(conn.execute(q.returning(rd.c.after_hours, rd.c.send_from_hour, rd.c.send_until_hour)).one())


def refresh_device(conn: Connection, now: datetime, account_id: int, endpoint: str, keys: tuple[str, str],
                   tz: str) -> Window | None:
    """A device already on gets fresh keys and zone, is visited `now` and follows the browser to `account_id`; its
    pick, or None when no row holds the endpoint."""
    q = update(rd).where(rd.c.endpoint == endpoint).values(
        account_id=account_id, p256dh=keys[0], auth=keys[1], tz=tz, visited_at=now
    ).returning(rd.c.after_hours, rd.c.send_from_hour, rd.c.send_until_hour)
    row = conn.execute(q).first()
    return None if row is None else _window(row)


def delete_endpoint(conn: Connection, account_id: int, endpoint: str) -> bool:
    """Turns the account's device off; False when the account holds no such endpoint."""
    return conn.execute(delete(rd).where(rd.c.account_id == account_id, rd.c.endpoint == endpoint)).rowcount > 0


def unsent(conn: Connection) -> list[DeviceRecord]:
    """Devices that have had no reminder since their last visit: the candidates `due` judges."""
    q = select(rd).where(or_(rd.c.last_sent_at.is_(None), rd.c.last_sent_at < rd.c.visited_at)).order_by(rd.c.id)
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
