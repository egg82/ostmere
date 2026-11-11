"""Tester feedback rows (feedback/), read and written in the caller's transaction. When rows go is the writer's
(feedback/service.py); this module only counts, trims and lists."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Connection, delete, insert, select

from .tables import feedback


@dataclass(frozen=True)
class FeedbackRecord:
    id: int
    created_at: datetime
    text: str
    build: str
    release: int
    account_id: int | None
    save_id: int | None
    game_time: int | None
    last_line: str | None


@dataclass(frozen=True)
class Sent:
    """What an insert stores besides the words and the time."""

    build: str
    release: int
    account_id: int | None
    save_id: int | None
    game_time: int | None
    last_line: str | None


def insert_feedback(conn: Connection, now: datetime, text: str, sent: Sent) -> int:
    return int(conn.execute(insert(feedback).values(
        created_at=now, text=text, build=sent.build, release=sent.release, account_id=sent.account_id,
        save_id=sent.save_id, game_time=sent.game_time, last_line=sent.last_line).returning(feedback.c.id)).scalar_one())


def delete_before(conn: Connection, before: datetime, limit: int) -> int:
    """Deletes up to `limit` of the oldest rows created before `before`; how many went."""
    doomed = (select(feedback.c.id).where(feedback.c.created_at < before).order_by(feedback.c.created_at)
              .limit(limit).with_for_update(skip_locked=True))
    return conn.execute(delete(feedback).where(feedback.c.id.in_(doomed))).rowcount


def listing(conn: Connection, since: datetime | None) -> list[FeedbackRecord]:
    """Rows created at or after `since` (all when None), oldest first."""
    q = select(feedback).order_by(feedback.c.created_at, feedback.c.id)
    if since is not None:
        q = q.where(feedback.c.created_at >= since)
    return [FeedbackRecord(
        id=r.id, created_at=r.created_at, text=r.text, build=r.build, release=r.release, account_id=r.account_id,
        save_id=r.save_id, game_time=r.game_time, last_line=r.last_line) for r in conn.execute(q)]
