"""How long a chain is (engine/design/spells.txt, "SPELLS": Due, Resolving, invariants 184, 185, 187, 190), written blind from
that part and api/contract/spells.txt alone. The flow runs a fight a second (per=3600) so floor(fought) at second t is t."""
from hypothesis import given, strategies as st

from ashfall_app.engine import QUANTITY_SCALE as Q, LaneDef, LaneId, advance, advance_logged, new_save, value, view
from contract_gen import few
from spells_world import (
    CHAINED, FOUGHT, LINK_KEYS, RLOST, SPELL, SPELL2, due_of, fought, kills, links, mixed, model_links, per_instant, play,
    ruled, spell, twin, world,
)

PER = 3600


def starts(gaps: list[int]) -> tuple[int, ...]:
    """Tap start times, each a tap and its 10 s of work apart from the last."""
    out: list[int] = []
    t = 0
    for g in gaps:
        t += 11 + g
        out.append(t)
    return tuple(out)


@kills(2, 3, 4, 8, 15)
@given(st.integers(2, 6), st.integers(1, 8), st.lists(st.integers(0, 9), min_size=1, max_size=7))
@few(25)
def test_each_chain_is_min_of_due_and_reach_and_the_tally_follows(m: int, reach: int, gaps: list[int]):
    r = world(m, reach, per=PER)
    taps = starts(gaps)
    s, lines = play(r, taps)
    want = model_links(r, tuple(t + 10 for t in taps), reach, m)
    assert per_instant(lines) == want
    assert value(s, r, CHAINED, s.time) == Q * sum(k for _, k in want)


