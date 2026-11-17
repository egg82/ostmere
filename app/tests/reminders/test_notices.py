"""The hands-free notice's pass of the reminders job (reminders/notices.py) over real saves: the app writes them, the job
forecasts each one a decision left without a kept answer (saves/handsfree.py `refresh`, under the shipped rules) and
sends a due notice once."""
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta

import pytest
from sqlalchemy import Engine

from ashfall_app import logs
from ashfall_app.db import handsfree as hf
from ashfall_app.db import reminders as store
from ashfall_app.reminders.notices import NoticeCounts, run_notices
from ashfall_app.reminders.run import Counts, run
from ashfall_app.reminders.sender import Delivery
from ashfall_app.reminders.words import lines
from ashfall_app.saves import handsfree
from tests.game_client import GameClient
from tests.reminders.wire import PUSH, engine_of
from tests.shipped_ruleset import ShippedRuleset

TAP = {"kind": "tap_card", "card": "stand_up"}


class Recorder:
    def __init__(self) -> None:
        self.sent: list[tuple[str, Mapping[str, str]]] = []

    def send(self, endpoint: str, p256dh: str, auth: str, payload: Mapping[str, str]) -> Delivery:
        self.sent.append((endpoint, payload))
        return Delivery("ok")


def taking(game: GameClient, hands_free: bool = True, after_hours: int | None = None) -> int:
    """A game begun on a browser whose device takes the notice; the save's id."""
    save: int = game.begin()["save"]["save_id"]
    with engine_of(game).begin() as conn:
        account = conn.exec_driver_sql("SELECT account_id FROM saves WHERE id = %s", (save,)).scalar_one()
        store.insert_device(conn, game.clock(), store.NewDevice(account, PUSH + "one", "p", "a", after_hours, "UTC", 0, 0,
                                                                hands_free=hands_free))
    return save


def refresher(engine: Engine, rs: ShippedRuleset, min_busy_s: int) -> Callable[[hf.Latest], bool]:
    return lambda latest: handsfree.refresh(engine, rs.rs, latest, min_busy_s, lambda: False)


def go(game: GameClient, rs: ShippedRuleset, sender: Recorder, now: datetime, min_busy_s: int = 0) -> NoticeCounts:
    engine = engine_of(game)
    return run_notices(engine, sender, lambda: now, refresher(engine, rs, min_busy_s))


def kept(game: GameClient) -> hf.Latest:
    with engine_of(game).connect() as conn:
        [found] = hf.latest(conn)
    return found


def test_a_decision_is_forecast_by_the_job_and_its_notice_goes_once(game: GameClient,
                                                                     shipped_ruleset: ShippedRuleset):
    save = taking(game)
    assert game.decide(save, TAP, after=0).status_code == 200
    sender, now = Recorder(), game.clock()
    assert go(game, shipped_ruleset, sender, now) == NoticeCounts(saves=1, refreshed=1)
    free = kept(game)
    assert free.at is not None and free.wall is not None and free.wall > now and sender.sent == []
    assert go(game, shipped_ruleset, sender, free.wall) == NoticeCounts(saves=1, due=1, sent=1)
    assert go(game, shipped_ruleset, sender, free.wall + timedelta(minutes=1)) == NoticeCounts(saves=1)
    [(endpoint, payload)] = sender.sent
    assert endpoint == PUSH + "one" and payload["title"] == "Ostmere" and payload["url"] == "/"
    assert payload["body"] in lines("hands_free_lines.json")


def test_no_notice_once_the_page_advanced_past_the_moment(game: GameClient, shipped_ruleset: ShippedRuleset):
    save = taking(game)
    game.decide(save, TAP, after=0)
    sender = Recorder()
    go(game, shipped_ruleset, sender, game.clock())
    free = kept(game)
    assert free.wall is not None
    game.clock.tick(seconds=60)
    assert game.advance(save).status_code == 200
    assert go(game, shipped_ruleset, sender, game.clock()) == NoticeCounts(saves=1)
    assert sender.sent == []


def test_work_given_less_than_min_busy_before_it_frees_sends_nothing(game: GameClient,
                                                                    shipped_ruleset: ShippedRuleset):
    save = taking(game)
    game.decide(save, TAP, after=0)
    sender, now = Recorder(), game.clock()
    assert go(game, shipped_ruleset, sender, now, min_busy_s=600) == NoticeCounts(saves=1, refreshed=1)
    found = kept(game)
    assert found.at is None and found.until is not None
    assert go(game, shipped_ruleset, sender, now + timedelta(hours=1), min_busy_s=600) == NoticeCounts(saves=1)
    assert sender.sent == []


def test_a_kept_answer_whose_reach_has_passed_is_forecast_again_from_there(game: GameClient,
                                                                           shipped_ruleset: ShippedRuleset):
    save = taking(game)
    game.decide(save, TAP, after=0)
    go(game, shipped_ruleset, Recorder(), game.clock(), min_busy_s=600)
    first = kept(game)
    assert first.until is not None
    later = first.started_at + timedelta(seconds=first.until + 1)
    assert go(game, shipped_ruleset, Recorder(), later, min_busy_s=600) == NoticeCounts(saves=1, refreshed=1)
    assert (kept(game).until or 0) > first.until


def test_a_device_with_the_absence_reminder_off_gets_no_reminder(game: GameClient):
    taking(game)
    engine = engine_of(game)
    assert run(engine, Recorder(), lambda: game.clock() + timedelta(days=30)) == Counts()


def test_one_line_per_pass_and_never_an_endpoint(game: GameClient, shipped_ruleset: ShippedRuleset,
                                                capsys: pytest.CaptureFixture[str]):
    logs.setup()
    save = taking(game)
    game.decide(save, TAP, after=0)
    go(game, shipped_ruleset, Recorder(), game.clock())
    out = capsys.readouterr().out
    runs = [ln for ln in out.splitlines() if "event=hands_free.run " in ln]
    assert len(runs) == 1 and " saves=1 refreshed=1 unrefreshed=0 due=0 sent=0 gone=0 failed=0 ms=" in runs[0]
    assert PUSH not in out
