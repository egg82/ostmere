"""Ids are never reused: a row made after the newest one was deleted gets a new id, and the app cannot choose one."""
from datetime import datetime, timezone

import psycopg
import pytest
from sqlalchemy import Table, create_engine, delete, insert
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.pool import NullPool

from ashfall_app.db import tables

T = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)
SAVE = {"created_at": T, "started_at": T, "updated_at": T, "state": "s", "format": 4, "rules_digest": "d",
        "decisions": 0, "game_time": 0}


def rows(account: int) -> list[tuple[Table, dict[str, object]]]:
    return [
        (tables.accounts, {"created_at": T, "last_seen_at": T}),
        (tables.sessions, {"account_id": account, "token_hash": b"h" * 32, "created_at": T, "last_seen_at": T}),
        (tables.saves, {"account_id": account, **SAVE}),
        (tables.tries, {"kind": "join", "who": b"w" * 32, "at": T}),
        (tables.feedback, {"created_at": T, "text": "t", "build": "b", "release": 1}),
    ]


def test_a_row_after_the_newest_was_deleted_gets_a_new_id(pg_url: str):
    engine = create_engine("postgresql+psycopg://", creator=lambda: psycopg.connect(pg_url), poolclass=NullPool)
    with engine.begin() as conn:
        keep = conn.execute(insert(tables.accounts).values(created_at=T, last_seen_at=T)
                            .returning(tables.accounts.c.id)).scalar_one()
        for table, values in rows(keep):
            first = conn.execute(insert(table).values(**values).returning(table.c.id)).scalar_one()
            conn.execute(delete(table).where(table.c.id == first))
            again = conn.execute(insert(table).values(**values).returning(table.c.id)).scalar_one()
            assert again > first, table.name
    engine.dispose()


def test_an_id_cannot_be_chosen(pg_url: str):
    engine = create_engine("postgresql+psycopg://", creator=lambda: psycopg.connect(pg_url), poolclass=NullPool)
    with pytest.raises(ProgrammingError, match="GENERATED ALWAYS"), engine.begin() as conn:
        conn.execute(insert(tables.accounts).values(id=1, created_at=T, last_seen_at=T))
    engine.dispose()
