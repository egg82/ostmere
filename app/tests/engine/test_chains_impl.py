"""A working's chain on a group threat (engine design/spells.txt, "SPELLS"): unit tests written beside the
implementation, one per Accept case of week-five-plan item 6. The contract tests are written blind elsewhere (item 7)."""
from collections.abc import Callable
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, AfterTime, Amount, CardDef, CardShare, ChainDef, FightDef, Flow, PacingCurve, SideDef, SideId,
    StoreDef, StoreId, ThreatDef, ThreatId, per_hour, ChainReach, InvalidRulesError, LineKey, Mix, MixId, Modifier,
    ModifierKind, Outcome, QueueEntry, Rules, Save, SaveMix, SetQueue, SourceId, SwitchMix, TapCard, TriggerDef,
    StandingDef, TriggerId, Unlock, UnlockKind, advance, advance_logged, chain_views, decide, decide_logged, decode,
    encode, new_save, rules_digest, validate_rules,
)
from ashfall_app.engine.api import Line

from tests.engine.chain_world import CHAINED, FOUGHT, JUMP, LINKS, LOST, RAID, WORK_S, world, without_chain

F6 = 6
"""Fights an hour: one every WORK_S seconds, so a cast tapped at WORK_S * j lands with exactly j + 1 fights fought."""


def _whole(save: Save, store: str) -> int:
    return next(st.segment.start_value for st in save.stores if st.store == store) // Q


def _cast(rules: Rules, at: int, save: Save | None = None) -> tuple[Save, tuple[Line, ...]]:
    """Tap the working at `at` and advance to its landing; the save and the lines of the landing instant."""
    s = decide(advance(save or new_save(rules), rules, at), rules, at, TapCard(JUMP))
    step = advance_logged(s, rules, at + WORK_S)
    return step.save, tuple(ln for ln in step.lines if ln.time == at + WORK_S)


def _links(lines: tuple[Line, ...]) -> list[LineKey]:
    return [ln.key for ln in lines if ln.card == JUMP]


@pytest.mark.parametrize("members,reach,fought", [
    (4, 3, 1), (4, 3, 2), (4, 3, 3), (4, 3, 4), (4, 3, 5), (4, 6, 1), (4, 6, 4), (2, 1, 3), (5, 5, 7), (3, 9, 9)])
def test_chain_is_min_of_due_and_reach_with_one_line_each(members: int, reach: int, fought: int) -> None:
    rules = world(members, reach, F6)
    save, lines = _cast(rules, WORK_S * (fought - 1))
    due = members - fought % members
    k = min(due, reach)
    assert _whole(save, FOUGHT) == fought
    assert _links(lines) == [LINKS[min(i, len(LINKS)) - 1] for i in range(1, k + 1)]
    assert _whole(save, CHAINED) == k


def test_a_second_cast_reads_the_links_of_the_first() -> None:
    rules = world(members=6, reach=4, fights_per_hour=F6)
    save, first = _cast(rules, 0)
    save, second = _cast(rules, save.time, save)
    assert len(_links(first)) == 4          # fought 1: 6 - 1 = 5 due, reach 4
    assert len(_links(second)) == min(6 - (2 + 4) % 6, 4) == 4   # fought 2, chained 4: a new group of 6, reach 4
    assert _whole(save, CHAINED) == 4 + len(_links(second))


def test_links_move_nothing_but_the_chained_tally() -> None:
    rules = world(members=4, reach=3, fights_per_hour=F6, side=0)
    with_chain, _ = _cast(rules, WORK_S)
    plain, _ = _cast(without_chain(rules), WORK_S)
    assert _whole(with_chain, CHAINED) == 2
    assert [st for st in with_chain.stores if st.store != CHAINED] == [st for st in plain.stores if st.store != CHAINED]
    assert _whole(with_chain, LOST) == _whole(with_chain, FOUGHT) == 2


def test_one_key_never_folds_the_links() -> None:
    rules = world(members=5, reach=5, fights_per_hour=F6, lines=(LineKey("again"),))
    _, lines = _cast(rules, 4 * WORK_S)
    assert _links(lines) == [LineKey("again")] * 5
    assert len({ln.seq for ln in lines if ln.card == JUMP}) == 5


def test_a_runner_that_is_not_fighting_owes_nothing() -> None:
    locked_raid = replace(world(members=4, reach=3, fights_per_hour=F6), opening=(Unlock(UnlockKind.CARD, JUMP),))
    save, lines = _cast(locked_raid, 0)
    assert _links(lines) == [] and _whole(save, CHAINED) == 0
    assert [ln.key for ln in lines] == []


def test_the_firing_cap_bounds_the_chain_and_counts_a_cascade() -> None:
    rules = world(members=8, reach=8, fights_per_hour=F6, max_firings=4)
    save, lines = _cast(rules, 0)
    assert len(_links(lines)) == 4 - 1      # due 7, reach 8: the completion's own firing, then three links reach the cap
    assert save.cascade_count == 1
    roomy, roomy_lines = _cast(world(members=8, reach=8, fights_per_hour=F6), 0)
    assert len(_links(roomy_lines)) == 7 and roomy.cascade_count == 0


