"""Transfer codes: the rows, stored only as their keyed hash (accounts/codes.py has the policy: length, lifetime, one
live code per account). In the caller's transaction; wall times are the caller's clock, never the database's."""

from datetime import datetime

from sqlalchemy import Connection, delete, select
from sqlalchemy.dialects.postgresql import insert

from .tables import transfer_codes


def insert_code(conn: Connection, account_id: int, code_hash: bytes, now: datetime, expires_at: datetime) -> bool:
    """Stores a code for the account; False when another code already has this hash (make another)."""
    done = conn.execute(insert(transfer_codes).values(account_id=account_id, code_hash=code_hash, created_at=now,
                                                      expires_at=expires_at)
                        .on_conflict_do_nothing(index_elements=["code_hash"]).returning(transfer_codes.c.id))
    return done.first() is not None


def delete_codes_of(conn: Connection, account_id: int) -> int:
    return conn.execute(delete(transfer_codes).where(transfer_codes.c.account_id == account_id)).rowcount


def delete_expired(conn: Connection, now: datetime, limit: int) -> int:
    """Deletes up to `limit` codes that stopped working at or before `now`, oldest first; how many went."""
    doomed = (select(transfer_codes.c.id).where(transfer_codes.c.expires_at <= now)
              .order_by(transfer_codes.c.expires_at).limit(limit).with_for_update(skip_locked=True))
    return conn.execute(delete(transfer_codes).where(transfer_codes.c.id.in_(doomed.scalar_subquery()))).rowcount


def holder(conn: Connection, code_hash: bytes, now: datetime) -> int | None:
    """The account a live code joins, its row held until the transaction ends (a second redeem waits, then finds
    nothing once the first used it)."""
    found = conn.execute(select(transfer_codes.c.account_id)
                         .where(transfer_codes.c.code_hash == code_hash, transfer_codes.c.expires_at > now)
                         .with_for_update()).scalar_one_or_none()
    return None if found is None else int(found)


def use(conn: Connection, code_hash: bytes) -> None:
    conn.execute(delete(transfer_codes).where(transfer_codes.c.code_hash == code_hash))
