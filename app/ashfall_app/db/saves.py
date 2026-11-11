"""Saves and what hangs off them (lines, the decision log, day snapshots): the rows, as typed records, read and written
in the caller's transaction. The save's truth is `state`, the engine's canonical text, which a record always holds
whole (a stripped column is read with its digest's manifest: db/manifests.py); the other columns describe it for
queries. What is written when, and what is pruned, is saves/; this module only reads and writes."""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Any
from datetime import datetime

from sqlalchemy import (
    CTE, ColumnElement, Connection, Row, ScalarSelect, Update, and_, bindparam, delete, func, insert, or_, select, update,
)

from .manifests import held_for, whole
from .tables import save_decisions, save_lines, save_snapshots, saves


@dataclass(frozen=True)
class SaveRecord:
    id: int
    account_id: int
    started_at: datetime
    updated_at: datetime
    state: str
    format: int
    rules_digest: str
    decisions: int
    game_time: int
    ended_at: int | None
    build: str | None
    release: int | None
    number: int | None
    camp_level: int | None
    deleted_at: datetime | None
    rule_runs: Any = None
    """What the rules did lately (saves/ruleruns.py), as JSONB reads back; None until a write that keeps it."""
    presentation: Any = None
    """What the page keeps about the save's teaching (api/CONTRACT.txt, SavePresentation), as JSONB reads back."""


@dataclass(frozen=True)
class Listed:
    """What a listing of saves reads: every column of a save but the state and what is needed to replay it."""

    id: int
    started_at: datetime
    updated_at: datetime
    decisions: int
    game_time: int
    ended_at: int | None
    number: int | None
    camp_level: int | None
    deleted_at: datetime | None


@dataclass(frozen=True)
class Written:
    """What a write sets on the save row."""

    state: str
    format: int
    rules_digest: str
    decisions: int
    game_time: int
    ended_at: int | None
    build: str
    release: int
    camp_level: int
    rule_runs: Any = None
    """saves/ruleruns.py's stored form."""


@dataclass(frozen=True)
class LineRecord:
    n: int
    at: int
    key: str


@dataclass(frozen=True)
class DecisionRecord:
    n: int
    at: int
    kind: str
    verb: Any
    """The engine's verb in its codec form (engine verb_to_json), as JSONB reads back: any JSON value."""
    rules_digest: str
    context: Any = None
    """What held as it was made (engine context_to_json), as JSONB reads back; None on rows written before it was
    kept."""


@dataclass(frozen=True)
class SnapshotRecord:
    day: int
    state: str
    rules_digest: str
    decisions: int


_COLUMNS = (saves.c.id, saves.c.account_id, saves.c.started_at, saves.c.updated_at, saves.c.state, saves.c.format,
            saves.c.rules_digest, saves.c.decisions, saves.c.game_time, saves.c.ended_at, saves.c.build,
            saves.c.release, saves.c.number, saves.c.camp_level, saves.c.deleted_at, saves.c.rule_runs,
            saves.c.presentation, held_for(saves.c.state, saves.c.rules_digest).label("manifest"))


LISTED = (saves.c.id, saves.c.started_at, saves.c.updated_at, saves.c.decisions, saves.c.game_time, saves.c.ended_at,
           saves.c.number, saves.c.camp_level, saves.c.deleted_at)


def as_listed(r: Row[Any]) -> Listed:
    return Listed(id=r.id, started_at=r.started_at, updated_at=r.updated_at, decisions=r.decisions,
                  game_time=r.game_time, ended_at=r.ended_at, number=r.number, camp_level=r.camp_level,
                  deleted_at=r.deleted_at)


def _record(r: Row[Any]) -> SaveRecord:
    return SaveRecord(id=r.id, account_id=r.account_id, started_at=r.started_at, updated_at=r.updated_at,
                      state=whole(r.state, r.manifest),
                      format=r.format, rules_digest=r.rules_digest, decisions=r.decisions, game_time=r.game_time,
                      ended_at=r.ended_at, build=r.build, release=r.release, number=r.number, camp_level=r.camp_level,
                      deleted_at=r.deleted_at, rule_runs=r.rule_runs, presentation=r.presentation)


def _next_number(account_id: int | ColumnElement[int]) -> ScalarSelect[Any]:
    """The highest number among the account's saves, deleted ones included, plus one (1 for its first)."""
    held = saves.alias("held")
    return (select(func.coalesce(func.max(held.c.number), 0) + 1).where(held.c.account_id == account_id)
            .scalar_subquery())


