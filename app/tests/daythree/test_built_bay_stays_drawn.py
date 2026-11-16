"""A built bay stays in the camp picture: the layer drawn once it is built holds in the real opening's view, where the
ledger lists only the stores the opening unlocks and the bay's is never one."""
import sys
from pathlib import Path

import pytest

from ashfall_app.engine import CardId
from ashfall_app.engine.work import completions
from tests.daytwo.player import DayTwoPlayer

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "scene"))
import daythree_layers as d3   # tools/scene, on the path from the line above
from stages import State, holds

pytestmark = pytest.mark.playthrough


@pytest.mark.parametrize("day3_route", ["typical"], indirect=True)
def test_a_built_bay_is_not_on_the_ledger_and_its_layer_holds(day3_route: tuple[str, DayTwoPlayer]):
    _, p = day3_route
    v = p.view()
    assert p.rules.opening is not None
    built = {c: completions(p.save, p.rules, CardId(c)) for c in ("make_bay", "n2_build_bay")}
    assert sum(built.values()) > 0
    assert "bay" not in {ln.store for ln in v.ledger}
    facts = frozenset(f"project:{c}" for c, n in built.items() if n > 0)
    assert holds(d3.BAY_BUILT, State(facts))
