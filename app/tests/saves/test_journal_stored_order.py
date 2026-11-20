"""A stored journal day reads as stored when opened: the order its notes were written in, its row untouched."""
from collections.abc import Callable

from sqlalchemy import Engine, update

from ashfall_app.db.tables import save_journal
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.journal import DAY_S
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.saves.journal_fixture import journaled, store_lines, stored


def never() -> Callable[[], bool]:
    return lambda: False


def test_opened_reads_a_day_written_as_it_went_as_stored(engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    saves = PgSaves(engine, journaled(rs), clock, stop_for=never)
    save_id = saves.create(account)[0].save_id
    store_lines(engine, save_id, ((50, "l_work"), (100, "l_beat")))
    clock.tick(DAY_S + 60)
    saves.open(account, save_id)
    right = stored(engine, save_id)[0]
    old = [{"subject": n.subject, "slot": n.slot, "key": n.key} for n in reversed(right.notes)]
    with engine.begin() as conn:
        conn.execute(update(save_journal).where(save_journal.c.save_id == save_id, save_journal.c.day == 0)
                     .values(notes=old))
    assert saves.open(account, save_id).days[0].notes == right.notes[::-1]
