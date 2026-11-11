"""A clock schedule (schedules._clock) visits at every hour it lists, every day, whatever order the hours are listed
in: evenings's and lunch's lists start in the evening and wrap past midnight."""
import pytest

from tests.dayone.schedules import HOUR, OPENING_CLOCK, schedule


@pytest.mark.parametrize(("name", "hours"), [("evenings", {7.5, 19, 20.5, 21.5, 22.5, 23}),
                                             ("lunch", {7.5, 12.5, 19, 20.5, 21.5, 22.5, 23})])
def test_a_clock_route_visits_at_each_of_its_hours_on_a_whole_day(name: str, hours: set[float]):
    end_at = HOUR
    day_two = (24 * HOUR - OPENING_CLOCK - end_at, 48 * HOUR - OPENING_CLOCK - end_at)
    starts = {((OPENING_CLOCK + end_at + v.start) % (24 * HOUR)) / HOUR
              for v in schedule(name, end_at).visits if day_two[0] <= v.start < day_two[1]}
    assert starts == hours