def insert_save(conn: Connection, account_id: int, now: datetime, w: Written) -> int:
    return int(conn.execute(insert(saves).values(
        account_id=account_id, created_at=now, started_at=now, updated_at=now, state=w.state, format=w.format,
        rules_digest=w.rules_digest, decisions=w.decisions, game_time=w.game_time, ended_at=w.ended_at, build=w.build,
        release=w.release, camp_level=w.camp_level, rule_runs=w.rule_runs,
        number=_next_number(account_id)).returning(saves.c.id)).scalar_one())


def save(conn: Connection, save_id: int, account_id: int | None, lock: bool = False,
         visit: CTE | None = None) -> SaveRecord | None:
    """A live save (not deleted) by id, the account's own when `account_id` is given; `lock` holds its row until the
    transaction ends (SELECT ... FOR UPDATE), so writes to one save run one after another on any pod. `visit` is a
    write that rides the same statement (reminders.visit)."""
    q = select(*_COLUMNS).where(saves.c.id == save_id, saves.c.deleted_at.is_(None))
    if account_id is not None:
        q = q.where(saves.c.account_id == account_id)
    if visit is not None:
        q = q.add_cte(visit)
    row = conn.execute(q.with_for_update() if lock else q).one_or_none()
    return None if row is None else _record(row)


def saves_of(conn: Connection, account_id: int) -> list[Listed]:
    """The account's live saves, the most recently written first."""
    rows = conn.execute(select(*LISTED).where(saves.c.account_id == account_id, saves.c.deleted_at.is_(None))
                        .order_by(saves.c.updated_at.desc(), saves.c.id.desc()))
    return [as_listed(r) for r in rows]


def live_count(conn: Connection, account_id: int) -> int:
    return int(conn.execute(select(func.count()).select_from(saves)
                            .where(saves.c.account_id == account_id, saves.c.deleted_at.is_(None))).scalar_one())


def deleted_of(conn: Connection, account_id: int, since: datetime) -> list[Listed]:
    """The account's saves deleted at or after `since` (still held), the most recently deleted first."""
    rows = conn.execute(select(*LISTED).where(saves.c.account_id == account_id, saves.c.deleted_at >= since)
                        .order_by(saves.c.deleted_at.desc(), saves.c.id.desc()))
    return [as_listed(r) for r in rows]


def deleted_save(conn: Connection, save_id: int, account_id: int, since: datetime) -> SaveRecord | None:
    """One of the account's saves deleted at or after `since`, its row held until the transaction ends."""
    row = conn.execute(select(*_COLUMNS).where(saves.c.id == save_id, saves.c.account_id == account_id,
                                               saves.c.deleted_at >= since).with_for_update()).one_or_none()
    return None if row is None else _record(row)


def set_deleted(conn: Connection, save_id: int, at: datetime | None) -> None:
    """Deletes the save at `at` (it is held), or with None restores it."""
    conn.execute(update(saves).where(saves.c.id == save_id).values(deleted_at=at))


def purge_deleted(conn: Connection, before: datetime, limit: int) -> int:
    """Deletes for good up to `limit` saves deleted before `before`, with their lines, decisions and snapshots (the
    foreign keys cascade); a row another transaction holds is left for the next. How many went."""
    doomed = (select(saves.c.id).where(saves.c.deleted_at < before).order_by(saves.c.deleted_at).limit(limit)
              .with_for_update(skip_locked=True))
    return conn.execute(delete(saves).where(saves.c.id.in_(doomed.scalar_subquery()))).rowcount


def kept_saves(conn: Connection, batch: int = 200) -> Iterator[SaveRecord]:
    """Every save kept, live or deleted and held, in id order, read `batch` rows at a time."""
    after = 0
    while True:
        rows = [_record(r) for r in conn.execute(
            select(*_COLUMNS).where(saves.c.id > after).order_by(saves.c.id).limit(batch))]
        yield from rows
        if len(rows) < batch:
            return
        after = rows[-1].id


WRITING: Update = update(saves).where(saves.c.id == bindparam("w_save_id", type_=saves.c.id.type)).values(
    {c.name: bindparam(f"w_{c.name}", type_=c.type) for c in (
        saves.c.updated_at, saves.c.state, saves.c.format, saves.c.rules_digest, saves.c.decisions, saves.c.game_time,
        saves.c.ended_at, saves.c.build, saves.c.release, saves.c.camp_level, saves.c.rule_runs)}
    | {"number": func.coalesce(saves.c.number, _next_number(saves.c.account_id))})
