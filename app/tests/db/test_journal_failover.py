"""A step that composes journal days and meets a failover (docs/decisions.md, "A database failover is replayed once, or
answered 503") stores each day once: replayed when the fault lands on its write, answered 503 when it lands on the
COMMIT, and composed by the page's next ask."""
import psycopg
import pytest

from ashfall_app.opening.schema import Opening
from ashfall_app.saves.journal import DAY_S
from tests.db.test_failover import at_commit, at_statement, engine_of, terminate
from tests.saves.journal_fixture import a_beat_line
from tests.game_client import GameClient


def into_journal(statement: str) -> bool:
    return "INSERT INTO save_journal" in statement


def days(url: str, save_id: int) -> list[tuple[int, int]]:
    """(day, notes) per stored day: the count of rows a day has is the point."""
    with psycopg.connect(url) as c:
        return [(d, len(n)) for d, n in c.execute(
            "SELECT day, notes FROM save_journal WHERE save_id = %s ORDER BY day", (save_id,)).fetchall()]


def three_days_on(game: GameClient, url: str, opening: Opening) -> int:
    """A save with a beat's line on day 1, its clock three days on."""
    save_id = int(game.begin()["save"]["save_id"])
    key, _ = a_beat_line(opening)
    with psycopg.connect(url) as c:
        c.execute("INSERT INTO save_lines (save_id, n, at, key) SELECT %s, coalesce(max(n) + 1, 0), %s, %s"
                  " FROM save_lines WHERE save_id = %s", (save_id, DAY_S + 30, key, save_id))
    game.clock.tick(3 * DAY_S + 60)
    return save_id


def test_a_step_whose_write_meets_a_failover_is_replayed_and_stores_each_day_once(
        game: GameClient, pg_url: str, shipped_opening: Opening, capsys: pytest.CaptureFixture[str]):
    save_id = three_days_on(game, pg_url, shipped_opening)
    at_statement(engine_of(game), terminate(pg_url), into_journal)
    r = game.advance(save_id)
    assert r.status_code == 200, r.text
    logged = [ln for ln in capsys.readouterr().out.splitlines() if "event=db.failover" in ln]
    assert len(logged) == 1 and "replayed=true" in logged[0], logged
    assert days(pg_url, save_id) == [(0, 0), (1, 1), (2, 0)]


def test_a_step_whose_commit_is_lost_is_answered_503_and_the_next_ask_stores_each_day_once(
        game: GameClient, pg_url: str, shipped_opening: Opening):
    save_id = three_days_on(game, pg_url, shipped_opening)
    at_commit(engine_of(game), terminate(pg_url))
    assert game.advance(save_id).status_code == 503
    r = game.advance(save_id)
    assert r.status_code == 200, r.text
    assert days(pg_url, save_id) == [(0, 0), (1, 1), (2, 0)]
