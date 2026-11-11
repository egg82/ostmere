"""Repeats through the saves service and the API's Step (CONTRACT.txt, "Repeats"): each decision's context is logged
as it is made, and every written Step serves the counts read back from the log. Rules: the opening's with everything
unlocked, and its own [repeat_offers]."""
from dataclasses import replace

import pytest
from sqlalchemy import Engine

from ashfall_app import engine as e
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.db import saves as rows
from ashfall_app.saves.interface import Played, Ruleset
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.opening.playthrough import opening

A, B = e.CardId("gather_wood"), e.CardId("scavenge")
M0, M1 = e.MixId("m0"), e.MixId("m1")


@pytest.fixture
def open_rs(rs: Ruleset) -> Ruleset:
    return replace(rs, rules=replace(rs.rules, opening=None))


@pytest.fixture
def open_saves(engine: Engine, open_rs: Ruleset, clock: FakeClock) -> PgSaves:
    return PgSaves(engine, open_rs, clock)


def decide(saves: PgSaves, account: int, played: Played, clock: FakeClock, verb: e.Verb, wait: int = 30) -> Played:
    clock.tick(wait)
    return saves.decide(account, played.save_id, verb, after=played.decisions)


def test_the_nth_tap_outside_the_running_mix_is_served(open_saves: PgSaves, open_rs: Ruleset, account: int,
                                                       clock: FakeClock, engine: Engine):
    r = open_rs.repeats
    assert r is not None and r.hand_taps >= 2
    _, p = open_saves.create(account)
    p = decide(open_saves, account, p, clock, e.SaveMix(e.Mix(M0, (e.CardShare(A, e.BP),))))
    p = decide(open_saves, account, p, clock, e.SwitchMix(M0))
    for _ in range(r.hand_taps - 1):
        p = decide(open_saves, account, p, clock, e.TapCard(B))
        p = decide(open_saves, account, p, clock, e.TapCard(A))   # in the mix: never counted
    assert p.failed is None and p.repeats.taps == ()
    p = decide(open_saves, account, p, clock, e.TapCard(B))
    assert p.repeats.taps == ((B, r.hand_taps),)
    step = Game(opening(), open_rs).step(p)
    assert step.repeats == w.Repeats(taps=[w.RepeatedTap(card=B, count=r.hand_taps)], switches=[])
    with engine.connect() as conn:
        logged = rows.decisions_after(conn, p.save_id, 0)
    assert len(logged) == p.decisions and all(d.context is not None for d in logged)
    clock.tick(r.hand_taps_within_s)
    assert open_saves.advance(account, p.save_id).repeats.taps == ()   # the window moved past the first tap


def test_a_repeated_switch_under_a_chip_is_served(open_saves: PgSaves, open_rs: Ruleset, account: int,
                                                  clock: FakeClock):
    r = open_rs.repeats
    assert r is not None
    _, p = open_saves.create(account)
    for m, card in ((M0, A), (M1, B)):
        p = decide(open_saves, account, p, clock, e.SaveMix(e.Mix(m, (e.CardShare(card, e.BP),))))
    for _ in range(r.switches):
        p = decide(open_saves, account, p, clock, e.SwitchMix(M0), wait=5)
        p = decide(open_saves, account, p, clock, e.SwitchMix(M1), wait=5)
    chips = e.view(p.save, open_rs.rules).chips
    assert chips   # control: a chip shows, so the switches count
    assert {(chip, mix) for chip, mix, n in p.repeats.switches if n == r.switches} >= {(chips[0], M0), (chips[0], M1)}
