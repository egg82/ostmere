"""The engine's outputs over the rich world, recorded: each rich save's text, lines, view and forecast after half a game
day, and after its modifier stack changes while its chips and unlock set stay the same objects (what the engine's
caches across saves key on, memo.PartsMemo). A change that makes the engine faster must leave these alone; one that
changes what the engine does re-records them on purpose, with RECORD=1 printing the new values."""
import hashlib
import os
from dataclasses import replace
from functools import cache

import pytest

from ashfall_app.engine import (
    HANDS, FlowKind, LaneSpeed, RateRef, Rules, Save, StoreId, UnlockKind, advance_logged, encode, forecast, view,
)
from cards_world import G, X, add, mul, rich_rules, rich_saves

DAY_S = 86_400
PROBES = (mul(LaneSpeed(HANDS), 7000, "probe"), add(RateRef(G, FlowKind.MAKE, X), -2500, "probe"))
RUNS = 3   # a half day on the save, then an eighth under each probe
RECORDED = {   # per save, the fingerprint of each run
    0: ('c19593cd8f94aae1', 'e44e9d18beed5008', 'd8e9d98f44e56fa8'),
    1: ('3da950967bee3916', 'ffdf4ca21b98cdf2', '7a85581caf018f0b'),
    2: ('731d960b8b092451', '66740cd6ca0e8dca', 'f7a7284b51467d93'),
    3: ('7811ac8d0886865b', '17d70dd2c227d528', '097933c0557d3378'),
    4: ('0b4d1df999c32672', '8a9ae6cdd417bb1b', 'fd2c0891ac1813df'),
    5: ('bfa7051ac6185c16', '8d29f1751d82a29a', '0589038dbe9c5733'),
    6: ('2edfd28b6b7d7232', 'd9b3f37e442f927a', 'ea553058917abb9e'),
    7: ('973ee2653da0a6a2', 'e26612d5b8b6ca64', 'fade856527198acf'),
    8: ('ff6a1d34ec2855cd', '1ea0b6546003bb26', '0c2abcd3fd8f1db5'),
    9: ('fd3def5fc46c7775', '8e14c7739407c026', '7ad87f8706b3e179'),
    10: ('3f01ae5cb0fc914b', '1207277541df14e6', '33144602d965af5c'),
}


def _shown(save: Save) -> tuple[StoreId, ...]:
    return tuple(StoreId(u.id) for u in save.unlocked if u.kind is UnlockKind.STORE)


def _outputs(save: Save, r: Rules, seconds: int) -> str:
    step = advance_logged(save, r, save.time + seconds)
    ahead = forecast(save, r, save.time + 6 * 3600, _shown(save))
    return repr((encode(step.save, r), step.lines, view(step.save, r), ahead))


@cache
def _world() -> tuple[Rules, list[Save]]:
    return rich_rules(), rich_saves()


def fingerprint(i: int, run: int) -> str:
    r, saves = _world()
    s = saves[i]
    if run == 0:
        return hashlib.sha256(_outputs(s, r, DAY_S // 2).encode()).hexdigest()[:16]
    return hashlib.sha256(_outputs(replace(s, modifiers=s.modifiers + (PROBES[run - 1],)), r, DAY_S // 8).encode()).hexdigest()[:16]


@pytest.mark.parametrize("run", range(RUNS))
@pytest.mark.parametrize("i", sorted(RECORDED))
def test_the_engine_gives_the_recorded_outputs(i: int, run: int):
    got = fingerprint(i, run)
    if os.environ.get("RECORD"):
        print(f"{i}: {got!r},")
    assert got == RECORDED[i][run]
