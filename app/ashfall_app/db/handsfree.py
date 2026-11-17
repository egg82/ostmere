"""The hands-free notice's columns on saves (docs/design/reminders.md, "The hands-free notice"), read and written in the
caller's transaction: the kept forecast's answer, the latest save of each account that takes the notice, and the claim
that sends a notice once. What is kept, when it is due and what is sent are saves/handsfree.py's and
reminders/notices.py's."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import Connection, Interval, literal_column, select, update

from .saves import DecisionRecord, decision_record
from .tables import reminder_devices as rd
from .tables import save_decisions, saves

_SECOND = literal_column("interval '1 second'", type_=Interval)
GIVING = ("tap_card", "set_queue")
"""The decision kinds that can give the hands work (saves/handsfree.py `given_at` judges each)."""


@dataclass(frozen=True)
class Latest:
    """An account's most recently written live save, as the notice reads it. `until`: how far its kept forecast
    reached, None when none is kept since its last decision."""

    save_id: int
    account_id: int
    started_at: datetime
    game_time: int
    decisions: int
    at: int | None
    wall: datetime | None
    until: int | None
    sent: int | None

    def stale(self, now: datetime) -> bool:
        """No kept forecast, or the one kept reached a game time now past without the hands coming free."""
        return self.until is None or (self.at is None and self.started_at + timedelta(seconds=self.until) < now)


def keep(conn: Connection, save_id: int, account_id: int, decisions: int, at: int | None, until: int) -> bool:
    """Keeps a forecast's answer on the save, unless a decision was written since the forecast read it (the count is
    no longer `decisions`) or the save was deleted. The wall time is the save's start plus `at` game seconds."""
    wall = None if at is None else saves.c.started_at + at * _SECOND
    q = update(saves).where(saves.c.id == save_id, saves.c.account_id == account_id, saves.c.decisions == decisions,
                            saves.c.deleted_at.is_(None)
                            ).values(hands_free_at=at, hands_free_wall=wall, hands_free_until=until)
    return conn.execute(q).rowcount > 0


def giving(conn: Connection, save_id: int, limit: int = 50) -> list[DecisionRecord]:
    """The save's latest decisions of the kinds that can give the hands work, newest first."""
    c = save_decisions.c
    q = select(save_decisions).where(c.save_id == save_id, c.kind.in_(GIVING)).order_by(c.n.desc()).limit(limit)
    return [decision_record(r) for r in conn.execute(q)]


def latest(conn: Connection) -> list[Latest]:
    """The latest live save of every account with a device that takes the notice."""
    s = saves.c
    takers = select(rd.c.account_id).where(rd.c.hands_free)
    q = (select(s.id, s.account_id, s.started_at, s.game_time, s.decisions, s.hands_free_at, s.hands_free_wall,
                s.hands_free_until, s.hands_free_sent)
         .where(s.deleted_at.is_(None), s.account_id.in_(takers))
         .distinct(s.account_id).order_by(s.account_id, s.updated_at.desc(), s.id.desc()))
    return [Latest(r.id, r.account_id, r.started_at, r.game_time, r.decisions, r.hands_free_at, r.hands_free_wall,
                   r.hands_free_until, r.hands_free_sent) for r in conn.execute(q)]


def claim(conn: Connection, save_id: int, at: int) -> bool:
    """Marks the notice for the instant `at` sent; True only for the caller that did. Another job's claim, a new
    forecast's answer, or a write at or past `at` (the player saw it) leaves nothing to mark. Commit before sending, so
    a crash loses a notice and never doubles one."""
    s = saves.c
    won = conn.execute(update(saves).where(
        s.id == save_id, s.hands_free_at == at, s.game_time < s.hands_free_at,
        s.hands_free_sent.is_distinct_from(s.hands_free_at),
    ).values(hands_free_sent=at).returning(s.id)).first()
    return won is not None
