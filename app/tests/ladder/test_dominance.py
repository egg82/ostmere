"""The dominance verdict on synthetic sets: it says yes where one shape wins everywhere and no where the lead changes
hands, and it counts shapes, ties and lone-shape instants as the definition says (dominance.py). The source shares by
band on a small fixture."""
from tests.ladder.dominance import Point, dominance
from tests.ladder.shares import DAY_S
from tests.ladder.sources import BANDS, band_shares

A = (("c1", 6000), ("c2", 4000))
A_AGAIN = (("c1", 6500), ("c2", 3500))
B = (("c1", 2000), ("c3", 8000))


def points(*scores: dict[str, tuple[tuple[tuple[str, int], ...], float]]) -> list[Point]:
    return [(i * 3600, s) for i, s in enumerate(scores)]


def test_one_shape_ahead_at_every_instant_always_wins() -> None:
    found = dominance(points(*({"x": (A, 3.0), "y": (B, 1.0)} for _ in range(6))))
    assert found.always and len(found.shapes) == 2 and found.wins[0] == 6


def test_the_lead_changing_hands_is_not_dominance() -> None:
    found = dominance(points(*({"x": (A, 3.0 - i), "y": (B, 1.5)} for i in range(4))))
    assert not found.always and dict(found.wins) == {0: 2, 1: 2}


def test_a_mix_saved_again_with_shares_moved_a_little_stays_one_shape() -> None:
    found = dominance(points({"x": (A, 3.0), "y": (B, 1.0)}, {"x": (A_AGAIN, 3.0), "y": (B, 1.0)}))
    assert len(found.shapes) == 2 and found.always


def test_two_mixes_of_one_shape_do_not_tie_each_other() -> None:
    found = dominance(points({"x": (A, 2.0), "z": (A_AGAIN, 2.0), "y": (B, 1.0)}))
    assert found.always and found.left_out == 0


def test_a_tie_between_shapes_or_no_xp_is_left_out_and_a_lone_shape_is_not_compared() -> None:
    found = dominance(points({"x": (A, 2.0), "y": (B, 2.0)}, {"x": (A, 0.0), "y": (B, 0.0)}, {"x": (A, 5.0)}))
    assert (found.left_out, found.single, found.winners, found.always) == (2, 1, (), False)


def test_the_control_sets_are_told_apart() -> None:
    dominated = dominance(points(*({"x": (A, 4.0), "y": (B, 1.0 + i)} for i in range(3))))
    contested = dominance(points(*({"x": (A, 2.0), "y": (B, 1.0 + i)} for i in range(3))))
    assert dominated.always and not contested.always


def test_source_shares_split_a_skill_over_a_band_and_drop_a_band_it_earned_nothing_in() -> None:
    samples = [(0, {"s": {"a": 30, "b": 10}}), (3600, {"s": {"a": 10, "b": 30}}), (3 * DAY_S, {"s": {"a": 0}})]
    got = band_shares(samples)["s"]
    assert got == {BANDS[0]: {"a": 50.0, "b": 50.0}}
