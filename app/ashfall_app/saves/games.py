"""Games on one account (api/CONTRACT.txt, "Games on one account"), in the caller's transaction: the account's row held
while its saves are counted, so making, deleting and restoring run one after another on any pod and MAX_SAVES and the
last live save hold under any race; the new-game limit counted in the same step (accounts/limits.py); and the writer's
own retention: a deleted save is held KEPT_DAYS, then a later delete or new game deletes it for good, PURGE_BATCH at a
time (no separate job)."""

import logging
from datetime import datetime, timedelta

from sqlalchemy import Connection

from .. import logs
from ..accounts import limits
from ..db import accounts as account_rows
from ..db import failover
from ..db import saves as rows
from .interface import KEPT_DAYS, MAX_SAVES, Deleted, Games, Info, NewGamesLimited, NotFound, TooManySaves

PURGE_BATCH = 20
KEPT = timedelta(days=KEPT_DAYS)
_log = logging.getLogger("ashfall.saves")


def info(row: rows.SaveRecord | rows.Listed) -> Info:
    return Info(save_id=row.id, number=row.number, decisions=row.decisions, game_time=row.game_time,
                ended_at=row.ended_at, started_at=row.started_at, played_at=row.updated_at, camp_level=row.camp_level)


def hold(conn: Connection, account_id: int) -> int:
    """Holds the account's row until the transaction ends; its live saves. NotFound for no such account."""
    if not account_rows.lock_account(conn, account_id):
        raise NotFound(f"account {account_id}")
    return rows.live_count(conn, account_id)


def room(conn: Connection, account_id: int, live: int, now: datetime) -> None:
    """A new game may be made: under MAX_SAVES (TooManySaves) and the new-game limit, which this counts
    (NewGamesLimited; a count that fails refuses too). An account's first save is not counted: the account limit
    counted it, and an account with no live save has none at all (its last live save cannot be deleted)."""
    if live >= MAX_SAVES:
        logs.info(_log, "save.full", account=account_id, live=live)
        raise TooManySaves(f"account {account_id} holds {live}")
    if live == 0:
        return
    try:
        refusal = limits.made_in(conn, limits.NEW_GAME, account_id, now)
    except Exception as ex:
        failover.let_through(ex)
        _log.error("save.limit_error", extra={"fields": {"account": account_id}}, exc_info=True)
        raise NewGamesLimited("error", limits.UNCOUNTED_RETRY_S) from ex
    if refusal is not None:
        logs.warning(_log, "save.limited", account=account_id, scope=refusal.scope)
        raise NewGamesLimited(refusal.scope, refusal.retry_after_s)


def purge(conn: Connection, now: datetime) -> int:
    """Deletes for good a batch of saves deleted more than KEPT ago, on any account; how many went."""
    gone = rows.purge_deleted(conn, now - KEPT, PURGE_BATCH)
    if gone:
        logs.info(_log, "save.purged", saves=gone)
    return gone


def listed(conn: Connection, account_id: int, now: datetime) -> Games:
    held = rows.deleted_of(conn, account_id, now - KEPT)
    return Games(saves=tuple(info(r) for r in rows.saves_of(conn, account_id)),
                 deleted=tuple(Deleted(info=info(r), deleted_at=r.deleted_at, purge_at=r.deleted_at + KEPT)
                               for r in held if r.deleted_at is not None))
