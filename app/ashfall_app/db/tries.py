"""Rate-limit tries: one row per counted request, shared by every pod. `who` is whatever the caller keys a client by
(accounts/limits.py stores an HMAC of the address, never the address, or an account's id). The policy is the
caller's; this module counts, trims and inserts in the caller's transaction."""

from collections.abc import Sequence
from datetime import datetime, timedelta
from functools import cache
from typing import Any, NamedTuple

from sqlalchemy import Connection, Integer, Select, and_, bindparam, delete, func, insert, select

from .tables import tries

_LOCK_SPACE = 0x74727931   # 'try1': the advisory lock space counted kinds are serialised in


def hold(conn: Connection, kind: str) -> None:
    """Until the transaction ends, no other transaction counts or inserts tries of `kind` (a transaction-scoped
    advisory lock), so a count and the insert that follows it are one step across pods."""
    conn.execute(select(func.pg_advisory_xact_lock(_LOCK_SPACE, func.hashtext(kind))))


def trim(conn: Connection, kind: str, before: datetime) -> int:
    """Deletes the tries of `kind` older than `before` that no other transaction holds; how many went. A held one is
    left for the next trim, so a trim never waits (counts only read tries inside their window). Other kinds have their
    own windows."""
    expired = select(tries.c.id).where(tries.c.kind == kind, tries.c.at < before).with_for_update(skip_locked=True)
    return conn.execute(delete(tries).where(tries.c.id.in_(expired))).rowcount


def count(conn: Connection, kind: str, since: datetime, who: bytes | None = None) -> int:
    """Tries of `kind` at or after `since`, from `who` only when given."""
    q = select(func.count()).select_from(tries).where(tries.c.kind == kind, tries.c.at >= since)
    if who is not None:
        q = q.where(tries.c.who == who)
    return int(conn.execute(q).scalar_one())


def oldest(conn: Connection, kind: str, since: datetime, who: bytes | None = None) -> datetime | None:
    """The earliest try `count` would count; None with none."""
    q = select(func.min(tries.c.at)).where(tries.c.kind == kind, tries.c.at >= since)
    if who is not None:
        q = q.where(tries.c.who == who)
    found: datetime | None = conn.execute(q).scalar_one()
    return found


def add(conn: Connection, kind: str, who: bytes, at: datetime) -> None:
    conn.execute(insert(tries).values(kind=kind, who=who, at=at))


class Reading(NamedTuple):
    """The tries of one window as `take` found them, before its own: how many, and the earliest."""

    found: int
    oldest: datetime | None


def take(conn: Connection, kind: str, who: bytes, windows: Sequence[tuple[int, timedelta]], now: datetime
         ) -> tuple[Reading, ...]:
    """`trim`, `count`, `oldest` and `add` for one `who`, as one statement: each (n, window) read at `now`, in order,
    and the try added unless some window has n or more. The trim goes `trim`'s way, past the longest window and never
    waiting. The caller holds what serialises `who`'s tries (the save's row), since the reads see the statement's
    snapshot."""
    params: dict[str, Any] = {"kind": kind, "who": who, "now": now, "before": now - max(w for _, w in windows)}
    for i, (n, window) in enumerate(windows):
        params |= {f"n{i}": n, f"since{i}": now - window}
    row = conn.execute(_taking(len(windows)), params).one()
    return tuple(Reading(int(row[2 * i]), row[2 * i + 1]) for i in range(len(windows)))


@cache
def _taking(windows: int) -> Select[Any]:
    """`take`'s statement for that many windows, built once with bound parameters: SQLAlchemy keys and compiles a
    construct once and reuses it, where one built from literals on every call is walked every time."""
    t = tries.c
    kind, who = bindparam("kind", type_=t.kind.type), bindparam("who", type_=t.who.type)
    counted = select(*(col for i in range(windows) for col in (
        func.count().filter(t.at >= bindparam(f"since{i}", type_=t.at.type)).label(f"c{i}"),
        func.min(t.at).filter(t.at >= bindparam(f"since{i}", type_=t.at.type)).label(f"o{i}")
    ))).where(t.kind == kind, t.who == who, t.at >= bindparam("before", type_=t.at.type)).cte("counted")
    room = and_(*(counted.c[f"c{i}"] < bindparam(f"n{i}", type_=Integer) for i in range(windows)))
    added = insert(tries).from_select(
        ["kind", "who", "at"], select(kind, who, bindparam("now", type_=t.at.type)).select_from(counted).where(room)
    ).returning(t.id).cte("added")
    expired = select(t.id).where(t.kind == kind, t.at < bindparam("before", type_=t.at.type)
                                 ).with_for_update(skip_locked=True)
    trimmed = delete(tries).where(t.id.in_(expired)).returning(t.id).cte("trimmed")
    return select(counted).add_cte(added, trimmed)
