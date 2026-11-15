"""tools/scene: a layer's `store:` condition reads the page's ledger, and the ledger holds only stores the opening
unlocks (engine/view.py `_ledger`). A condition on a store nothing unlocks never holds in play, though it holds on every
fixture, where every store counts as unlocked. What a built thing shows on is a card's completions instead."""
import re
import sys
from pathlib import Path

from ashfall_app.opening.refs import outcomes
from ashfall_app.opening.schema import load_opening

SCENE = Path(__file__).resolve().parents[2] / "tools" / "scene"
sys.path.insert(0, str(SCENE))

HELD = frozenset({"b7_clock", "b9_clock", "drift_left", "e2_clock", "morning_13", "night_12", "night_14",
                  "stranger_clock"})
"""Hidden clocks and a countdown the layers read, which the page cannot: their layers do not draw until the view carries
what a hidden store holds. Shrinks only."""


def named_in_the_scene() -> set[str]:
    return {m for p in SCENE.glob("*.py") if p.name != "stages.py"
            for m in re.findall(r"\bstore:([a-z][a-z0-9_]*)", p.read_text())}


def unlocked_by_the_opening() -> set[str]:
    o = load_opening()
    return {u.id for u in [*o.start, *(u for _, out in outcomes(o) for u in out.unlocks)] if u.unlock_kind == "store"}


def test_the_scene_names_stores_and_the_opening_unlocks_some():
    assert {"stakes", "stones"} <= named_in_the_scene() & unlocked_by_the_opening()


def test_every_store_a_layer_reads_is_one_the_opening_unlocks():
    never = named_in_the_scene() - unlocked_by_the_opening()
    assert never == HELD, f"new: {sorted(never - HELD)}; mended, take out of HELD: {sorted(HELD - never)}"
