"""A skill's prestige track holds at least two nodes of one rank each, so every click but the last is a choice
(opening/prestige.py, check_tracks), and the shipped tracks' nodes act beyond their skill by an ordinary rank amount. Read off the shipped
content, with planted changes."""
from collections import Counter

import pytest

from ashfall_app.opening.checks import check_structure
from ashfall_app.opening.prestige import check_tracks
from ashfall_app.opening.schema import Opening


def test_every_shipped_track_holds_at_least_two_nodes(shipped_opening: Opening):
    held = Counter(n.skill for n in shipped_opening.nodes)
    assert len(held) >= 6 and min(held.values()) >= 2, held


def test_every_shipped_node_is_one_rank(shipped_opening: Opening):
    assert shipped_opening.nodes and {n.ranks for n in shipped_opening.nodes} == {1}


def test_a_two_rank_node_is_refused(shipped_opening: Opening):
    nodes = [n.model_copy(update={"ranks": 2}) if n.id == "wc_lever" else n for n in shipped_opening.nodes]
    with pytest.raises(ValueError, match="node wc_lever has 2 ranks"):
        check_tracks(nodes)
    check_tracks(shipped_opening.nodes)


def test_every_shipped_rank_is_sized_like_the_first_ones(shipped_opening: Opening):
    assert {n.per_rank_bp for n in shipped_opening.nodes} == {2500}


def test_a_track_of_one_node_is_refused(shipped_opening: Opening):
    nodes = [n for n in shipped_opening.nodes if n.id != "ar_dry_shelf"]
    assert Counter(n.skill for n in nodes)["arcana"] == 1   # the plant leaves arcana one node
    with pytest.raises(ValueError, match="prestige arcana: its track is one node"):
        check_tracks(nodes)


def test_the_load_runs_the_check(shipped_opening: Opening):
    nodes = [n for n in shipped_opening.nodes if n.id != "me_sinew_ties"]
    with pytest.raises(ValueError, match="prestige melee: its track is one node"):
        check_structure(shipped_opening.model_copy(update={"nodes": nodes}))
