"""What one decision writes, whatever the number of statements that write it: decisions on two saves of one account run
side by side and each is counted once, a step's lines number on from the save's last across writes, and the repeats a
write serves come off the decision log it has just pruned and added to."""
import threading
from datetime import timedelta

from dataclasses import replace

from sqlalchemy import Engine, func, select, update

from ashfall_app import engine as e
from ashfall_app.accounts import limits
from ashfall_app.db import saves as rows
from ashfall_app.db.tables import save_decisions, save_lines, saves as saves_table, tries
from ashfall_app.saves.interface import Played, Ruleset
from ashfall_app.saves.service import PgSaves
from ashfall_app.saves.write import DECISIONS_KEPT
from tests.fake_clock import FakeClock

A, B, M0 = e.CardId("gather_wood"), e.CardId("scavenge"), e.MixId("m0")
STAND = e.TapCard(e.CardId("stand_up"))


def test_decisions_on_two_saves_of_one_account_run_side_by_side_and_count_once_each(
        saves: PgSaves, engine: Engine, account: int, clock: FakeClock):
    first, _ = saves.create(account)
    second, _ = saves.create(account)
    rounds, errors = 3, list[Exception]()
    barrier = threading.Barrier(2)

    def play(save_id: int) -> None:
        try:
            barrier.wait(timeout=10)
            for n in range(rounds):
                clock.tick(minutes=11)
                saves.decide(account, save_id, STAND, after=n)
        except Exception as ex:
            errors.append(ex)

    threads = [threading.Thread(target=play, args=(s.save_id,)) for s in (first, second)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert errors == [], errors
    with engine.connect() as conn:
        logged = {r.save_id: r.n for r in conn.execute(
            select(save_decisions.c.save_id, func.count().label("n")).group_by(save_decisions.c.save_id))}
        counted = conn.execute(select(func.count()).select_from(tries).where(tries.c.kind == limits.DECISION)).scalar_one()
    assert logged == {first.save_id: rounds, second.save_id: rounds}
    assert counted == 2 * rounds


def test_lines_number_on_from_the_saves_last_across_writes(
        saves: PgSaves, engine: Engine, account: int, clock: FakeClock):
    info, _ = saves.create(account)
    for n in range(3):
        clock.tick(minutes=10)
        saves.decide(account, info.save_id, STAND, after=n)
    clock.tick(days=1)
    saves.advance(account, info.save_id)
    with engine.connect() as conn:
        ns = list(conn.execute(select(save_lines.c.n).where(save_lines.c.save_id == info.save_id).order_by(save_lines.c.n)
                               ).scalars())
        other = conn.execute(select(func.count()).select_from(save_lines).where(save_lines.c.save_id != info.save_id)
                             ).scalar_one()
    assert len(ns) > 3, "control: the steps wrote lines"
    assert ns == list(range(len(ns))) and other == 0


def test_a_write_returns_the_row_as_written_and_numbers_a_save_begun_before_numbers(
        saves: PgSaves, engine: Engine, account: int, clock: FakeClock):
    info, _ = saves.create(account)
    with engine.begin() as conn:
        conn.execute(update(saves_table).where(saves_table.c.id == info.save_id).values(number=None))
    clock.tick(minutes=10)
    played = saves.decide(account, info.save_id, STAND, after=0)
    with engine.connect() as conn:
        row = rows.save(conn, info.save_id, account)
    assert row is not None and row.number == 1 and row.decisions == played.decisions == 1
    assert row.updated_at == clock()


def test_the_repeats_a_write_serves_leave_out_the_decisions_it_prunes_and_count_the_one_it_adds(
        engine: Engine, account: int, clock: FakeClock, rs: Ruleset):
    open_rs = replace(rs, rules=replace(rs.rules, opening=None))
    saves = PgSaves(engine, open_rs, clock)
    r = open_rs.repeats
    assert r is not None
    _, p = saves.create(account)

    def decide(verb: e.Verb) -> Played:
        clock.tick(30)
        return saves.decide(account, p.save_id, verb, after=p.decisions)

    p = decide(e.SaveMix(e.Mix(M0, (e.CardShare(A, e.BP),))))
    p = decide(e.SwitchMix(M0))
    for _ in range(r.hand_taps - 1):
        p = decide(e.TapCard(B))
    with engine.begin() as conn:   # every decision so far is older than the log's retention, its game time unchanged
        conn.execute(update(save_decisions).where(save_decisions.c.save_id == p.save_id)
                     .values(wall=clock() - DECISIONS_KEPT - timedelta(seconds=1)))
    p = decide(e.TapCard(B))
    assert p.repeats.taps == (), "the pruned taps do not count"
    for _ in range(r.hand_taps - 1):
        p = decide(e.TapCard(B))
    assert p.repeats.taps == ((B, r.hand_taps),), "the tap the write adds does"
