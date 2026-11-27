"""A line said again and again draws from at least MIN_POOL different keys (rules/checks/text/pool_checks.py): the shipped content
passes with every kind of pool seen, and each planted short pool fails naming its source."""
from collections.abc import Callable
from functools import cache

import pytest

from ashfall_app.rules.checks.text.pool_checks import MIN_POOL, check_pools, pools
from ashfall_app.rules.schema import Opening, load_opening

type Plant = Callable[[Opening], Opening]


@cache
def shipped() -> Opening:
    return load_opening()


def test_the_shipped_pools_pass_and_the_scan_sees_every_kind():
    found = dict(pools(shipped()))
    check_pools(shipped())
    assert MIN_POOL == 6
    assert {"chip hurt off_line_keys", "card hunt_wolf won_line_keys", "action rats lost_line_keys",
            "people went at_least 5"} <= found.keys()
    assert all(len(set(keys)) >= MIN_POOL for keys in found.values())


def _chip(o: Opening) -> Opening:
    chips = [c.model_copy(update={"off_line_keys": c.off_line_keys[:MIN_POOL - 1]}) if c.id == "hurt" else c
             for c in o.chips]
    return o.model_copy(update={"chips": chips})


def _twice(o: Opening) -> Opening:
    """Six entries, five different keys."""
    chips = [c.model_copy(update={"off_line_keys": [*c.off_line_keys[:MIN_POOL - 1], c.off_line_keys[0]]})
             if c.id == "hurt" else c for c in o.chips]
    return o.model_copy(update={"chips": chips})


def _fight(o: Opening) -> Opening:
    standing = [a.model_copy(update={"fight": a.fight.model_copy(update={"lost_line_keys": a.fight.lost_line_keys[:2]})})
                if a.id == "rats" and a.fight is not None else a for a in o.standing]
    return o.model_copy(update={"standing": standing})


def _band(o: Opening) -> Opening:
    assert o.people is not None
    went = [b.model_copy(update={"keys": b.keys[:1]}) if b.at_least == 5 else b for b in o.people.went]
    return o.model_copy(update={"people": o.people.model_copy(update={"went": went})})


def _uncapped(o: Opening) -> Opening:
    card = next(c for c in o.cards if c.cap is None)
    cards = [c.model_copy(update={"line_keys": ["l_healed"]}) if c is card else c for c in o.cards]
    return o.model_copy(update={"cards": cards})


@pytest.mark.parametrize("plant,match", [
    (_chip, "^chip hurt off_line_keys: 5 different lines"),
    (_twice, "^chip hurt off_line_keys: 5 different lines"),
    (_fight, "^action rats lost_line_keys: 2 different lines"),
    (_band, "^people went at_least 5: 1 different lines"),
    (_uncapped, "^card .*: an uncapped card's line_keys"),
], ids=["chip off", "a key twice", "fight lost", "people band", "uncapped card"])
def test_a_planted_short_pool_fails_naming_its_source(plant: Plant, match: str):
    with pytest.raises(ValueError, match=match):
        check_pools(plant(shipped()))


def test_an_empty_fight_pool_is_the_stock_line_and_no_pool():
    o = shipped()
    standing = [a.model_copy(update={"fight": a.fight.model_copy(update={"won_line_keys": []})})
                if a.id == "rats" and a.fight is not None else a for a in o.standing]
    bare = o.model_copy(update={"standing": standing})
    check_pools(bare)
    assert "action rats won_line_keys" not in dict(pools(bare))
