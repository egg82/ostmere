"""What a join reads and changes across two accounts (accounts/join.py has the policy): their rows locked in id order,
what each holds, and a device's account folded into another. In the caller's transaction."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Connection, Row, delete, func, select, update

from .tables import accounts, reminder_devices, saves, sessions


@dataclass(frozen=True)
class Holds:
    """What two accounts hold: live saves on each side, the game time of the named one's newest, and whether both have
    recovery words (a merge then ends this side's)."""

    here: int
    there: int
    there_newest_game_time: int | None
    words_replaced: bool


def lock_accounts(conn: Connection, ids: set[int]) -> set[int]:
    """Holds these account rows, lowest id first (two joins crossing each other never deadlock); the ids that exist."""
    found = conn.execute(select(accounts.c.id).where(accounts.c.id.in_(sorted(ids))).order_by(accounts.c.id)
                         .with_for_update()).scalars()
    return {int(i) for i in found}


def has_progress(conn: Connection, account_id: int) -> bool:
    """Whether any save of the account, deleted or not, holds a decision; its saves are held, lowest id first, so a
    decision landing meanwhile waits for the join and is then seen."""
    rows = conn.execute(select(saves.c.decisions).where(saves.c.account_id == account_id).order_by(saves.c.id)
                        .with_for_update()).scalars()
    return any(int(d) > 0 for d in rows)


def holds(conn: Connection, here: int, there: int) -> Holds:
    def live(account_id: int) -> int:
        return int(conn.execute(select(func.count()).select_from(saves)
                                .where(saves.c.account_id == account_id, saves.c.deleted_at.is_(None))).scalar_one())
    newest = conn.execute(select(saves.c.game_time).where(saves.c.account_id == there, saves.c.deleted_at.is_(None))
                          .order_by(saves.c.updated_at.desc(), saves.c.id.desc()).limit(1)).scalar_one_or_none()
    worded = (accounts.c.id.in_((here, there)), accounts.c.words_hash.is_not(None))
    with_words = int(conn.execute(select(func.count()).select_from(accounts).where(*worded)).scalar_one())
    return Holds(here=live(here), there=live(there), there_newest_game_time=None if newest is None else int(newest),
                 words_replaced=here != there and with_words == 2)


def move_sessions(conn: Connection, from_id: int, to_id: int) -> int:
    """Every session of one account becomes the other's, tokens unchanged; how many moved."""
    return conn.execute(update(sessions).where(sessions.c.account_id == from_id).values(account_id=to_id)).rowcount


def move_reminders(conn: Connection, from_id: int, to_id: int) -> int:
    """Every device with reminders on of one account becomes the other's; how many moved."""
    rd = reminder_devices
    return conn.execute(update(rd).where(rd.c.account_id == from_id).values(account_id=to_id)).rowcount


def move_session(conn: Connection, session_id: int, to_id: int) -> int:
    """One session becomes another account's, its token unchanged; how many moved (0: it is gone)."""
    return conn.execute(update(sessions).where(sessions.c.id == session_id).values(account_id=to_id)).rowcount


def move_saves(conn: Connection, from_id: int, to_id: int) -> int:
    """Every save of one account, deleted ones included, becomes the other's, numbered on from the highest number the
    other holds (deleted saves included) in the moving account's own order, unnumbered first; how many moved."""
    base = (select(func.coalesce(func.max(saves.c.number), 0)).where(saves.c.account_id == to_id)
            .scalar_subquery())
    order = (select(saves.c.id, func.row_number().over(order_by=(saves.c.number.asc().nulls_first(), saves.c.id))
                    .label("k")).where(saves.c.account_id == from_id).subquery())
    return conn.execute(update(saves).where(saves.c.id == order.c.id)
                        .values(account_id=to_id, number=base + order.c.k)).rowcount


def carry_words(conn: Connection, from_id: int, to_id: int) -> bool:
    """One account's recovery words become the other's when the other has none; whether they moved."""
    def words(account_id: int) -> Row[tuple[bytes | None, datetime | None]] | None:
        return conn.execute(select(accounts.c.words_hash, accounts.c.words_made_at)
                            .where(accounts.c.id == account_id)).one_or_none()
    mine, theirs = words(from_id), words(to_id)
    if mine is None or mine.words_hash is None or theirs is None or theirs.words_hash is not None:
        return False
    conn.execute(update(accounts).where(accounts.c.id == from_id).values(words_hash=None, words_made_at=None))
    conn.execute(update(accounts).where(accounts.c.id == to_id)
                 .values(words_hash=mine.words_hash, words_made_at=mine.words_made_at))
    return True


def delete_empty_account(conn: Connection, account_id: int) -> int:
    """Deletes an account holding no progress (none decided, or its saves already moved) and its saves (their lines and
    snapshots with them); how many saves went. Its sessions, codes and words go with it."""
    gone = conn.execute(delete(saves).where(saves.c.account_id == account_id)).rowcount
    conn.execute(delete(accounts).where(accounts.c.id == account_id))
    return gone
