"""The Mixes list's numbers and the player's own earlier best per goal (contract/mix-rows.txt, "Mix rows"; saves/mixbest.py):
each saved mix on separate numbers, the kept best per goal naming the mix that set it, a later mix that does worse
leaving it be, and the best read back from the row by a fresh service. Rules: the opening's with everything unlocked."""
from dataclasses import replace

import pytest
from sqlalchemy import Engine

from ashfall_app import engine as e
from ashfall_app.api.rules.mixrows import goal_key
from ashfall_app.api.service import Game
from ashfall_app.rules.schema import Opening
from ashfall_app.saves.interface import Played, Ruleset
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock

A, B = e.CardId("gather_wood"), e.CardId("scavenge")
FAST, SLOW, OTHER = e.MixId("fast"), e.MixId("slow"), e.MixId("other")


@pytest.fixture(scope="module")
def game(rs: Ruleset, shipped_opening: Opening) -> Game:
    """Built once for the module's tests; they only read it."""
    return Game(shipped_opening, replace(rs, rules=replace(rs.rules, opening=None)))


@pytest.fixture
def open_saves(engine: Engine, rs: Ruleset, game: Game, clock: FakeClock) -> PgSaves:
    return PgSaves(engine, replace(rs, rules=replace(rs.rules, opening=None), mix_marks=game.mixes.marks), clock)


def save_mix(saves: PgSaves, account: int, p: Played, clock: FakeClock, mix: e.Mix) -> Played:
    clock.tick(30)
    return saves.decide(account, p.save_id, e.SaveMix(mix), after=p.decisions)


def test_two_saved_mixes_have_separate_numbers_and_the_best_names_its_mix(open_saves: PgSaves, game: Game, account: int,
                                                                          clock: FakeClock):
    _, p = open_saves.create(account)
    p = save_mix(open_saves, account, p, clock, e.Mix(FAST, (e.CardShare(A, e.BP),)))
    p = save_mix(open_saves, account, p, clock, e.Mix(OTHER, (e.CardShare(B, e.BP),)))
    answer = game.mixes.rows(p, open_saves.mix_best(account, p.save_id))
    assert [r.id for r in answer.rows] == ["fast", "other"]
    fast, other = answer.rows
    assert [(g.lands_at, g.per_hour) for g in fast.goals] != [(g.lands_at, g.per_hour) for g in other.goals]
    kept = {b.goal: b for b in answer.best}
    assert kept["level||scavenging|2"].mix_id == "other"   # only the scavenging mix lands it
    assert kept["store|catch||3600000"].mix_id == "fast"   # both land it at once: the earlier mix keeps it
    for r in answer.rows:
        for g in r.goals:
            if g.lands_at is not None and g.lands_at > p.save.time:
                assert kept[goal_key(g)].lands_at <= g.lands_at


def test_a_later_mix_that_lands_a_goal_later_leaves_the_best_and_a_fresh_service_reads_it(
        open_saves: PgSaves, engine: Engine, account: int, clock: FakeClock, rs: Ruleset):
    scavenging = "level||scavenging|2"
    _, p = open_saves.create(account)
    p = save_mix(open_saves, account, p, clock, e.Mix(OTHER, (e.CardShare(B, e.BP),)))
    first = {b.goal: b for b in open_saves.mix_best(account, p.save_id)}
    assert first[scavenging].mix == "other"
    p = save_mix(open_saves, account, p, clock, e.Mix(SLOW, (e.CardShare(A, e.BP // 4), e.CardShare(B, 3 * e.BP // 4))))
    after = {b.goal: b for b in open_saves.mix_best(account, p.save_id)}
    assert after[scavenging] == first[scavenging]   # slow lands it later: the earlier mix keeps it
    p = save_mix(open_saves, account, p, clock, e.Mix(OTHER, (e.CardShare(B, e.BP // 2), e.CardShare(A, e.BP // 2))))
    assert {b.goal: b for b in open_saves.mix_best(account, p.save_id)}[scavenging] == first[scavenging]
    reopened = PgSaves(engine, replace(rs, rules=replace(rs.rules, opening=None)), clock)
    assert reopened.mix_best(account, p.save_id) == open_saves.mix_best(account, p.save_id)
