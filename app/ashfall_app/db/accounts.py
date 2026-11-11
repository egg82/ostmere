"""Accounts and their sessions: the rows, as typed records. The policy (lifetimes, renewal, limits) is accounts/; this
module only reads and writes, in the caller's transaction. Wall times are the caller's clock, never the database's."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import ColumnElement, Connection, and_, delete, exists, insert, select, update
from sqlalchemy.exc import IntegrityError

from .tables import accounts, saves, sessions

Json = dict[str, object]


@dataclass(frozen=True)
class SessionRecord:
    id: int
    account_id: int
    last_seen_at: datetime


@dataclass(frozen=True)
class AccountRecord:
    id: int
    created_at: datetime
    last_seen_at: datetime
    presentation: Json
    lessons: bool
    """The lessons setting: on until the player turns lessons off."""
    has_words: bool
    has_progress: bool
    """A decision on any save of the account."""


def create_account(conn: Connection, now: datetime) -> int:
    return int(conn.execute(insert(accounts).values(created_at=now, last_seen_at=now).returning(accounts.c.id))
               .scalar_one())


def account(conn: Connection, account_id: int) -> AccountRecord | None:
    progress = exists().where(saves.c.account_id == accounts.c.id, saves.c.decisions > 0)
    row = conn.execute(select(accounts.c.id, accounts.c.created_at, accounts.c.last_seen_at, accounts.c.presentation,
                              accounts.c.lessons, accounts.c.words_hash.is_not(None).label("has_words"),
                              progress.label("has_progress"))
                       .where(accounts.c.id == account_id)).one_or_none()
    if row is None:
        return None
    return AccountRecord(id=row.id, created_at=row.created_at, last_seen_at=row.last_seen_at,
                         presentation=dict(row.presentation), lessons=bool(row.lessons), has_words=bool(row.has_words),
                         has_progress=bool(row.has_progress))


def lock_account(conn: Connection, account_id: int) -> bool:
    """Holds the account's row until the transaction ends; False for no such account."""
    found = conn.execute(select(accounts.c.id).where(accounts.c.id == account_id).with_for_update())
    return found.first() is not None


def set_words(conn: Connection, account_id: int, words_hash: bytes, now: datetime) -> bool | None:
    """Replaces the account's recovery words; False for no such account, None when another account has this hash
    (make other words). In a savepoint, so a clash leaves the caller's transaction usable."""
    try:
        with conn.begin_nested():
            done = conn.execute(update(accounts).where(accounts.c.id == account_id)
                                .values(words_hash=words_hash, words_made_at=now))
    except IntegrityError:
        return None
    return done.rowcount == 1


def account_by_words(conn: Connection, words_hash: bytes) -> int | None:
    found = conn.execute(select(accounts.c.id).where(accounts.c.words_hash == words_hash)).scalar_one_or_none()
    return None if found is None else int(found)


def keep_presentation(conn: Connection, account_id: int, merge: Callable[[Json], Json]) -> tuple[Json, Json] | None:
    """Replaces the stored presentation with `merge(stored)`, the row held from the read to the write so two writers
    cannot both merge into the same old copy; (stored, merged), or None for no such account."""
    stored = conn.execute(select(accounts.c.presentation).where(accounts.c.id == account_id)
                          .with_for_update()).scalar_one_or_none()
    if stored is None:
        return None
    merged = merge(dict(stored))
    conn.execute(update(accounts).where(accounts.c.id == account_id).values(presentation=merged))
    return dict(stored), merged


def set_lessons(conn: Connection, account_id: int, on: bool) -> bool:
    """Sets the account's lessons setting; False for no such account."""
    return conn.execute(update(accounts).where(accounts.c.id == account_id).values(lessons=on)).rowcount == 1


def _live_save(account_id: int, save_id: int) -> ColumnElement[bool]:
    return and_(saves.c.id == save_id, saves.c.account_id == account_id, saves.c.deleted_at.is_(None))


