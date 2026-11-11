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
    0: ('822a379be881ea93', '1e672a7122e3e0d6', '6872c066cf712d99'),
    1: ('3ce8459a62d503f9', 'adad7a367f91de7a', 'bd0e7f6d207e4d5c'),
    2: ('96f9d3b0973240f9', 'e25836f8cb48a600', '756341b452f94fa1'),
    3: ('e892aceb3a989960', 'f954601e2e417c54', 'b1c028d01fb59e5d'),
    4: ('0316506fdf843bf0', '68c2cb1deb2fa36f', 'a52be3902d80b737'),
    5: ('9c2bc72040694839', '923b7a27d5ce9190', '547833bfc3f22ce4'),
    6: ('562997558c5a87fe', 'de322026c2186a92', '932344e613e8cf19'),
    7: ('f87a6234ea7425ad', '9e6cc00c42011d2c', '0a3bdab2f0797184'),
    8: ('b7de74059d6babb2', '8dc06e549b9a2fd5', '035bf32a5b5d7323'),
    9: ('bec52bbceac66e26', 'f381689f418a72b7', '8b41de6453293cb0'),
    10: ('e25c967fd942cccc', '7f6981d2d443ff3b', '078411ce61299306'),
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
