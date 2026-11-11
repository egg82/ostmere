"""Invariant 18, behaviourally, for the cards part: the engine is a deterministic function of its inputs. The static half
(imports only the stdlib and itself) is engine_contract/test_purity.py, which scans every module of the package.

The same run gives the same saves, text and view in this process and in fresh interpreters with other string-hash
seeds, which catches a result that depends on set or dict iteration order, a clock or a random draw."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
APP = HERE.parents[1]
SCRIPT = f"""
import hashlib, sys
sys.path.insert(0, {str(HERE)!r})
from cards_world import rich_rules, rich_saves
from ashfall_app.engine import encode, view
r = rich_rules()
h = hashlib.sha256()
for s in rich_saves():
    h.update(encode(s, r).encode())
    h.update(repr(view(s, r)).encode())
print(h.hexdigest())
"""


def fingerprint() -> str:
    from ashfall_app.engine import encode, view
    from cards_world import rich_rules, rich_saves
    r = rich_rules()
    h = hashlib.sha256()
    for s in rich_saves():
        h.update(encode(s, r).encode())
        h.update(repr(view(s, r)).encode())
    return h.hexdigest()


@pytest.fixture(scope="module")
def here() -> str:
    """This process's fingerprint, computed once for every seed's comparison."""
    return fingerprint()


@pytest.mark.parametrize("seed", ["1", "2"])
def test_same_run_same_result_under_any_hash_seed(seed: str, here: str):
    """Invariant 18: a fresh interpreter with PYTHONHASHSEED=seed computes the same fingerprint of every save's text and
    view as this process does."""
    env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=str(APP))
    out = subprocess.run([sys.executable, "-c", SCRIPT], cwd=APP, env=env, capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr[-2000:]
    assert out.stdout.strip() == here


@pytest.mark.parametrize("first", range(4))
def test_an_outcomes_starts_apply_in_the_order_listed(first: int):
    """Invariant 18 / Outcome: a rack completion's starts are tapped in the order listed, whatever the hash seed: with
    four hands cards listed in each rotation, the one listed first takes HANDS."""
    from ashfall_app.engine import HANDS, CardDef, CardId, Outcome, StoreDef, StoreId, advance, new_save
    from cards_world import Q, RACK, lane, rules, tap

    hands = [CardId(f"h{i}") for i in range(4)]
    listed = tuple(hands[first:] + hands[:first])
    r = rules([StoreDef(StoreId("y"), 20 * Q, 0)],
              cards=[CardDef(h, 100) for h in hands] + [CardDef(CardId("rk"), 10, lane=RACK, cap=3,
                                                                 outcome=Outcome(starts=listed))],
              lanes=[RACK])
    landed = advance(tap(new_save(r), r, 0, CardId("rk")), r, 10)
    assert lane(landed, HANDS).card == hands[first]


def test_running_dry_pauses_the_same_card_every_time():
    """Invariant 18, "Running dry": the last card in mix order is paused first, and only as many as needed; the same run
    repeated gives the same pauses (a random draw in the choice shows within a dozen repeats)."""
    from ashfall_app.engine import CardDef, CardId, Flow, StoreDef, StoreId, advance, new_save
    from cards_world import Q, rules, with_mix

    y = StoreId("y")
    mk, light, heavy = CardId("make"), CardId("light"), CardId("heavy")
    r = rules([StoreDef(y, 20 * Q, 10_000)],
              cards=[CardDef(mk, 100, makes=(Flow(y, 1000),)), CardDef(light, 100, costs=(Flow(y, 500),)),
                     CardDef(heavy, 100, costs=(Flow(y, 2000),))])
    s = with_mix(new_save(r), r, 0, {mk: 3000, light: 3000, heavy: 3000})
    for _ in range(12):
        assert [p.runner for p in advance(s, r, 100).pauses] == [heavy]
