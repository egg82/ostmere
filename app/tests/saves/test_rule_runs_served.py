"""What the rules did lately through the saves service and the API's Step (CONTRACT.txt, "Rule runs"): a write keeps
the record on the save's row, built from the engine's rule changes and pruned by the save's rules, and every written
Step serves it. Rules: the opening's with everything unlocked."""
from dataclasses import replace

import pytest
from sqlalchemy import Engine

from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.saves.interface import Played, Ruleset
from ashfall_app.saves.ruleruns import RuleRun
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.opening.playthrough import opening

A = e.CardId("gather_wood")
M0 = e.MixId("m0")


@pytest.fixture
def open_rs(rs: Ruleset) -> Ruleset:
    return replace(rs, rules=replace(rs.rules, opening=None))


@pytest.fixture
def open_saves(engine: Engine, open_rs: Ruleset, clock: FakeClock) -> PgSaves:
    return PgSaves(engine, open_rs, clock)


def decide(saves: PgSaves, account: int, played: Played, clock: FakeClock, verb: e.Verb) -> Played:
    clock.tick(30)
    return saves.decide(account, played.save_id, verb, after=played.decisions)


def test_a_rule_that_comes_on_is_kept_and_served_and_an_edit_drops_it(open_saves: PgSaves, open_rs: Ruleset,
                                                                      account: int, clock: FakeClock):
    store = open_rs.rules.stores[0].id
    always = e.Order(e.AtLeast(e.StoreValue(store), 0, 0), e.SwitchMix(M0))
    _, p = open_saves.create(account)
    assert p.rule_runs == ()
    p = decide(open_saves, account, p, clock, e.SaveMix(e.Mix(M0, (e.CardShare(A, e.BP),))))
    p = decide(open_saves, account, p, clock, e.SetOrders((always,)))
    level = e.segment(p.save, open_rs.rules, store).start_value
    assert p.rule_runs == (RuleRun(always, 1, p.save.time, level),)
    clock.tick(600)
    later = open_saves.advance(account, p.save_id)
    assert later.rule_runs == p.rule_runs   # read back off the row: nothing changed since
    step = Game(opening(), open_rs).step(later)
    assert step.rule_runs == [w.RuleRun(order=w.Order(when=convert.condition(always.when),
                                                      then=convert.order_verb(always.then)),
                                        starts=1, on_at=p.save.time, on_level=level, off_at=None, off_level=None,
                                        ended=None, made=[])]
    never = e.Order(e.AfterTime(10**9), e.SwitchMix(M0))
    assert decide(open_saves, account, later, clock, e.SetOrders((never,))).rule_runs == ()   # its rule is gone
