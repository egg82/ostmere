"""db/joins.py's merge rows against a migrated database of the test's own: saves moved between accounts and numbered on
after the receiving account's, and recovery words carried to an account with none."""
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import Connection, select, update

from ashfall_app.db import accounts as a
from ashfall_app.db import joins
from ashfall_app.db import saves as s
from ashfall_app.db.engine import open_database
from ashfall_app.db.tables import accounts, saves

T0 = datetime(2026, 10, 1, 12, tzinfo=UTC)


@pytest.fixture
def conn(pg_url: str) -> Iterator[Connection]:
    database = open_database(pg_url)
    with database.engine.begin() as c:
        yield c
    database.close()


def begun(conn: Connection, account_id: int, n: int) -> list[int]:
    w = s.Written(state="{}", format=4, rules_digest="d", decisions=1, game_time=0, ended_at=None, build="b",
                  release=1, camp_level=0)
    return [s.insert_save(conn, account_id, T0, w) for _ in range(n)]


def held(conn: Connection) -> dict[int, tuple[int, int | None]]:
    return {int(r.id): (int(r.account_id), r.number)
            for r in conn.execute(select(saves.c.id, saves.c.account_id, saves.c.number))}


def test_moved_saves_are_numbered_after_the_receiving_accounts_deleted_ones_included(conn: Connection):
    t, d, other = (a.create_account(conn, T0) for _ in range(3))
    there = begun(conn, t, 3)
    s.set_deleted(conn, there[2], T0)   # the highest number is a deleted save's
    here = begun(conn, d, 3)
    conn.execute(update(saves).where(saves.c.id == here[2]).values(number=None))   # begun before numbers
    bystander = begun(conn, other, 1)
    assert joins.move_saves(conn, d, t) == 3
    found = held(conn)
    assert [found[i] for i in there] == [(t, 1), (t, 2), (t, 3)]
    assert [found[i] for i in here] == [(t, 5), (t, 6), (t, 4)]   # the unnumbered one first, then by number
    assert found[bystander[0]] == (other, 1)


def test_moving_from_an_account_with_no_saves_moves_none(conn: Connection):
    t, d = a.create_account(conn, T0), a.create_account(conn, T0)
    begun(conn, t, 1)
    assert joins.move_saves(conn, d, t) == 0 and [n for _, n in held(conn).values()] == [1]


def test_words_go_to_an_account_with_none_and_never_over_its_own(conn: Connection):
    t, d = a.create_account(conn, T0), a.create_account(conn, T0)
    assert a.set_words(conn, d, b"mine", T0) is True
    assert joins.carry_words(conn, d, t) is True
    found = {int(r.id): r.words_hash for r in conn.execute(select(accounts.c.id, accounts.c.words_hash))}
    assert found == {t: b"mine", d: None}
    assert a.set_words(conn, d, b"newer", T0) is True
    assert joins.carry_words(conn, d, t) is False and a.account_by_words(conn, b"mine") == t
    assert joins.carry_words(conn, a.create_account(conn, T0), d) is False   # nothing to carry
