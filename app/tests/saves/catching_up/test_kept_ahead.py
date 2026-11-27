"""A catch-up kept ahead by the job (saves/ahead.py): a save the job advanced while its player was away opens to what
one open without the job writes and serves (the row, its lines, rule runs and journal days; the step's lines and rule
runs), also when the rows were written under older rules and rebased; what is kept goes stale with the row it began
from; and two jobs, or two builds' jobs, never step it back."""
import logging
from collections.abc import Callable
from dataclasses import replace
from datetime import timedelta
from typing import Any, NamedTuple

import pytest
from sqlalchemy import Engine, delete, select, update

from ashfall_app import engine as e
from ashfall_app.db import ahead as kept_rows
from ashfall_app.db import saves as rows
from ashfall_app.db.tables import save_ahead, save_decisions, save_journal, save_lines, save_snapshots, saves
from ashfall_app.saves import ahead
from ashfall_app.saves.interface import Played, Ruleset
from ashfall_app.saves.builds.load import load
from ashfall_app.saves.ruleruns import RuleRun
from ashfall_app.saves.service import PgSaves
from ashfall_app.saves.write import written
from tests.fake_clock import FakeClock
from tests.saves.catching_up.behind import BUSY_AWAY_S, seed_busy, snapshot
from tests.saves.catching_up.chunks import never

JOB_EVERY_S = 1800


Stored = tuple[tuple[object, ...], list[tuple[Any, ...]]]


class Served(NamedTuple):
    save: e.Save
    lines: tuple[e.Line, ...]
    rule_runs: tuple[RuleRun, ...]
    catching_up_to: int | None
    days: tuple[object, ...]


def stored(engine: Engine, save_id: int) -> Stored:
    with engine.connect() as conn:
        days = conn.execute(select(save_journal).where(save_journal.c.save_id == save_id)
                            .order_by(save_journal.c.day)).all()
    return snapshot(engine, save_id), [tuple(d) for d in days]


def served(played: Played) -> Served:
    return Served(played.save, played.lines, played.rule_runs, played.catching_up_to, played.days)


