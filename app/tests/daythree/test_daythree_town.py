"""The town's default policy and the 2 AM test across two joins (docs/design/day-three-plan.md, item 3f), on the fixture
chapter (daythree/townfix.py): a player who leaves the join's split ends level with one who re-splits by hand at the
visit after each join, when the join's split is the best one; the measure can tell, since on a fixture whose join leaves a faster card
idle the re-splitter ends ahead. Worth is the stores' total, each store counted alike (the fixture's rates share a unit)."""
from ashfall_app.engine import BP, QUANTITY_SCALE as Q, CardShare, SaveMix, Unlock, UnlockKind, new_save
from tests.daythree import town, townfix
from tests.daythree.townfix import H, Played
from tests.dayone.parity import Measured, replay

VISITS = (0, 2 * H, 5 * H, 9 * H)
"""The first sets the people's rules; the joins land at 1 h and 3 h, between the visits."""
UNTIL = 20 * H


def pair(alt_rate: int) -> tuple[Played, Played, Measured, Measured]:
    r = townfix.rules(alt_rate)
    default = townfix.play(r, VISITS, town.default_split, UNTIL)
    by_hand = townfix.play(r, VISITS, town.resplit, UNTIL)
    start = new_save(r)
    return (default, by_hand, replay(r, start, default.log, UNTIL, False, boosts=()),
            replay(r, start, by_hand.log, UNTIL, False, boosts=()))


def worth(m: Measured) -> int:
    return sum(s.segment.start_value for s in m.save.stores)


def test_the_joins_make_the_town_mix_and_the_default_changes_nothing_after():
    default, _, _, _ = pair(Q)
    (mix,) = default.save.mixes
    assert mix.id == townfix.TOWN and set(mix.components) == {CardShare(townfix.P1_A, BP), CardShare(townfix.P2_A, BP)}
    assert Unlock(UnlockKind.JOINED, townfix.P1) in default.save.unlocked and Unlock(UnlockKind.JOINED, townfix.P2) in default.save.unlocked
    assert [v for _, v in default.log] == [townfix.SET]


def test_the_by_hand_policy_re_splits_at_the_visit_after_each_join():
    _, by_hand, _, _ = pair(Q)
    assert sorted({t for t, v in by_hand.log if isinstance(v, SaveMix)}) == [2 * H, 5 * H]


def test_the_replay_is_the_play():
    default, by_hand, w, b = pair(Q)
    assert w.save == default.save and b.save == by_hand.save


def test_the_re_splitter_ends_level_when_the_joins_split_is_the_best():
    _, _, w, b = pair(Q)
    assert worth(b) == worth(w) > 0


def test_the_re_splitter_ends_ahead_when_the_join_leaves_a_faster_card_idle():
    """The planted control: each person's second card makes three times the first."""
    _, _, w, b = pair(3 * Q)
    assert worth(b) > worth(w)
