"""The lines a chain emits and the firing room it runs in (engine/design/spells.txt, "SPELLS": Resolving, Completion,
Answers to the blind tests' questions; invariant 190), written blind from that part and api/contract/spells.txt alone."""
from collections.abc import Sequence

from ashfall_app.engine import Line, LineKey
from spells_world import LINK_KEYS, SPELL, TAP, kills, links, model_links, per_instant, play, world

PER = 3600
A, B, C = LINK_KEYS
OWNS = (LineKey("own1"), LineKey("own2"), LineKey("own3"))


def at(lines: Sequence[Line], t: int) -> list[Line]:
    return [x for x in lines if x.time == t]


@kills(9, 10, 21)
def test_each_link_is_a_line_of_its_own_and_link_i_reads_the_list_at_min_i_n():
    """A group of 5 at fought 10 makes 5 due; the reach is 5; two keys: a, b, b, b, b, one line each."""
    r = world(5, 5, (A, B), per=PER)
    _, lines = play(r, (0,))
    got = at(lines, 10)
    assert [x.key for x in got] == [A, B, B, B, B] and all(x.card == SPELL for x in got)
    assert [x.seq for x in got] == sorted({x.seq for x in got}) and len({x.seq for x in got}) == 5


@kills(9, 10)
def test_more_keys_than_links_use_the_first_ones_and_one_key_serves_every_link_without_a_repeat_dropped():
    _, lines = play(world(5, 2, (A, B, C), per=PER), (0,))
    assert [x.key for x in links(lines)] == [A, B]
    _, lines = play(world(3, 3, (A,), per=PER), (2,))
    assert [x.key for x in links(lines)] == [A, A, A]


@kills(24, 25)
def test_an_uncapped_tapped_cards_links_come_before_its_own_tap_line():
    r = world(5, 3, (A,), per=PER, own=(TAP,))
    _, lines = play(r, (0,))
    assert [x.key for x in at(lines, 10)] == [A, A, A, TAP]


@kills(19, 20)
def test_a_capped_cards_own_line_comes_first_and_every_completion_chains():
    """Each of a capped card's completions, tapped, lands its own line then its chain, up to the cap."""
    r = world(3, 2, (A,), per=PER, cap=3, own=OWNS)
    taps = (0, 11, 22)
    _, lines = play(r, taps)
    want = model_links(r, (10, 21, 32), 2, 3)
    assert per_instant(lines) == want
    for i, (t, k) in enumerate(want):
        assert [x.key for x in at(lines, t)] == [OWNS[i], *[A] * k]


@kills(11, 12)
def test_the_firing_room_bounds_a_chain_by_the_completion_and_its_links():
    """Fought 10 in a group of 50, reach 20: 40 due. With room c the completion is one firing, so k = c - 1 at most."""
    for c in (2, 6, 21, 22, 40):
        r = world(50, 20, per=PER, max_firings=c)
        _, lines = play(r, (0,))
        assert per_instant(lines) == model_links(r, (10,), 20, 50) == [(10, min(20, c - 1))]


def test_a_chain_that_fills_the_room_makes_the_instant_a_cascade_and_one_that_does_not_does_not():
    full, roomy = world(50, 20, per=PER, max_firings=6), world(50, 20, per=PER, max_firings=30)
    s, _ = play(full, (0,))
    assert s.cascade_count == 1 and s.last_cascade is not None and s.last_cascade.time == 10
    s, _ = play(roomy, (0,))
    assert s.cascade_count == 0 and s.last_cascade is None


@kills(11, 12)
def test_with_no_room_the_completion_lands_as_without_a_chain():
    r = world(50, 20, per=PER, max_firings=1)
    s, lines = play(r, (0,))
    assert links(lines) == [] and s.time == 10
