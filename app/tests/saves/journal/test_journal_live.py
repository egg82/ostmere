"""A step writes the day in progress as it goes (docs/design/journal.md, "Written as the day goes"): the day's row holds
the notes so far, a note once stored is never removed or changed by a later step, many small steps store what one long
advance or a return stores, and a closed row is never recomposed."""
from collections.abc import Callable

from sqlalchemy import Engine, insert

from ashfall_app.db import accounts
from ashfall_app.db.engine import open_database
from ashfall_app.db.migrate import migrate
from ashfall_app.db.tables import save_journal
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.journal import DAY_S, ComposedDay, Note
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.saves.journal.journal_fixture import journaled, store_lines, stored

HOUR = 3600


def never() -> Callable[[], bool]:
    return lambda: False


def begun(engine: Engine, rs: Ruleset, clock: FakeClock, account: int) -> tuple[PgSaves, int]:
    saves = PgSaves(engine, journaled(rs), clock, stop_for=never)
    info, _ = saves.create(account)
    store_lines(engine, info.save_id)
    return saves, info.save_id


def _begins(later: list[ComposedDay], earlier: list[ComposedDay]) -> bool:
    """Every day of `earlier` is in `later`, its notes the start of the later day's and its gap kept."""
    by_day = {d.day: d for d in later}
    return all(d.day in by_day and by_day[d.day].notes[:len(d.notes)] == d.notes
               and (d.gap is None or by_day[d.day].gap == d.gap) for d in earlier)


def test_a_day_in_progress_is_stored_with_its_notes_so_far(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                           account: int):
    saves, save_id = begun(engine, rs, clock, account)
    clock.tick(HOUR)
    played = saves.advance(account, save_id)
    today = stored(engine, save_id)
    assert [d.day for d in today] == [0]
    assert Note("s_beat", "first", "j.beat") in today[0].notes
    assert list(played.days) == today


def test_a_note_once_stored_never_disappears_or_changes(engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    saves, save_id = begun(engine, rs, clock, account)
    seen: list[ComposedDay] = []
    for _ in range(3 * 24 // 4):
        clock.tick(4 * HOUR + 7)
        saves.advance(account, save_id)
        now = stored(engine, save_id)
        assert _begins(now, seen), (seen, now)
        seen = now
    assert sum(len(d.notes) for d in seen) > 2


def _stepped(url: str, rs: Ruleset, steps: list[int], open_at_end: bool) -> tuple[int, list[ComposedDay]]:
    database = open_database(url, max_size=2)
    try:
        clock = FakeClock()
        with database.engine.begin() as conn:
            account = accounts.create_account(conn, clock())
        saves, save_id = begun(database.engine, rs, clock, account)
        for s in steps:
            clock.tick(s)
            saves.advance(account, save_id)
        if open_at_end:
            saves.open(account, save_id)
        return save_id, stored(database.engine, save_id)
    finally:
        database.close()


SMALL = [8 * HOUR + 17 * 60] * 16
"""Sixteen steps of 8h17m: about five and a half days, crossing each day's end mid-step."""


def test_small_steps_and_one_long_advance_store_the_same_rows(pg_url: str, pg_empty: str, rs: Ruleset):
    """Two databases, so the two saves share an id: every roll is keyed by it."""
    migrate(pg_empty)
    small = _stepped(pg_url, rs, SMALL, False)
    jump = _stepped(pg_empty, rs, [sum(SMALL)], False)
    assert small[0] == jump[0] and small[1] == jump[1] and len(small[1]) == 6


def test_a_return_composes_what_live_play_composes(pg_url: str, pg_empty: str, rs: Ruleset):
    migrate(pg_empty)
    live = _stepped(pg_url, rs, SMALL, False)
    back = _stepped(pg_empty, rs, [sum(SMALL)], True)
    assert live == back


def test_closed_rows_stay_and_the_day_in_progress_is_composed_from_its_start(
        engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    saves, save_id = begun(engine, rs, clock, account)
    whole: list[dict[str, object]] = [{"save_id": save_id, "day": 0, "notes": [{"subject": "s_beat", "slot": "first", "key": "j.beat"}],
              "gap": None, "through": DAY_S},
             {"save_id": save_id, "day": 1, "notes": [], "gap": "busy", "through": 2 * DAY_S}]
    with engine.begin() as conn:
        conn.execute(insert(save_journal), whole)
    before = stored(engine, save_id)
    clock.tick(2 * DAY_S + HOUR)
    saves.advance(account, save_id)
    after = stored(engine, save_id)
    assert after[:2] == before
    assert [d.day for d in after] == [0, 1, 2]
    assert Note("s_work", "catchup", "j.work_caught") in after[2].notes
