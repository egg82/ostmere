"""A cast is for good (api/contract/casting.txt, "CASTING", "The pick" last paragraph): later counts, a later lane's
joining and the cast lane's leaving move nothing, and a rebase keeps a held cast or makes the cast at its own instant.
Written blind from that part."""
from pathlib import Path

from ashfall_app.engine import CardId, CardShare, Mix, Rules, Save, SaveMix, advance, decide, encode, rebase
from casting_world import CAST_AT, TOWN, completions, held, kills, rules_of, scene

SHARES = dict(t_a_chop=1000, t_b_chop=3000, t_c_chop=2000)


def shift(s: Save, r: Rules, t: int, **by_card: int) -> Save:
    """The save advanced to t, then the town mix changed to `by_card`."""
    s = advance(s, r, t)
    return decide(s, r, t, SaveMix(Mix(TOWN, tuple(CardShare(CardId(c), bp) for c, bp in by_card.items()))))


def test_the_cast_lands_at_the_outcomes_instant_and_not_before(tmp_path: Path):
    r = rules_of(tmp_path)
    s = scene(r, SHARES)
    assert held(advance(s, r, CAST_AT - 1), r) == []
    assert held(advance(s, r, CAST_AT), r) == ["t_b"]


@kills(4)
def test_counts_that_change_after_the_cast_move_nothing(tmp_path: Path):
    r = rules_of(tmp_path)
    s = shift(advance(scene(r, SHARES), r, CAST_AT + 5), r, 300, t_a_chop=9000)
    s = advance(s, r, 3000)
    assert completions(s, r, "t_a_chop") > completions(s, r, "t_b_chop")
    assert held(s, r) == ["t_b"]


@kills(4)
def test_a_lane_that_joins_later_with_the_most_work_does_not_take_the_role(tmp_path: Path):
    r = rules_of(tmp_path, joins={"t_m": 400})
    s = shift(advance(scene(r, SHARES), r, 400), r, 400, t_m_chop=9000)
    s = advance(s, r, 3000)
    assert completions(s, r, "t_m_chop") > completions(s, r, "t_b_chop")
    assert held(s, r) == ["t_b"]


@kills(12)
def test_the_cast_lane_leaving_the_town_does_not_move_the_role(tmp_path: Path):
    r = rules_of(tmp_path, leaves={"t_b": 300})
    s = advance(scene(r, SHARES), r, 1000)
    assert held(s, r) == ["t_b"]


@kills(14)
def test_a_rebase_of_a_save_that_holds_the_feature_keeps_it_exactly(tmp_path: Path):
    """Under the same rules, and under rules whose cast is at another instant (so the save is reshaped)."""
    r = rules_of(tmp_path)
    s = advance(scene(r, SHARES), r, 400)
    for new in (r, rules_of(tmp_path, cast_at=250)):
        kept = rebase(encode(s, r), new)
        assert held(kept, new) == ["t_b"] and kept.unlocked == s.unlocked


@kills(4, 14)
def test_an_outcome_replayed_for_a_role_already_cast_changes_nothing(tmp_path: Path):
    """The rules lose the cast trigger and gain the same cast under another id: the rebase fires it for a save that
    holds the role, and counts have moved on (b still leads, but holds the role, so a would be next)."""
    old, new = rules_of(tmp_path), rules_of(tmp_path, cast_id="t_cast_again", cast_at=300)
    s = advance(scene(old, SHARES), old, 400)
    assert held(rebase(encode(s, old), new), new) == ["t_b"]


@kills(14)
def test_a_rebase_that_lands_the_cast_picks_from_the_counts_the_save_holds_then(tmp_path: Path):
    """The save is at 300 under rules with no cast. a led at 205 (6 against none); by 300 b has 8 against a's 6. Live play
    casts a at 205; the rebase casts at 300, from the counts there: b."""
    first = dict(t_a_chop=3000)
    later = dict(t_b_chop=9000)
    old, new = rules_of(tmp_path, casts=None), rules_of(tmp_path)
    s = advance(shift(scene(old, first), old, 210, **later), old, 300)
    assert (completions(s, old, "t_a_chop"), completions(s, old, "t_b_chop")) == (6, 8)
    live = advance(shift(scene(new, first), new, 210, **later), new, 300)
    assert held(live, new) == ["t_a"]
    assert held(rebase(encode(s, old), new), new) == ["t_b"]


def test_a_save_not_yet_at_the_moment_has_no_cast_after_a_rebase(tmp_path: Path):
    old, new = rules_of(tmp_path, casts=None), rules_of(tmp_path)
    s = advance(scene(old, SHARES), old, CAST_AT - 50)
    assert held(rebase(encode(s, old), new), new) == []
