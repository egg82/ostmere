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
    0: ('d946938ef9fc1191', 'c7b25c75d1334dcc', 'b0769cb3e4be9ef8'),
    1: ('4b070151fe85068e', 'e43fa7dfb2733edc', 'f35eeea0126c8539'),
    2: ('cfabda43f1ece36e', '344fd2c0038beda8', '6925bf900602798c'),
    3: ('b1e5cbd231fcdd01', '4dc087966a108f87', '372945c9b4c6739a'),
    4: ('b3f39dc07684b3aa', 'a58249735f8fee4c', '6e41a9526cac092e'),
    5: ('64675e92382367f4', '34168420f682435f', '0430f17b64e936ba'),
    6: ('1c90df9fd5c136ba', '62d516edccbdfbb4', '13397f6c4b244b7e'),
    7: ('ccf532712552d3ea', '5963ec172af4c88f', '4f078689fdae77de'),
    8: ('f301e11dbce5560d', 'a9605aa0dd89aab5', 'e5c5e9b711ae0561'),
    9: ('8fe27b32e76f831e', 'd353bdce88ad0e0a', 'e017124b8b486ec8'),
    10: ('9104f37d5501c5e1', '7f50f54751873f51', '9c7d2144f19e6527'),
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