@kills(2)
def test_a_chain_longer_than_the_group_ends_the_group_exactly():
    """Fought 10 by t=10, a group of 3: the member under way is the 2nd of its group, so 2 are due; the reach is 10."""
    r = world(3, 10, per=PER)
    s, lines = play(r, (0,))
    assert fought(r, 10) == 10 and due_of(3, 10, 0) == 2
    assert per_instant(lines) == [(10, 2)]
    assert (fought(r, 10) + value(s, r, CHAINED, 10) // Q) % 3 == 0


@kills(4)
def test_the_member_being_fought_counts_in_due():
    """Fought 11 in a group of 3: 11 mod 3 = 2, so 1 is due (the one under way); fought 12: a whole group of 3 is due."""
    r = world(3, 10, per=PER)
    assert per_instant(play(r, (1,))[1]) == [(11, 1)]
    assert per_instant(play(r, (2,))[1]) == [(12, 3)]


@kills(3)
def test_due_reads_the_links_already_resolved_not_only_the_flow():
    """Group of 3, reach 5: fought 11 leaves 1 due and the chain takes it; at fought 21 the group count is 21 + 1 = 22,
    so 2 are due (the flow alone would say 3). Likewise a group of 5: 4 due at 11, then 4 again at 22 (22 + 4 = 26)."""
    assert per_instant(play(world(3, 5, per=PER), (1, 11))[1]) == [(11, 1), (21, 2)]
    assert per_instant(play(world(5, 5, per=PER), (1, 12))[1]) == [(11, 4), (22, 4)]


def test_a_reach_under_the_due_ends_at_the_reach():
    r = world(6, 2, per=PER)
    assert fought(r, 12) == 12 and due_of(6, 12, 0) == 6
    assert per_instant(play(r, (2,))[1]) == [(12, 2)]


@kills(5)
def test_a_runner_that_is_not_fighting_resolves_no_link():
    """Its fought tally stands at its cap from second 5; the completion at 20 finds it not fighting: nothing lands and the
    chained tally stays 0. Control: the same world with the completion before the cap does chain."""
    r = world(4, 5, per=PER, fought_cap=5 * Q, work_s=2)
    s, lines = play(r, (18,))
    assert links(lines) == [] and value(s, r, CHAINED, s.time) == 0 and s.time == 20
    s, lines = play(r, (1,))
    assert fought(r, 3) == 3 and per_instant(lines) == [(3, 1)]


@kills(13, 14)
def test_a_chain_moves_no_store_of_its_runner_but_the_chained_tally():
    """Invariant 187: fought, lost and every other store equal those of the same save with the chain taken off."""
    r = world(4, 3, per=PER)
    s, lines = play(r, (0, 11, 22))
    t = twin(r)
    s0 = advance(new_save(t), t, s.time)
    assert links(lines)
    for store in (FOUGHT, RLOST):
        assert value(s, r, store, s.time) == value(s0, t, store, s.time)
    assert view(s, r).fights[0].fought == view(s0, t).fights[0].fought
    assert view(s, r).fights[0].lost == view(s0, t).fights[0].lost
    assert view(s, r).fights[0].loss_bp == view(s0, t).fights[0].loss_bp


@kills(13, 14)
def test_a_link_is_in_neither_fought_nor_lost():
    r = world(4, 3, per=PER)
    s, _ = play(r, (0,))
    assert value(s, r, FOUGHT, 10) == 10 * Q
    assert value(s, r, RLOST, 10) <= value(s, r, FOUGHT, 10)
    assert value(s, r, RLOST, 10) == value(advance(new_save(twin(r)), twin(r), 10), twin(r), RLOST, 10)


def test_odds_do_not_move_due_lost_fights_are_fought_fights():
    """A side of strength 0 loses every fight, a strong one wins nearly all; the chain is the same."""
    weak, strong = world(3, 10, per=PER, side=0), world(3, 10, per=PER, side=10**6)
    assert per_instant(play(weak, (1, 12))[1]) == per_instant(play(strong, (1, 12))[1]) == [(11, 1), (22, 1)]


@kills(16)
def test_two_chains_at_one_instant_share_one_due_the_second_reads_what_the_first_left():
    """Two spells at half a mix each complete together at 20: fought 20 in a group of 5 makes 5 due. The first (reach 1)
    resolves 1; the second (reach 5) then finds 4 due, not 5."""
    cards = (spell(10, 1, LINK_KEYS[:1]), spell(10, 5, LINK_KEYS[1:2], card_id=SPELL2))
    r = world(5, cards=cards, per=PER)
    s = mixed(r, {SPELL: 5000, SPELL2: 5000})
    step = advance_logged(s, r, 20)
    first, second = links(step.lines, SPELL, LINK_KEYS[:1]), links(step.lines, SPELL2, LINK_KEYS[1:2])
    assert (len(first), len(second)) == (1, 4) and all(x.time == 20 for x in (*first, *second))
    assert max(x.seq for x in first) < min(x.seq for x in second)
    assert value(step.save, r, CHAINED, 20) == 5 * Q


@kills(17)
def test_a_mixed_completion_chains_each_time_and_a_long_stretch_equals_its_slices():
    """The mix runs the spell at its whole share; each completion (every 10 s) resolves its chain, one advance or many."""
    r = world(4, 3, per=PER)
    s = mixed(r, {SPELL: 10_000})
    whole = advance_logged(s, r, 100)
    assert per_instant(whole.lines) == model_links(r, tuple(range(10, 101, 10)), 3, 4)
    a = advance_logged(s, r, 37)
    b = advance_logged(a.save, r, 61)
    c = advance_logged(b.save, r, 100)
    assert (*a.lines, *b.lines, *c.lines) == whole.lines and c.save == whole.save


@kills(18)
def test_a_chain_never_repeats_as_a_rate_each_landing_is_an_event():
    """The spell on a ruled lane, tapped again by a rule at every landing, resolves a chain at each of its completions."""
    lane = LaneId("L")
    r = world(4, 3, per=PER, lanes=(LaneDef(lane, True),), cards=(spell(10, 3, lane=lane),))
    s = ruled(r)
    step = advance_logged(s, r, 100)
    assert per_instant(step.lines) == model_links(r, tuple(range(10, 101, 10)), 3, 4)
    assert len(per_instant(step.lines)) == 10


def test_after_a_chain_of_the_due_links_the_next_group_starts_whole():
    """After a chain of the due links, F + C is a multiple of the group size: the next completion at the same fought
    count would find the whole group due."""
    r = world(3, 10, per=60, work_s=60)
    s, _ = play(r, (0,))
    f, c = fought(r, 60), value(s, r, CHAINED, 60) // Q
    assert due_of(3, f, c) == 3
