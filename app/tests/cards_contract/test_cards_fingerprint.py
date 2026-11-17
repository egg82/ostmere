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
    0: ('04d597517629818b', '44850b184e1ad758', '978cb4d310902b6d'),
    1: ('e9e3adeaf6e3ac61', '08179576dd2fb3ff', '32e48c3111690062'),
    2: ('9e5c20592435788c', 'cc62f755d59b9157', 'd7ad5e9932f2f68c'),
    3: ('d77cb00a3023a042', '122107069020802d', 'ed551cbadfa7e065'),
    4: ('42058c61f7e2e259', 'cdae0dd41b90948c', '8ebcf5b6ce146fc2'),
    5: ('24b66f13245aeb37', '0cc5734059b35e04', '7b428d53b46120b8'),
    6: ('8c40eaaffff65221', '4eb74a3106717890', 'ef91723c1a039145'),
    7: ('1c37116ddf1bd671', 'e5ed8dec09bc3a76', 'ba4955271fa47c5b'),
    8: ('86bb0a57c40d10ab', '5e2ec108736c1705', 'bd74867ed5c9a6c4'),
    9: ('11199db09289625e', '7d9a8a30e7509e66', '2fbb439d820f95ce'),
    10: ('5f93679b1f5619aa', 'b21d97733cc9d012', '7dfd50fb08ddad6f'),
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