"""The statement that writes the save, built once with bound parameters (`writing`), so SQLAlchemy keys and compiles
it once, not on every write; one begun by a build before numbers takes the next number now."""

_WRITE = WRITING.returning(*LISTED)


def writing(save_id: int, now: datetime, w: Written) -> dict[str, Any]:
    """`WRITING`'s parameters."""
    return {"w_save_id": save_id, "w_updated_at": now, "w_state": w.state, "w_format": w.format,
            "w_rules_digest": w.rules_digest, "w_decisions": w.decisions, "w_game_time": w.game_time,
            "w_ended_at": w.ended_at, "w_build": w.build, "w_release": w.release, "w_camp_level": w.camp_level,
            "w_rule_runs": w.rule_runs}


def write(conn: Connection, save_id: int, now: datetime, w: Written) -> Listed:
    """Writes the save, alone (a step's write is db/step.py). The row as written."""
    return as_listed(conn.execute(_WRITE, writing(save_id, now, w)).one())


def append_lines(conn: Connection, save_id: int, lines: Sequence[tuple[int, str]]) -> None:
    """Appends (at, key) lines after the save's last, numbered on from it. Lines are never pruned."""
    if not lines:
        return
    last = conn.execute(select(func.coalesce(func.max(save_lines.c.n), -1)).where(save_lines.c.save_id == save_id)
                        ).scalar_one()
    conn.execute(insert(save_lines), [{"save_id": save_id, "n": int(last) + 1 + i, "at": at, "key": key}
                                      for i, (at, key) in enumerate(lines)])


def last_lines(conn: Connection, save_id: int, limit: int) -> list[LineRecord]:
    """The save's last `limit` lines, oldest first."""
    rows = conn.execute(select(save_lines.c.n, save_lines.c.at, save_lines.c.key).where(save_lines.c.save_id == save_id)
                        .order_by(save_lines.c.n.desc()).limit(limit)).all()
    return [LineRecord(n=r.n, at=r.at, key=r.key) for r in reversed(rows)]


def decisions_after(conn: Connection, save_id: int, n: int) -> list[DecisionRecord]:
    """The save's logged decisions numbered above `n`, in order (those not yet pruned)."""
    rows = conn.execute(select(save_decisions).where(save_decisions.c.save_id == save_id, save_decisions.c.n > n)
                        .order_by(save_decisions.c.n))
    return [_decision(r) for r in rows]


def recent_decisions(conn: Connection, save_id: int, since: dict[str, int]) -> list[DecisionRecord]:
    """The save's logged decisions of each kind in `since` made at or after its game time, in order."""
    c = save_decisions.c
    rows = conn.execute(select(save_decisions).where(c.save_id == save_id, or_(
        *(and_(c.kind == kind, c.at >= at) for kind, at in since.items()))).order_by(c.n))
    return [_decision(r) for r in rows]


def _decision(r: Row[Any]) -> DecisionRecord:
    return DecisionRecord(n=r.n, at=r.at, kind=r.kind, verb=r.verb, rules_digest=r.rules_digest, context=r.context)


def delete_decisions_above(conn: Connection, save_id: int, n: int) -> int:
    return conn.execute(delete(save_decisions).where(save_decisions.c.save_id == save_id,
                                                     save_decisions.c.n > n)).rowcount


def snapshot(conn: Connection, save_id: int, day: int) -> SnapshotRecord | None:
    s = save_snapshots.c
    row = conn.execute(select(s.day, s.state, s.rules_digest, s.decisions,
                              held_for(s.state, s.rules_digest).label("manifest"))
                       .where(s.save_id == save_id, s.day == day)).one_or_none()
    return None if row is None else SnapshotRecord(day=row.day, state=whole(row.state, row.manifest),
                                                   rules_digest=row.rules_digest,
                                                   decisions=row.decisions)


def delete_snapshots_above(conn: Connection, save_id: int, n: int) -> int:
    """Deletes the snapshots taken after decision `n`."""
    return conn.execute(delete(save_snapshots).where(save_snapshots.c.save_id == save_id,
                                                     save_snapshots.c.decisions > n)).rowcount


