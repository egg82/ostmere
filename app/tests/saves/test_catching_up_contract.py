"""A long absence catches up in bounded slices, one per request (saves/interface.py: Played.catching_up_to, Behind):
open, advance and decide each do one slice; a decision never lands on a save that is behind; repeated advances end
where one unbounded advance of the same save ends. The clock is fixed at one `now`, so every slice aims at one time."""
import pytest
from sqlalchemy import Engine

from ashfall_app import engine as e
from ashfall_app.db import saves as rows
from ashfall_app.saves.interface import Behind, Played, Ruleset, Stale
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.saves.behind import AWAY_S, SAVED_AT, seed, snapshot
from tests.saves.chunks import MakeStop, Stop, always, every, irregular, never

VERB = e.SetOrders(())
"""Valid on the seeded save, which holds orders; a save it was applied to differs from one it was not."""
CAP = 400


def service(engine: Engine, rs: Ruleset, clock: FakeClock, make_stop: MakeStop) -> PgSaves:
    return PgSaves(engine, rs, clock, stop_for=make_stop)


def unbounded(engine: Engine, rs: Ruleset, clock: FakeClock) -> PgSaves:
    return service(engine, rs, clock, never)


def caught_up(saves: PgSaves, account: int, save_id: int) -> list[Played]:
    """Advances until one is not catching up; each slice before the last aims at one time and gets nearer it."""
    slices: list[Played] = []
    for _ in range(CAP):
        slices.append(saves.advance(account, save_id))
        if slices[-1].catching_up_to is None:
            return slices
    raise AssertionError(f"still catching up after {CAP} requests")


def stored_row(engine: Engine, save_id: int) -> rows.SaveRecord:
    with engine.connect() as conn:
        row = rows.save(conn, save_id, None)
    assert row is not None
    return row


@pytest.fixture
def behind(engine: Engine, rs: Ruleset, clock: FakeClock, account: int) -> tuple[int, int]:
    """A save at game time SAVED_AT with the clock AWAY_S on; and an identical twin to compare with."""
    first, twin = seed(engine, rs, account, clock()), seed(engine, rs, account, clock())
    clock.tick(AWAY_S)
    return first, twin


def test_an_advance_is_one_slice_that_names_the_time_it_is_heading_for(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                                      account: int, behind: tuple[int, int]):
    save_id, _ = behind
    played = service(engine, rs, clock, every(5)).advance(account, save_id)
    assert played.catching_up_to == AWAY_S
    assert SAVED_AT < played.save.time < AWAY_S
    row = stored_row(engine, save_id)
    assert row.game_time == played.save.time and e.decode(row.state, rs.rules) == played.save
    assert played.lines, "a slice of five instants brought no line: nothing to compare"
    assert snapshot(engine, save_id)[-1] == [(ln.time, str(ln.key)) for ln in played.lines]


@pytest.fixture
def both_caught_up(engine: Engine, rs: Ruleset, clock: FakeClock, account: int, behind: tuple[int, int],
                   make_stop: MakeStop) -> tuple[list[Played], Played]:
    """The save advanced in slices under the stop, its twin in one advance, in setup."""
    save_id, twin_id = behind
    return (caught_up(service(engine, rs, clock, make_stop), account, save_id),
            unbounded(engine, rs, clock).advance(account, twin_id))


@pytest.mark.parametrize("make_stop", [always, every(7), irregular(3), irregular(5, 0.7)],
                         ids=["every-1", "every-7", "irregular-3", "irregular-5"])
def test_repeated_advances_end_where_one_unbounded_advance_does(engine: Engine, behind: tuple[int, int],
                                                               make_stop: MakeStop,
                                                               both_caught_up: tuple[list[Played], Played]):
    save_id, twin_id = behind
    slices, whole = both_caught_up
    assert whole.catching_up_to is None and whole.save.time == AWAY_S
    assert len(slices) > 1 and all(s.catching_up_to == AWAY_S for s in slices[:-1])
    times = [s.save.time for s in slices]
    assert times == sorted(set(times)) and times[-1] == AWAY_S
    assert snapshot(engine, save_id) == snapshot(engine, twin_id)
    assert [(ln.time, ln.key, ln.card) for s in slices for ln in s.lines] == [
        (ln.time, ln.key, ln.card) for ln in whole.lines]
    assert slices[-1].save == whole.save and slices[-1].rule_runs == whole.rule_runs


def test_a_request_that_catches_up_is_not_catching_up(engine: Engine, rs: Ruleset, clock: FakeClock, account: int,
                                                     behind: tuple[int, int]):
    save_id, twin_id = behind
    played = service(engine, rs, clock, every(10_000)).advance(account, save_id)
    assert played.catching_up_to is None and played.save.time == AWAY_S
    unbounded(engine, rs, clock).advance(account, twin_id)
    assert snapshot(engine, save_id) == snapshot(engine, twin_id)
    again = service(engine, rs, clock, always).advance(account, save_id)
    assert again.catching_up_to is None, "nothing left to resolve is caught up, whatever the stop says"


