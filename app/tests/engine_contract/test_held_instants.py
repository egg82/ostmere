"""Invariants 112 and 113 (engine DESIGN.txt, "ENTRIES HELD WHILE A CARD RUNS": "Instants"): the held entries change only
at the instants where a tap, a running mix, a pause, a card's Run, the unlock set or a greying changes, so a fight's odds
move at exactly those instants; and timing does not matter, invariant 81's shape, with a held card in the running town
mix and a fight on its side."""
from collections.abc import Callable

import pytest
from hypothesis import given, strategies as st

from ashfall_app.engine import (
    BP, CardShare, Mix, Rules, Save, SaveMix, TapCard, advance, decide, encode, next_event, value, view,
)
from held_world import (
    FOOD, FOUGHT, GA, GA2, GAC, GDRY, GH, GREQ, HF, HM, RLOST, STASH, flat, hands, held_mods, ja, kills, loss, odds_loss,
    town, world,
)
from contract_gen import few
from town_mix_world import TM, TOWN_RULE, always, orders


def state_key(s: Save, r: Rules) -> tuple[object, ...]:
    """Everything invariant 112 allows a held entry to follow: taps, mixes, pauses, unlocks, greying and each card's Run."""
    v = view(s, r)
    return (s.lanes, s.mixes, s.active, s.latches, s.pauses, s.unlocked, v.greyed_mixes, tuple(c.run for c in v.cards))


def instants(s: Save, r: Rules, n: int) -> list[Save]:
    out = [s]
    for _ in range(n):
        ev = next_event(out[-1], r)
        if ev is None:
            break
        out.append(advance(out[-1], r, ev.time))
    return out


def _dry() -> tuple[Rules, Save]:
    r = world(drain=FOOD)
    return r, hands(r, (GDRY, BP))


def _requires() -> tuple[Rules, Save]:
    r = world()
    return r, hands(r, (GREQ, BP))


def _town() -> tuple[Rules, Save]:
    """ga and ga2 at shares on la, and la's capped gac taps for 20 s first (a yield, a landing)."""
    r = world((ja(),))
    s = decide(town(r, (GA, 4000), (GA2, 3000)), r, 0, orders(TOWN_RULE, always(GAC)))
    return r, s


@kills(22)
@given(probe=st.floats(0, 1), scenario=st.sampled_from([_town, _dry, _requires]))
def test_between_instants_the_held_entries_do_not_move(probe: float, scenario: Callable[[], tuple[Rules, Save]]):
    """For s.time <= t < the next instant, advance(s, t) holds the entries s holds."""
    r, s = scenario()
    seq = instants(s, r, 8)
    assert len(seq) > 2
    for a in seq[:-1]:
        ev = next_event(a, r)
        assert ev is not None
        t = a.time + int(probe * (ev.time - a.time - 1))
        assert held_mods(advance(a, r, t), r) == held_mods(a, r), (a.time, t)


@kills(22)
@pytest.mark.parametrize("scenario", [_town, _dry, _requires])
def test_a_held_entry_changes_only_where_a_task_a_mix_a_pause_a_run_the_unlocks_or_a_greying_changes(
        scenario: Callable[[], tuple[Rules, Save]]):
    """Event by event, the held entries differ between consecutive instants only where the state invariant 112 lists
    differs."""
    r, s = scenario()
    seq = instants(s, r, 12)
    assert len(seq) > 3
    for a, b in zip(seq, seq[1:]):
        if held_mods(a, r) != held_mods(b, r):
            assert state_key(a, r) != state_key(b, r), (a.time, b.time)


@kills(1, 3, 4, 14)
def test_a_share_change_moves_a_standing_fights_odds_at_that_instant_and_at_no_other_time():
    """ga at 4000 holds 1600; a SaveMix of the running town mix to 8000 at 30 makes it 3200: the raid's loss_bp is
    odds_loss(1600) through 29 and odds_loss(3200) from 30 on, nowhere else."""
    r = world((ja(),))
    s = town(r, (GA, 4000))
    s = decide(advance(s, r, 30), r, 30, SaveMix(Mix(TM, (CardShare(GA, 8000),))))
    before, after = odds_loss(flat(4000, 4000)), odds_loss(flat(4000, 8000))
    assert before != after
    base = town(r, (GA, 4000))
    for t in (0, 1, 15, 29):
        assert loss(advance(base, r, t), r) == before
    for t in (30, 31, 500):
        assert loss(advance(s, r, t), r) == after, t


@kills(1, 3, 4, 14, 22)
def test_a_mixed_fights_odds_move_at_the_instant_a_guard_in_its_mix_changes_share():
    """hf (a fight card on g) shares the hands' mix with gh: it reads the live stack, so its loss_bp moves at the
    instant gh's share does, and at no other time."""
    r = world()
    s = hands(r, (HF, 3000), (GH, 3000))
    edit = decide(advance(s, r, 40), r, 40, SaveMix(Mix(HM, (CardShare(HF, 3000), CardShare(GH, 6000)))))

    def hf_loss(x: Save) -> int:
        return next(f.loss_bp for f in view(x, r).fights if f.runner == HF)

    assert [hf_loss(advance(s, r, t)) for t in (0, 20, 39)] == [odds_loss(flat(5000, 3000))] * 3
    assert [hf_loss(advance(edit, r, t)) for t in (40, 41, 300)] == [odds_loss(flat(5000, 6000))] * 3


def scenario_save(r: Rules, shares: tuple[int, int], at: tuple[int, int]) -> Callable[[Callable[[Save, int], Save]], Save]:
    """The decisions of invariant 113's scenario: la joins at 0 with ga, a SaveMix at at[0], a tap of the hands' guard at
    at[1]; `step` is how the caller reaches each time (one advance, or slices with reads between)."""
    def play(step: Callable[[Save, int], Save]) -> Save:
        s = step(town(r, (GA, shares[0])), at[0])
        s = decide(s, r, at[0], SaveMix(Mix(TM, (CardShare(GA, shares[1]), CardShare(GA2, BP - shares[1])))))
        s = step(s, at[1])
        return decide(s, r, at[1], TapCard(GH))
    return play


@few(12)
@given(shares=st.tuples(st.integers(1, BP), st.integers(1, BP)), at=st.tuples(st.integers(1, 400), st.integers(401, 900)),
       cuts=st.lists(st.integers(1, 1500), min_size=1, max_size=5), end=st.integers(901, 4000))
def test_timing_does_not_matter_with_a_held_card_in_the_running_town_mix(
        shares: tuple[int, int], at: tuple[int, int], cuts: list[int], end: int):
    """Invariant 113: the same decisions at the same times, reached by one advance or by slices with views and
    snapshots between them, give equal saves at `end`, the tallies included."""
    r = world((ja(),))
    play = scenario_save(r, shares, at)

    def direct(s: Save, t: int) -> Save:
        return advance(s, r, t)

    def sliced(s: Save, t: int) -> Save:
        for c in sorted({min(s.time + c, t) for c in cuts}):
            s = advance(s, r, c)
            view(s, r)
            encode(s, r)
        return advance(s, r, t)

    a, b = play(direct), play(sliced)
    assert a == b
    a, b = advance(a, r, end), advance(b, r, end)
    assert a == b
    assert [value(a, r, x, end) for x in (RLOST, FOUGHT, STASH)] == [value(b, r, x, end) for x in (RLOST, FOUGHT, STASH)]
