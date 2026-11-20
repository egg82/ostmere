"""The release lock and pooled lanes (engine DESIGN.txt, "GROUPS (pooled lanes)", "Release lock"): a released lane's
`pooled` changing either way is forbidden; a new pooled lane, and a released person's group changing (not recorded:
nothing saved names membership), are not."""
from functools import cache

import pytest

from ashfall_app.opening.lock import Lock, snapshot
from ashfall_app.opening.lock_checks import Problem, problems
from ashfall_app.opening.renames import load_renames
from ashfall_app.opening.schema import load_opening, to_rules

PERSON = "n1"
NEW = "t_new_crew"


@cache
def released() -> Lock:
    o = load_opening()
    return snapshot(o, to_rules(o), load_renames())


def forbidden(lock: Lock, now: Lock) -> list[Problem]:
    return [p for p in problems(lock, now, load_renames()) if p.cls == "forbidden"]


def with_new_lane(lock: Lock, pooled: bool) -> Lock:
    return lock.model_copy(update={
        "ids": {**lock.ids, "lane": sorted([*lock.ids["lane"], NEW])},
        "lane_ruled": {**lock.lane_ruled, NEW: True}, "lane_pooled": [*lock.lane_pooled, NEW] if pooled else lock.lane_pooled})


def test_the_unchanged_content_has_nothing_forbidden():
    assert released().lane_pooled == [] and forbidden(released(), released()) == []


def test_a_released_lane_becoming_pooled_is_forbidden():
    now = released().model_copy(update={"lane_pooled": [PERSON]})
    assert any(f"lane {PERSON}'s pooled changed" in p.message for p in forbidden(released(), now))


def test_a_released_pooled_lane_becoming_a_person_is_forbidden():
    was = released().model_copy(update={"lane_pooled": [PERSON]})
    assert any(f"lane {PERSON}'s pooled changed" in p.message for p in forbidden(was, released()))


@pytest.mark.parametrize("pooled", [True, False])
def test_a_new_lane_is_free_pooled_or_not(pooled: bool):
    assert forbidden(released(), with_new_lane(released(), pooled)) == []
