"""tools/bench_ab.py's verdict: the ratio is head's fastest over base's, and a side with nothing measured is an error,
never a pass."""
import pytest

from tools.bench_ab import SLOWER_MAX, fastest, verdict

SAME = {"reading": [0.6, 0.58], "steps": [0.42, 0.4]}


def test_the_same_samples_are_a_ratio_of_one() -> None:
    assert verdict(SAME, SAME) == {"reading": 1.0, "steps": 1.0}


def test_a_slower_head_is_over_the_limit_and_only_in_its_workload() -> None:
    slower = {"reading": SAME["reading"], "steps": [s * (1 + SLOWER_MAX + 0.03) for s in SAME["steps"]]}
    ratios = verdict(SAME, slower)
    assert ratios["steps"] > 1 + SLOWER_MAX
    assert ratios["reading"] <= 1 + SLOWER_MAX


def test_the_fastest_sample_decides_so_one_slow_sample_does_not() -> None:
    noisy = {"reading": [0.58, 0.9], "steps": [0.4, 1.5]}
    assert verdict(SAME, noisy) == {"reading": 1.0, "steps": 1.0}


@pytest.mark.parametrize("side", ["base", "head"])
def test_a_side_with_no_samples_raises(side: str) -> None:
    empty = {"reading": [], "steps": [0.4]}
    with pytest.raises(ValueError):
        verdict(empty, SAME) if side == "base" else verdict(SAME, empty)


def test_the_absolute_numbers_are_each_sides_fastest_sample() -> None:
    assert fastest(SAME, {"reading": [0.7, 0.65], "steps": [0.5, 0.45]}) == (
        "reading: base=0.580s head=0.650s steps: base=0.400s head=0.450s")