def test_queued_and_away_lands_the_same_chain_as_watched() -> None:
    rules = world(members=4, reach=3, fights_per_hour=F6)
    watched, watched_lines = _cast(rules, WORK_S)
    s = advance(new_save(rules), rules, WORK_S)
    queued = decide(s, rules, WORK_S, SetQueue((QueueEntry(TapCard(JUMP), AfterTime(10**9)),)))
    one = advance_logged(queued, rules, 2 * WORK_S)
    sliced = queued
    lines: list[Line] = []
    for t in range(WORK_S + 37, 2 * WORK_S + 1, 113):
        step = advance_logged(sliced, rules, t)
        sliced, lines = step.save, lines + list(step.lines)
    step = advance_logged(sliced, rules, 2 * WORK_S)
    sliced, lines = step.save, lines + list(step.lines)
    assert _links(one.lines) == _links(tuple(lines)) == _links(watched_lines) == list(LINKS[:2])
    assert _whole(one.save, CHAINED) == _whole(sliced, CHAINED) == _whole(watched, CHAINED) == 2


def test_a_mixed_working_resolves_a_chain_at_each_completion() -> None:
    rules = world(members=4, reach=3, fights_per_hour=F6)
    mix = Mix(MixId("m"), (CardShare(JUMP, 10_000),))
    s = decide(decide(new_save(rules), rules, 0, SaveMix(mix)), rules, 0, SwitchMix(mix.id))
    step = advance_logged(s, rules, 3 * WORK_S)
    # completions at 600, 1200, 1800 with 1, 2 and 3 fought: due 3, then 4 - (2 + 3) % 4 = 3, then 4 - (3 + 6) % 4 = 3
    assert [ln.time for ln in step.lines if ln.card == JUMP] == [600] * 3 + [1200] * 3 + [1800] * 3
    assert _whole(step.save, CHAINED) == 9


def test_a_capped_workings_own_line_comes_before_its_links() -> None:
    rules = world(members=4, reach=2, fights_per_hour=F6, cap=2)
    _, lines = _cast(rules, 0)
    assert [ln.key for ln in lines] == [LineKey("own_1"), *LINKS[:2]]


def test_reach_shown_is_reach_run_and_a_level_pay_raises_both() -> None:
    pay = Modifier(ChainReach(JUMP), ModifierKind.ADD_BP, 5_000, SourceId("level"))
    rules = world(members=8, reach=2, fights_per_hour=F6,
                  triggers=(TriggerDef(TriggerId("level"), AfterTime(2 * WORK_S), Outcome(modifiers=(pay,))),))
    before = chain_views(advance(new_save(rules), rules, 0), rules)[0]
    _, early = _cast(rules, 0)
    later_save = advance(new_save(rules), rules, 2 * WORK_S)
    shown = chain_views(later_save, rules)[0]
    _, late = _cast(rules, 2 * WORK_S)
    assert (before.reach.value, len(_links(early))) == (2, 2)
    assert (shown.reach.value, len(_links(late))) == (3, 3)
    assert [m.source for m in shown.reach.adds] == [SourceId("level")]


def test_a_tap_shows_its_reach_before_the_tap() -> None:
    rules = world(members=8, reach=4, fights_per_hour=F6)
    step = decide_logged(advance(new_save(rules), rules, 0), rules, 0, TapCard(JUMP))
    assert chain_views(step.save, rules)[0].reach.value == 4


def _threat(members: int) -> Rules:
    r = world()
    return replace(r, threats=(replace(r.threats[0], members=members),))


def _chain(reach: int = 3, lines: tuple[LineKey, ...] = LINKS) -> Rules:
    r = world()
    return replace(r, cards=(replace(r.cards[0], chain=ChainDef(RAID, reach, lines)),))


def _untallied() -> Rules:
    r = world()
    fight = r.standing[0].fight
    assert fight is not None
    return replace(r, standing=(replace(r.standing[0], fight=replace(fight, chained=None)),))


@pytest.mark.parametrize("build,message", [
    (lambda: _threat(1), "whose threat pack is not a group"), (lambda: _threat(0), "members must be >= 1"),
    (lambda: _chain(reach=0), "reach must be >= 1"), (lambda: _chain(lines=()), "at least one line"),
    (_untallied, "no fought or chained tally"),
])
def test_validation_refuses_a_chain_that_cannot_be_exact(build: Callable[[], Rules], message: str) -> None:
    with pytest.raises(InvalidRulesError, match=message):
        validate_rules(build())


PLAIN_DIGEST = "41c9c7bdcce12730297f80ce53ad0dc4e0c1a9894e68e3a9281fb8b7754f7b7b"
"""rules_digest of the rules below, computed by the codec at the commit before chains existed."""


def test_rules_with_no_chain_keep_their_digest_and_a_reach_entry_round_trips() -> None:
    fought, lost, hair, ash = (StoreId(n) for n in ("fought", "lost", "hair", "ash"))
    plain = Rules(tuple(StoreDef(x, 10**6 * Q) for x in (fought, lost, hair, ash)), (),
                  (StandingDef(RAID, fight=FightDef(SideId("hand"), ThreatId("pack"), lost, fought, per_hour(6))),),
                  PacingCurve((10**15,)), cards=(CardDef(JUMP, 600, inputs=(Amount(hair, 2 * Q),),
                                                         makes=(Flow(ash, per_hour(1)),)),),
                  sides=(SideDef(SideId("hand"), 1),), threats=(ThreatDef(ThreatId("pack"), 1),))
    assert rules_digest(plain) == PLAIN_DIGEST
    pay = Modifier(ChainReach(JUMP), ModifierKind.MUL_BP, 20_000, SourceId("level"))
    rules = world(triggers=(TriggerDef(TriggerId("level"), AfterTime(0), Outcome(modifiers=(pay,))),))
    save = advance(new_save(rules), rules, 10)
    assert pay in save.modifiers and decode(encode(save, rules), rules) == save
