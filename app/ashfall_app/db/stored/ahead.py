"""A save's catch-up kept ahead (tables.save_ahead), read and written in the caller's transaction. Whether a kept one
fits the row a step loads, and computing it, is saves/ahead.py's."""

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Connection, Engine, func, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ..tables import save_ahead, saves

_CLAIM = 0x0A4EAD
"""The first key of the advisory lock a job claims a save's advance with (the second is the save's id)."""


@dataclass(frozen=True)
class AheadRecord:
    save_id: int
    base: str
    rules_digest: str
    release: int
    game_time: int
    state: str
    lines: Any
    rule_runs: Any


def kept(conn: Connection, save_id: int) -> AheadRecord | None:
    row = conn.execute(select(save_ahead).where(save_ahead.c.save_id == save_id)).one_or_none()
    return None if row is None else AheadRecord(row.save_id, row.base, row.rules_digest, row.release, row.game_time,
                                                row.state, row.lines, row.rule_runs)


def keep(conn: Connection, rec: AheadRecord, now: datetime) -> bool:
    """Keeps `rec` in place of the one kept, unless that one is of the same row and either of a later release, or of
    these rules and as far ahead or further (two jobs at once, or a pod mid-deploy, never step one back). False when
    it was not kept."""
    c = save_ahead.c
    values = {"base": rec.base, "rules_digest": rec.rules_digest, "release": rec.release, "game_time": rec.game_time,
              "state": rec.state, "lines": rec.lines, "rule_runs": rec.rule_runs, "written_at": now}
    ins = pg_insert(save_ahead).values(save_id=rec.save_id, **values)
    q = ins.on_conflict_do_update(
        index_elements=[c.save_id], set_=values,
        where=or_(c.base != rec.base, c.release < rec.release,
                  (c.release == rec.release) & (c.rules_digest == rec.rules_digest) & (c.game_time < rec.game_time)))
    return conn.execute(q.returning(c.save_id)).one_or_none() is not None


@contextmanager
def claimed(engine: Engine, save_id: int) -> Generator[bool]:
    """Whether this job holds the claim on advancing the save, held on a connection of its own until the block ends:
    the other site's job, running the same minute, passes it over."""
    with engine.connect() as conn:
        got = bool(conn.execute(select(func.pg_try_advisory_lock(_CLAIM, save_id))).scalar_one())
        conn.commit()
        try:
            yield got
        finally:
            if got:
                conn.execute(select(func.pg_advisory_unlock(_CLAIM, save_id)))
                conn.commit()


def behind(conn: Connection, now: datetime, visited_since: datetime, min_behind_s: int) -> list[int]:
    """The live saves written since `visited_since` whose game clock is more than `min_behind_s` past both the save as
    stored and what is kept ahead of it, oldest written first."""
    s, a = saves.c, save_ahead.c
    clock = func.floor(func.extract("epoch", now - s.started_at))
    reached = func.greatest(s.game_time, func.coalesce(a.game_time, s.game_time))
    q = (select(s.id).select_from(saves.outerjoin(save_ahead, a.save_id == s.id))
         .where(s.deleted_at.is_(None), s.updated_at >= visited_since, clock - reached > min_behind_s)
         .order_by(s.updated_at))
    return [r.id for r in conn.execute(q)]