def keep_save_presentation(conn: Connection, account_id: int, save_id: int,
                           merge: Callable[[Json], Json]) -> tuple[Json, Json] | None:
    """keep_presentation for the account's live save `save_id`, the save's row held from the read to the write; None
    when it has no such save."""
    stored = conn.execute(select(saves.c.presentation).where(_live_save(account_id, save_id))
                          .with_for_update()).scalar_one_or_none()
    if stored is None:
        return None
    merged = merge(dict(stored))
    conn.execute(update(saves).where(saves.c.id == save_id).values(presentation=merged))
    return dict(stored), merged


def session_by_hash(conn: Connection, token_hash: bytes, alive_since: datetime) -> SessionRecord | None:
    """The session with this token hash, if it was last used at or after `alive_since`."""
    row = conn.execute(select(sessions.c.id, sessions.c.account_id, sessions.c.last_seen_at)
                       .where(sessions.c.token_hash == token_hash, sessions.c.last_seen_at >= alive_since)
                       ).one_or_none()
    return None if row is None else SessionRecord(id=row.id, account_id=row.account_id, last_seen_at=row.last_seen_at)


def insert_session(conn: Connection, account_id: int, token_hash: bytes, now: datetime, label: str | None = None) -> int:
    return int(conn.execute(insert(sessions).values(account_id=account_id, token_hash=token_hash, created_at=now,
                                                     last_seen_at=now, label=label).returning(sessions.c.id)
                            ).scalar_one())


@dataclass(frozen=True)
class DeviceRecord:
    session_id: int
    label: str | None
    """Null on a session made before labels."""
    created_at: datetime
    last_seen_at: datetime


def sessions_of(conn: Connection, account_id: int) -> list[DeviceRecord]:
    """The account's sessions, most recently used first."""
    found = conn.execute(select(sessions.c.id, sessions.c.label, sessions.c.created_at, sessions.c.last_seen_at)
                         .where(sessions.c.account_id == account_id)
                         .order_by(sessions.c.last_seen_at.desc(), sessions.c.id.desc()))
    return [DeviceRecord(r.id, r.label, r.created_at, r.last_seen_at) for r in found]


def delete_session(conn: Connection, account_id: int, session_id: int) -> bool:
    """Ends one session of this account; False when it is not this account's (or is not there)."""
    done = conn.execute(delete(sessions).where(sessions.c.id == session_id, sessions.c.account_id == account_id))
    return done.rowcount == 1


def keep_newest_sessions(conn: Connection, account_id: int, keep: int) -> int:
    """Drops all but the `keep` sessions of this account used most recently; how many went."""
    newest = (select(sessions.c.id).where(sessions.c.account_id == account_id)
              .order_by(sessions.c.last_seen_at.desc(), sessions.c.id.desc()).limit(keep))
    done = conn.execute(delete(sessions).where(sessions.c.account_id == account_id, sessions.c.id.not_in(newest)))
    return done.rowcount


def delete_sessions_unused_since(conn: Connection, before: datetime) -> int:
    return conn.execute(delete(sessions).where(sessions.c.last_seen_at < before)).rowcount


def touch(conn: Connection, session: SessionRecord, now: datetime) -> None:
    """The session and its account were used at `now`."""
    conn.execute(update(sessions).where(sessions.c.id == session.id).values(last_seen_at=now))
    conn.execute(update(accounts).where(accounts.c.id == session.account_id).values(last_seen_at=now))


def delete_empty_accounts(conn: Connection, unused_since: datetime, limit: int) -> int:
    """Deletes up to `limit` accounts unused since `unused_since` that hold no decision on any save, with their saves
    (and the saves' lines and snapshots) and sessions; how many accounts went."""
    # The NOT EXISTS scan looks indexable but isn't worth it: a partial index left the plan unchanged (~42 ms at 80k
    # accounts), and a flag column would take the save lock before the account lock, deadlocking against this prune.
    progress = exists().where(saves.c.account_id == accounts.c.id, saves.c.decisions > 0)
    doomed = [int(i) for i in conn.execute(
        select(accounts.c.id).where(accounts.c.last_seen_at < unused_since, ~progress)
        .order_by(accounts.c.last_seen_at).limit(limit).with_for_update(skip_locked=True)).scalars()]
    if not doomed:
        return 0
    conn.execute(delete(saves).where(saves.c.account_id.in_(doomed), saves.c.decisions == 0))
    return conn.execute(delete(accounts).where(accounts.c.id.in_(doomed), ~progress)).rowcount
