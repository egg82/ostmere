"""Share by day and the quiet flag on small fixtures: means over a day's samples, a card a sample omits counted as zero,
a gap in the samples refused, and the flag naming exactly the cards that held a share and then none to the end."""
import pytest

from tests.ladder.shares import DAY_S, day_averages, gone_quiet


def test_day_average_is_the_mean_of_the_days_samples_in_percent() -> None:
    samples = [(0, {"a": 10_000}), (DAY_S // 2, {"a": 5_000, "b": 5_000}), (DAY_S, {"b": 10_000})]
    first, second = day_averages(samples, 2)
    assert first == {"a": 75.0, "b": 25.0}
    assert second == {"b": 100.0}


def test_a_day_without_a_sample_is_refused() -> None:
    with pytest.raises(ValueError, match="day 2"):
        day_averages([(0, {"a": 10_000})], 2)


def test_quiet_cards_are_those_that_held_a_share_and_then_none_to_the_end() -> None:
    days = [{"old": 50.0, "live": 50.0}, {"old": 20.0, "live": 80.0}, {"live": 100.0}, {"live": 100.0}]
    assert gone_quiet(days) == {"old": 3}


def test_a_card_that_returns_or_never_held_a_share_is_not_flagged() -> None:
    days = [{"back": 50.0, "never": 0.0}, {"other": 100.0}, {"back": 10.0, "other": 100.0}]
    assert gone_quiet(days) == {}


def test_nothing_to_flag_on_no_days() -> None:
    assert gone_quiet([]) == {}
