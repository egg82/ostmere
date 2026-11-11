"""The empty-account prune (db/accounts.py delete_empty_accounts) against a decision that commits while it waits on the
save's row: the prune chose its accounts from a snapshot that saw no decision, so what it deletes after the wait must
be judged again against what committed."""
import threading
import time
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import psycopg
import pytest
from sqlalchemy import Engine, text

from ashfall_app.db import accounts as a
from ashfall_app.db import saves as s
from ashfall_app.db.engine import open_database

T0 = datetime(2026, 10, 1, 12, tzinfo=UTC)
CUTOFF = T0 + timedelta(days=30)


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url)
    yield database.engine
    database.close()


def waiting_on_a_lock(url: str) -> bool:
    with psycopg.connect(url) as c:
        row = c.execute("SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock'").fetchone()
    return row is not None and row[0] > 0


def prune_while_a_decision_commits(engine: Engine, url: str, decisions: int) -> tuple[int, int]:
    """(accounts pruned, saves left) when `decisions` is written on an idle account's save and committed only after the
    prune is blocked on that save's row."""
    with engine.begin() as conn:
        account = a.create_account(conn, T0)
        save_id = s.insert_save(conn, account, T0, s.Written(
            state="{}", format=4, rules_digest="d", decisions=0, game_time=0, ended_at=None, build="b", release=1,
            camp_level=0))
    pruned: list[int] = []

    def prune() -> None:
        with engine.begin() as conn:
            pruned.append(a.delete_empty_accounts(conn, CUTOFF, limit=10))

    with engine.connect() as decide:
        decide.execute(text("UPDATE saves SET decisions = :n WHERE id = :id"), {"n": decisions, "id": save_id})
        worker = threading.Thread(target=prune)
        worker.start()
        for _ in range(100):
            if waiting_on_a_lock(url) or not worker.is_alive():
                break
            time.sleep(0.05)
        assert worker.is_alive(), "the prune was not blocked on the save's row, so the race was not set up"
        decide.commit()
    worker.join(20)
    with engine.connect() as c:
        left = int(c.execute(text("SELECT count(*) FROM saves WHERE id = :id"), {"id": save_id}).scalar_one())
    return pruned[0], left


def test_a_save_whose_first_decision_committed_during_the_prune_is_kept(engine: Engine, pg_url: str):
    pruned, left = prune_while_a_decision_commits(engine, pg_url, decisions=1)
    assert (pruned, left) == (0, 1)


def test_a_save_that_stays_empty_through_the_wait_is_still_pruned(engine: Engine, pg_url: str):
    pruned, left = prune_while_a_decision_commits(engine, pg_url, decisions=0)
    assert (pruned, left) == (1, 0)