def test_open_does_the_first_slice_and_was_stays_the_view_as_last_written(engine: Engine, rs: Ruleset,
                                                                         clock: FakeClock, account: int,
                                                                         behind: tuple[int, int]):
    save_id, twin_id = behind
    sliced = service(engine, rs, clock, every(5))
    before = e.decode(stored_row(engine, save_id).state, rs.rules)
    opened = sliced.open(account, save_id)
    assert opened.was == before and opened.was.time == SAVED_AT
    assert opened.played.catching_up_to == AWAY_S and SAVED_AT < opened.played.save.time < AWAY_S
    assert opened.info.game_time == opened.played.save.time and opened.played.lines
    again = sliced.open(account, save_id)   # the page was shut mid-catch-up: it sees what the last slice wrote
    assert again.was == opened.played.save
    assert [p.key for p in again.history][-len(opened.played.lines):] == [str(ln.key) for ln in opened.played.lines]
    rest = caught_up(sliced, account, save_id)
    unbounded(engine, rs, clock).advance(account, twin_id)
    assert rest[-1].catching_up_to is None and snapshot(engine, save_id) == snapshot(engine, twin_id)


def test_stop_for_is_asked_once_a_request(engine: Engine, rs: Ruleset, clock: FakeClock, account: int,
                                         behind: tuple[int, int]):
    save_id, _ = behind
    asked: list[int] = []

    def make() -> Stop:
        asked.append(1)
        return every(5)()

    sliced = service(engine, rs, clock, make)
    sliced.open(account, save_id)
    assert len(asked) == 1
    sliced.advance(account, save_id)
    assert len(asked) == 2
    with pytest.raises(Behind):
        sliced.decide(account, save_id, VERB, after=0)
    assert len(asked) == 3


def test_a_decision_on_a_save_that_is_behind_writes_the_slice_and_not_the_verb(engine: Engine, rs: Ruleset,
                                                                              clock: FakeClock, account: int,
                                                                              behind: tuple[int, int]):
    save_id, twin_id = behind
    sliced = service(engine, rs, clock, every(5))
    with pytest.raises(Behind) as behind_it:
        sliced.decide(account, save_id, VERB, after=0)
    played = behind_it.value.played
    assert played.decisions == 0 and played.catching_up_to == AWAY_S and SAVED_AT < played.save.time < AWAY_S
    row = stored_row(engine, save_id)
    assert row.decisions == 0 and row.game_time == played.save.time
    with engine.connect() as conn:
        assert rows.decisions_after(conn, save_id, 0) == [], "the verb was logged"
    sliced.advance(account, twin_id)   # the same slice, as a plain advance
    assert snapshot(engine, save_id) == snapshot(engine, twin_id), "the verb changed the save"
    assert e.decode(row.state, rs.rules).orders != (), "the verb was applied"


def test_a_decision_lands_once_the_save_has_caught_up(engine: Engine, rs: Ruleset, clock: FakeClock, account: int,
                                                     behind: tuple[int, int]):
    save_id, _ = behind
    sliced = service(engine, rs, clock, every(5))
    with pytest.raises(Behind):
        sliced.decide(account, save_id, VERB, after=0)
    caught_up(sliced, account, save_id)
    played = sliced.decide(account, save_id, VERB, after=0)
    assert played.decisions == 1 and played.catching_up_to is None and played.save.orders == ()
    assert stored_row(engine, save_id).decisions == 1


def test_a_decision_on_a_save_not_behind_is_unchanged_by_the_stop(engine: Engine, rs: Ruleset, clock: FakeClock,
                                                                 account: int):
    sliced = service(engine, rs, clock, every(10_000))
    info, made = sliced.create(account)
    assert made.catching_up_to is None
    clock.tick(2)
    played = sliced.decide(account, info.save_id, e.TapCard(e.CardId("stand_up")), after=0)
    assert played.catching_up_to is None and played.decisions == 1
    clock.tick(100)
    with pytest.raises(Stale) as stale:
        sliced.decide(account, info.save_id, e.TapCard(e.CardId("stand_up")), after=0)
    assert stale.value.played.catching_up_to is None


def test_a_dry_run_on_a_save_that_is_behind_is_refused_and_writes_nothing(engine: Engine, rs: Ruleset,
                                                                         clock: FakeClock, account: int,
                                                                         behind: tuple[int, int]):
    save_id, _ = behind
    sliced = service(engine, rs, clock, every(5))
    before, row = snapshot(engine, save_id), stored_row(engine, save_id)
    with pytest.raises(Behind):
        sliced.dry_run(account, save_id, (VERB,))
    assert snapshot(engine, save_id) == before and stored_row(engine, save_id) == row
    caught_up(sliced, account, save_id)
    assert sliced.dry_run(account, save_id, (VERB,)).orders == ()
    assert snapshot(engine, save_id)[2] == 0, "a dry run is not a decision"
