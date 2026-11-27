"""A chain is no chance and no clock (engine/design/spells.txt, "SPELLS": Determinism, Same instant; invariants 81, 189),
written blind from that part alone."""
import random

from hypothesis import given, strategies as st

from ashfall_app.engine import TapCard, advance_logged, decide_logged, new_save
from contract_gen import few
from spells_world import SPELL, kills, links, play, world

PER = 3600
TAPS = (0, 11, 22)


def sliced(cuts: list[int]):
    """The taps fixed, the advances cut at `cuts`: the final save and every line."""
    r = world(3, 2, per=PER)
    s, lines, now = new_save(r), [], 0
    for mark in sorted({*cuts, *TAPS, 32}):
        if mark > now:
            step = advance_logged(s, r, mark)
            s, lines, now = step.save, lines + list(step.lines), mark
        if mark in TAPS:
            step = decide_logged(s, r, mark, TapCard(SPELL))
            s, lines = step.save, lines + list(step.lines)
    return s, lines


@kills(8)
@given(st.lists(st.integers(0, 32), max_size=6))
@few(20)
def test_any_slicing_of_the_advances_gives_the_same_save_and_the_same_lines(cuts: list[int]):
    assert sliced(cuts) == sliced([])


@kills(8)
def test_a_chain_does_not_read_the_modules_random_state_or_the_wall_clock():
    r = world(40, 30, per=PER)
    outcomes = []
    for seed in (1, 2, 3, 99):
        random.seed(seed)
        s, lines = play(r, (0, 11, 22))
        outcomes.append((s, [(x.time, x.seq, x.key, x.card) for x in lines]))
    assert all(o == outcomes[0] for o in outcomes) and links(play(r, (0,))[1])


@kills(8)
def test_a_chain_is_exact_not_a_draw_the_same_state_gives_the_same_length_every_time():
    r = world(40, 30, per=PER)
    lengths = {len(links(play(r, (0,))[1])) for _ in range(12)}
    assert lengths == {30}