def away_with_jobs(engine: Engine, rs: Ruleset, clock: FakeClock) -> int:
    """Moves the clock through the absence, the job running every JOB_EVERY_S; the game seconds it kept."""
    gained = 0
    for _ in range(BUSY_AWAY_S // JOB_EVERY_S):
        clock.tick(JOB_EVERY_S)
        gained += ahead.keep(engine, lambda: rs, clock, 600.0)
    clock.tick(BUSY_AWAY_S % JOB_EVERY_S + 30)
    return gained


class _Used(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.INFO)
        self.used = False

    def emit(self, record: logging.LogRecord) -> None:
        self.used = self.used or record.msg == "save.ahead_used"


def both_ways[T](engine: Engine, rs: Ruleset, clock: FakeClock, save_id: int,
                 back: Callable[[int], T]) -> tuple[tuple[T, Stored], tuple[T, Stored], bool]:
    """`back` (what the player's return serves) on the save after an absence the job kept ahead under `rs`, then on
    that same save put back as it was and the job's work gone, at the same clock (a journal page is seeded by the
    save's id): each with what it stored, and whether the first continued what was kept."""
    with engine.connect() as conn:
        before: dict[str, Any] = dict(conn.execute(select(saves).where(saves.c.id == save_id)).mappings().one())
    away_with_jobs(engine, rs, clock)
    log, watch = logging.getLogger("ashfall.saves"), _Used()
    level = log.level
    log.setLevel(logging.INFO)
    log.addHandler(watch)
    try:
        kept = back(save_id), stored(engine, save_id)
    finally:
        log.removeHandler(watch)
        log.setLevel(level)
    with engine.begin() as conn:
        for t in (save_lines, save_journal, save_ahead, save_decisions, save_snapshots):
            conn.execute(delete(t).where(t.c.save_id == save_id))
        conn.execute(update(saves).where(saves.c.id == save_id).values({k: v for k, v in before.items() if k != "id"}))
    return kept, (back(save_id), stored(engine, save_id)), watch.used


def test_an_open_kept_ahead_writes_and_serves_what_an_open_without_it_does(
        engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    saves_ = PgSaves(engine, rs, clock, stop_for=never)
    save_id = seed_busy(engine, rs, account, clock())
    kept, plain, used = both_ways(engine, rs, clock, save_id, lambda i: served(saves_.open(account, i).played))
    assert used
    assert len(plain[0].lines) > 3 and plain[0].rule_runs, "too quiet a span to compare"
    assert plain[1][1], "no journal day was written to compare"
    assert kept == plain


def test_a_rebased_row_kept_ahead_opens_as_one_rebased_and_advanced_on_the_open(
        engine: Engine, rs: Ruleset, rs_changed: Ruleset, clock: FakeClock, account: int):
    saves_ = PgSaves(engine, rs_changed, clock, stop_for=never)

    def opened(i: int) -> tuple[e.Save, Served]:
        o = saves_.open(account, i)
        return o.was, served(o.played)
    kept, plain, used = both_ways(engine, rs_changed, clock, seed_busy(engine, rs, account, clock()), opened)
    assert used and kept == plain


def test_a_rule_the_rebase_installs_counts_in_the_runs_of_an_open_kept_ahead(engine: Engine, clock: FakeClock,
                                                                             account: int):
    old, new = installs(False), installs(True)
    with engine.begin() as conn:
        save_id = rows.insert_save(conn, account, clock(), written(e.advance(e.new_save(old.rules), old.rules, 20), 0, old))
        conn.execute(update(saves).where(saves.c.id == save_id).values(started_at=clock() - timedelta(seconds=20)))
    saves_ = PgSaves(engine, new, clock, stop_for=never)
    kept, plain, used = both_ways(engine, new, clock, save_id, lambda i: served(saves_.open(account, i).played))
    assert used and kept == plain
    assert plain[0].rule_runs, "the installed rule never came on"


def installs(on: bool) -> Ruleset:
    """A rule installed by a trigger, as in test_rebase_rule_changes: a save written without it comes on at its load."""
    a, q = e.CardId("a"), e.QUANTITY_SCALE
    t = e.TriggerDef(e.TriggerId("arrive"), e.AfterTime(10), e.Outcome(orders=(e.RuleInstall(a),)))
    r = e.Rules(stores=(e.StoreDef(e.StoreId("x"), 10 * q),), skills=(e.SkillDef(e.SkillId("k")),), standing=(),
                curve=e.PacingCurve((10 * q,)), lanes=(e.LaneDef(e.LaneId("helper"), True),),
                cards=(e.CardDef(a, 30, lane=e.LaneId("helper")),), triggers=(t,) if on else ())
    return Ruleset(rules=r, digest=e.rules_digest(r), start_lines=(), line_keys=frozenset(), build="b",
                   release=2 if on else 1)


def test_a_row_another_build_moved_is_not_continued(engine: Engine, rs: Ruleset, rs_changed: Ruleset,
                                                     clock: FakeClock, account: int):
    save_id = seed_busy(engine, rs, account, clock())
    away_with_jobs(engine, rs_changed, clock)
    PgSaves(engine, rs, clock, stop_for=lambda: lambda: True).advance(account, save_id)   # the old build, one instant
    with engine.connect() as conn:
        row = rows.save(conn, save_id, None)
        assert row is not None
        loaded = load(row, rs_changed)
        kept = kept_rows.kept(conn, save_id)
        assert kept is not None and kept.game_time > loaded.save.time   # what was kept is further on, but of the old row
        assert row.ahead_at == kept.game_time   # read, so the row is looked up
        assert ahead.continuing(conn, row, loaded, rs_changed) is None


def test_what_is_kept_goes_stale_once_the_row_moves(engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    save_id = seed_busy(engine, rs, account, clock())
    away_with_jobs(engine, rs, clock)
    saves_ = PgSaves(engine, rs, clock, stop_for=never)
    saves_.open(account, save_id)   # continues what was kept, and writes the row on from it
    clock.tick(600)
    log, watch = logging.getLogger("ashfall.saves"), _Used()
    level = log.level
    log.addHandler(watch)
    log.setLevel(logging.INFO)
    try:
        saves_.advance(account, save_id)
    finally:
        log.removeHandler(watch)
        log.setLevel(level)
    with engine.connect() as conn:
        assert kept_rows.kept(conn, save_id) is not None   # still there, of the row before the open
    assert not watch.used


def test_a_job_never_steps_back_what_a_later_release_or_a_further_job_kept(engine: Engine, rs: Ruleset,
                                                                          clock: FakeClock, account: int):
    save_id = seed_busy(engine, rs, account, clock())
    rec = kept_rows.AheadRecord(save_id, "base", rs.digest, 2, 1000, "state", [], None)
    with engine.begin() as conn:
        assert kept_rows.keep(conn, rec, clock())
        assert not kept_rows.keep(conn, replace(rec, game_time=900), clock())   # not as far
        assert not kept_rows.keep(conn, replace(rec, release=1, rules_digest="older", game_time=5000), clock())
        assert kept_rows.keep(conn, replace(rec, game_time=1100), clock())
        assert kept_rows.keep(conn, replace(rec, release=3, rules_digest="newer", game_time=10), clock())
        assert kept_rows.keep(conn, replace(rec, base="moved", release=1, game_time=5), clock())   # another row
        found = kept_rows.kept(conn, save_id)
    assert found is not None and (found.base, found.game_time) == ("moved", 5)


def test_a_save_another_job_claimed_is_passed_over(engine: Engine, rs: Ruleset, clock: FakeClock, account: int):
    save_id = seed_busy(engine, rs, account, clock())
    clock.tick(JOB_EVERY_S)
    with kept_rows.claimed(engine, save_id) as mine:
        assert mine
        assert ahead.keep(engine, lambda: rs, clock, 600.0) == 0
    assert ahead.keep(engine, lambda: rs, clock, 600.0) > 0


def test_kept_lines_read_back_as_written():
    lines = (e.Line(5, 0, e.LineKey("a"), e.CardId("c")), e.Line(5, 1, e.LineKey("b")))
    assert ahead.lines_from_json(ahead.lines_to_json(lines)) == lines
    with pytest.raises(e.StateFormatError):
        ahead.lines_from_json([[5, 0, "a"]])
