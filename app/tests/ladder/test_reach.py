"""First-reach bisection on small fixtures: a level reached inside a gap between saves is found within the tolerance,
one reached at a sample is that sample, an unreached one is None, and the call count stays logarithmic."""
from tests.ladder.reach import Reach, first_reach, reaches

TIMES = [0, 1000, 5000, 20000]


def ramp(t: int) -> int:
    """A level that is t // 3000 + 1: level n is first reached at 3000 * (n - 1)."""
    return t // 3000 + 1


def test_inside_a_gap_is_bisected_to_within_the_tolerance() -> None:
    found = first_reach(TIMES, ramp, 4, tol=60)   # truly 9000, between the samples 5000 and 20000
    assert found is not None and 9000 <= found <= 9060


def test_a_level_reached_at_a_sample_is_that_sample() -> None:
    found = first_reach(TIMES, lambda t: 1 if t < 1000 else 2, 2, tol=1)
    assert found == 1000


def test_reached_before_the_first_sample_reads_the_first_instant() -> None:
    assert first_reach(TIMES, lambda t: 5, 3) == 0


def test_unreached_is_none() -> None:
    assert first_reach(TIMES, ramp, 10) is None
    assert first_reach([], ramp, 1) is None


def test_the_search_asks_few_instants() -> None:
    asked: list[int] = []

    def counting(t: int) -> int:
        asked.append(t)
        return ramp(t)
    first_reach(list(range(0, 100_000, 100)), counting, 20, tol=60)
    assert len(asked) < 30


def test_reaches_carries_the_gap_and_goes_none_past_the_edge() -> None:
    got = reaches(TIMES, ramp, [2, 3, 9], tol=1)
    assert got[0] == Reach(2, 3000, 3000)
    assert got[1] == Reach(3, 6000, 3000)
    assert got[2] == Reach(9, None, None)
