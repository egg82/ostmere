"""The shipped prestige tracks' nodes act beyond their skill by an ordinary rank amount, and the tracks' readout
(tests/opening/tracks_readout.py) reports how many ranks bring something new. How many nodes a track holds and how many
ranks a node has are taste: reported, never failed (the engine's nodechecks.py holds what must be true of a node). Read off
the shipped content, with planted changes."""
from collections import Counter

from ashfall_app.opening.schema import Opening
from tests import readout_snapshot as rs
from tests.opening import tracks_readout


def test_every_shipped_rank_is_sized_like_the_first_ones(shipped_opening: Opening):
    assert {n.per_rank_bp for n in shipped_opening.nodes} == {2500}


def test_the_committed_readouts_are_the_ones_the_tracks_write():
    assert rs.stray("tracks", tracks_readout.NAMES) == ([], [])


def test_the_tracks_readout_is_reported(shipped_opening: Opening):
    assert shipped_opening.nodes
    text = tracks_readout.render(shipped_opening.nodes)
    assert len(text.splitlines()) == len(Counter(n.skill for n in shipped_opening.nodes)) + 1
    rs.check("tracks", text)


def test_the_readout_counts_repeats_and_nodes_that_bring_something_new(shipped_opening: Opening):
    first = shipped_opening.nodes[0]
    twice = first.model_copy(update={"ranks": 3})
    same = first.model_copy(update={"id": "planted_again"})
    planted = [twice, same, *(n for n in shipped_opening.nodes if n.skill == first.skill and n.id != first.id)]
    row = tracks_readout.render(planted).splitlines()[1].split()
    held = len(planted)
    ranks = 3 + 1 + held - 2
    assert row[:5] == [first.skill, str(held), str(ranks), str(held - 1), str(ranks - (held - 1))]
    assert f"{first.id} x3" in " ".join(row) and "planted_again" in row[-1]


def test_a_multi_rank_node_loads(shipped_opening: Opening):
    from ashfall_app.opening.checks import check_structure
    nodes = [n.model_copy(update={"ranks": 2}) if n.id == "wc_lever" else n for n in shipped_opening.nodes]
    check_structure(shipped_opening.model_copy(update={"nodes": nodes}))
