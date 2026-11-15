"""Makers by band on small fixtures: a sample's rate held for the step and summed per maker, a store made in nothing in a
band absent, and the at-cap percent per band."""
from tests.ladder.shares import DAY_S
from tests.makers.tally import Band, at_cap_share, band_spans, made_by_band, merged


def test_made_is_each_samples_rate_held_for_the_step_per_maker_and_band() -> None:
    samples = [(0, {"s": {"a": 2.0, "b": 1.0}}), (DAY_S // 2, {"s": {"a": 1.0}}), (4 * DAY_S, {"s": {"b": 3.0}})]
    got = made_by_band(samples, 4)
    assert got["s"][(1, 2)] == {"a": 12.0, "b": 4.0}
    assert got["s"][(3, 5)] == {"b": 12.0}
    assert (6, 9) not in got["s"]


def test_a_store_with_no_rate_in_a_band_is_absent_there() -> None:
    assert made_by_band([(0, {"s": {"a": 0.0}})], 4) == {"s": {}}


def test_at_cap_is_the_percent_of_a_bands_samples_at_the_cap() -> None:
    samples = [(0, {"s": True}), (1, {"s": False}), (2, {"s": True}), (3, {"s": True}), (3 * DAY_S, {"s": False})]
    assert at_cap_share(samples) == {"s": {(1, 2): 75.0, (3, 5): 0.0}}


def test_merged_sums_makers_a_store_shares_across_readings() -> None:
    first, later = (1, 2), (3, 5)
    a: dict[str, dict[Band, dict[str, float]]] = {"s": {first: {"x": 1.0}}}
    b: dict[str, dict[Band, dict[str, float]]] = {"s": {first: {"x": 2.0, "y": 1.0}, later: {"y": 4.0}}}
    assert merged(a, b) == {"s": {first: {"x": 3.0, "y": 1.0}, later: {"y": 4.0}}}


def test_band_spans_stop_at_the_route_end_and_leave_out_later_bands() -> None:
    assert band_spans(4 * DAY_S) == [((1, 2), 0, 2 * DAY_S), ((3, 5), 2 * DAY_S, 4 * DAY_S)]
